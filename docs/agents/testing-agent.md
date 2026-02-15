# Testing Agent

## Role

Ensures test quality, coverage, and strategy across all repos.

## Testing Pyramid

- 70% Unit tests — single function, mocked dependencies, fast
- 20% Integration tests — service → repository → test DB
- 10% E2E tests — full API request/response via TestClient

## Test Structure (every repo)

~~~
tests/
├── conftest.py
├── test_unit/
├── test_integration/
├── test_e2e/
└── fixtures/
~~~

## Database Strategy

- Unit tests: SQLite in-memory (per-test isolation)
- Integration tests: SQLite file (cleaned between tests)
- E2E tests: SQLite + FastAPI TestClient
- NEVER connect to production Neon.tech in tests

## Naming Convention

~~~
test_<method>_<scenario>_<expected_result>
~~~

## Coverage Requirements

| Repo | Minimum | Critical Paths |
|------|---------|----------------|
| beat-books-data | 70% | 80% on services |
| beat-books-model | 70% | 90% on features |
| beat-books-api | 60% | 80% on routes |

Run: `pytest --cov=src --cov-report=html --cov-fail-under=70`
