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

## Variables

| Variable | Descripción |
|----------|-------------|
| `VITE_API_BASE_URL` | URL de la API (vacío = proxy Vite en dev) |

## Build

```powershell
npm run build
npm run preview
```
