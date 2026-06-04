# Proyecto Corte 1 Full Stack — PEF ejecución presupuestal



**Alumno:** 233298 · Cruz Jiménez · Julio Alberto  

**Curso:** Minería de Datos · UPCh 2026A  



Producto end-to-end sobre el avance de gasto federal (**PEF**): warehouse analítico (DuckDB), EDA/preproceso, modelado (regresión + clasificación), API (FastAPI) y frontend (React).



**Fuente principal:** `PEF_avance_gasto.csv` (ruta en `.env` → `PEF_RAW_CSV`; ver `.env.example`).



**Informe PDF:** `report/proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto.pdf` (generar con `python report/build_pdf.py`).



---



## Requisitos



| Herramienta | Versión mínima |

|-------------|----------------|

| Python | 3.10+ (probado con 3.12/3.14 en venv local) |

| Node.js | 18+ |

| CSV PEF | Copia o ruta absoluta al archivo de avance de gasto 2026 |



---



## Configuración inicial (una vez)



```powershell

cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

copy .env.example .env

# Editar .env: PEF_RAW_CSV=C:\ruta\a\PEF_avance_gasto.csv

```



Opcional: copiar el CSV a `data/raw/PEF_avance_gasto.csv` y apuntar `PEF_RAW_CSV` ahí.



---



## Pipeline reproducible (orden obligatorio)



Ejecutar desde la **raíz del proyecto** con el venv activado.



### 1. Limpieza y perfil (`data/`)



```powershell

python -m data.run_cleaning

```



**Salidas:** `data/processed/pef_limpio.parquet`, `pef_analitico.parquet`, `profile_summary.json`  

**Docs:** `data/PEF_PERFIL_Y_LIMPIEZA.md` · **Notebook:** `notebooks/01_data_understanding.ipynb`



### 2. Warehouse DuckDB (`warehouse/`)



```powershell

python -m warehouse.build

```



**Salida:** `warehouse/warehouse.duckdb` (variable `WAREHOUSE_DB` en `.env`)  

**Docs:** `warehouse/WAREHOUSE_MODELO.md` · **Vistas:** `warehouse/sql/02_olap_views.sql`



### 3. Modelado ML (`ml/`)



```powershell

python -m ml

```



**Salidas:** `ml/artifacts/regression_model.joblib`, `classification_model.joblib`, `preprocessor.joblib`, `training_metrics.json`  

**Docs:** `ml/README.md`  

**Duración:** varios minutos (~150k filas; Random Forest es el más lento).

Entrenamiento ligero recomendado para iterar:

```powershell
$env:ML_FAST="1"
$env:ML_SAMPLE_SIZE="10000"
python -m ml
```

Ese modo usa parquet procesado, 3-fold CV, omite Random Forest y entrena sobre una muestra estratificada del dataset.



| Tarea | Target | Filtro | Modelos comparados |

|-------|--------|--------|-------------------|

| Regresión | `ratio_ejecucion` | `filtro_modelado_programable` | ElasticNet, HistGradientBoosting, RandomForest |

| Clasificación | `alta_ejecucion` (ratio ≥ 0.80) | mismo | Logistic (balanced), HistGradientBoosting, RandomForest |



### 4. Informe PDF (`report/`)



```powershell

python report/build_pdf.py

```



Requiere `profile_summary.json`; incluye métricas si existe `ml/artifacts/training_metrics.json`. Figuras opcionales en `report/figures/*.png`.



### 5. API FastAPI (`api/`)



Requiere `warehouse/warehouse.duckdb`. Para **predicción**, ejecutar antes el paso 3.



```powershell

uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

```



| Método | Ruta | Descripción |

|--------|------|-------------|

| GET | `/health` | Estado warehouse y modelos |

| GET | `/olap/meta` | Ejes y vistas disponibles |

| GET | `/olap/kpis` | KPIs globales |

