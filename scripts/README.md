# Scripts

## create-labels.sh

Creates consistent GitHub labels across all BeatTheBooks repositories.

### Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Write access to the target repository

### Usage

```bash
# Make script executable
chmod +x scripts/create-labels.sh

# Run for a specific repository
./scripts/create-labels.sh <owner/repo>
```

### Examples

```bash
# Create labels in beat-books-infra
./scripts/create-labels.sh Kame4201/beat-books-infra

# Create labels in beat-books-data
./scripts/create-labels.sh Kame4201/beat-books-data

# Create labels in beat-books-model
./scripts/create-labels.sh Kame4201/beat-books-model

# Create labels in beat-books-api
./scripts/create-labels.sh Kame4201/beat-books-api
```

### What it creates

The script creates 22 labels in three categories:

**Phase labels (4):**
- `phase:1-foundation` - Phase 1: Foundation
- `phase:2-model` - Phase 2: Model
- `phase:3-production` - Phase 3: Production
- `phase:4-scale` - Phase 4: Scale

**Priority labels (3):**
- `priority:high` - High priority
- `priority:medium` - Medium priority
- `priority:low` - Low priority

**Type labels (15):**
- `database`, `data-ingestion`, `data-science`, `api`, `testing`, `devops`, `documentation`, `bugfix`, `enhancement`, `architecture`, `code-quality`, `betting-strategy`, `blocking`, `standards`, `project-management`

### Notes

- If a label already exists, the script will update it with the correct color
- The script uses the GitHub CLI (`gh label create` and `gh label edit`)
- All label colors match the specifications in issue #4
