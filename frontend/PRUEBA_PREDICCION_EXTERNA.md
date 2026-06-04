# Guía de prueba externa — Predicción ML (PEF)

Documento para que una persona **sin conocer el código** valide la pestaña **Predicción ML** del frontend y, opcionalmente, los endpoints `POST /predict/*`.

**Proyecto:** `proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto`  
**Última verificación de resultados esperados:** artefactos en `ml/artifacts/` (regresión: `elasticnet`, clasificación: `hist_gbc`).

---

## 1. Qué se está probando

| Salida | Significado |
|--------|-------------|
| **Regresión → `ratio_ejecucion`** | Estimación de \( \text{monto\_pagado} / \text{monto\_modificado} \) **sin** ingresar el pago real. |
| **Clasificación → `alta_ejecucion`** | `1` = “alta ejecución” (en entrenamiento: ratio observado ≥ **0.80**); `0` = no. |
| **Prob. clase positiva** | Confianza del clasificador para la clase 1 (útil por desbalance ~8–9 % de positivos). |

**No debe pedirse ni ingresarse:** `monto_pagado`, `ratio_ejecucion`, `banda_ejecucion`, `alta_ejecucion` (eso es lo que se predice o se excluye por fuga de datos).

---

## 2. Requisitos previos

1. **Python 3.10+** y **Node.js 18+** instalados.
2. En la raíz del proyecto:
   - Warehouse construido: `python -m warehouse.build`
   - Modelos entrenados: `python -m ml`
3. Banner superior del frontend con pills en verde: **Regresión** y **Clasificación**.

### Arranque (dos terminales)

**Terminal A — API**

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Comprobar: abrir http://127.0.0.1:8000/health → JSON con `"regression_model_ready": true` y `"classification_model_ready": true`.

**Terminal B — Frontend**

```powershell
cd c:\IS\DataMining_Slices_and_Code\proyecto_corte_1_full_stack_233298_cruz_jimenez_julio_alberto\frontend
copy .env.example .env
npm install
npm run dev
```

Abrir http://localhost:5173 → pestaña **Predicción ML**.

---

## 3. Caso A — Dejar el formulario como viene (prueba mínima)

Al cargar la página, el formulario trae **valores por defecto**. No modifique ningún campo.

### 3.1 Valores que debe ver (o equivalentes)

| Campo | Valor esperado en pantalla |
|-------|----------------------------|
| `tipo_gasto` | `PROGRAMABLE` |
| `ciclo` | `2026` |
| `monto_aprobado` | `1000000` |
| `monto_modificado` | `1000000` |
| `monto_aprobado_mensual` | `100000` |
| `monto_modificado_mensual` | `100000` |
| Resto de campos numéricos | `0` o vacío |
| Resto de campos de texto | vacío |

### 3.2 Pasos

1. Pulsar **Ejecutar modelos**.
2. Esperar dos tarjetas de resultado (regresión y clasificación), sin error rojo.

### 3.3 Resultados esperados (referencia)

Con los artefactos actuales del repositorio, los valores deben coincidir **aproximadamente** (tolerancia indicada):

| Métrica | Valor esperado | Tolerancia |
|---------|----------------|------------|
| Regresión — predicción | **25.60** (ratio) | ± 0.05 |
| Regresión — modelo | `elasticnet` | exacto |
| Clasificación — etiqueta | **No alta ejecución** (`prediction` = 0) | exacto |
| Clasificación — prob. positiva | **0.34 %** (~0.00341) | ± 0.0005 |
| Clasificación — modelo | `hist_gbc` | exacto |

> **Nota para evaluadores:** la regresión con solo montos genéricos y sin dimensiones descriptivas puede dar ratios **fuera del rango 0–1**; el modelo tiene R² bajo en test (~0.006). Lo importante en este caso es que **la API responde 200** y los números son **reproducibles**, no que el ratio sea “realista” presupuestalmente.

### 3.4 Criterio de éxito — Caso A

- [ ] Botón ejecuta sin mensaje de error.
- [ ] Aparecen ambas tarjetas (regresión + clasificación).
- [ ] Valores numéricos dentro de la tolerancia de la tabla 3.3.

---

## 4. Caso B — Rellenar el formulario (renglón real del warehouse)

Simula un renglón **PROGRAMABLE** de alto volumen (IMSS / pensiones), tomado de `vw_olap_star` en el warehouse del proyecto.  
**No copie** `monto_pagado` ni `ratio_ejecucion` al formulario.

### 4.1 Tabla de captura (copiar al formulario)