| GET | `/olap/aggregate/{axis}` | Agregados (`ramo`, `ur`, `entidad`, `capitulo`, `programa`, `fuente`, `banda`, `tipo_gasto`) |

| GET | `/olap/star` | Detalle filtrable |

| GET | `/olap/dimensions/{dim}` | Valores para filtros UI |

| GET | `/predict/schema` | Features del formulario |

| POST | `/predict/regression` | Predicción `ratio_ejecucion` |

| POST | `/predict/classification` | Predicción `alta_ejecucion` |



Documentación: `api/README.md` · Swagger: http://127.0.0.1:8000/docs



### 6. Frontend React (`frontend/`)



En **otra terminal**, con la API en ejecución:



```powershell

cd frontend

copy .env.example .env

npm install

npm run dev

```



Abrir http://localhost:5173



| Vista | Función |

|-------|---------|

| Exploración OLAP | KPIs, agregados por eje, gráfico y tabla vía `/olap/*` |

| Predicción ML | Formulario desde `/predict/schema`; regresión + clasificación en vivo |



Build producción: `npm run build` → `frontend/dist` · Detalle: `frontend/README.md` · Prueba externa predicción: `frontend/PRUEBA_PREDICCION_EXTERNA.md`



---



## Pruebas automatizadas



Desde la raíz (usa `pytest.ini` + `tests/conftest.py`):



```powershell

pytest tests -q

```



| Archivo | Qué valida |

|---------|------------|

| `tests/test_warehouse.py` | Esquema y vistas OLAP |

| `tests/test_ml.py` | Carga de frame y política de features |

| `tests/test_api.py` | Contratos `/health`, OLAP e inferencia |



---



## Estado de fases



| Fase | Carpeta | Estado |

|------|---------|--------|

| 1 Datos | `data/` | Implementado |

| 2 Warehouse | `warehouse/` | Implementado |

| 3 EDA | `notebooks/` | `01_data_understanding.ipynb` |

| 4 ML | `ml/` | Implementado (requiere `python -m ml` local) |

| 5 API | `api/` | Implementado |

| 6 Frontend | `frontend/` | Implementado |

| 7 Reporte | `report/` | PDF vía `report/build_pdf.py` |



---



## Estructura del repositorio



```

proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto/

├── data/                 # Limpieza CSV → parquet + perfil

├── warehouse/            # ETL DuckDB + vistas OLAP

├── notebooks/            # EDA reproducible

├── ml/artifacts/         # Modelos (generados; no versionar en git si son pesados)

├── api/                  # FastAPI

├── frontend/             # React + Vite

├── report/               # build_pdf.py + PDF + figures/

├── tests/

├── .env.example

├── requirements.txt

├── AI_USAGE.md

└── README.md

```



---



## Objetivos de modelado



- **Regresión:** predecir `ratio_ejecucion` con montos **aprobado/modificado** y dimensiones estructurales (sin `monto_pagado`).

- **Clasificación:** `alta_ejecucion` (umbral 0.80 sobre ratio observado en entrenamiento; excluido como feature).



Política anti-leakage: ver `ml/config.py` → `LEAKAGE_COLUMNS`.



---



## Limitaciones conocidas



- **Snapshot 2026:** un solo ciclo; no hay serie temporal multianual.

- **Desbalance:** `alta_ejecucion` ~8–9 % de positivos; métricas PR-AUC / recall relevantes.

- **Colinealidad** entre montos presupuestales puede inflar R² en regresión.

- **Dominio presupuestal:** glosario y contexto en `data/PEF_PERFIL_Y_LIMPIEZA.md` e informe PDF.



---



## Declaración de IA



Ver `AI_USAGE.md` (uso de Cursor Composer por componente y validación manual).



---



## Referencia rápida (todo el stack)



```powershell

.\venv\Scripts\Activate.ps1

python -m data.run_cleaning

python -m warehouse.build

python -m ml

python report/build_pdf.py

pytest tests -q

# Terminal 1:

uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2:

cd frontend; npm run dev

```

