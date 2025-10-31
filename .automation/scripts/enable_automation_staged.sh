#!/usr/bin/env bash
# Staged Cron Enablement - Issue #34 Phase 3
# 
# Gradually re-enables automation with 24-hour observation periods:
# - Phase 1: Screenshot import only (24 hours)
# - Phase 2: Add inbox processing (24 hours)
# - Phase 3: Full automation (confirm 48-hour stability)
#
# Safety: Backs up current crontab before any changes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
CRON_BACKUP_DIR="$REPO_ROOT/.automation/cron"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Backup current crontab
backup_crontab() {
    mkdir -p "$CRON_BACKUP_DIR"
    
    if crontab -l > /dev/null 2>&1; then
        local backup_file="$CRON_BACKUP_DIR/crontab_backup_$TIMESTAMP.txt"
        crontab -l > "$backup_file"
        log "Crontab backed up to: $backup_file"
        echo "$backup_file"
    else
        log "No existing crontab to backup"
        echo ""
    fi
}

# Phase 1: Enable screenshot import only
enable_phase1() {
    log "=========================================="
    log "PHASE 1: Screenshot Import Only"
    log "=========================================="
    
    backup_file=$(backup_crontab)
    
    local cron_file="/tmp/inneros_cron_phase1_$$"
    
    cat > "$cron_file" << EOF
# InnerOS Automation - Phase 1 (Screenshot Import Only)
# Enabled: $(date)
# Observation Period: 24 hours

# Daily screenshot import at 11:30 PM
30 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/automated_screenshot_import.sh >/dev/null 2>&1

# Health monitoring: Every 4 hours
0 6,10,14,18,22 * * * cd "$REPO_ROOT" && ./.automation/scripts/health_monitor.sh >/dev/null 2>&1

# Automation health check (for monitoring)
*/30 * * * * cd "$REPO_ROOT" && python3 .automation/scripts/check_automation_health.py --export .automation/logs/automation_status.json --json >/dev/null 2>&1

EOF
    
    crontab "$cron_file"
    rm "$cron_file"
    
    log "✅ Phase 1 enabled: Screenshot import + health monitoring"
    log ""
    log "📊 Scheduled tasks:"
    log "  • Screenshot import: Daily at 11:30 PM"
    log "  • Health monitoring: Every 4 hours (6 AM - 10 PM)"
    log "  • Status export: Every 30 minutes"
    log ""
    warn "⏰ OBSERVATION PERIOD: 24 hours"
    log ""
    log "Monitor with: python3 .automation/scripts/check_automation_health.py"
    log "Logs: .automation/logs/screenshot_import_*.log"
    log ""
    log "After 24 hours with zero issues, run:"
    log "  $0 phase2"
    
    if [[ -n "$backup_file" ]]; then
        log ""
        log "To rollback: crontab $backup_file"
    fi
}

# Phase 2: Add inbox processing
enable_phase2() {
    log "=========================================="
    log "PHASE 2: Add Inbox Processing"
    log "=========================================="
    
    backup_file=$(backup_crontab)
    
    local cron_file="/tmp/inneros_cron_phase2_$$"
    
    cat > "$cron_file" << EOF
# InnerOS Automation - Phase 2 (Screenshot + Inbox Processing)
# Enabled: $(date)
# Observation Period: 24 hours

# Daily screenshot import at 11:30 PM
30 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/automated_screenshot_import.sh >/dev/null 2>&1

# Supervised inbox processing: Monday, Wednesday, Friday at 6:00 AM
0 6 * * 1,3,5 cd "$REPO_ROOT" && ./.automation/scripts/supervised_inbox_processing.sh >/dev/null 2>&1

# Health monitoring: Every 4 hours
0 6,10,14,18,22 * * * cd "$REPO_ROOT" && ./.automation/scripts/health_monitor.sh >/dev/null 2>&1

# Automation health check (for monitoring)
*/30 * * * * cd "$REPO_ROOT" && python3 .automation/scripts/check_automation_health.py --export .automation/logs/automation_status.json --json >/dev/null 2>&1

EOF
    
    crontab "$cron_file"
    rm "$cron_file"
    
    log "✅ Phase 2 enabled: Screenshot + inbox processing"
    log ""
    log "📊 Scheduled tasks:"
    log "  • Screenshot import: Daily at 11:30 PM"
    log "  • Inbox processing: Mon/Wed/Fri at 6:00 AM"
    log "  • Health monitoring: Every 4 hours (6 AM - 10 PM)"
    log "  • Status export: Every 30 minutes"
    log ""
    warn "⏰ OBSERVATION PERIOD: 24 hours"
    log ""
    log "Monitor concurrent execution on Mon/Wed/Fri mornings!"
    log "Check: .automation/logs/automation_status.json"
    log ""
    log "After 24 hours with zero issues, run:"
    log "  $0 phase3"
    
    if [[ -n "$backup_file" ]]; then
        log ""
        log "To rollback: crontab $backup_file"
    fi
}

