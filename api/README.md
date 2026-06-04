# API (FastAPI)

Servicio que consulta `warehouse.duckdb` y expone inferencia con modelos en `ml/artifacts/`.

## Arranque

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Requiere `WAREHOUSE_DB` en `.env`. Para `/predict/*`, ejecutar antes `python -m ml`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Warehouse y modelos cargados |
| GET | `/olap/meta` | Ejes y vistas |
| GET | `/olap/kpis` | KPIs globales |
| GET | `/olap/aggregate/{axis}` | Agregados por eje |
| GET | `/olap/star` | Detalle filtrable |
| GET | `/olap/dimensions/{dim}` | Valores para filtros |
| GET | `/predict/schema` | Schema del formulario ML |
| POST | `/predict/regression` | `ratio_ejecucion` |
| POST | `/predict/classification` | `alta_ejecucion` |

Documentación interactiva: http://127.0.0.1:8000/docs

## Variables `.env`

`API_HOST`, `API_PORT`, `CORS_ORIGINS`, `WAREHOUSE_DB`, `ML_REGRESSION_MODEL`, `ML_CLASSIFICATION_MODEL`, `ML_PREPROCESSOR`.

## Pruebas

```powershell
pytest tests/test_api.py -q
```
