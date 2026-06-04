"""
Entrenamiento comparativo: regresión (ratio_ejecucion) y clasificación (alta_ejecucion).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import ElasticNet, LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline

from data.paths import PROJECT_ROOT
from ml.config import (
    CLASSIFICATION_TARGET,
    CV_FOLDS,
    ML_FAST,
    ML_SAMPLE_SIZE,
    MODELING_FILTER,
    RANDOM_STATE,
    REGRESSION_TARGET,
    TEST_SIZE,
)
from ml.data import load_modeling_frame
from ml.evaluate import (
    classification_metrics,
    rank_classification_models,
    rank_regression_models,
    regression_metrics,
)
from ml.features import build_preprocessor, feature_columns

ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"


def _regression_candidates() -> dict[str, Any]:
    base = {
        "elasticnet": ElasticNet(
            alpha=0.01,
            l1_ratio=0.5,
            max_iter=5000,
            random_state=RANDOM_STATE,
        ),
        "hist_gbr": HistGradientBoostingRegressor(
            max_depth=8,
            learning_rate=0.08,
            max_iter=120 if ML_FAST else 200,
            random_state=RANDOM_STATE,
        ),
    }
    if ML_FAST:
        return base
    base["random_forest"] = RandomForestRegressor(
        n_estimators=60,
        max_depth=12,
        min_samples_leaf=30,
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    return base


def _classification_candidates() -> dict[str, Any]:
    base = {
        "logistic_balanced": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "hist_gbc": HistGradientBoostingClassifier(
            max_depth=8,
            learning_rate=0.08,
            max_iter=120 if ML_FAST else 200,
            random_state=RANDOM_STATE,
        ),
    }
    if ML_FAST:
        return base
    base["random_forest"] = RandomForestClassifier(
        n_estimators=60,
        max_depth=12,
        min_samples_leaf=30,
        class_weight="balanced",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    return base


def _cv_regression(pipe: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }
    cv = cross_validate(
        pipe,
        X,
        y,
        cv=CV_FOLDS,
        scoring=scoring,
        n_jobs=1 if ML_FAST else -1,
        error_score="raise",
    )
    return {
        "mae_mean": float(-cv["test_mae"].mean()),
        "mae_std": float(cv["test_mae"].std()),
        "rmse_mean": float(-cv["test_rmse"].mean()),
        "rmse_std": float(cv["test_rmse"].std()),
        "r2_mean": float(cv["test_r2"].mean()),
        "r2_std": float(cv["test_r2"].std()),
    }


def _cv_classification(pipe: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    scoring = {
        "f1": "f1",
        "recall": "recall",
        "precision": "precision",
        "roc_auc": "roc_auc",
        "pr_auc": "average_precision",
    }
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_out = cross_validate(
        pipe,
        X,
        y,
        cv=cv,
        scoring=scoring,
        n_jobs=1 if ML_FAST else -1,
        error_score="raise",
    )
    return {
        "f1_mean": float(cv_out["test_f1"].mean()),
        "f1_std": float(cv_out["test_f1"].std()),
        "recall_mean": float(cv_out["test_recall"].mean()),
        "precision_mean": float(cv_out["test_precision"].mean()),
        "roc_auc_mean": float(cv_out["test_roc_auc"].mean()),
        "pr_auc_mean": float(cv_out["test_pr_auc"].mean()),
    }


def train_regression(
    df: pd.DataFrame,
    artifacts_dir: Path,
) -> dict[str, Any]:
    y = df[REGRESSION_TARGET].astype(float)
    numeric, categorical, all_cols = feature_columns(df)
    X = df[all_cols]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )
    preprocessor = build_preprocessor(numeric, categorical)
    comparison: list[dict[str, Any]] = []

    for name, estimator in _regression_candidates().items():
        pipe = Pipeline([("prep", preprocessor), ("model", estimator)])
        cv_metrics = _cv_regression(pipe, X_train, y_train)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        test_metrics = regression_metrics(y_test, y_pred)
        comparison.append(
            {
                "model": name,
                "cv_metrics": cv_metrics,
                "test_metrics": test_metrics,
                "pipeline": pipe,
            }
        )

    ranked = rank_regression_models(comparison)
    best = ranked[0]
    best_name = best["model"]
    best_pipe: Pipeline = best["pipeline"]

    reg_path = artifacts_dir / "regression_model.joblib"
    joblib.dump(best_pipe, reg_path)

    summary = {
        "task": "regression",
        "target": REGRESSION_TARGET,
        "filter": MODELING_FILTER,
        "n_samples": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "feature_columns": all_cols,
        "best_model": best_name,
        "best_test_metrics": best["test_metrics"],
        "best_cv_metrics": best["cv_metrics"],
        "comparison": [
            {
                "model": r["model"],
                "cv_metrics": r["cv_metrics"],
                "test_metrics": r["test_metrics"],
            }
            for r in ranked
        ],
        "artifact": str(reg_path.relative_to(PROJECT_ROOT)),
    }
    return summary


def train_classification(
    df: pd.DataFrame,
    artifacts_dir: Path,
) -> dict[str, Any]:
    y = df[CLASSIFICATION_TARGET].astype(int)
    numeric, categorical, all_cols = feature_columns(df)
    X = df[all_cols]

    pos_rate = float(y.mean())
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    preprocessor = build_preprocessor(numeric, categorical)
    comparison: list[dict[str, Any]] = []

    for name, estimator in _classification_candidates().items():
        pipe = Pipeline([("prep", preprocessor), ("model", estimator)])
        cv_metrics = _cv_classification(pipe, X_train, y_train)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        if hasattr(pipe.named_steps["model"], "predict_proba"):
            y_proba = pipe.predict_proba(X_test)[:, 1]
        else:
            y_proba = pipe.decision_function(X_test)
            y_proba = (y_proba - y_proba.min()) / (y_proba.max() - y_proba.min() + 1e-9)
        test_metrics = classification_metrics(y_test, y_pred, y_proba)
        comparison.append(
            {
                "model": name,
                "cv_metrics": cv_metrics,
                "test_metrics": test_metrics,
                "pipeline": pipe,
            }
        )

    ranked = rank_classification_models(comparison)
    best = ranked[0]
    best_name = best["model"]
    best_pipe: Pipeline = best["pipeline"]

    clf_path = artifacts_dir / "classification_model.joblib"
    prep_path = artifacts_dir / "preprocessor.joblib"
    joblib.dump(best_pipe, clf_path)
    joblib.dump(best_pipe.named_steps["prep"], prep_path)

    summary = {
        "task": "classification",
        "target": CLASSIFICATION_TARGET,
        "filter": MODELING_FILTER,
        "positive_rate": pos_rate,
        "n_samples": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "feature_columns": all_cols,
        "best_model": best_name,
        "best_test_metrics": best["test_metrics"],
        "best_cv_metrics": best["cv_metrics"],
        "comparison": [
            {
                "model": r["model"],
                "cv_metrics": r["cv_metrics"],
                "test_metrics": r["test_metrics"],
            }
            for r in ranked
        ],
        "artifact": str(clf_path.relative_to(PROJECT_ROOT)),
        "preprocessor_artifact": str(prep_path.relative_to(PROJECT_ROOT)),
    }
    return summary


def _sample_modeling_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce el frame para corridas rápidas preservando la proporción del target binario."""
    if ML_SAMPLE_SIZE <= 0 or len(df) <= ML_SAMPLE_SIZE:
        return df

    sampled_parts = []
    for _, group in df.groupby(CLASSIFICATION_TARGET, group_keys=False):
        n_group = max(1, round(ML_SAMPLE_SIZE * len(group) / len(df)))
        sampled_parts.append(
            group.sample(
                n=min(n_group, len(group)),
                random_state=RANDOM_STATE,
            )
        )
    sampled = pd.concat(sampled_parts).sample(frac=1, random_state=RANDOM_STATE)
    return sampled.head(ML_SAMPLE_SIZE).reset_index(drop=True)


