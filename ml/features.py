"""
Preprocesamiento sklearn sin fuga: numéricos presupuestales + categóricas estructurales.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.config import (
    BUDGET_NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    FACT_DROP_COLUMNS,
    LEAKAGE_COLUMNS,
    LOW_CARDINALITY_NUMERIC,
)


def feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    """Devuelve (numéricas, categóricas, todas) usables para el pipeline."""
    banned = LEAKAGE_COLUMNS | FACT_DROP_COLUMNS
    candidate_numeric = [
        c
        for c in list(BUDGET_NUMERIC_FEATURES) + list(LOW_CARDINALITY_NUMERIC)
        if c in df.columns and c not in banned
    ]
    numeric: list[str] = []
    categorical_extra: list[str] = []
    for col in candidate_numeric:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric.append(col)
        else:
            categorical_extra.append(col)

    categorical = [
        c
        for c in list(CATEGORICAL_FEATURES) + categorical_extra
        if c in df.columns and c not in banned
    ]
    # Sin duplicados preservando orden
    seen: set[str] = set()
    categorical_unique: list[str] = []
    for c in categorical:
        if c not in seen:
            seen.add(c)
            categorical_unique.append(c)
    return numeric, categorical_unique, numeric + categorical_unique


def build_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> ColumnTransformer:
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=50),
            ),
        ]
    )
    transformers = []
    if numeric_cols:
        transformers.append(("num", numeric_pipe, numeric_cols))
    if categorical_cols:
        transformers.append(("cat", categorical_pipe, categorical_cols))
    return ColumnTransformer(transformers=transformers, remainder="drop")
