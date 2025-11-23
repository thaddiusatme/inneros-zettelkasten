"""inneros-status CLI wrapper.

Provides a simple terminal interface for the shared automation
health check_all function in src.automation.system_health.

Design goals:
- Print a clear, compact summary of each automation.
- Print an overall status line that can be parsed by humans.
- Return exit code 0 when overall_status is OK, non zero otherwise.
"""

from typing import Any, Dict, List, Optional

from src.automation.system_health import check_all


def _format_automation(automation: Dict[str, Any]) -> str:
    """Format a single automation entry for terminal output."""

    name = automation.get("name", "unknown")
    running = bool(automation.get("running", False))
    last_status = automation.get("last_run_status", "unknown")
    error_message = automation.get("error_message")

    status_parts: List[str] = []
    if running:
        status_parts.append("running")
    else:
        status_parts.append("not running")

    if last_status:
        status_parts.append(f"last run: {last_status}")

    line = f"- {name}: " + ", ".join(status_parts)

    if error_message:
        line += f" - {error_message}"

    return line


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

    result: Dict[str, Any] = check_all()
    overall_status = result.get("overall_status", "ERROR")
    automations = result.get("automations", [])

    print("Automation status")
    for automation in automations:
        print(_format_automation(automation))

    print(f"Overall status: {overall_status}")

    return 0 if overall_status == "OK" else 1
