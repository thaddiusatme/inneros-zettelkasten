#!/usr/bin/env python3
"""
CLI Output Contract - Standardized JSON output for automation CLIs

Part of Issue #39: Migrate Automation Scripts to Dedicated CLIs (TDD Iteration 3)

This module provides a consistent JSON output contract that all automation CLIs
must follow. This enables reliable machine parsing of CLI outputs.

Contract specification:
- success (bool): Whether the operation succeeded
- errors (list[str]): List of error messages (empty on success)
- data (dict): Command-specific payload
- meta (dict): Metadata (cli, subcommand, timestamp)

Usage:
    from src.cli.cli_output_contract import build_json_response

    response = build_json_response(
        success=True,
        data={"backup_path": "/path/to/backup"},
        errors=[],
        cli_name="backup_cli",
        subcommand="backup",
    )
"""

from datetime import datetime
from typing import Any


def build_json_response(
    success: bool,
    data: dict[str, Any],
    errors: list[str] | None = None,
    cli_name: str = "cli",
    subcommand: str = "",
) -> dict[str, Any]:
    """
    Build a standardized JSON response following the CLI output contract.

    Contract:
    - success (bool): Whether the operation succeeded
    - errors (list[str]): List of error messages (empty on success)
    - data (dict): Command-specific payload
    - meta (dict): Metadata (cli, subcommand, timestamp)

    Args:
        success: Whether the operation succeeded
        data: Command-specific payload
        errors: List of error messages (defaults to empty list)
        cli_name: Name of the CLI for metadata
        subcommand: Subcommand name for metadata

    Returns:
        Standardized JSON response dict
    """
    return {
        "success": success,
        "errors": errors or [],
        "data": data,
        "meta": {
            "cli": cli_name,
            "subcommand": subcommand,
            "timestamp": datetime.now().isoformat(),
        },
    }
