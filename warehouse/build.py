"""CLI: construye warehouse.duckdb desde datos PEF limpios."""

from __future__ import annotations

import argparse
import json
import sys

from warehouse.etl import run_etl


def build_warehouse() -> dict:
    return run_etl()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ETL PEF → DuckDB (dimensiones, fact_ejecucion, vistas OLAP)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime el resumen del build en JSON.",
    )
    args = parser.parse_args()
    result = build_warehouse()
    if args.json:
        payload = {
            "warehouse_db": str(result["warehouse_db"]),
            "source_rows": result["source_rows"],
            "fact_rows": result["fact_rows"],
            "dimensions": result["dimensions"],
            "views": result["views"],
            "validation": result["validation"],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        v = result["validation"]
        print(f"Warehouse: {result['warehouse_db']}")
        print(f"Filas fuente (filtro_olap): {result['source_rows']:,}")
        print(f"Filas fact_ejecucion: {result['fact_rows']:,}")
        print("Dimensiones:", ", ".join(f"{k}={n}" for k, n in result["dimensions"].items()))
        print(f"Vistas OLAP: {len(result['views'])}")
        print(f"Validación OK: {v['ok']} (huérfanos={v['orphan_fact_rows']})")
    return 0 if result["validation"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
