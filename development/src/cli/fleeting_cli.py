#!/usr/bin/env python3
"""
Fleeting Notes CLI - Dedicated command-line interface for fleeting note workflows

Extracted from workflow_demo.py as part of ADR-004 CLI Layer Extraction.
Provides clean, focused interface for fleeting note health monitoring and triage.

**Bug #3 Fix**: Uses WorkflowManager directly instead of buggy adapter
- Bug report: Projects/ACTIVE/bug-fleeting-health-attributeerror-2025-10-10.md
- Root cause: workflow_manager_adapter.py calls self.analytics.analyze_fleeting_notes() which doesn't exist
- Fix: Bypass adapter, use WorkflowManager.generate_fleeting_health_report() directly

Architecture:
- Uses WorkflowManager for fleeting note analysis and triage
- Uses formatter functions for display (imported from workflow_demo temporarily)
- Argparse for clean command-line interface

Usage:
    # Generate fleeting notes health report
    python3 fleeting_cli.py fleeting-health

    # Export health report
    python3 fleeting_cli.py fleeting-health --export health-report.md

    # Generate AI-powered triage report
    python3 fleeting_cli.py fleeting-triage

    # Triage with custom quality threshold
    python3 fleeting_cli.py fleeting-triage --quality-threshold 0.8

    # JSON output for automation
    python3 fleeting_cli.py fleeting-health --format json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.workflow_manager import WorkflowManager
from src.cli.fleeting_formatter import FleetingFormatter
from src.cli.cli_output_contract import build_json_response

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


class FleetingCLI:
    """
    Dedicated CLI for fleeting notes workflows

    Responsibilities:
    - Health monitoring for fleeting notes
    - AI-powered triage with quality assessment
    - Handle output formatting (normal/JSON)
    - Manage export functionality
    - Provide user-friendly error messages

    Bug #3 Fix: Uses WorkflowManager directly to avoid AttributeError in adapter
    """

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Fleeting Notes CLI

        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        # BUG #3 FIX: Use WorkflowManager directly (NOT adapter)
        self.workflow = WorkflowManager(self.vault_path)
        self.formatter = FleetingFormatter()
        logger.info(f"Fleeting CLI initialized with vault: {self.vault_path}")

    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60 + "\n")

    def _print_section(self, title: str) -> None:
        """Print a formatted subsection header."""
        print(f"\n{title}")
        print("-" * len(title))

    def _is_quiet_mode(self, output_format: str) -> bool:
        """Check if output should be suppressed (JSON mode)."""
        return output_format == "json"

    def fleeting_health(
        self, output_format: str = "normal", export_path: Optional[str] = None
    ) -> int:
        """
        Generate fleeting notes health report

        Args:
            output_format: 'normal' or 'json'
            export_path: Optional path to export report

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)
        logger.info(f"cli=fleeting_cli subcommand=fleeting-health vault={self.vault_path} format={output_format}")

        try:
            # Display header
            if not quiet:
                print("📊 Generating fleeting notes health report...")

            # Generate health report - BUG #3 FIX: WorkflowManager has the method
            health_report = self.workflow.generate_fleeting_health_report()

            # Format and display output
            if quiet:
                response = build_json_response(
                    success=True,
                    data=health_report,
                    errors=[],
                    cli_name="fleeting_cli",
                    subcommand="fleeting-health",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                self._print_header("FLEETING NOTES HEALTH REPORT")
                print(self.formatter.display_health_report(health_report))

            # Export if requested
            if export_path:
                export_path_obj = Path(export_path)
                with open(export_path_obj, "w", encoding="utf-8") as f:
                    if quiet:
                        json.dump(health_report, f, indent=2, default=str)
                    else:
                        f.write("# FLEETING NOTES HEALTH REPORT\n\n")
                        f.write(self.formatter.format_health_markdown(health_report))
                if not quiet:
                    print(f"\n📄 Health report exported to: {export_path}")

            return 0

        except Exception as e:
            if quiet:
                response = build_json_response(
                    success=False,
                    data={},
                    errors=[str(e)],
                    cli_name="fleeting_cli",
                    subcommand="fleeting-health",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                print(f"❌ Error generating fleeting health report: {e}", file=sys.stderr)
            logger.exception("Error in fleeting_health")
            return 1

    def fleeting_triage(
        self,
        quality_threshold: Optional[float] = 0.7,
        fast: bool = True,
        output_format: str = "normal",
        export_path: Optional[str] = None,
    ) -> int:
        """
        Generate AI-powered fleeting notes triage report

        Args:
            quality_threshold: Minimum quality score (0.0-1.0)
            fast: Use fast mode for better performance
            output_format: 'normal' or 'json'
            export_path: Optional path to export report

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        # Validate quality threshold
        if quality_threshold is not None and (
            quality_threshold < 0.0 or quality_threshold > 1.0
        ):
            print(
                "❌ Error: Quality threshold must be between 0.0 and 1.0",
                file=sys.stderr,
            )
            return 1

        logger.info(f"cli=fleeting_cli subcommand=fleeting-triage vault={self.vault_path} format={output_format} quality_threshold={quality_threshold} fast={fast}")

        try:
            # Display header
            if not quiet:
                print("📊 Generating AI-powered fleeting notes triage report...")

            # Generate triage report
            triage_report = self.workflow.generate_fleeting_triage_report(
                quality_threshold=quality_threshold, fast=fast
            )

            # Format and display output
            if quiet:
                response = build_json_response(
                    success=True,
                    data=triage_report,
                    errors=[],
                    cli_name="fleeting_cli",
                    subcommand="fleeting-triage",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                self._print_header("FLEETING NOTES TRIAGE REPORT")
                print(self.formatter.display_triage_report(triage_report))

            # Export if requested
            if export_path:
                export_path_obj = Path(export_path)
                with open(export_path_obj, "w", encoding="utf-8") as f:
                    if quiet:
                        json.dump(triage_report, f, indent=2, default=str)
                    else:
                        f.write(self.formatter.format_triage_markdown(triage_report))
                if not quiet:
                    print(f"\n📄 Triage report exported to: {export_path}")

            return 0

        except Exception as e:
            if quiet:
                response = build_json_response(
                    success=False,
                    data={},
                    errors=[str(e)],
                    cli_name="fleeting_cli",
                    subcommand="fleeting-triage",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                print(f"❌ Error generating triage report: {e}", file=sys.stderr)
            logger.exception("Error in fleeting_triage")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for Fleeting Notes CLI

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Fleeting Notes Health and Triage CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate fleeting notes health report
  %(prog)s fleeting-health
  
  # Export health report
  %(prog)s fleeting-health --export health-report.md
  
  # Generate AI-powered triage report
  %(prog)s fleeting-triage
  
  # Triage with custom quality threshold
  %(prog)s fleeting-triage --quality-threshold 0.8
  
  # JSON output for automation
  %(prog)s fleeting-health --format json
        """,
    )

    # Global options
    parser.add_argument(
        "--vault",
        type=str,
        default=".",
        help="Path to vault root directory (default: current directory)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # fleeting-health subcommand
    health_parser = subparsers.add_parser(
        "fleeting-health", help="Generate fleeting notes health report"
    )
    health_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )
    health_parser.add_argument(
        "--export", type=str, metavar="PATH", help="Export report to file"
    )

    # fleeting-triage subcommand
    triage_parser = subparsers.add_parser(
        "fleeting-triage", help="Generate AI-powered triage report for fleeting notes"
    )
    triage_parser.add_argument(
        "--quality-threshold",
        type=float,
        default=0.7,
        help="Minimum quality score threshold (0.0-1.0, default: 0.7)",
    )
    triage_parser.add_argument(
        "--fast",
        action="store_true",
        default=True,
        help="Use fast mode for better performance (default: true)",
    )
    triage_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )
    triage_parser.add_argument(
        "--export", type=str, metavar="PATH", help="Export report to file"
    )

    return parser


def main():
    """Main entry point for Fleeting Notes CLI"""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Check if command was provided
    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    try:
        cli = FleetingCLI(vault_path=args.vault)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1

    # Execute command
    try:
        if args.command == "fleeting-health":
            return cli.fleeting_health(
                output_format=args.format, export_path=args.export
            )
        elif args.command == "fleeting-triage":
            return cli.fleeting_triage(
                quality_threshold=args.quality_threshold,
                fast=args.fast,
                output_format=args.format,
                export_path=args.export,
            )
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        logger.exception("Unexpected error during execution")
        return 1


if __name__ == "__main__":
    sys.exit(main())
