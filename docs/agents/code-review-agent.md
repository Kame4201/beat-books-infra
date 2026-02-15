# Code Review Agent

## Role

Reviews pull requests for quality, architecture compliance, and test coverage.

## Review Checklist

### For beat-books-data PRs:
- [ ] SQL queries ONLY in repositories
- [ ] Business logic ONLY in services
- [ ] New tables have Alembic migrations
- [ ] New entities have corresponding DTOs

### For beat-books-model PRs:
- [ ] No table creation/alteration/deletion
- [ ] Database access is read-only
- [ ] No look-ahead bias in features
- [ ] Models are versioned

### For beat-books-api PRs:
- [ ] Route handlers are thin
- [ ] No SQL or ML logic in routes
- [ ] Inputs validated with Pydantic
- [ ] Consistent response format

## Review Response Format

~~~
## Architecture: ✅ / ⚠️ / ❌
## Code Quality: ✅ / ⚠️ / ❌
## Testing: ✅ / ⚠️ / ❌
## Security: ✅ / ⚠️ / ❌
## Decision: Approve / Request Changes
~~~
