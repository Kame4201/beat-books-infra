# Docker Image Build, Tagging, and Registry Strategy

> Defines how Docker images are built, tagged, stored, and scanned for the BeatTheBooks platform.
> Related: [Deployment Runbook](deployment-runbook.md) | [Service Contracts](../architecture/service-contracts.md)

## Registry: GitHub Container Registry (GHCR)

We use **GHCR** (`ghcr.io`) because:
- Free for public repos
- Integrated with GitHub Actions (no extra credentials)
- Supports OCI images
- Per-repo access control via GitHub permissions

### Image naming convention

```
ghcr.io/kame4201/<service-name>:<tag>
```

| Service | Image |
|---------|-------|
| beat-books-data | `ghcr.io/kame4201/beat-books-data` |
| beat-books-model | `ghcr.io/kame4201/beat-books-model` |
| beat-books-api | `ghcr.io/kame4201/beat-books-api` |

## Tagging Strategy

Every image push produces multiple tags:

| Tag | Example | When |
|-----|---------|------|
| Short SHA | `abc1234` | Every build |
| Branch name | `main`, `Dev` | Every build |
| `latest` | `latest` | Merges to `main` only |
| SemVer | `1.2.0`, `1.2` | When a `v*` tag is pushed |

### Tag lifecycle

```
feature branch merge → Dev
  → ghcr.io/kame4201/beat-books-data:Dev
  → ghcr.io/kame4201/beat-books-data:<sha>

promotion to main
  → ghcr.io/kame4201/beat-books-data:main
  → ghcr.io/kame4201/beat-books-data:latest
  → ghcr.io/kame4201/beat-books-data:<sha>

release tag (v1.0.0)
  → ghcr.io/kame4201/beat-books-data:1.0.0
  → ghcr.io/kame4201/beat-books-data:1.0
  → ghcr.io/kame4201/beat-books-data:<sha>
```

## CI Workflow

Use the reusable workflow `ci-templates/reusable/reusable-docker-build.yml`.

### Caller example (in each app repo)

```yaml
name: Docker Build

on:
  push:
    branches: [main, Dev]
    tags: ["v*"]

jobs:
  build:
    uses: Kame4201/beat-books-infra/.github/workflows/reusable-docker-build.yml@main
    with:
      image-name: beat-books-data  # change per repo
    permissions:
      contents: read
      packages: write
```

## Multi-Stage Build Recommendations

Each app repo should use multi-stage Dockerfiles to keep production images slim:

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ src/
EXPOSE 8001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Security Scanning

The reusable workflow includes **Trivy** vulnerability scanning on every push. It scans for CRITICAL and HIGH severity CVEs. Currently set to non-blocking (`exit-code: 0`) — switch to `exit-code: 1` to enforce.

## Setup Checklist

- [ ] Each app repo has a multi-stage `Dockerfile`
- [ ] Each app repo calls the reusable docker-build workflow
- [ ] GHCR packages are linked to the repos (happens automatically on first push)
- [ ] Reusable workflow is copied to `.github/workflows/` in infra repo (requires `workflow` OAuth scope)
