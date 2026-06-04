"""
ETL PEF → DuckDB: dimensiones, hecho de ejecución y vistas OLAP.

Entrada: `pef_limpio.parquet` (preferido) o CSV vía `data.pef_cleaning`.
Filtro de carga al hecho: `filtro_olap` (sin montos negativos).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from data.paths import get_paths
from data.pef_cleaning import apply_analytical_filter, clean_pef, load_raw_pef

DIM_TIEMPO_COLS = ("ciclo",)
DIM_RAMO_COLS = ("id_ramo", "desc_ramo")
DIM_UR_COLS = ("id_ur", "desc_ur", "id_ramo", "desc_ramo")
DIM_ENTIDAD_COLS = ("id_entidad_federativa", "entidad_federativa")
DIM_FF_COLS = ("id_ff", "desc_ff")
DIM_ECO_COLS = (
    "id_capitulo",
    "desc_capitulo",
    "id_concepto",
    "desc_concepto",
    "id_partida_generica",
    "desc_partida_generica",
    "id_partida_especifica",
    "desc_partida_especifica",
    "id_tipogasto",
    "desc_tipogasto",
)
DIM_FUNC_COLS = (
    "gpo_funcional",
    "desc_gpo_funcional",
    "id_funcion",
    "desc_funcion",
    "id_subfuncion",
    "desc_subfuncion",
    "id_ai",
    "desc_ai",
    "id_modalidad",
    "desc_modalidad",
    "id_pp",
    "desc_pp",
)

FACT_MEASURES = (
    "monto_aprobado",
    "monto_modificado",
    "monto_aprobado_mensual",
    "monto_modificado_mensual",
    "monto_pagado",
)
FACT_ATTRS = (
    "tipo_gasto",
    "ratio_ejecucion",
    "ratio_aprobado",
    "log1p_monto_pagado",
    "sin_pago",
    "alta_ejecucion",
    "sobre_ejecucion",
    "banda_ejecucion",
    "flag_modificado_cero",
    "flag_registro_valido",
)


def load_olap_source() -> pd.DataFrame:
    """Carga datos limpios y aplica filtro OLAP."""
    paths = get_paths()
    parquet = paths["pef_limpio_parquet"]
    if parquet.exists():
        df = pd.read_parquet(parquet)
    else:
        df = clean_pef(load_raw_pef())
    return apply_analytical_filter(df, "filtro_olap")


def _assign_surrogate_key(dim: pd.DataFrame, sk_col: str) -> pd.DataFrame:
    out = dim.reset_index(drop=True).copy()
    out[sk_col] = range(1, len(out) + 1)
    return out


def build_dimensions(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Construye tablas de dimensión con llaves sustitutas."""
    dims: dict[str, pd.DataFrame] = {}

    dims["dim_tiempo"] = _assign_surrogate_key(
        df[list(DIM_TIEMPO_COLS)].drop_duplicates().sort_values("ciclo"),
        "tiempo_sk",
    )
    dims["dim_ramo"] = _assign_surrogate_key(
        df[list(DIM_RAMO_COLS)].drop_duplicates().sort_values(["id_ramo", "desc_ramo"]),
        "ramo_sk",
    )
    dims["dim_ur"] = _assign_surrogate_key(
        df[list(DIM_UR_COLS)].drop_duplicates().sort_values(["id_ur", "desc_ur"]),
        "ur_sk",
    )
    dims["dim_entidad"] = _assign_surrogate_key(
        df[list(DIM_ENTIDAD_COLS)]
        .drop_duplicates()
        .sort_values(["id_entidad_federativa", "entidad_federativa"]),
        "entidad_sk",
    )
    dims["dim_fuente_financiamiento"] = _assign_surrogate_key(
        df[list(DIM_FF_COLS)].drop_duplicates().sort_values(["id_ff", "desc_ff"]),
        "ff_sk",
    )
    dims["dim_clasificacion_economica"] = _assign_surrogate_key(
        df[list(DIM_ECO_COLS)].drop_duplicates().sort_values(
            ["id_capitulo", "id_concepto", "id_partida_generica", "id_partida_especifica"]
        ),
        "eco_sk",
    )
    dims["dim_clasificacion_funcional"] = _assign_surrogate_key(
        df[list(DIM_FUNC_COLS)].drop_duplicates().sort_values(
            ["gpo_funcional", "id_funcion", "id_subfuncion", "id_pp"]
        ),
        "func_sk",
    )
    return dims


