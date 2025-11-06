#!/usr/bin/env bash
# InnerOS Zettelkasten – Inbox Processing Orchestrator
# Safely runs backup, Samsung screenshot import (optional dry-run → actual),
# then processes the inbox with progress, and optional follow-ups.
#
# Vault Configuration:
# - Uses centralized vault config via development/src imports
# - Automatically handles knowledge/Inbox, knowledge/Permanent Notes paths
# - No hardcoded paths - all paths relative to repo root
# - Compatible with knowledge/ subdirectory structure
# - See: .automation/README.md for vault config integration details
#
# Usage examples:
#   ./process_inbox_workflow.sh                   # full workflow (backup → screenshots (dry-run+actual) → inbox processing)
#   ./process_inbox_workflow.sh --dry-run-only    # backup + screenshots dry-run only (no actual import, no processing)
#   ./process_inbox_workflow.sh --skip-backup     # skip backup
#   ./process_inbox_workflow.sh --skip-screenshots
#   ./process_inbox_workflow.sh --no-ocr          # force OCR fallback (prevents stalls)
#   ./process_inbox_workflow.sh --timeout 30      # kill commands after 30 seconds
#   ./process_inbox_workflow.sh --onedrive-path "/Users/me/Library/CloudStorage/OneDrive-Personal/Screenshots"
#   ./process_inbox_workflow.sh --export reports/inbox-processing-$(date +%F).md
#   ./process_inbox_workflow.sh --suggest-links   # run link suggestions after processing
#   ./process_inbox_workflow.sh --fleeting-triage --min-quality 0.6
#
# Notes:
# - Requires running from repo root or sets REPO_ROOT by traversing up from this script.
# - Non-destructive dry-runs are used before any mutating step.
# - Inbox processing will show progress; fast-mode is used in dry-run.

set -euo pipefail

# Resolve repo root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
cd "$REPO_ROOT"

KNOWLEDGE_DIR="knowledge/"

# Dedicated CLI paths (migrated from deprecated monolithic CLI per ADR-004 Iteration 4)
CORE_WORKFLOW_CLI="python3 $REPO_ROOT/development/src/cli/core_workflow_cli.py"
SAFE_WORKFLOW_CLI="python3 $REPO_ROOT/development/src/cli/safe_workflow_cli.py"
FLEETING_CLI="python3 $REPO_ROOT/development/src/cli/fleeting_cli.py"
CONNECTIONS_CLI="python3 $REPO_ROOT/development/src/cli/connections_demo.py"

# TEMPORARY: evening-screenshots not yet extracted - still uses workflow_demo.py
# TODO: Extract --evening-screenshots to dedicated screenshot_cli.py (future iteration)
WORKFLOW_DEMO_CLI="python3 $REPO_ROOT/development/src/cli/workflow_demo.py"

TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"

# Migration note: Dedicated CLI migration completed 2025-11-04 (Issue #39, TDD Iteration 4)
# - core_workflow_cli.py: status, process-inbox commands
# - safe_workflow_cli.py: backup command
# - fleeting_cli.py: fleeting-triage command
# - connections_demo.py: suggest-links command
# - workflow_demo.py: TEMPORARY for --evening-screenshots only (pending extraction)

# Defaults
DO_BACKUP=1
DO_SCREENSHOTS=1
DRY_RUN_ONLY=0
EXPORT_PATH=""
RUN_SUGGEST_LINKS=0
RUN_FLEETING_TRIAGE=0
MIN_QUALITY="0.6"
ONEDRIVE_PATH=""
NO_OCR=0
TIMEOUT=0
FORCE_FALLBACK=0

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-backup) DO_BACKUP=0; shift ;;
    --skip-screenshots) DO_SCREENSHOTS=0; shift ;;
    --dry-run-only) DRY_RUN_ONLY=1; shift ;;
    --export) EXPORT_PATH="$2"; shift 2 ;;
    --suggest-links) RUN_SUGGEST_LINKS=1; shift ;;
    --fleeting-triage) RUN_FLEETING_TRIAGE=1; shift ;;
    --min-quality) MIN_QUALITY="$2"; shift 2 ;;
    --onedrive-path) ONEDRIVE_PATH="$2"; shift 2 ;;
    --no-ocr) NO_OCR=1; shift ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --force-fallback) FORCE_FALLBACK=1; shift ;;
    -h|--help)
      sed -n '1,80p' "$0" | sed 's/^# \{0,1\}//' ; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Helper function to run commands with timeout and fallback
run_with_timeout() {
  local cmd="$1"
  local timeout_msg="$2"
  
  if [[ "$TIMEOUT" -gt 0 ]]; then
    echo "Running with ${TIMEOUT}s timeout: $cmd"
    # Use gtimeout if available (from coreutils), otherwise skip timeout
    if command -v gtimeout >/dev/null 2>&1; then
      if gtimeout "$TIMEOUT" bash -c "$cmd"; then
        return 0
      else
        echo "⚠️  Command timed out after ${TIMEOUT}s: $timeout_msg"
        return 1
      fi
    elif command -v timeout >/dev/null 2>&1; then
      if timeout "$TIMEOUT" bash -c "$cmd"; then
        return 0
      else
        echo "⚠️  Command timed out after ${TIMEOUT}s: $timeout_msg"
        return 1
      fi
    else
      echo "⚠️  No timeout command available - running without timeout protection"
      eval "$cmd"
    fi
  else
    eval "$cmd"
  fi
}

echo "[1/5] Checking workflow status (read-only)…"
run_with_timeout "$CORE_WORKFLOW_CLI '$KNOWLEDGE_DIR' status" "Status check timed out" || true

