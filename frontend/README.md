# Frontend PEF — React + Vite

Panel de exploración OLAP y predicción ML conectado a la API FastAPI.

## Arranque

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

En otra terminal, con warehouse y (opcional) modelos ML listos:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir http://localhost:5173

**Prueba externa de predicción:** ver [PRUEBA_PREDICCION_EXTERNA.md](./PRUEBA_PREDICCION_EXTERNA.md) (casos A/B/C con datos y resultados esperados).

## Variables

| Variable | Descripción |
|----------|-------------|
| `VITE_API_BASE_URL` | URL de la API (vacío = proxy Vite en dev) |

## Build

```powershell
npm run build
npm run preview
```
