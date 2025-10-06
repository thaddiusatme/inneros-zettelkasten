#!/bin/bash
# Move Architectural Rules to .windsurf/rules/

echo "🏗️  Moving Architectural Rules to .windsurf/rules/..."
echo ""

# Copy new architectural constraints
echo "1. Copying architectural-constraints.md..."
cp Projects/ACTIVE/windsurf-rules-ready-to-move/architectural-constraints.md .windsurf/rules/

# Replace development workflow with updated version
echo "2. Replacing updated-development-workflow.md..."
cp Projects/ACTIVE/windsurf-rules-ready-to-move/updated-development-workflow.md .windsurf/rules/

echo ""
echo "✅ Files moved successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review the files in .windsurf/rules/"
echo "2. Delete the staging directory:"
echo "   rm -rf Projects/ACTIVE/windsurf-rules-ready-to-move/"
echo "3. Delete superseded draft:"
echo "   rm Projects/ACTIVE/architectural-rules-draft.md"
echo "4. Commit the changes:"
echo "   git add .windsurf/rules/"
echo "   git commit -m 'chore: Deploy architectural rules to .windsurf/rules/'"
echo ""
echo "🎉 Architectural guardrails deployed!"
