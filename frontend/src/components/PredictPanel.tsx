import { FormEvent, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type {
  ClassificationPredictionResponse,
  HealthResponse,
  ModelInfoResponse,
  PredictionFeatures,
  RegressionPredictionResponse,
} from "../types/api";
import { fieldLabel, formatNumber, formatPercent } from "../utils/format";

const DEFAULTS: PredictionFeatures = {
  tipo_gasto: "PROGRAMABLE",
  monto_aprobado: 1_000_000,
  monto_modificado: 1_000_000,
  monto_aprobado_mensual: 100_000,
  monto_modificado_mensual: 100_000,
  ciclo: 2026,
};

const PRIORITY_FIELDS = [
  "tipo_gasto",
  "ciclo",
  "monto_aprobado",
  "monto_modificado",
  "monto_aprobado_mensual",
  "monto_modificado_mensual",
  "id_ramo",
  "desc_ramo",
  "id_ur",
  "desc_ur",
  "id_entidad_federativa",
  "entidad_federativa",
  "id_capitulo",
  "desc_capitulo",
  "id_ff",
  "desc_ff",
  "id_pp",
  "desc_pp",
];

export function PredictPanel({ health }: { health: HealthResponse | null }) {
  const [schema, setSchema] = useState<ModelInfoResponse | null>(null);
  const [values, setValues] = useState<PredictionFeatures>({ ...DEFAULTS });
  const [regResult, setRegResult] = useState<RegressionPredictionResponse | null>(null);
  const [clfResult, setClfResult] = useState<ClassificationPredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [schemaError, setSchemaError] = useState<string | null>(null);

  useEffect(() => {
    api
      .predictSchema()
      .then((s) => {
        setSchema(s);
        const init: PredictionFeatures = { ...DEFAULTS };
        for (const col of s.feature_columns) {
          if (init[col] === undefined) {
            if (s.numeric_features.includes(col)) init[col] = 0;
            else if (col === "tipo_gasto") init[col] = "PROGRAMABLE";
            else init[col] = "";
          }
        }
        setValues(init);
      })
      .catch((e) =>
        setSchemaError(e instanceof Error ? e.message : "No se pudo cargar el esquema"),
      );
  }, []);

  const orderedFields = useMemo(() => {
    if (!schema) return [];
    const cols = schema.feature_columns;
    const ordered = [
      ...PRIORITY_FIELDS.filter((c) => cols.includes(c)),
      ...cols.filter((c) => !PRIORITY_FIELDS.includes(c)),
    ];
    return ordered;
  }, [schema]);

  const modelsReady =
    health?.regression_model_ready && health?.classification_model_ready;

  const setField = (name: string, raw: string) => {
    setValues((prev) => {
      const next = { ...prev };
      if (raw === "") {
        delete next[name];
        return next;
      }
      if (schema?.numeric_features.includes(name)) {
        next[name] = Number(raw);
      } else {
        next[name] = raw;
      }
      return next;
    });
  };

  const buildPayload = (): PredictionFeatures => {
    const payload: PredictionFeatures = {};
    for (const [k, v] of Object.entries(values)) {
      if (v === "" || v === null || v === undefined) continue;
      payload[k] = v;
    }
    return payload;
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!modelsReady) return;
    setLoading(true);
    setError(null);
    setRegResult(null);
    setClfResult(null);
    const payload = buildPayload();
    try {
      const [reg, clf] = await Promise.all([
        api.predictRegression(payload),
        api.predictClassification(payload),
      ]);
      setRegResult(reg);
      setClfResult(clf);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en predicción");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <header className="panel__header">
        <div>
          <h2>Predicción en vivo</h2>
          <p className="panel__subtitle">
            Inferencia contra modelos serializados (<code>POST /predict/*</code>).
          </p>
        </div>
      </header>

      {schemaError && <div className="inline-error">{schemaError}</div>}

      {!modelsReady && (
        <p className="muted">
          Entrene modelos con <code>python -m ml</code> y reinicie la API para habilitar
          regresión y clasificación.
        </p>
      )}

      {schema && (
        <form className="predict-form" onSubmit={onSubmit}>
          <div className="form-grid">
            {orderedFields.map((name) => {
              const isNumeric = schema.numeric_features.includes(name);
              const val = values[name];
              return (
                <label key={name} className={isNumeric ? "" : "form-grid--wide"}>
                  {fieldLabel(name)}
                  {isNumeric ? (
                    <input
                      type="number"
                      step="any"
                      value={val === undefined || val === null ? "" : Number(val)}
                      onChange={(e) => setField(name, e.target.value)}
                    />
                  ) : (
                    <input
                      type="text"
                      value={val === undefined || val === null ? "" : String(val)}
                      onChange={(e) => setField(name, e.target.value)}
                    />
                  )}
                </label>
              );
            })}
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={loading || !modelsReady}>
              {loading ? "Prediciendo…" : "Ejecutar modelos"}
            </button>
          </div>
        </form>
      )}

      {error && <div className="inline-error">{error}</div>}

      <div className="results-grid">
        {regResult && (
          <article className="result-card">
            <h3>Regresión — {regResult.target}</h3>
            <p className="result-card__value">{formatNumber(regResult.prediction)}</p>
            <p className="result-card__meta">Modelo: {regResult.model}</p>
            <p className="result-card__note">{regResult.note}</p>
          </article>
        )}
        {clfResult && (
          <article className="result-card">
            <h3>Clasificación — {clfResult.target}</h3>
            <p className="result-card__value">
              {clfResult.prediction === 1 ? "Alta ejecución" : "No alta ejecución"}
            </p>
            <p className="result-card__meta">
              Prob. clase positiva: {formatPercent(clfResult.probability_positive)} ·{" "}
              {clfResult.model}
            </p>
            <p className="result-card__note">{clfResult.note}</p>
          </article>
        )}
      </div>

      {schema?.regression && (
        <details className="metrics-details">
          <summary>Métricas de entrenamiento (test)</summary>
          <pre>{JSON.stringify(schema.regression.best_test_metrics, null, 2)}</pre>
          {schema.classification && (
            <pre>{JSON.stringify(schema.classification.best_test_metrics, null, 2)}</pre>
          )}
        </details>
      )}
    </section>
  );
}
