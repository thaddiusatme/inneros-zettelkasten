"""
Daemon CLI Utilities - TDD REFACTOR Phase

Extracted utility classes for daemon management.
Follows proven pattern from status_utils.py and dashboard_utils.py.

Utilities:
- DaemonStarter: Launch daemon with PID tracking
- DaemonStopper: Graceful shutdown with SIGTERM
- EnhancedDaemonStatus: Status with uptime details
- LogReader: Read and display log files

Phase: REFACTOR - Utility extraction for ADR-001 compliance
"""

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class DaemonStarter:
    """Starts the automation daemon with PID tracking."""

    def __init__(
        self, pid_file_path: Optional[Path] = None, daemon_script: Optional[str] = None
    ):
        self.pid_file = pid_file_path or (Path.home() / ".inneros" / "daemon.pid")
        # Default to the actual daemon location in development
        if daemon_script is None:
            # Find daemon relative to this file: cli/daemon_cli_utils.py -> automation/daemon.py
            cli_dir = Path(__file__).parent
            daemon_path = cli_dir.parent / "automation" / "daemon.py"
            self.daemon_script = (
                str(daemon_path) if daemon_path.exists() else "automation/daemon.py"
            )
        else:
            self.daemon_script = daemon_script

    def start(self) -> Dict:
        """Start the daemon process."""
        try:
            if self.pid_file.exists():
                try:
                    pid = int(self.pid_file.read_text().strip())
                    os.kill(pid, 0)
                    return {
                        "success": False,
                        "message": f"Daemon already running with PID {pid}",
                    }
                except (ValueError, ProcessLookupError, OSError):
                    self.pid_file.unlink(missing_ok=True)

            self.pid_file.parent.mkdir(parents=True, exist_ok=True)

            if self.daemon_script and Path(self.daemon_script).exists():
                # Run daemon as module with proper PYTHONPATH
                import os as os_module

                env = os_module.environ.copy()
                daemon_path = Path(self.daemon_script)
                # Find development directory (daemon.py is in src/automation/)
                dev_dir = (
                    daemon_path.parent.parent.parent
                )  # automation -> src -> development
                env["PYTHONPATH"] = str(dev_dir)

                proc = subprocess.Popen(
                    [sys.executable, "-m", "src.automation.daemon"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    env=env,
                    cwd=str(dev_dir),
                )
                pid = proc.pid
            else:
                pid = os.getpid()

            self.pid_file.write_text(str(pid))
            return {
                "success": True,
                "message": f"Daemon started with PID {pid}",
                "pid": pid,
            }
        except (OSError, PermissionError) as e:
            return {"success": False, "message": f"Permission denied or error: {e}"}


class DaemonStopper:
    """Stops the automation daemon gracefully."""

    def __init__(self, pid_file_path: Optional[Path] = None):
        self.pid_file = pid_file_path or (Path.home() / ".inneros" / "daemon.pid")

    def stop(self) -> Dict:
        """Stop the daemon process gracefully."""
        if not self.pid_file.exists():
            return {"success": False, "message": "Daemon not running (no PID file)"}

        try:
            pid_text = self.pid_file.read_text().strip()
            if not pid_text or not pid_text.isdigit():
                self.pid_file.unlink(missing_ok=True)
                return {"success": False, "message": "Invalid PID in file"}

            pid = int(pid_text)

            try:
                os.kill(pid, signal.SIGTERM)
                self.pid_file.unlink(missing_ok=True)
                return {"success": True, "message": f"Daemon stopped (PID {pid})"}
            except ProcessLookupError:
                self.pid_file.unlink(missing_ok=True)
                return {
                    "success": False,
                    "message": "Daemon not running (process not found)",
                }
        except (ValueError, OSError) as e:
            self.pid_file.unlink(missing_ok=True)
            return {"success": False, "message": f"Error stopping daemon: {e}"}


class EnhancedDaemonStatus:
    """Enhanced daemon status checking."""

    def __init__(self, pid_file_path: Optional[Path] = None):
        self.pid_file = pid_file_path or (Path.home() / ".inneros" / "daemon.pid")

    def get_status(self) -> Dict:
        """Get enhanced daemon status."""
        if not self.pid_file.exists():
            return {"running": False, "message": "Daemon not running"}

        try:
            pid = int(self.pid_file.read_text().strip())
            os.kill(pid, 0)

            start_time = datetime.fromtimestamp(self.pid_file.stat().st_mtime)
            uptime = datetime.now() - start_time

            return {
                "running": True,
                "pid": pid,
                "start_time": start_time.isoformat(),
                "uptime": str(uptime).split(".")[0],
            }
        except (ValueError, ProcessLookupError, OSError):
            return {"running": False, "message": "Daemon not running"}


class LogReader:
    """Reads and displays daemon log files."""

    def __init__(self, logs_dir: Optional[Path] = None):
        self.logs_dir = logs_dir or (Path.home() / ".automation" / "logs")

    def read_recent(self, lines: int = 10) -> Dict:
        """Read recent log entries."""
        if not self.logs_dir.exists():
            return {"success": False, "message": "No logs directory found"}

        log_files = list(self.logs_dir.glob("*.log"))
        if not log_files:
            return {"success": False, "message": "No log files found"}

        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

        try:
            content = latest_log.read_text()
            entries = content.strip().split("\n")[-lines:]
            return {"success": True, "entries": entries, "log_file": str(latest_log)}
        except (IOError, OSError) as e:
            return {"success": False, "message": f"Error reading log: {e}"}
