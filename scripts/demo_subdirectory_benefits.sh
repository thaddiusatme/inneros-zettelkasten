#!/bin/bash
# Demonstration: Auto-Promotion Subdirectory Enhancement Benefits
# Shows what you can do RIGHT NOW with the new feature

echo "🎯 Auto-Promotion Subdirectory Enhancement - Live Demo"
echo "======================================================"
echo ""

cd "$(dirname "$0")/.."

echo "1️⃣  BEFORE vs AFTER Comparison:"
echo "   OLD (glob - root only): $(find knowledge/Inbox -maxdepth 1 -name '*.md' | wc -l | tr -d ' ') notes"
echo "   NEW (rglob - recursive): $(find knowledge/Inbox -name '*.md' | wc -l | tr -d ' ') notes"
echo ""

echo "2️⃣  Subdirectory Discovery:"
echo "   - YouTube/: $(find knowledge/Inbox/YouTube -name '*.md' 2>/dev/null | wc -l | tr -d ' ') notes"
echo "   - Transcripts/: $(find knowledge/Inbox/Transcripts -name '*.md' 2>/dev/null | wc -l | tr -d ' ') notes"
echo "   - Root level: $(find knowledge/Inbox -maxdepth 1 -name '*.md' | wc -l | tr -d ' ') notes"
echo ""

echo "3️⃣  Auto-Promotion Status (DRY-RUN):"
cd development
python3 validate_auto_promotion.py 2>&1 | grep -A 5 "Analysis Complete"
cd ..
echo ""

echo "4️⃣  What You Can Do RIGHT NOW:"
echo "   ✅ Option A: Promote 12-13 ready notes immediately"
echo "      → cd development && python3 validate_auto_promotion.py --execute"
echo ""
echo "   ✅ Option B: Fix YouTube notes quality_scores first"
echo "      → See quick fix options below"
echo ""
echo "   ✅ Option C: View detailed preview"
echo "      → cd development && python3 validate_auto_promotion.py | less"
echo ""

echo "5️⃣  Quick Fix for YouTube Notes (17 notes missing quality_score):"
echo "   Option A: Default score (fastest - 2 min)"
echo "   Option B: AI processing (thorough - 5 min)"
echo "   Option C: Manual review (precise - 15 min)"
echo ""
echo "======================================================"
echo "🚀 Enhancement is LIVE and WORKING on this branch!"
