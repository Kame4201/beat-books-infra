# API Endpoints

## Overview

All public endpoints are served through `beat-books-api` (port 8000), which delegates to backend services.

## Current Endpoints (beat-books-data, port 8001)

### Health Check
~~~
GET /
Response: {"status": "ok", "service": "beat-books-data"}
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

## Planned Endpoints

### Data Retrieval (Phase 1)

~~~
GET /teams/{team}/stats?season=2024
GET /players?season=2024&position=QB&page=1&limit=50
GET /games?season=2024&week=1
GET /standings?season=2024
~~~

### Predictions (Phase 2)

~~~
GET /predictions/predict?team1=chiefs&team2=eagles
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
~~~json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "No stats found for team 'invalidteam' in season 2024"
  }
}
~~~

## Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| beat-books-api | 8000 | Public gateway (users hit this) |
| beat-books-data | 8001 | Internal data service |
| beat-books-model | 8002 | Internal prediction service |
