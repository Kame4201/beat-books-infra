# BeatTheBooks Cross-Repo Roadmap

> Living document tracking all open issues, dependencies, and phases across the platform.
> Last updated: 2026-02-25

## Phases

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1: Foundation** | Repo structure, CI, Docker, contracts, onboarding | In Progress |
| **Phase 2: Model** | Data ingestion, feature engineering, baseline ML, odds | Not Started |
| **Phase 3: Production** | Deployment, monitoring, releases, security hardening | Not Started |

## Dependency Graph

```
Legend: A ──▶ B means "A must complete before B can start"

  ┌──────────────────── PHASE 1: FOUNDATION ────────────────────┐
  │                                                              │
  │  infra#25 (Reusable CI) ──▶ infra#42 (Smoke Tests)          │
  │                                                              │
  │  infra#43 (Onboarding) ──────────────────────────────┐      │
  │                                                       ▼      │
  │  infra#45 (Dependabot)                          Contributors │
  │  infra#46 (Pre-commit)                          can ramp up  │
  │                                                              │
  │  infra#6  (Archive old model repo)                           │
  │  infra#14 (Markdown lint CI)                                 │
  │  infra#15 (Branch protection)                                │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────── PHASE 2: MODEL ─────────────────────────┐
  │                                                              │
  │  data#4  (Odds API) ──▶ model#1 (Feature Engineering)       │
  │                               │                              │
  │  infra#27 (API rate limits)   ▼                              │
  │                         model#2 (Baseline Model)             │
  │                               │                              │
  │  infra#24 (Model versioning)  ▼                              │
  │                         model#3 (Backtesting)                │
  │                               │                              │
  │                               ▼                              │
  │                         model#4 (Kelly Criterion)            │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────── PHASE 3: PRODUCTION ────────────────────┐
  │                                                              │
  │  infra#41 (Docker registry) ──▶ infra#28 (Deployment)       │
  │                                      │                       │
  │  infra#44 (Versioning/changelog)     ▼                       │
  │                               infra#22 (Env promotion)       │
  │                                      │                       │
  │  infra#26 (DB backup/recovery)       ▼                       │
  │  infra#23 (Monitoring)         Production launch             │
  └──────────────────────────────────────────────────────────────┘
```

## Critical Path to First Deployment

The shortest path from current state to a working production deployment:

1. **infra#25** — Reusable CI workflows (enables consistent CI across repos)
2. **infra#41** — Docker registry strategy (enables image storage)
3. **infra#28** — Deployment runbook (enables hosting)
4. **infra#22** — Environment promotion (enables staging → production flow)

## Issue Inventory by Repo

### beat-books-infra

| Issue | Title | Phase | Priority | Blocked By | Blocks |
|-------|-------|-------|----------|------------|--------|
| #6 | Archive BeatTheBooksModel repo | 1 | Low | — | — |
| #14 | Markdown linting CI | 1 | Low | — | — |
| #15 | Branch protection rules | 1 | Medium | #14 | — |
| #22 | Environment promotion workflow | 3 | Medium | #28 | Production |
| #23 | Monitoring and observability | 3 | Medium | — | Production |
| #24 | Model versioning strategy | 2 | Medium | — | model#2 |
| #25 | Reusable CI workflows | 1 | High | — | #42 |
| #26 | Database backup and recovery | 3 | Medium | — | Production |
| #27 | External API rate limits doc | 2 | Medium | — | data#4 |
| #28 | Deployment runbook | 3 | High | #41 | #22 |
| #29 | This roadmap | 1 | High | — | — |
| #40 | Shared types / contract stubs | 2 | Medium | — | — |
| #41 | Docker image build + registry | 3 | High | — | #28 |
| #42 | Cross-service smoke tests | 1 | Medium | #25 | — |
| #43 | Developer onboarding guide | 1 | High | — | Contributors |
| #44 | Release versioning + changelog | 3 | Medium | — | Production |
| #45 | Dependabot configuration | 1 | Medium | — | — |
| #46 | Pre-commit hooks | 1 | Low | — | — |

### beat-books-data (external — for reference)

| Issue | Title | Phase | Blocked By |
|-------|-------|-------|------------|
| #4 | Live odds integration | 2 | — |
| #6 | Database indexes | 1 | — |
| #7 | Config management | 1 | — |

### beat-books-model (external — for reference)

| Issue | Title | Phase | Blocked By |
|-------|-------|-------|------------|
| #1 | Feature engineering | 2 | data#4 |
| #2 | Baseline model | 2 | model#1 |
| #3 | Backtesting framework | 2 | model#2 |
| #4 | Kelly Criterion | 2 | model#3 |

## How to Update This Document

When closing an issue, mark it as done in the table above by adding ~~strikethrough~~ to the title. When adding new issues, place them in the correct phase and update the dependency graph if needed.
