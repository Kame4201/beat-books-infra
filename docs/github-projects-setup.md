# GitHub Projects Board Setup Guide

## Overview
This guide walks through setting up the "BeatTheBooks Roadmap" GitHub Projects board to track all issues across the 4 repositories.

## Step-by-Step Instructions

### 1. Create the Project

1. Navigate to https://github.com/Kame4201?tab=projects (for user-level project)
   - Or use your organization URL if you want an org-level project
2. Click **"New project"**
3. Choose **"Board"** template
4. Name it: **"BeatTheBooks Roadmap"**
5. Click **"Create project"**

### 2. Configure Columns

The default board comes with "Todo", "In Progress", and "Done" columns. You'll need to customize these:

1. Click the **"..."** menu on each default column and rename/delete as needed
2. Add the following columns (in order):
   - **Backlog** - Issues that are planned but not yet started
   - **Phase 1: Foundation** - Alembic migrations, DTOs, data retrieval API, test infrastructure
   - **Phase 2: Model** - Odds data, feature engineering, baseline ML model, backtesting
   - **Phase 3: Production** - Scraper resilience, Kelly Criterion, CI/CD, config management
   - **Phase 4: Scale** - Injury/weather data, batch scraping, Docker deployment
   - **In Progress** - Currently being worked on
   - **Done** - Completed issues

### 3. Add Custom Fields

1. Click **"+ New field"** in the project settings
2. Create a **"Repo"** field:
   - Field name: `Repo`
   - Field type: `Single select`
   - Options:
     - `beat-books-infra`
     - `beat-books-data`
     - `beat-books-model`
     - `beat-books-api`
3. Save the field

### 4. Add Issues to the Board

For each repository, add all issues:

1. Click **"+ Add item"** at the bottom of any column
2. Search for issues by repository:
   - `repo:Kame4201/beat-books-infra`
   - `repo:Kame4201/beat-books-data`
   - `repo:Kame4201/beat-books-model`
   - `repo:Kame4201/beat-books-api`
3. Add all open issues from each repo

**Note:** As of setup, there should be approximately 22 issues total across all repositories.

### 5. Organize Issues by Phase

For each issue on the board:

1. Review the issue's `phase:X-name` label
2. Drag the issue to the corresponding phase column:
   - `phase:1-foundation` → **Phase 1: Foundation** column
   - `phase:2-model` → **Phase 2: Model** column
   - `phase:3-production` → **Phase 3: Production** column
   - `phase:4-scale` → **Phase 4: Scale** column
   - Issues without a phase label → **Backlog** column

3. Set the **Repo** custom field for each issue to match its source repository

### 6. Set Up Views and Filters

Create useful views for different perspectives:

1. **Default Board View** - Shows all issues organized by phase
2. **By Repository View**:
   - Click **"View 1"** dropdown → **"New view"**
   - Name it "By Repository"
   - Group by: `Repo` field
3. **Current Sprint View**:
   - Filter by `Status: In Progress`
   - Shows only actively worked issues

### 7. Document the Board Link

Once created, add the project board URL to the beat-books-infra README.md:

1. Copy your project board URL (should be something like `https://github.com/users/Kame4201/projects/1`)
2. Update the README.md with the link (see the Project Management section)

## Maintenance

- Move issues to "In Progress" when work begins
- Move to "Done" when PRs are merged
- Add new issues to the board as they're created
- Update the Repo field for all new issues
- Regularly review and organize the Backlog

## Quick Links

- Project Board: [Add your project URL here after creation]
- [beat-books-infra](https://github.com/Kame4201/beat-books-infra)
- [beat-books-data](https://github.com/Kame4201/beat-books-data)
- [beat-books-model](https://github.com/Kame4201/beat-books-model)
- [beat-books-api](https://github.com/Kame4201/beat-books-api)
