# How to Test a Dev → Main Release PR

Use this checklist when preparing or reviewing a release PR from `Dev` to `main` in any BeatTheBooks repo.

---

## 1. Unit Tests (per repo)

Run unit tests in each repo on the `Dev` branch before merging.

| Repo | Command | Min Coverage |
|------|---------|-------------|
| beat-books-data | `uv run pytest tests/ -v --cov=src` | 70% |
| beat-books-model | `pytest tests/ -v --cov=src -m "not integration"` | 70% |
| beat-books-api | `pytest tests/ -v --cov=src` | 70% |

**Pass criteria:** All tests pass, coverage meets threshold.

```bash
# Quick all-repo check (run from ~/beat-books)
for repo in beat-books-data beat-books-model beat-books-api; do
  echo "=== $repo ==="
  cd ~/beat-books/$repo
  git checkout Dev && git pull
  pip install -r requirements.txt 2>/dev/null || uv sync 2>/dev/null
  pytest tests/ -v --tb=short 2>&1 | tail -5
  echo ""
done
```

---

## 2. Contract Checks

Verify that service contracts (URLs, schemas, health responses) are consistent.

### Health endpoint contract

Each service must return JSON from `GET /health`:

```json
{
  "status": "healthy",
  "service": "<service-name>"
}
```

| Service | Port | Expected `service` value |
|---------|------|-------------------------|
| beat-books-api | 8000 | `beat-books-api` |
| beat-books-data | 8001 | `beat-books-data` |
| beat-books-model | 8002 | `beat-books-model` |

### Service URL expectations

| Consumer | Env Var | Expected Value (Docker) |
|----------|---------|------------------------|
| beat-books-api | `DATA_SERVICE_URL` | `http://data-service:8001` |
| beat-books-api | `MODEL_SERVICE_URL` | `http://model-service:8002` |
| beat-books-data | `DATABASE_URL` | `postgresql://btb:<pw>@postgres:5432/beatthebooks` |
| beat-books-model | `DATABASE_URL` | `postgresql://btb:<pw>@postgres:5432/beatthebooks` |

### Error response contract

All services must return structured errors:

```json
{
  "detail": "Human-readable error message"
}
```

Verify: `GET /teams/nonexistent_team_xyz/stats?season=9999` returns HTTP 404 with JSON body.

---

## 3. E2E Smoke Test

The automated E2E smoke test validates the full scrape → store → predict pipeline.

### Run it

```bash
cd ~/beat-books/beat-books-infra

# Full run (builds stack, tests, tears down)
bash scripts/e2e_smoke.sh

# Stack already running
bash scripts/e2e_smoke.sh --no-build

# Keep stack after tests (for manual inspection)
bash scripts/e2e_smoke.sh --keep
```

### What it checks

| Step | Check | Expected |
|------|-------|----------|
| 0 | `docker compose config` valid | Exit 0 |
| 1 | Stack builds and starts | All containers up |
| 2 | Health endpoints respond | HTTP 200 within 120s |
| 3 | Health schema correct | `status=healthy`, `service` field present |
| 4 | Scrape trigger | HTTP 200 or 401 (auth-protected) |
| 4 | Data retrieval | HTTP 200 with valid JSON |
| 5 | Model prediction | HTTP 200 with `winner` field |
| 6 | API Gateway proxy to data | HTTP 200 or 404 |
| 6 | API Gateway proxy to model | HTTP 200 with prediction |

### Exit codes

- `0` = All checks passed
- `1` = One or more checks failed

---

## 4. Manual Spot Checks

After the E2E smoke passes, do these quick manual verifications:

### Health endpoints

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
curl -s http://localhost:8001/health | python3 -m json.tool
curl -s http://localhost:8002/health | python3 -m json.tool
```

### One sample prediction (via API gateway)

```bash
curl -s "http://localhost:8000/predictions/predict?team1=KC&team2=BUF" | python3 -m json.tool
```

Expected: JSON response with `home_team`, `away_team`, `prediction.winner`, `prediction.win_probability`.

### Data retrieval

```bash
curl -s "http://localhost:8001/api/v1/stats/teams/2023" | python3 -m json.tool | head -20
```

Expected: JSON array (may be empty if no data scraped yet, but must be valid JSON).

### Container health

```bash
cd ~/beat-books/beat-books-infra/docker
docker compose ps
```

Expected: All 4 services show `healthy` status.

---

## 5. Scrape → Store → Predict: What "Done" Looks Like

The scrape → store → predict pipeline is **complete** when:

### Scrape (beat-books-data)

- [ ] `GET /scrape/team_offense/2023` returns HTTP 200 and scrapes Pro-Football-Reference
- [ ] Data appears in the `team_offense` PostgreSQL table
- [ ] Scrape respects rate limits (`SCRAPE_DELAY_SECONDS`)
- [ ] Auth is enforced if `API_KEY` is configured

### Store (beat-books-data)

- [ ] `GET /api/v1/stats/teams/2023` returns the scraped data as JSON
- [ ] Data is queryable by team: `GET /api/v1/stats/teams/2023/KC`
- [ ] Database schema matches entity definitions (Alembic migrations applied)

### Predict (beat-books-model)

- [ ] `POST /predictions/predict` with `{"home_team": "KC", "away_team": "BUF"}` returns a prediction
- [ ] Response includes `winner`, `win_probability`, `predicted_spread`, `confidence`
- [ ] Model service loads trained artifact from `model_artifacts/` (or returns stub prediction)

### End-to-End (beat-books-api)

- [ ] `GET /predictions/predict?team1=KC&team2=BUF` via API gateway returns prediction
- [ ] API gateway correctly proxies to both data and model services
- [ ] All health endpoints return `status: healthy`

### Current Known Gaps

1. **Model is in stub mode**: `beat-books-model` returns hardcoded 50/50 predictions. Real predictions require training a model and placing the `.joblib` artifact in `model_artifacts/`.
2. **Scraping requires browser**: The team game-log scraper (`/scrape/team-gamelog/`) needs Selenium + Chrome. Season stat scrapes (`/scrape/team_offense/`) also use Selenium. This won't work in Docker without a headless Chrome setup.
3. **No odds data yet**: The Odds API integration (`ODDS_API_KEY`) is not yet connected to the prediction pipeline.

---

## Release PR Body Template

Copy-paste this into your dev → main PR description:

```markdown
## Release: Dev → Main

### Changes
<!-- List key changes from git log -->

### Test Results

- [ ] Unit tests pass in all repos (beat-books-data, beat-books-model, beat-books-api)
- [ ] Coverage meets 70% threshold
- [ ] E2E smoke test passes (`bash scripts/e2e_smoke.sh`)
- [ ] Health endpoints verified manually
- [ ] Sample prediction returns valid response
- [ ] Contract checks pass (health schema, error responses)

### Known Limitations
<!-- List any known issues or gaps -->

### Test Plan
See [docs/RELEASE_TESTING.md](docs/RELEASE_TESTING.md) for full testing procedures.
```
