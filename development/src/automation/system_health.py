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

from src.cli.automation_status_cli import DaemonDetector, DaemonRegistry, LogParser


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
) -> Dict[str, Any]:
    """Build a single automation status entry from daemon and log state."""

    name = daemon_config["name"]
    script_path = daemon_config["script_path"]

    status = detector.check_daemon_status(name, script_path)

    log_rel_path = daemon_config.get(
        "log_path", f".automation/logs/{name}.log"
    )
    log_path = repo_root / log_rel_path
    last_run = parser.parse_last_run(log_path)

    return {
        "name": name,
        "running": bool(status.get("running", False)),
        "last_run_status": last_run.get("status", "unknown"),
        "last_run_timestamp": last_run.get("timestamp"),
        "error_message": last_run.get("error_message"),
    }


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

    automations: List[Dict[str, Any]] = []
    for daemon in daemons:
        automations.append(
            _build_automation_entry(
                detector=detector,
                parser=parser,
                repo_root=repo_root,
                daemon_config=daemon,
            )
        )

    overall_status = _derive_overall_status(automations)

    return {
        "overall_status": overall_status,
        "automations": automations,
    }
