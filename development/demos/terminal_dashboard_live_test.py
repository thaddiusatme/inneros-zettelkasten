#!/usr/bin/env python3
"""
Live Data Test: Terminal UI Dashboard

Validates TDD Iteration 7:
- Dashboard polls /health endpoint
- Live-updating display refreshes every second
- Color-coded status indicators
- Handler metrics display
- Graceful error handling when daemon offline
"""

import sys
from pathlib import Path

# Add development src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.terminal_dashboard import run_dashboard


def print_section(title: str, emoji: str = "📋"):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"{emoji}  {title}")
    print("=" * 70)


def main():
    print_section("Terminal UI Dashboard Live Test", "🧪")
    print("Testing: Real-time monitoring with live-updating display")
    print("\nPrerequisites:")
    print("  1. Daemon must be running: python3 development/demos/daemon_live_test.py")
    print("  2. HTTP server on port 8080")
    print("\nInstructions:")
    print("  • Dashboard will refresh every second")
    print("  • Press Ctrl+C to stop")
    print("  • Watch for status changes as daemon processes events")
    
    input("\n👉 Press Enter to start dashboard (or Ctrl+C to cancel)...")
    
    print_section("Starting Dashboard", "🚀")
    
    # Run dashboard - will connect to http://localhost:8080
    try:
        run_dashboard(url='http://localhost:8080', refresh_interval=1)
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped gracefully")
        return 0
    except Exception as e:
        print(f"\n\n❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
