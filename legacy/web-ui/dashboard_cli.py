"""
System Observability Phase 2.2: Dashboard-Daemon Integration - TDD Implementation

Provides unified entry points for dashboard access with daemon status integration:
- Web UI dashboard (workflow_dashboard.py)
- Live terminal dashboard (terminal_dashboard.py)
- Real-time daemon status detection and display

Phase: REFACTOR - Production-ready with daemon integration
Target: <200 LOC main file with utility extraction (Current: 204 LOC)

Architecture:
- DashboardLauncher: Web UI dashboard launcher
- TerminalDashboardLauncher: Live terminal mode launcher
- DashboardOrchestrator: Main orchestration with daemon status checking
- DashboardDaemonIntegration: Status detection (dashboard_utils.py)
- DaemonStatusFormatter: Color-coded display (dashboard_utils.py)
- DashboardHealthMonitor: Combined health view (dashboard_utils.py)

Phase 2.2 Enhancements:
- Auto-detect daemon status before dashboard launch
- Display daemon PID and uptime in results
- Graceful error handling when daemon not running
- Quick-start suggestions for stopped daemon

Following patterns from Phase 2.1 daemon management success.
"""

import logging
import sys
from typing import Any, Dict

# Import extracted utilities
from .dashboard_utils import (
    BrowserDashboardLauncher,
    LiveDashboardLauncher,
    OutputFormatter,
    WebDashboardLauncher,
)

# Configure logging for performance tracking
logger = logging.getLogger(__name__)

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

    def __init__(self, vault_path: str = "."):
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

    def __init__(self, daemon_url: str = "http://localhost:8080"):
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

    Phase 2.2 GREEN: Enhanced with daemon status integration.
    """

    def __init__(self, vault_path: str = "."):
        """Initialize dashboard orchestrator.

        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = vault_path
        self.web_launcher = DashboardLauncher(vault_path=vault_path)
        self.browser_launcher = BrowserDashboardLauncher(vault_path=vault_path)
        self.terminal_launcher = TerminalDashboardLauncher()
        self.daemon_detector = DaemonDetector() if HAVE_STATUS_UTILS else None

        # Phase 2.2: Add daemon integration
        try:
            from .dashboard_utils import DashboardDaemonIntegration

            self.daemon_integration = DashboardDaemonIntegration()
        except ImportError:
            self.daemon_integration = None

    def run(self, live_mode: bool = False, web_mode: bool = False) -> Dict[str, Any]:
        """Run dashboard launcher.

        Args:
            live_mode: If True, launch terminal dashboard; else web UI
            web_mode: If True, launch browser-based web dashboard

        Returns:
            Result dictionary with success status and daemon status
        """
        # Phase 2.2: Check daemon status before launch
        daemon_status = self.check_daemon_status()

        if web_mode:
            launcher = self.browser_launcher
            mode = "web"
        elif live_mode:
            launcher = self.terminal_launcher
            mode = "live"
        else:
            launcher = self.web_launcher
            mode = "workflow"

        result = launcher.launch()
        result["mode"] = mode

        # Phase 2.2: Include daemon status in result
        result["daemon_status"] = daemon_status

        return result

    def check_daemon_status(self) -> Dict[str, Any]:
        """Check if automation daemon is running.

        Returns:
            Daemon status dictionary
        """
        # Phase 2.2: Use new integration if available
        if self.daemon_integration:
            return self.daemon_integration.check_daemon_status()

        # Fallback to old method
        if self.daemon_detector:
            is_running, pid = self.daemon_detector.is_running()
            return {"running": is_running, "available": True, "pid": pid}
        return {
            "running": False,
            "available": False,
            "message": "Status utilities not available",
        }


def main():
    """CLI entry point for dashboard commands."""
    import argparse

    parser = argparse.ArgumentParser(
        description="InnerOS Dashboard Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inneros dashboard              Launch workflow dashboard (terminal UI)
  inneros dashboard --live       Launch live terminal dashboard
  inneros dashboard --web        Launch browser web dashboard
  
Dashboard provides real-time system monitoring and quick workflow actions.
        """,
    )

    parser.add_argument(
        "vault_path",
        nargs="?",
        default=".",
        help="Path to vault root (default: current directory)",
    )

    parser.add_argument(
        "--live",
        action="store_true",
        help="Launch live terminal dashboard instead of web UI",
    )

    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch browser-based web dashboard",
    )

    parser.add_argument(
        "--daemon-url",
        default="http://localhost:8080",
        help="Daemon URL for live mode (default: http://localhost:8080)",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = DashboardOrchestrator(vault_path=args.vault_path)

    # Update terminal launcher URL if specified
    if args.live and args.daemon_url:
        orchestrator.terminal_launcher.daemon_url = args.daemon_url

    # Run appropriate launcher
    result = orchestrator.run(live_mode=args.live, web_mode=args.web)

    # Display results using OutputFormatter
    if result.get("success"):
        print(OutputFormatter.format_success(result))
    else:
        print(OutputFormatter.format_error(result))
        if result.get("error"):
            sys.exit(1)


if __name__ == "__main__":
    main()
