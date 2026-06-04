# Declaración de uso de IA

**Proyecto:** Corte 1 Full Stack — PEF ejecución presupuestal (PEF)  
**Alumno:** 233298 · Cruz Jiménez · Julio Alberto  
**Curso:** Minería de Datos · UPCh 2026A

---

## Herramientas usadas

| Herramienta | Modelo / versión | Uso en este proyecto |
|-------------|------------------|----------------------|
| **Cursor** | **Composer** | Estructura base del repositorio (`README.md`, `requirements.txt`, `.env.example`, `.gitignore`, carpetas `data/`, `warehouse/`, `notebooks/`, `ml/`, `api/`, `frontend/`, `report/`) según plan de acción del proyecto corte 1. |
| **Cursor** | **Composer** | Fase data-understanding: módulo `data/pef_cleaning.py`, CLI `data/run_cleaning.py`, documento `data/PEF_PERFIL_Y_LIMPIEZA.md`, notebook `notebooks/01_data_understanding.ipynb`. Validación manual pendiente de cifras en informe final. |
| **Cursor** | **Composer** | Fase warehouse: `warehouse/etl.py`, `warehouse/build.py`, vistas `warehouse/sql/02_olap_views.sql`, `warehouse/WAREHOUSE_MODELO.md`, prueba `tests/test_warehouse.py`. Build validado sobre CSV PEF (~167k filas OLAP). |

---

## Componentes pendientes de declarar

Warehouse, modelado, API, frontend e informe PDF (actualizar esta tabla al implementarlos).
