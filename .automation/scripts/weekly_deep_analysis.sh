#!/usr/bin/env bash
#
# Weekly Deep Analysis Workflow
#
# Vault Configuration:
# - Uses centralized vault config via development/src imports
# - Automatically handles all knowledge/ directory paths
# - No hardcoded paths - all paths relative to repo root
# - Compatible with knowledge/ subdirectory structure
# - See: .automation/README.md for vault config integration details
#
# InnerOS Zettelkasten - Weekly Deep Analysis (Tier 3: Human-Gated)
# Comprehensive weekly analysis with human review queue generation
# Creates detailed reports for human decision-making on promotions and organization

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
KNOWLEDGE_DIR="$REPO_ROOT/knowledge/"
CLI="python3 $REPO_ROOT/development/src/cli/workflow_demo.py"
LOG_DIR="$REPO_ROOT/.automation/logs"
REVIEW_DIR="$REPO_ROOT/.automation/review_queue"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="$LOG_DIR/weekly_analysis_$TIMESTAMP.log"
ANALYSIS_REPORT="$REVIEW_DIR/weekly_analysis_$TIMESTAMP.md"

# Weekly analysis settings
MIN_QUALITY_THRESHOLD=0.7
STALE_THRESHOLD_DAYS=90
ENHANCED_METRICS_EXPORT="$REVIEW_DIR/weekly_metrics_$TIMESTAMP.md"

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

