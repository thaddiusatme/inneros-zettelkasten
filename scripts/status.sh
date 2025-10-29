#!/bin/bash
# Simple status dashboard for InnerOS Zettelkasten
# Shows what's working and what you can do

cd "$(dirname "$0")"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        InnerOS Zettelkasten - System Status              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 1. Note counts
echo "📚 YOUR NOTES:"
inbox_count=$(find knowledge/Inbox -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
fleeting_count=$(find knowledge/Fleeting\ Notes -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
permanent_count=$(find knowledge/Permanent\ Notes -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
literature_count=$(find knowledge/Literature\ Notes -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
total=$((inbox_count + fleeting_count + permanent_count + literature_count))

echo "   📥 Inbox:      $inbox_count notes (waiting to be processed)"
echo "   📝 Fleeting:   $fleeting_count notes"
echo "   💎 Permanent:  $permanent_count notes"
echo "   📖 Literature: $literature_count notes"
echo "   ─────────────────────────────"
echo "   ✨ TOTAL:      $total notes in your knowledge system"
echo ""

# 2. What's ready to process
echo "🎯 READY FOR ACTION:"
echo "   • $inbox_count notes in Inbox/ can be processed"
echo "   • Run: cd development && python3 src/cli/core_workflow_cli.py process-inbox"
echo ""

# 3. Quick actions
echo "⚡ QUICK ACTIONS:"
echo ""
echo "   1. Process Inbox (AI enhance all inbox notes):"
echo "      → cd development && python3 src/cli/core_workflow_cli.py process-inbox"
echo ""
echo "   2. See promotion candidates (notes ready to move):"
echo "      → cd development && python3 validate_auto_promotion.py"
echo ""
echo "   3. Get analytics (understand your knowledge):"
echo "      → cd development && python3 ../src/cli/analytics_demo.py ../knowledge --section overview"
echo ""
echo "   4. Weekly review (what needs attention):"
echo "      → cd development && python3 src/cli/weekly_review_cli.py weekly-review"
echo ""

# 4. System health
echo "🔍 SYSTEM CHECK:"
if [ -d "development/src" ]; then
    echo "   ✓ Code structure intact"
else
    echo "   ✗ Code structure issue"
fi

if python3 -c "import sys; sys.path.insert(0, 'development'); from src.ai.workflow_manager import WorkflowManager" 2>/dev/null; then
    echo "   ✓ AI engine functional"
else
    echo "   ✗ AI engine issue"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📖 For detailed guide, see: Projects/REFERENCE/USABILITY-DASHBOARD.md"
echo "═══════════════════════════════════════════════════════════"
echo ""
