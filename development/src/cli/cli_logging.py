#!/usr/bin/env python3
"""
CLI Logging Context - Standardized logging for dedicated CLIs

Issue #39 P1: Provides consistent logging context across all CLI tools.
This module ensures all CLIs log startup context in a predictable format
and that logs go to stderr (not stdout) to avoid JSON contamination.

Usage:
    from src.cli.cli_logging import configure_cli_logging, log_cli_context

    logger = configure_cli_logging("backup_cli")
    log_cli_context(
        logger=logger,
        cli_name="backup_cli",
        subcommand="backup",
        vault_path="/path/to/vault",
        dry_run=True,
        output_format="json",
    )

Key principles:
1. Logs go to stderr (not stdout) - stdout is reserved for JSON output
2. Consistent key=value format for machine parseability
3. All CLIs should log the same context fields at startup
"""

import logging
import sys
from typing import Optional


def configure_cli_logging(
    cli_name: str,
    level: int = logging.INFO,
    log_format: str = "%(levelname)s - %(name)s - %(message)s",
) -> logging.Logger:
    """
    Configure a logger for a CLI that writes to stderr.

    This ensures that log messages don't contaminate stdout,
    which is reserved for JSON output in --format json mode.

    Args:
        cli_name: Name of the CLI (used as logger name)
        level: Logging level (default: INFO)
        log_format: Format string for log messages

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(cli_name)
    logger.setLevel(level)

    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create stderr handler (crucial: not stdout!)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(log_format))

    logger.addHandler(handler)

    # Prevent propagation to root logger (avoids duplicate logs)
    logger.propagate = False

    return logger


def log_cli_context(
    logger: logging.Logger,
    cli_name: str,
    subcommand: str,
    vault_path: Optional[str] = None,
    dry_run: Optional[bool] = None,
    output_format: Optional[str] = None,
    **extra_context: object,
) -> None:
    """
    Log standardized CLI startup context.

    Logs a consistent set of fields for diagnosability and automation trust.
    Format: key=value pairs for machine parseability.

    Args:
        logger: Logger instance to use
        cli_name: Name of the CLI (e.g., "backup_cli")
        subcommand: Subcommand being executed (e.g., "backup", "prune-backups")
        vault_path: Path to vault (if applicable)
        dry_run: Whether dry-run mode is enabled
        output_format: Output format (e.g., "json", "normal")
        **extra_context: Additional key=value pairs to log
    """
    parts = [f"cli={cli_name}", f"subcommand={subcommand}"]

    if vault_path is not None:
        parts.append(f"vault={vault_path}")

    if dry_run is not None:
        parts.append(f"dry_run={dry_run}")

    if output_format is not None:
        parts.append(f"format={output_format}")

    # Add any extra context
    for key, value in extra_context.items():
        parts.append(f"{key}={value}")

    logger.info(" ".join(parts))
