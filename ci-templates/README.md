# CI Templates

## Reusable Workflows (Recommended)

The reusable workflow files are in `ci-templates/reusable/`. To activate them, the repo owner must copy them into `.github/workflows/` (pushing to `.github/workflows/` requires the `workflow` OAuth scope).

### Deployment step (one-time, requires repo owner)

```bash
cp ci-templates/reusable/*.yml .github/workflows/
git add .github/workflows/reusable-*.yml
git commit -m "ci: add reusable workflows"
git push
```

### How to call from an app repo

Create a file like `.github/workflows/ci.yml` in your app repo:

```yaml
name: CI

on:
  push:
    branches: [main, Dev]
  pull_request:
    branches: [main, Dev]

jobs:
  ci:
    uses: Kame4201/beat-books-infra/.github/workflows/reusable-full-pipeline.yml@main
    with:
      python-version: "3.11"
      source-dir: "src/"
      coverage-threshold: 70
```

Or call individual workflows:

```yaml
jobs:
  lint:
    uses: Kame4201/beat-books-infra/.github/workflows/reusable-lint.yml@main
    with:
      source-dir: "src/"

  test:
    uses: Kame4201/beat-books-infra/.github/workflows/reusable-test.yml@main
    with:
      coverage-threshold: 80
```

### Available reusable workflows

| Workflow | Inputs | Description |
|----------|--------|-------------|
| `reusable-lint.yml` | `python-version`, `source-dir` | Runs ruff + black |
| `reusable-test.yml` | `python-version`, `source-dir`, `coverage-threshold` | pytest + coverage + Codecov |
| `reusable-type-check.yml` | `python-version`, `source-dir` | mypy type checking |
| `reusable-security.yml` | `python-version`, `source-dir` | bandit + pip-audit |
| `reusable-full-pipeline.yml` | `python-version`, `source-dir`, `coverage-threshold` | All of the above with correct ordering |

### Important notes

- Reference `@main` for latest stable, or pin to a commit SHA for reproducibility.
- The calling repo must be public, or the infra repo must grant workflow access in Settings > Actions > General > Access.

## Legacy Copy-Paste Templates

The `.yml` files in this directory root are the original copy-paste templates. They still work but require manual syncing across repos. Prefer the reusable workflows above.

| Template | Purpose |
|----------|---------|
| `lint.yml` | Ruff + Black |
| `test.yml` | pytest + coverage |
| `type-check.yml` | mypy |
| `security.yml` | bandit + pip-audit |
| `full-pipeline.yml` | All checks combined |
| `claude.yml` | Claude Code agent (copy-paste only — repo-specific) |
| `claude-code-review.yml` | Claude PR review (copy-paste only — repo-specific) |
