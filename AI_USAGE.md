# Declaración de uso de IA



**Proyecto:** Corte 1 Full Stack — PEF ejecución presupuestal  

**Alumno:** 233298 · Cruz Jiménez · Julio Alberto  

**Curso:** Minería de Datos · UPCh 2026A



Este documento describe cómo se usó asistencia de IA (Cursor / Composer) y qué validó el autor manualmente.



---



## Herramientas



| Herramienta | Modelo | Uso principal |

|-------------|--------|----------------|

| **Cursor** | **Composer** | Scaffolding, ETL, warehouse, ML, API, frontend, pruebas, documentación e informe PDF. |

| **Cursor** | **Composer** | Revisión de política anti-leakage, contratos API y flujo reproducible en README. |



---



## Uso por componente



| Componente | Asistencia IA | Validación humana |

|------------|---------------|-------------------|

| **Estructura y README** | Carpetas, `requirements.txt`, `.env.example`, guía de ejecución | Rutas locales en `.env`, orden de comandos probado en Windows |

| **data/** (`pef_cleaning.py`, `run_cleaning.py`) | Perfil, derivadas (`ratio_ejecucion`, bandas), filtros | Cifras contrastadas con `profile_summary.json` y `PEF_PERFIL_Y_LIMPIEZA.md` |

| **warehouse/** (ETL DuckDB, vistas OLAP) | Modelo estrella, SQL de vistas, `build.py` | `python -m warehouse.build`, conteos en `tests/test_warehouse.py` |

| **notebooks/** | `01_data_understanding.ipynb` alineado al ETL | Ejecución con CSV real vía `PEF_RAW_CSV` |

| **ml/** | Pipelines sklearn, comparativa ≥2 modelos/tarea, `training_metrics.json` | Revisión de exclusiones en `ml/config.py`; entrenamiento `python -m ml` |

| **api/** | Routers OLAP/inferencia, schemas, CORS | `pytest tests/test_api.py`, smoke con `uvicorn` |

| **frontend/** | React + Vite, paneles Explore/Predict, cliente API | `npm run dev` contra API viva; sin gráficos estáticos precocinados |

| **report/** | `build_pdf.py`, texto del informe desde JSON de métricas | Lectura del PDF y coherencia con métricas de entrenamiento |

| **tests/** | `conftest.py`, `pytest.ini` | `pytest tests -q` desde raíz del proyecto |



---



## Qué no delegó la IA sin supervisión



- Definición del **target** (`ratio_ejecucion`, `alta_ejecucion` con umbral 0.80) y filtro `filtro_modelado_programable`.

- Interpretación de **limitaciones** del snapshot 2026.

- Decisión de **no usar** `monto_pagado` ni etiquetas derivadas del pago en features.



---



## Fragmentos generados con mayor intervención humana


- Ajustes de umbrales y bandas en `data/pef_cleaning.py` tras revisar distribución del ratio.

- Selección del modelo ganador según métricas en `ml/artifacts/training_metrics.json` (no hardcodeado en API).

- Estilos y textos de UI en `frontend/src/` (marca, copy, layout).

---



## Reproducibilidad



Cualquier revisor puede repetir:



```powershell

python -m data.run_cleaning

python -m warehouse.build

python -m ml

pytest tests -q

uvicorn api.main:app --host 127.0.0.1 --port 8000

python report/build_pdf.py
