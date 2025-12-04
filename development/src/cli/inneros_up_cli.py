"""inneros-up CLI wrapper.

Provides a simple terminal interface for starting the automation daemon.

Design goals:
- Print clear success/failure messages for make target output.
- Return exit code 0 on success (including idempotent "already running").
- Return exit code 1 on failure with actionable error messages.
- Validate daemon is actually running after startup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


def start_daemon() -> Dict[str, Any]:
    """Start the automation daemon.

    Returns:
        Dictionary with keys:
        - success: bool indicating if operation succeeded
        - message: Human-readable status message
        - pid: Process ID if daemon is running
        - already_running: True if daemon was already running (idempotent)
        - error: Error type if failed
        - validation_error: Validation failure details if startup validation failed
    """
    from src.cli.daemon_cli_utils import DaemonStarter

    pid_file = Path.home() / ".inneros" / "daemon.pid"
    starter = DaemonStarter(pid_file_path=pid_file)

    result = starter.start()

    # Transform DaemonStarter result to our expected format
    if result.get("success"):
        return {
            "success": True,
            "message": result.get("message", "Daemon started successfully"),
            "pid": result.get("pid"),
        }
    else:
        # Check if "already running" - this is idempotent success
        message = result.get("message", "")
        if "already running" in message.lower():
            return {
                "success": True,
                "already_running": True,
                "message": message,
                "pid": result.get("pid"),
            }
        # Actual failure
        return {
            "success": False,
            "message": message,
            "error": result.get("error", "Unknown error"),
        }


# =============================================================================
# Output Formatting Helpers
# =============================================================================


def _format_success(result: Dict[str, Any]) -> str:
    """Format successful startup output.

    Args:
        result: Start result dictionary with pid and already_running flag.

    Returns:
        Formatted status line for terminal output.
    """
    pid = result.get("pid")
    if result.get("already_running"):
        return f"Daemon already running (PID {pid})"
    return f"Daemon started successfully (PID {pid})"


def _format_failure(result: Dict[str, Any]) -> str:
    """Format failure output with actionable message.

    Args:
        result: Start result dictionary with error details.

    Returns:
        Formatted error message for terminal output.
    """
    validation_error = result.get("validation_error")
    if validation_error:
        return f"Startup validation failed: {validation_error}"
    return f"Failed to start daemon: {result.get('message', 'Unknown error')}"


# =============================================================================
# Main Entry Point
# =============================================================================


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for inneros-up.

    Args:
        argv: Optional argument list. Currently unused but accepted
            for future extensibility and easier testing.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    _ = argv  # Currently unused

    try:
        result = start_daemon()
    except Exception as e:
        print(f"Error starting daemon: {e}")
        return 1

    if result.get("success", False):
        print(_format_success(result))
        return 0
    else:
        print(_format_failure(result))
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
