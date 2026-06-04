"""Health check y metadatos de servicio."""

from __future__ import annotations

from fastapi import APIRouter, Request

from api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    bundle = request.app.state.models
    wh_path = settings.warehouse_path
    return HealthResponse(
        status="ok",
        warehouse_ready=wh_path.exists(),
        warehouse_path=str(wh_path),
        regression_model_ready=bundle.regression_ready,
        classification_model_ready=bundle.classification_ready,
        metrics_ready=settings.metrics_path.exists(),
    )
