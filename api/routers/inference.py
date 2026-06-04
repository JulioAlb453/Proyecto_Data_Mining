"""Endpoints de inferencia ML."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from api.schemas import (
    ClassificationPredictionResponse,
    ModelInfoResponse,
    PredictionFeatures,
    RegressionPredictionResponse,
)
from api.services.inference import ModelsNotReadyError, model_info, predict_classification, predict_regression

router = APIRouter(prefix="/predict", tags=["predict"])


@router.get("/schema", response_model=ModelInfoResponse)
def predict_schema(request: Request) -> ModelInfoResponse:
    bundle = request.app.state.models
    info = model_info(bundle)
    return ModelInfoResponse(**info)


@router.post("/regression", response_model=RegressionPredictionResponse)
def predict_regression_endpoint(
    request: Request,
    body: PredictionFeatures,
) -> RegressionPredictionResponse:
    bundle = request.app.state.models
    try:
        result = predict_regression(bundle, body.to_feature_dict())
    except ModelsNotReadyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error en predicción: {exc}") from exc
    return RegressionPredictionResponse(**result)


@router.post("/classification", response_model=ClassificationPredictionResponse)
def predict_classification_endpoint(
    request: Request,
    body: PredictionFeatures,
) -> ClassificationPredictionResponse:
    bundle = request.app.state.models
    try:
        result = predict_classification(bundle, body.to_feature_dict())
    except ModelsNotReadyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error en predicción: {exc}") from exc
    return ClassificationPredictionResponse(**result)
