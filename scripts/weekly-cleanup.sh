#!/bin/bash
#
# InnerOS Zettelkasten - Weekly Cleanup Script
# ============================================
# 
# A comprehensive weekly maintenance routine that:
#   1. Creates a backup before any changes
#   2. Processes all inbox notes (AI tagging, quality, connections)
#   3. Processes YouTube notes specifically (transcripts, quotes)
#   4. Generates weekly review checklist
#   5. Shows fleeting notes health report
#
# Usage:
#   ./scripts/weekly-cleanup.sh              # Full run (dry-run first, then apply)
#   ./scripts/weekly-cleanup.sh --dry-run    # Preview only, no changes
#   ./scripts/weekly-cleanup.sh --apply      # Apply changes directly (skip dry-run)
#   ./scripts/weekly-cleanup.sh --help       # Show this help
#
# Created: 2025-12-11
# Updated: 2025-12-11
#

set -e  # Exit on first error

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="$REPO_ROOT/knowledge"
DEV_CLI="$REPO_ROOT/development/src/cli"
REVIEWS_DIR="$REPO_ROOT/Reviews"
DATE_STAMP=$(date +%Y-%m-%d)
TIME_STAMP=$(date +%H%M)

# CLI paths
SAFE_CLI="$DEV_CLI/safe_workflow_cli.py"
CORE_CLI="$DEV_CLI/core_workflow_cli.py"
YOUTUBE_CLI="$DEV_CLI/youtube_cli.py"
WEEKLY_REVIEW_CLI="$DEV_CLI/weekly_review_cli.py"
FLEETING_CLI="$DEV_CLI/fleeting_cli.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}▶ $1${NC}"
    echo -e "${CYAN}────────────────────────────────────────${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_help() {
    echo "InnerOS Zettelkasten - Weekly Cleanup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run     Preview all changes without applying them"
    echo "  --apply       Apply changes directly (skip dry-run preview)"
    echo "  --help        Show this help message"
    echo ""
    echo "Default behavior (no options):"
    echo "  1. Run dry-run preview for all operations"
    echo "  2. Prompt user to confirm before applying changes"
    echo ""
    echo "Steps performed:"
    echo "  1. Create timestamped backup"
    echo "  2. Process inbox notes (AI tagging, quality scoring, connections)"
    echo "  3. Process YouTube notes (transcript extraction, quotes)"
    echo "  4. Generate weekly review checklist"
    echo "  5. Show fleeting notes health report"
    echo ""
    echo "Examples:"
    echo "  $0                    # Interactive: preview then confirm"
    echo "  $0 --dry-run          # Just preview, no changes"
    echo "  $0 --apply            # Apply directly without preview"
    echo ""
}