| Campo | Valor a ingresar |
|-------|------------------|
| `tipo_gasto` | `PROGRAMABLE` |
| `ciclo` | `2026` |
| `monto_aprobado` | `795824000000` |
| `monto_modificado` | `795824000000` |
| `monto_aprobado_mensual` | `252510633958` |
| `monto_modificado_mensual` | `255816350331.1` |
| `id_ramo` | `19` |
| `desc_ramo` | `Aportaciones a Seguridad Social` |
| `id_ur` | `GYR` |
| `desc_ur` | `Instituto Mexicano del Seguro Social` |
| `id_entidad_federativa` | `9` |
| `entidad_federativa` | `Ciudad de México` |
| `id_capitulo` | `4000` |
| `desc_capitulo` | `Transferencias, asignaciones, subsidios y otras ayudas` |
| `id_ff` | `1` |
| `desc_ff` | `Recursos fiscales` |
| `id_pp` | `3` |
| `desc_pp` | `Pensiones y Jubilaciones en curso de Pago` |
| `gpo_funcional` | `2` |
| `id_funcion` | `6` |
| `id_subfuncion` | `2` |
| `id_ai` | `4` |
| `id_concepto` | `4500` |
| `id_partida_generica` | `452` |
| `id_partida_especifica` | `45203` |
| `id_tipogasto` | `4` |
| `desc_concepto` | `Pensiones y jubilaciones` |
| `desc_partida_generica` | `Jubilaciones` |
| `desc_partida_especifica` | `Transferencias para el pago de pensiones y jubilaciones` |
| `desc_tipogasto` | `Pensiones y jubilaciones` |
| `desc_gpo_funcional` | `Desarrollo Social` |
| `desc_funcion` | `Protección Social` |
| `desc_subfuncion` | `Edad Avanzada` |
| `desc_ai` | `Pensiones y Jubilaciones a cargo del Gobierno Federal` |
| `desc_modalidad` | `Pensiones y jubilaciones` |

Campos no listados: dejar en `0` o vacío.

### 4.2 Resultados esperados — Caso B

| Métrica | Valor esperado | Tolerancia |
|---------|----------------|------------|
| Regresión — predicción | **-0.933** | ± 0.05 |
| Clasificación — etiqueta | **No alta ejecución** | exacto |
| Clasificación — prob. positiva | **~1.77 %** (0.0177) | ± 0.005 |

### 4.3 Referencia solo para el evaluador (no ingresar en el formulario)

Valores **reales** del mismo renglón en el warehouse (para contrastar limitaciones del modelo):

| Campo real | Valor |
|------------|-------|
| `ratio_ejecucion` observado | **0.321** (~32 % ejecutado) |
| `alta_ejecucion` observada | **No** (0) |
| `monto_pagado` | `255248920467.5` |

La predicción del modelo **no tiene por qué** acercarse al ratio real; el ejercicio valida **reproducibilidad del servicio**, no precisión presupuestal.

### 4.4 Criterio de éxito — Caso B

- [ ] Todos los campos de la tabla 4.1 capturados.
- [ ] Respuesta 200 y tarjetas visibles.
- [ ] Resultados dentro de tolerancia de 4.2.

---

## 5. Caso C — Renglón mediano (opcional, más campos “normales”)

Útil si el Caso B resulta tedioso por el tamaño de los montos.

| Campo | Valor |
|-------|-------|
| `tipo_gasto` | `PROGRAMABLE` |
| `ciclo` | `2026` |
| `monto_aprobado` | `0` |
| `monto_modificado` | `5842504.6` |
| `monto_aprobado_mensual` | `0` |
| `monto_modificado_mensual` | `5094428.1` |
| `id_ramo` | `27` |
| `desc_ramo` | `Anticorrupción y Buen Gobierno` |
| `id_ur` | `820` |
| `desc_ur` | `Dirección General de Recursos Humanos y Organización` |
| `id_entidad_federativa` | `9` |
| `entidad_federativa` | `Ciudad de México` |
| `id_capitulo` | `1000` |
| `desc_capitulo` | `Servicios personales` |
| `id_ff` | `1` |
| `desc_ff` | `Recursos fiscales` |
| `id_pp` | `1` |
| `desc_pp` | `Actividades de apoyo administrativo` |
| `gpo_funcional` | `1` |
| `id_funcion` | `3` |
| `id_subfuncion` | `4` |
| `id_ai` | `2` |
| `id_concepto` | `1100` |
| `id_partida_generica` | `113` |
| `id_partida_especifica` | `11301` |
| `id_tipogasto` | `1` |
| `desc_concepto` | `Remuneraciones al personal de carácter permanente` |
| `desc_partida_generica` | `Sueldos base al personal permanente` |
| `desc_partida_especifica` | `Sueldos base` |
| `desc_tipogasto` | `Gasto corriente` |
| `desc_gpo_funcional` | `Gobierno` |
| `desc_funcion` | `Coordinación de la Política de Gobierno` |
| `desc_subfuncion` | `Función Pública` |
| `desc_ai` | `Servicios de apoyo administrativo` |
| `desc_modalidad` | `Apoyo para el desarrollo de las funciones de gobierno` |

