# Database Backup, Recovery, and Migration Coordination

> Defines backup strategy, recovery procedures, and migration coordination for the BeatTheBooks PostgreSQL database.
> Related: [Database Schema](../architecture/database-schema.md) | [Secret Management](secret-management.md)

## Database Overview

| Property | Value |
|----------|-------|
| Provider | Neon.tech (managed PostgreSQL) |
| Engine | PostgreSQL 16 |
| Schema owner | beat-books-data (via Alembic) |
| Read-only access | beat-books-model |
| No access | beat-books-api (proxies through data service) |

## Backup Strategy

### Tier 1: Neon.tech Built-in (Automatic)

Neon.tech provides:

| Feature | Details |
|---------|---------|
| Point-in-time recovery (PITR) | Restore to any point within the retention window |
| Retention | 7 days (Free), 30 days (Pro) |
| Branching | Create instant copy-on-write database branches |

**No configuration needed** — this is enabled by default on Neon.tech.

### Tier 2: Manual `pg_dump` (Scheduled)

For additional safety, run periodic `pg_dump` backups to a separate location.

#### How to run manually

```bash
# Set connection string (never hardcode in scripts)
export DATABASE_URL="postgresql://user:password@host:5432/beatthebooks"

# Full dump (compressed)
pg_dump "$DATABASE_URL" --format=custom --file="backup_$(date +%Y%m%d_%H%M%S).dump"

# Schema only (useful for audit)
pg_dump "$DATABASE_URL" --schema-only --file="schema_$(date +%Y%m%d).sql"
```

#### Recommended schedule

| Trigger | What | Where to store |
|---------|------|----------------|
| Weekly (automated) | Full `pg_dump` | Cloud storage (S3, GCS, or equivalent) |
| Before any migration | Full `pg_dump` | Local + cloud storage |
| After major data scrape | Full `pg_dump` | Cloud storage |

### Tier 3: Neon.tech Branching (Pre-Migration Safety Net)

Before running any migration:

```bash
# Create a branch (instant, zero-cost until it diverges)
# Use the Neon.tech dashboard or CLI:
neonctl branches create --name pre-migration-$(date +%Y%m%d)
```

This creates a point-in-time copy of the entire database. If the migration fails, switch the app to the branch endpoint.

## Recovery Procedures

### Scenario 1: Accidental data deletion

1. **Neon.tech PITR:** Restore to a point before the deletion
   - Go to Neon.tech dashboard → Project → Settings → Point-in-time recovery
   - Select timestamp just before the incident
   - Create a new branch at that timestamp
   - Verify data is intact
   - Update `DATABASE_URL` to point to the restored branch
2. **From pg_dump:** If PITR window has passed
   ```bash
   pg_restore --dbname="$DATABASE_URL" --clean --if-exists backup_YYYYMMDD.dump
   ```

### Scenario 2: Bad migration (schema change broke something)

1. Stop all services: `docker compose down`
2. Revert the migration in beat-books-data:
   ```bash
   cd beat-books-data
   alembic downgrade -1
   ```
3. If downgrade fails, restore from Neon.tech branch:
   - Switch `DATABASE_URL` to the pre-migration branch
   - Redeploy services
4. Fix the migration, test locally, then re-apply

### Scenario 3: Complete database loss

1. Create a new Neon.tech project
2. Run all Alembic migrations from beat-books-data:
   ```bash
   cd beat-books-data
   alembic upgrade head
   ```
3. Restore data from latest pg_dump:
   ```bash
   pg_restore --dbname="$NEW_DATABASE_URL" --data-only backup_latest.dump
   ```
4. Update `DATABASE_URL` in all services
5. Re-scrape any data newer than the backup

### Who has access to perform recovery

| Action | Who | How |
|--------|-----|-----|
| Neon.tech dashboard | Repo owner | Neon.tech account login |
| pg_dump / pg_restore | Repo owner | `DATABASE_URL` credentials |
| Alembic migrations | Anyone with beat-books-data repo | Local dev environment |

## Migration Coordination

### The Problem

`beat-books-data` owns the schema. When it changes a table, `beat-books-model` (which reads that table) may break. There's no compile-time check for this.

### Migration Workflow

```
1. beat-books-data creates Alembic migration
2. Developer reviews: does this change affect tables read by beat-books-model?
   ├── NO  → Proceed normally
   └── YES → Coordinate:
       a. Create matching issue in beat-books-model
       b. Update service-contracts.md in beat-books-infra
       c. Deploy beat-books-data migration FIRST
       d. Deploy beat-books-model update SECOND
       e. Run smoke tests (scripts/smoke-test.sh)
```

### Tables shared across services

| Table | Owner (R/W) | Reader (R/O) | Breaking change risk |
|-------|-------------|-------------|---------------------|
| `team_offense` | beat-books-data | beat-books-model | High — feature engineering reads this |
| `team_defense` | beat-books-data | beat-books-model | High |
| `games` | beat-books-data | beat-books-model | High |
| `standings` | beat-books-data | beat-books-model | Medium |
| `odds` | beat-books-data | beat-books-model | Medium (planned) |

### Safe migration patterns

| Change | Risk | Approach |
|--------|------|----------|
| Add column | Low | No coordination needed (readers ignore new columns) |
| Rename column | **High** | Coordinate — add new column, migrate data, update readers, drop old |
| Drop column | **High** | Verify no reader uses it, then drop |
| Change type | Medium | Test that readers handle the new type |
| Add table | None | No coordination needed |
| Drop table | **High** | Verify no reader uses it |

## Checklist

- [ ] Neon.tech PITR is active (check dashboard)
- [ ] pg_dump script scheduled (weekly at minimum)
- [ ] Backup storage location configured
- [ ] Recovery procedures tested at least once
- [ ] Migration coordination process documented and followed
