# CLAUDE.md — beat-books-infra

## Project Overview
Shared infrastructure, documentation, CI/CD templates, and cross-repo standards for the BeatTheBooks platform. This repo does NOT contain application code.

## Architecture
This repo defines standards and provides infrastructure for 3 application repos:
- beat-books-data (data ingestion & storage)
- beat-books-model (ML predictions & strategy)
- beat-books-api (API gateway)

## Directory Structure
```
docs/              # Shared documentation (architecture, SDLC, agent roles)
ci-templates/      # Reusable GitHub Actions workflow templates
docker/            # docker-compose files for full stack
scripts/           # Developer setup and utility scripts
templates/         # Test fixtures, conftest templates
```

## Rules — ALWAYS Follow
- Keep docs in sync with actual repo structures
- CI templates must work across all repos with minimal modification
- Docker configs must use environment variables (never hardcode secrets)

## Rules — NEVER Do
- NEVER put application code here (no Python services, models, etc.)
- NEVER store secrets or credentials
- NEVER modify this repo to fix bugs in application repos

## Common Commands
```bash
# Start full stack
cd docker && docker-compose up

# Lint docs
markdownlint docs/
```

## Related Repos
- beat-books-data: Data service (port 8001)
- beat-books-model: Prediction service (port 8002)
- beat-books-api: API gateway (port 8000)
