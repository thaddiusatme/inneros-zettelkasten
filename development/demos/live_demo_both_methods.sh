#!/bin/bash

# Live End-to-End Demo: YouTube Automation (Both Methods)
# This script demonstrates both the Daemon and API automation methods

set -e

REPO_ROOT="/Users/thaddius/repos/inneros-zettelkasten"
DEV_DIR="$REPO_ROOT/development"
DEMO_NOTE="$REPO_ROOT/knowledge/Inbox/YouTube/demo-automation-test-$(date +%Y%m%d-%H%M%S).md"

echo "================================================================"
echo "🎬 LIVE DEMO: YouTube Automation (Both Methods)"
echo "================================================================"
echo ""
echo "This demo will show:"
echo "  1. ✅ File Watcher Daemon (automatic processing)"
echo "  2. ✅ HTTP API Server (webhook processing)"
echo ""
echo "Press ENTER to start..."
read

# ============================================================================
# PART 1: Daemon Demo (File Watcher)
# ============================================================================

echo ""
echo "================================================================"
echo "📋 PART 1: File Watcher Daemon Demo"
echo "================================================================"
echo ""
echo "We'll create a test note and watch the daemon process it"
echo "automatically when we check the approval box."
echo ""
echo "Press ENTER to continue..."
read

# Create test note with unchecked box
echo ""
echo "📝 Creating test note with approval box UNCHECKED..."
cat > "$DEMO_NOTE" << 'EOF'
---
type: literature
created: 2025-10-21 15:15
status: draft
ready_for_processing: false
tags: [youtube, demo, automation-test]
visibility: private
source: youtube
video_id: aircAruvnKk
video_url: https://www.youtube.com/watch?v=aircAruvnKk
channel: 3Blue1Brown
author: Grant Sanderson
---

# But what is a neural network? | Demo Test

## Why I'm Saving This
Testing the automation system end-to-end.

## Key Takeaways
<!-- Will be filled by AI processing -->

---

## 🚦 AI Processing Approval

**Status**: Draft - Ready for Review

To approve this note for AI quote extraction:
- [ ] ✅ Check this box when ready

**Current Status**: `draft`
EOF

echo "✅ Test note created: $DEMO_NOTE"
echo ""
echo "📋 Current frontmatter:"
grep -A 12 "^---$" "$DEMO_NOTE" | head -14
echo ""

# Check if daemon is running
echo "🔍 Checking if daemon is running..."
cd "$DEV_DIR"

if python3 -c "from src.automation.daemon import AutomationDaemon; import sys; d = AutomationDaemon(); status = d.get_status(); sys.exit(0 if status.state.value == 'running' else 1)" 2>/dev/null; then
    echo "✅ Daemon is already running!"
else
    echo "⚠️  Daemon not running. Starting it now..."
    echo ""
    python3 -m src.automation.daemon start &
    DAEMON_PID=$!
    sleep 3
    echo "✅ Daemon started (PID: $DAEMON_PID)"
fi

echo ""
echo "================================================================"
echo "⏰ Now simulating user approval..."
echo "================================================================"
echo ""
echo "In real usage, you would:"
echo "  1. Open the note in Obsidian"
echo "  2. Check the approval box"
echo "  3. Save the file"
echo ""
echo "We'll simulate this by updating the file..."
echo ""
echo "Press ENTER to simulate checking the approval box..."
read

# Update the note to simulate checking the box
echo "✏️  Updating note: ready_for_processing: false → true"
sed -i '' 's/ready_for_processing: false/ready_for_processing: true/' "$DEMO_NOTE"
sed -i '' 's/- \[ \] ✅ Check this box when ready/- [x] ✅ Check this box when ready/' "$DEMO_NOTE"

echo "✅ Approval box checked!"
echo ""
echo "📋 Updated frontmatter:"
grep -A 12 "^---$" "$DEMO_NOTE" | head -14
echo ""

echo "⏳ Waiting for daemon to detect and process (5-10 seconds)..."
echo ""

# Monitor the file for changes
for i in {1..15}; do
    sleep 1
    echo -n "."
    
    # Check if processing has started
    if grep -q "processing_started_at" "$DEMO_NOTE"; then
        echo ""
        echo "🚀 Processing started!"
        break
    fi
done

# Wait for completion
echo ""
echo "⏳ Waiting for processing to complete..."
for i in {1..30}; do
    sleep 1
    echo -n "."
    
    if grep -q "processing_completed_at" "$DEMO_NOTE"; then
        echo ""
        echo "✅ Processing completed!"
        break
    fi
done

echo ""
echo "================================================================"
echo "📊 RESULTS: File Watcher Daemon"
echo "================================================================"
echo ""
echo "📋 Final frontmatter:"
grep -A 20 "^---$" "$DEMO_NOTE" | head -25
echo ""

