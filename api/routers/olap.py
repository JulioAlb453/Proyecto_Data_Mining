"""Endpoints de consulta OLAP."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from api.db import WarehouseNotFoundError, get_warehouse
from api.schemas import (
    DimensionValuesResponse,
    OlapMetaResponse,
    OlapQueryResponse,
    OlapStarResponse,
    OlapAxis,
)
from api.services import olap as olap_service

router = APIRouter(prefix="/olap", tags=["olap"])


def _clamp_limit(request: Request, limit: int) -> int:
    settings = request.app.state.settings
    return max(1, min(limit, settings.max_olap_limit))


@router.get("/meta", response_model=OlapMetaResponse)
def olap_meta() -> OlapMetaResponse:
    return OlapMetaResponse(
        axes=olap_service.list_axes(),
        views=olap_service.OLAP_VIEWS,
        filterable_star_fields=sorted(olap_service.STAR_FILTER_COLUMNS),
    )


@router.get("/kpis", response_model=OlapQueryResponse)
def olap_kpis(
    request: Request,
    ciclo: int | None = Query(None),
    limit: int = Query(50, ge=1),
) -> OlapQueryResponse:
    return _aggregate(request, "global", ciclo=ciclo, limit=limit)


@router.get("/aggregate/{axis}", response_model=OlapQueryResponse)
def olap_aggregate(
    request: Request,
    axis: OlapAxis,
    ciclo: int | None = Query(None),
    id_ramo: int | None = Query(None),
    desc_ramo: str | None = Query(None),
    id_ur: int | None = Query(None),
    desc_ur: str | None = Query(None),
    id_entidad_federativa: int | None = Query(None),
    entidad_federativa: str | None = Query(None),
    id_capitulo: int | None = Query(None),
    desc_capitulo: str | None = Query(None),
    id_pp: int | None = Query(None),
    desc_pp: str | None = Query(None),
    id_funcion: int | None = Query(None),
    id_ff: int | None = Query(None),
    desc_ff: str | None = Query(None),
    banda_ejecucion: str | None = Query(None),
    tipo_gasto: str | None = Query(None),
    limit: int = Query(100, ge=1),
) -> OlapQueryResponse:
    return _aggregate(
        request,
        axis,
        ciclo=ciclo,
        id_ramo=id_ramo,
        desc_ramo=desc_ramo,
        id_ur=id_ur,
        desc_ur=desc_ur,
        id_entidad_federativa=id_entidad_federativa,
        entidad_federativa=entidad_federativa,
        id_capitulo=id_capitulo,
        desc_capitulo=desc_capitulo,
        id_pp=id_pp,
        desc_pp=desc_pp,
        id_funcion=id_funcion,
        id_ff=id_ff,
        desc_ff=desc_ff,
        banda_ejecucion=banda_ejecucion,
        tipo_gasto=tipo_gasto,
        limit=limit,
    )


def _aggregate(request: Request, axis: str, limit: int = 100, **filters: Any) -> OlapQueryResponse:
    wh = get_warehouse()
    try:
        result = olap_service.query_aggregate(
            wh,
            axis=axis,
            filters=filters,
            limit=_clamp_limit(request, limit),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WarehouseNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return OlapQueryResponse(**result)


@router.get("/star", response_model=OlapStarResponse)
def olap_star(
    request: Request,
    ciclo: int | None = Query(None),
    id_ramo: int | None = Query(None),
    id_ur: int | None = Query(None),
    id_entidad_federativa: int | None = Query(None),
    entidad_federativa: str | None = Query(None),
    id_capitulo: int | None = Query(None),
    id_ff: int | None = Query(None),
    id_pp: int | None = Query(None),
    tipo_gasto: str | None = Query(None),
    banda_ejecucion: str | None = Query(None),
    desc_ramo: str | None = Query(None),
    desc_ur: str | None = Query(None),
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
) -> OlapStarResponse:
    wh = get_warehouse()
    settings = request.app.state.settings
    lim = _clamp_limit(request, limit)
    filters = {
        "ciclo": ciclo,
        "id_ramo": id_ramo,
        "id_ur": id_ur,
        "id_entidad_federativa": id_entidad_federativa,
        "entidad_federativa": entidad_federativa,
        "id_capitulo": id_capitulo,
        "id_ff": id_ff,
        "id_pp": id_pp,
        "tipo_gasto": tipo_gasto,
        "banda_ejecucion": banda_ejecucion,
        "desc_ramo": desc_ramo,
        "desc_ur": desc_ur,
    }
    try:
        result = olap_service.query_star(wh, filters=filters, limit=lim, offset=offset)
    except WarehouseNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if lim > settings.max_olap_limit:
        result["limit"] = settings.max_olap_limit
    return OlapStarResponse(**result)


@router.get("/dimensions/{dimension}", response_model=DimensionValuesResponse)
def olap_dimension_values(dimension: str) -> DimensionValuesResponse:
    wh = get_warehouse()
    try:
        values = olap_service.query_dimension(wh, dimension)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WarehouseNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DimensionValuesResponse(dimension=dimension, values=values)
