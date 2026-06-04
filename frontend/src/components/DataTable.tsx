import { fieldLabel, formatNumber } from "../utils/format";

interface Props {
  rows: Record<string, unknown>[];
  maxCols?: number;
}

export function DataTable({ rows, maxCols = 12 }: Props) {
  if (!rows.length) {
    return <p className="muted">Sin filas para los filtros seleccionados.</p>;
  }

  const keys = Object.keys(rows[0]).slice(0, maxCols);

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {keys.map((k) => (
              <th key={k}>{fieldLabel(k)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {keys.map((k) => (
                <td key={k}>
                  {typeof row[k] === "number" ? formatNumber(row[k]) : String(row[k] ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
