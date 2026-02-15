# CI/CD Pipeline

## Pipeline Stages

~~~
Lint (ruff + black) → Type Check (mypy) → Test (pytest + coverage) → Security (bandit + pip-audit)
~~~

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
