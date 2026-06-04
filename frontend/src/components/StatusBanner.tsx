import type { HealthResponse } from "../types/api";

interface Props {
  health: HealthResponse | null;
  error: string | null;
  loading: boolean;
}

export function StatusBanner({ health, error, loading }: Props) {
  if (loading && !health) {
    return <div className="banner banner--info">Conectando con la API…</div>;
  }
  if (error && !health) {
    return (
      <div className="banner banner--error">
        No se pudo contactar la API. Inicie:{" "}
        <code>uvicorn api.main:app --reload --host 127.0.0.1 --port 8000</code>
        <span className="banner__detail">{error}</span>
      </div>
    );
  }
  if (!health) return null;

  const pills = [
    { ok: health.warehouse_ready, label: "Warehouse DuckDB" },
    { ok: health.regression_model_ready, label: "Regresión" },
    { ok: health.classification_model_ready, label: "Clasificación" },
    { ok: health.metrics_ready, label: "Métricas ML" },
  ];

  return (
    <div className={`banner ${health.warehouse_ready ? "banner--ok" : "banner--warn"}`}>
      <span className="banner__title">API {health.status}</span>
      <div className="banner__pills">
        {pills.map((p) => (
          <span key={p.label} className={`pill ${p.ok ? "pill--ok" : "pill--off"}`}>
            {p.label}
          </span>
        ))}
      </div>
    </div>
  );
}
