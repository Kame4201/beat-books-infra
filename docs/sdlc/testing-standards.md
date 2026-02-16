# Testing Standards

## Overview

This document defines testing standards, coverage requirements, and best practices for all BeatTheBooks repositories. All repos follow the 70/20/10 test pyramid defined by the [Testing Agent](../agents/testing-agent.md).

## Test Pyramid (70/20/10)

```
        ┌─────────────┐
        │  E2E (10%)  │  Full API request/response via TestClient
        ├─────────────┤
        │ Integration │  Service → Repository → Test DB
        │   (20%)     │
        ├─────────────┤
        │    Unit     │  Single function, mocked dependencies, fast
        │   (70%)     │
        └─────────────┘
```

### Unit Tests (70%)

**Purpose:** Test individual functions and methods in isolation.

**Characteristics:**
- Fast execution (< 100ms per test)
- No external dependencies (database, network, filesystem)
- All dependencies mocked using `unittest.mock` or `pytest-mock`
- Each function should have 3+ test cases: happy path, error case, edge case

**Example locations:**
- `beat-books-data/tests/test_unit/test_scrape_service.py`
- `beat-books-model/tests/test_unit/test_kelly.py`
- `beat-books-api/tests/test_unit/test_validation.py`

**See:** [Unit test templates](../../templates/tests/test_unit/)

### Integration Tests (20%)

**Purpose:** Test interactions between multiple components (service + repository + database).

**Characteristics:**
- Medium execution time (100ms - 1s per test)
- Use SQLite test database (file or in-memory)
- Mock external HTTP/API calls
- Test full workflows: input → processing → storage → retrieval

**Example locations:**
- `beat-books-data/tests/test_integration/test_scrape_workflow.py`
- `beat-books-model/tests/test_integration/test_prediction_pipeline.py`

**See:** [Integration test template](../../templates/tests/test_integration/test_scrape_workflow_example.py)

### E2E Tests (10%)

**Purpose:** Test complete user-facing flows through the API.

**Characteristics:**
- Slower execution (1s+ per test)
- Use FastAPI `TestClient`
- Test HTTP request → response cycle
- Validate response shapes, status codes, error handling

**Example locations:**
- `beat-books-api/tests/test_e2e/test_api.py`

**See:** [E2E test template](../../templates/tests/test_e2e/test_api_example.py)

## Coverage Requirements

### Overall Coverage Thresholds

| Repo              | Minimum Coverage | Critical Paths    |
|-------------------|------------------|-------------------|
| beat-books-data   | 70%              | 80% on services/  |
| beat-books-model  | 70%              | 90% on features/  |
| beat-books-api    | 60%              | 80% on routes/    |

### Running Coverage

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Fail build if below threshold
pytest --cov=src --cov-fail-under=70

# Generate XML report for CI/CD
pytest --cov=src --cov-report=xml
```

### What to Exclude from Coverage

- Database migration files (`migrations/`)
- `__init__.py` files (unless they contain logic)
- Debug/repr methods (`__repr__`, `__str__`)
- Abstract methods and protocols
- Script entry points (`if __name__ == "__main__"`)

## Test Structure (Every Repo)

```
tests/
├── conftest.py              # Shared fixtures (copy from templates/)
├── test_unit/               # 70% - Unit tests
│   ├── test_scrape_service.py
│   ├── test_dto_validation.py
│   └── test_kelly.py
├── test_integration/        # 20% - Integration tests
│   ├── test_scrape_workflow.py
│   └── test_prediction_pipeline.py
├── test_e2e/                # 10% - E2E tests
│   └── test_api.py
└── fixtures/                # Test data (JSON, CSV, etc.)
    ├── sample_games.json
    └── sample_odds.csv
```

## Database Strategy

### Unit Tests
- **Use:** SQLite in-memory (`:memory:`)
- **Why:** Maximum isolation, no shared state between tests
- **Setup:** New engine + session per test via fixture

```python
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # Create tables, yield session, cleanup
```

### Integration Tests
- **Use:** SQLite file (`test_integration.db`)
- **Why:** Persistent across test, cleaned between tests
- **Setup:** Created once per test run, cleaned via fixture

### E2E Tests
- **Use:** SQLite + FastAPI TestClient
- **Why:** Full API stack without hitting production Neon.tech

### Production
- **NEVER** connect tests to production Neon.tech database
- **NEVER** use real API keys in test fixtures
- All external APIs must be mocked

## Naming Convention

```
test_<method>_<scenario>_<expected_result>
```

**Examples:**
- `test_scrape_game_data_success()`
- `test_scrape_game_data_403_error_retry()`
- `test_kelly_fraction_negative_edge_zero_bet()`
- `test_post_prediction_missing_required_field()`

## Test Organization

### Use pytest markers

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    pass

@pytest.mark.integration
def test_database_integration():
    pass

@pytest.mark.e2e
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_expensive_operation():
    pass
```

