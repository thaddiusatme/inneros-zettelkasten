#!/usr/bin/env bash
# Configure sprint project with custom fields

set -euo pipefail

PROJECT_NUMBER=2

echo "⚙️  Configuring Sprint Project..."
echo ""

# List existing fields
echo "📋 Current project fields:"
gh project field-list $PROJECT_NUMBER --owner @me --format json | \
  jq -r '.fields[] | "  - \(.name) (\(.dataType))"'

echo ""
echo "✨ Creating custom fields for sprint tracking..."
echo ""

# Create Priority field (if not exists)
echo "Creating Priority field..."
gh project field-create $PROJECT_NUMBER \
  --owner @me \
  --name "Priority" \
  --data-type "SINGLE_SELECT" \
  --single-select-options '[
    {"name": "P0 - Critical", "color": "RED"},
    {"name": "P1 - High", "color": "ORANGE"},
    {"name": "P2 - Medium", "color": "YELLOW"}
  ]' 2>/dev/null \
  && echo "  ✅ Priority field created" \
  || echo "  ℹ️  Priority field may already exist"

# Create Sprint Day field
echo "Creating Sprint Day field..."
gh project field-create $PROJECT_NUMBER \
  --owner @me \
  --name "Sprint Day" \
  --data-type "SINGLE_SELECT" \
  --single-select-options '[
    {"name": "Day 1-2 (Bug Fixes)", "color": "PINK"},
    {"name": "Day 2-3 (Testing)", "color": "BLUE"},
    {"name": "Day 3 (Health)", "color": "BLUE"},
    {"name": "Day 4-5 (Deploy)", "color": "GREEN"},
    {"name": "Day 5-7 (Monitor)", "color": "PURPLE"},
    {"name": "Day 7 (Retro)", "color": "GRAY"}
  ]' 2>/dev/null \
  && echo "  ✅ Sprint Day field created" \
  || echo "  ℹ️  Sprint Day field may already exist"

# Create Estimated Hours field
echo "Creating Estimated Hours field..."
gh project field-create $PROJECT_NUMBER \
  --owner @me \
  --name "Estimated Hours" \
  --data-type "NUMBER" 2>/dev/null \
  && echo "  ✅ Estimated Hours field created" \
  || echo "  ℹ️  Estimated Hours field may already exist"

echo ""
echo "✅ Project configured!"
echo ""
echo "🔗 View your project: https://github.com/users/thaddiusatme/projects/2"
echo ""
echo "📊 Recommended views to create (via web UI):"
echo "  1. Kanban Board - Group by Status"
echo "  2. Priority View - Group by Priority"
echo "  3. Timeline View - Group by Sprint Day"
echo ""
echo "🚀 Ready to start sprint! First issue: #29"
