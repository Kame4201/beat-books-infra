# Development Agent

## Role

Implements features, fixes bugs, and writes code following the project's architecture and standards.

## Workflow

1. Read the GitHub issue and repo's CLAUDE.md
2. Plan: identify which layers are affected (entity, DTO, repository, service, route)
3. Implement following 3-tier architecture strictly
4. Write unit tests (mock all external dependencies)
5. Submit PR with description and checklist

## Adding a New Data Source (e.g., odds)

1. Create Alembic migration for new table (beat-books-data)
2. Create entity in `src/entities/` (beat-books-data)
3. Create DTOs in `src/dtos/` (beat-books-data)
4. Create repository in `src/repositories/` (beat-books-data)
5. Create service in `src/services/` (beat-books-data)
6. Add endpoint in route handler (beat-books-api)
7. Write unit tests for each layer

## Common Mistakes to Avoid

1. Putting SQL in a service instead of a repository
2. Skipping DTO validation
3. Hardcoding configuration values
4. Writing tests that hit the production database
5. Using random train/test splits instead of walk-forward
6. Creating database tables in beat-books-model (read-only!)
