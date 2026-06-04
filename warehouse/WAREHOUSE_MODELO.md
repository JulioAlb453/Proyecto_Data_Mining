# Modelo dimensional — warehouse PEF (DuckDB)

## Grano del hecho

Una fila de `fact_ejecucion` corresponde a un registro de avance de gasto en el snapshot del ciclo (2026), tras `filtro_olap` (sin montos negativos en columnas presupuestales).

## Tablas

| Tabla | Rol | Llave natural |
|-------|-----|----------------|
| `dim_tiempo` | Periodo fiscal | `ciclo` |
| `dim_ramo` | Ramo administrativo | `id_ramo`, `desc_ramo` |
| `dim_ur` | Unidad responsable | `id_ur`, `desc_ur`, `id_ramo`, `desc_ramo` |
| `dim_entidad` | Entidad federativa | `id_entidad_federativa`, `entidad_federativa` |
| `dim_clasificacion_economica` | Capítulo, concepto, partidas, tipo de gasto | IDs y descripciones económicas |
| `dim_clasificacion_funcional` | Grupo funcional → programa | `gpo_funcional` … `id_pp` |
| `dim_fuente_financiamiento` | Fuente de financiamiento | `id_ff`, `desc_ff` |
| `fact_ejecucion` | Hecho de ejecución presupuestal | SKs a dimensiones + medidas |

## Medidas y atributos en el hecho

- **Montos:** `monto_aprobado`, `monto_modificado`, `monto_*_mensual`, `monto_pagado`
- **Derivadas (desde `data/pef_cleaning.py`):** `ratio_ejecucion`, `sin_pago`, `alta_ejecucion`, `banda_ejecucion`, etc.
- **Degenerada:** `id_clave_cartera`

## Vistas OLAP (`warehouse/sql/02_olap_views.sql`)

| Vista | Uso |
|-------|-----|
| `vw_olap_star` | Cubo desnormalizado para filtros dinámicos (API) |
| `vw_olap_kpis_global` | KPIs del ciclo |
| `vw_olap_ejecucion_por_ramo` | Agregado por ramo |
| `vw_olap_ejecucion_por_ur` | Agregado por unidad responsable |
| `vw_olap_ejecucion_por_entidad` | Agregado por entidad federativa |
| `vw_olap_ejecucion_por_capitulo` | Clasificación económica (capítulo) |
| `vw_olap_ejecucion_por_programa` | Programa presupuestario (`id_pp`) |
| `vw_olap_ejecucion_por_fuente` | Fuente de financiamiento |
| `vw_olap_ejecucion_por_banda` | Distribución por banda de ejecución |
| `vw_olap_ejecucion_por_tipo_gasto` | PROGRAMABLE vs NO PROGRAMABLE |

El ratio agregado en vistas usa **suma pagado / suma modificado** (solo filas con modificado > 0 en el numerador del denominador), no el promedio simple de ratios.

## Construcción

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto
python -m warehouse.build
```

Salida: `WAREHOUSE_DB` (por defecto `warehouse/warehouse.duckdb`).
