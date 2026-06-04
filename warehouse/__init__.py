"""Warehouse analítico PEF (DuckDB): modelo dimensional y vistas OLAP."""

__all__ = ["build_warehouse"]


def build_warehouse():
    from warehouse.build import build_warehouse as _build

    return _build()
