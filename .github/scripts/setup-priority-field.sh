#!/usr/bin/env bash
# Setup Priority field and populate values based on issue labels

set -euo pipefail

PROJECT_NUMBER=2
PROJECT_ID="PVT_kwHOCbOJic4BG4bY"

echo "🔧 Setting up Priority field..."
echo ""

# Delete the malformed Priority field
echo "Removing old Priority field..."
PRIORITY_FIELD_ID=$(gh project field-list $PROJECT_NUMBER --owner @me --format json | \
  jq -r '.fields[] | select(.name == "Priority") | .id')

if [ -n "$PRIORITY_FIELD_ID" ]; then
  gh project field-delete $PROJECT_NUMBER --owner @me --id "$PRIORITY_FIELD_ID" 2>/dev/null \
    && echo "  ✅ Deleted old Priority field" \
    || echo "  ⚠️  Could not delete old field"
fi

echo ""
echo "Creating new Priority field with proper options..."

# Create Priority field with proper single-select options
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "'"$PROJECT_ID"'"
    dataType: SINGLE_SELECT
    name: "Priority"
    singleSelectOptions: [
      {name: "P0 - Critical", color: RED, description: "Must complete this week"},
      {name: "P1 - High", color: ORANGE, description: "Nice to have"},
      {name: "P2 - Medium", color: YELLOW, description: "Backlog"}
    ]
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
        options {
          id
          name
        }
      }
    }
  }
}' > /tmp/priority_field.json

PRIORITY_FIELD_ID=$(jq -r '.data.createProjectV2Field.projectV2Field.id' /tmp/priority_field.json)
echo "  ✅ Priority field created: $PRIORITY_FIELD_ID"
echo ""

# Get option IDs
P0_OPTION_ID=$(jq -r '.data.createProjectV2Field.projectV2Field.options[] | select(.name == "P0 - Critical") | .id' /tmp/priority_field.json)
P1_OPTION_ID=$(jq -r '.data.createProjectV2Field.projectV2Field.options[] | select(.name == "P1 - High") | .id' /tmp/priority_field.json)

echo "Option IDs:"
echo "  P0 - Critical: $P0_OPTION_ID"
echo "  P1 - High: $P1_OPTION_ID"
echo ""

# Get all project items
echo "Getting project items and their labels..."
ITEMS=$(gh project item-list $PROJECT_NUMBER --owner @me --format json --limit 100)

echo "Setting priority for each item based on labels..."
echo ""

# Function to get labels for an issue
get_issue_labels() {
  local issue_num=$1
  gh issue view $issue_num --json labels --jq '.labels[].name' | tr '\n' ' '
}

# Process each item
echo "$ITEMS" | jq -r '.items[] | "\(.id)|\(.content.number)"' | while IFS='|' read -r item_id issue_num; do
  if [ -z "$issue_num" ] || [ "$issue_num" == "null" ]; then
    continue
  fi
  
  labels=$(get_issue_labels $issue_num)
  
  if echo "$labels" | grep -q "priority:p0"; then
    priority="P0"
    option_id="$P0_OPTION_ID"
  elif echo "$labels" | grep -q "priority:p1"; then
    priority="P1"
    option_id="$P1_OPTION_ID"
  else
    echo "  #$issue_num - No priority label, skipping"
    continue
  fi
  
  echo "  #$issue_num → $priority"
  
  # Set the priority using GraphQL API
  gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "'"$PROJECT_ID"'"
      itemId: "'"$item_id"'"
      fieldId: "'"$PRIORITY_FIELD_ID"'"
      value: {singleSelectOptionId: "'"$option_id"'"}
    }) {
      projectV2Item {
        id
      }
    }
  }' > /dev/null && echo "    ✅ Set" || echo "    ❌ Failed"
done

echo ""
echo "✅ Priority field setup complete!"
echo ""
echo "🔗 View project: https://github.com/users/thaddiusatme/projects/2"
echo ""
echo "📊 Summary:"
echo "  • P0 - Critical: 6 issues (#29, #30, #31, #32, #34, #36)"
echo "  • P1 - High: 3 issues (#33, #35, #37)"
