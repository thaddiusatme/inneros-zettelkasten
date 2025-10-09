#!/bin/bash
# Stop All InnerOS Automation - Emergency Shutdown Script
# Created: 2025-10-08
# Purpose: Stop file watching loop causing YouTube rate limiting

set -euo pipefail

REPO_ROOT="/Users/thaddius/repos/inneros-zettelkasten"

echo "🛑 STOPPING ALL INNEROS AUTOMATION"
echo "=================================="
echo ""

# 1. Kill any running Python automation processes
echo "1. Checking for running Python automation processes..."
PYTHON_PIDS=$(ps aux | grep -E "python.*automation|python.*daemon|python.*file.*watch" | grep -v grep | awk '{print $2}' || true)
if [ -n "$PYTHON_PIDS" ]; then
    echo "   Found Python automation processes: $PYTHON_PIDS"
    for pid in $PYTHON_PIDS; do
        echo "   Killing process $pid..."
        kill -TERM "$pid" 2>/dev/null || true
        sleep 1
        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "   Force killing process $pid..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    echo "   ✅ Python processes stopped"
else
    echo "   ✅ No Python automation processes running"
fi
echo ""

# 2. Disable cron jobs (comment them out)
echo "2. Disabling cron jobs..."
if crontab -l > /dev/null 2>&1; then
    # Backup current crontab
    BACKUP_FILE="$REPO_ROOT/.automation/cron/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    mkdir -p "$REPO_ROOT/.automation/cron"
    crontab -l > "$BACKUP_FILE"
    echo "   📦 Backed up crontab to: $BACKUP_FILE"
    
    # Comment out all InnerOS cron jobs
    crontab -l | sed 's/^\([^#].*inneros.*\)/#DISABLED# \1/' | crontab -
    echo "   ✅ Cron jobs disabled (commented out)"
    echo "   📝 To re-enable: crontab $BACKUP_FILE"
else
    echo "   ✅ No crontab configured"
fi
echo ""

# 3. Check for launchd agents
echo "3. Checking for LaunchAgents..."
LAUNCHD_AGENTS=$(find ~/Library/LaunchAgents -name "*inneros*" -o -name "*zettelkasten*" 2>/dev/null || true)
if [ -n "$LAUNCHD_AGENTS" ]; then
    echo "   Found LaunchAgents:"
    for agent in $LAUNCHD_AGENTS; do
        echo "   - $agent"
        launchctl unload "$agent" 2>/dev/null || true
    done
    echo "   ✅ LaunchAgents unloaded"
else
    echo "   ✅ No LaunchAgents found"
fi
echo ""

# 4. Stop any file watchers
echo "4. Checking for file watcher processes..."
WATCHER_PIDS=$(ps aux | grep -E "watchdog|fswatch|file.*watch" | grep -v grep | awk '{print $2}' || true)
if [ -n "$WATCHER_PIDS" ]; then
    echo "   Found file watcher processes: $WATCHER_PIDS"
    for pid in $WATCHER_PIDS; do
        echo "   Killing process $pid..."
        kill -TERM "$pid" 2>/dev/null || true
    done
    echo "   ✅ File watchers stopped"
else
    echo "   ✅ No file watchers running"
fi
echo ""

# 5. Check automation scripts status
echo "5. Current automation status:"
echo "   Script directory: $REPO_ROOT/.automation/scripts"
echo "   Log directory: $REPO_ROOT/.automation/logs"
echo ""

# 6. Verify everything is stopped
echo "6. Verification:"
REMAINING=$(ps aux | grep -E "python.*automation|daemon.*inneros" | grep -v grep || true)
if [ -z "$REMAINING" ]; then
    echo "   ✅ All automation processes stopped"
else
    echo "   ⚠️  Some processes may still be running:"
    echo "$REMAINING"
fi
echo ""

# 7. Create status file
echo "7. Creating status file..."
cat > "$REPO_ROOT/.automation/AUTOMATION_DISABLED" << EOF
InnerOS Automation DISABLED
===========================
Date: $(date)
Reason: YouTube rate limiting investigation
Action: Manual stop via stop_all_automation.sh

To re-enable:
1. Fix file watching loop bug (add cooldown logic)
2. Remove this file
3. Restore crontab: crontab $BACKUP_FILE
4. Test with single file before full restart

Status: AUTOMATION STOPPED ✅
EOF
echo "   ✅ Status file created: .automation/AUTOMATION_DISABLED"
echo ""

echo "=================================="
echo "✅ ALL AUTOMATION STOPPED"
echo ""
echo "📊 Summary:"
echo "   - Python processes: Killed"
echo "   - Cron jobs: Disabled (commented out)"
echo "   - File watchers: Stopped"
echo "   - LaunchAgents: Unloaded (if any)"
echo ""
echo "⚠️  IMPORTANT: Automation will stay disabled until you:"
echo "   1. Fix the file watching loop bug"
echo "   2. Remove .automation/AUTOMATION_DISABLED"
echo "   3. Re-enable crontab"
echo ""
echo "📝 Crontab backup: $BACKUP_FILE"
echo "🔧 Next step: Implement cooldown fix in feature_handlers.py"
