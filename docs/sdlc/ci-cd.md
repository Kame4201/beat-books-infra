# CI/CD Pipeline

## Pipeline Stages

~~~
Lint (ruff + black) → Type Check (mypy) → Test (pytest + coverage) → Security (bandit + pip-audit)
~~~

## Workflow Templates

Reusable GitHub Actions workflow templates are available in the `ci-templates/` directory:

- `lint.yml` - Code linting with ruff and black
- `test.yml` - Unit tests with pytest and coverage reporting
- `type-check.yml` - Static type checking with mypy
- `security.yml` - Security scanning with bandit and pip-audit
- `full-pipeline.yml` - Combined workflow with proper job dependencies

### How to Use Templates

1. Copy the desired template(s) from `ci-templates/` to your repo's `.github/workflows/` directory
2. Customize as needed for your specific repo (see per-repo guidance below)
3. Commit and push to enable CI for your repo

### Per-Repo Customization

#### beat-books-data
- **Workflows**: Use all templates (lint, test, type-check, security)
- **Customization**: Default configuration should work
- **Coverage**: Ensure `--cov-fail-under=70` in test.yml

#### beat-books-model
- **Workflows**: Use all templates (lint, test, type-check, security)
- **Customization**:
  - Add model artifact caching in test.yml:
    ```yaml
    - name: Cache trained models
      uses: actions/cache@v4
      with:
        path: models/artifacts/
        key: ${{ runner.os }}-models-${{ hashFiles('src/features/**') }}
    ```
- **Coverage**: Ensure `--cov-fail-under=70` in test.yml

#### beat-books-api
- **Workflows**: Use all templates (lint, test, type-check, security)
- **Customization**:
  - Add Docker build step after tests pass:
    ```yaml
    docker-build:
      needs: [test, security]
      steps:
        - name: Build Docker image
          run: docker build -t beat-books-api:${{ github.sha }} .
    ```
- **Coverage**: Adjust to `--cov-fail-under=60` in test.yml

#### beat-books-infra
- **Workflows**: Use markdownlint only (not Python-based templates)
- **Customization**:
  - Create custom workflow for documentation linting:
    ```yaml
    - name: Lint markdown
      run: npx markdownlint-cli docs/
    ```

## Coverage Thresholds

| Repo | Minimum Overall | Critical Paths |
|------|----------------|----------------|
| beat-books-data | 70% | 80% on src/services/ |
| beat-books-model | 70% | 90% on src/features/ |
| beat-books-api | 60% | 80% on src/routes/ |

## Branch Protection Rules

- Require PR reviews before merging (1 reviewer minimum)
- Require status checks to pass: `lint`, `test`
- Require branches to be up to date before merging
