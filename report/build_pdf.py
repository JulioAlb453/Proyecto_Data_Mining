"""
Genera el informe PDF técnico desde profile_summary.json y training_metrics.json.

Uso:
    python report/build_pdf.py
"""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = PROJECT_ROOT / "data" / "processed" / "profile_summary.json"
METRICS_PATH = PROJECT_ROOT / "ml" / "artifacts" / "training_metrics.json"
FIGURES_DIR = Path(__file__).resolve().parent / "figures"
OUTPUT_PDF = Path(__file__).resolve().parent / (
    "proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto.pdf"
)


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _wrap(text: str, width: int = 92) -> str:
    return "\n".join(textwrap.fill(line, width=width) for line in text.splitlines())


def _add_text_page(pdf: PdfPages, title: str, body: str) -> None:
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    y = 0.94
    fig.text(0.08, y, title, fontsize=14, fontweight="bold", va="top")
    y -= 0.04
    for paragraph in body.strip().split("\n\n"):
        block = _wrap(paragraph)
        for line in block.splitlines():
            if y < 0.06:
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
                fig = plt.figure(figsize=(8.27, 11.69))
                fig.patch.set_facecolor("white")
                y = 0.94
            fig.text(0.08, y, line, fontsize=9, va="top", family="sans-serif")
            y -= 0.028
        y -= 0.02
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _fnum(value: object, fmt: str = ".4f") -> str:
    if isinstance(value, (int, float)):
        return format(value, fmt)
    return "N/D"


def _fmt_metrics_table(metrics: dict) -> str:
    reg = metrics.get("regression", {})
    clf = metrics.get("classification", {})
    lines = [
        "REGRESIÓN — target: ratio_ejecucion",
        f"  Mejor modelo: {reg.get('best_model', 'N/D')}",
        f"  Muestras: {reg.get('n_samples', 'N/D')}",
    ]
    bt = reg.get("best_test_metrics") or {}
    bc = reg.get("best_cv_metrics") or {}
    lines += [
        f"  Test — MAE: {_fnum(bt.get('mae'))}",
        f"  Test — RMSE: {_fnum(bt.get('rmse'))}",
        f"  Test — R²: {_fnum(bt.get('r2'))}",
        f"  CV 5-fold — R² media: {_fnum(bc.get('r2_mean'))}",
        "",
        "CLASIFICACIÓN — target: alta_ejecucion (ratio ≥ 0.80)",
        f"  Mejor modelo: {clf.get('best_model', 'N/D')}",
        f"  Tasa positivos: {_fnum(clf.get('positive_rate'), '.2%')}"
        if clf.get("positive_rate") is not None
        else "  Tasa positivos: N/D",
    ]
    bt2 = clf.get("best_test_metrics") or {}
    lines += [
        f"  Test — F1: {_fnum(bt2.get('f1'))}",
        f"  Test — Recall: {_fnum(bt2.get('recall'))}",
        f"  Test — PR-AUC: {_fnum(bt2.get('pr_auc'))}",
        f"  Test — ROC-AUC: {_fnum(bt2.get('roc_auc'))}",
    ]
    comp_reg = reg.get("comparison") or []
    if comp_reg:
        lines.append("\nComparativa regresión (test R²):")
        for row in comp_reg:
            r2 = (row.get("test_metrics") or {}).get("r2")
            lines.append(f"  - {row.get('model')}: R²={r2:.4f}" if isinstance(r2, (int, float)) else f"  - {row.get('model')}")
    comp_clf = clf.get("comparison") or []
    if comp_clf:
        lines.append("\nComparativa clasificación (test F1):")
        for row in comp_clf:
            f1 = (row.get("test_metrics") or {}).get("f1")
            lines.append(f"  - {row.get('model')}: F1={f1:.4f}" if isinstance(f1, (int, float)) else f"  - {row.get('model')}")
    return "\n".join(lines)


