"""Pruebas de contrato API (OLAP e inferencia)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from api.config import get_settings
from warehouse.etl import run_etl


@pytest.fixture(scope="module")
def warehouse_db(tmp_path_factory):
    db = tmp_path_factory.mktemp("api_wh") / "api_test.duckdb"
    run_etl(db_path=db)
    return db


@pytest.fixture
def client(warehouse_db, monkeypatch):
    monkeypatch.setenv("WAREHOUSE_DB", str(warehouse_db))
    get_settings.cache_clear()
    from api.main import app

    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["warehouse_ready"] is True


def test_olap_meta(client):
    r = client.get("/olap/meta")
    assert r.status_code == 200
    axes = r.json()["axes"]
    assert "ramo" in axes
    assert "global" in axes


def test_olap_kpis(client):
    r = client.get("/olap/kpis")
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) >= 1
    assert "n_registros" in data[0]


def test_olap_aggregate_ramo(client):
    r = client.get("/olap/aggregate/ramo", params={"limit": 5})
    assert r.status_code == 200
    assert r.json()["axis"] == "ramo"
    assert len(r.json()["data"]) <= 5


def test_olap_star_pagination(client):
    r = client.get("/olap/star", params={"limit": 3, "offset": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["row_count"] > 0
    assert len(body["data"]) <= 3


def test_olap_dimension_ramo(client):
    r = client.get("/olap/dimensions/ramo")
    assert r.status_code == 200
    assert len(r.json()["values"]) >= 1


def test_predict_schema(client):
    r = client.get("/predict/schema")
    assert r.status_code == 200
    assert "feature_columns" in r.json()


@pytest.mark.skipif(
    not (
        os.getenv("RUN_API_ML_TESTS") == "1"
        or (
            __import__("pathlib").Path(__file__).resolve().parents[1]
            / "ml"
            / "artifacts"
            / "regression_model.joblib"
        ).exists()
    ),
    reason="Artefactos ML no entrenados",
)
def test_predict_regression_with_artifacts(client):
    schema = client.get("/predict/schema").json()
    cols = schema["feature_columns"]
    payload = {c: 0 for c in cols}
    if "tipo_gasto" in payload:
        payload["tipo_gasto"] = "PROGRAMABLE"
    if "monto_modificado" in payload:
        payload["monto_modificado"] = 1_000_000.0
    if "monto_aprobado" in payload:
        payload["monto_aprobado"] = 1_000_000.0
    r = client.post("/predict/regression", json=payload)
    assert r.status_code == 200
    assert "prediction" in r.json()
