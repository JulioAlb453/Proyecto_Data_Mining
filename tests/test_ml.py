"""Pruebas mínimas del módulo ML."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pytest

from data.paths import PROJECT_ROOT, get_paths
from ml.config import CLASSIFICATION_TARGET, LEAKAGE_COLUMNS, REGRESSION_TARGET
from ml.data import load_modeling_frame
from ml.features import feature_columns


@pytest.fixture(scope="module")
def warehouse_available() -> bool:
    return get_paths()["warehouse_db"].exists()


def test_load_modeling_frame(warehouse_available: bool) -> None:
    if not warehouse_available:
        pytest.skip("warehouse.duckdb no construido")
    df = load_modeling_frame()
    assert len(df) > 10_000
    assert (df["tipo_gasto"] == "PROGRAMABLE").all()
    assert (df["monto_modificado"] > 0).all()


def test_no_leakage_in_features(warehouse_available: bool) -> None:
    if not warehouse_available:
        pytest.skip("warehouse.duckdb no construido")
    df = load_modeling_frame()
    _, _, all_cols = feature_columns(df)
    overlap = set(all_cols) & LEAKAGE_COLUMNS
    assert not overlap, f"Fuga en features: {overlap}"


@pytest.mark.slow
def test_training_artifacts(warehouse_available: bool) -> None:
    if not warehouse_available:
        pytest.skip("warehouse.duckdb no construido")
    from ml.train import run_training

    report = run_training()
    art = PROJECT_ROOT / "ml" / "artifacts"
    assert (art / "regression_model.joblib").exists()
    assert (art / "classification_model.joblib").exists()
    assert (art / "training_metrics.json").exists()

    reg = joblib.load(art / "regression_model.joblib")
    clf = joblib.load(art / "classification_model.joblib")
    assert hasattr(reg, "predict")
    assert hasattr(clf, "predict")

    metrics = json.loads((art / "training_metrics.json").read_text(encoding="utf-8"))
    assert metrics["regression"]["target"] == REGRESSION_TARGET
    assert metrics["classification"]["target"] == CLASSIFICATION_TARGET
    assert len(metrics["regression"]["comparison"]) >= 2
    assert len(metrics["classification"]["comparison"]) >= 2
