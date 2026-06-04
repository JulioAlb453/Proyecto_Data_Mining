# Warehouse (DuckDB)

Scripts SQL y proceso de construcción de `warehouse.duckdb`.

**Esquema previsto:**

- Hecho: ejecución presupuestal (montos, ratio derivado en vistas).
- Dimensiones: `dim_ramo`, `dim_ur`, `dim_entidad`, `dim_clasificacion_economica`, `dim_clasificacion_funcional`, `dim_fuente_financiamiento`, `dim_tiempo`.
- Vistas analíticas para consumo por la API (agregados por ramo, UR, entidad, capítulo, programa, fuente).

Salida: `warehouse/warehouse.duckdb` (ignorado en git; regenerable).
