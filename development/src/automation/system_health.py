"""Shared automation health checks for InnerOS.

Provides a single check_all entry point that summarizes daemon
status using the existing daemon registry and log parsing utilities.

This module is intended to be used by:
- inneros-status CLI
- Web UI automation status view
- .automation/scripts/check_automation_health.py (in a later refactor)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from src.automation.log_aggregator import LogAggregator
from src.cli.automation_status_cli import DaemonDetector, DaemonRegistry, LogParser


def _get_daemon_pid_file() -> Path:
    """Get the default daemon PID file path.

    The daemon writes its PID to ~/.inneros/daemon.pid when started.
    This is the canonical location used by `inneros daemon start`.

    Returns:
        Path to the daemon PID file.
    """
    return Path.home() / ".inneros" / "daemon.pid"


def _load_daemons(repo_root: Path) -> List[Dict[str, Any]]:
    """Load daemon configurations from the standard registry location.

    The path mirrors the production layout:
    - .automation/config/daemon_registry.yaml
    """

    registry_path = repo_root / ".automation" / "config" / "daemon_registry.yaml"
    if not registry_path.exists():
        return []

    registry = DaemonRegistry(registry_path)
    return registry.get_all_daemons()


def _build_automation_entry(
    detector: DaemonDetector,
    parser: LogParser,
    repo_root: Path,
    daemon_config: Dict[str, Any],
    log_aggregator: Optional[LogAggregator] = None,
) -> Dict[str, Any]:
    """Build a single automation status entry from daemon and log state.

    Detection strategy:
    1. If daemon_config has a pid_file field, use PID file detection
    2. Otherwise fall back to ps aux script path matching

    Log aggregation (Issue #67):
    - Uses LogAggregator to find most recent activity across handler logs
    - Falls back to single log file if aggregator not available

    This allows the Python daemon (which uses PID files) to be detected
    alongside legacy shell script daemons (which use ps aux matching).
    """
    name = daemon_config["name"]
    script_path = daemon_config["script_path"]

    # Determine PID file path - check for both relative and absolute paths
    pid_file_path = daemon_config.get("pid_file")
    if pid_file_path:
        # Expand ~ to home directory
        pid_file = Path(pid_file_path).expanduser()
        # If it's a relative path (after expansion), resolve against repo_root
        if not pid_file.is_absolute():
            pid_file = repo_root / pid_file_path
        # Use PID file detection for Python daemons
        status = detector.check_daemon_by_pid_file(pid_file)
    else:
        # Fall back to ps aux script path matching for shell scripts
        status = detector.check_daemon_status(name, script_path)

    # Get last run info - prefer aggregated handler logs for true last-activity
    last_run: Dict[str, Any] = {}
    handler_activity: Dict[str, Any] = {}

    if log_aggregator:
        # Use aggregated handler logs for accurate last-activity (Issue #67)
        overall_activity = log_aggregator.get_overall_last_activity()
        if overall_activity.get("last_timestamp"):
            last_run = {
                "status": overall_activity.get("status", "unknown"),
                "timestamp": overall_activity.get("last_timestamp"),
                "error_message": overall_activity.get("error_snippet"),
            }
        # Also get per-handler activity for detailed reporting
        handler_activity = log_aggregator.get_all_handler_activity()

    # Fallback to single log file if aggregator didn't find anything
    if not last_run.get("timestamp"):
        log_rel_path = daemon_config.get("log_path", f".automation/logs/{name}.log")
        log_path = repo_root / log_rel_path
        last_run = parser.parse_last_run(log_path)

    result: Dict[str, Any] = {
        "name": name,
        "running": bool(status.get("running", False)),
        "last_run_status": last_run.get("status", "unknown"),
        "last_run_timestamp": last_run.get("timestamp"),
        "error_message": last_run.get("error_message"),
    }

    # Include handler activity if available (for detailed status output)
    if handler_activity:
        result["handler_activity"] = {
            h: a.get("last_timestamp")
            for h, a in handler_activity.items()
            if a.get("last_timestamp")
        }

    return result


def _derive_overall_status(automations: List[Dict[str, Any]]) -> str:
    """Derive overall_status from individual automation entries.

    Rules:
    - If any automation has last_run_status == "failed" or is not running
      with a non success last_run_status, overall_status is "ERROR".
    - Else if any automation is not running, overall_status is "WARNING".
    - Else overall_status is "OK".
    """

    if not automations:
        return "OK"

    has_error = False
    has_warning = False

    for a in automations:
        running = bool(a.get("running", False))
        last_status = (a.get("last_run_status") or "").lower()

        if last_status == "failed" or (not running and last_status != "success"):
            has_error = True
            break
        if not running:
            has_warning = True

    if has_error:
        return "ERROR"
    if has_warning:
        return "WARNING"
    return "OK"


def check_all(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Check health of all registered automations.

    Args:
        repo_root: Optional repository root. Defaults to current working
            directory when not provided.

    Returns:
        Dictionary with keys:
        - overall_status: "OK" | "WARNING" | "ERROR"
        - automations: list of automation status entries
    """

    if repo_root is None:
        repo_root = Path.cwd()
    else:
        repo_root = Path(repo_root)

    daemons = _load_daemons(repo_root)
    detector = DaemonDetector()
    parser = LogParser()

    # Initialize LogAggregator for handler log aggregation (Issue #67)
    logs_dir = repo_root / ".automation" / "logs"
    log_aggregator = LogAggregator(logs_dir) if logs_dir.exists() else None

    automations: List[Dict[str, Any]] = []
    for daemon in daemons:
        automations.append(
            _build_automation_entry(
                detector=detector,
                parser=parser,
                repo_root=repo_root,
                daemon_config=daemon,
                log_aggregator=log_aggregator,
            )
        )

    overall_status = _derive_overall_status(automations)

    return {
        "overall_status": overall_status,
        "automations": automations,
    }