# Phase 3: Full automation
enable_phase3() {
    log "=========================================="
    log "PHASE 3: Full Automation"
    log "=========================================="
    
    backup_file=$(backup_crontab)
    
    local cron_file="/tmp/inneros_cron_phase3_$$"
    
    cat > "$cron_file" << EOF
# InnerOS Automation - Phase 3 (Full Automation)
# Enabled: $(date)
# Observation Period: 48 hours minimum

# Daily screenshot import at 11:30 PM
30 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/automated_screenshot_import.sh >/dev/null 2>&1

# Supervised inbox processing: Monday, Wednesday, Friday at 6:00 AM
0 6 * * 1,3,5 cd "$REPO_ROOT" && ./.automation/scripts/supervised_inbox_processing.sh >/dev/null 2>&1

# Weekly deep analysis: Sunday at 9:00 AM
0 9 * * 0 cd "$REPO_ROOT" && ./.automation/scripts/weekly_deep_analysis.sh >/dev/null 2>&1

# Health monitoring: Every 4 hours
0 6,10,14,18,22 * * * cd "$REPO_ROOT" && ./.automation/scripts/health_monitor.sh >/dev/null 2>&1

# Automation health check (for monitoring)
*/30 * * * * cd "$REPO_ROOT" && python3 .automation/scripts/check_automation_health.py --export .automation/logs/automation_status.json --json >/dev/null 2>&1

# Daily log cleanup (keep last 30 days)
0 2 * * * find "$REPO_ROOT/.automation/logs" -name "*.log" -mtime +30 -delete >/dev/null 2>&1

EOF
    
    crontab "$cron_file"
    rm "$cron_file"
    
    log "✅ Phase 3 enabled: Full automation"
    log ""
    log "📊 Complete schedule:"
    log "  • Screenshot import: Daily at 11:30 PM"
    log "  • Inbox processing: Mon/Wed/Fri at 6:00 AM"
    log "  • Weekly analysis: Sunday at 9:00 AM"
    log "  • Health monitoring: Every 4 hours (6 AM - 10 PM)"
    log "  • Status export: Every 30 minutes"
    log "  • Log cleanup: Daily at 2:00 AM (keep 30 days)"
    log ""
    warn "⏰ STABILITY CHECK: Monitor for 48 hours"
    log ""
    log "Success criteria:"
    log "  • Zero automation failures"
    log "  • No stale locks detected"
    log "  • CPU usage <5% average"
    log "  • All scheduled jobs completing successfully"
    log ""
    log "Monitor: python3 .automation/scripts/check_automation_health.py"
    log "View cron: crontab -l"
    
    if [[ -n "$backup_file" ]]; then
        log ""
        log "To rollback: crontab $backup_file"
    fi
}

# Show current status
show_status() {
    log "=========================================="
    log "CURRENT AUTOMATION STATUS"
    log "=========================================="
    
    if ! crontab -l > /dev/null 2>&1; then
        warn "No crontab configured"
        return
    fi
    
    log "Current crontab:"
    log ""
    crontab -l | grep -v '^#' | grep -v '^$' || echo "  (no active jobs)"
    log ""
    
    log "Health status:"
    python3 "$REPO_ROOT/.automation/scripts/check_automation_health.py"
}

# Main script
main() {
    local command="${1:-help}"
    
    case "$command" in
        phase1)
            enable_phase1
            ;;
        phase2)
            enable_phase2
            ;;
        phase3)
            enable_phase3
            ;;
        status)
            show_status
            ;;
        help|*)
            echo "Staged Automation Enablement - Issue #34"
            echo ""
            echo "Usage: $0 [phase1|phase2|phase3|status]"
            echo ""
            echo "Phases:"
            echo "  phase1  - Enable screenshot import only (24h observation)"
            echo "  phase2  - Add inbox processing (24h observation)"
            echo "  phase3  - Full automation (48h stability check)"
            echo "  status  - Show current status"
            echo ""
            echo "Safety: Always backs up crontab before changes"
            echo ""
            exit 0
            ;;
    esac
}

main "$@"
