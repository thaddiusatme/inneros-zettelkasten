"""
Daemon CLI - TDD REFACTOR Phase

Commands for daemon management:
- inneros daemon start: Launch automation daemon
- inneros daemon stop: Graceful shutdown
- inneros daemon status: Enhanced status display
- inneros daemon logs: Recent activity display

Phase: REFACTOR - ADR-001 compliant with utility extraction
Target: <200 LOC (utilities in daemon_cli_utils.py)
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional

from .daemon_cli_utils import (
    DaemonStarter,
    DaemonStopper,
    EnhancedDaemonStatus,
    LogReader,
)


class DaemonOrchestrator:
    """Main orchestrator for daemon commands."""

    def __init__(
        self, pid_file_path: Optional[Path] = None, logs_dir: Optional[Path] = None
    ):
        # Prioritize local .inneros/.automation if they exist (dev mode), fallback to home
        cwd = Path.cwd()
        local_automation = cwd / ".automation"

        default_pid = (
            (local_automation / "daemon.pid")
            if local_automation.exists()
            else (Path.home() / ".inneros" / "daemon.pid")
        )

        default_logs = (
            (local_automation / "logs")
            if local_automation.exists()
            else (Path.home() / ".automation" / "logs")
        )

        self.pid_file = pid_file_path or default_pid
        self.logs_dir = logs_dir or default_logs

    def start(self) -> Dict:
        """Route to start command."""
        return DaemonStarter(pid_file_path=self.pid_file).start()

    def stop(self) -> Dict:
        """Route to stop command."""
        return DaemonStopper(pid_file_path=self.pid_file).stop()

    def status(self) -> Dict:
        """Route to status command."""
        return EnhancedDaemonStatus(pid_file_path=self.pid_file).get_status()

    def logs(self, lines: int = 10) -> Dict:
        """Route to logs command."""
        return LogReader(logs_dir=self.logs_dir).read_recent(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Daemon management commands")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Start command
    subparsers.add_parser("start", help="Start the daemon")

    # Stop command
    subparsers.add_parser("stop", help="Stop the daemon")

    # Status command
    subparsers.add_parser("status", help="Show daemon status")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show recent logs")
    logs_parser.add_argument(
        "--lines", type=int, default=10, help="Number of lines to show"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    orchestrator = DaemonOrchestrator()

    if args.command == "start":
        result = orchestrator.start()
    elif args.command == "stop":
        result = orchestrator.stop()
    elif args.command == "status":
        result = orchestrator.status()
    elif args.command == "logs":
        result = orchestrator.logs(lines=args.lines)
    else:
        parser.print_help()
        sys.exit(1)

    print(result)
    sys.exit(0 if result.get("success", result.get("running", False)) else 1)


if __name__ == "__main__":
    main()
