-- Vistas OLAP para consumo por API y notebooks.
-- Requieren tablas dim_* y fact_ejecucion cargadas por warehouse.etl.

CREATE OR REPLACE VIEW vw_olap_star AS
SELECT
    f.fact_sk,
    f.id_clave_cartera,
    dt.ciclo,
    dr.id_ramo,
    dr.desc_ramo,
    du.id_ur,
    du.desc_ur,
    de.id_entidad_federativa,
    de.entidad_federativa,
    dff.id_ff,
    dff.desc_ff,
    deco.id_capitulo,
    deco.desc_capitulo,
    deco.id_concepto,
    deco.desc_concepto,
    deco.id_partida_generica,
    deco.desc_partida_generica,
    deco.id_partida_especifica,
    deco.desc_partida_especifica,
    deco.id_tipogasto,
    deco.desc_tipogasto,
    dfunc.gpo_funcional,
    dfunc.desc_gpo_funcional,
    dfunc.id_funcion,
    dfunc.desc_funcion,
    dfunc.id_subfuncion,
    dfunc.desc_subfuncion,
    dfunc.id_ai,
    dfunc.desc_ai,
    dfunc.id_modalidad,
    dfunc.desc_modalidad,
    dfunc.id_pp,
    dfunc.desc_pp,
    f.tipo_gasto,
    f.monto_aprobado,
    f.monto_modificado,
    f.monto_aprobado_mensual,
    f.monto_modificado_mensual,
    f.monto_pagado,
    f.ratio_ejecucion,
    f.ratio_aprobado,
    f.sin_pago,
    f.alta_ejecucion,
    f.sobre_ejecucion,
    f.banda_ejecucion,
    f.flag_modificado_cero,
    f.flag_registro_valido
FROM fact_ejecucion f
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
JOIN dim_ramo dr ON f.ramo_sk = dr.ramo_sk
JOIN dim_ur du ON f.ur_sk = du.ur_sk
JOIN dim_entidad de ON f.entidad_sk = de.entidad_sk
JOIN dim_fuente_financiamiento dff ON f.ff_sk = dff.ff_sk
JOIN dim_clasificacion_economica deco ON f.eco_sk = deco.eco_sk
JOIN dim_clasificacion_funcional dfunc ON f.func_sk = dfunc.func_sk;

CREATE OR REPLACE VIEW vw_olap_kpis_global AS
SELECT
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_aprobado) AS monto_aprobado,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) AS base_modificado_positivo,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado,
    AVG(CASE WHEN f.monto_modificado > 0 THEN f.ratio_ejecucion END) AS ratio_ejecucion_promedio,
    SUM(CASE WHEN f.sin_pago THEN 1 ELSE 0 END) AS n_sin_pago,
    SUM(CASE WHEN f.alta_ejecucion THEN 1 ELSE 0 END) AS n_alta_ejecucion,
    SUM(CASE WHEN f.sobre_ejecucion THEN 1 ELSE 0 END) AS n_sobre_ejecucion
FROM fact_ejecucion f
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_ramo AS
SELECT
    dr.ramo_sk,
    dr.id_ramo,
    dr.desc_ramo,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_aprobado) AS monto_aprobado,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado,
    SUM(CASE WHEN f.sin_pago THEN 1 ELSE 0 END) AS n_sin_pago,
    SUM(CASE WHEN f.alta_ejecucion THEN 1 ELSE 0 END) AS n_alta_ejecucion
FROM fact_ejecucion f
JOIN dim_ramo dr ON f.ramo_sk = dr.ramo_sk
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY dr.ramo_sk, dr.id_ramo, dr.desc_ramo, dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_ur AS
SELECT
    du.ur_sk,
    du.id_ur,
    du.desc_ur,
    dr.id_ramo,
    dr.desc_ramo,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado,
    SUM(CASE WHEN f.sin_pago THEN 1 ELSE 0 END) AS n_sin_pago
FROM fact_ejecucion f
JOIN dim_ur du ON f.ur_sk = du.ur_sk
JOIN dim_ramo dr ON du.id_ramo = dr.id_ramo
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY du.ur_sk, du.id_ur, du.desc_ur, dr.id_ramo, dr.desc_ramo, dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_entidad AS
SELECT
    de.entidad_sk,
    de.id_entidad_federativa,
    de.entidad_federativa,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado,
    SUM(CASE WHEN f.sin_pago THEN 1 ELSE 0 END) AS n_sin_pago
FROM fact_ejecucion f
JOIN dim_entidad de ON f.entidad_sk = de.entidad_sk
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY de.entidad_sk, de.id_entidad_federativa, de.entidad_federativa, dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_capitulo AS
SELECT
    deco.eco_sk,
    deco.id_capitulo,
    deco.desc_capitulo,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado
FROM fact_ejecucion f
JOIN dim_clasificacion_economica deco ON f.eco_sk = deco.eco_sk
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY deco.eco_sk, deco.id_capitulo, deco.desc_capitulo, dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_programa AS
SELECT
    dfunc.func_sk,
    dfunc.id_pp,
    dfunc.desc_pp,
    dfunc.id_funcion,
    dfunc.desc_funcion,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado
FROM fact_ejecucion f
JOIN dim_clasificacion_funcional dfunc ON f.func_sk = dfunc.func_sk
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY
    dfunc.func_sk,
    dfunc.id_pp,
    dfunc.desc_pp,
    dfunc.id_funcion,
    dfunc.desc_funcion,
    dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_fuente AS
SELECT
    dff.ff_sk,
    dff.id_ff,
    dff.desc_ff,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    CASE
        WHEN SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END) > 0
        THEN SUM(f.monto_pagado)
             / SUM(CASE WHEN f.monto_modificado > 0 THEN f.monto_modificado ELSE 0 END)
        ELSE NULL
    END AS ratio_ejecucion_ponderado
FROM fact_ejecucion f
JOIN dim_fuente_financiamiento dff ON f.ff_sk = dff.ff_sk
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY dff.ff_sk, dff.id_ff, dff.desc_ff, dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_banda AS
SELECT
    f.banda_ejecucion,
    f.tipo_gasto,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado
FROM fact_ejecucion f
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY f.banda_ejecucion, f.tipo_gasto, dt.ciclo;

CREATE OR REPLACE VIEW vw_olap_ejecucion_por_tipo_gasto AS
SELECT
    f.tipo_gasto,
    dt.ciclo,
    COUNT(*) AS n_registros,
    SUM(f.monto_modificado) AS monto_modificado,
    SUM(f.monto_pagado) AS monto_pagado,
    AVG(CASE WHEN f.monto_modificado > 0 THEN f.ratio_ejecucion END) AS ratio_ejecucion_promedio
FROM fact_ejecucion f
JOIN dim_tiempo dt ON f.tiempo_sk = dt.tiempo_sk
GROUP BY f.tipo_gasto, dt.ciclo;
