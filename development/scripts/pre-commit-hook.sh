#!/bin/bash
#
# Pre-commit Hook - CLI Pattern Linter
#
# This hook runs the CLI pattern linter on staged CLI files before commit.
# It prevents commits with CLI argument pattern violations.
#
# Installation:
#   ./development/scripts/install-pre-commit-hook.sh
#
# Bypass (use sparingly):
#   git commit --no-verify
#
# Configuration:
#   Create .cli-lint-config.json in repo root to customize behavior

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
LINTER_SCRIPT="$REPO_ROOT/development/scripts/cli_pattern_linter.py"

# Check if config file exists and linter is disabled
CONFIG_FILE="$REPO_ROOT/.cli-lint-config.json"
if [ -f "$CONFIG_FILE" ]; then
    # Check if linter is disabled in config
    if grep -q '"enabled".*:.*false' "$CONFIG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}⏭️  CLI linter disabled via config${NC}"
        exit 0
    fi
fi

# Get list of staged files
if [ -n "$TEST_FILES" ]; then
    # Test mode - use provided files
    STAGED_FILES="$TEST_FILES"
else
    # Normal mode - get staged .py files
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
fi

# If no Python files staged, exit successfully
if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# Filter to only CLI files (development/src/cli/*.py)
CLI_FILES=""
for file in $STAGED_FILES; do
    if [[ "$file" == development/src/cli/*.py ]]; then
        # Check if file exists (not deleted)
        if [ -f "$REPO_ROOT/$file" ]; then
            CLI_FILES="$CLI_FILES $REPO_ROOT/$file"
        fi
    fi
done

# If no CLI files staged, exit successfully
if [ -z "$CLI_FILES" ]; then
    echo -e "${GREEN}✓${NC} No CLI files to check"
    exit 0
fi

# Run linter on each CLI file
echo -e "${YELLOW}🔍 Checking CLI argument patterns...${NC}"

VIOLATIONS_FOUND=0
for file in $CLI_FILES; do
    echo -e "  Checking: ${file##*/}"
    
    # Run linter with --fail-on-violations flag
    if ! python "$LINTER_SCRIPT" --fail-on-violations "$file" > /tmp/cli-lint-output.txt 2>&1; then
        VIOLATIONS_FOUND=1
        echo -e "${RED}  ✗ Violations found${NC}"
        cat /tmp/cli-lint-output.txt
        echo ""
    else
        echo -e "${GREEN}  ✓ No violations${NC}"
    fi
done

# Clean up temp file
rm -f /tmp/cli-lint-output.txt

# Exit based on violations
if [ $VIOLATIONS_FOUND -eq 1 ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ Commit blocked: CLI argument pattern violations found${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "Please fix the violations above, or:"
    echo -e "  • Review the CLI Argument Standards: ${YELLOW}development/docs/CLI-ARGUMENT-STANDARDS.md${NC}"
    echo -e "  • Run linter manually: ${YELLOW}python development/scripts/cli_pattern_linter.py <file>${NC}"
    echo -e "  • Bypass hook (not recommended): ${YELLOW}git commit --no-verify${NC}"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ All CLI files pass argument pattern checks${NC}"
    exit 0
fi
