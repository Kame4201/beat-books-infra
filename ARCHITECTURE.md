# Cross-Repo Architecture

## Data Flow

```
Pro-Football-Reference  ──scrape──▶  beat-books-data  ──store──▶  PostgreSQL
The Odds API            ──fetch───▶  beat-books-data  ──store──▶  PostgreSQL

PostgreSQL  ──read──▶  beat-books-model  ──features──▶  ML Model  ──predict──▶  Prediction + Kelly Sizing

User  ──HTTP──▶  beat-books-api  ──route──▶  beat-books-data (stats/scraping)
                                 ──route──▶  beat-books-model (predictions)
```

## Database Ownership

beat-books-data OWNS the database schema:
- Creates all tables via Alembic migrations
- Provides entities (SQLAlchemy models) as source of truth
- READ/WRITE access

beat-books-model has READ-ONLY access:
- Queries existing tables for feature engineering
- NEVER creates, alters, or drops tables

beat-books-api has NO direct database access:
- Routes through beat-books-data for all data operations

## Dependency Chain

```
Phase 1:  beat-books-data (Alembic, DTOs, Read API)
              ↓
Phase 2:  beat-books-model (Features, ML, Backtesting)  ←  depends on data being queryable
              ↓
Phase 3:  beat-books-api (wire predictions)  ←  depends on model existing
```