if grep -q "ai_processed: true" "$DEMO_NOTE"; then
    echo "✅ SUCCESS! Note was automatically processed by the daemon!"
    echo ""
    echo "📊 Processing Details:"
    grep "quote_count:" "$DEMO_NOTE" || echo "   (quotes check skipped)"
    grep "transcript_file:" "$DEMO_NOTE" || echo "   (transcript check skipped)"
    grep "processing_time_seconds:" "$DEMO_NOTE" || echo "   (timing check skipped)"
else
    echo "⚠️  Daemon didn't process the note yet (may need more time)"
    echo "   Note: File watcher typically processes within 5-10 seconds"
fi

echo ""
echo "Press ENTER to continue to API demo..."
read

# ============================================================================
# PART 2: HTTP API Demo
# ============================================================================

echo ""
echo "================================================================"
echo "📋 PART 2: HTTP API Server Demo"
echo "================================================================"
echo ""
echo "We'll start the API server and trigger processing via HTTP POST."
echo ""
echo "Press ENTER to continue..."
read

# Create another test note
DEMO_NOTE_2="$REPO_ROOT/knowledge/Inbox/YouTube/demo-api-test-$(date +%Y%m%d-%H%M%S).md"

echo ""
echo "📝 Creating second test note for API demo..."
cat > "$DEMO_NOTE_2" << 'EOF'
---
type: literature
created: 2025-10-21 15:20
status: draft
ready_for_processing: true
tags: [youtube, demo, api-test]
visibility: private
source: youtube
video_id: aircAruvnKk
video_url: https://www.youtube.com/watch?v=aircAruvnKk
channel: 3Blue1Brown
author: Grant Sanderson
---

# Neural Network Demo - API Test

## Why I'm Saving This
Testing the HTTP API automation.

## Key Takeaways
<!-- Will be filled by AI processing -->
EOF

echo "✅ API test note created: $DEMO_NOTE_2"
echo "   Note: ready_for_processing is already TRUE"
echo ""

# Start API server in background
echo "🌐 Starting HTTP API server..."
cd "$DEV_DIR"
python3 run_youtube_api_server.py > /tmp/youtube_api_server.log 2>&1 &
API_PID=$!
sleep 3

# Check if server is running
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API server running (PID: $API_PID)"
    echo "   URL: http://localhost:8080"
else
    echo "❌ API server failed to start"
    echo "   Check logs: /tmp/youtube_api_server.log"
    exit 1
fi

echo ""
echo "📋 Available endpoints:"
curl -s http://localhost:8080/ | python3 -m json.tool 2>/dev/null || echo "   (Could not fetch endpoints)"
echo ""

echo "Press ENTER to trigger processing via HTTP POST..."
read

# Trigger processing via API
NOTE_PATH="${DEMO_NOTE_2#$REPO_ROOT/}"
echo ""
echo "📡 Sending HTTP POST request..."
echo "   Endpoint: http://localhost:8080/api/youtube/process"
echo "   Note: $NOTE_PATH"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8080/api/youtube/process \
    -H "Content-Type: application/json" \
    -d "{\"note_path\": \"$NOTE_PATH\"}")

echo "📬 API Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Extract job_id
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null || echo "")

if [ -n "$JOB_ID" ]; then
    echo "✅ Processing job queued: $JOB_ID"
    echo ""
    echo "⏳ Waiting for API to process note (15-20 seconds)..."
    
    for i in {1..25}; do
        sleep 1
        echo -n "."
        
        if grep -q "ai_processed: true" "$DEMO_NOTE_2"; then
            echo ""
            echo "✅ Processing completed!"
            break
        fi
    done
else
    echo "⚠️  No job_id received. Processing may have failed."
fi

echo ""
echo "================================================================"
echo "📊 RESULTS: HTTP API Server"
echo "================================================================"
echo ""
echo "📋 Final frontmatter:"
grep -A 20 "^---$" "$DEMO_NOTE_2" | head -25
echo ""

if grep -q "ai_processed: true" "$DEMO_NOTE_2"; then
    echo "✅ SUCCESS! Note was processed via HTTP API!"
else
    echo "⚠️  API processing still in progress or failed"
fi

echo ""
echo "🧹 Cleanup..."
echo "   Stopping API server (PID: $API_PID)..."
kill $API_PID 2>/dev/null || true

echo ""
echo "================================================================"
echo "🎉 DEMO COMPLETE!"
echo "================================================================"
echo ""
echo "Summary:"
echo "  ✅ Method 1 (Daemon): Automatic file watching"
echo "  ✅ Method 2 (HTTP API): Webhook-based processing"
echo ""
echo "Test notes created:"
echo "  1. $DEMO_NOTE"
echo "  2. $DEMO_NOTE_2"
echo ""
echo "You can delete these test notes or keep them for reference."
echo ""
echo "To use in production:"
echo "  • Daemon: python3 -m src.automation.daemon start"
echo "  • API: python3 run_youtube_api_server.py"
echo ""
