"""Esquemas Pydantic para contratos de la API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

OlapAxis = Literal[
    "global",
    "ramo",
    "ur",
    "entidad",
    "capitulo",
    "programa",
    "fuente",
    "banda",
    "tipo_gasto",
]


class HealthResponse(BaseModel):
    status: str
    warehouse_ready: bool
    warehouse_path: str
    regression_model_ready: bool
    classification_model_ready: bool
    metrics_ready: bool


class OlapMetaResponse(BaseModel):
    axes: list[str]
    views: dict[str, str]
    filterable_star_fields: list[str]


class OlapQueryResponse(BaseModel):
    axis: str
    view: str
    row_count: int
    filters_applied: dict[str, Any]
    data: list[dict[str, Any]]


class OlapStarResponse(BaseModel):
    row_count: int
    limit: int
    offset: int
    filters_applied: dict[str, Any]
    data: list[dict[str, Any]]


class DimensionValuesResponse(BaseModel):
    dimension: str
    values: list[dict[str, Any]]


class ModelInfoResponse(BaseModel):
    regression: dict[str, Any] | None = None
    classification: dict[str, Any] | None = None
    feature_columns: list[str] = Field(default_factory=list)
    numeric_features: list[str] = Field(default_factory=list)
    categorical_features: list[str] = Field(default_factory=list)


class PredictionFeatures(BaseModel):
    """Features de inferencia alineadas con ml.config (sin targets ni fuga)."""

    tipo_gasto: str | None = "PROGRAMABLE"
    monto_aprobado: float | None = None
    monto_modificado: float | None = None
    monto_aprobado_mensual: float | None = None
    monto_modificado_mensual: float | None = None
    ciclo: int | None = None
    id_ramo: int | None = None
    desc_ramo: str | None = None
    id_ur: int | None = None
    desc_ur: str | None = None
    id_entidad_federativa: int | None = None
    entidad_federativa: str | None = None
    id_capitulo: int | None = None
    desc_capitulo: str | None = None
    id_concepto: int | None = None
    desc_concepto: str | None = None
    id_partida_generica: int | None = None
    desc_partida_generica: str | None = None
    id_partida_especifica: int | None = None
    desc_partida_especifica: str | None = None
    id_tipogasto: int | None = None
    desc_tipogasto: str | None = None
    id_ff: int | None = None
    desc_ff: str | None = None
    gpo_funcional: int | None = None
    desc_gpo_funcional: str | None = None
    id_funcion: int | None = None
    desc_funcion: str | None = None
    id_subfuncion: int | None = None
    desc_subfuncion: str | None = None
    id_ai: int | None = None
    desc_ai: str | None = None
    id_modalidad: int | None = None
    desc_modalidad: str | None = None
    id_pp: int | None = None
    desc_pp: str | None = None

    def to_feature_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.model_dump().items() if v is not None}


class RegressionPredictionResponse(BaseModel):
    target: str
    prediction: float
    model: str
    note: str


class ClassificationPredictionResponse(BaseModel):
    target: str
    prediction: int
    probability_positive: float
    model: str
    note: str
