# Pull Request Guide

## PR Title Format

~~~
[type] Short description (#issue-number)
~~~

Examples:
- `[feat] Add odds entity and repository (#1)`
- `[fix] Strip URL hash fragments to prevent 403s (#3)`

## PR Body Template

~~~markdown
## Summary
Brief description of what this PR does and why.

## Changes
- List of files/areas changed

## Testing
- [ ] Unit tests pass
- [ ] New tests added for new code
- [ ] Manual testing done

## Checklist
- [ ] Code follows 3-tier architecture
- [ ] DTOs validate input
- [ ] Alembic migration created (if schema changed)
- [ ] No hardcoded config values

## Related Issues
Closes #issue-number
~~~

## Merge Strategy

Use squash merge to keep `main` history clean.
