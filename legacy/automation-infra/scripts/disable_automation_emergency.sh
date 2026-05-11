#!/usr/bin/env bash
# Emergency Automation Rollback - Issue #34
#
# Immediately disables ALL automation when issues detected:
# - Stale locks
# - Repeated failures
# - Resource exhaustion
# - Critical errors
#
# Usage: .automation/scripts/disable_automation_emergency.sh [reason]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
CRON_BACKUP_DIR="$REPO_ROOT/.automation/cron"
LOG_DIR="$REPO_ROOT/.automation/logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REASON="${1:-Manual emergency disable}"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

main() {
    error "=========================================="
    error "🚨 EMERGENCY AUTOMATION ROLLBACK"
    error "=========================================="
    error "Reason: $REASON"
    error "Time: $(date)"
    log ""
    
    # 1. Backup current crontab
    log "1. Backing up current crontab..."
    mkdir -p "$CRON_BACKUP_DIR"
    
    if crontab -l > /dev/null 2>&1; then
        local backup_file="$CRON_BACKUP_DIR/emergency_backup_$TIMESTAMP.txt"
        crontab -l > "$backup_file"
        log "   ✅ Backed up to: $backup_file"
    else
        log "   ℹ️  No crontab to backup"
    fi
    
    # 2. Disable all cron jobs
    log ""
    log "2. Disabling all InnerOS cron jobs..."
    
    if crontab -l > /dev/null 2>&1; then
        # Comment out all InnerOS-related cron jobs
        crontab -l | sed 's/^\([^#].*inneros.*\)/#EMERGENCY_DISABLED# \1/' | \
                     sed 's/^\([^#].*\.automation.*\)/#EMERGENCY_DISABLED# \1/' | \
                     crontab -
        log "   ✅ All automation cron jobs disabled"
    else
        log "   ℹ️  No crontab configured"
    fi
    
    # 3. Kill any running daemon processes
    log ""
    log "3. Stopping any running automation processes..."
    
    # Stop Python daemon if running
    if pgrep -f "python.*automation.*daemon" > /dev/null; then
        pkill -TERM -f "python.*automation.*daemon" || true
        sleep 2
        
        # Force kill if still running
        if pgrep -f "python.*automation.*daemon" > /dev/null; then
            pkill -KILL -f "python.*automation.*daemon" || true
        fi
        log "   ✅ Daemon processes stopped"
    else
        log "   ℹ️  No daemon processes running"
    fi
    
    # 4. Clean up any PID files
    log ""
    log "4. Cleaning up PID files..."
    
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.pid" -delete 2>/dev/null || true
        log "   ✅ PID files cleaned up"
    fi
    
    # 5. Create emergency status file
    log ""
    log "5. Creating emergency status file..."
    
    cat > "$REPO_ROOT/.automation/AUTOMATION_EMERGENCY_DISABLED" << EOF
InnerOS Automation EMERGENCY DISABLED
======================================
Disabled: $(date)
Reason: $REASON

Emergency rollback executed due to critical issue.
All automation has been stopped immediately.

To re-enable automation:
1. Investigate and resolve the issue that triggered this rollback
2. Remove this file: rm .automation/AUTOMATION_EMERGENCY_DISABLED
3. Review system health: python3 .automation/scripts/check_automation_health.py
4. If healthy, re-enable with: .automation/scripts/enable_automation_staged.sh phase1

Backup Location:
$backup_file

Do NOT re-enable automation until the root cause is resolved!
EOF
    
    log "   ✅ Status file created"
    
    # 6. Capture final system state
    log ""
    log "6. Capturing system state for investigation..."
    
    local state_file="$LOG_DIR/emergency_state_$TIMESTAMP.log"
    {
        echo "=== Emergency Rollback State Capture ==="
        echo "Time: $(date)"
        echo "Reason: $REASON"
        echo ""
        echo "=== Recent Logs ==="
        find "$LOG_DIR" -name "*.log" -mtime -1 -exec tail -20 {} \; 2>/dev/null || true
        echo ""
        echo "=== Process List ==="
        ps aux | grep -E "python|automation|daemon" | grep -v grep || true
        echo ""
        echo "=== Disk Usage ==="
        df -h "$REPO_ROOT" || true
        echo ""
        echo "=== Memory Usage ==="
        free -h 2>/dev/null || vm_stat || true
    } > "$state_file"
    
    log "   ✅ State captured to: $state_file"
    
    # 7. Final summary
    log ""
    error "=========================================="
    error "🛑 AUTOMATION EMERGENCY ROLLBACK COMPLETE"
    error "=========================================="
    log ""
    log "Actions taken:"
    log "  ✅ Crontab backed up"
    log "  ✅ All cron jobs disabled"
    log "  ✅ Daemon processes stopped"
    log "  ✅ PID files cleaned up"
    log "  ✅ Emergency status file created"
    log "  ✅ System state captured"
    log ""
    warn "⚠️  DO NOT RE-ENABLE AUTOMATION UNTIL:"
    log "  1. Root cause identified and resolved"
    log "  2. System health verified"
    log "  3. Proper testing completed"
    log ""
    log "Investigation files:"
    log "  • Status: .automation/AUTOMATION_EMERGENCY_DISABLED"
    log "  • State: $state_file"
    log "  • Logs: $LOG_DIR/"
    log ""
    log "To check system health:"
    log "  python3 .automation/scripts/check_automation_health.py"
    log ""
}

main "$@"
