# Shared Types: Cross-Repo Contract Enforcement Proposal

> Proposes how to enforce service contracts in code without putting application code in beat-books-infra.
> Related: [Service Contracts](service-contracts.md) | CLAUDE.md ("NEVER put application code here")

## Problem

Service contracts are defined in `docs/architecture/service-contracts.md` but enforced only by per-repo JSON schema tests (Option C). Each repo independently defines its own Pydantic models for health checks, error responses, and DTOs. When `beat-books-data` changes a response field, `beat-books-api` breaks at runtime with no warning.

## Constraint

`CLAUDE.md` states: **"NEVER put application code here (no Python services, models, etc.)"**. Therefore, we cannot host an installable Python package in this repo.

## Recommended Solution: Contract Stub Templates

### What goes in beat-books-infra

Pydantic model stubs in `templates/contract_stubs/` that app repos **copy** into their codebase. These are templates, not an installable package.

### What goes in app repos

Each app repo vendors (copies) the stubs and imports them. When contracts change, update the stubs in infra first, then copy to app repos.

## Contract Stubs

The following stubs are provided in `templates/contract_stubs/` and align exactly with `docs/architecture/service-contracts.md`:

### `contracts.py`

Defines the shared Pydantic models:
- `HealthResponse` — standard health check response
- `ErrorResponse` — standard error response
- `PaginatedResponse` — standard pagination wrapper

### Usage in app repos

```python
# Copy templates/contract_stubs/contracts.py to your repo, e.g.:
#   cp beat-books-infra/templates/contract_stubs/contracts.py src/contracts.py

from src.contracts import HealthResponse, ErrorResponse

@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="beat-books-data",
        version="0.1.0"
    )
```

## Future: Standalone Package (beat-books-shared)

If the platform grows beyond 3 services or contract drift becomes a real problem, consider creating a `beat-books-shared` repo with:

```
beat-books-shared/
├── pyproject.toml
├── src/
│   └── beat_books_shared/
│       ├── __init__.py
│       ├── health.py
│       ├── errors.py
│       └── pagination.py
└── tests/
```

App repos would then `pip install` it:
```
# requirements.txt
beat-books-shared @ git+https://github.com/Kame4201/beat-books-shared.git@v0.1.0
```

**Not recommended yet** — adds dependency management complexity for 3 services. The copy-paste stubs approach is sufficient for current scale.

## Decision Log

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A: Contract stubs in infra/templates** | No app code in infra, simple copy | Manual sync | **Current choice** |
| B: beat-books-shared repo | Single source of truth, pip install | Extra repo, versioning overhead | Future option |
| C: Status quo (JSON tests only) | Zero effort | Contracts drift, runtime breakage | Not recommended |
