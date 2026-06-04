"""Rutas del proyecto resueltas desde variables de entorno."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args: object, **_kwargs: object) -> bool:
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_path(value: str, base: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_project_env() -> None:
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv(PROJECT_ROOT / ".env.example")


def get_paths() -> dict[str, Path]:
    load_project_env()
    raw_default = PROJECT_ROOT / "data" / "raw" / "PEF_avance_gasto.csv"
    raw_csv = Path(os.getenv("PEF_RAW_CSV", str(raw_default)))
    processed_dir = _resolve_path(
        os.getenv("DATA_PROCESSED_DIR", "data/processed"),
        PROJECT_ROOT,
    )
    return {
        "project_root": PROJECT_ROOT,
        "raw_csv": raw_csv,
        "processed_dir": processed_dir,
    }
