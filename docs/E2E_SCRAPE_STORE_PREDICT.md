# End-to-End: Scrape → Store → Train → Predict

One-command guide to prove the full pipeline works.

## Prerequisites

All 4 repos cloned as siblings:
```
~/beat-books/
├── beat-books-infra/
├── beat-books-data/
├── beat-books-api/
└── beat-books-model/
```

## Quick Start (One Command)

```bash
cd ~/beat-books/beat-books-infra
bash scripts/e2e_smoke.sh --keep
```

This will:
1. Validate docker-compose config
2. Build and start the full stack (postgres, data, model, api)
3. Wait for all health endpoints
4. Scrape NFL stats (team_offense, team_defense, standings, games) for 2023
5. Train a baseline model (synthetic data if no real data)
6. Run predictions via model service (POST with full team names)
7. Run predictions via API gateway (GET with aliases/nicknames)
8. Print PASS/FAIL summary

### Script Options

| Flag | Description |
|------|-------------|
| `--no-build` | Skip `docker compose up` (stack already running) |
| `--keep` | Don't tear down after tests |
| `--skip-scrape` | Skip scrape step (use existing data) |

### Environment Overrides

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost` | Service base URL |
| `HEALTH_TIMEOUT` | `120` | Seconds to wait for health checks |
| `SCRAPE_SEASON` | `2023` | Season to scrape |

## Manual Step-by-Step

### Step 1: Start the Stack

```bash
cd ~/beat-books/beat-books-infra/docker
cp .env.example .env
echo "DB_PASSWORD=localdev123" >> .env

docker compose up -d --build
docker compose ps   # all 4 services should show "healthy"
```

### Step 2: Scrape Data

**Option A: Batch scrape (preferred)**
```bash
curl -s -X POST http://localhost:8001/scrape/batch/2023 \
  -H "Content-Type: application/json" \
  -d '{"stats": ["team_offense", "team_defense", "standings", "games"], "dry_run": false}' \
  | python3 -m json.tool
```

**Option B: Individual scrapes**
```bash
curl -s http://localhost:8001/scrape/team_offense/2023 | python3 -m json.tool
sleep 5  # respect rate limits
curl -s http://localhost:8001/scrape/team_defense/2023 | python3 -m json.tool
sleep 5
curl -s http://localhost:8001/scrape/standings/2023 | python3 -m json.tool
sleep 5
curl -s http://localhost:8001/scrape/games/2023 | python3 -m json.tool
```

**Rate limiting notes:**
- Pro-Football-Reference rate limits aggressively. The data service respects `SCRAPE_DELAY_SECONDS` (default: 5s in compose).
- Retries are handled automatically with exponential backoff (30s, 60s, 120s).
- Scrapes are idempotent for most stat types (safe to re-run).
- Expected batch scrape time: ~2-5 minutes for 4 stat types.

Note: If `API_KEY` is set, add `-H "X-API-Key: <key>"` to requests.

### Step 3: Verify Data is Stored

```bash
curl -s http://localhost:8001/api/v1/stats/teams/2023 | python3 -m json.tool | head -30
curl -s http://localhost:8001/api/v1/standings/2023 | python3 -m json.tool | head -30
```

Expected: JSON arrays with team data.

### Step 4: Train the Model

**Option A: Inside the container (preferred)**
```bash
cd ~/beat-books/beat-books-infra/docker
docker compose exec model-service python scripts/train_baseline.py \
    --train-seasons 2023 --test-season 2023
```

**Option B: From the host**
```bash
cd ~/beat-books/beat-books-model
cp .env.example .env
echo "DATABASE_URL=postgresql://btb:localdev123@localhost:5432/beatthebooks" >> .env

pip install -r requirements.txt  # or: uv sync
python scripts/train_baseline.py --train-seasons 2023 --test-season 2023
```

**Option C: Synthetic data (no scrape needed)**
```bash
docker compose exec model-service python scripts/train_baseline.py --synthetic
```

Expected output:
```
INFO: Training set: N samples, 11 features
INFO: Model trained successfully
Done! Model ID: <uuid>
```

The `.joblib` artifact is saved to `model_artifacts/` which is mounted into the container.

### Step 5: Get a Prediction

**Via the model service directly (uses full team names):**
```bash
curl -s -X POST http://localhost:8002/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Kansas City Chiefs", "away_team": "Buffalo Bills", "season": 2023}' \
  | python3 -m json.tool
```

**Via the API gateway (uses nicknames/abbreviations):**
```bash
# With team alias mapping (requires API PR #56):
curl -s "http://localhost:8000/predictions/predict?team1=chiefs&team2=bills" \
  | python3 -m json.tool

# Also accepts abbreviations and full names:
curl -s "http://localhost:8000/predictions/predict?team1=KC&team2=BUF" \
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

### Step 6: Check Model Info

```bash
curl -s http://localhost:8002/model/info | python3 -m json.tool
```

## Team Name Mapping

The infra repo provides `docker/resources/team_aliases.json` which maps all forms
of team names to canonical full names:

| Input Forms | Canonical Name |
|-------------|---------------|
| `chiefs`, `kc`, `kansas city` | Kansas City Chiefs |
| `bills`, `buf`, `buffalo` | Buffalo Bills |
| `eagles`, `phi`, `philly`, `philadelphia` | Philadelphia Eagles |
| *(all 32 NFL teams mapped)* | |

This file is volume-mounted into the API container and loaded via `TEAM_ALIASES_PATH`.

## Scraping Configuration

| Env Variable | Default (compose) | Description |
|-------------|-------------------|-------------|
| `SCRAPE_BACKEND` | `scrapling` | Scrape engine (no Chrome needed) |
| `SCRAPE_DELAY_SECONDS` | `5` | Delay between requests |
| `SCRAPE_REQUEST_TIMEOUT` | `30` | HTTP timeout per request |
| `SCRAPE_MAX_RETRIES` | `3` | Retry attempts on failure |
| `SCRAPE_RETRY_DELAYS` | `[30, 60, 120]` | Exponential backoff delays |

## Teardown

```bash
cd ~/beat-books/beat-books-infra/docker
docker compose down -v
```

## Known Limitations

1. **Spread model not implemented**: `predicted_spread` is always `0.0`. Win probability and winner are functional.
2. **Rate limiting**: Pro-Football-Reference may rate-limit scraping. Use batch endpoint and allow retries. Expected scrape time: 2-5 minutes.
3. **Team name mapping**: Gateway accepts abbreviations only when API PR #56 is merged and `team_aliases.json` is mounted. Without it, use full team names for the model service directly.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Scrape returns 401/403 | Set `API_KEY=` (empty) in data-service env to disable auth |
| Scrape returns 429/500 | Rate limited — wait and retry, or use `--skip-scrape` |
| Scrape returns 500 | Check data-service logs: `docker compose logs data-service` |
| Prediction returns 503 | No trained model — run Step 4 |
| Model can't connect to DB | Check DATABASE_URL matches compose postgres settings |
| Team name not found (400) | Use full team names (e.g., "Kansas City Chiefs") or wait for alias PR |
| Gateway returns 502/504 | Model service may still be loading — wait for health check |
