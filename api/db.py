"""Acceso de solo lectura a DuckDB warehouse."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import duckdb

from api.config import get_settings


class WarehouseNotFoundError(FileNotFoundError):
    """El archivo warehouse.duckdb no existe."""


class WarehouseConnection:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def ensure_exists(self) -> None:
        if not self.db_path.exists():
            raise WarehouseNotFoundError(
                f"No existe {self.db_path}. Ejecute: python -m warehouse.build"
            )

    @contextmanager
    def connect(self) -> Iterator[duckdb.DuckDBPyConnection]:
        self.ensure_exists()
        con = duckdb.connect(str(self.db_path), read_only=True)
        try:
            yield con
        finally:
            con.close()

    def fetch_df(self, sql: str, params: list[Any] | None = None):
        import pandas as pd

        with self.connect() as con:
            if params:
                return con.execute(sql, params).fetchdf()
            return con.execute(sql).fetchdf()

    def fetch_all(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        df = self.fetch_df(sql, params)
        if df.empty:
            return []
        records = df.to_dict(orient="records")
        for row in records:
            for key, val in row.items():
                if hasattr(val, "item"):
                    row[key] = val.item()
                elif val is None or (isinstance(val, float) and val != val):
                    row[key] = None
        return records

    def fetch_one_scalar(self, sql: str, params: list[Any] | None = None) -> Any:
        with self.connect() as con:
            if params:
                row = con.execute(sql, params).fetchone()
            else:
                row = con.execute(sql).fetchone()
        return row[0] if row else None


def get_warehouse() -> WarehouseConnection:
    settings = get_settings()
    return WarehouseConnection(settings.warehouse_path)
