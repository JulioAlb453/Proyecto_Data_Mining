"""
Perfilado, limpieza y variables derivadas para PEF_avance_gasto.csv.

Salidas típicas en data/processed/:
  - pef_limpio.parquet (registro completo con flags y derivadas)
  - pef_analitico.parquet (filtro base para OLAP/ML)
  - profile_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from data.paths import get_paths

# Umbrales acordados con el plan (ajustables en un solo lugar)
RATIO_ALTA_EJECUCION = 0.80
RATIO_MEDIA_EJECUCION = 0.50
MONTO_COLUMNS = (
    "monto_aprobado",
    "monto_modificado",
    "monto_aprobado_mensual",
    "monto_modificado_mensual",
    "monto_pagado",
)

ID_TEXT_COLUMNS = (
    "desc_ramo",
    "id_ur",
    "desc_ur",
    "desc_gpo_funcional",
    "desc_funcion",
    "desc_subfuncion",
    "desc_ai",
    "id_modalidad",
    "desc_modalidad",
    "desc_pp",
    "desc_capitulo",
    "desc_concepto",
    "desc_partida_generica",
    "desc_partida_especifica",
    "desc_tipogasto",
    "desc_ff",
    "entidad_federativa",
    "tipo_gasto",
)

DERIVED_COLUMN_DOCS: dict[str, str] = {
    "ratio_ejecucion": "monto_pagado / monto_modificado cuando modificado > 0; NaN si no aplica.",
    "ratio_aprobado": "monto_pagado / monto_aprobado cuando aprobado > 0.",
    "log1p_monto_pagado": "log(1 + max(monto_pagado, 0)) para regresión con colas pesadas.",
    "sin_pago": "modificado > 0 y monto_pagado == 0 (rezago total de pago).",
    "alta_ejecucion": f"ratio_ejecucion >= {RATIO_ALTA_EJECUCION} con modificado > 0.",
    "sobre_ejecucion": "ratio_ejecucion > 1 con modificado > 0.",
    "banda_ejecucion": "categoría ordenada: sin_base | sin_pago | baja | media | alta | sobre.",
    "flag_montos_negativos": "algún monto presupuestal < 0 (registro anómalo).",
    "flag_modificado_cero": "monto_modificado == 0 (sin base para ratio).",
    "flag_registro_valido": "pasa controles mínimos de calidad para modelado.",
}

ANALYTICAL_FILTER_SPECS: dict[str, str] = {
    "filtro_olap": (
        "Todos los registros con montos no negativos y sin duplicados exactos; "
        "incluye modificado == 0 para agregados presupuestales."
    ),
    "filtro_modelado_ratio": (
        "flag_registro_valido, monto_modificado > 0, sin montos negativos; "
        "excluye filas donde ratio no está definido."
    ),
    "filtro_modelado_programable": (
        "filtro_modelado_ratio y tipo_gasto == 'PROGRAMABLE' "
        "(reduce sesgo por 203 filas NO PROGRAMABLE)."
    ),
    "filtro_clasificacion_sin_pago": (
        "monto_modificado > 0 y montos no negativos; target sin_pago."
    ),
}


def load_raw_pef(csv_path: Path | None = None) -> pd.DataFrame:
    paths = get_paths()
    path = csv_path or paths["raw_csv"]
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el CSV en {path}. "
            "Copie PEF_avance_gasto.csv a data/raw/ o defina PEF_RAW_CSV en .env."
        )
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    if df["desc_ramo"].str.contains("\ufffd", na=False).any():
        df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    return df


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in MONTO_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["ciclo"] = pd.to_numeric(out["ciclo"], errors="coerce").astype("Int64")
    out["id_clave_cartera"] = pd.to_numeric(
        out["id_clave_cartera"], errors="coerce"
    ).astype("Int64")
    for col in ID_TEXT_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip()
    for col in (
        "id_ramo",
        "gpo_funcional",
        "id_funcion",
        "id_subfuncion",
        "id_ai",
        "id_pp",
        "id_capitulo",
        "id_concepto",
        "id_partida_generica",
        "id_partida_especifica",
        "id_tipogasto",
        "id_ff",
        "id_entidad_federativa",
    ):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def build_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mod = out["monto_modificado"]
    apr = out["monto_aprobado"]
    pag = out["monto_pagado"]

    out["flag_montos_negativos"] = (out[list(MONTO_COLUMNS)] < 0).any(axis=1)
    out["flag_modificado_cero"] = mod == 0
    out["flag_modificado_negativo"] = mod < 0

    base_ratio = mod > 0
    out["ratio_ejecucion"] = np.where(base_ratio, pag / mod, np.nan)
    out["ratio_aprobado"] = np.where(apr > 0, pag / apr, np.nan)
    out["log1p_monto_pagado"] = np.log1p(pag.clip(lower=0))

    out["sin_pago"] = (mod > 0) & (pag == 0)
    out["alta_ejecucion"] = base_ratio & (out["ratio_ejecucion"] >= RATIO_ALTA_EJECUCION)
    out["sobre_ejecucion"] = base_ratio & (out["ratio_ejecucion"] > 1.0)

    banda = np.full(len(out), "sin_base", dtype=object)
    banda[out["flag_modificado_cero"] & ~out["flag_modificado_negativo"]] = "sin_base"
    valid = base_ratio & ~out["flag_montos_negativos"]
    banda[valid & out["sin_pago"]] = "sin_pago"
    ratio = out.loc[valid, "ratio_ejecucion"]
    idx = ratio.index
    banda[idx[ratio < RATIO_MEDIA_EJECUCION]] = "baja"
    banda[idx[(ratio >= RATIO_MEDIA_EJECUCION) & (ratio < RATIO_ALTA_EJECUCION)]] = "media"
    banda[idx[(ratio >= RATIO_ALTA_EJECUCION) & (ratio <= 1.0)]] = "alta"
    banda[idx[ratio > 1.0]] = "sobre"
    out["banda_ejecucion"] = pd.Categorical(
        banda,
        categories=["sin_base", "sin_pago", "baja", "media", "alta", "sobre"],
        ordered=True,
    )

    out["flag_registro_valido"] = (
        ~out["flag_montos_negativos"]
        & ~out["flag_modificado_negativo"]
        & out["ciclo"].notna()
    )
    return out


def clean_pef(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos, elimina duplicados exactos y añade derivadas y flags."""
    out = _coerce_types(df)
    n_dup = int(out.duplicated().sum())
    if n_dup:
        out = out.drop_duplicates().reset_index(drop=True)
    out = build_derived_features(out)
    out.attrs["duplicados_eliminados"] = n_dup
    return out


