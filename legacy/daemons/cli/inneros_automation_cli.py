"""Automation helper CLI for InnerOS.

Provides a thin, ergonomic entrypoint that routes high-level automation
commands to dedicated CLIs. This module is intentionally small and focuses
on:

- Command routing (daemon / ai subcommands)
- Argument forwarding to underlying Python CLIs via ``python -m``
- Exit code propagation for reliable automation
"""

from __future__ import annotations

import subprocess
import sys
from typing import List, Optional


def _run_subprocess(cmd: List[str]) -> int:
    """Execute a subprocess command and return its exit code.

    This indirection exists primarily to make testing and monkeypatching
    straightforward while keeping the main routing logic simple.
    """

    result = subprocess.run(cmd, check=False)
    return int(getattr(result, "returncode", 1))


def _handle_daemon(args: List[str]) -> int:
    """Handle ``daemon`` subcommands.

    Expected forms:
        inneros-automation daemon start
        inneros-automation daemon stop
        inneros-automation daemon status
    """

    if not args:
        print("Usage: inneros-automation daemon <start|stop|status>")
        return 1

    subcommand = args[0]
    cmd = ["python3", "-m", "src.cli.daemon_cli", subcommand]
    return _run_subprocess(cmd)


def _handle_ai(args: List[str]) -> int:
    """Handle ``ai`` subcommands.

    Expected forms:
        inneros-automation ai inbox-sweep [--repo-root ...] [--format ...]
        inneros-automation ai repair-metadata [--repo-root ...] [--execute] [--format ...]

    All arguments following the specific AI subcommand are forwarded
    transparently to the underlying CLI module.
    """

    if not args:
        print("Usage: inneros-automation ai <inbox-sweep|repair-metadata> [options]")
        return 1

    subcommand = args[0]
    forwarded = args[1:]

    if subcommand == "inbox-sweep":
        cmd = ["python3", "-m", "src.cli.inneros_ai_inbox_sweep_cli", *forwarded]
        return _run_subprocess(cmd)

    if subcommand == "repair-metadata":
        cmd = ["python3", "-m", "src.cli.inneros_ai_repair_metadata_cli", *forwarded]
        return _run_subprocess(cmd)

    print(f"Unknown ai subcommand: {subcommand}")
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entrypoint for automation helper CLI.

    Args:
        argv: Optional explicit argument list (excluding program name).
            When None, ``sys.argv[1:]`` is used.

    Returns:
        Process exit code from underlying command, or non-zero on error.
    """

    args = list(argv) if argv is not None else sys.argv[1:]

    if not args:
        print("Usage: inneros-automation <daemon|ai> ...")
        return 1

    group = args[0]
    remaining = args[1:]

    if group == "daemon":
        return _handle_daemon(remaining)

    if group == "ai":
        return _handle_ai(remaining)

    # For unknown commands, do not attempt any subprocess calls; just
    # return a non-zero exit code so automation can detect the failure.
    print(f"Unknown command: {group}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