# Generate comprehensive weekly analysis report
generate_weekly_report() {
    local report_file="$1"
    
    cat > "$report_file" << EOF
# 📊 Weekly Knowledge Base Analysis Report
**Generated**: $(date '+%Y-%m-%d %H:%M:%S')  
**Analysis Period**: Last 7 days  
**Log File**: \`$LOG_FILE\`

## 🎯 High-Priority Human Decisions Required

### 🚀 Notes Ready for Promotion (Quality ≥ $MIN_QUALITY_THRESHOLD)
*These fleeting notes have achieved high quality and should be considered for promotion to permanent status*

EOF

    # Extract promotion candidates from fleeting triage
    if [[ -f "$REVIEW_DIR/fleeting_triage_$TIMESTAMP.md" ]]; then
        grep -A 20 "High Quality" "$REVIEW_DIR/fleeting_triage_$TIMESTAMP.md" >> "$report_file" || true
    fi

    cat >> "$report_file" << EOF

### 🔗 New Semantic Connections Discovered
*AI-suggested connections between existing notes that could strengthen your knowledge graph*

EOF

    # Extract connection suggestions from link analysis
    if [[ -f "$REVIEW_DIR/link_suggestions_$TIMESTAMP.md" ]]; then
        grep -A 10 "Suggested Links" "$REVIEW_DIR/link_suggestions_$TIMESTAMP.md" >> "$report_file" || true
    fi

    cat >> "$report_file" << EOF

### 📁 Directory Organization Recommendations
*Notes that may be in the wrong directories based on their type and content*

### ⚠️ Stale Notes Requiring Attention
*Notes not modified in $STALE_THRESHOLD_DAYS+ days that may need updating or archiving*

## 📈 Weekly Knowledge Metrics

### Note Creation & Processing
- **Total Notes**: [Extract from status]
- **Inbox Processing**: [Extract from supervised processing]
- **Weekly Captures**: [Extract from screenshot imports]
- **Quality Improvements**: [Extract from AI enhancement]

### Knowledge Graph Growth
- **New Connections**: [Extract from link suggestions]
- **Orphaned Notes**: [Extract from enhanced metrics]
- **Link Density**: [Extract from enhanced metrics]

### Content Quality Evolution
- **Promotion Rate**: X% of fleeting notes promoted this week
- **AI Enhancement Success**: X% improvement in average quality scores
- **Tag Organization**: X problematic tags resolved

## 🔄 Recommended Actions This Week

### High Priority (Complete First)
- [ ] Review and promote high-quality fleeting notes
- [ ] Validate and implement suggested semantic connections
- [ ] Address stale notes (archive, update, or delete)

### Medium Priority (Time Permitting)  
- [ ] Organize misplaced notes into correct directories
- [ ] Update outdated permanent notes with fresh insights
- [ ] Review and clean up problematic tags

### Low Priority (Future Weeks)
- [ ] Expand thin permanent notes with more content
- [ ] Create MOCs for emerging topic clusters
- [ ] Archive or delete truly obsolete content

## 📊 Detailed Metrics Report
*See attached: \`$ENHANCED_METRICS_EXPORT\`*

## 📄 Processing Logs Summary
\`\`\`
$(tail -30 "$LOG_FILE")
\`\`\`

---
*This analysis was generated automatically. Human review and decision-making required for all recommendations.*
EOF
}

# Send weekly summary notification
send_weekly_notification() {
    local status="$1"
    local summary="$2"
    
    local notification_msg="📊 InnerOS Weekly Analysis: $status

$summary

📋 Full Analysis Report: $ANALYSIS_REPORT
📊 Metrics Report: $ENHANCED_METRICS_EXPORT
📄 Full Log: $LOG_FILE

Review recommendations and take action when convenient."
    
    log "$notification_msg"
    # TODO: Add email/Slack notifications if configured
}

# Main weekly analysis logic
main() {
    cd "$REPO_ROOT"
    
    log "📊 Starting weekly deep analysis"
    log "Repository: $REPO_ROOT"
    log "Knowledge base: $KNOWLEDGE_DIR"
    
    # Step 1: System health check
    log "🏥 Checking system health..."
    if ! run_with_timeout "$CLI '$KNOWLEDGE_DIR' --status" 30; then
        log_error "System health check failed"
        send_weekly_notification "FAILED" "System health check failed"
        exit 1
    fi
    
    # Step 2: Safety backup
    log "💾 Creating weekly backup..."
    if ! run_with_timeout "$CLI '$KNOWLEDGE_DIR' --backup" 120; then
        log_error "Weekly backup failed"
        send_weekly_notification "FAILED" "Weekly backup failed"
        exit 1
    fi
    
    # Step 3: Fleeting note triage analysis
    log "📝 Analyzing fleeting notes for promotion candidates..."
    triage_export="$REVIEW_DIR/fleeting_triage_$TIMESTAMP.md"
    if run_with_timeout "$CLI '$KNOWLEDGE_DIR' --fleeting-triage --min-quality $MIN_QUALITY_THRESHOLD --export '$triage_export'" 180; then
        log "✅ Fleeting triage completed"
    else
        log_error "Fleeting triage failed (non-critical)"
    fi
    
    # Step 4: Enhanced metrics with orphaned/stale detection
    log "📊 Generating enhanced knowledge metrics..."
    if run_with_timeout "$CLI '$KNOWLEDGE_DIR' --enhanced-metrics --export '$ENHANCED_METRICS_EXPORT'" 120; then
        log "✅ Enhanced metrics completed"
    else
        log_error "Enhanced metrics failed (non-critical)"
    fi
    
    # Step 5: Semantic connection discovery
    log "🔗 Discovering new semantic connections..."
    links_export="$REVIEW_DIR/link_suggestions_$TIMESTAMP.md"
    if run_with_timeout "$CLI '$KNOWLEDGE_DIR' --suggest-links --export '$links_export'" 300; then
        log "✅ Link suggestions completed"
    else
        log_error "Link suggestions failed (non-critical)"
    fi
    
    # Step 6: Generate comprehensive weekly report
    generate_weekly_report "$ANALYSIS_REPORT"
    
    # Step 7: Generate summary stats
    total_notes=$(find "$KNOWLEDGE_DIR" -name "*.md" | wc -l | tr -d ' ')
    inbox_notes=$(find "$KNOWLEDGE_DIR/Inbox" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    fleeting_notes=$(find "$KNOWLEDGE_DIR/Fleeting Notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    permanent_notes=$(find "$KNOWLEDGE_DIR/Permanent Notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    weekly_summary="Total: $total_notes notes | Inbox: $inbox_notes | Fleeting: $fleeting_notes | Permanent: $permanent_notes
📋 Analysis report generated with promotion candidates and connection suggestions."
    
    send_weekly_notification "SUCCESS" "$weekly_summary"
    
    log "📊 Weekly analysis completed successfully"
    log "📋 Report: $ANALYSIS_REPORT"
    log "📊 Metrics: $ENHANCED_METRICS_EXPORT"
}

# Trap to ensure completion logging
trap 'log "🔚 Weekly analysis ended with exit code $?"' EXIT

# Run main function
main "$@"