### Run specific test types

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run unit and integration
pytest -m "unit or integration"

# Run all tests in directory
pytest tests/test_unit/
```

## Mock Patterns

### Mock HTTP Requests

```python
from unittest.mock import patch, Mock

@patch("requests.get")
def test_scrape(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>...</html>"
    mock_get.return_value = mock_response

    # Test code here
```

### Mock Database Sessions

```python
@pytest.fixture
def mock_db_session():
    class MockSession:
        def query(self, model):
            return self
        def filter(self, *args):
            return self
        def first(self):
            return None
    return MockSession()
```

### Mock External Services

```python
@pytest.fixture
def mock_prediction_service():
    class MockPredictionService:
        def predict(self, game_id):
            return {"home_win_prob": 0.65}
    return MockPredictionService()
```

## Fixtures

### Shared Fixtures (conftest.py)

Each repo has a `conftest.py` with shared fixtures. Copy from templates:

- **beat-books-data:** [conftest_data.py](../../templates/tests/conftest_data.py)
- **beat-books-model:** [conftest_model.py](../../templates/tests/conftest_model.py)
- **beat-books-api:** [conftest_api.py](../../templates/tests/conftest_api.py)

### Fixture Scopes

- `scope="function"` (default) - New fixture per test (use for DB sessions)
- `scope="module"` - One fixture per test file
- `scope="session"` - One fixture per test run

## Pytest Configuration

Copy pytest configuration from [pyproject_testing.toml](../../templates/pyproject_testing.toml) into your repo's `pyproject.toml`.

**Key settings:**
- Test discovery paths
- Coverage thresholds (adjust per repo)
- Markers for test types
- Warning filters

## CI/CD Integration

### GitHub Actions Workflow

```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-report=xml --cov-fail-under=70

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      language: system
      pass_filenames: false
      always_run: true
      args: ["-m", "not slow"]  # Skip slow tests in pre-commit
```

## Common Test Scenarios

### Valid Input (Happy Path)

```python
def test_valid_input_success():
    result = function(valid_input)
    assert result == expected_output
```

### Invalid Input (Error Case)

```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError, match="error message"):
        function(invalid_input)
```

### Edge Cases

```python
def test_edge_case_empty_list():
    result = function([])
    assert result == []

def test_edge_case_negative_value():
    result = function(-1)
    assert result == 0
```

### Parametrized Tests (Multiple Inputs)

```python
@pytest.mark.parametrize("input,expected", [
    (0.55, 0.10),
    (0.60, 0.20),
    (0.45, 0.00),
])
def test_kelly_multiple_scenarios(input, expected):
    result = calculate_kelly(input)
    assert result == pytest.approx(expected, rel=0.01)
```

## Best Practices

### Do's ✓

- Write tests BEFORE or alongside code (TDD when possible)
- Each test should test ONE thing
- Use descriptive test names that explain the scenario
- Mock all external dependencies (HTTP, DB, filesystem)
- Use `pytest.approx()` for floating-point comparisons
- Clean up test databases/files after tests
- Keep tests fast (< 100ms for unit tests)

### Don'ts ✗

- DON'T test framework code (FastAPI, SQLAlchemy internals)
- DON'T connect to production databases or APIs
- DON'T use real API keys or secrets in tests
- DON'T share state between tests (use fixtures)
- DON'T write brittle tests (too tightly coupled to implementation)
- DON'T skip writing tests for "simple" code
- DON'T commit commented-out tests (`# def test_...`)

## Debugging Failed Tests

```bash
# Run with verbose output and print statements
pytest -vv -s tests/test_unit/test_example.py

# Run single test function
pytest tests/test_unit/test_example.py::test_function_name

# Drop into debugger on failure
pytest --pdb

# Show local variables in traceback
pytest --showlocals
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing guide](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker)

## Template Files

All test templates are in `templates/tests/`:

- **Conftest fixtures:**
  - [conftest_data.py](../../templates/tests/conftest_data.py)
  - [conftest_model.py](../../templates/tests/conftest_model.py)
  - [conftest_api.py](../../templates/tests/conftest_api.py)

- **Unit test examples:**
  - [test_scrape_service_example.py](../../templates/tests/test_unit/test_scrape_service_example.py)
  - [test_dto_validation_example.py](../../templates/tests/test_unit/test_dto_validation_example.py)
  - [test_kelly_example.py](../../templates/tests/test_unit/test_kelly_example.py)

- **Integration test example:**
  - [test_scrape_workflow_example.py](../../templates/tests/test_integration/test_scrape_workflow_example.py)

- **E2E test example:**
  - [test_api_example.py](../../templates/tests/test_e2e/test_api_example.py)

- **Pytest configuration:**
  - [pyproject_testing.toml](../../templates/pyproject_testing.toml)

---

**Related:**
- [Testing Agent](../agents/testing-agent.md)
- [SDLC Overview](./sdlc-overview.md)
