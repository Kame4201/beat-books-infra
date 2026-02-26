# Contract Stubs

Pydantic model stubs that enforce the schemas defined in `docs/architecture/service-contracts.md`.

## How to use

Copy `contracts.py` into your app repo:

```bash
cp beat-books-infra/templates/contract_stubs/contracts.py src/contracts.py
```

Then import and use:

```python
from src.contracts import HealthResponse, ErrorResponse

@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="healthy", service="beat-books-data", version="0.1.0")
```

## When to update

When `docs/architecture/service-contracts.md` changes, update `contracts.py` here first, then copy to all app repos.

## Models provided

| Model | Contract Section | Purpose |
|-------|-----------------|---------|
| `HealthResponse` | Standard Health Check | `GET /health` response |
| `ErrorResponse` | Standard Error Response | All error responses |
| `PaginationMeta` | Pagination | Pagination metadata |
| `PaginatedResponse` | Pagination | Paginated list wrapper |