def apply_analytical_filter(df: pd.DataFrame, name: str) -> pd.DataFrame:
    if name == "filtro_olap":
        return df[~df["flag_montos_negativos"]].copy()
    if name == "filtro_modelado_ratio":
        return df[df["flag_registro_valido"] & (df["monto_modificado"] > 0)].copy()
    if name == "filtro_modelado_programable":
        base = apply_analytical_filter(df, "filtro_modelado_ratio")
        return base[base["tipo_gasto"] == "PROGRAMABLE"].copy()
    if name == "filtro_clasificacion_sin_pago":
        return df[
            df["flag_registro_valido"] & (df["monto_modificado"] > 0)
        ].copy()
    raise ValueError(f"Filtro desconocido: {name}. Opciones: {list(ANALYTICAL_FILTER_SPECS)}")


def profile_raw(df: pd.DataFrame) -> dict[str, Any]:
    """Perfil estructural del dataset (crudo o ya tipado)."""
    summary: dict[str, Any] = {
        "n_filas": int(len(df)),
        "n_columnas": int(len(df.columns)),
        "columnas": list(df.columns),
        "ciclo_valores": df["ciclo"].dropna().unique().tolist() if "ciclo" in df else [],
        "duplicados_exactos": int(df.duplicated().sum()),
        "nulos_por_columna": df.isna().sum().to_dict(),
        "tipo_gasto": df["tipo_gasto"].value_counts().to_dict()
        if "tipo_gasto" in df
        else {},
        "desc_tipogasto_top10": df["desc_tipogasto"].value_counts().head(10).to_dict()
        if "desc_tipogasto" in df
        else {},
        "cardinalidad": {
            "id_ramo": int(df["id_ramo"].nunique()),
            "id_ur": int(df["id_ur"].nunique()),
            "entidad_federativa": int(df["entidad_federativa"].nunique()),
        },
    }
    montos: dict[str, Any] = {}
    for col in MONTO_COLUMNS:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        montos[col] = {
            "min": float(s.min()),
            "max": float(s.max()),
            "media": float(s.mean()),
            "mediana": float(s.median()),
            "negativos": int((s < 0).sum()),
            "nulos": int(s.isna().sum()),
            "p95": float(s.quantile(0.95)),
            "p99": float(s.quantile(0.99)),
        }
    summary["montos"] = montos

    mod = pd.to_numeric(df["monto_modificado"], errors="coerce")
    pag = pd.to_numeric(df["monto_pagado"], errors="coerce")
    mask = mod > 0
    ratio = pag[mask] / mod[mask]
    summary["ratio_ejecucion_crudo"] = {
        "filas_con_modificado_positivo": int(mask.sum()),
        "modificado_cero": int((mod == 0).sum()),
        "modificado_negativo": int((mod < 0).sum()),
        "mediana": float(ratio.median()),
        "p95": float(ratio.quantile(0.95)),
        "p99": float(ratio.quantile(0.99)),
        "sobre_ejecucion_gt_1": int((ratio > 1).sum()),
        "sin_pago": int(((mod > 0) & (pag == 0)).sum()),
    }
    return summary


