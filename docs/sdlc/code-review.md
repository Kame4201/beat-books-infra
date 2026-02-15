# Code Review Standards

## Review Checklist

### Architecture (Critical)
- [ ] SQL queries ONLY in repositories
- [ ] Business logic ONLY in services
- [ ] Route handlers are thin (delegate to services)
- [ ] DTOs used for all external data validation
- [ ] Database changes use Alembic migrations

### Code Quality
- [ ] Functions have type hints
- [ ] Error handling is explicit (no bare `except:`)
- [ ] No hardcoded values (uses config.py)
- [ ] No commented-out code
- [ ] Descriptive variable names

### Testing
- [ ] Unit tests exist for new code
- [ ] Tests use mocks (no real DB/HTTP)
- [ ] Coverage maintained or improved

### Security
- [ ] No secrets in code
- [ ] SQL injection prevented (parameterized queries via SQLAlchemy)
- [ ] Rate limiting respected

## Common Issues to Flag

1. SQL in services → "Move this query to the repository layer"
2. Missing DTOs → "Add a DTO for input validation"
3. Hardcoded config → "Use settings from config.py"
4. Missing tests → "Add unit tests for this new method"
5. Data leakage → "This feature uses future data — look-ahead bias"
