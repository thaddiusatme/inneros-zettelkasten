#!/usr/bin/env bash
# InnerOS Zettelkasten - Automated Screenshot Import (Tier 1: Fully Safe)
# Runs unattended to import Samsung screenshots with OCR fallback protection
# Safe for automation: only creates new notes, never modifies existing content

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
KNOWLEDGE_DIR="$REPO_ROOT/knowledge/"
PYTHON="$REPO_ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    echo "[ERROR] Missing executable venv python at: $PYTHON" >&2
    echo "[ERROR] Run 'make setup' to create the repo venv." >&2
    exit 1
fi
# Dedicated CLIs (ADR-004 CLI Layer Extraction - Issue #39)
CORE_CLI="$PYTHON $REPO_ROOT/development/src/cli/core_workflow_cli.py"
BACKUP_CLI="$PYTHON $REPO_ROOT/development/src/cli/backup_cli.py"
SCREENSHOT_CLI="$PYTHON $REPO_ROOT/development/src/cli/screenshot_cli.py"
LOG_DIR="$REPO_ROOT/.automation/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="$LOG_DIR/screenshot_import_$TIMESTAMP.log"

# Automation settings
MAX_RUNTIME=300  # 5 minutes max runtime
NOTIFICATION_EMAIL=""  # Set if you want email notifications
SLACK_WEBHOOK=""       # Set if you want Slack notifications

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Timeout wrapper for safety
run_with_timeout() {
    local cmd="$1"
    local timeout_sec="$2"
    
    log "Running with ${timeout_sec}s timeout: $cmd"
    # Use gtimeout if available (from coreutils), otherwise skip timeout
    if command -v gtimeout >/dev/null 2>&1; then
        if gtimeout "$timeout_sec" bash -c "$cmd" >> "$LOG_FILE" 2>&1; then
            return 0
        else
            log_error "Command timed out after ${timeout_sec}s"
            return 1
        fi
    elif command -v timeout >/dev/null 2>&1; then
        if timeout "$timeout_sec" bash -c "$cmd" >> "$LOG_FILE" 2>&1; then
            return 0
        else
            log_error "Command timed out after ${timeout_sec}s"
            return 1
        fi
    else
        log "No timeout command available - running without timeout protection"
        if bash -c "$cmd" >> "$LOG_FILE" 2>&1; then
            return 0
        else
            log_error "Command failed"
            return 1
        fi
    fi
}

# Send notifications (optional)
send_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "$NOTIFICATION_EMAIL" ]]; then
        echo "$message" | mail -s "InnerOS Screenshot Import: $status" "$NOTIFICATION_EMAIL" || true
    fi
    
    if [[ -n "$SLACK_WEBHOOK" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"📸 InnerOS Screenshot Import: $status\\n$message\"}" \
            "$SLACK_WEBHOOK" || true
    fi
}

# Main automation logic
main() {
    cd "$REPO_ROOT"
    
    log "🤖 Starting automated screenshot import"
    log "Repository: $REPO_ROOT"
    log "Knowledge base: $KNOWLEDGE_DIR"
    
    # Step 1: System health check (30s timeout)
    log "📊 Checking system health..."
    if ! run_with_timeout "$CORE_CLI '$KNOWLEDGE_DIR' status" 30; then
        log_error "System health check failed or timed out"
        send_notification "FAILED" "System health check failed. Check logs: $LOG_FILE"
        exit 1
    fi
    
    # Step 2: Create backup (safety first, 60s timeout)  
    log "💾 Creating safety backup..."
    if ! run_with_timeout "$BACKUP_CLI --vault '$KNOWLEDGE_DIR' backup" 60; then
        log_error "Backup creation failed"
        send_notification "FAILED" "Backup creation failed. Check logs: $LOG_FILE"
        exit 1
    fi
    
    # Step 3: Import screenshots with built-in fallback handling (180s timeout)
    log "📸 Importing Samsung screenshots with progress tracking..."
    screenshot_cmd="$SCREENSHOT_CLI --vault '$KNOWLEDGE_DIR' process --progress"
    
    if run_with_timeout "$screenshot_cmd" 180; then
        screenshot_count=$(grep -c "✅ Screenshot imported" "$LOG_FILE" || echo "0")
        log "✅ Screenshot import completed successfully ($screenshot_count screenshots)"
        send_notification "SUCCESS" "Successfully imported $screenshot_count screenshots. Log: $LOG_FILE"
    else
        log_error "Screenshot import failed or timed out"
        send_notification "FAILED" "Screenshot import failed. Check logs: $LOG_FILE"
        exit 1
    fi
    
    # Step 4: Generate summary stats
    log "📈 Generating summary..."
    total_notes=$(find "$KNOWLEDGE_DIR" -name "*.md" | wc -l | tr -d ' ')
    inbox_notes=$(find "$KNOWLEDGE_DIR/Inbox" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    log "📊 Summary: $total_notes total notes, $inbox_notes in inbox"
    log "🏁 Automated screenshot import completed successfully"
}

# Trap to ensure we always log completion
trap 'log "🔚 Script ended with exit code $?"' EXIT

# Run main function
main "$@"