def run_training(artifacts_dir: Path | None = None) -> dict[str, Any]:
    out_dir = artifacts_dir or ARTIFACTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_modeling_frame()
    if REGRESSION_TARGET not in df.columns or CLASSIFICATION_TARGET not in df.columns:
        raise ValueError("El frame de modelado debe incluir targets derivados del ETL.")
    df = _sample_modeling_frame(df)

    reg_summary = train_regression(df, out_dir)
    clf_summary = train_classification(df, out_dir)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology": {
            "regression_models": list(_regression_candidates().keys()),
            "classification_models": list(_classification_candidates().keys()),
            "cv_folds": CV_FOLDS,
            "test_size": TEST_SIZE,
            "ml_fast": ML_FAST,
            "sample_size": ML_SAMPLE_SIZE if ML_SAMPLE_SIZE > 0 else None,

            "leakage_policy": (
                "Excluye monto_pagado, ratios derivados del pago observado y etiquetas "
                "del target. Usa montos presupuestales (aprobado/modificado) y "
                "dimensiones estructurales."
            ),
            "limitations": [
                "Snapshot ciclo 2026 sin serie temporal multianual.",
                "Clasificación alta_ejecucion muy desbalanceada (~8-9% positivos).",
                "Colinealidad entre montos presupuestales puede inflar R² en regresión.",
            ],
        },
        "regression": reg_summary,
        "classification": clf_summary,
    }

    metrics_path = out_dir / "training_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    report["metrics_path"] = str(metrics_path.relative_to(PROJECT_ROOT))
    return report
