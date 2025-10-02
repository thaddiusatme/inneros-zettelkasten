#!/usr/bin/env bash
# InnerOS Zettelkasten - Automation Setup
# Sets up cron jobs for automated workflows with proper logging and monitoring

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
USER=$(whoami)

echo "🤖 Setting up InnerOS Zettelkasten automation..."
echo "Repository: $REPO_ROOT"
echo "User: $USER"

# Make scripts executable
chmod +x "$REPO_ROOT/.automation/scripts/"*.sh

# Create cron configuration
CRON_FILE="/tmp/inneros_cron_$$"

cat > "$CRON_FILE" << EOF
# InnerOS Zettelkasten Automated Workflows
# Generated on $(date)

# Daily screenshot import at 11:30 PM (when screenshots likely synced)
30 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/automated_screenshot_import.sh >/dev/null 2>&1

# Supervised inbox processing: Monday, Wednesday, Friday at 6:00 AM
0 6 * * 1,3,5 cd "$REPO_ROOT" && ./.automation/scripts/supervised_inbox_processing.sh >/dev/null 2>&1

# Weekly deep analysis: Sunday at 9:00 AM  
0 9 * * 0 cd "$REPO_ROOT" && ./.automation/scripts/weekly_deep_analysis.sh >/dev/null 2>&1

# Daily log cleanup (keep last 30 days)
0 2 * * * find "$REPO_ROOT/.automation/logs" -name "*.log" -mtime +30 -delete >/dev/null 2>&1

# System health monitoring: Every 4 hours during wake hours (6 AM - 10 PM)
0 6,10,14,18,22 * * * cd "$REPO_ROOT" && ./.automation/scripts/health_monitor.sh >/dev/null 2>&1

EOF

# Install cron jobs
echo "📅 Installing cron jobs..."
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "✅ Cron jobs installed successfully!"
echo ""
echo "📋 Scheduled automation:"
echo "  • Daily screenshot import: 11:30 PM"  
echo "  • Supervised processing: Mon/Wed/Fri 6:00 AM"
echo "  • Weekly deep analysis: Sunday 9:00 AM"
echo "  • Health monitoring: Every 4 hours (6 AM - 10 PM)"
echo "  • Log cleanup: Daily at 2:00 AM"
echo ""
echo "📁 Logs will be stored in: $REPO_ROOT/.automation/logs/"
echo "📋 Review reports in: $REPO_ROOT/.automation/review_queue/"
echo ""
echo "🔧 To view current cron jobs: crontab -l"
echo "🗑️  To remove automation: crontab -r"