def profile_clean(df: pd.DataFrame) -> dict[str, Any]:
    base = profile_raw(df)
    base["flags"] = {
        "flag_montos_negativos": int(df["flag_montos_negativos"].sum()),
        "flag_modificado_cero": int(df["flag_modificado_cero"].sum()),
        "flag_registro_valido": int(df["flag_registro_valido"].sum()),
        "sin_pago": int(df["sin_pago"].sum()),
        "alta_ejecucion": int(df["alta_ejecucion"].sum()),
        "sobre_ejecucion": int(df["sobre_ejecucion"].sum()),
    }
    base["banda_ejecucion"] = df["banda_ejecucion"].value_counts().astype(int).to_dict()
    filtros = {}
    for name in ANALYTICAL_FILTER_SPECS:
        filtros[name] = int(len(apply_analytical_filter(df, name)))
    base["filtros_analiticos_n_filas"] = filtros
    base["umbrales"] = {
        "RATIO_ALTA_EJECUCION": RATIO_ALTA_EJECUCION,
        "RATIO_MEDIA_EJECUCION": RATIO_MEDIA_EJECUCION,
    }
    if "duplicados_eliminados" in df.attrs:
        base["duplicados_eliminados"] = df.attrs["duplicados_eliminados"]
    return base


def save_processed(
    df_limpio: pd.DataFrame,
    df_analitico: pd.DataFrame,
    profile: dict[str, Any],
    processed_dir: Path | None = None,
) -> dict[str, Path]:
    paths = get_paths()
    out_dir = processed_dir or paths["processed_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    limpio_path = out_dir / "pef_limpio.parquet"
    analitico_path = out_dir / "pef_analitico.parquet"
    profile_path = out_dir / "profile_summary.json"

    df_limpio.to_parquet(limpio_path, index=False)
    df_analitico.to_parquet(analitico_path, index=False)
    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return {
        "pef_limpio": limpio_path,
        "pef_analitico": analitico_path,
        "profile_summary": profile_path,
    }


def run_pipeline(csv_path: Path | None = None) -> dict[str, Any]:
    raw = load_raw_pef(csv_path)
    profile_before = profile_raw(raw)
    limpio = clean_pef(raw)
    profile_after = profile_clean(limpio)
    profile_after["perfil_entrada"] = profile_before
    analitico = apply_analytical_filter(limpio, "filtro_modelado_programable")
    paths_written = save_processed(limpio, analitico, profile_after)
    return {
        "profile": profile_after,
        "paths": paths_written,
        "n_limpio": len(limpio),
        "n_analitico": len(analitico),
    }
