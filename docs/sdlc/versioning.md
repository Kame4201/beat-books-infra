# Release Versioning and Changelog Strategy

> Defines how versions are assigned, changelogs are generated, and releases are published across all BeatTheBooks repos.
> Related: [Git Workflow](git-workflow.md) | [Docker Registry](../operations/docker-registry.md)

## Versioning Scheme: Semantic Versioning

All repos follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

| Component | When to bump | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking API/contract changes | `1.0.0 → 2.0.0` |
| **MINOR** | New features, backward-compatible | `1.0.0 → 1.1.0` |
| **PATCH** | Bug fixes, documentation | `1.0.0 → 1.0.1` |

### Starting version

All repos start at `0.1.0`. Versions below `1.0.0` indicate pre-release — breaking changes are expected.

### Where the version lives

Each app repo stores its version in `pyproject.toml`:

```toml
[project]
name = "beat-books-data"
version = "0.1.0"
```

The health check endpoint reads this value and returns it:

```json
{"status": "healthy", "service": "beat-books-data", "version": "0.1.0"}
```

## Git Tags

### Tag format

```
v<MAJOR>.<MINOR>.<PATCH>
```

Examples: `v0.1.0`, `v1.0.0`, `v1.2.3`

### How to tag a release

```bash
# After merging to main
git checkout main && git pull
git tag v0.2.0
git push origin v0.2.0
```

### Tag rules

- Tags are only created on `main` branch
- Tags trigger the Docker build workflow (image tagged with `1.2.0`, `1.2`, etc.)
- Never delete or move tags after pushing

## Changelog

### Format

Each repo maintains a `CHANGELOG.md` at the root, following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [Unreleased]

### Added
- New feature description (#issue)

### Fixed
- Bug fix description (#issue)

## [0.1.0] - 2026-02-25

### Added
- Initial release
- Health check endpoint
- Basic data scraping
```

### Categories

| Category | When to use |
|----------|-------------|
| **Added** | New features |
| **Changed** | Changes to existing features |
| **Deprecated** | Features to be removed in future |
| **Removed** | Removed features |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability fixes |

### Workflow

1. During development: add entries under `[Unreleased]`
2. At release time: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`
3. Add a new empty `[Unreleased]` section at the top

## Release Workflow Template

Create `.github/workflows/release.yml` in each app repo (copy-paste template):

```yaml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Extract version from tag
        id: version
        run: echo "version=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          name: "v${{ steps.version.outputs.version }}"
```

## Cross-Repo Version Coordination

Services do not need to share the same version number. Each repo versions independently. However:

- Breaking contract changes (see `service-contracts.md`) require a **MAJOR** bump on all affected services
- The `model_version` field in prediction responses tracks the ML model version separately from the service version

## CHANGELOG.md Template

Copy this to the root of each app repo:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-02-25

### Added
- Initial project setup
```
