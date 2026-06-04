# Machine learning

Pipelines de entrenamiento, evaluación y serialización.

- **Regresión:** al menos dos modelos; métricas MAE / RMSE / R² según el target.
- **Clasificación:** al menos dos algoritmos; F1, recall, PR-AUC ante desbalance.
- Artefactos en `ml/artifacts/` (modelos `.joblib`, preprocessor).

Control explícito de **data leakage** (no usar montos colineales con el target de forma indebida).
