"""
Automation Status CLI - TDD GREEN Phase
Provides visibility into automation daemon status, logs, and control.
"""

import os
import psutil
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class DaemonDetector:
    """Detects running daemon processes."""

    def check_daemon_status(self, daemon_name: str, script_path: str) -> Dict[str, Any]:
        """
        Check if a daemon is running by looking for its process.

        Args:
            daemon_name: Name of the daemon
            script_path: Script path to match in command line

        Returns:
            Dictionary with 'running' status and 'pid' if running
        """
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline", [])
                if cmdline and any(script_path in cmd for cmd in cmdline):
                    return {"running": True, "pid": proc.info["pid"]}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {"running": False, "pid": None}

    def check_daemon_by_pid_file(self, pid_file: Path) -> Dict[str, Any]:
        """
        Check if a daemon is running by reading its PID file.

        This method is used for Python daemons that write their PID to a file
        (e.g., ~/.inneros/daemon.pid) instead of being detected via ps aux.

        Args:
            pid_file: Path to the PID file

        Returns:
            Dictionary with 'running' status and 'pid' if running
        """
        if not pid_file.exists():
            return {"running": False, "pid": None}

        try:
            pid_text = pid_file.read_text().strip()
            if not pid_text or not pid_text.isdigit():
                return {"running": False, "pid": None}

            pid = int(pid_text)
            # Check if process is actually running
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            return {"running": True, "pid": pid}
        except (ValueError, ProcessLookupError, OSError):
            # PID file exists but process is not running (stale)
            return {"running": False, "pid": None}

    def check_all_daemons(self, daemon_configs: List[tuple]) -> List[Dict[str, Any]]:
        """
        Check status of multiple daemons.

        Args:
            daemon_configs: List of (name, script_path) tuples

        Returns:
            List of status dictionaries
        """
        statuses = []
        for name, script_path in daemon_configs:
            status = self.check_daemon_status(name, script_path)
            status["name"] = name
            statuses.append(status)
        return statuses


class LogParser:
    """Parses daemon log files."""

    def parse_last_run(self, log_path: Path) -> Dict[str, Any]:
        """
        Parse last execution details from log file.

        Args:
            log_path: Path to log file

        Returns:
            Dictionary with status, timestamp, duration, error_message
        """
        if not log_path.exists():
            return {"status": "unknown", "error_message": "No log file found"}

        try:
            with open(log_path, "r") as f:
                lines = f.read().strip().split("\n")

            # Look for status indicators in reverse order
            status = "unknown"
            timestamp = None
            duration = None
            error_message = None

            for line in reversed(lines):
                if "SUCCESS" in line or "completed successfully" in line.lower():
                    status = "success"
                    # Extract timestamp from line
                    parts = line.split(" - ")
                    if len(parts) > 0:
                        timestamp = parts[0].strip()
                    break
                elif "FAILED" in line or "ERROR" in line:
                    status = "failed"
                    # Look for error message  - check all lines for ERROR messages
                    for err_line in reversed(lines):
                        if "ERROR" in err_line:
                            parts = err_line.split(" - ")
                            if len(parts) >= 3:
                                error_message = parts[2].strip()
                                break
                    # Fallback to generic error message
                    if not error_message:
                        error_message = "Execution failed"
                    break

            # Look for duration
            for line in reversed(lines):
                if "seconds" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "seconds" in part.lower() and i > 0:
                            duration = f"{parts[i-1]} seconds"
                            break
                    if duration:
                        break

            return {
                "status": status,
                "timestamp": timestamp,
                "duration": duration,
                "error_message": error_message,
            }

        except Exception as e:
            return {
                "status": "unknown",
                "error_message": f"Failed to parse log: {str(e)}",
            }

    def get_log_tail(self, log_path: Path, lines: int = 10) -> List[str]:
        """
        Get last N lines from log file.

        Args:
            log_path: Path to log file
            lines: Number of lines to retrieve

        Returns:
            List of log lines
        """
        if not log_path.exists():
            return []

        try:
            with open(log_path, "r") as f:
                all_lines = f.read().strip().split("\n")
            return all_lines[-lines:] if all_lines else []
        except Exception:
            return []


