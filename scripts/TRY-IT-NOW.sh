#!/bin/bash
# Interactive Demo: See the subdirectory enhancement in action
# Safe to run - shows benefits without making changes

echo ""
echo "🎯 Auto-Promotion Subdirectory Enhancement - LIVE DEMO"
echo "══════════════════════════════════════════════════════"
echo ""
echo "✨ This enhancement makes 66 additional notes discoverable!"
echo ""

# Change to repo root
cd "$(dirname "$0")"

echo "📊 IMPACT COMPARISON:"
echo "────────────────────"
echo -n "   Before (root only):   "
find knowledge/Inbox -maxdepth 1 -name '*.md' | wc -l | tr -d ' '
echo " notes"
echo -n "   After (recursive):     "
find knowledge/Inbox -name '*.md' | wc -l | tr -d ' '
echo " notes"
echo ""

echo "📁 SUBDIRECTORY DISCOVERY:"
echo "──────────────────────────"
youtube_count=$(find knowledge/Inbox/YouTube -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
echo "   YouTube/:  $youtube_count notes (NOW DISCOVERABLE!)"
echo "   Root/:     $(find knowledge/Inbox -maxdepth 1 -name '*.md' | wc -l | tr -d ' ') notes"
echo ""

echo "✅ WHAT YOU CAN DO NOW:"
echo "───────────────────────"
echo ""
echo "   Option 1: See what's ready (SAFE - no changes)"
echo "   → cd development && python3 validate_auto_promotion.py"
echo ""
echo "   Option 2: Promote 13 notes immediately"
echo "   → cd development && python3 validate_auto_promotion.py --execute"
echo ""
echo "   Option 3: Fix YouTube notes + promote all ~30"
echo "   → See Projects/REFERENCE/QUICK-START-PROMOTION.md for full instructions"
echo ""

echo "🎯 QUICK TEST - See a YouTube note that's NOW discoverable:"
echo "───────────────────────────────────────────────────────────"
youtube_note=$(find knowledge/Inbox/YouTube -name "*.md" | head -1)
if [ -n "$youtube_note" ]; then
    echo "   File: $(basename "$youtube_note")"
    echo "   Path: $youtube_note"
    echo ""
    echo "   This note is in a SUBDIRECTORY - the old code would miss it!"
    echo "   The new code FINDS IT with rglob() recursive scanning."
fi
echo ""

echo "📖 For detailed instructions, see:"
echo "   - Projects/REFERENCE/QUICK-START-PROMOTION.md (how to use the enhancement)"
echo "   - scripts/demo_subdirectory_benefits.sh (technical demo)"
echo ""
echo "🚀 Ready to try? Run:"
echo "   cd development && python3 validate_auto_promotion.py"
echo ""
