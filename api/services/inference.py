"""Carga de pipelines sklearn y predicción en línea."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from api.config import ApiSettings
from ml.config import (
    BUDGET_NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    CLASSIFICATION_TARGET,
    REGRESSION_TARGET,
)
from ml.features import feature_columns


class ModelsNotReadyError(RuntimeError):
    """Los artefactos ML no están disponibles."""


@dataclass
class ModelBundle:
    regression: Pipeline | None
    classification: Pipeline | None
    metrics: dict[str, Any] | None
    regression_model_name: str
    classification_model_name: str
    feature_columns: list[str]
    numeric_features: list[str]
    categorical_features: list[str]

    @property
    def regression_ready(self) -> bool:
        return self.regression is not None

    @property
    def classification_ready(self) -> bool:
        return self.classification is not None


def _load_metrics(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _feature_lists_from_metrics(
    metrics: dict[str, Any] | None,
) -> tuple[list[str], list[str], list[str]]:
    if metrics:
        cols = metrics.get("regression", {}).get("feature_columns") or metrics.get(
            "classification", {}
        ).get("feature_columns")
        if cols:
            numeric = [c for c in cols if c in BUDGET_NUMERIC_FEATURES]
            categorical = [c for c in cols if c in CATEGORICAL_FEATURES]
            low_card = [c for c in cols if c not in numeric and c not in categorical]
            numeric = numeric + low_card
            return list(cols), numeric, categorical

    numeric = list(BUDGET_NUMERIC_FEATURES)
    categorical = list(CATEGORICAL_FEATURES)
    return numeric + categorical, numeric, categorical


def load_models(settings: ApiSettings) -> ModelBundle:
    metrics = _load_metrics(settings.metrics_path)
    feature_cols, numeric, categorical = _feature_lists_from_metrics(metrics)

    reg_name = metrics.get("regression", {}).get("best_model", "unknown") if metrics else "unknown"
    clf_name = (
        metrics.get("classification", {}).get("best_model", "unknown") if metrics else "unknown"
    )

    regression = None
    classification = None
    if settings.regression_model_path.exists():
        regression = joblib.load(settings.regression_model_path)
    if settings.classification_model_path.exists():
        classification = joblib.load(settings.classification_model_path)

    if metrics and metrics.get("regression", {}).get("feature_columns"):
        feature_cols = list(metrics["regression"]["feature_columns"])
        # Tipos coherentes con pipeline entrenado
        dummy = pd.DataFrame({c: [0] for c in feature_cols})
        num, cat, all_cols = feature_columns(dummy)
        numeric, categorical, feature_cols = num, cat, all_cols

    return ModelBundle(
        regression=regression,
        classification=classification,
        metrics=metrics,
        regression_model_name=reg_name,
        classification_model_name=clf_name,
        feature_columns=feature_cols,
        numeric_features=numeric,
        categorical_features=categorical,
    )


def _row_from_features(features: dict[str, Any], columns: list[str]) -> pd.DataFrame:
    row = {col: features.get(col) for col in columns}
    return pd.DataFrame([row])


def predict_regression(bundle: ModelBundle, features: dict[str, Any]) -> dict[str, Any]:
    if bundle.regression is None:
        raise ModelsNotReadyError(
            "Modelo de regresión no encontrado. Ejecute: python -m ml"
        )
    X = _row_from_features(features, bundle.feature_columns)
    pred = float(bundle.regression.predict(X)[0])
    return {
        "target": REGRESSION_TARGET,
        "prediction": pred,
        "model": bundle.regression_model_name,
        "note": (
            "Predicción de ratio de ejecución con montos presupuestales y dimensiones "
            "estructurales; no incluye monto_pagado observado."
        ),
    }


def predict_classification(bundle: ModelBundle, features: dict[str, Any]) -> dict[str, Any]:
    if bundle.classification is None:
        raise ModelsNotReadyError(
            "Modelo de clasificación no encontrado. Ejecute: python -m ml"
        )
    X = _row_from_features(features, bundle.feature_columns)
    pred = int(bundle.classification.predict(X)[0])
    model_step = bundle.classification.named_steps["model"]
    if hasattr(model_step, "predict_proba"):
        proba = float(bundle.classification.predict_proba(X)[0, 1])
    else:
        score = bundle.classification.decision_function(X)[0]
        proba = float(1.0 / (1.0 + pow(2.718281828, -score)))
    return {
        "target": CLASSIFICATION_TARGET,
        "prediction": pred,
        "probability_positive": proba,
        "model": bundle.classification_model_name,
        "note": (
            "Clasificación alta_ejecucion (ratio ≥ umbral en entrenamiento). "
            "Métricas orientadas a desbalance (F1, PR-AUC)."
        ),
    }


def model_info(bundle: ModelBundle) -> dict[str, Any]:
    info: dict[str, Any] = {
        "feature_columns": bundle.feature_columns,
        "numeric_features": bundle.numeric_features,
        "categorical_features": bundle.categorical_features,
    }
    if bundle.metrics:
        info["regression"] = {
            "target": bundle.metrics.get("regression", {}).get("target"),
            "best_model": bundle.regression_model_name,
            "best_test_metrics": bundle.metrics.get("regression", {}).get("best_test_metrics"),
        }
        info["classification"] = {
            "target": bundle.metrics.get("classification", {}).get("target"),
            "best_model": bundle.classification_model_name,
            "best_test_metrics": bundle.metrics.get("classification", {}).get(
                "best_test_metrics"
            ),
            "positive_rate": bundle.metrics.get("classification", {}).get("positive_rate"),
        }
    return info
