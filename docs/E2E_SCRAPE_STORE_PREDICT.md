# End-to-End: Scrape → Store → Predict

Step-by-step guide to prove the full pipeline works.

## Prerequisites

All 4 repos cloned as siblings:
```
~/beat-books/
├── beat-books-infra/
├── beat-books-data/
├── beat-books-api/
└── beat-books-model/
```

## Step 1: Start the Stack

```bash
cd ~/beat-books/beat-books-infra/docker
cp .env.example .env
# Set DB_PASSWORD in .env (any value for local dev)
echo "DB_PASSWORD=localdev123" >> .env

docker compose up -d --build
```

Wait for all services to be healthy:
```bash
docker compose ps
# All 4 services should show "healthy"
```

## Step 2: Scrape Data (via data service)

Scrape team offense stats for a season:
```bash
# Season stat scrape (uses Scrapling — no Chrome needed)
curl -s http://localhost:8001/scrape/team_offense/2023 | python3 -m json.tool

# Scrape more stat types for better model training
curl -s http://localhost:8001/scrape/team_defense/2023
curl -s http://localhost:8001/scrape/standings/2023
curl -s http://localhost:8001/scrape/games/2023
```

Note: If API_KEY is set, add `-H "X-API-Key: <key>"` to requests.

## Step 3: Verify Data is Stored

```bash
curl -s http://localhost:8001/api/v1/stats/teams/2023 | python3 -m json.tool | head -30
curl -s http://localhost:8001/api/v1/standings/2023 | python3 -m json.tool | head -30
```

Expected: JSON arrays with team data.

## Step 4: Train the Model

Run training from the host (connects to the same Postgres):
```bash
cd ~/beat-books/beat-books-model
cp .env.example .env
echo "DATABASE_URL=postgresql://btb:localdev123@localhost:5432/beatthebooks" >> .env

pip install -r requirements.txt  # or: uv sync
python scripts/train_baseline.py --train-seasons 2023 --test-season 2023
```

Or run training inside the model container:
```bash
docker compose exec model-service python scripts/train_baseline.py \
    --train-seasons 2023 --test-season 2023
```

Expected output:
```
INFO: Training set: N samples, 11 features
INFO: Model trained successfully
INFO: Test metrics: {'accuracy': 0.XX, ...}
Done! Model ID: <uuid>
```

The `.joblib` artifact is saved to `model_artifacts/` which is mounted into the container.

## Step 5: Get a Prediction

Via the model service directly:
```bash
curl -s -X POST http://localhost:8002/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Kansas City Chiefs", "away_team": "Buffalo Bills", "season": 2023}' \
  | python3 -m json.tool
```

Via the API gateway:
```bash
curl -s "http://localhost:8000/predictions/predict?team1=Kansas+City+Chiefs&team2=Buffalo+Bills" \
  | python3 -m json.tool
```

Expected response:
```json
{
    "home_team": "Kansas City Chiefs",
    "away_team": "Buffalo Bills",
    "prediction": {
        "winner": "Kansas City Chiefs",
        "win_probability": 0.62,
        "predicted_spread": 0.0,
        "confidence": "medium"
    },
    "model_version": "1.0.0"
}
```

## Step 6: Check Model Info

```bash
curl -s http://localhost:8002/model/info | python3 -m json.tool
```

Expected:
```json
{
    "model_type": "win_loss_classifier",
    "model_version": "1.0.0",
    "features_used": 11,
    "training_date": "2026-...",
    "accuracy": 0.XX
}
```

## Teardown

```bash
cd ~/beat-books/beat-books-infra/docker
docker compose down -v
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Scrape returns 401/403 | Set `API_KEY=` (empty) in data-service env to disable auth |
| Scrape returns 500 | Check data-service logs: `docker compose logs data-service` |
| Prediction returns 503 | No trained model — run Step 4 |
| Model can't connect to DB | Check DATABASE_URL matches compose postgres settings |
| Team name not found | Use full team names as stored in standings.tm (e.g. "Kansas City Chiefs") |
