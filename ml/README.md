# Machine learning

Pipelines reproducibles de entrenamiento, evaluación comparativa y serialización.

## Tareas definidas

| Tarea | Target | Filtro | Modelos comparados (5-fold CV + hold-out 20%) |
|-------|--------|--------|--------------------------------------------------|
| **Regresión** | `ratio_ejecucion` | `filtro_modelado_programable` | ElasticNet, HistGradientBoosting, RandomForest |
| **Clasificación** | `alta_ejecucion` (ratio ≥ 0.80) | mismo filtro | Logistic (balanced), HistGradientBoosting, RandomForest (balanced) |

Métricas: regresión → MAE, RMSE, R²; clasificación → F1, recall, precision, ROC-AUC, PR-AUC.

Política anti-leakage en `ml/config.py`: se excluyen `monto_pagado`, ratios/etiquetas derivadas del pago y SKs del hecho.

## Ejecución

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto
.\venv\Scripts\Activate.ps1
python -m ml
# o: python -m ml.train (vía run_training en ml/__main__.py)
```

**Entrada:** `warehouse/warehouse.duckdb` (preferido) o `data/processed/pef_analitico.parquet`.

**Salidas** (`ml/artifacts/`):

- `regression_model.joblib` — pipeline ganador (preprocesador + estimador)
- `classification_model.joblib` — pipeline ganador
- `preprocessor.joblib` — solo preprocesador del clasificador
- `training_metrics.json` — comparativa CV y test de todos los modelos

## Módulos

- `config.py` — targets, columnas prohibidas, hiperparámetros globales
- `data.py` — carga desnormalizada desde DuckDB
- `features.py` — `ColumnTransformer` (imputación + escala + one-hot acotado)
- `evaluate.py` — métricas y ranking
- `train.py` — orquestación

Pruebas: `pytest tests/test_ml.py -q`
