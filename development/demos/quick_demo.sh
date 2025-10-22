#!/bin/bash
# Quick Demo - Just show the daemon processing a note automatically

set -e

REPO_ROOT="/Users/thaddius/repos/inneros-zettelkasten"
DEV_DIR="$REPO_ROOT/development"
TEST_NOTE="$REPO_ROOT/knowledge/Inbox/YouTube/quick-demo-$(date +%Y%m%d-%H%M%S).md"

echo "🎬 Quick Demo: YouTube Automation"
echo "=================================="
echo ""

# Create test note
echo "📝 Step 1: Creating test note..."
cat > "$TEST_NOTE" << 'EOF'
---
type: literature
created: 2025-10-21 15:30
status: draft
ready_for_processing: false
tags: [youtube, demo]
visibility: private
source: youtube
video_id: aircAruvnKk
video_url: https://www.youtube.com/watch?v=aircAruvnKk
channel: 3Blue1Brown
---

# Neural Network Demo

## Why I'm Saving This
Quick automation test.
EOF

echo "✅ Created: $(basename $TEST_NOTE)"
echo ""

# Start daemon if not running
echo "🤖 Step 2: Ensuring daemon is running..."
cd "$DEV_DIR"

if pgrep -f "src.automation.daemon" > /dev/null; then
    echo "✅ Daemon already running"
else
    echo "   Starting daemon..."
    python3 -m src.automation.daemon start > /dev/null 2>&1 &
    sleep 3
    echo "✅ Daemon started"
fi
echo ""

# Show before state
echo "📋 Step 3: Current state (BEFORE):"
echo "   status: draft"
echo "   ready_for_processing: false"
echo "   ai_processed: (not set)"
echo ""

echo "✅ Step 4: Simulating user approval..."
echo "   (In Obsidian, you'd just check the box)"
sed -i '' 's/ready_for_processing: false/ready_for_processing: true/' "$TEST_NOTE"
echo "✅ Approval checkbox checked!"
echo ""

echo "⏳ Step 5: Waiting for daemon to process (10 seconds)..."
for i in {1..10}; do
    sleep 1
    echo -n "."
    if grep -q "ai_processed: true" "$TEST_NOTE"; then
        echo ""
        break
    fi
done
echo ""

# Show after state
echo ""
echo "📋 Step 6: Final state (AFTER):"
if grep -q "ai_processed: true" "$TEST_NOTE"; then
    echo "✅ SUCCESS! Note automatically processed!"
    echo ""
    echo "Details:"
    grep "status:" "$TEST_NOTE" || true
    grep "ai_processed:" "$TEST_NOTE" || true
    grep "quote_count:" "$TEST_NOTE" || true
    grep "processing_time" "$TEST_NOTE" || true
else
    echo "⏳ Still processing... (may need more time)"
    echo "   Check: $TEST_NOTE"
fi

echo ""
echo "🎉 Demo complete!"
echo ""
echo "Test note: $TEST_NOTE"
echo "You can delete it or keep it for reference."
echo ""
