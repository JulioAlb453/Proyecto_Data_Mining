import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import { ExplorePanel } from "./components/ExplorePanel";
import { PredictPanel } from "./components/PredictPanel";
import { StatusBanner } from "./components/StatusBanner";
import type { HealthResponse } from "./types/api";

type Tab = "explore" | "predict";

export default function App() {
  const [tab, setTab] = useState<Tab>("explore");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  const refreshHealth = useCallback(async () => {
    setHealthLoading(true);
    try {
      const h = await api.health();
      setHealth(h);
      setHealthError(null);
    } catch (e) {
      setHealth(null);
      setHealthError(e instanceof Error ? e.message : "Error de conexión");
    } finally {
      setHealthLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshHealth();
    const id = setInterval(refreshHealth, 30_000);
    return () => clearInterval(id);
  }, [refreshHealth]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__brand">
          <span className="app-header__badge">PEF 2026</span>
          <h1>Ejecución presupuestal federal</h1>
          <p>Proyecto Corte 1 · 233298 · Full Stack + Minería de Datos</p>
        </div>
        <nav className="tabs" aria-label="Secciones">
          <button
            type="button"
            className={`tabs__btn ${tab === "explore" ? "tabs__btn--active" : ""}`}
            onClick={() => setTab("explore")}
          >
            Exploración OLAP
          </button>
          <button
            type="button"
            className={`tabs__btn ${tab === "predict" ? "tabs__btn--active" : ""}`}
            onClick={() => setTab("predict")}
          >
            Predicción ML
          </button>
        </nav>
      </header>

      <StatusBanner health={health} error={healthError} loading={healthLoading} />

      <main className="app-main">
        {tab === "explore" ? (
          <ExplorePanel health={health} />
        ) : (
          <PredictPanel health={health} />
        )}
      </main>

      <footer className="app-footer">
        Datos servidos por FastAPI + DuckDB · UI React (Vite) · sin resultados estáticos
      </footer>
    </div>
  );
}