**Resultados esperados (referencia):**

| Métrica | Valor | Tolerancia |
|---------|-------|------------|
| Regresión | **4.683** | ± 0.05 |
| Clasificación | No alta ejecución | exacto |
| Prob. positiva | **~13.7 %** (0.137) | ± 0.02 |

**Ratio real en datos (solo referencia):** 0.756 — aún por debajo del umbral 0.80 de `alta_ejecucion`.

---

## 6. Prueba sin interfaz gráfica (API / curl)

### 6.1 Esquema de features

```powershell
curl -s http://127.0.0.1:8000/predict/schema
```

Debe devolver `feature_columns` (lista larga) y modelos en `regression` / `classification`.

### 6.2 Caso A — JSON mínimo (defaults)

```powershell
curl -s -X POST http://127.0.0.1:8000/predict/regression ^
  -H "Content-Type: application/json" ^
  -d "{\"tipo_gasto\":\"PROGRAMABLE\",\"monto_aprobado\":1000000,\"monto_modificado\":1000000,\"monto_aprobado_mensual\":100000,\"monto_modificado_mensual\":100000,\"ciclo\":2026}"

curl -s -X POST http://127.0.0.1:8000/predict/classification ^
  -H "Content-Type: application/json" ^
  -d "{\"tipo_gasto\":\"PROGRAMABLE\",\"monto_aprobado\":1000000,\"monto_modificado\":1000000,\"monto_aprobado_mensual\":100000,\"monto_modificado_mensual\":100000,\"ciclo\":2026}"
```

Respuesta esperada: `"prediction": 25.59767900085319` (regresión) y `"prediction": 0`, `"probability_positive": 0.0034140680208336045` (clasificación).

### 6.3 Caso B — payload completo

Guarde el archivo `frontend/fixtures/predict_caso_b.json` (incluido en el repositorio) y ejecute:

```powershell
curl -s -X POST http://127.0.0.1:8000/predict/regression -H "Content-Type: application/json" -d "@fixtures/predict_caso_b.json"
curl -s -X POST http://127.0.0.1:8000/predict/classification -H "Content-Type: application/json" -d "@fixtures/predict_caso_b.json"
```

*(En PowerShell, si `@` falla, use `Get-Content fixtures/predict_caso_b.json -Raw` como cuerpo.)*

---

## 7. Errores frecuentes

| Síntoma | Causa probable | Acción |
|---------|----------------|--------|
| Pills Regresión/Clasificación apagadas | No existe `ml/artifacts/*.joblib` | `python -m ml` y reiniciar API |
| Error 503 en predicción | Modelos no cargados | Igual que arriba |
| Banner rojo “No se pudo contactar la API” | API no levantada | Terminal A con uvicorn |
| Resultados distintos a la tabla | Artefactos reentrenados | Reejecutar `python -m ml` y actualizar esta guía o comparar con `fixtures/expected_predictions.json` |

---

## 8. Hoja de registro para el probador externo

| Caso | Fecha | ¿OK? | Regresión obtenida | Clasificación (0/1) | Prob. positiva | Observaciones |
|------|-------|------|--------------------|---------------------|----------------|---------------|
| A — defaults | | | | | | |
| B — IMSS | | | | | | |
| C — RH (opcional) | | | | | | |

**Firma / nombre del probador:** ___________________________

---

## 9. Obtener otro renglón desde el warehouse (avanzado)

Si desea armar un **Caso D** propio:

1. Pestaña **Exploración OLAP** → tabla con detalle, o consulta SQL:
   ```sql
   SELECT * FROM vw_olap_star
   WHERE tipo_gasto = 'PROGRAMABLE' LIMIT 5;
   ```
2. Copie al formulario todos los campos de features **excepto** `monto_pagado`, `ratio_ejecucion`, `alta_ejecucion`, `banda_ejecucion`.
3. Anote predicción vs. ratio real solo como análisis crítico (informe), no como criterio de fallo del smoke test.

---

*Documento generado para pruebas de aceptación del módulo de inferencia en vivo. Para arquitectura y métricas de entrenamiento, ver `README.md` y `ml/artifacts/training_metrics.json`.*
