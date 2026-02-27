#!/usr/bin/env bash
# Configure branch protection rules for the main branch.
# Requires: gh CLI authenticated with admin access.
# Usage: bash scripts/setup-branch-protection.sh [REPO]
set -e

REPO="${1:-Kame4201/beat-books-infra}"

echo "Setting branch protection on $REPO main branch..."

gh api "repos/$REPO/branches/main/protection" \
  -X PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["markdown-lint"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF

echo "Branch protection configured:"
echo "  - 1 PR review required"
echo "  - markdown-lint status check required"
echo "  - Branches must be up to date with main"
