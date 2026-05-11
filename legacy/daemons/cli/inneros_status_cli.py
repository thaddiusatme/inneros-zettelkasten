"""inneros-status CLI wrapper.

Provides a simple terminal interface for the shared automation
health check_all function in src.automation.system_health.

Design goals:
- Print a clear, compact summary of each automation.
- Print an overall status line that can be parsed by humans.
- Return exit code 0 when overall_status is OK, non zero otherwise.
- Machine-parseable output with clear status indicators.
"""

from typing import Any, Dict, List, Optional

from src.automation.system_health import check_all


# =============================================================================
# Output Formatting Helpers
# =============================================================================


def _format_automation(automation: Dict[str, Any]) -> str:
    """Format a single automation entry for terminal output.

    Args:
        automation: Dictionary with keys: name, running, last_run_status,
            last_run_timestamp, error_message

    Returns:
        Formatted string like "- daemon_name: running, last run: success (2025-12-18 21:35)"
    """
    name = automation.get("name", "unknown")
    running = bool(automation.get("running", False))
    last_status = automation.get("last_run_status", "unknown")
    last_timestamp = automation.get("last_run_timestamp")
    error_message = automation.get("error_message")

    status_parts: List[str] = []
    if running:
        status_parts.append("running")
    else:
        status_parts.append("not running")

    if last_status:
        if last_timestamp:
            status_parts.append(f"last run: {last_status} ({last_timestamp})")
        else:
            status_parts.append(f"last run: {last_status}")

    line = f"- {name}: " + ", ".join(status_parts)

    if error_message:
        line += f" - {error_message}"

    return line


def _format_summary(automations: List[Dict[str, Any]]) -> str:
    """Format the daemon summary line showing running/total counts.

    Args:
        automations: List of automation status dictionaries

    Returns:
        Summary string like "Daemons: 3/3 running"
    """
    total = len(automations)
    running = sum(1 for a in automations if a.get("running", False))
    return f"Daemons: {running}/{total} running"


# =============================================================================
# Main Entry Point
# =============================================================================


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for inneros-status.

    Args:
        argv: Optional argument list. Currently unused but accepted
            for future extensibility and easier testing.

    Returns:
        Exit code: 0 when overall_status is OK, non zero otherwise.
    """

    # We ignore argv for now but keep the signature for future options.
    _ = argv

    try:
        result: Dict[str, Any] = check_all()
    except Exception as e:
        print(f"Error checking automation status: {e}")
        print("Overall status: ERROR")
        return 1

    overall_status = result.get("overall_status", "ERROR")
    automations = result.get("automations", [])

    # Print formatted status report
    print("Automation status")
    print(_format_summary(automations))
    print()
    for automation in automations:
        print(_format_automation(automation))

    print(f"\nOverall status: {overall_status}")

    return 0 if overall_status == "OK" else 1


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
