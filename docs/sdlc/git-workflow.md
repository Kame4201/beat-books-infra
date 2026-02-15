# Git Workflow

## Branching Strategy

We follow a simplified GitFlow model. All changes go through feature branches and pull requests. Never commit directly to `main`.

## Branch Naming

~~~
feature/short-description    — New functionality
fix/short-description        — Bug fixes
refactor/short-description   — Code restructuring
docs/short-description       — Documentation only
test/short-description       — Test additions
chore/short-description      — Dependencies, CI/CD, tooling
~~~

## Commit Message Format

~~~
type: short description

Longer explanation if needed.

Refs: #issue-number
~~~

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

## Workflow

1. `git checkout main && git pull`
2. `git checkout -b feature/your-feature`
3. Make changes, commit with conventional messages
4. `git push origin feature/your-feature`
5. Create PR on GitHub targeting `main`
6. Get review approval + CI passing
7. Squash merge to `main`
8. Delete feature branch

## Cross-Repo Coordination

When a change requires work in multiple repos, create issues in BOTH repos referencing each other. Complete the dependency first (usually `beat-books-data` schema changes) before building on top in the dependent repo.
