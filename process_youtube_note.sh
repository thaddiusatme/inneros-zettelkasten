#!/bin/bash
# Manual YouTube note processor
# Usage: ./process_youtube_note.sh "knowledge/Inbox/YouTube/YOUR-NOTE.md.md"

if [ -z "$1" ]; then
    echo "Usage: $0 <note-path>"
    echo "Example: $0 'knowledge/Inbox/YouTube/lit-20251019-1300-prismo-the-mirage-of-desire.md.md'"
    exit 1
fi

NOTE_PATH="$1"

echo "📝 Processing YouTube note: $NOTE_PATH"

RESPONSE=$(curl -s -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d "{\"note_path\": \"$NOTE_PATH\"}")

echo "✅ Response:"
echo "$RESPONSE" | python3 -m json.tool

JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 'none'))" 2>/dev/null)

if [ "$JOB_ID" != "none" ]; then
    echo ""
    echo "🎉 Processing started! Job ID: $JOB_ID"
    echo "⏳ Check your note in ~30-60 seconds for AI-generated quotes"
else
    echo ""
    echo "❌ Processing failed. Check the error above."
fi
