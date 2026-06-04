"""Consultas OLAP sobre vistas vw_olap_* en DuckDB."""

from __future__ import annotations

from typing import Any

from api.db import WarehouseConnection

OLAP_VIEWS: dict[str, str] = {
    "global": "vw_olap_kpis_global",
    "ramo": "vw_olap_ejecucion_por_ramo",
    "ur": "vw_olap_ejecucion_por_ur",
    "entidad": "vw_olap_ejecucion_por_entidad",
    "capitulo": "vw_olap_ejecucion_por_capitulo",
    "programa": "vw_olap_ejecucion_por_programa",
    "fuente": "vw_olap_ejecucion_por_fuente",
    "banda": "vw_olap_ejecucion_por_banda",
    "tipo_gasto": "vw_olap_ejecucion_por_tipo_gasto",
}

STAR_FILTER_COLUMNS = frozenset(
    {
        "ciclo",
        "id_ramo",
        "id_ur",
        "id_entidad_federativa",
        "entidad_federativa",
        "id_capitulo",
        "id_ff",
        "id_pp",
        "tipo_gasto",
        "banda_ejecucion",
        "desc_ramo",
        "desc_ur",
    }
)

AGGREGATE_FILTER_COLUMNS: dict[str, frozenset[str]] = {
    "ramo": frozenset({"ciclo", "id_ramo", "desc_ramo"}),
    "ur": frozenset({"ciclo", "id_ramo", "id_ur", "desc_ur"}),
    "entidad": frozenset({"ciclo", "id_entidad_federativa", "entidad_federativa"}),
    "capitulo": frozenset({"ciclo", "id_capitulo", "desc_capitulo"}),
    "programa": frozenset({"ciclo", "id_pp", "desc_pp", "id_funcion"}),
    "fuente": frozenset({"ciclo", "id_ff", "desc_ff"}),
    "banda": frozenset({"ciclo", "banda_ejecucion", "tipo_gasto"}),
    "tipo_gasto": frozenset({"ciclo", "tipo_gasto"}),
    "global": frozenset({"ciclo"}),
}

DIMENSION_QUERIES: dict[str, str] = {
    "ramo": "SELECT id_ramo, desc_ramo FROM dim_ramo ORDER BY id_ramo",
    "ur": "SELECT id_ur, desc_ur, id_ramo FROM dim_ur ORDER BY id_ur",
    "entidad": """
        SELECT id_entidad_federativa, entidad_federativa
        FROM dim_entidad ORDER BY entidad_federativa
    """,
    "fuente": "SELECT id_ff, desc_ff FROM dim_fuente_financiamiento ORDER BY id_ff",
    "capitulo": """
        SELECT DISTINCT id_capitulo, desc_capitulo
        FROM dim_clasificacion_economica ORDER BY id_capitulo
    """,
    "programa": """
        SELECT DISTINCT id_pp, desc_pp FROM dim_clasificacion_funcional
        WHERE id_pp IS NOT NULL ORDER BY id_pp
    """,
    "banda_ejecucion": """
        SELECT DISTINCT banda_ejecucion FROM fact_ejecucion
        WHERE banda_ejecucion IS NOT NULL ORDER BY 1
    """,
    "tipo_gasto": """
        SELECT DISTINCT tipo_gasto FROM fact_ejecucion ORDER BY tipo_gasto
    """,
}


def list_axes() -> list[str]:
    return list(OLAP_VIEWS.keys())


def query_aggregate(
    wh: WarehouseConnection,
    axis: str,
    filters: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    if axis not in OLAP_VIEWS:
        raise ValueError(f"Eje OLAP no válido: {axis}")
    view = OLAP_VIEWS[axis]
    allowed = AGGREGATE_FILTER_COLUMNS.get(axis, frozenset())
    clauses: list[str] = []
    params: list[Any] = []
    applied: dict[str, Any] = {}
    for key, value in filters.items():
        if value is None or key not in allowed:
            continue
        clauses.append(f"{key} = ?")
        params.append(value)
        applied[key] = value

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM {view}{where_sql} ORDER BY n_registros DESC NULLS LAST LIMIT ?"
    params.append(limit)
    data = wh.fetch_all(sql, params)
    return {
        "axis": axis,
        "view": view,
        "row_count": len(data),
        "filters_applied": applied,
        "data": data,
    }


def query_star(
    wh: WarehouseConnection,
    filters: dict[str, Any],
    limit: int,
    offset: int,
) -> dict[str, Any]:
    clauses: list[str] = []
    params: list[Any] = []
    applied: dict[str, Any] = {}
    for key, value in filters.items():
        if value is None or key not in STAR_FILTER_COLUMNS:
            continue
        clauses.append(f"{key} = ?")
        params.append(value)
        applied[key] = value

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    count_sql = f"SELECT COUNT(*) FROM vw_olap_star{where_sql}"
    total = int(wh.fetch_one_scalar(count_sql, list(params)) or 0)

    sql = (
        f"SELECT * FROM vw_olap_star{where_sql} "
        f"ORDER BY monto_modificado DESC LIMIT ? OFFSET ?"
    )
    page_params = list(params) + [limit, offset]
    data = wh.fetch_all(sql, page_params)
    return {
        "row_count": total,
        "limit": limit,
        "offset": offset,
        "filters_applied": applied,
        "data": data,
    }


def query_dimension(wh: WarehouseConnection, dimension: str) -> list[dict[str, Any]]:
    if dimension not in DIMENSION_QUERIES:
        raise ValueError(f"Dimensión no válida: {dimension}")
    return wh.fetch_all(DIMENSION_QUERIES[dimension])
