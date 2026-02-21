# Inter-Service Contracts

> Defines the HTTP contracts between BeatTheBooks services.
> Every inter-service call must conform to these schemas.
> Related: [API Endpoints](api-endpoints.md) | [Architecture Overview](overview.md)

## Standard Health Check

Every service must expose:

```
GET /health
```

Response (`200 OK`):

```json
{
  "status": "healthy",
  "service": "beat-books-data",
  "version": "0.1.0"
}
```

| Field | Type | Description |
|---|---|---|
| `status` | `str` | Always `"healthy"` if responding |
| `service` | `str` | Service name: `beat-books-data`, `beat-books-model`, `beat-books-api` |
| `version` | `str` | SemVer from `pyproject.toml` |

If the service can respond to HTTP, it returns `200`. If it can't, the caller gets a connection error — there is no `"unhealthy"` response.

## Standard Error Response

All services must return errors in this format:

```json
{
  "error": "NOT_FOUND",
  "detail": "No stats found for team 'invalidteam' in season 2024",
  "status_code": 404
}
```

| Field | Type | Description |
|---|---|---|
| `error` | `str` | Machine-readable error code (UPPER_SNAKE_CASE) |
| `detail` | `str` | Human-readable explanation |
| `status_code` | `int` | HTTP status code (mirrored in body for convenience) |

### Error Codes

| Code | HTTP Status | When |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `SERVICE_UNAVAILABLE` | 503 | Downstream service unreachable |
| `INTERNAL_ERROR` | 500 | Unhandled exception |

### Pydantic Model

```python
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int
```

## Timeouts and Retries

| Caller | Target | Timeout | Retries |
|---|---|---|---|
| beat-books-api | beat-books-data | 10s | None (fail fast) |
| beat-books-api | beat-books-model | 30s | None (fail fast) |
| beat-books-model | PostgreSQL | 5s | None (fail fast) |

**Current policy: no retries.** Services fail fast and return a `503 SERVICE_UNAVAILABLE` error to the caller. Retry logic will be added in a future phase if needed. The API gateway should never silently hang — if a backend is down, tell the user immediately.

## Inter-Service Endpoints

### beat-books-data (port 8001)

Called by: `beat-books-api`

#### Get Team Stats

```
GET /teams/{team}/stats?season={year}
```

| Param | Type | Required | Description |
|---|---|---|---|
| `team` | path `str` | Yes | Team name (e.g. `"chiefs"`) |
| `season` | query `int` | Yes | Season year |

Response (`200 OK`):

```json
{
  "data": {
    "team": "chiefs",
    "season": 2024,
    "offense": { "points_per_game": 27.5, "yards_per_game": 365.2 },
    "defense": { "points_allowed_per_game": 17.3, "yards_allowed_per_game": 310.8 }
  }
}
```

#### Get Games

```
GET /games?season={year}&week={week}
```

| Param | Type | Required | Description |
|---|---|---|---|
| `season` | query `int` | Yes | Season year |
| `week` | query `int` | No | Filter to specific week |

Response (`200 OK`):

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 272,
    "total_pages": 6
  }
}
```

#### Get Standings

```
GET /standings?season={year}
```

| Param | Type | Required | Description |
|---|---|---|---|
| `season` | query `int` | Yes | Season year |

Response (`200 OK`):

```json
{
  "data": [
    { "team": "chiefs", "wins": 11, "losses": 6, "division": "AFC West" }
  ]
}
```

#### Scrape Team

```
GET /scrape/{team}/{year}
```

Response (`200 OK`):

```json
{
  "message": "Scraped stats for chiefs 2024",
  "rows_inserted": 17
}
```

### beat-books-model (port 8002)

Called by: `beat-books-api`

#### Predict Game Outcome

```
POST /predictions/predict
```

Request body:

```json
{
  "home_team": "chiefs",
  "away_team": "eagles",
  "season": 2024,
  "week": 10
}
```

Response (`200 OK`):

```json
{
  "home_team": "chiefs",
  "away_team": "eagles",
  "prediction": {
    "winner": "chiefs",
    "win_probability": 0.62,
    "predicted_spread": -3.5,
    "confidence": "medium"
  },
  "model_version": "0.1.0"
}
```

#### Get Model Info

```
GET /model/info
```

Response (`200 OK`):

```json
{
  "model_type": "XGBoost",
  "model_version": "0.1.0",
  "features_used": 42,
  "training_date": "2024-11-01",
  "accuracy": 0.58
}
```

### beat-books-api (port 8000)

This is the **public-facing gateway**. It does not expose internal endpoints — it proxies to data and model services. Its contracts are with external clients, not other services.

The API gateway is responsible for:
- Routing requests to the correct backend service
- Returning standardized error responses when a backend is unreachable
- Enforcing timeouts per the table above

## Docker Compose Health Checks

All services must declare health checks so `depends_on` can use `condition: service_healthy`:

```yaml
data-service:
  build: ../beat-books-data
  ports:
    - "8001:8001"
  environment:
    DATABASE_URL: postgresql://btb:${DB_PASSWORD}@postgres:5432/beatthebooks
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 10s
    timeout: 5s
    retries: 3
  depends_on:
    postgres:
      condition: service_healthy

model-service:
  build: ../beat-books-model
  ports:
    - "8002:8002"
  environment:
    DATABASE_URL: postgresql://btb:${DB_PASSWORD}@postgres:5432/beatthebooks
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
    interval: 10s
    timeout: 5s
    retries: 3
  depends_on:
    postgres:
      condition: service_healthy

api:
  build: ../beat-books-api
  ports:
    - "8000:8000"
  environment:
    DATA_SERVICE_URL: http://data-service:8001
    MODEL_SERVICE_URL: http://model-service:8002
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 10s
    timeout: 5s
    retries: 3
  depends_on:
    data-service:
      condition: service_healthy
    model-service:
      condition: service_healthy

postgres:
  image: postgres:16
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U btb -d beatthebooks"]
    interval: 5s
    timeout: 3s
    retries: 5
```

## Contract Testing Approach

We use **Option C: JSON schema tests in CI** — the lightest approach that still catches breaking changes.

### How It Works

Each repo has a `tests/test_contracts.py` that validates response shapes against the schemas defined above. These run in CI on every PR.

### Example: beat-books-data

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "service" in body
    assert "version" in body


def test_error_contract():
    response = client.get("/teams/nonexistent/stats?season=9999")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert "detail" in body
    assert "status_code" in body
    assert body["status_code"] == 404
```

### Example: beat-books-api (gateway)

```python
def test_gateway_returns_503_when_backend_down(monkeypatch):
    """API gateway returns standard error when data service is unreachable."""
    response = client.get("/teams/chiefs/stats?season=2024")
    # With no backend running, expect 503
    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "SERVICE_UNAVAILABLE"
    assert body["status_code"] == 503
```

### Why Not Option A or B?

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **A: Shared Pydantic models** | Strong typing, single source of truth | Adds a shared dependency across repos, versioning complexity | Overkill for 3 services |
| **B: OpenAPI snapshot comparison** | Auto-generated, catches any schema drift | Requires OpenAPI export pipeline, diff tooling | More infrastructure than we need now |
| **C: JSON schema tests in CI** | Zero dependencies, runs in existing pytest | Manual — must update tests when contracts change | Right-sized for current scale |

Option C can be upgraded to A or B later if the platform grows.
