#!/bin/bash
# Manual End-to-End Demo - Guaranteed to work

set -e

REPO_ROOT="/Users/thaddius/repos/inneros-zettelkasten"
DEV_DIR="$REPO_ROOT/development"
TEST_NOTE="$REPO_ROOT/knowledge/Inbox/YouTube/manual-demo-$(date +%Y%m%d-%H%M%S).md"

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🎬 YouTube Automation: Complete End-to-End Demo              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This demo will show the complete workflow:"
echo "  1. Create a YouTube note"
echo "  2. Set approval status"
echo "  3. Process with AI"
echo "  4. Show the results"
echo ""
read -p "Press ENTER to start..."

# ============================================================================
# STEP 1: Create the note
# ============================================================================

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  STEP 1: Creating YouTube Note                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cat > "$TEST_NOTE" << 'EOF'
---
type: literature
created: 2025-10-21 15:30
status: draft
ready_for_processing: false
tags:
  - youtube
  - demo
  - neural-networks
visibility: private
source: youtube
video_id: aircAruvnKk
video_url: https://www.youtube.com/watch?v=aircAruvnKk
channel: 3Blue1Brown
author: Grant Sanderson
---

# But what is a neural network? | Manual Demo

## Video Information
- **Channel**: 3Blue1Brown
- **Video URL**: https://www.youtube.com/watch?v=aircAruvnKk
- **Video ID**: `aircAruvnKk`
- **Date Saved**: 2025-10-21

## Why I'm Saving This

This is an excellent visual explanation of neural networks from first
principles. Grant Sanderson's animations make complex mathematical
concepts intuitive and accessible.

## Key Takeaways
<!-- AI will extract key quotes here -->

---

## 🚦 AI Processing Approval

**Status**: Draft - Ready for Review

To approve this note for AI quote extraction:
- [ ] ✅ **Check this box when ready**

**Current Status**: `draft`
EOF

echo "✅ Created note: $(basename $TEST_NOTE)"
echo ""
echo "📄 Initial frontmatter:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
head -18 "$TEST_NOTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Key fields:"
echo "  📌 status: draft"
echo "  📌 ready_for_processing: false"
echo "  📌 ai_processed: (not set)"
echo ""
read -p "Press ENTER to continue..."

# ============================================================================
# STEP 2: User reviews and approves
# ============================================================================

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  STEP 2: User Reviews & Approves Note                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "In real usage, the user would:"
echo "  1. Open the note in Obsidian"
echo "  2. Add their thoughts and context"
echo "  3. Check the approval checkbox when ready"
echo "  4. Save the file"
echo ""
echo "This triggers: ready_for_processing: false → true"
echo ""
read -p "Press ENTER to simulate approval..."

# Update the approval status
sed -i '' 's/ready_for_processing: false/ready_for_processing: true/' "$TEST_NOTE"
sed -i '' 's/- \[ \] ✅ \*\*Check this box when ready\*\*/- [x] ✅ **Check this box when ready**/' "$TEST_NOTE"

echo ""
echo "✅ Approval checkbox checked!"
echo ""
echo "📄 Updated frontmatter:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
head -18 "$TEST_NOTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Key fields:"
echo "  📌 status: draft"
echo "  📌 ready_for_processing: true ← APPROVED!"
echo "  📌 ai_processed: (not set)"
echo ""
read -p "Press ENTER to process with AI..."

# ============================================================================
# STEP 3: Process with AI
# ============================================================================

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  STEP 3: AI Processing                                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Processing will:"
echo "  1. ✅ Validate approval status"
echo "  2. 🔄 Update status: draft → processing"
echo "  3. 📡 Fetch English transcript from YouTube"
echo "  4. 🤖 Extract key quotes using AI"
echo "  5. 💾 Archive transcript with bidirectional links"
echo "  6. 🔄 Update status: processing → processed"
echo "  7. ✅ Mark as ai_processed: true"
echo ""
echo "This typically takes 15-20 seconds..."
echo ""
read -p "Press ENTER to start processing..."

echo ""
cd "$DEV_DIR"
python3 process_single_youtube_note.py "$TEST_NOTE"

echo ""
read -p "Press ENTER to see the results..."

# ============================================================================
# STEP 4: Show results
# ============================================================================

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  STEP 4: Results                                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📄 Final frontmatter:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
head -30 "$TEST_NOTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Processing Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Extract key fields
STATUS=$(grep "^status:" "$TEST_NOTE" | cut -d: -f2 | xargs)
AI_PROCESSED=$(grep "^ai_processed:" "$TEST_NOTE" | cut -d: -f2 | xargs)
QUOTE_COUNT=$(grep "^quote_count:" "$TEST_NOTE" | cut -d: -f2 | xargs || echo "N/A")
TRANSCRIPT=$(grep "^transcript_file:" "$TEST_NOTE" | cut -d: -f2 | xargs || echo "N/A")
PROCESSING_TIME=$(grep "^processing_time_seconds:" "$TEST_NOTE" | cut -d: -f2 | xargs || echo "N/A")

echo "  📌 Status: $STATUS"
echo "  📌 AI Processed: $AI_PROCESSED"
echo "  📌 Quotes Extracted: $QUOTE_COUNT"
echo "  📌 Processing Time: ${PROCESSING_TIME}s"
echo "  📌 Transcript: $TRANSCRIPT"
echo ""

# Show extracted quotes
if grep -q "### 🎯 Extracted Quotes" "$TEST_NOTE"; then
    echo "🎯 Extracted Quotes Preview:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    sed -n '/### 🎯 Extracted Quotes/,/^---$/p' "$TEST_NOTE" | head -20
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🎉 Demo Complete!                                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Test note location:"
echo "   $TEST_NOTE"
echo ""
echo "🚀 In Production:"
echo "   Method 1 (Daemon): Processes automatically when you check the box"
echo "   Method 2 (API): Trigger via HTTP POST webhook"
echo "   Method 3 (CLI): Manual processing for testing"
echo ""
echo "To start the daemon:"
echo "   cd $DEV_DIR"
echo "   python3 -m src.automation.daemon start"
echo ""
