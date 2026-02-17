#!/bin/bash
# Configure branch protection rules for the main branch
# Usage: ./configure-branch-protection.sh [owner/repo]
# Example: ./configure-branch-protection.sh Kame4201/beat-books-infra
#
# Prerequisites:
#   - GitHub CLI (gh) installed and authenticated
#   - Admin access to the target repository
#   - The 'markdown-lint' status check must exist (i.e., a workflow that runs
#     a job named 'markdown-lint' must have run at least once on the repo)

set -e

REPO="${1:-Kame4201/beat-books-infra}"
BRANCH="main"

echo "Configuring branch protection for '${BRANCH}' on '${REPO}'..."
echo ""

# Use the GitHub API via gh to set branch protection rules.
# Rules applied:
#   1. Require at least 1 pull request review before merging
#   2. Require status check 'markdown-lint' to pass before merging
#   3. Require branch to be up to date with main before merging
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["markdown-lint"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false
  },
  "restrictions": null
}
EOF

echo ""
echo "Branch protection rules applied to '${BRANCH}' on '${REPO}':"
echo "  ✓ Require at least 1 pull request review before merging"
echo "  ✓ Require 'markdown-lint' status check to pass"
echo "  ✓ Require branch to be up to date with main (strict: true)"
echo ""
echo "To verify, run:"
echo "  gh api /repos/${REPO}/branches/${BRANCH}/protection"
