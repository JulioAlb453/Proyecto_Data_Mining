import type {
  ClassificationPredictionResponse,
  DimensionValuesResponse,
  HealthResponse,
  ModelInfoResponse,
  OlapFilters,
  OlapMetaResponse,
  OlapQueryResponse,
  OlapStarResponse,
  OlapAxis,
  PredictionFeatures,
  RegressionPredictionResponse,
} from "../types/api";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
  const base = API_BASE || "";
  const url = new URL(`${base}${path}`, window.location.origin);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== "" && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path.startsWith("http") ? path : buildUrl(path), {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = (await res.json()) as { detail?: string | { msg?: string }[] };
      if (typeof err.detail === "string") detail = err.detail;
      else if (Array.isArray(err.detail)) {
        detail = err.detail.map((d) => d.msg ?? JSON.stringify(d)).join("; ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail || `Error HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

function olapParams(filters: OlapFilters): Record<string, string | number | undefined> {
  return {
    ciclo: filters.ciclo,
    id_ramo: filters.id_ramo,
    desc_ramo: filters.desc_ramo,
    id_ur: filters.id_ur,
    desc_ur: filters.desc_ur,
    id_entidad_federativa: filters.id_entidad_federativa,
    entidad_federativa: filters.entidad_federativa,
    id_capitulo: filters.id_capitulo,
    desc_capitulo: filters.desc_capitulo,
    id_pp: filters.id_pp,
    desc_pp: filters.desc_pp,
    id_funcion: filters.id_funcion,
    id_ff: filters.id_ff,
    desc_ff: filters.desc_ff,
    banda_ejecucion: filters.banda_ejecucion,
    tipo_gasto: filters.tipo_gasto,
    limit: filters.limit,
    offset: filters.offset,
  };
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  olapMeta: () => request<OlapMetaResponse>("/olap/meta"),

  olapKpis: (filters?: OlapFilters) =>
    request<OlapQueryResponse>(buildUrl("/olap/kpis", olapParams(filters ?? {}))),

  olapAggregate: (axis: OlapAxis, filters?: OlapFilters) =>
    request<OlapQueryResponse>(
      buildUrl(`/olap/aggregate/${axis}`, olapParams({ limit: 50, ...filters })),
    ),

  olapStar: (filters?: OlapFilters) =>
    request<OlapStarResponse>(
      buildUrl("/olap/star", olapParams({ limit: 25, offset: 0, ...filters })),
    ),

  olapDimension: (dimension: string) =>
    request<DimensionValuesResponse>(`/olap/dimensions/${dimension}`),

  predictSchema: () => request<ModelInfoResponse>("/predict/schema"),

  predictRegression: (body: PredictionFeatures) =>
    request<RegressionPredictionResponse>("/predict/regression", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  predictClassification: (body: PredictionFeatures) =>
    request<ClassificationPredictionResponse>("/predict/classification", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
