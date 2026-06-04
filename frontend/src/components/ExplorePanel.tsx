import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { HealthResponse, OlapAxis, OlapFilters, OlapQueryResponse } from "../types/api";
import { axisLabel, formatNumber } from "../utils/format";
import { AggregateChart } from "./AggregateChart";
import { DataTable } from "./DataTable";

const EXPLORE_AXES: OlapAxis[] = [
  "ramo",
  "ur",
  "entidad",
  "capitulo",
  "programa",
  "fuente",
  "banda",
  "tipo_gasto",
];

interface DimOption {
  value: string;
  label: string;
}

export function ExplorePanel({ health }: { health: HealthResponse | null }) {
  const [axis, setAxis] = useState<OlapAxis>("ramo");
  const [filters, setFilters] = useState<OlapFilters>({ limit: 50 });
  const [kpis, setKpis] = useState<OlapQueryResponse | null>(null);
  const [aggregate, setAggregate] = useState<OlapQueryResponse | null>(null);
  const [ramoOptions, setRamoOptions] = useState<DimOption[]>([]);
  const [bandaOptions, setBandaOptions] = useState<DimOption[]>([]);
  const [tipoOptions, setTipoOptions] = useState<DimOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!health?.warehouse_ready) return;
    Promise.all([
      api.olapDimension("ramo").catch(() => null),
      api.olapDimension("banda_ejecucion").catch(() => null),
      api.olapDimension("tipo_gasto").catch(() => null),
    ]).then(([ramo, banda, tipo]) => {
      if (ramo) {
        setRamoOptions(
          ramo.values.map((v) => ({
            value: String(v.id_ramo),
            label: `${v.id_ramo} — ${String(v.desc_ramo ?? "").slice(0, 50)}`,
          })),
        );
      }
      if (banda) {
        setBandaOptions(
          banda.values.map((v) => ({
            value: String(v.banda_ejecucion),
            label: String(v.banda_ejecucion),
          })),
        );
      }
      if (tipo) {
        setTipoOptions(
          tipo.values.map((v) => ({
            value: String(v.tipo_gasto),
            label: String(v.tipo_gasto),
          })),
        );
      }
    });
  }, [health?.warehouse_ready]);

  const loadData = useCallback(async () => {
    if (!health?.warehouse_ready) return;
    setLoading(true);
    setError(null);
    try {
      const [kpiRes, aggRes] = await Promise.all([
        api.olapKpis(filters),
        api.olapAggregate(axis, filters),
      ]);
      setKpis(kpiRes);
      setAggregate(aggRes);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar OLAP");
    } finally {
      setLoading(false);
    }
  }, [axis, filters, health?.warehouse_ready]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const updateFilter = (key: keyof OlapFilters, value: string) => {
    setFilters((prev) => {
      const next = { ...prev };
      if (value === "") {
        delete next[key];
        return next;
      }
      if (key === "id_ramo" || key === "ciclo" || key === "id_ur") {
        next[key] = Number(value);
      } else {
        (next as Record<string, string | number>)[key] = value;
      }
      return next;
    });
  };

  const kpiRow = kpis?.data?.[0];

  if (!health?.warehouse_ready) {
    return (
      <section className="panel">
        <h2>Exploración presupuestal</h2>
        <p className="muted">
          Construya el warehouse con <code>python -m warehouse.build</code> y reinicie la API.
        </p>
      </section>
    );
  }

  return (
    <section className="panel">
      <header className="panel__header">
        <div>
          <h2>Exploración presupuestal</h2>
          <p className="panel__subtitle">
            Agregados OLAP en vivo desde DuckDB — sin datos precocinados en el cliente.
          </p>
        </div>
        <button type="button" className="btn btn--secondary" onClick={loadData} disabled={loading}>
          {loading ? "Cargando…" : "Actualizar"}
        </button>
      </header>

      <div className="filters">
        <label>
          Eje analítico
          <select value={axis} onChange={(e) => setAxis(e.target.value as OlapAxis)}>
            {EXPLORE_AXES.map((a) => (
              <option key={a} value={a}>
                {axisLabel(a)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Ramo
          <select
            value={filters.id_ramo ?? ""}
            onChange={(e) => updateFilter("id_ramo", e.target.value)}
          >
            <option value="">Todos</option>
            {ramoOptions.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Banda ejecución
          <select
            value={filters.banda_ejecucion ?? ""}
            onChange={(e) => updateFilter("banda_ejecucion", e.target.value)}
          >
            <option value="">Todas</option>
            {bandaOptions.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tipo de gasto
          <select
            value={filters.tipo_gasto ?? ""}
            onChange={(e) => updateFilter("tipo_gasto", e.target.value)}
          >
            <option value="">Todos</option>
            {tipoOptions.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Ciclo
          <input
            type="number"
            placeholder="Ej. 2026"
            value={filters.ciclo ?? ""}
            onChange={(e) => updateFilter("ciclo", e.target.value)}
          />
        </label>
      </div>

      {error && <div className="inline-error">{error}</div>}

      {kpiRow && (
        <div className="kpi-grid">
          {Object.entries(kpiRow)
            .filter(([, v]) => typeof v === "number")
            .slice(0, 6)
            .map(([key, value]) => (
              <article key={key} className="kpi-card">
                <span className="kpi-card__label">{key.replace(/_/g, " ")}</span>
                <span className="kpi-card__value">{formatNumber(value)}</span>
              </article>
            ))}
        </div>
      )}

      {aggregate && (
        <>
          <AggregateChart axis={axis} rows={aggregate.data} />
          <DataTable rows={aggregate.data} />
          <p className="meta-line">
            Vista: <code>{aggregate.view}</code> · {aggregate.row_count} filas · filtros:{" "}
            {JSON.stringify(aggregate.filters_applied) || "{}"}
          </p>
        </>
      )}
    </section>
  );
}
