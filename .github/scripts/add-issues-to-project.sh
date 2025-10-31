#!/usr/bin/env bash
# Add sprint issues to GitHub Project

set -euo pipefail

PROJECT_NUMBER=2
REPO="thaddiusatme/inneros-zettelkasten"

echo "📝 Adding issues #29-#37 to Project #${PROJECT_NUMBER}..."
echo ""

# Add each issue to the project
for issue_num in 29 30 31 32 33 34 35 36 37; do
  echo "Adding issue #${issue_num}..."
  gh project item-add $PROJECT_NUMBER \
    --owner @me \
    --url "https://github.com/${REPO}/issues/${issue_num}" \
    && echo "  ✅ Added #${issue_num}" \
    || echo "  ❌ Failed #${issue_num}"
done

echo ""
echo "✅ All issues added to project!"
echo "🔗 View project: https://github.com/users/thaddiusatme/projects/2"
echo ""
echo "📋 Next: Configure project columns and statuses"
