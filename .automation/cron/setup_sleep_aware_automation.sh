#!/usr/bin/env bash
# InnerOS Zettelkasten - Sleep-Aware Automation Setup
# Sets up cron jobs with sleep prevention for reliable automation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
USER=$(whoami)

echo "🤖 Setting up sleep-aware InnerOS Zettelkasten automation..."
echo "Repository: $REPO_ROOT"
echo "User: $USER"

# Make scripts executable
chmod +x "$REPO_ROOT/.automation/scripts/"*.sh

# Create enhanced cron configuration with sleep management
CRON_FILE="/tmp/inneros_sleep_aware_cron_$$"

cat > "$CRON_FILE" << EOF
# InnerOS Zettelkasten Sleep-Aware Automated Workflows
# Generated on $(date)

# Prevent sleep 10 minutes before evening screenshot processing
20 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/manage_sleep_schedule.sh evening >/dev/null 2>&1

# Daily screenshot import at 11:30 PM (with sleep prevention active)
30 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/automated_screenshot_import.sh >/dev/null 2>&1

# Prevent sleep 10 minutes before morning processing (Mon/Wed/Fri)
50 5 * * 1,3,5 cd "$REPO_ROOT" && ./.automation/scripts/manage_sleep_schedule.sh morning >/dev/null 2>&1

# Supervised inbox processing: Monday, Wednesday, Friday at 6:00 AM
0 6 * * 1,3,5 cd "$REPO_ROOT" && ./.automation/scripts/supervised_inbox_processing.sh >/dev/null 2>&1

# Prevent sleep 10 minutes before weekly analysis (Sunday)
50 8 * * 0 cd "$REPO_ROOT" && ./.automation/scripts/manage_sleep_schedule.sh weekly >/dev/null 2>&1

# Weekly deep analysis: Sunday at 9:00 AM  
0 9 * * 0 cd "$REPO_ROOT" && ./.automation/scripts/weekly_deep_analysis.sh >/dev/null 2>&1

# Daily log cleanup (keep last 30 days)
0 2 * * * find "$REPO_ROOT/.automation/logs" -name "*.log" -mtime +30 -delete >/dev/null 2>&1

# System health monitoring: Every 4 hours during wake hours (6 AM - 10 PM)
0 6,10,14,18,22 * * * cd "$REPO_ROOT" && ./.automation/scripts/health_monitor.sh >/dev/null 2>&1

# Clean up sleep prevention processes (daily at midnight)
0 0 * * * cd "$REPO_ROOT" && ./.automation/scripts/manage_sleep_schedule.sh stop >/dev/null 2>&1

EOF

# Install enhanced cron jobs
echo "📅 Installing sleep-aware cron jobs..."
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "✅ Sleep-aware cron jobs installed successfully!"
echo ""
echo "📋 Enhanced automation schedule:"
echo "  • Sleep prevention: 10 minutes before each automation"  
echo "  • Evening screenshots: 11:20 PM - 11:40 PM (sleep-protected)"
echo "  • Morning processing: 5:50 AM - 6:20 AM (sleep-protected Mon/Wed/Fri)"
echo "  • Weekly analysis: 8:50 AM - 9:30 AM (sleep-protected Sunday)"
echo "  • Health monitoring: Every 4 hours (6 AM - 10 PM)"
echo "  • Cleanup: Daily at midnight (logs + sleep processes)"
echo ""
echo "🛌 Sleep management:"
echo "  • Mac will stay awake during automation windows"
echo "  • Normal sleep behavior preserved outside automation"
echo "  • Manual control: ./.automation/scripts/manage_sleep_schedule.sh"
echo ""
echo "🔧 Commands:"
echo "  Check status: ./.automation/scripts/manage_sleep_schedule.sh status"
echo "  Stop sleep prevention: ./.automation/scripts/manage_sleep_schedule.sh stop"
echo "  View cron jobs: crontab -l"
