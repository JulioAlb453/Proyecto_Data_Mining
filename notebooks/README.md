# Notebooks

EDA reproducible sobre PEF: calidad de datos, desbalance por `tipo_gasto`, variables derivadas (`ratio_ejecucion`, indicadores de rezago) y validación previa al modelado.

| Notebook | Contenido |
|----------|-----------|
| `01_data_understanding.ipynb` | Perfil, limpieza, filtros analíticos (requiere CSV vía `.env`) |

Ejecutar primero `python -m data.run_cleaning` desde la raíz del proyecto. El notebook `02_*` usará `warehouse.duckdb` cuando exista el ETL.