def _add_figure_pages(pdf: PdfPages) -> None:
    if not FIGURES_DIR.is_dir():
        return
    for img_path in sorted(FIGURES_DIR.glob("*.png")):
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.imshow(plt.imread(img_path))
        ax.axis("off")
        ax.set_title(img_path.stem.replace("_", " "), fontsize=11)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def build_report() -> Path:
    profile = _load_json(PROFILE_PATH) or {}
    metrics = _load_json(METRICS_PATH)

    ratio = profile.get("ratio_ejecucion_crudo") or {}
    flags = profile.get("flags") or {}
    filtros = profile.get("filtros_analiticos_n_filas") or {}

    intro = f"""
Proyecto Corte 1 Full Stack — PEF ejecución presupuestal
Alumno: 233298 · Cruz Jiménez · Julio Alberto
Curso: Minería de Datos · UPCh 2026A
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}

1. Problema y contexto
Se analiza el avance de gasto federal (PEF, ciclo 2026) para explorar ejecución
presupuestal vía warehouse OLAP y modelos predictivos. El grano es una línea de gasto
con montos aprobado/modificado/pagado y clasificadores administrativos.

2. Decisiones de diseño
- Limpieza reproducible (data/pef_cleaning.py) con flags de calidad y filtros analíticos.
- Warehouse estrella en DuckDB con vistas OLAP consumidas por FastAPI.
- Regresión sobre ratio_ejecucion y clasificación alta_ejecucion (umbral 0.80).
- Política anti-leakage: sin monto_pagado ni etiquetas derivadas del pago en features.
- Producto: API + frontend React sin resultados precocinados estáticos.
"""

    calidad = f"""
3. Calidad de datos (profile_summary.json)
Filas limpias: {profile.get('n_filas', 'N/D')}
Ciclo: {profile.get('ciclo_valores', ['2026'])}
Mediana ratio (modificado>0): {ratio.get('mediana', 'N/D')}
Sin pago (flags): {flags.get('sin_pago', 'N/D')}
Alta ejecución: {flags.get('alta_ejecucion', 'N/D')}
Filtro modelado programable: {filtros.get('filtro_modelado_programable', 'N/D')} filas
Sesgo tipo_gasto: PROGRAMABLE domina (~99.9%).
"""

    if metrics:
        resultados = "4. Resultados de modelado\n\n" + _fmt_metrics_table(metrics)
        meth = metrics.get("methodology") or {}
        lims = meth.get("limitations") or []
        limitaciones = "5. Limitaciones\n\n" + "\n".join(f"- {x}" for x in lims)
    else:
        resultados = (
            "4. Resultados de modelado\n\n"
            "No se encontró ml/artifacts/training_metrics.json. "
            "Ejecute: python -m ml"
        )
        limitaciones = """
5. Limitaciones
- Snapshot ciclo 2026 sin serie temporal multianual.
- Clasificación alta_ejecucion desbalanceada (~8-9% positivos).
- Colinealidad entre montos presupuestales puede inflar R² en regresión.
- Dominio presupuestal: interpretación requiere contexto institucional.
"""

    producto = """
6. Capa de producto (API + frontend)
FastAPI expone KPIs/agregados OLAP y endpoints POST de inferencia.
React consume /olap/* y /predict/* en tiempo real.
Pruebas: pytest tests -q (desde raíz del proyecto).

7. Uso de IA
Detalle por componente en AI_USAGE.md (Cursor Composer en scaffolding,
ETL, ML, API, frontend y este informe).
"""

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUTPUT_PDF) as pdf:
        _add_text_page(pdf, "Informe técnico — PEF Full Stack", intro)
        _add_text_page(pdf, "Calidad y perfil de datos", calidad)
        _add_text_page(pdf, "Resultados cuantitativos", resultados)
        _add_text_page(pdf, "Limitaciones y cierre", limitaciones + "\n\n" + producto)
        _add_figure_pages(pdf)

    print(f"PDF generado: {OUTPUT_PDF}")
    return OUTPUT_PDF


if __name__ == "__main__":
    build_report()
