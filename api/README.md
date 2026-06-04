# API (FastAPI)

Servicio que consulta `warehouse.duckdb` y expone inferencia de modelos en `ml/artifacts/`.

**Endpoints previstos:**

- OLAP: filtros y agregados (ramo, UR, entidad, capítulo, programa, fuente, periodo).
- Inferencia: regresión (`ratio_ejecucion` o target definido) y clasificación (`alta_ejecucion` / `sin_pago`).

Arranque previsto:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Variables en `.env`: `API_HOST`, `API_PORT`, `CORS_ORIGINS`, rutas a modelos.
