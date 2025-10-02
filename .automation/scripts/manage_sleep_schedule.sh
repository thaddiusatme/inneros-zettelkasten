#!/usr/bin/env bash
# InnerOS Zettelkasten - Sleep Management for Automation
# Prevents sleep during critical automation windows

set -euo pipefail

# Check if caffeinate is available
if ! command -v caffeinate >/dev/null 2>&1; then
    echo "❌ caffeinate not available - cannot manage sleep"
    exit 1
fi

case "${1:-}" in
    "evening")
        # Keep Mac awake for evening screenshot processing (11:20 PM - 11:40 PM)
        echo "☕ Preventing sleep for evening screenshot automation..."
        caffeinate -s -t 1200 &  # 20 minutes
        echo $! > /tmp/inneros_caffeinate_evening.pid
        echo "✅ Sleep prevention active for 20 minutes (PID: $!)"
        ;;
    "morning")  
        # Keep Mac awake for morning inbox processing (5:50 AM - 6:20 AM)
        echo "☕ Preventing sleep for morning inbox automation..."
        caffeinate -s -t 1800 &  # 30 minutes
        echo $! > /tmp/inneros_caffeinate_morning.pid
        echo "✅ Sleep prevention active for 30 minutes (PID: $!)"
        ;;
    "weekly")
        # Keep Mac awake for weekly analysis (8:50 AM - 9:30 AM)
        echo "☕ Preventing sleep for weekly analysis..."
        caffeinate -s -t 2400 &  # 40 minutes
        echo $! > /tmp/inneros_caffeinate_weekly.pid  
        echo "✅ Sleep prevention active for 40 minutes (PID: $!)"
        ;;
    "stop")
        # Stop all sleep prevention
        echo "🛌 Stopping sleep prevention..."
        for pidfile in /tmp/inneros_caffeinate_*.pid; do
            if [[ -f "$pidfile" ]]; then
                pid=$(cat "$pidfile")
                if kill "$pid" 2>/dev/null; then
                    echo "✅ Stopped sleep prevention (PID: $pid)"
                fi
                rm -f "$pidfile"
            fi
        done
        ;;
    "status")
        # Check current sleep prevention status
        echo "☕ Sleep Prevention Status:"
        for pidfile in /tmp/inneros_caffeinate_*.pid; do
            if [[ -f "$pidfile" ]]; then
                pid=$(cat "$pidfile")
                if ps -p "$pid" >/dev/null 2>&1; then
                    echo "✅ Active: $(basename "$pidfile" .pid) (PID: $pid)"
                else
                    echo "❌ Stale: $(basename "$pidfile" .pid) (PID: $pid)"
                    rm -f "$pidfile"
                fi
            fi
        done
        ;;
    *)
        echo "Usage: $0 {evening|morning|weekly|stop|status}"
        echo ""
        echo "Commands:"
        echo "  evening  - Prevent sleep for evening screenshot processing"
        echo "  morning  - Prevent sleep for morning inbox processing" 
        echo "  weekly   - Prevent sleep for weekly analysis"
        echo "  stop     - Stop all sleep prevention"
        echo "  status   - Check current sleep prevention status"
        exit 1
        ;;
esac
