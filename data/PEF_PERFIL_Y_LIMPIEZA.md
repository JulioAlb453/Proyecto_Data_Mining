# Perfil y limpieza — PEF_avance_gasto.csv

Documento de referencia para la fase **data-understanding** (snapshot ciclo 2026).

## Fuente

| Atributo | Valor |
|----------|--------|
| Archivo | `PEF_avance_gasto.csv` |
| Filas | 167 593 |
| Columnas | 38 |
| Ciclo | 2026 (único valor) |
| Duplicados exactos (crudo) | 0 |
| Duplicados tras normalizar textos | 41 (eliminados en limpieza) |

Ruta por defecto: `PEF_RAW_CSV` en `.env` o copia en `data/raw/`.

## Calidad observada

### Montos presupuestales

| Columna | Negativos | Notas |
|---------|-----------|--------|
| `monto_aprobado` | 1 | Valor extremo (~−12.6e9) aislado |
| `monto_modificado` | 32 | Inconsistente con ejecución interpretable |
| `monto_pagado` | 293 | Incluye devoluciones/ajustes contables |
| `monto_*_mensual` | 1–61 | Misma lógica; no se usan como target principal |

Cuando `monto_modificado > 0` (150 228 filas):

- Mediana `ratio_ejecucion` ≈ **0.099**
- p95 ≈ **1.0**, p99 ≈ **1.51**
- `sin_pago` (pagado = 0): **58 535** (~39 %)
- Sobre-ejecución (`ratio > 1`): **4 208**
- `monto_modificado == 0`: **17 365** (sin ratio definido)

### Sesgo por `tipo_gasto`

| tipo_gasto | Filas | % |
|------------|------:|---:|
| PROGRAMABLE | 167 390 | 99.88 % |
| NO PROGRAMABLE | 203 | 0.12 % |

`desc_tipogasto` dominante: **Gasto corriente** (~86 %). Para modelado comparativo se recomienda el filtro `filtro_modelado_programable`.

### Cardinalidad OLAP (segmentación)

| Dimensión | Valores únicos |
|-----------|----------------|
| `id_ramo` / `desc_ramo` | 46 |
| `id_ur` | 534 |
| `entidad_federativa` | 34 |
| Clasificadores económicos/funcionales | Ver columnas `id_*` / `desc_*` en CSV |

## Variables derivadas (implementadas en `data/pef_cleaning.py`)

| Variable | Definición |
|----------|------------|
| `ratio_ejecucion` | `monto_pagado / monto_modificado` si modificado > 0 |
| `ratio_aprobado` | `monto_pagado / monto_aprobado` si aprobado > 0 |
| `log1p_monto_pagado` | `log1p(max(monto_pagado, 0))` |
| `sin_pago` | modificado > 0 y pagado = 0 |
| `alta_ejecucion` | ratio ≥ **0.80** (umbral `RATIO_ALTA_EJECUCION`) |
| `sobre_ejecucion` | ratio > 1 |
| `banda_ejecucion` | `sin_base` \| `sin_pago` \| `baja` (<0.5) \| `media` \| `alta` \| `sobre` |

Flags de calidad: `flag_montos_negativos`, `flag_modificado_cero`, `flag_modificado_negativo`, `flag_registro_valido`.

## Filtros analíticos

| Nombre | Uso | Criterio resumido |
|--------|-----|-------------------|
| `filtro_olap` | Agregados warehouse / API | Sin montos negativos |
| `filtro_modelado_ratio` | Regresión sobre `ratio_ejecucion` | Válido + modificado > 0 |
| `filtro_modelado_programable` | **Salida por defecto** `pef_analitico.parquet` | Anterior + `tipo_gasto == PROGRAMABLE` |
| `filtro_clasificacion_sin_pago` | Clasificación `sin_pago` | Válido + modificado > 0 |

## Limpieza aplicada

1. Lectura UTF-8 con fallback Latin-1 si hay caracteres dañados.
2. Coerción de tipos (`ciclo`, montos numéricos, textos `string` sin espacios extra).
3. Eliminación de duplicados exactos (0 en la fuente actual).
4. Cálculo de derivadas y flags (no se imputan montos; se excluyen vía flags/filtros).
5. Exportación a `data/processed/pef_limpio.parquet` (167 552 filas), `pef_analitico.parquet` (149 838 filas) y `profile_summary.json`.

Tras limpieza (ejecución de referencia): registros válidos 167 213; `sin_pago` 58 495; `alta_ejecucion` 13 010.

## Ejecución reproducible

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto
pip install -r requirements.txt
python -m data.run_cleaning
```

Notebook complementario: `notebooks/01_data_understanding.ipynb`.

## Riesgos para modelado (mitigación)

- **Fuga de datos:** no usar `monto_pagado` ni `monto_modificado` como features cuando el target es `ratio_ejecucion` o `sin_pago` derivado de pagado.
- **Colas extremas:** preferir `log1p_monto_pagado` o modelos robustos; revisar outliers en p99+.
- **Snapshot único:** sin serie temporal multianual; limitar conclusiones causales.
