import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { axisLabel, chartMetricKey, fieldLabel, formatNumber, rowLabel } from "../utils/format";
import type { OlapAxis } from "../types/api";

interface Props {
  axis: OlapAxis;
  rows: Record<string, unknown>[];
}

export function AggregateChart({ axis, rows }: Props) {
  const metricKey = chartMetricKey(rows);
  const data = rows.slice(0, 15).map((row, i) => ({
    id: i,
    name: rowLabel(row, axis),
    value: Number(row[metricKey] ?? 0),
  }));

  if (!data.length) {
    return <p className="muted">No hay datos para graficar.</p>;
  }

  return (
    <div className="chart-block">
      <p className="chart-caption">
        Top 15 · {axisLabel(axis)} · {fieldLabel(metricKey)}
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis type="number" tickFormatter={(v) => formatNumber(v)} fontSize={11} />
          <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 10 }} />
          <Tooltip
            formatter={(v: number) => [formatNumber(v), fieldLabel(metricKey)]}
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
            }}
          />
          <Bar dataKey="value" fill="var(--accent)" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
