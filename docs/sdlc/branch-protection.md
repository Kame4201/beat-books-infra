# Branch Protection Rules

Branch protection is configured on the `main` branch of each BeatTheBooks repository to enforce code quality standards before merging.

## Rules Applied to `main`

| Rule | Setting |
|------|---------|
| Required PR reviews | At least **1 approving review** before merging |
| Required status checks | `markdown-lint` must pass |
| Up-to-date requirement | Branch must be **up to date** with `main` before merging |
| Admin enforcement | Not enforced (admins may bypass in emergencies) |

## Prerequisites

Before running the configuration script, ensure the following are in place:

### 1. `markdown-lint` CI Workflow

The `markdown-lint` status check must exist as a GitHub Actions job. Add a workflow to `.github/workflows/markdown-lint.yml`:

```yaml
name: Markdown Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  markdown-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run markdownlint
        uses: DavidAnson/markdownlint-cli2-action@v16
        with:
          globs: "**/*.md"
```

> **Note:** The status check name in branch protection must exactly match the GitHub Actions **job name** (`markdown-lint`). The workflow must have run at least once before the API will accept it as a required status check.

### 2. GitHub CLI Authentication

Install and authenticate the GitHub CLI:

```bash
gh auth login
```

### 3. Admin Access

You must have admin access to the repository to modify branch protection rules.

## Applying the Rules

Use the provided script:

```bash
# Make executable
chmod +x scripts/configure-branch-protection.sh

# Run for this repo
./scripts/configure-branch-protection.sh Kame4201/beat-books-infra

# Or for other repos
./scripts/configure-branch-protection.sh Kame4201/beat-books-data
./scripts/configure-branch-protection.sh Kame4201/beat-books-model
./scripts/configure-branch-protection.sh Kame4201/beat-books-api
```

## Manual Steps (GitHub UI)

Alternatively, configure via the GitHub web UI:

1. Go to **Settings** → **Branches** in the repository
2. Click **Add branch ruleset** (or **Add branch protection rule**)
3. Set **Branch name pattern** to `main`
4. Enable **Require a pull request before merging**
   - Set **Required approvals** to `1`
5. Enable **Require status checks to pass before merging**
   - Enable **Require branches to be up to date before merging**
   - Search for and add `markdown-lint` to the required checks
6. Click **Create** (or **Save changes**)

## Verifying the Configuration

```bash
gh api /repos/Kame4201/beat-books-infra/branches/main/protection
```

## Related

- [Git Workflow](git-workflow.md)
- [CI/CD](ci-cd.md)
- [Pull Request Guide](pull-request-guide.md)
