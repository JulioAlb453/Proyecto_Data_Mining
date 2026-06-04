"""CLI: perfilar, limpiar y exportar PEF a data/processed/."""

from __future__ import annotations

import argparse
import sys

from data.pef_cleaning import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Perfilado y limpieza PEF_avance_gasto.csv")
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Ruta al CSV (por defecto PEF_RAW_CSV o data/raw/PEF_avance_gasto.csv)",
    )
    args = parser.parse_args()
    csv_path = None if args.csv is None else __import__("pathlib").Path(args.csv)

    try:
        result = run_pipeline(csv_path)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    print("Limpieza PEF completada.")
    print(f"  Filas limpio: {result['n_limpio']:,}")
    print(f"  Filas analítico (filtro_modelado_programable): {result['n_analitico']:,}")
    for key, path in result["paths"].items():
        print(f"  {key}: {path}")
    flags = result["profile"]["flags"]
    print(
        "  Flags — válidos:",
        f"{flags['flag_registro_valido']:,}",
        "| sin_pago:",
        f"{flags['sin_pago']:,}",
        "| alta_ejecucion:",
        f"{flags['alta_ejecucion']:,}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
