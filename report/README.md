# Reporte técnico (PDF)

Informe final: problema, decisiones de diseño, resultados cuantitativos, limitaciones del snapshot 2026 y uso de IA por componente.

## Generar el PDF

Desde la raíz del proyecto (con venv activado):

```powershell
python -m ml
python report/build_pdf.py
```

**Salida:** `report/proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto.pdf`

**Entradas:**

- `data/processed/profile_summary.json` (perfil de datos)
- `ml/artifacts/training_metrics.json` (métricas de modelado; opcional pero recomendado)

## Figuras

Exportar gráficos desde notebooks a `report/figures/*.png`; el script las incorpora automáticamente al PDF.
