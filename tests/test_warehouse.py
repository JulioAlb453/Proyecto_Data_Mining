"""Pruebas mínimas del ETL warehouse."""

from __future__ import annotations

import duckdb
import pytest

from data.paths import get_paths
from warehouse.etl import run_etl


@pytest.fixture(scope="module")
def warehouse_result(tmp_path_factory):
    paths = get_paths()
    db = tmp_path_factory.mktemp("wh") / "test_warehouse.duckdb"
    return run_etl(db_path=db)


def test_build_ok(warehouse_result):
    assert warehouse_result["validation"]["ok"]
    assert warehouse_result["fact_rows"] == warehouse_result["source_rows"]
    assert warehouse_result["validation"]["orphan_fact_rows"] == 0


def test_olap_views_queryable(warehouse_result):
    db = warehouse_result["warehouse_db"]
    con = duckdb.connect(str(db))
    try:
        n = con.execute("SELECT COUNT(*) FROM vw_olap_star").fetchone()[0]
        assert n == warehouse_result["fact_rows"]
        kpis = con.execute("SELECT ciclo, n_registros FROM vw_olap_kpis_global").fetchdf()
        assert len(kpis) >= 1
        assert int(kpis["n_registros"].iloc[0]) == warehouse_result["fact_rows"]
    finally:
        con.close()
