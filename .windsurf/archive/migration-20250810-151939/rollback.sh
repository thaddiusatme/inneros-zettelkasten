#!/bin/bash
# Rollback script for rules migration 20250810-151939
echo "🔙 Rolling back rules migration..."
cd "$(dirname "$0")/../.."

# Remove modular rules
rm -f .windsurf/rules/session-context.md
rm -f .windsurf/rules/current-issues.md
rm -f .windsurf/rules/file-organization.md
rm -f .windsurf/rules/ai-integration.md
rm -f .windsurf/rules/development-workflow.md
rm -f .windsurf/rules/content-standards.md
rm -f .windsurf/rules/privacy-security.md

# Restore unified rules
cp .windsurf/archive/migration-20250810-151939/*.md .windsurf/rules/ 2>/dev/null || true

echo "✅ Rollback complete"
