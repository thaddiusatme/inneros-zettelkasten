#!/bin/bash

# Windsurf Rules Migration Script
# Purpose: Archive unified rules and install modular ruleset
# Updated: 2025-08-10

set -e  # Exit on any error

echo "🔄 Windsurf Rules Migration Script"
echo "=================================="

# Define paths
RULES_DIR=".windsurf/rules"
ARCHIVE_DIR=".windsurf/archive"
PROJECT_ROOT="."

# Modular rules files to install
MODULAR_FILES=(
    "session-context.md"
    "current-issues.md"
    "file-organization.md"
    "ai-integration.md"
    "development-workflow.md"
    "content-standards.md"
    "privacy-security.md"
)

# Current unified rules files to archive
UNIFIED_FILES=(
    "windsurfrules.md"
    "windsurfrules-v4-balanced.md"
    "windsurfrules-v4-concise.md"
    "windsurfrules-v4-minimal.md"
)

echo "📋 Migration Plan:"
echo "- Archive existing unified rules → $ARCHIVE_DIR/"
echo "- Install modular rules → $RULES_DIR/"
echo "- Create backup and rollback options"
echo ""

# Create backup timestamp
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="$ARCHIVE_DIR/migration-$TIMESTAMP"

# Confirm with user
read -p "🤔 Proceed with migration? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting migration..."

# Step 1: Create necessary directories
echo "📁 Creating directories..."
mkdir -p "$BACKUP_DIR"
mkdir -p "$RULES_DIR"

# Step 2: Archive existing unified rules
echo "📦 Archiving existing unified rules..."
for file in "${UNIFIED_FILES[@]}"; do
    if [ -f "$RULES_DIR/$file" ]; then
        echo "  • Archiving $file"
        cp "$RULES_DIR/$file" "$BACKUP_DIR/"
        rm "$RULES_DIR/$file"
    else
        echo "  • Skipping $file (not found)"
    fi
done

# Step 3: Install modular rules
echo "📥 Installing modular rules..."
INSTALLED_COUNT=0
MISSING_COUNT=0

for file in "${MODULAR_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  • Installing $file"
        mv "$PROJECT_ROOT/$file" "$RULES_DIR/"
        INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
    else
        echo "  ⚠️  Missing $file (skipped)"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

# Step 4: Archive the old monolithic v4 file if it exists
if [ -f "$PROJECT_ROOT/windsurfrules-v4.md" ]; then
    echo "📦 Archiving windsurfrules-v4.md..."
    mv "$PROJECT_ROOT/windsurfrules-v4.md" "$BACKUP_DIR/"
fi

# Step 5: Create rollback script
echo "🔄 Creating rollback script..."
cat > "$BACKUP_DIR/rollback.sh" << EOF
#!/bin/bash
# Rollback script for rules migration $TIMESTAMP
echo "🔙 Rolling back rules migration..."
cd "\$(dirname "\$0")/../.."

# Remove modular rules
rm -f .windsurf/rules/session-context.md
rm -f .windsurf/rules/current-issues.md
rm -f .windsurf/rules/file-organization.md
rm -f .windsurf/rules/ai-integration.md
rm -f .windsurf/rules/development-workflow.md
rm -f .windsurf/rules/content-standards.md
rm -f .windsurf/rules/privacy-security.md

# Restore unified rules
cp .windsurf/archive/migration-$TIMESTAMP/*.md .windsurf/rules/ 2>/dev/null || true

echo "✅ Rollback complete"
EOF

chmod +x "$BACKUP_DIR/rollback.sh"

# Step 6: Create rules index (optional)
echo "📝 Creating rules index..."
cat > "$RULES_DIR/README.md" << EOF
# Windsurf Rules - Modular Structure

> **Migration Date**: $(date +"%Y-%m-%d %H:%M")  
> **Backup Location**: $BACKUP_DIR  

## 📂 Rules Structure

### Core Rules Files
1. **session-context.md** - Session principles, required reads, critical path management
2. **current-issues.md** - Critical bugs, active projects, blocking dependencies  
3. **file-organization.md** - File rules, metadata schemas, directory structure
4. **ai-integration.md** - AI capabilities, usage patterns, ethics & transparency
5. **development-workflow.md** - TDD methodology, integration guidelines, performance targets
6. **content-standards.md** - Note types, naming conventions, quality standards
7. **privacy-security.md** - Privacy by design, data portability, validation rules

### Usage Pattern
- Reference individual files when working on specific aspects
- All files work together to provide comprehensive guidance
- Update independently when requirements change

### Rollback
If needed, run: \`$BACKUP_DIR/rollback.sh\`
EOF

echo ""
echo "✅ Migration Complete!"
echo "===================="
echo "📊 Summary:"
echo "  • Installed: $INSTALLED_COUNT modular rules files"
echo "  • Missing: $MISSING_COUNT files (check project root)"
echo "  • Archived: ${#UNIFIED_FILES[@]} unified rules files"
echo "  • Backup: $BACKUP_DIR"
echo "  • Rollback: $BACKUP_DIR/rollback.sh"
echo ""
echo "📁 New rules structure:"
ls -la "$RULES_DIR/"
echo ""
echo "🎯 Next steps:"
echo "  1. Test the modular rules in a development session"
echo "  2. Commit the new rules structure to git"
echo "  3. Update documentation if needed"
echo ""
echo "💡 Tip: Use specific rule files as needed for focused development work"
