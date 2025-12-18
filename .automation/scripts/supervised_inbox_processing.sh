#!/usr/bin/env bash
# InnerOS Zettelkasten - Supervised Inbox Processing (Tier 2: Supervised Automation)
# Enhances inbox notes with AI analysis, queues results for human review
# Safe for automation: enhances metadata without changing core content

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
CONNECTIONS_CLI="$PYTHON $REPO_ROOT/development/src/cli/connections_demo.py"
LOG_DIR="$REPO_ROOT/.automation/logs"
REVIEW_DIR="$REPO_ROOT/.automation/review_queue"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="$LOG_DIR/supervised_processing_$TIMESTAMP.log"
REVIEW_REPORT="$REVIEW_DIR/inbox_analysis_$TIMESTAMP.md"

# Automation settings  
MAX_RUNTIME=600  # 10 minutes max runtime
MIN_QUALITY_THRESHOLD=0.7  # Only highlight high-quality notes for promotion

# Ensure directories exist
mkdir -p "$LOG_DIR" "$REVIEW_DIR"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Timeout wrapper
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

# Generate human-readable review report
generate_review_report() {
    local report_file="$1"
    
    cat > "$report_file" << EOF
# 📋 Inbox Processing Review Report
**Generated**: $(date '+%Y-%m-%d %H:%M:%S')  
**Log File**: \`$LOG_FILE\`

## 🎯 High-Priority Items for Review

### Notes Recommended for Promotion (Quality ≥ $MIN_QUALITY_THRESHOLD)
EOF

    # Extract high-quality notes from log (this would need to be implemented in CLI)
    log "📝 Generating review report: $report_file"
    
    cat >> "$report_file" << EOF

### New Connections Discovered
_AI-suggested semantic connections between notes_

### Processing Summary
- **Total Notes Processed**: [Extract from log]
- **Tags Added**: [Extract from log]  
- **Quality Scores Updated**: [Extract from log]
- **Connections Found**: [Extract from log]

## 🔄 Next Steps
- [ ] Review high-quality notes for promotion to Permanent
- [ ] Validate AI-suggested connections
- [ ] Consider creating new MOCs from connection clusters

## 📊 Full Processing Log
\`\`\`
$(tail -50 "$LOG_FILE")
\`\`\`

---
*This report was generated automatically. Review and take action as needed.*
EOF
}

# Send notification with review report
send_notification() {
    local status="$1"
    local message="$2"
    
    # Create notification with link to review report
    local notification_msg="$message

📋 Review Report: $REVIEW_REPORT
📄 Full Log: $LOG_FILE

Review high-priority items when convenient."
    
    log "$notification_msg"
    
    # TODO: Add email/Slack notifications if configured
    # echo "$notification_msg" | mail -s "InnerOS Inbox Processing: $status" "$EMAIL"
}

# Main automation logic
main() {
    cd "$REPO_ROOT"
    
    log "🤖 Starting supervised inbox processing"
    log "Repository: $REPO_ROOT"
    log "Knowledge base: $KNOWLEDGE_DIR"
    
    # Step 1: Quick health check
    log "📊 Checking system health..."
    if ! run_with_timeout "$CORE_CLI '$KNOWLEDGE_DIR' status" 30; then
        log_error "System health check failed"
        send_notification "FAILED" "System health check failed"
        exit 1
    fi
    
    # Step 2: Safety backup
    log "💾 Creating safety backup..."  
    if ! run_with_timeout "$BACKUP_CLI --vault '$KNOWLEDGE_DIR' backup" 60; then
        log_error "Backup creation failed"
        send_notification "FAILED" "Backup creation failed"
        exit 1
    fi
    
    # Step 3: Process inbox with AI enhancement (no promotion, just analysis)
    log "🧠 Processing inbox with AI enhancement..."
    process_cmd="$CORE_CLI '$KNOWLEDGE_DIR' process-inbox"
    
    if run_with_timeout "$process_cmd" 300; then
        notes_processed=$(grep -c "processed" "$LOG_FILE" || echo "0")
        log "✅ Inbox processing completed ($notes_processed notes processed)"
    else
        log_error "Inbox processing failed or timed out"
        send_notification "FAILED" "Inbox processing failed"
        exit 1
    fi
    
    # Step 4: Generate connection suggestions
    log "🔗 Discovering semantic connections..."
    if run_with_timeout "$CONNECTIONS_CLI '$KNOWLEDGE_DIR' --corpus-dir '$KNOWLEDGE_DIR'" 120; then
        log "✅ Connection discovery completed"
    else
        log_error "Connection discovery failed or timed out (non-critical)"
    fi
    
    # Step 5: Generate human review report
    generate_review_report "$REVIEW_REPORT"
    
    # Step 6: Summary notification  
    total_notes=$(find "$KNOWLEDGE_DIR" -name "*.md" | wc -l | tr -d ' ')
    inbox_notes=$(find "$KNOWLEDGE_DIR/Inbox" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    send_notification "SUCCESS" "Processed $notes_processed notes. $inbox_notes remain in inbox. Review queued."
    
    log "📊 Summary: $total_notes total notes, $inbox_notes in inbox"
    log "🏁 Supervised processing completed successfully"
}

# Trap to ensure completion logging
trap 'log "🔚 Script ended with exit code $?"' EXIT

# Run main function
main "$@"
