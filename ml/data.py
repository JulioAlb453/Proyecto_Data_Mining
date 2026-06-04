"""
Carga del dataset de modelado desde warehouse DuckDB o parquet analítico.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from data.paths import get_paths
from data.pef_cleaning import apply_analytical_filter, clean_pef, load_raw_pef

from ml.config import MODELING_FILTER

_STAR_QUERY = """
SELECT
    f.fact_sk,
    f.tiempo_sk,
    f.ramo_sk,
    f.ur_sk,
    f.entidad_sk,
    f.ff_sk,
    f.eco_sk,
    f.func_sk,
    f.id_clave_cartera,
    f.monto_aprobado,
    f.monto_modificado,
    f.monto_aprobado_mensual,
    f.monto_modificado_mensual,
    f.monto_pagado,
    f.tipo_gasto,
    f.ratio_ejecucion,
    f.ratio_aprobado,
    f.log1p_monto_pagado,
    f.sin_pago,
    f.alta_ejecucion,
    f.sobre_ejecucion,
    CAST(f.banda_ejecucion AS VARCHAR) AS banda_ejecucion,
    f.flag_modificado_cero,
    f.flag_registro_valido,
    t.ciclo,
    r.id_ramo,
    r.desc_ramo,
    u.id_ur,
    u.desc_ur,
    e.id_entidad_federativa,
    e.entidad_federativa,
    ec.id_capitulo,
    ec.desc_capitulo,
    ec.id_concepto,
    ec.desc_concepto,
    ec.id_partida_generica,
    ec.desc_partida_generica,
    ec.id_partida_especifica,
    ec.desc_partida_especifica,
    ec.id_tipogasto,
    ec.desc_tipogasto,
    ff.id_ff,
    ff.desc_ff,
    fn.gpo_funcional,
    fn.desc_gpo_funcional,
    fn.id_funcion,
    fn.desc_funcion,
    fn.id_subfuncion,
    fn.desc_subfuncion,
    fn.id_ai,
    fn.desc_ai,
    fn.id_modalidad,
    fn.desc_modalidad,
    fn.id_pp,
    fn.desc_pp
FROM fact_ejecucion f
JOIN dim_tiempo t ON f.tiempo_sk = t.tiempo_sk
JOIN dim_ramo r ON f.ramo_sk = r.ramo_sk
JOIN dim_ur u ON f.ur_sk = u.ur_sk
JOIN dim_entidad e ON f.entidad_sk = e.entidad_sk
JOIN dim_clasificacion_economica ec ON f.eco_sk = ec.eco_sk
JOIN dim_fuente_financiamiento ff ON f.ff_sk = ff.ff_sk
JOIN dim_clasificacion_funcional fn ON f.func_sk = fn.func_sk
WHERE f.monto_modificado > 0
  AND f.flag_registro_valido
  AND f.tipo_gasto = 'PROGRAMABLE'
"""


def load_from_warehouse(db_path: Path | None = None) -> pd.DataFrame:
    paths = get_paths()
    db = db_path or paths["warehouse_db"]
    if not db.exists():
        raise FileNotFoundError(
            f"No existe {db}. Ejecute: python -m warehouse.build"
        )
    con = duckdb.connect(str(db), read_only=True)
    try:
        return con.execute(_STAR_QUERY).fetchdf()
    finally:
        con.close()


def load_from_processed() -> pd.DataFrame | None:
    paths = get_paths()
    analitico = paths["processed_dir"] / "pef_analitico.parquet"
    if analitico.exists():
        return pd.read_parquet(analitico)
    limpio = paths["pef_limpio_parquet"]
    if limpio.exists():
        df = pd.read_parquet(limpio)
        return apply_analytical_filter(df, MODELING_FILTER)
    return None


def load_modeling_frame(
    db_path: Path | None = None,
    csv_path: Path | None = None,
) -> pd.DataFrame:
    """
    Orden de preferencia: warehouse → parquet procesado → CSV + limpieza.
    """
    paths = get_paths()
    db = db_path or paths["warehouse_db"]
    if db.exists():
        return load_from_warehouse(db)

    processed = load_from_processed()
    if processed is not None:
        if "banda_ejecucion" in processed.columns:
            processed = processed.copy()
            processed["banda_ejecucion"] = processed["banda_ejecucion"].astype(str)
        return processed

    raw = load_raw_pef(csv_path)
    limpio = clean_pef(raw)
    return apply_analytical_filter(limpio, MODELING_FILTER)