class DaemonRegistry:
    """Manages daemon registry configuration."""

    def __init__(self, registry_path: Path):
        """
        Initialize daemon registry.

        Args:
            registry_path: Path to daemon_registry.yaml
        """
        self.registry_path = registry_path
        self._load_registry()

    def _load_registry(self):
        """Load daemon configurations from YAML."""
        with open(self.registry_path, "r") as f:
            config = yaml.safe_load(f)
            self.daemons = config.get("daemons", [])

    def get_all_daemons(self) -> List[Dict[str, Any]]:
        """Get all daemon configurations."""
        return self.daemons

    def get_daemon(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific daemon configuration.

        Args:
            name: Daemon name

        Returns:
            Daemon configuration or None
        """
        for daemon in self.daemons:
            if daemon["name"] == name:
                return daemon
        return None

    def validate(self):
        """Validate daemon configurations have required fields."""
        required_fields = ["name", "script_path", "log_path", "pid_file", "description"]
        for daemon in self.daemons:
            missing = [field for field in required_fields if field not in daemon]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")


class StatusFormatter:
    """Formats daemon status output."""

    def format_daemon_status(self, status: Dict[str, Any]) -> str:
        """
        Format single daemon status with colored indicators.

        Args:
            status: Status dictionary

        Returns:
            Formatted status string
        """
        if status["running"]:
            indicator = "🟢"
            status_text = f"Running (PID: {status['pid']})"
        else:
            indicator = "🔴"
            status_text = "Stopped"

        name = status.get("name", "Unknown")
        output = f"{indicator} {name}: {status_text}"

        # Add last run info if available
        if "last_run" in status:
            last_run = status["last_run"]
            if last_run.get("status") == "success":
                output += f" | Last run: {last_run.get('status', 'unknown')}"
            elif last_run.get("status"):
                output += f" | Last run: {last_run['status']}"

        return output

    def format_summary(self, statuses: List[Dict[str, Any]]) -> str:
        """
        Format summary of all daemon statuses.

        Args:
            statuses: List of status dictionaries

        Returns:
            Formatted summary string
        """
        running = sum(1 for s in statuses if s.get("running", False))
        total = len(statuses)

        summary = f"\n{'='*60}\n"
        summary += f"Automation Status Summary: {running}/{total} daemons running\n"
        summary += f"{'='*60}\n"

        for status in statuses:
            summary += self.format_daemon_status(status) + "\n"

        return summary


class AutomationStatusCLI:
    """Main CLI interface for automation status."""

    def __init__(self, registry_path: Path, workspace_root: Path):
        """
        Initialize automation status CLI.

        Args:
            registry_path: Path to daemon registry YAML
            workspace_root: Root directory of workspace
        """
        self.registry = DaemonRegistry(registry_path)
        self.detector = DaemonDetector()
        self.parser = LogParser()
        self.formatter = StatusFormatter()
        self.workspace_root = workspace_root

    def status(self) -> Dict[str, Any]:
        """
        Check status of all registered daemons.

        Returns:
            Dictionary with total_daemons, running_daemons, daemon_statuses
        """
        daemons = self.registry.get_all_daemons()
        daemon_configs = [(d["name"], d["script_path"]) for d in daemons]

        statuses = self.detector.check_all_daemons(daemon_configs)
        running_count = sum(1 for s in statuses if s["running"])

        return {
            "total_daemons": len(daemons),
            "running_daemons": running_count,
            "daemon_statuses": statuses,
        }

    def last_run(self, daemon_name: str) -> Dict[str, Any]:
        """
        Get last execution details for specific daemon.

        Args:
            daemon_name: Name of daemon

        Returns:
            Dictionary with daemon name and last run details

        Raises:
            ValueError: If daemon name is invalid
        """
        daemon = self.registry.get_daemon(daemon_name)
        if not daemon:
            raise ValueError(f"Unknown daemon: {daemon_name}")

        log_path = self.workspace_root / daemon["log_path"]
        last_run_info = self.parser.parse_last_run(log_path)

        return {"daemon": daemon_name, **last_run_info}

    def logs(self, daemon_name: str, lines: int = 10) -> Dict[str, Any]:
        """
        Display last N lines of daemon log.

        Args:
            daemon_name: Name of daemon
            lines: Number of lines to display

        Returns:
            Dictionary with daemon name and log lines

        Raises:
            ValueError: If daemon name is invalid
        """
        daemon = self.registry.get_daemon(daemon_name)
        if not daemon:
            raise ValueError(f"Unknown daemon: {daemon_name}")

        log_path = self.workspace_root / daemon["log_path"]
        log_lines = self.parser.get_log_tail(log_path, lines)

        return {"daemon": daemon_name, "log_lines": log_lines}
