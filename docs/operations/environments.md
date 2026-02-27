# Environment Promotion Workflow

> Defines what each environment means, what infrastructure backs it, and how changes flow from development to production.
> Related: [Git Workflow](../sdlc/git-workflow.md) | [Deployment Runbook](deployment-runbook.md) | [Docker Registry](docker-registry.md)

## Environments

| Environment | Git Branch | Purpose | Infrastructure | Database |
|-------------|-----------|---------|----------------|----------|
| **Local Dev** | `feature/*` | Developer workstation | Docker Compose | Local PostgreSQL (ephemeral container) |
| **CI** | Any (on PR) | Automated testing | GitHub Actions runners | SQLite or test PostgreSQL (ephemeral) |
| **Staging** | `stage` | Pre-production validation | Hosting platform (TBD) | Neon.tech branch (isolated copy) |
| **Production** | `main` | Live system | Hosting platform (TBD) | Neon.tech main branch |

## Promotion Flow

```
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  feature/*   │────▶│     Dev      │────▶│    stage     │────▶│    main      │
  │  (develop)   │ PR  │  (integrate) │ PR  │  (validate)  │ PR  │ (production) │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
        │                     │                    │                    │
   Local tests           CI runs            Smoke tests          Auto-deploy
   Developer review      Auto-merge OK      Manual approval      Tag release
```

### Step 1: Feature → Dev

| Item | Details |
|------|---------|
| **Trigger** | Developer opens PR from `feature/*` to `Dev` |
| **Gate** | CI passes (lint, test, type-check, security) |
| **Approval** | 0 required (developer can self-merge) |
| **Deploy** | No deployment — Dev is an integration branch |

### Step 2: Dev → Stage

| Item | Details |
|------|---------|
| **Trigger** | Maintainer opens promotion PR from `Dev` to `stage` |
| **Gate** | CI passes + all feature PRs merged cleanly |
| **Approval** | 1 reviewer recommended |
| **Deploy** | Auto-deploy to staging environment (when configured) |
| **Post-deploy** | Run smoke tests (`scripts/smoke-test.sh`) against staging URL |

### Step 3: Stage → Main

| Item | Details |
|------|---------|
| **Trigger** | Maintainer opens promotion PR from `stage` to `main` |
| **Gate** | CI passes + smoke tests pass on staging |
| **Approval** | 1 reviewer required (branch protection) |
| **Deploy** | Auto-deploy to production (when configured) |
| **Post-deploy** | Run smoke tests against production URL, monitor for errors |

## Database Strategy per Environment

| Environment | Database | Connection | Migrations |
|-------------|----------|------------|------------|
| **Local Dev** | Docker PostgreSQL (`postgres:16`) | `postgresql://btb:password@localhost:5432/beatthebooks` | Run `alembic upgrade head` locally |
| **CI** | Ephemeral (test fixtures or SQLite) | Configured per test | Not applicable |
| **Staging** | Neon.tech branch | Branch-specific connection string | Run before smoke tests |
| **Production** | Neon.tech main | Production connection string | Run during deploy, with backup first |

### Neon.tech Branching for Staging

```bash
# Create a staging branch from production (instant, copy-on-write)
neonctl branches create --name staging --parent main

# Get the connection string for the staging branch
neonctl connection-string --branch staging
```

This gives staging an isolated database that starts as a copy of production. Changes in staging don't affect production.

## Rollback Procedure

### Application rollback

```bash
# Option 1: Revert the merge commit on main
git revert <merge-commit-sha>
git push origin main
# Auto-deploy will pick up the revert

# Option 2: Deploy a specific previous image
# (platform-specific — see deployment-runbook.md)
```

### Database rollback

```bash
# If a migration caused the issue:
cd beat-books-data
alembic downgrade -1

# If data corruption:
# Switch to a Neon.tech branch created before the deploy
# See docs/operations/database-ops.md for details
```

## Environment Variables

Each environment needs its own set of environment variables. Never share credentials between environments.

| Variable | Local Dev | CI | Staging | Production |
|----------|-----------|-----|---------|------------|
| `DATABASE_URL` | Docker PostgreSQL | Test DB | Neon staging branch | Neon production |
| `DATA_SERVICE_URL` | `http://localhost:8001` | Mock/test | Internal staging URL | Internal prod URL |
| `MODEL_SERVICE_URL` | `http://localhost:8002` | Mock/test | Internal staging URL | Internal prod URL |
| `ODDS_API_KEY` | Test key or empty | Empty | Test key | Production key |

## Checklist

- [ ] Hosting platform chosen for staging and production
- [ ] Neon.tech staging branch created
- [ ] Staging environment variables configured
- [ ] Production environment variables configured
- [ ] Auto-deploy configured for `stage` and `main` branches
- [ ] Smoke tests passing on staging before first production deploy
- [ ] Branch protection rules set on `main` (#15)
