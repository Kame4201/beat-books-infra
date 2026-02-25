# Developer Onboarding Guide

> Get the full BeatTheBooks platform running locally in under 10 minutes.

## Prerequisites

| Tool | Minimum Version | Install |
|------|----------------|---------|
| Git | 2.30+ | [git-scm.com](https://git-scm.com/) |
| Docker | 20.10+ | [docker.com](https://www.docker.com/get-started/) |
| Docker Compose | v2+ | Included with Docker Desktop |
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) (for local dev without Docker) |
| gh CLI | 2.0+ | [cli.github.com](https://cli.github.com/) (optional, recommended) |

## Quick Start (automated)

```bash
# Clone the infra repo first
git clone https://github.com/Kame4201/beat-books-infra.git
cd beat-books-infra

# Run the bootstrap script
bash scripts/bootstrap.sh
```

The script will:
1. Check that prerequisites are installed
2. Clone all 4 repos as siblings in the same parent directory
3. Create `.env` files from `.env.example` templates
4. Start the full stack via Docker Compose (dev mode)
5. Wait for health checks to pass

Use `--skip-docker` if you only want to clone repos and set up env files.

## Manual Setup

If you prefer to set things up step-by-step:

### 1. Clone all repos

```bash
mkdir beatthebooks && cd beatthebooks
git clone https://github.com/Kame4201/beat-books-data.git
git clone https://github.com/Kame4201/beat-books-model.git
git clone https://github.com/Kame4201/beat-books-api.git
git clone https://github.com/Kame4201/beat-books-infra.git
```

### 2. Configure environment

```bash
cd beat-books-infra/docker
cp .env.example .env
# Edit .env — set DB_PASSWORD at minimum
```

### 3. Start with Docker Compose

```bash
# Development mode (hot reload)
./scripts/docker-up.sh dev

# Production mode
./scripts/docker-up.sh

# Test mode
./scripts/docker-up.sh test
```

### 4. Verify

```bash
curl http://localhost:8000/health  # API gateway
curl http://localhost:8001/health  # Data service
curl http://localhost:8002/health  # Model service
```

## Repo Overview

```
beatthebooks/
├── beat-books-infra/    # You are here — CI, docs, Docker, scripts
├── beat-books-data/     # Data scraping + storage (port 8001)
├── beat-books-model/    # ML predictions (port 8002)
└── beat-books-api/      # API gateway (port 8000)
```

| Repo | Responsibility | Port | Database Access |
|------|---------------|------|-----------------|
| beat-books-data | NFL stat scraping, storage, retrieval | 8001 | Read/Write (schema owner) |
| beat-books-model | Feature engineering, ML models, bet sizing | 8002 | Read Only |
| beat-books-api | Public API gateway, routing | 8000 | None (proxies to services) |
| beat-books-infra | CI templates, Docker configs, docs, scripts | — | None |

## Branching Workflow

All repos use the same branching model:

```
feature/* → Dev → stage → main
```

- Create feature branches from `Dev`
- PRs target `Dev`
- Promotion PRs: `Dev → stage → main`

See [docs/sdlc/git-workflow.md](sdlc/git-workflow.md) for details.

## Key Documentation

| Doc | Path | Description |
|-----|------|-------------|
| Architecture Overview | [docs/architecture/overview.md](architecture/overview.md) | System design and tech stack |
| Service Contracts | [docs/architecture/service-contracts.md](architecture/service-contracts.md) | HTTP API contracts between services |
| Database Schema | [docs/architecture/database-schema.md](architecture/database-schema.md) | Table definitions |
| Testing Standards | [docs/sdlc/testing-standards.md](sdlc/testing-standards.md) | Test patterns and coverage requirements |
| Secret Management | [docs/operations/secret-management.md](operations/secret-management.md) | How secrets are handled |
| Roadmap | [docs/roadmap.md](roadmap.md) | Cross-repo issue tracking and phases |

## Troubleshooting

**Docker Compose fails to build:**
- Ensure all 4 repos are cloned as siblings in the same directory
- Check that Docker Desktop is running

**Service health check fails:**
- Check logs: `docker compose -f docker/docker-compose.yml logs <service-name>`
- Ensure `.env` has valid `DB_PASSWORD`

**Port conflict:**
- Default ports: 8000, 8001, 8002, 5432
- Stop any local services on these ports before starting
