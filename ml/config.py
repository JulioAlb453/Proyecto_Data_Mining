"""
Configuración de tareas ML: targets, filtros y política anti-leakage.
"""

from __future__ import annotations

# Filtro alineado con data.pef_cleaning.apply_analytical_filter
MODELING_FILTER = "filtro_modelado_programable"

REGRESSION_TARGET = "ratio_ejecucion"
CLASSIFICATION_TARGET = "alta_ejecucion"

# Columnas que no deben entrar como features (fuga directa o derivadas del pago observado)
LEAKAGE_COLUMNS = frozenset(
    {
        "monto_pagado",
        "ratio_ejecucion",
        "ratio_aprobado",
        "log1p_monto_pagado",
        "sin_pago",
        "alta_ejecucion",
        "sobre_ejecucion",
        "banda_ejecucion",
        "id_clave_cartera",
        "fact_sk",
    }
)

# SKs y degeneradas del hecho (no aportan señal causal; evitan memorizar IDs)
FACT_DROP_COLUMNS = frozenset(
    {
        "fact_sk",
        "tiempo_sk",
        "ramo_sk",
        "ur_sk",
        "entidad_sk",
        "ff_sk",
        "eco_sk",
        "func_sk",
        "flag_modificado_cero",
        "flag_registro_valido",
    }
)

# Montos permitidos como features presupuestales (sin monto_pagado)
BUDGET_NUMERIC_FEATURES = (
    "monto_aprobado",
    "monto_modificado",
    "monto_aprobado_mensual",
    "monto_modificado_mensual",
)

CATEGORICAL_FEATURES = (
    "tipo_gasto",
    "desc_ramo",
    "desc_ur",
    "entidad_federativa",
    "desc_capitulo",
    "desc_concepto",
    "desc_partida_generica",
    "desc_partida_especifica",
    "desc_tipogasto",
    "desc_ff",
    "desc_gpo_funcional",
    "desc_funcion",
    "desc_subfuncion",
    "desc_ai",
    "desc_modalidad",
    "desc_pp",
)

LOW_CARDINALITY_NUMERIC = (
    "ciclo",
    "id_ramo",
    "id_ur",
    "id_entidad_federativa",
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
)

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
