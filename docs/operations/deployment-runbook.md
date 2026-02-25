# Deployment Runbook and Hosting Infrastructure Plan

> Defines where and how BeatTheBooks services are deployed to production.
> Related: [Docker Registry Strategy](docker-registry.md) | [Secret Management](secret-management.md) | [Service Contracts](../architecture/service-contracts.md)

## Hosting Platform Evaluation

| Platform | Pros | Cons | Est. Cost |
|----------|------|------|-----------|
| **Railway** | Easy Docker deploy, GitHub integration, auto-deploy | Limited free compute | $5–20/mo |
| **Render** | Free tier, auto-deploy from GitHub | Cold starts on free tier | $0–25/mo |
| **Fly.io** | Edge deployment, good free tier, Docker-native | More CLI config needed | $0–20/mo |
| DigitalOcean App Platform | Predictable pricing | Less flexible | $12–24/mo |
| Self-hosted VPS | Full control | More ops burden | $5–10/mo |

**Recommendation:** Start with **Railway** or **Render** for simplicity. Both support Docker images from GHCR and GitHub-based auto-deploy. Migrate to Fly.io or a VPS if cost or performance requirements change.

> **Decision needed:** Owner should pick a platform and update this section.

## Architecture in Production

```
┌──────────────┐
│   Internet   │
└──────┬───────┘
       │ HTTPS (443)
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ beat-books-  │────▶│ beat-books-  │     │ beat-books-  │
│ api          │     │ data         │     │ model        │
│ (public)     │────▶│ (internal)   │◀────│ (internal)   │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                    │
                            ▼                    ▼
                     ┌─────────────────────────────────┐
                     │  Neon.tech PostgreSQL (managed)  │
                     └─────────────────────────────────┘
```

- Only `beat-books-api` is publicly accessible
- `beat-books-data` and `beat-books-model` are internal services
- Database is managed Neon.tech (not self-hosted)

## Deployment Pipeline (CD)

### Trigger

Merges to `main` branch in any app repo trigger deployment.

### Flow

```
1. PR merged to main
2. GitHub Actions builds Docker image (reusable-docker-build.yml)
3. Image pushed to GHCR with :latest and :main tags
4. Hosting platform pulls new image and restarts service
5. Health check confirms service is running
```

### Rollback

```bash
# Deploy a specific previous image tag
# (platform-specific — example for Railway CLI)
railway deploy --image ghcr.io/kame4201/beat-books-api:<previous-sha>
```

## Environment Variables

Each service requires environment variables. Never hardcode secrets.

### beat-books-data

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |

### beat-books-model

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (read-only user) | `postgresql://readonly:pass@host:5432/db` |

### beat-books-api

| Variable | Description | Example |
|----------|-------------|---------|
| `DATA_SERVICE_URL` | Internal URL of data service | `http://data-service:8001` |
| `MODEL_SERVICE_URL` | Internal URL of model service | `http://model-service:8002` |

See [Secret Management](secret-management.md) for how secrets are stored and rotated.

## Domain and SSL

| Component | Value | Notes |
|-----------|-------|-------|
| Domain | TBD | Purchase via Namecheap, Cloudflare, etc. |
| DNS | TBD | Point to hosting platform |
| SSL | Auto (Let's Encrypt) | Most platforms handle this automatically |

> **Decision needed:** Owner should register a domain and configure DNS.

## Pre-Deployment Checklist

- [ ] Hosting platform chosen and account created
- [ ] Docker images building and pushing to GHCR (#41)
- [ ] Environment variables configured on hosting platform
- [ ] Database connection verified from hosting platform to Neon.tech
- [ ] Domain registered and DNS configured
- [ ] SSL certificate active
- [ ] Health check endpoints responding
- [ ] Smoke tests passing (`scripts/smoke-test.sh`)

## Post-Deployment Verification

```bash
# Check health of all services
curl https://your-domain.com/health

# Run smoke tests against production
bash scripts/smoke-test.sh https://your-domain.com
```

## Incident Response

1. **Service down:** Check hosting platform dashboard for error logs
2. **Bad deploy:** Rollback to previous image SHA (see Rollback section)
3. **Database issue:** See [Database Operations](database-ops.md) (once created)
4. **Rate limited by external API:** See [External APIs](../architecture/external-apis.md) (once created)
