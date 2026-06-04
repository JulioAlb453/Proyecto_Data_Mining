# Datos crudos (PEF)

Colocar aquí una copia de `PEF_avance_gasto.csv` o configurar en `.env` la ruta absoluta al archivo en `Downloads`.

```powershell
copy $env:USERPROFILE\Downloads\PEF_avance_gasto.csv .\data\raw\PEF_avance_gasto.csv
```

No versionar archivos CSV muy grandes si el repositorio lo requiere; en ese caso usar solo `PEF_RAW_CSV` en `.env`.