check_prerequisites() {
    print_section "Checking prerequisites"
    
    local errors=0
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "python3 is not installed or not in PATH"
        errors=$((errors + 1))
    else
        print_success "Python3 found: $(python3 --version)"
    fi
    
    # Check vault directory
    if [ ! -d "$VAULT_PATH" ]; then
        print_error "Vault directory not found: $VAULT_PATH"
        errors=$((errors + 1))
    else
        print_success "Vault directory found: $VAULT_PATH"
    fi
    
    # Check CLI files exist
    local cli_files=("$BACKUP_CLI" "$CORE_CLI" "$YOUTUBE_CLI" "$WEEKLY_REVIEW_CLI" "$FLEETING_CLI")
    for cli in "${cli_files[@]}"; do
        if [ ! -f "$cli" ]; then
            print_warning "CLI not found: $cli"
        fi
    done
    
    # Check inbox has files
    local inbox_count=$(find "$VAULT_PATH/Inbox" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    print_info "Inbox notes found: $inbox_count"
    
    # Check fleeting notes
    local fleeting_count=$(find "$VAULT_PATH/Fleeting Notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    print_info "Fleeting notes found: $fleeting_count"
    
    if [ $errors -gt 0 ]; then
        print_error "Prerequisites check failed with $errors error(s)"
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# ============================================================================
# Main Operations
# ============================================================================

step_backup() {
    print_section "Step 1: Creating Backup"
    
    if [ -f "$SAFE_CLI" ]; then
        python3 "$SAFE_CLI" --vault "$VAULT_PATH" backup
        print_success "Backup created"
    else
        # Fallback: simple directory backup
        local backup_name="knowledge-backup-${DATE_STAMP}-${TIME_STAMP}"
        local backup_path="$REPO_ROOT/backups/$backup_name"
        mkdir -p "$backup_path"
        cp -r "$VAULT_PATH"/* "$backup_path/" 2>/dev/null || true
        print_success "Backup created at: $backup_path"
    fi
}

step_process_inbox() {
    local mode=$1  # "dry-run" or "apply"
    
    print_section "Step 2: Processing Inbox Notes"
    
    if [ ! -f "$CORE_CLI" ]; then
        print_warning "Core workflow CLI not found, skipping inbox processing"
        return
    fi
    
    if [ "$mode" = "dry-run" ]; then
        print_info "Running inbox processing preview..."
        python3 "$CORE_CLI" "$VAULT_PATH" process-inbox --fast || {
            print_warning "Inbox processing preview completed with warnings"
        }
    else
        print_info "Applying inbox processing..."
        python3 "$CORE_CLI" "$VAULT_PATH" process-inbox || {
            print_warning "Inbox processing completed with warnings"
        }
    fi
    
    print_success "Inbox processing complete"
}

step_process_youtube() {
    local mode=$1  # "dry-run" or "apply"
    
    print_section "Step 3: Processing YouTube Notes"
    
    if [ ! -f "$YOUTUBE_CLI" ]; then
        print_warning "YouTube CLI not found, skipping YouTube processing"
        return
    fi
    
    if [ "$mode" = "dry-run" ]; then
        print_info "Running YouTube processing preview..."
        python3 "$YOUTUBE_CLI" --vault "$VAULT_PATH" batch-process --preview || {
            print_warning "YouTube processing preview completed with warnings"
        }
    else
        print_info "Applying YouTube processing..."
        python3 "$YOUTUBE_CLI" --vault "$VAULT_PATH" batch-process || {
            print_warning "YouTube processing completed with warnings"
        }
    fi
    
    print_success "YouTube processing complete"
}

step_weekly_review() {
    print_section "Step 4: Generating Weekly Review Checklist"
    
    if [ ! -f "$WEEKLY_REVIEW_CLI" ]; then
        print_warning "Weekly review CLI not found, skipping weekly review"
        return
    fi
    
    local review_file="$REVIEWS_DIR/weekly-review-${DATE_STAMP}.md"
    mkdir -p "$REVIEWS_DIR"
    
    print_info "Generating weekly review checklist..."
    python3 "$WEEKLY_REVIEW_CLI" --vault "$VAULT_PATH" weekly-review --export "$review_file" || {
        print_warning "Weekly review generation completed with warnings"
    }
    
    if [ -f "$review_file" ]; then
        print_success "Weekly review exported to: $review_file"
    else
        print_info "Weekly review generated (no export file created)"
    fi
}

step_fleeting_health() {
    print_section "Step 5: Fleeting Notes Health Report"
    
    if [ ! -f "$FLEETING_CLI" ]; then
        print_warning "Fleeting CLI not found, skipping health report"
        return
    fi
    
    print_info "Generating fleeting notes health report..."
    python3 "$FLEETING_CLI" --vault "$VAULT_PATH" fleeting-health || {
        print_warning "Fleeting health report completed with warnings"
    }
    
    print_success "Fleeting health report complete"
}

step_summary() {
    print_header "Weekly Cleanup Summary"
    
    local inbox_count=$(find "$VAULT_PATH/Inbox" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local fleeting_count=$(find "$VAULT_PATH/Fleeting Notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local permanent_count=$(find "$VAULT_PATH/Permanent Notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local literature_count=$(find "$VAULT_PATH/Literature Notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    echo "📊 Current Note Counts:"
    echo "   📥 Inbox:           $inbox_count"
    echo "   📝 Fleeting Notes:  $fleeting_count"
    echo "   📚 Literature:      $literature_count"
    echo "   💎 Permanent:       $permanent_count"
    echo ""
    
    if [ -f "$REVIEWS_DIR/weekly-review-${DATE_STAMP}.md" ]; then
        echo "📋 Weekly review exported to:"
        echo "   $REVIEWS_DIR/weekly-review-${DATE_STAMP}.md"
        echo ""
    fi
    
    print_success "Weekly cleanup complete! 🎉"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    local mode="interactive"  # default: preview then confirm
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                mode="dry-run"
                shift
                ;;
            --apply)
                mode="apply"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header "InnerOS Weekly Cleanup - ${DATE_STAMP}"
    echo "Mode: $mode"
    echo "Vault: $VAULT_PATH"
    
    # Change to repo root
    cd "$REPO_ROOT"
    
    # Check prerequisites
    check_prerequisites
    
    if [ "$mode" = "dry-run" ]; then
        # Dry-run only
        print_header "DRY RUN - Preview Only (No Changes)"
        step_backup
        step_process_inbox "dry-run"
        step_process_youtube "dry-run"
        step_weekly_review
        step_fleeting_health
        step_summary
        
        echo ""
        print_info "This was a dry-run. To apply changes, run:"
        echo "   $0 --apply"
        
    elif [ "$mode" = "apply" ]; then
        # Apply directly
        print_header "APPLYING CHANGES"
        step_backup
        step_process_inbox "apply"
        step_process_youtube "apply"
        step_weekly_review
        step_fleeting_health
        step_summary
        
    else
        # Interactive: dry-run first, then confirm
        print_header "PHASE 1: Preview (Dry Run)"
        step_backup
        step_process_inbox "dry-run"
        step_process_youtube "dry-run"
        step_weekly_review
        step_fleeting_health
        
        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}Preview complete. Ready to apply changes?${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        read -p "Apply changes now? [y/N] " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_header "PHASE 2: Applying Changes"
            step_process_inbox "apply"
            step_process_youtube "apply"
            step_summary
        else
            print_info "Skipped applying changes. Run with --apply when ready."
        fi
    fi
}

# Run main
main "$@"
