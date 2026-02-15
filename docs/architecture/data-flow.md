# Data Flow

## Scraping Flow (Current)

~~~
User Request                Pro-Football-Reference          PostgreSQL
     │                              │                           │
     │  GET /scrape/chiefs/2024     │                           │
     ├─────────────────────▶        │                           │
     │                     │        │                           │
     │              ScrapeService   │                           │
     │                     │        │                           │
     │                     │  HTTP GET (Selenium)               │
     │                     ├───────────────────▶                │
     │                     │        │                           │
     │                     │  HTML Response                     │
     │                     ◀───────────────────┤                │
     │                     │        │                           │
     │              BeautifulSoup   │                           │
     │              Parse HTML      │                           │
     │                     │        │                           │
     │              Repository      │                           │
     │                     │  INSERT/UPSERT                     │
     │                     ├───────────────────────────────────▶│
     │                     │        │                           │
     │  200 OK             │        │                           │
     ◀─────────────────────┤        │                           │
~~~

## Data Retrieval Flow (Planned — Phase 1)

~~~
User ──▶ beat-books-api ──▶ beat-books-data ──▶ PostgreSQL
                                    │
                              StatsRetrievalService
                              Repository.find_by_*()
                                    │
User ◀── JSON response ◀── Response DTO ◀── Query result
~~~

## Prediction Flow (Planned — Phase 2)

~~~
User ──▶ beat-books-api ──▶ beat-books-model ──▶ PostgreSQL (read-only)
                                    │
                              FeatureEngineering
                              → ML Model predict
                              → Kelly Criterion sizing
                                    │
User ◀── JSON response ◀── Prediction + bet recommendation
~~~

## Feature Engineering Flow (Planned — Phase 2)

For each team, for each game, compute features using ONLY data from BEFORE the game date (no look-ahead bias):

- 3/5/10-game rolling averages (points, yards, turnovers)
- Home/away splits, rest days, strength of schedule
- Red zone efficiency, third-down conversion rate
- Current win/loss streak, bye week indicator
