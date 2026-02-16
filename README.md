# BeatTheBooks — NFL Game Prediction Platform

Predict NFL game outcomes, find edges against the sportsbook lines, and size bets optimally using Kelly Criterion.

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ beat-books-  │    │ beat-books-  │    │ beat-books-  │
│ api          │───▶│ data         │    │ model        │
│ (gateway)    │    │ (scraping,   │◀───│ (features,   │
│ port 8000    │───▶│  storage)    │    │  ML, bets)   │
│              │    │ port 8001    │    │ port 8002    │
└──────────────┘    └──────┬───────┘    └──────┬───────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────────────────────────┐
                    │     PostgreSQL (Neon.tech)       │
                    │  beat-books-data: READ/WRITE     │
                    │  beat-books-model: READ ONLY     │
                    └─────────────────────────────────┘
```

## Repos

| Repo | Purpose | Port |
|------|---------|------|
| [beat-books-data](https://github.com/Kame4201/beat-books-data) | NFL data scraping, storage, retrieval | 8001 |
| [beat-books-model](https://github.com/Kame4201/beat-books-model) | ML predictions, backtesting, bet sizing | 8002 |
| [beat-books-api](https://github.com/Kame4201/beat-books-api) | Public API gateway | 8000 |
| [beat-books-infra](https://github.com/Kame4201/beat-books-infra) | CI/CD, docs, Docker | — |

## Quick Start

```bash
# Clone all repos
git clone https://github.com/Kame4201/beat-books-data.git
git clone https://github.com/Kame4201/beat-books-model.git
git clone https://github.com/Kame4201/beat-books-api.git
git clone https://github.com/Kame4201/beat-books-infra.git

# Set up beat-books-data first
cd beat-books-data
pip install -r requirements.txt
cp .env.example .env  # Add your DATABASE_URL
uvicorn src.main:app --reload --port 8001

# Then beat-books-api
cd ../beat-books-api
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --port 8000
```

## Tech Stack

Python 3.11+ · FastAPI · SQLAlchemy · PostgreSQL (Neon.tech) · Alembic · scikit-learn · XGBoost · Selenium · Docker · GitHub Actions

## Roadmap

- **Phase 1 (Foundation)**: Alembic migrations, DTOs, data retrieval API, test infrastructure
- **Phase 2 (Model)**: Odds data, feature engineering, baseline ML model, backtesting
- **Phase 3 (Production)**: Scraper resilience, Kelly Criterion, CI/CD, config management
- **Phase 4 (Scale)**: Injury/weather data, batch scraping, Docker deployment

## Project Management

**Project Board:** [BeatTheBooks Roadmap](https://github.com/users/Kame4201/projects/1) *(Update with your actual project URL)*

Track all issues across the 4 repositories in a single board with phase-based organization. See [docs/github-projects-setup.md](docs/github-projects-setup.md) for setup instructions.

## Documentation

See the [docs/](docs/) folder for detailed architecture, SDLC, and agent documentation.
