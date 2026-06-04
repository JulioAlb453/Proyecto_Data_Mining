const AXIS_LABELS: Record<string, string> = {
  global: "Global (KPIs)",
  ramo: "Ramo",
  ur: "Unidad responsable",
  entidad: "Entidad federativa",
  capitulo: "Capítulo",
  programa: "Programa",
  fuente: "Fuente de financiamiento",
  banda: "Banda de ejecución",
  tipo_gasto: "Tipo de gasto",
};

const FIELD_LABELS: Record<string, string> = {
  n_registros: "Registros",
  sum_monto_aprobado: "Aprobado (suma)",
  sum_monto_modificado: "Modificado (suma)",
  sum_monto_pagado: "Pagado (suma)",
  avg_ratio_ejecucion: "Ratio ejecución (prom.)",
  pct_sin_pago: "% sin pago",
  pct_alta_ejecucion: "% alta ejecución",
  desc_ramo: "Ramo",
  desc_ur: "UR",
  entidad_federativa: "Entidad",
  desc_capitulo: "Capítulo",
  desc_pp: "Programa",
  desc_ff: "Fuente",
  banda_ejecucion: "Banda",
  tipo_gasto: "Tipo gasto",
  ciclo: "Ciclo",
  monto_aprobado: "Monto aprobado",
  monto_modificado: "Monto modificado",
  monto_pagado: "Monto pagado",
  ratio_ejecucion: "Ratio ejecución",
};

export function axisLabel(axis: string): string {
  return AXIS_LABELS[axis] ?? axis;
}

export function fieldLabel(key: string): string {
  return FIELD_LABELS[key] ?? key.replace(/_/g, " ");
}

export function formatNumber(value: unknown): string {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  if (Number.isInteger(n)) return n.toLocaleString("es-MX");
  return n.toLocaleString("es-MX", { maximumFractionDigits: 4 });
}

export function formatPercent(value: unknown): string {
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  return `${(n * 100).toFixed(1)}%`;
}

/** Etiqueta legible para barras según el eje OLAP activo. */
export function rowLabel(row: Record<string, unknown>, axis: string): string {
  const candidates = [
    "desc_ramo",
    "desc_ur",
    "entidad_federativa",
    "desc_capitulo",
    "desc_pp",
    "desc_ff",
    "banda_ejecucion",
    "tipo_gasto",
    "ciclo",
  ];
  for (const key of candidates) {
    const v = row[key];
    if (v != null && String(v).trim()) return String(v).slice(0, 40);
  }
  if (axis === "global") return "Total";
  return Object.values(row)[0]?.toString().slice(0, 40) ?? "—";
}

export function chartMetricKey(rows: Record<string, unknown>[]): string {
  if (!rows.length) return "n_registros";
  const prefs = ["avg_ratio_ejecucion", "sum_monto_pagado", "sum_monto_modificado", "n_registros"];
  for (const key of prefs) {
    if (key in rows[0] && typeof rows[0][key] === "number") return key;
  }
  const numeric = Object.keys(rows[0]).find(
    (k) => typeof rows[0][k] === "number" && !k.startsWith("id_"),
  );
  return numeric ?? "n_registros";
}
