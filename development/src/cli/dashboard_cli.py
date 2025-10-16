"""
System Observability Phase 2: Dashboard Launcher - TDD Implementation

Provides unified entry points for dashboard access:
- Web UI dashboard (workflow_dashboard.py)
- Live terminal dashboard (terminal_dashboard.py)

Phase: GREEN - Minimal implementation to pass tests
Target: <200 LOC main file with utility extraction

Architecture:
- DashboardLauncher: Web UI dashboard launcher
- TerminalDashboardLauncher: Live terminal mode launcher
- DashboardOrchestrator: Main orchestration class
- Utilities extracted to dashboard_utils.py

Following patterns from Phase 1 status CLI success.
"""

import sys
from typing import Dict, Any

# Import extracted utilities
from .dashboard_utils import (
    WebDashboardLauncher,
    LiveDashboardLauncher,
    OutputFormatter
)

# Import Phase 1 utilities for daemon detection
try:
    from .status_utils import DaemonDetector
    HAVE_STATUS_UTILS = True
except ImportError:
    HAVE_STATUS_UTILS = False


class DashboardLauncher:
    """Facade for web UI workflow dashboard.
    
    REFACTOR phase: Delegates to WebDashboardLauncher utility.
    """
    
    def __init__(self, vault_path: str = '.'):
        """Initialize dashboard launcher.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.launcher = WebDashboardLauncher(vault_path=vault_path)
    
    def launch(self) -> Dict[str, Any]:
        """Launch workflow dashboard.
        
        Returns:
            Result dictionary with success status and URL
        """
        return self.launcher.launch()


class TerminalDashboardLauncher:
    """Facade for live terminal dashboard.
    
    REFACTOR phase: Delegates to LiveDashboardLauncher utility.
    """
    
    def __init__(self, daemon_url: str = 'http://localhost:8080'):
        """Initialize terminal dashboard launcher.
        
        Args:
            daemon_url: URL of automation daemon
        """
        self.launcher = LiveDashboardLauncher(daemon_url=daemon_url)
        self.daemon_url = daemon_url  # Keep for compatibility
    
    def launch(self) -> Dict[str, Any]:
        """Launch terminal dashboard.
        
        Returns:
            Result dictionary with success status
        """
        return self.launcher.launch()


class DashboardOrchestrator:
    """Main orchestrator for dashboard commands.
    
    REFACTOR phase: Clean orchestration logic.
    """
    
    def __init__(self, vault_path: str = '.'):
        """Initialize dashboard orchestrator.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = vault_path
        self.web_launcher = DashboardLauncher(vault_path=vault_path)
        self.terminal_launcher = TerminalDashboardLauncher()
        self.daemon_detector = DaemonDetector() if HAVE_STATUS_UTILS else None
    
    def run(self, live_mode: bool = False) -> Dict[str, Any]:
        """Run dashboard launcher.
        
        Args:
            live_mode: If True, launch terminal dashboard; else web UI
            
        Returns:
            Result dictionary with success status
        """
        launcher = self.terminal_launcher if live_mode else self.web_launcher
        result = launcher.launch()
        result['mode'] = 'live' if live_mode else 'web'
        return result
    
    def check_daemon_status(self) -> Dict[str, Any]:
        """Check if automation daemon is running.
        
        Returns:
            Daemon status dictionary
        """
        if self.daemon_detector:
            is_running, pid = self.daemon_detector.is_running()
            return {'running': is_running, 'available': True, 'pid': pid}
        return {'running': False, 'available': False, 'message': 'Status utilities not available'}


def main():
    """CLI entry point for dashboard commands."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='InnerOS Dashboard Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inneros dashboard              Launch web UI dashboard
  inneros dashboard --live       Launch live terminal dashboard
  
Dashboard provides real-time system monitoring and quick workflow actions.
        """
    )
    
    parser.add_argument(
        'vault_path',
        nargs='?',
        default='.',
        help='Path to vault root (default: current directory)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Launch live terminal dashboard instead of web UI'
    )
    
    parser.add_argument(
        '--daemon-url',
        default='http://localhost:8080',
        help='Daemon URL for live mode (default: http://localhost:8080)'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = DashboardOrchestrator(vault_path=args.vault_path)
    
    # Update terminal launcher URL if specified
    if args.live and args.daemon_url:
        orchestrator.terminal_launcher.daemon_url = args.daemon_url
    
    # Run appropriate launcher
    result = orchestrator.run(live_mode=args.live)
    
    # Display results using OutputFormatter
    if result.get('success'):
        print(OutputFormatter.format_success(result))
    else:
        print(OutputFormatter.format_error(result))
        if result.get('error'):
            sys.exit(1)


if __name__ == '__main__':
    main()
