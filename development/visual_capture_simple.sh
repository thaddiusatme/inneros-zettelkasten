#!/bin/bash

# Visual Capture Processor - Simple Test Script
# Purpose: Validate real workflow before building complex system

echo "📸 Visual Capture Processor - Simple Test"
echo "========================================="

# Configuration - adjust these paths for your setup
CAPTURES_INBOX="$HOME/Desktop/Screenshots"  # Change to your actual screenshot folder
PROCESSED_DIR="$HOME/Desktop/processed_captures"
NOTES_DIR="knowledge/Inbox"

# Create directories if they don't exist
mkdir -p "$PROCESSED_DIR"
mkdir -p "$NOTES_DIR"

# Find the most recent screenshot
LATEST_CAPTURE=$(ls -t "$CAPTURES_INBOX"/*.png 2>/dev/null | head -1)

if [ -z "$LATEST_CAPTURE" ]; then
    echo "❌ No screenshots found in $CAPTURES_INBOX"
    echo "💡 Adjust CAPTURES_INBOX path in script to your screenshot folder"
    exit 1
fi

echo "📄 Processing: $(basename "$LATEST_CAPTURE")"
echo "📅 Size: $(du -h "$LATEST_CAPTURE" | cut -f1)"
echo ""

# Show the image (macOS specific - adjust for your OS)
if command -v open >/dev/null 2>&1; then
    echo "🖼️  Opening image for review..."
    open "$LATEST_CAPTURE"
    sleep 2  # Give time for image to open
fi

echo ""
echo "=== CAPTURE ANNOTATION ==="
read -p "📝 Your notes (or press Enter to skip): " user_notes

if [ -z "$user_notes" ]; then
    echo "⏩ Skipped - no notes provided"
    exit 0
fi

# Generate simple note filename
timestamp=$(date +"%Y%m%d-%H%M%S")
note_filename="capture-${timestamp}.md"
note_path="$NOTES_DIR/$note_filename"

# Create basic capture note
cat > "$note_path" << EOF
---
type: capture
created: $(date +"%Y-%m-%d %H:%M")
status: inbox
tags: [visual-capture, screenshot]
original_file: $(basename "$LATEST_CAPTURE")
---

# Visual Capture - $(date +"%Y-%m-%d %H:%M")

![Screenshot]($(basename "$LATEST_CAPTURE"))

## My Notes
$user_notes

## Source
- Captured: $(date +"%Y-%m-%d %H:%M")
- Original: $(basename "$LATEST_CAPTURE")

## Processing Notes
- Processed via simple capture script
- Original preserved in processed_captures/
EOF

# Move original to processed folder
processed_name="$(basename "$LATEST_CAPTURE" .png)_processed_$(date +%Y%m%d_%H%M%S).png"
cp "$LATEST_CAPTURE" "$PROCESSED_DIR/$processed_name"

echo ""
echo "✅ Capture processed successfully!"
echo "📝 Note created: $note_path"
echo "🖼️  Original preserved: $PROCESSED_DIR/$processed_name"
echo "📊 Note ready for AI processing via existing workflow"

echo ""
echo "🔄 Next steps:"
echo "   → Process with AI: cd $(dirname $0) && python3 inneros_batch_processor.py --ai-process --limit 1"
echo "   → Review in weekly workflow: python3 src/cli/workflow_demo.py . --weekly-review"

# Optional: Show created note content
echo ""
read -p "🔍 View created note? (y/n): " show_note
if [[ "$show_note" == "y" || "$show_note" == "Y" ]]; then
    echo ""
    echo "=== CREATED NOTE ==="
    cat "$note_path"
fi

echo ""
echo "🎯 Test completed! If this workflow feels right, we'll build the full system."
