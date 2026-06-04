# Proyecto Corte 1 Full Stack — PEF ejecución presupuestal

**Alumno:** 233298 · Cruz Jiménez · Julio Alberto  
**Curso:** Minería de Datos · UPCh 2026A  

Producto end-to-end sobre el avance de gasto federal (**PEF**): warehouse analítico (DuckDB), EDA/preproceso, modelado (regresión + clasificación), API (FastAPI) y frontend (React).

**Fuente principal:** `PEF_avance_gasto.csv` (por defecto en `Downloads`; ver `.env.example`).

## Requisitos

- Python 3.10+
- Node.js 18+ (fase frontend; se documentará al crear `frontend/`)
- Copiar o enlazar el CSV en `data/raw/` (ver `data/raw/README.md`)

## Configuración inicial

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Editar .env con la ruta real a PEF_avance_gasto.csv
```

## Flujo de trabajo (por implementar)

| Fase | Carpeta | Descripción |
|------|---------|-------------|
| 1 | `data/raw`, `data/processed` | Ingesta y limpieza del CSV PEF |
| 2 | `warehouse/` | ETL SQL → `warehouse.duckdb` (hechos + dimensiones OLAP) |
| 3 | `notebooks/` | EDA reproducible, variables derivadas (`ratio_ejecucion`, bandas de ejecución) |
| 4 | `ml/` | Entrenamiento, evaluación y serialización de modelos |
| 5 | `api/` | Endpoints OLAP e inferencia (FastAPI + DuckDB) |
| 6 | `frontend/` | Panel exploratorio y formulario de predicción en vivo |
| 7 | `report/` | Informe PDF técnico y figuras |

### Comandos previstos (referencia)

```powershell
# Warehouse (cuando existan scripts)
# python -m warehouse.build   o scripts en warehouse/sql/

# API
# uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (cuando exista package.json)
# cd frontend && npm install && npm run dev
```

## Estructura del repositorio

```
proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto/
├── data/
│   ├── raw/              # CSV fuente (PEF)
│   └── processed/        # Salidas ETL listas para warehouse/ML
├── warehouse/            # SQL, build DuckDB, vistas OLAP
├── notebooks/            # EDA y validación analítica
├── ml/
│   └── artifacts/        # Modelos y preprocessors serializados (.gitignore)
├── api/                  # FastAPI
├── frontend/             # React + Vite
├── report/               # PDF e imágenes del informe
├── .env.example
├── requirements.txt
├── AI_USAGE.md
└── README.md
```

## Objetivos de modelado (plan)

- **Regresión:** `ratio_ejecucion` o `log1p(monto_pagado)` con variables estructurales/presupuestales sin fuga.
- **Clasificación:** `alta_ejecucion` (umbral sobre ratio) o `sin_pago` (pagado = 0 con modificado > 0).

## Limitaciones conocidas

- Snapshot 2026: sin serie temporal multianual en la fuente actual.
- Dominio presupuestal complejo: consultar glosario en el informe cuando esté disponible.

## Declaración de IA

Ver `AI_USAGE.md`.