def build_fact(df: pd.DataFrame, dims: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une hechos con dimensiones y devuelve tabla lista para DuckDB."""
    work = df.copy()
    if hasattr(work["banda_ejecucion"], "astype"):
        work["banda_ejecucion"] = work["banda_ejecucion"].astype(str)

    merged = work
    join_specs = [
        ("dim_tiempo", DIM_TIEMPO_COLS, "tiempo_sk"),
        ("dim_ramo", DIM_RAMO_COLS, "ramo_sk"),
        ("dim_ur", DIM_UR_COLS, "ur_sk"),
        ("dim_entidad", DIM_ENTIDAD_COLS, "entidad_sk"),
        ("dim_fuente_financiamiento", DIM_FF_COLS, "ff_sk"),
        ("dim_clasificacion_economica", DIM_ECO_COLS, "eco_sk"),
        ("dim_clasificacion_funcional", DIM_FUNC_COLS, "func_sk"),
    ]
    for dim_name, key_cols, sk_col in join_specs:
        dim = dims[dim_name][list(key_cols) + [sk_col]]
        merged = merged.merge(dim, on=list(key_cols), how="left", validate="m:1")

    missing = merged[list({s[2] for s in join_specs})].isna().any()
    if missing.any():
        bad = missing[missing].index.tolist()
        raise RuntimeError(f"Filas sin match dimensional en SKs: {bad}")

    fact_cols = (
        ["id_clave_cartera"]
        + [s[2] for s in join_specs]
        + list(FACT_MEASURES)
        + list(FACT_ATTRS)
    )
    fact = merged[fact_cols].copy()
    fact.insert(0, "fact_sk", range(1, len(fact) + 1))
    return fact


def _load_table(con: duckdb.DuckDBPyConnection, name: str, frame: pd.DataFrame) -> None:
    con.register("_etl_frame", frame)
    con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM _etl_frame")
    con.unregister("_etl_frame")


def apply_olap_views(con: duckdb.DuckDBPyConnection, sql_dir: Path) -> list[str]:
    """Ejecuta scripts SQL de vistas en orden."""
    views_file = sql_dir / "02_olap_views.sql"
    if not views_file.exists():
        raise FileNotFoundError(f"No se encontró {views_file}")
    sql = views_file.read_text(encoding="utf-8")
    con.execute(sql)
    rows = con.execute(
        """
        SELECT view_name
        FROM duckdb_views()
        WHERE schema_name = 'main' AND view_name LIKE 'vw_olap_%'
        ORDER BY view_name
        """
    ).fetchall()
    return [r[0] for r in rows]


def validate_warehouse(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    """Comprobaciones mínimas post-ETL."""
    fact_n = con.execute("SELECT COUNT(*) FROM fact_ejecucion").fetchone()[0]
    orphan = con.execute(
        """
        SELECT COUNT(*) FROM fact_ejecucion
        WHERE tiempo_sk IS NULL OR ramo_sk IS NULL OR ur_sk IS NULL
           OR entidad_sk IS NULL OR ff_sk IS NULL
           OR eco_sk IS NULL OR func_sk IS NULL
        """
    ).fetchone()[0]
    dims = {
        name: con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name in (
            "dim_tiempo",
            "dim_ramo",
            "dim_ur",
            "dim_entidad",
            "dim_fuente_financiamiento",
            "dim_clasificacion_economica",
            "dim_clasificacion_funcional",
        )
    }
    views = con.execute(
        """
        SELECT COUNT(*) FROM duckdb_views()
        WHERE schema_name = 'main' AND view_name LIKE 'vw_olap_%'
        """
    ).fetchone()[0]
    return {
        "fact_ejecucion_rows": int(fact_n),
        "orphan_fact_rows": int(orphan),
        "dimensions": dims,
        "olap_views": int(views),
        "ok": orphan == 0 and fact_n > 0 and views >= 8,
    }


def run_etl(db_path: Path | None = None, sql_dir: Path | None = None) -> dict[str, Any]:
    """Pipeline completo: staging → dimensiones → hecho → vistas."""
    paths = get_paths()
    db = db_path or paths["warehouse_db"]
    sql = sql_dir or Path(__file__).resolve().parent / "sql"
    db.parent.mkdir(parents=True, exist_ok=True)

    source = load_olap_source()
    dims = build_dimensions(source)
    fact = build_fact(source, dims)

    if db.exists():
        db.unlink()

    con = duckdb.connect(str(db))
    try:
        for table_name, frame in dims.items():
            _load_table(con, table_name, frame)
        _load_table(con, "fact_ejecucion", fact)
        view_names = apply_olap_views(con, sql)
        validation = validate_warehouse(con)
    finally:
        con.close()

    return {
        "warehouse_db": db,
        "source_rows": len(source),
        "fact_rows": len(fact),
        "dimensions": {k: len(v) for k, v in dims.items()},
        "views": view_names,
        "validation": validation,
    }
