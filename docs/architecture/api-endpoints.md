# API Endpoints

## Overview

All public endpoints are served through `beat-books-api` (port 8000), which delegates to backend services.

## Current Endpoints (beat-books-data, port 8001)

### Health Check
~~~
GET /health
Response: {"status": "healthy", "service": "beat-books-data", "version": "0.1.0"}
~~~

### Scraping

#### Scrape Single Team
~~~
GET /scrape/{team}/{year}
Path Params:
  team: string  — Team name (e.g., "chiefs")
  year: integer — Season year (e.g., 2024)
Response: Scraped stats stored in database
~~~

#### Scrape Team Offense Stats
~~~
GET /scrape/{year}
Path Params:
  year: integer — Season year
Response: Team offense stats for all teams in that season
~~~

#### Batch Scrape from Excel
~~~
POST /scrape/excel
Body: Excel file with URLs to scrape
Response: Batch scraping results
Note: 60-second delay between requests (configurable via SCRAPE_DELAY_SECONDS)
~~~

## Current Endpoints (beat-books-model, port 8002)

### Health Check
~~~
GET /health
Response: {"status": "healthy", "service": "beat-books-model", "version": "0.1.0"}
~~~

### Predict Game Outcome
~~~
POST /predictions/predict
Body:
  {
    "home_team": "chiefs",
    "away_team": "eagles",
    "season": 2024,
    "week": 10
  }
Response:
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
~~~

### Model Info
~~~
GET /model/info
Response:
  {
    "model_type": "XGBoost",
    "model_version": "0.1.0",
    "features_used": 42,
    "training_date": "2024-11-01",
    "accuracy": 0.58
  }
~~~

## Planned Endpoints

### Data Retrieval (Phase 1)

~~~
GET /teams/{team}/stats?season=2024
GET /games?season=2024&week=1
GET /standings?season=2024
~~~

### Odds (Phase 2)

~~~
GET /odds?season=2024&week=1
~~~

## Response Format

### Success
~~~json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 342,
    "total_pages": 7
  }
}
~~~

### Error

> See [service-contracts.md](service-contracts.md) for the full error standard.

~~~json
{
  "error": "NOT_FOUND",
  "detail": "No stats found for team 'invalidteam' in season 2024",
  "status_code": 404
}
~~~

## Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| beat-books-api | 8000 | Public gateway (users hit this) |
| beat-books-data | 8001 | Internal data service |
| beat-books-model | 8002 | Internal prediction service |
