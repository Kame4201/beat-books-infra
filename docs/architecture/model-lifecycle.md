# Model Versioning and Experiment Tracking Strategy

> Defines how ML models are versioned, experiments are tracked, and models are promoted to production in beat-books-model.
> Related: [Architecture Overview](overview.md) | [Service Contracts](service-contracts.md) | [Release Versioning](../sdlc/versioning.md)

## Model vs Service Versioning

| Concept | What it tracks | Example |
|---------|---------------|---------|
| **Service version** | The beat-books-model application code | `0.2.0` (from `pyproject.toml`) |
| **Model version** | The trained ML artifact being served | `xgboost_spread_v3_20260215` |

These are independent. A new service version can ship with the same model, and a new model can be hot-swapped without changing the service code.

The `/predictions/predict` response includes `model_version` to identify which model made each prediction:

```json
{
  "prediction": { "winner": "chiefs", "win_probability": 0.62 },
  "model_version": "xgboost_spread_v3_20260215"
}
```

## Model Naming Convention

```
{algorithm}_{target}_{version}_{date}
```

| Component | Values | Example |
|-----------|--------|---------|
| `algorithm` | `xgboost`, `lightgbm`, `logistic`, `ensemble` | `xgboost` |
| `target` | `spread`, `moneyline`, `total`, `winner` | `spread` |
| `version` | `v1`, `v2`, ... (increments per target) | `v3` |
| `date` | `YYYYMMDD` of training | `20260215` |

Example: `xgboost_spread_v3_20260215`

## Experiment Tracking

### What to log per training run

| Category | Fields |
|----------|--------|
| **Identity** | model_name, version, training_date, trained_by |
| **Data** | training_data_range (e.g., 2020-2024), num_samples, feature_count |
| **Features** | feature_list, feature_importance_top_10 |
| **Hyperparameters** | All model hyperparameters (learning_rate, max_depth, etc.) |
| **Performance** | accuracy, precision, recall, AUC, f1_score |
| **Backtest** | backtest_roi, backtest_win_rate, backtest_profit_loss |
| **Metadata** | training_duration_seconds, model_size_bytes |

### Storage format: JSON experiment log

Start simple — a JSON file per experiment, stored in `experiments/` (gitignored):

```json
{
  "model_name": "xgboost_spread_v3_20260215",
  "algorithm": "xgboost",
  "target": "spread",
  "version": "v3",
  "training_date": "2026-02-15",
  "training_data_range": "2020-01-01 to 2025-12-31",
  "num_samples": 5120,
  "features": ["home_ppg", "away_ppg", "home_ypg", "away_ypg", "..."],
  "hyperparameters": {
    "learning_rate": 0.1,
    "max_depth": 6,
    "n_estimators": 200,
    "subsample": 0.8
  },
  "metrics": {
    "accuracy": 0.583,
    "auc": 0.621,
    "f1_score": 0.574
  },
  "backtest": {
    "roi": 0.034,
    "win_rate": 0.547,
    "total_bets": 312,
    "profit_loss": 340.00
  },
  "training_duration_seconds": 45,
  "model_size_bytes": 245760
}
```

### Future: MLflow (when needed)

If experiment volume grows beyond what JSON files can handle, migrate to MLflow:

```python
import mlflow

mlflow.set_experiment("spread_prediction")
with mlflow.start_run(run_name="xgboost_spread_v3"):
    mlflow.log_params(hyperparameters)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, "model")
```

**Not recommended yet** — adds infrastructure complexity (MLflow server, artifact store). JSON logs are sufficient for early development.

## Model Storage

### Development (local)

```
beat-books-model/
├── models/              # gitignored — trained model files
│   ├── xgboost_spread_v3_20260215.joblib
│   └── current.joblib   # symlink to active model
├── experiments/         # gitignored — experiment logs
│   ├── xgboost_spread_v1_20260101.json
│   ├── xgboost_spread_v2_20260201.json
│   └── xgboost_spread_v3_20260215.json
```

### Production

| Stage | Storage | Details |
|-------|---------|---------|
| Phase 1 | Bundled in Docker image | Model file baked into the image at build time |
| Phase 2 | Cloud storage (S3/GCS) | Model downloaded at startup; enables hot-swap |
| Phase 3 | Model registry (MLflow) | Full lifecycle management |

**Start with Phase 1** — simplest, no extra infrastructure. The model is trained locally, committed to a `models/` path (or downloaded during Docker build), and served.

## Serialization Format

| Format | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| `joblib` | Fast, standard for scikit-learn/XGBoost | Python-only | **Use for Phase 1** |
| `pickle` | Built-in | Security concerns, version-sensitive | Avoid |
| `ONNX` | Cross-language, optimized inference | Extra conversion step | Consider for Phase 2 |

## Model Promotion Workflow

```
Train new model
      │
      ▼
Run backtest on holdout data
      │
      ▼
Compare to current production model
      │
  ┌───┴───┐
  │       │
Better?  Worse?
  │       │
  ▼       ▼
Promote  Discard
  │
  ▼
Update current.joblib symlink (local)
  or push to cloud storage (production)
  │
  ▼
Rebuild Docker image with new model
  │
  ▼
Deploy via normal promotion flow
(Dev → stage → main)
```

### "Better" criteria

A new model is considered better if it meets **all** of:

| Metric | Threshold |
|--------|-----------|
| Backtest accuracy | >= current model accuracy |
| Backtest ROI | > 0% (profitable) |
| Backtest win rate | >= 52% (above break-even for -110 odds) |
| No regression on any metric | > 2% drop = reject |

## Implementation Checklist

- [ ] Add `models/` and `experiments/` to `.gitignore` in beat-books-model
- [ ] Create experiment logging utility in beat-books-model
- [ ] Implement model loading at startup (from `models/current.joblib`)
- [ ] Expose `model_version` in `/predictions/predict` response
- [ ] Expose `model_version` in `/model/info` endpoint
- [ ] Document promotion criteria in beat-books-model README
