#!/bin/bash
# Script to create consistent GitHub labels across all BeatTheBooks repos
# Usage: ./create-labels.sh <owner/repo>
# Example: ./create-labels.sh Kame4201/beat-books-infra

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <owner/repo>"
    echo "Example: $0 Kame4201/beat-books-infra"
    exit 1
fi

REPO=$1

echo "Creating labels for repository: $REPO"

# Function to create or update a label
create_label() {
    local name=$1
    local color=$2
    local description=$3

    # Remove '#' from color if present
    color=${color#\#}

    # Try to create the label, if it exists, update it
    if gh label create "$name" --color "$color" --description "$description" --repo "$REPO" 2>/dev/null; then
        echo "✓ Created label: $name"
    else
        # Label exists, try to update it
        if gh label edit "$name" --color "$color" --description "$description" --repo "$REPO" 2>/dev/null; then
            echo "✓ Updated label: $name"
        else
            echo "⚠ Could not create or update label: $name"
        fi
    fi
}

echo ""
echo "Creating Phase labels..."
create_label "phase:1-foundation" "0E8A16" "Phase 1: Foundation - Initial setup and infrastructure"
create_label "phase:2-model" "1D76DB" "Phase 2: Model - Machine learning model development"
create_label "phase:3-production" "D93F0B" "Phase 3: Production - Production deployment and monitoring"
create_label "phase:4-scale" "5319E7" "Phase 4: Scale - Scaling and optimization"

echo ""
echo "Creating Priority labels..."
create_label "priority:high" "B60205" "High priority issue"
create_label "priority:medium" "FBCA04" "Medium priority issue"
create_label "priority:low" "0E8A16" "Low priority issue"

echo ""
echo "Creating Type labels..."
create_label "database" "D4C5F9" "Database related"
create_label "data-ingestion" "C5DEF5" "Data ingestion pipeline"
create_label "data-science" "BFD4F2" "Data science and analytics"
create_label "api" "F9D0C4" "API related"
create_label "testing" "FEF2C0" "Testing and QA"
create_label "devops" "E6E6E6" "DevOps and infrastructure"
create_label "documentation" "0075CA" "Documentation"
create_label "bugfix" "D73A4A" "Bug fix"
create_label "enhancement" "A2EEEF" "New feature or enhancement"
create_label "architecture" "7057FF" "Architecture decisions"
create_label "code-quality" "BFDADC" "Code quality improvements"
create_label "betting-strategy" "006B75" "Betting strategy related"
create_label "blocking" "B60205" "Blocking other work"
create_label "standards" "C2E0C6" "Standards and conventions"
create_label "project-management" "D4C5F9" "Project management"

echo ""
echo "✓ Label creation complete for $REPO"
