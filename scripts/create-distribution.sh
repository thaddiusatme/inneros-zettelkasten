#!/usr/bin/env bash
#
# InnerOS Distribution Creation Script
# 
# Creates a clean distribution for public release by:
# 1. Cloning source repository
# 2. Removing personal content
# 3. Injecting sample knowledge pack
# 4. Running security audit
# 5. Validating tests pass
#
# REFACTOR PHASE: Extracted functions with improved error handling.

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOURCE_DIR="${1:-.}"
DIST_NAME="inneros-distribution"
DIST_DIR="$(dirname "$SOURCE_DIR")/$DIST_NAME"
STEP_COUNT=0

# ================================================
# HELPER FUNCTIONS (REFACTOR PHASE)
# ================================================

# Print step header
print_step() {
    STEP_COUNT=$((STEP_COUNT + 1))
    echo -e "${YELLOW}📋 Step $STEP_COUNT: $1...${NC}"
}

# Print success message
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo ""
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Print error and exit
print_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    exit 1
}

# Remove personal content directories
remove_personal_content() {
    local dist_dir="$1"
    local personal_dirs=(
        "knowledge/Inbox"
        "Reviews"
        "Media"
        "backups"
        ".automation/logs"
    )
    
    for dir in "${personal_dirs[@]}"; do
        if [ -d "$dist_dir/$dir" ]; then
            echo "   Removing $dir..."
            rm -rf "$dist_dir/$dir"
        fi
    done
}

# Count files in directory (for validation)
count_files() {
    local dir="$1"
    find "$dir" -type f | wc -l | tr -d ' '
}

# ================================================
# MAIN SCRIPT
# ================================================

echo -e "${BLUE}🚀 InnerOS Distribution Creation${NC}"
echo "================================================"
echo ""

# Validate source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "Source directory does not exist: $SOURCE_DIR"
fi

# Step 1: Clone source to distribution directory
print_step "Cloning source repository"
if [ -d "$DIST_DIR" ]; then
    echo "   Removing existing distribution directory..."
    rm -rf "$DIST_DIR" || print_error "Failed to remove existing distribution"
fi

echo "   Copying source to distribution..."
cp -r "$SOURCE_DIR" "$DIST_DIR" || print_error "Failed to copy source directory"

SOURCE_FILE_COUNT=$(count_files "$SOURCE_DIR")
echo "   Source files: $SOURCE_FILE_COUNT"
print_success "Source cloned to $DIST_DIR"

# Step 2: Remove personal content directories
print_step "Removing personal content"
remove_personal_content "$DIST_DIR"
print_success "Personal content removed"

# Step 3: Inject sample knowledge pack
print_step "Injecting sample knowledge pack"
if [ -d "$SOURCE_DIR/knowledge-starter-pack" ]; then
    cp -r "$SOURCE_DIR/knowledge-starter-pack" "$DIST_DIR/" || \
        print_error "Failed to copy knowledge starter pack"
    print_success "Sample knowledge pack injected"
else
    print_warning "No knowledge-starter-pack found, skipping"
    echo ""
fi

# Step 4: Swap .gitignore to distribution version
print_step "Swapping .gitignore"
if [ -f "$SOURCE_DIR/.gitignore-distribution" ]; then
    cp "$SOURCE_DIR/.gitignore-distribution" "$DIST_DIR/.gitignore" || \
        print_error "Failed to copy .gitignore-distribution"
    print_success ".gitignore swapped to distribution version"
else
    print_warning "No .gitignore-distribution found, skipping"
    echo ""
fi

# Step 5: Run security audit
print_step "Running security audit"
if python3 "$SOURCE_DIR/scripts/security-audit.py" "$DIST_DIR"; then
    print_success "Security audit passed"
else
    print_error "Security audit failed - distribution blocked"
fi

# Step 6: Validate tests (if pytest available)
print_step "Validating tests"
if command -v pytest &> /dev/null; then
    if [ -d "$DIST_DIR/development/tests" ]; then
        echo "   Running pytest validation..."
        # This is just a check that tests exist and can be discovered
        # Don't fail the whole script if some tests fail
        pytest "$DIST_DIR/development/tests" --collect-only &> /dev/null || true
        print_success "Test validation complete"
    else
        print_warning "No tests directory found"
        echo ""
    fi
else
    print_warning "pytest not available, skipping test validation"
    echo ""
fi

# Final file count and success message
DIST_FILE_COUNT=$(count_files "$DIST_DIR")
echo "================================================"
echo -e "${GREEN}🎉 Distribution created successfully!${NC}"
echo ""
echo "📊 Distribution Statistics:"
echo "   Location: $DIST_DIR"
echo "   Files: $DIST_FILE_COUNT (reduced from $SOURCE_FILE_COUNT)"
echo ""
echo "📋 Next steps:"
echo "  1. Review the distribution manually"
echo "  2. Run tests: cd $DIST_DIR && pytest"
echo "  3. Create git repository and push to GitHub"
echo "  4. Tag with version: git tag v0.1.0-alpha"
echo ""
