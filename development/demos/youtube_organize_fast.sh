#!/bin/bash
#
# Fast YouTube Notes Migration Script
# Uses grep for speed, then Python for precise frontmatter updates
#

set -e

VAULT_ROOT="${1:-.}"
INBOX_DIR="$VAULT_ROOT/knowledge/Inbox"
YOUTUBE_DIR="$INBOX_DIR/YouTube"
DRY_RUN="${2:-true}"

echo "========================================================================"
echo "YOUTUBE NOTES FAST MIGRATION"
echo "========================================================================"
echo ""

if [ "$DRY_RUN" = "false" ]; then
    echo "✅ LIVE MODE - Changes will be applied"
else
    echo "⚠️  DRY RUN MODE - No changes will be made"
fi
echo ""

# Create YouTube directory if needed
if [ "$DRY_RUN" = "false" ]; then
    mkdir -p "$YOUTUBE_DIR"
fi

# Find YouTube notes using grep (FAST!)
# Exclude backup files (_backup_ pattern)
echo "Finding YouTube notes (excluding backups)..."
YOUTUBE_FILES=$(grep -l "source: youtube" "$INBOX_DIR"/*.md 2>/dev/null | grep -v "_backup_" || true)

if [ -z "$YOUTUBE_FILES" ]; then
    echo "No YouTube notes found."
    exit 0
fi

# Count files
FILE_COUNT=$(echo "$YOUTUBE_FILES" | wc -l | tr -d ' ')
echo "Found $FILE_COUNT YouTube notes"
echo ""

MOVED=0
FIXED=0

# Process each file
for FILE in $YOUTUBE_FILES; do
    BASENAME=$(basename "$FILE")
    echo "Processing: $BASENAME"
    
    # Check if already in YouTube dir
    if [[ "$FILE" == *"/YouTube/"* ]]; then
        echo "  → Already in YouTube directory"
        continue
    fi
    
    # Check if video_id is empty
    VIDEO_ID=$(grep "^video_id:" "$FILE" | sed 's/video_id: *//')
    
    if [ -z "$VIDEO_ID" ] || [ "$VIDEO_ID" = "" ]; then
        echo "  → Empty video_id, extracting from body..."
        
        # Extract from body using grep and sed
        BODY_VIDEO_ID=$(grep -o "Video ID[*: ]*\`*[a-zA-Z0-9_-]\+" "$FILE" | tail -1 | sed 's/.*[`]//' | sed 's/[`]$//')
        
        if [ -n "$BODY_VIDEO_ID" ]; then
            echo "  → Extracted: $BODY_VIDEO_ID"
            
            if [ "$DRY_RUN" = "false" ]; then
                # Update frontmatter using sed
                sed -i.bak "s/^video_id: *$/video_id: $BODY_VIDEO_ID/" "$FILE"
                rm "$FILE.bak"
            fi
            
            FIXED=$((FIXED + 1))
        else
            echo "  ⚠️  Could not extract video_id from body"
        fi
    fi
    
    # Move file to YouTube directory
    TARGET="$YOUTUBE_DIR/$BASENAME"
    
    if [ -f "$TARGET" ]; then
        echo "  ⚠️  Target already exists, skipping move"
    else
        echo "  → Moving to Inbox/YouTube/"
        
        if [ "$DRY_RUN" = "false" ]; then
            mv "$FILE" "$TARGET"
        fi
        
        MOVED=$((MOVED + 1))
    fi
    
    echo ""
done

# Final report
echo "========================================================================"
echo "MIGRATION SUMMARY"
echo "========================================================================"
echo "YouTube notes found: $FILE_COUNT"
echo "Files moved: $MOVED"
echo "Frontmatter fixed: $FIXED"
echo "========================================================================"
