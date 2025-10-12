#!/bin/bash
# Interactive Workflow Dashboard Launcher
# Quick start script for daily usage

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎯 InnerOS Interactive Workflow Dashboard"
echo "  TDD Iterations 1 & 2 - Production Ready"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Change to development directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import rich, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies!"
    echo "   Install with: pip install rich requests"
    exit 1
fi

echo "✅ Dependencies ready"
echo ""

# Show quick reference
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚡ Keyboard Shortcuts Quick Reference"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  [P] - Process Inbox      Process all inbox notes"
echo "  [W] - Weekly Review      Run weekly review workflow"
echo "  [F] - Fleeting Health    Check fleeting notes health"
echo "  [S] - System Status      View comprehensive status"
echo "  [B] - Backup             Create vault backup"
echo "  [Q] - Quit               Exit dashboard cleanly"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting dashboard..."
echo "   Vault: $(pwd)/../knowledge"
echo ""

# Launch dashboard (pointing to knowledge/ directory)
python3 src/cli/workflow_dashboard.py ../knowledge

# Exit message
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  👋 Dashboard closed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
