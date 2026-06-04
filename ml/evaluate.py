"""
Métricas de evaluación comparativa para regresión y clasificación desbalanceada.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    out: dict[str, float] = {
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
    }
    if y_proba is not None and len(np.unique(y_true)) > 1:
        proba = np.asarray(y_proba, dtype=float)
        out["roc_auc"] = float(roc_auc_score(y_true, proba))
        out["pr_auc"] = float(average_precision_score(y_true, proba))
    return out


def rank_regression_models(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena por RMSE CV (menor mejor), desempate por R²."""
    return sorted(
        results,
        key=lambda r: (r["cv_metrics"]["rmse_mean"], -r["cv_metrics"]["r2_mean"]),
    )


def rank_classification_models(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena por F1 CV (mayor mejor), desempate por PR-AUC."""
    return sorted(
        results,
        key=lambda r: (
            -r["cv_metrics"]["f1_mean"],
            -r["cv_metrics"].get("pr_auc_mean", 0.0),
        ),
    )
