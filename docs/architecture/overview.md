# Architecture Overview

## System Architecture

BeatTheBooks is a 4-repo NFL game prediction platform built on a 3-tier architecture pattern.

## High-Level Diagram

~~~
┌─────────────────────────────────────────────────────────────┐
│                        USERS / CLIENTS                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (port 8000)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      beat-books-api                          │
│                     (API Gateway)                            │
│                                                              │
│  Routes only — no business logic                             │
│  /scrape/*  /teams/*  /players/*  /predictions/*             │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐     ┌─────────────────────────────────┐
│   beat-books-data   │     │       beat-books-model           │
│   (Data Service)    │     │     (Prediction Engine)          │
│                     │     │                                  │
│  Scraping           │     │  Feature Engineering             │
│  Storage            │     │  ML Models (Win/Loss, Spread)    │
│  Retrieval          │     │  Backtesting                     │
│  Schema Owner       │     │  Kelly Criterion Bet Sizing      │
│  port 8001          │     │  port 8002                       │
└────────┬────────────┘     └──────────────┬──────────────────┘
         │ READ/WRITE                      │ READ ONLY
         ▼                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL (Neon.tech)                      │
│                                                              │
│  team_offense · team_defense · passing_stats · rushing_stats │
│  receiving_stats · defense_stats · kicking_stats · games     │
│  standings · odds · injury_reports · game_weather            │
└─────────────────────────────────────────────────────────────┘
~~~

## 3-Tier Pattern (within beat-books-data)

Each service repo follows this layered architecture:

~~~
┌──────────────────────────────────────┐
│  Presentation Layer (FastAPI)        │
│  src/main.py, src/routes/            │
│  - HTTP endpoints                     │
│  - Input validation (Pydantic)        │
│  - Response formatting                │
├──────────────────────────────────────┤
│  Business Logic Layer (Services)     │
│  src/services/                       │
│  - Business rules                     │
│  - Data transformation                │
│  - Orchestration                      │
│  - NO direct SQL                      │
├──────────────────────────────────────┤
│  Data Access Layer (Repositories)    │
│  src/repositories/                   │
│  - ALL SQL queries                    │
│  - CRUD operations                    │
│  - Database abstraction               │
│  - NO business logic                  │
└──────────────────────────────────────┘
~~~

## Key Design Decisions

### Repository Pattern
All database interactions go through repository classes that extend `BaseRepository`. This provides testability (mock the repo in unit tests), abstraction (swap PostgreSQL for SQLite in tests), and single responsibility (SQL stays in one place).

### DTO Pattern
Pydantic models validate all external input before it reaches the service layer. `*Create` DTOs handle incoming data, `*Response` DTOs handle outgoing data. These are separate from SQLAlchemy entities to decouple API contracts from DB schema.

### Database Ownership
Only `beat-books-data` can create, alter, or drop tables. Other repos get read-only access. This prevents migration conflicts when multiple AI agents work in parallel.

### Dependency Injection
Services receive repositories via constructor injection, enabling loose coupling and easier testing.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL (Neon.tech) |
| Scraping | Selenium + BeautifulSoup + Pandas |
| ML | scikit-learn, XGBoost, LightGBM |
| Config | Pydantic Settings |
| Testing | pytest, pytest-cov |
| CI/CD | GitHub Actions |
| Containerization | Docker + docker-compose |
