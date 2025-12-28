#!/usr/bin/env bash
#
# inneros.sh - Developer helper script for InnerOS automation
#
# This is a convenience wrapper for common InnerOS commands.
# Note: This script is temporary - prefer `make` commands for daily use.
# The Makefile is the canonical interface for InnerOS operations.
#
# Usage: ./inneros.sh <command> [args...]
#
# Commands:
#   status      - Show automation daemon status (same as: make status)
#   up          - Start the automation daemon (same as: make up)
#   down        - Stop the automation daemon (same as: make down)
#   logs        - Show daemon logs (same as: make logs)
#   ai <cmd>    - Run AI workflow commands
#     inbox-sweep     - Process inbox notes with AI
#     repair-metadata - Fix metadata issues in notes
#   help        - Show this help message
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv if present
if [[ -d "$SCRIPT_DIR/venv" ]]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [[ -d "$SCRIPT_DIR/.venv" ]]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
    # Already in a venv, use it
    :
fi

show_help() {
    cat << 'EOF'
Usage: ./inneros.sh <command> [args...]

InnerOS Developer Helper Script
(Temporary convenience wrapper - prefer `make` commands for daily use)

Commands:
  status          Show automation daemon status
  up              Start the automation daemon
  down            Stop the automation daemon
  logs            Show daemon logs
  ai <command>    Run AI workflow commands:
    inbox-sweep       Process inbox notes with AI
    repair-metadata   Fix metadata issues in notes
  help            Show this help message

Examples:
  ./inneros.sh status
  ./inneros.sh up
  ./inneros.sh ai inbox-sweep

Note: These commands are wrappers around `make` targets.
      For production use, prefer: make status, make up, etc.
EOF
}

cmd_status() {
    make -C "$SCRIPT_DIR" status
}

cmd_up() {
    make -C "$SCRIPT_DIR" up
}

cmd_down() {
    make -C "$SCRIPT_DIR" down
}

cmd_logs() {
    make -C "$SCRIPT_DIR" logs
}

cmd_ai() {
    local subcmd="${1:-}"
    shift || true
    
    case "$subcmd" in
        inbox-sweep)
            make -C "$SCRIPT_DIR" ai-inbox-sweep
            ;;
        repair-metadata)
            make -C "$SCRIPT_DIR" ai-repair-metadata
            ;;
        "")
            echo "Error: ai command requires a subcommand"
            echo "Available: inbox-sweep, repair-metadata"
            exit 1
            ;;
        *)
            echo "Error: Unknown ai subcommand: $subcmd"
            echo "Available: inbox-sweep, repair-metadata"
            exit 1
            ;;
    esac
}

main() {
    local cmd="${1:-help}"
    shift || true
    
    case "$cmd" in
        status)
            cmd_status
            ;;
        up)
            cmd_up
            ;;
        down)
            cmd_down
            ;;
        logs)
            cmd_logs
            ;;
        ai)
            cmd_ai "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Error: Unknown command: $cmd"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
