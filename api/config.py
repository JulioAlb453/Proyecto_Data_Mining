"""Configuración de la API desde variables de entorno."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from data.paths import PROJECT_ROOT, load_project_env


def _resolve_path(value: str, base: Path = PROJECT_ROOT) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

    warehouse_db: str = "warehouse/warehouse.duckdb"
    ml_regression_model: str = "ml/artifacts/regression_model.joblib"
    ml_classification_model: str = "ml/artifacts/classification_model.joblib"
    ml_metrics_json: str = "ml/artifacts/training_metrics.json"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_title: str = "PEF Full Stack API"
    api_version: str = "1.0.0"
    default_olap_limit: int = 500
    max_olap_limit: int = 5000

    @property
    def warehouse_path(self) -> Path:
        return _resolve_path(self.warehouse_db)

    @property
    def regression_model_path(self) -> Path:
        return _resolve_path(self.ml_regression_model)

    @property
    def classification_model_path(self) -> Path:
        return _resolve_path(self.ml_classification_model)

    @property
    def metrics_path(self) -> Path:
        return _resolve_path(self.ml_metrics_json)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> ApiSettings:
    load_project_env()
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        return ApiSettings(_env_file=env_file)
    example = PROJECT_ROOT / ".env.example"
    if example.exists():
        return ApiSettings(_env_file=example)
    return ApiSettings(
        warehouse_db=os.getenv("WAREHOUSE_DB", "warehouse/warehouse.duckdb"),
        ml_regression_model=os.getenv(
            "ML_REGRESSION_MODEL", "ml/artifacts/regression_model.joblib"
        ),
        ml_classification_model=os.getenv(
            "ML_CLASSIFICATION_MODEL", "ml/artifacts/classification_model.joblib"
        ),
        cors_origins=os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ),
    )
