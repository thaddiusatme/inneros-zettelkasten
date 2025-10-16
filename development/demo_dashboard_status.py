#!/usr/bin/env python3
"""
Quick demo of dashboard-daemon integration.
Shows the actual result dictionary with daemon status.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.dashboard_cli import DashboardOrchestrator
from src.cli.dashboard_utils import DaemonStatusFormatter
import json

def main():
    print("=" * 60)
    print("Dashboard-Daemon Integration Demo")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = DashboardOrchestrator(vault_path='.')
    
    # Check daemon status
    print("\n1️⃣  Checking Daemon Status:")
    print("-" * 60)
    daemon_status = orchestrator.check_daemon_status()
    print(json.dumps(daemon_status, indent=2))
    
    # Format the status nicely
    print("\n2️⃣  Formatted Status Display:")
    print("-" * 60)
    formatter = DaemonStatusFormatter()
    formatted = formatter.format_status(daemon_status, color=True, include_instructions=True)
    print(formatted)
    
    # Show what would be included in dashboard launch result
    print("\n3️⃣  Dashboard Launch Result (simulated):")
    print("-" * 60)
    result = {
        'success': True,
        'message': 'Dashboard launched successfully',
        'url': 'http://localhost:8000',
        'mode': 'web',
        'daemon_status': daemon_status
    }
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    
    # Show helpful info
    if not daemon_status.get('running'):
        print("\n💡 Tip: Start the daemon with:")
        print("   PYTHONPATH=/Users/thaddius/repos/inneros-zettelkasten/development \\")
        print("     python3 -m src.cli.daemon_cli start")

if __name__ == '__main__':
    main()
