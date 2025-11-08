#!/bin/bash
#
# Install Pre-commit Hook - CLI Pattern Linter
#
# This script installs the CLI pattern linter as a Git pre-commit hook.
# The hook will run automatically before each commit to validate CLI files.
#
# Usage:
#   ./development/scripts/install-pre-commit-hook.sh
#
# What it does:
#   1. Checks if .git/hooks directory exists
#   2. Backs up existing pre-commit hook if present
#   3. Copies pre-commit-hook.sh to .git/hooks/pre-commit
#   4. Makes the hook executable
#
# To uninstall:
#   rm .git/hooks/pre-commit
#   # Or restore backup:
#   mv .git/hooks/pre-commit.backup .git/hooks/pre-commit

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

# Check if we're in a git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Paths
HOOK_SOURCE="$REPO_ROOT/development/scripts/pre-commit-hook.sh"
HOOK_DEST="$REPO_ROOT/.git/hooks/pre-commit"
HOOK_BACKUP="$REPO_ROOT/.git/hooks/pre-commit.backup"

# Check if source hook exists
if [ ! -f "$HOOK_SOURCE" ]; then
    echo "Error: Hook source not found: $HOOK_SOURCE"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$REPO_ROOT/.git/hooks"

# Backup existing hook if present
if [ -f "$HOOK_DEST" ]; then
    echo -e "${YELLOW}⚠️  Existing pre-commit hook found${NC}"
    echo -e "   Backing up to: pre-commit.backup"
    cp "$HOOK_DEST" "$HOOK_BACKUP"
fi

# Copy hook
echo -e "${GREEN}📋 Installing CLI pattern linter pre-commit hook...${NC}"
cp "$HOOK_SOURCE" "$HOOK_DEST"

# Make executable
chmod +x "$HOOK_DEST"

# Verify installation
if [ -x "$HOOK_DEST" ]; then
    echo -e "${GREEN}✓ Pre-commit hook installed successfully${NC}"
    echo ""
    echo "The hook will now run automatically before each commit to check:"
    echo "  • --vault flag presence in workflow CLIs"
    echo "  • Help text completeness (description, epilog)"
    echo "  • Argument naming conventions (lowercase-with-hyphens)"
    echo "  • Boolean flag patterns (store_true/store_false)"
    echo ""
    echo "To bypass the hook (not recommended):"
    echo "  git commit --no-verify"
    echo ""
    echo "To configure the hook:"
    echo "  Create .cli-lint-config.json in repository root"
    echo ""
    echo "To uninstall:"
    echo "  rm .git/hooks/pre-commit"
    if [ -f "$HOOK_BACKUP" ]; then
        echo "  # Or restore your previous hook:"
        echo "  mv .git/hooks/pre-commit.backup .git/hooks/pre-commit"
    fi
else
    echo "Error: Failed to install hook"
    exit 1
fi