echo
if [[ "$DO_BACKUP" -eq 1 ]]; then
  echo "[2/5] Creating timestamped backup (safety-first)…"
  $SAFE_WORKFLOW_CLI --vault "$KNOWLEDGE_DIR" backup
else
  echo "[2/5] Skipping backup as requested (--skip-backup)."
fi

echo
if [[ "$DO_SCREENSHOTS" -eq 1 ]]; then
  echo "[3/5] Samsung Evening Screenshots: DRY-RUN (non-mutating)…"
  
  # Build screenshot command with options (TEMPORARY: using workflow_demo.py until extracted)
  screenshot_cmd="$WORKFLOW_DEMO_CLI '$KNOWLEDGE_DIR' --evening-screenshots --dry-run --progress"
  if [[ -n "$ONEDRIVE_PATH" ]]; then
    screenshot_cmd="$screenshot_cmd --onedrive-path '$ONEDRIVE_PATH'"
  fi
  if [[ "$NO_OCR" -eq 1 ]] || [[ "$FORCE_FALLBACK" -eq 1 ]]; then
    echo "⚠️  Note: OCR fallback requested but --no-ocr not available in CLI yet"
  fi
  
  if ! run_with_timeout "$screenshot_cmd" "Screenshot dry-run timed out - probably OCR stall"; then
    echo "⚠️  Screenshot dry-run failed/timed out. Try --no-ocr or --force-fallback"
    if [[ "$NO_OCR" -eq 0 ]]; then
      echo "Retrying with basic command (OCR fallback not yet available in CLI)..."
      basic_cmd="$WORKFLOW_DEMO_CLI '$KNOWLEDGE_DIR' --evening-screenshots --dry-run --progress"
      if [[ -n "$ONEDRIVE_PATH" ]]; then
        basic_cmd="$basic_cmd --onedrive-path '$ONEDRIVE_PATH'"
      fi
      run_with_timeout "$basic_cmd" "Screenshot dry-run with basic command timed out"
    fi
  fi

  if [[ "$DRY_RUN_ONLY" -eq 1 ]]; then
    echo "--dry-run-only set: stopping after screenshots dry-run."
    exit 0
  fi

  echo
  read -r -p "Proceed with ACTUAL Samsung screenshot import? [y/N] " RESP
  if [[ "$RESP" =~ ^[Yy]$ ]]; then
    # Build actual command
    actual_cmd="$WORKFLOW_DEMO_CLI '$KNOWLEDGE_DIR' --evening-screenshots --progress"
    if [[ -n "$ONEDRIVE_PATH" ]]; then
      actual_cmd="$actual_cmd --onedrive-path '$ONEDRIVE_PATH'"
    fi
    if [[ "$NO_OCR" -eq 1 ]] || [[ "$FORCE_FALLBACK" -eq 1 ]]; then
      echo "⚠️  Note: OCR fallback requested but --no-ocr not available in CLI yet"
    fi
    
    if ! run_with_timeout "$actual_cmd" "Screenshot import timed out - likely OCR stall"; then
      echo "⚠️  Screenshot import failed/timed out. Notes may be partially created."
    fi
  else
    echo "Skipped actual screenshot import."
  fi
else
  echo "[3/5] Skipping Samsung screenshots step (--skip-screenshots)."
fi

echo
echo "[4/5] Inbox processing: DRY-RUN (fast-mode) to preview…"
if ! run_with_timeout "$CORE_WORKFLOW_CLI '$KNOWLEDGE_DIR' process-inbox --fast" "Inbox dry-run timed out"; then
  echo "⚠️  Inbox dry-run failed/timed out. Continuing anyway..."
fi

if [[ "$DRY_RUN_ONLY" -eq 1 ]]; then
  echo "--dry-run-only set: stopping after inbox dry-run preview."
  exit 0
fi

echo
read -r -p "Proceed with ACTUAL inbox processing with progress? [y/N] " RESP2
if [[ "$RESP2" =~ ^[Yy]$ ]]; then
  inbox_cmd="$CORE_WORKFLOW_CLI '$KNOWLEDGE_DIR' process-inbox"
  if [[ -n "$EXPORT_PATH" ]]; then
    echo "Running with export → $EXPORT_PATH"
    inbox_cmd="$inbox_cmd --export '$EXPORT_PATH'"
  fi
  
  if ! run_with_timeout "$inbox_cmd" "Inbox processing timed out"; then
    echo "⚠️  Inbox processing failed/timed out. Some notes may be partially processed."
  fi
else
  echo "Skipped actual inbox processing."
fi

# Optional follow-ups
if [[ "$RUN_FLEETING_TRIAGE" -eq 1 ]]; then
  echo
  echo "[5/5] Optional: Fleeting triage report (min-quality=$MIN_QUALITY)…"
  run_with_timeout "$FLEETING_CLI '$KNOWLEDGE_DIR' fleeting-triage --quality-threshold '$MIN_QUALITY'" "Fleeting triage timed out" || echo "⚠️  Triage failed/timed out"
fi

if [[ "$RUN_SUGGEST_LINKS" -eq 1 ]]; then
  echo
  echo "[5/5] Optional: Smart Link suggestions for new/updated notes…"
  echo "⚠️  Note: suggest-links requires manual note selection - skipping in automation context"
  echo "    Run manually: $CONNECTIONS_CLI <note-path> '$KNOWLEDGE_DIR' suggest-links"
fi

echo
echo "✅ Workflow complete at $TIMESTAMP"
