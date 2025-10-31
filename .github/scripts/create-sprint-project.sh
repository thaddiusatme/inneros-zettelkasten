#!/usr/bin/env bash
# Create GitHub Project for Automation Revival Sprint

set -euo pipefail

echo "🎯 Creating GitHub Project: Automation Revival Sprint"
echo ""

# Note: gh project create requires specific format
# Using user-scoped project (not repo-scoped) for better flexibility

# Create project
echo "Creating project..."
PROJECT_URL=$(gh project create \
  --title "Automation Revival Sprint" \
  --owner "@me" \
  2>&1 | grep -o 'https://[^"]*' || echo "")

if [ -z "$PROJECT_URL" ]; then
  echo "❌ Failed to create project"
  echo "Please create manually via web UI: https://github.com/users/thaddiusatme/projects/new"
  exit 1
fi

echo "✅ Project created: $PROJECT_URL"
echo ""

# Add issues to project (requires project number)
echo "📝 Adding issues to project..."
echo "Note: You'll need to add issues manually via web UI"
echo ""
echo "To add issues:"
echo "  1. Go to: $PROJECT_URL"
echo "  2. Click '+ Add item'"
echo "  3. Search for issues with label: sprint:automation-revival"
echo "  4. Add all 9 issues (#29-#37)"
echo ""

# Suggested columns setup
echo "📋 Recommended columns:"
echo "  • Backlog (for P1 nice-to-haves)"
echo "  • To Do (ready to start)"
echo "  • In Progress (actively working)"
echo "  • Blocked (waiting on something)"
echo "  • Done (completed)"
echo ""

echo "✅ Next: Open project and configure columns!"
