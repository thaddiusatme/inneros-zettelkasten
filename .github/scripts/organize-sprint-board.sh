#!/usr/bin/env bash
# Organize sprint board - set all items to Todo status

set -euo pipefail

PROJECT_NUMBER=2
STATUS_FIELD_ID="PVTSSF_lAHOCbOJic4BG4bYzg3zJag"
TODO_OPTION_ID="f75ad846"

echo "📋 Organizing Sprint Board..."
echo ""

# Get all project items and their IDs
echo "Getting project items..."
ITEMS=$(gh project item-list $PROJECT_NUMBER --owner @me --format json --limit 100)

# Extract item IDs
ITEM_IDS=$(echo "$ITEMS" | jq -r '.items[].id')

echo "Found $(echo "$ITEM_IDS" | wc -l | tr -d ' ') items"
echo ""

# Set each item to "Todo" status
echo "Setting all items to 'Todo' status..."
for item_id in $ITEM_IDS; do
  ISSUE_NUM=$(echo "$ITEMS" | jq -r ".items[] | select(.id == \"$item_id\") | .content.number")
  echo "  Issue #${ISSUE_NUM} → Todo"
  
  gh project item-edit \
    --project-id "PVT_kwHOCbOJic4BG4bY" \
    --id "$item_id" \
    --field-id "$STATUS_FIELD_ID" \
    --single-select-option-id "$TODO_OPTION_ID" \
    2>/dev/null \
    && echo "    ✅ Set" \
    || echo "    ⚠️  Already set or failed"
done

echo ""
echo "✅ Board organized!"
echo ""
echo "📊 Current sprint organization (by existing labels):"
echo ""
echo "🔴 P0 - Critical (Must Do This Week):"
echo "  #29 Fix YouTube Rate Limiting (bug-fix, 2h)"
echo "  #30 Fix File Watching Loop Bug (bug-fix, 2h)"
echo "  #31 Test Screenshot Import (testing, 2h)"
echo "  #32 Test Inbox Processing (testing, 2h)"
echo "  #34 Staged Cron Re-enablement (deployment, 2h)"
echo "  #36 48-Hour Stability Monitoring (monitoring, 4h)"
echo ""
echo "🟠 P1 - High Priority (Nice to Have):"
echo "  #33 Test Health Monitor (testing, 1h)"
echo "  #35 Automation Visibility (monitoring, 3h)"
echo "  #37 Sprint Retrospective (documentation, 2h)"
echo ""
echo "🔗 View project: https://github.com/users/thaddiusatme/projects/2"
echo ""
echo "💡 In the web UI:"
echo "  • Click 'View' dropdown → Group by 'Labels' to see priorities"
echo "  • Click 'View' dropdown → Group by 'Status' for kanban board"
echo "  • Drag items between Todo → In Progress → Done as you work"
