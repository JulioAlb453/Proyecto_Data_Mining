export type OlapAxis =
  | "global"
  | "ramo"
  | "ur"
  | "entidad"
  | "capitulo"
  | "programa"
  | "fuente"
  | "banda"
  | "tipo_gasto";

export interface HealthResponse {
  status: string;
  warehouse_ready: boolean;
  warehouse_path: string;
  regression_model_ready: boolean;
  classification_model_ready: boolean;
  metrics_ready: boolean;
}

export interface OlapMetaResponse {
  axes: string[];
  views: Record<string, string>;
  filterable_star_fields: string[];
}

export interface OlapQueryResponse {
  axis: string;
  view: string;
  row_count: number;
  filters_applied: Record<string, unknown>;
  data: Record<string, unknown>[];
}

export interface OlapStarResponse {
  row_count: number;
  limit: number;
  offset: number;
  filters_applied: Record<string, unknown>;
  data: Record<string, unknown>[];
}

export interface DimensionValuesResponse {
  dimension: string;
  values: Record<string, unknown>[];
}

export interface ModelInfoResponse {
  regression?: Record<string, unknown> | null;
  classification?: Record<string, unknown> | null;
  feature_columns: string[];
  numeric_features: string[];
  categorical_features: string[];
}

export interface RegressionPredictionResponse {
  target: string;
  prediction: number;
  model: string;
  note: string;
}

export interface ClassificationPredictionResponse {
  target: string;
  prediction: number;
  probability_positive: number;
  model: string;
  note: string;
}

export type PredictionFeatures = Record<string, string | number | null>;

export interface OlapFilters {
  ciclo?: number;
  id_ramo?: number;
  desc_ramo?: string;
  id_ur?: number;
  desc_ur?: string;
  id_entidad_federativa?: number;
  entidad_federativa?: string;
  id_capitulo?: number;
  desc_capitulo?: string;
  id_pp?: number;
  desc_pp?: string;
  id_funcion?: number;
  id_ff?: number;
  desc_ff?: string;
  banda_ejecucion?: string;
  tipo_gasto?: string;
  limit?: number;
  offset?: number;
}
