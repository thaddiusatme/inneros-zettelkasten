#!/usr/bin/env bash
# InnerOS Zettelkasten - System Health Monitor
# Lightweight monitoring that runs every 4 hours to detect issues early
# Sends alerts only when problems are detected

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
KNOWLEDGE_DIR="$REPO_ROOT/knowledge/"
CLI="python3 $REPO_ROOT/development/src/cli/workflow_demo.py"
LOG_DIR="$REPO_ROOT/.automation/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="$LOG_DIR/health_monitor_$TIMESTAMP.log"

# Health thresholds
MAX_INBOX_SIZE=50      # Alert if inbox grows beyond 50 notes
MAX_LOG_SIZE_MB=100    # Alert if log directory exceeds 100MB
MIN_DISK_SPACE_GB=5    # Alert if available space < 5GB
MAX_BACKUP_AGE_DAYS=7  # Alert if no backup in 7 days

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1" | tee -a "$LOG_FILE" >&2
}

# Send alert notification (only when issues detected)
send_alert() {
    local issue="$1"
    local details="$2"
    
    # TODO: Configure email/Slack webhook
    log "🚨 ALERT: $issue - $details"
    
    # For now, create alert file in review queue
    echo "# 🚨 InnerOS System Alert

**Issue**: $issue  
**Details**: $details  
**Time**: $(date)  
**Log**: $LOG_FILE

Investigate and resolve when convenient." > "$REPO_ROOT/.automation/review_queue/ALERT_$(date +%Y%m%d_%H%M).md"
}

# Check inbox size
check_inbox_size() {
    local inbox_count=$(find "$KNOWLEDGE_DIR/Inbox" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    if [[ $inbox_count -gt $MAX_INBOX_SIZE ]]; then
        send_alert "Large inbox detected" "Inbox contains $inbox_count notes (threshold: $MAX_INBOX_SIZE). Consider running supervised processing."
        return 1
    fi
    
    log "✅ Inbox size OK: $inbox_count notes"
    return 0
}

# Check log directory size
check_log_size() {
    local log_size_mb=$(du -sm "$LOG_DIR" 2>/dev/null | cut -f1 || echo "0")
    
    if [[ $log_size_mb -gt $MAX_LOG_SIZE_MB ]]; then
        send_alert "Log directory too large" "Log directory is ${log_size_mb}MB (threshold: ${MAX_LOG_SIZE_MB}MB). Consider running log cleanup."
        return 1
    fi
    
    log "✅ Log size OK: ${log_size_mb}MB"
    return 0
}

# Check available disk space
check_disk_space() {
    local available_gb=$(df -BG "$REPO_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [[ $available_gb -lt $MIN_DISK_SPACE_GB ]]; then
        send_alert "Low disk space" "Only ${available_gb}GB available (threshold: ${MIN_DISK_SPACE_GB}GB). Free up space soon."
        return 1
    fi
    
    log "✅ Disk space OK: ${available_gb}GB available"
    return 0
}

# Check backup recency
check_backup_recency() {
    # Backups are created by the CLI using the knowledge directory basename (e.g., 'knowledge')
    local backup_root_name
    backup_root_name="$(basename "$KNOWLEDGE_DIR")"
    local backup_dir="$HOME/backups/$backup_root_name"
    
    if [[ ! -d "$backup_dir" ]]; then
        send_alert "No backup directory" "Backup directory not found: $backup_dir. Create initial backup."
        return 1
    fi
    
    # Match any timestamped backup for this vault (e.g., knowledge-YYYYMMDD-HHMMSS)
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "${backup_root_name}-*" | sort | tail -1)
    
    if [[ -z "$latest_backup" ]]; then
        send_alert "No backups found" "No backups found in $backup_dir. Create initial backup."
        return 1
    fi
    
    local backup_age_days=$((($(date +%s) - $(stat -f %m "$latest_backup")) / 86400))
    
    if [[ $backup_age_days -gt $MAX_BACKUP_AGE_DAYS ]]; then
        send_alert "Backup too old" "Latest backup is ${backup_age_days} days old (threshold: ${MAX_BACKUP_AGE_DAYS} days). Create fresh backup."
        return 1
    fi
    
    log "✅ Backup recency OK: ${backup_age_days} days old"
    return 0
}

# Quick system responsiveness check (macOS-compatible timeout)
check_system_responsiveness() {
    local start_time=$(date +%s)
    local ok=1
    if command -v gtimeout >/dev/null 2>&1; then
        if gtimeout 15 "$CLI" "$KNOWLEDGE_DIR" --status >/dev/null 2>&1; then ok=0; fi
    elif command -v timeout >/dev/null 2>&1; then
        if timeout 15 "$CLI" "$KNOWLEDGE_DIR" --status >/dev/null 2>&1; then ok=0; fi
    else
        # No timeout available; run directly
        if "$CLI" "$KNOWLEDGE_DIR" --status >/dev/null 2>&1; then ok=0; fi
    fi
    if [[ $ok -eq 0 ]]; then
        local duration=$(($(date +%s) - start_time))
        log "✅ System responsive: ${duration}s"
        return 0
    else
        send_alert "System unresponsive" "System status check failed or timed out after 15s. Check for hanging processes."
        return 1
    fi
}

# Main health monitoring logic
main() {
    cd "$REPO_ROOT"
    
    log "🏥 Starting health monitoring check"
    
    local issues=0
    
    # Run all health checks
    check_inbox_size || ((issues++))
    check_log_size || ((issues++))
    check_disk_space || ((issues++))
    check_backup_recency || ((issues++))
    check_system_responsiveness || ((issues++))
    
    # Summary
    if [[ $issues -eq 0 ]]; then
        log "✅ All health checks passed - system healthy"
    else
        log "⚠️ Health monitoring found $issues issue(s) - check alerts"
    fi
    
    # Clean up old health logs (keep last 7 days)
    find "$LOG_DIR" -name "health_monitor_*.log" -mtime +7 -delete 2>/dev/null || true
}

# Trap to ensure completion logging
trap 'log "🔚 Health monitoring ended with exit code $?"' EXIT

# Run main function (silent unless issues found)
main "$@" 2>/dev/null || echo "Health monitoring detected issues - check $LOG_FILE"
