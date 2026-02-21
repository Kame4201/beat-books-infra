# Secret Management Strategy

> Defines how secrets are stored, accessed, and validated across all BeatTheBooks repos.
> Referenced by: [Code Review Standards](../sdlc/code-review.md)
> Related issue: beat-books-data#32 (hardcoded credentials in `database.py`)

## Secret Inventory

| Variable | Required | Used By | Description |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | beat-books-data, beat-books-api | Neon.tech PostgreSQL connection string |
| `ODDS_API_KEY` | No (unless odds enabled) | beat-books-data | The Odds API key for live odds ingestion |
| `MODEL_SERVICE_URL` | **Yes** (api) | beat-books-api | URL to the prediction service (e.g. `http://localhost:8002`) |
| `DATA_SERVICE_URL` | **Yes** (api) | beat-books-api | URL to the data service (e.g. `http://localhost:8001`) |
| `DEBUG` | No | all repos | Enable debug mode (`true`/`false`, default `false`) |
| `ENV` | No | all repos | Environment name: `local`, `dev`, `stage`, `prod` (default `local`) |

Add new secrets to this table when introduced.

## Environments

### Local Development

Secrets live in `.env` files at the repo root, **never committed to git**.

1. Copy the template: `cp templates/.env.example .env`
2. Fill in real values
3. Verify `.env` is in `.gitignore` (all repos must have this)

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/beatbooks
ODDS_API_KEY=abc123
MODEL_SERVICE_URL=http://localhost:8002
DATA_SERVICE_URL=http://localhost:8001
DEBUG=true
ENV=local
```

### CI/CD (GitHub Actions)

Secrets are stored as **GitHub Actions repository secrets** and injected as environment variables.

**Setup per repo:**
1. Go to repo → Settings → Secrets and variables → Actions
2. Add each secret from the inventory table above
3. Reference in workflows:

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  ODDS_API_KEY: ${{ secrets.ODDS_API_KEY }}
  MODEL_SERVICE_URL: ${{ vars.MODEL_SERVICE_URL }}
  DATA_SERVICE_URL: ${{ vars.DATA_SERVICE_URL }}
  ENV: ${{ vars.ENV }}
```

**Rules:**
- Never echo or log secret values in CI
- Use `environment` scopes if you need separate staging/production secrets
- Mask secrets in output with `::add-mask::` if dynamically generated

### Production

Secrets are set as **environment variables on the hosting platform**. No secrets in code, config files, or Docker images.

| Platform | How to set |
|---|---|
| **Neon.tech** | Connection string available in the Neon dashboard → Connection Details |
| **Railway** | Variables tab in the service settings |
| **Render** | Environment section in the service dashboard |

For Docker deployments, pass secrets at runtime:

```bash
docker run --env-file .env myimage
```

Never bake secrets into a Docker image via `ENV` or `COPY .env`.

## Pydantic Settings Pattern

All repos must use `pydantic-settings` to load and validate configuration. This ensures the app **fails fast** with a clear error if a required secret is missing.

### Installation

```bash
pip install pydantic-settings
```

### Basic Usage

```python
# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str                   # Required — app won't start without it
    odds_api_key: str = ""              # Optional — only needed for odds features
    model_service_url: str = ""         # Required for beat-books-api
    data_service_url: str = ""          # Required for beat-books-api
    debug: bool = False                 # Optional — defaults to False
    env: str = "local"                  # Optional — local/dev/stage/prod

    model_config = {"env_file": ".env"}
```

### Loading Settings

```python
# Usage anywhere in the app
from config import Settings

settings = Settings()
print(settings.database_url)  # Loaded from env or .env file
```

### Validation Behavior

**Missing required field** — app crashes immediately with a clear message:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
database_url
  Field required [type=missing, input_value={}, input_type=dict]
```

**Invalid type** — caught at startup, not at runtime:

```python
class Settings(BaseSettings):
    debug: bool = False  # Accepts: true/false, 1/0, yes/no

# DEBUG=notabool → ValidationError
```

**Constrained values** — use validators for stricter rules:

```python
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "local"

    @field_validator("env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"local", "dev", "stage", "prod"}
        if v.lower() not in allowed:
            raise ValueError(f"env must be one of {allowed}")
        return v.lower()
```

### Per-Repo Overrides

Each repo extends the base pattern with its own fields:

```python
# beat-books-data/src/config.py
class Settings(BaseSettings):
    database_url: str
    odds_api_key: str = ""
    debug: bool = False
    env: str = "local"

# beat-books-model/src/config.py
class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    env: str = "local"

# beat-books-api/src/config.py
class Settings(BaseSettings):
    database_url: str
    model_service_url: str              # Required — calls prediction service
    data_service_url: str               # Required — calls data service
    debug: bool = False
    env: str = "local"
```

## Checklist for Adding a New Secret

1. Add the variable to the **Secret Inventory** table above
2. Add it to `templates/.env.example` with a descriptive comment
3. Add it to the relevant repo's `Settings` class in `config.py`
4. Add it to GitHub Actions secrets for the repo
5. Add it to the production hosting platform
6. Update any Docker Compose files to pass it through
