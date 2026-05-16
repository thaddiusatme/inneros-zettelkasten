#!/usr/bin/env python3
"""
inneros — unified CLI entry point for the InnerOS Zettelkasten automation system.

Consolidates backup_cli, fleeting_cli, weekly_review_cli into a single entry
point. Each domain is a top-level subcommand; secondary actions are nested
subcommands under that domain.

Usage:
    inneros --vault /path/to/vault backup
    inneros --vault /path/to/vault backup prune [--keep N] [--dry-run]
    inneros --vault /path/to/vault fleeting health [--format json]
    inneros --vault /path/to/vault fleeting triage [--quality-threshold 0.8] [--fast]
    inneros --vault /path/to/vault review [--preview] [--export] [--format json]
    inneros --vault /path/to/vault review metrics [--format json]
    inneros --vault /path/to/vault inbox [--dry-run] [--format json]
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from src.cli.cli_logging import configure_cli_logging

logger = configure_cli_logging("inneros")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inneros",
        description="InnerOS Zettelkasten automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    _add_backup_subcommand(subparsers)
    _add_fleeting_subcommand(subparsers)
    _add_review_subcommand(subparsers)
    _add_inbox_subcommand(subparsers)

    return parser


def _add_backup_subcommand(subparsers):
    backup = subparsers.add_parser("backup", help="Vault backup operations")
    backup_sub = backup.add_subparsers(dest="subcommand", metavar="subcommand")

    prune = backup_sub.add_parser("prune", help="Prune old backups")
    prune.add_argument(
        "--keep", type=int, default=3, help="Number of backups to keep (default: 3)"
    )
    prune.add_argument(
        "--dry-run", action="store_true", help="Preview without deleting"
    )
    prune.add_argument("--format", choices=["text", "json"], default="text")


def _add_fleeting_subcommand(subparsers):
    fleeting = subparsers.add_parser("fleeting", help="Fleeting note operations")
    fleeting_sub = fleeting.add_subparsers(dest="subcommand", metavar="subcommand")
    fleeting_sub.required = True

    health = fleeting_sub.add_parser("health", help="Fleeting notes health report")
    health.add_argument("--format", choices=["text", "json"], default="text")
    health.add_argument("--export", metavar="FILE", help="Export report to file")

    triage = fleeting_sub.add_parser("triage", help="AI-powered fleeting note triage")
    triage.add_argument("--quality-threshold", type=float, default=0.6)
    triage.add_argument(
        "--fast", action="store_true", help="Skip AI scoring, use heuristics"
    )
    triage.add_argument("--format", choices=["text", "json"], default="text")


def _add_review_subcommand(subparsers):
    review = subparsers.add_parser("review", help="Weekly review operations")
    review_sub = review.add_subparsers(dest="subcommand", metavar="subcommand")

    review.add_argument(
        "--preview", action="store_true", help="Preview mode (no writes)"
    )
    review.add_argument(
        "--export", action="store_true", help="Export checklist to file"
    )
    review.add_argument("--format", choices=["text", "json"], default="text")

    metrics = review_sub.add_parser("metrics", help="Enhanced analytics metrics")
    metrics.add_argument("--format", choices=["text", "json"], default="text")
    metrics.add_argument("--export", metavar="FILE", help="Export metrics to file")


def _add_inbox_subcommand(subparsers):
    inbox = subparsers.add_parser("inbox", help="Process unprocessed inbox notes")
    inbox.add_argument(
        "--dry-run", action="store_true", help="Scan only, no processing"
    )
    inbox.add_argument("--format", choices=["text", "json"], default="text")


# ---------------------------------------------------------------------------
# Dispatch handlers
# ---------------------------------------------------------------------------


def _run_backup(args) -> int:
    from src.cli.backup_cli import BackupCLI

    cli = BackupCLI(vault_path=args.vault)
    subcommand = getattr(args, "subcommand", None)
    if subcommand == "prune":
        return cli.prune_backups(
            keep=args.keep,
            dry_run=args.dry_run,
            output_format=getattr(args, "format", "normal"),
        )
    return cli.backup(output_format=getattr(args, "format", "normal"))


def _run_fleeting(args) -> int:
    from src.cli.fleeting_cli import FleetingCLI

    cli = FleetingCLI(vault_path=args.vault)
    subcommand = getattr(args, "subcommand", "health")
    if subcommand == "triage":
        return cli.fleeting_triage(
            output_format=getattr(args, "format", "normal"),
            quality_threshold=getattr(args, "quality_threshold", 0.6),
            fast=getattr(args, "fast", False),
        )
    return cli.fleeting_health(output_format=getattr(args, "format", "normal"))


def _run_review(args) -> int:
    from src.cli.weekly_review_cli import WeeklyReviewCLI

    cli = WeeklyReviewCLI(vault_path=args.vault)
    subcommand = getattr(args, "subcommand", None)
    if subcommand == "metrics":
        return cli.enhanced_metrics(output_format=getattr(args, "format", "normal"))
    return cli.weekly_review(
        output_format=getattr(args, "format", "normal"),
        preview=getattr(args, "preview", False),
    )


def _run_inbox(args) -> int:
    from src.ai.batch import batch_process_unprocessed_inbox

    vault = Path(args.vault)
    inbox_dir = vault / "Inbox"
    result = batch_process_unprocessed_inbox(inbox_dir, dry_run=args.dry_run)
    errors = result.get("errors", 0)
    return 1 if errors and errors > 0 else 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    dispatch = {
        "backup": _run_backup,
        "fleeting": _run_fleeting,
        "review": _run_review,
        "inbox": _run_inbox,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
