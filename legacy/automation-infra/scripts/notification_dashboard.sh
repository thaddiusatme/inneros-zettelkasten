#!/usr/bin/env bash
# InnerOS Zettelkasten - Notification Dashboard
# Displays summary of automation activity and pending reviews
# Run manually to check automation status

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
LOG_DIR="$REPO_ROOT/.automation/logs"
REVIEW_DIR="$REPO_ROOT/.automation/review_queue"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
colored_echo() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

count_files() {
    local pattern="$1"
    find "$LOG_DIR" -name "$pattern" 2>/dev/null | wc -l | tr -d ' '
}

get_latest_file() {
    local pattern="$1"
    find "$LOG_DIR" -name "$pattern" 2>/dev/null | sort | tail -1
}

get_file_age_hours() {
    local file="$1"
    if [[ -f "$file" ]]; then
        echo $(( ($(date +%s) - $(stat -f %m "$file")) / 3600 ))
    else
        echo "N/A"
    fi
}

# Main dashboard display
show_dashboard() {
    clear
    colored_echo "$BLUE" "╔════════════════════════════════════════════════════════════════════════════════════════╗"
    colored_echo "$BLUE" "║                            📊 InnerOS Automation Dashboard                            ║"
    colored_echo "$BLUE" "╚════════════════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # System Status Overview
    colored_echo "$YELLOW" "🏥 SYSTEM STATUS"
    echo "─────────────────────────────────────────────────────────"
    
    # Check if automation is running
    if crontab -l 2>/dev/null | grep -q "inneros"; then
        colored_echo "$GREEN" "✅ Automation: ACTIVE (cron jobs installed)"
    else
        colored_echo "$RED" "❌ Automation: INACTIVE (no cron jobs found)"
    fi
    
    # Recent activity summary
    local screenshot_logs=$(count_files "screenshot_import_*.log")
    local processing_logs=$(count_files "supervised_processing_*.log")  
    local weekly_logs=$(count_files "weekly_analysis_*.log")
    local health_logs=$(count_files "health_monitor_*.log")
    
    echo "📊 Activity Summary (All Time):"
    echo "   Screenshot Imports: $screenshot_logs"
    echo "   Supervised Processing: $processing_logs"
    echo "   Weekly Analyses: $weekly_logs"
    echo "   Health Checks: $health_logs"
    echo ""
    
    # Recent Automation Activity
    colored_echo "$YELLOW" "🤖 RECENT AUTOMATION ACTIVITY"
    echo "─────────────────────────────────────────────────────────"
    
    # Screenshot imports
    local latest_screenshot=$(get_latest_file "screenshot_import_*.log")
    if [[ -n "$latest_screenshot" && -f "$latest_screenshot" ]]; then
        local age_hours=$(get_file_age_hours "$latest_screenshot")
        local success_count=$(grep -c "✅ Screenshot imported" "$latest_screenshot" 2>/dev/null || echo "0")
        colored_echo "$GREEN" "📸 Latest Screenshot Import: ${age_hours}h ago ($success_count screenshots)"
    else
        colored_echo "$YELLOW" "📸 Screenshot Import: No recent activity"
    fi
    
    # Supervised processing
    local latest_processing=$(get_latest_file "supervised_processing_*.log")
    if [[ -n "$latest_processing" && -f "$latest_processing" ]]; then
        local age_hours=$(get_file_age_hours "$latest_processing")
        local processed_count=$(grep -c "processed" "$latest_processing" 2>/dev/null || echo "0")
        colored_echo "$GREEN" "🧠 Latest Inbox Processing: ${age_hours}h ago ($processed_count notes)"
    else
        colored_echo "$YELLOW" "🧠 Inbox Processing: No recent activity"
    fi
    
    # Weekly analysis
    local latest_weekly=$(get_latest_file "weekly_analysis_*.log")
    if [[ -n "$latest_weekly" && -f "$latest_weekly" ]]; then
        local age_hours=$(get_file_age_hours "$latest_weekly")
        colored_echo "$GREEN" "📊 Latest Weekly Analysis: ${age_hours}h ago"
    else
        colored_echo "$YELLOW" "📊 Weekly Analysis: No recent activity"
    fi
    
    # Health monitoring
    local latest_health=$(get_latest_file "health_monitor_*.log")
    if [[ -n "$latest_health" && -f "$latest_health" ]]; then
        local age_hours=$(get_file_age_hours "$latest_health")
        if grep -q "ALERT" "$latest_health" 2>/dev/null; then
            colored_echo "$RED" "🚨 Latest Health Check: ${age_hours}h ago (ALERTS FOUND)"
        else
            colored_echo "$GREEN" "✅ Latest Health Check: ${age_hours}h ago (healthy)"
        fi
    else
        colored_echo "$YELLOW" "🏥 Health Monitoring: No recent activity"
    fi
    echo ""
    
    # Pending Reviews
    colored_echo "$YELLOW" "📋 PENDING HUMAN REVIEWS"
    echo "─────────────────────────────────────────────────────────"
    
    local review_count=$(find "$REVIEW_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    if [[ $review_count -gt 0 ]]; then
        colored_echo "$BLUE" "📋 $review_count review report(s) pending:"
        find "$REVIEW_DIR" -name "*.md" -type f 2>/dev/null | sort -r | head -5 | while read -r file; do
            local basename=$(basename "$file")
            local age_hours=$(get_file_age_hours "$file")
            echo "   • $basename (${age_hours}h ago)"
        done
        if [[ $review_count -gt 5 ]]; then
            echo "   ... and $((review_count - 5)) more"
        fi
    else
        colored_echo "$GREEN" "✅ No pending reviews"
    fi
    
    # Alert files
    local alert_count=$(find "$REVIEW_DIR" -name "ALERT_*.md" 2>/dev/null | wc -l | tr -d ' ')
    if [[ $alert_count -gt 0 ]]; then
        colored_echo "$RED" "🚨 $alert_count system alert(s) requiring attention!"
        find "$REVIEW_DIR" -name "ALERT_*.md" -type f 2>/dev/null | sort -r | head -3 | while read -r file; do
            local basename=$(basename "$file")
            local age_hours=$(get_file_age_hours "$file")
            echo "   • $basename (${age_hours}h ago)"
        done
    fi
    echo ""
    
    # Quick Actions
    colored_echo "$YELLOW" "⚡ QUICK ACTIONS"
    echo "─────────────────────────────────────────────────────────"
    echo "📋 View pending reviews: ls -la $REVIEW_DIR/"
    echo "📄 View recent logs: ls -la $LOG_DIR/ | tail -10"
    echo "🤖 Check automation status: crontab -l"
    echo "🔧 Run manual processing: $REPO_ROOT/.automation/scripts/process_inbox_workflow.sh"
    echo "🏥 Manual health check: $REPO_ROOT/.automation/scripts/health_monitor.sh"
    echo ""
    
    # Storage usage
    local log_size=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1 || echo "0B")
    local review_size=$(du -sh "$REVIEW_DIR" 2>/dev/null | cut -f1 || echo "0B")
    echo "💾 Storage: Logs ($log_size) | Reviews ($review_size)"
    echo ""
    
    colored_echo "$BLUE" "Last updated: $(date)"
}

# Interactive mode
interactive_mode() {
    while true; do
        show_dashboard
        echo ""
        colored_echo "$YELLOW" "🎮 Actions: [r]efresh | [l]ogs | [v]iew reviews | [q]uit"
        read -r -p "Choice: " choice
        
        case "$choice" in
            r|R) continue ;;
            l|L) 
                echo "Recent logs:"
                ls -la "$LOG_DIR" | tail -10
                read -r -p "Press Enter to continue..."
                ;;
            v|V)
                if [[ -d "$REVIEW_DIR" && $(find "$REVIEW_DIR" -name "*.md" | wc -l) -gt 0 ]]; then
                    echo "Opening review directory..."
                    open "$REVIEW_DIR"
                else
                    echo "No reviews pending."
                fi
                read -r -p "Press Enter to continue..."
                ;;
            q|Q) break ;;
            *) echo "Invalid choice. Try again." ;;
        esac
    done
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        interactive_mode
    else
        case "$1" in
            --status) show_dashboard ;;
            --help) 
                echo "Usage: $0 [--status|--help]"
                echo "  --status  Show dashboard once and exit"
                echo "  (no args) Interactive mode"
                ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    fi
}

main "$@"
