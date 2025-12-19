#!/usr/bin/env python3
"""
Weekly Review CLI - Dedicated command-line interface for weekly review workflows

Extracted from workflow_demo.py as part of ADR-004 CLI Layer Extraction.
Provides clean, focused interface for weekly review and metrics without bloating workflow_demo.py.

Architecture:
- Uses AnalyticsManager for metrics generation
- Uses WeeklyReviewFormatter for display formatting
- Argparse for clean command-line interface

Usage:
    # Generate weekly review checklist
    python3 weekly_review_cli.py weekly-review

    # Export checklist to file
    python3 weekly_review_cli.py weekly-review --export weekly-review.md

    # Generate enhanced metrics report
    python3 weekly_review_cli.py enhanced-metrics

    # JSON output for automation
    python3 weekly_review_cli.py enhanced-metrics --format json

    # Export metrics report
    python3 weekly_review_cli.py enhanced-metrics --export metrics.md
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
from src.cli.weekly_review_formatter import WeeklyReviewFormatter
from src.cli.cli_output_contract import build_json_response

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


class WeeklyReviewCLI:
    """
    Dedicated CLI for weekly review and metrics workflows

    Responsibilities:
    - Parse command-line arguments
    - Coordinate WorkflowManager and WeeklyReviewFormatter
    - Handle output formatting (normal/JSON)
    - Manage export functionality
    - Provide user-friendly error messages
    """

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Weekly Review CLI

        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        self.workflow = WorkflowManager(self.vault_path)
        self.formatter = WeeklyReviewFormatter()
        logger.info(f"Weekly Review CLI initialized with vault: {self.vault_path}")

    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60 + "\n")

    def _is_quiet_mode(self, output_format: str) -> bool:
        """Check if output should be suppressed (JSON mode)."""
        return output_format == "json"

    def weekly_review(
        self,
        preview: bool = False,
        output_format: str = "normal",
        export_path: Optional[str] = None,
    ) -> int:
        """
        Generate weekly review checklist

        Args:
            preview: Dry-run mode - no files will be modified
            output_format: 'normal' or 'json'
            export_path: Optional path to export checklist

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            # Display header
            if not quiet:
                print("📋 Generating weekly review checklist...")

            # Scan for review candidates
            candidates = self.workflow.scan_review_candidates()
            if not quiet:
                print(f"   Found {len(candidates)} notes requiring review")

            # Show dry-run notice if applicable
            if preview and not quiet:
                print("   🔍 DRY RUN MODE - No files will be modified")

            # Generate recommendations (pass preview as dry_run to skip AI calls in preview mode)
            recommendations = self.workflow.generate_weekly_recommendations(
                candidates, dry_run=preview
            )

            # Format and display output
            if quiet:
                response = build_json_response(
                    success=True,
                    data=recommendations,
                    errors=[],
                    cli_name="weekly_review_cli",
                    subcommand="weekly-review",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                self._print_header("WEEKLY REVIEW CHECKLIST")
                checklist = self.formatter.format_checklist(recommendations)
                print(checklist)

            # Export checklist if requested
            if export_path:
                export_path_obj = Path(export_path)
                result_path = self.formatter.export_checklist(
                    recommendations, export_path_obj
                )
                if not quiet:
                    print(f"\n📄 Checklist exported to: {result_path}")

            # Show completion message
            if not quiet:
                summary = recommendations["summary"]
                if summary["total_notes"] > 0:
                    print(
                        f"\n✨ Review {summary['total_notes']} notes above and check them off as you complete each action."
                    )
                else:
                    print("\n🎉 No notes require review - your workflow is up to date!")

            return 0

        except Exception as e:
            if quiet:
                response = build_json_response(
                    success=False,
                    data={},
                    errors=[str(e)],
                    cli_name="weekly_review_cli",
                    subcommand="weekly-review",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                print(f"❌ Error generating weekly review: {e}", file=sys.stderr)
            logger.exception("Error in weekly_review")
            return 1

    def enhanced_metrics(
        self, output_format: str = "normal", export_path: Optional[str] = None
    ) -> int:
        """
        Generate enhanced metrics report

        Args:
            output_format: 'normal' or 'json'
            export_path: Optional path to export report

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            # Display header
            if not quiet:
                print("📊 Generating enhanced metrics report...")

            # Generate metrics
            metrics = self.workflow.generate_enhanced_metrics()

            # Format and display output
            if quiet:
                response = build_json_response(
                    success=True,
                    data=metrics,
                    errors=[],
                    cli_name="weekly_review_cli",
                    subcommand="enhanced-metrics",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                self._print_header("ENHANCED METRICS REPORT")
                metrics_report = self.formatter.format_enhanced_metrics(metrics)
                print(metrics_report)

            # Export if requested
            if export_path:
                export_path_obj = Path(export_path)
                with open(export_path_obj, "w", encoding="utf-8") as f:
                    if quiet:
                        json.dump(metrics, f, indent=2, default=str)
                    else:
                        f.write(metrics_report)
                if not quiet:
                    print(f"\n📄 Enhanced metrics exported to: {export_path}")

            # Show summary insights
            if not quiet:
                summary = metrics["summary"]
                print(
                    f"\n📈 Summary: {summary['total_notes']} total notes, {summary['total_orphaned']} orphaned, {summary['total_stale']} stale"
                )
                if summary["total_orphaned"] > 0 or summary["total_stale"] > 0:
                    print(
                        "💡 Consider addressing orphaned and stale notes to improve your knowledge graph"
                    )

            return 0

        except Exception as e:
            if quiet:
                response = build_json_response(
                    success=False,
                    data={},
                    errors=[str(e)],
                    cli_name="weekly_review_cli",
                    subcommand="enhanced-metrics",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                print(f"❌ Error generating enhanced metrics: {e}", file=sys.stderr)
            logger.exception("Error in enhanced_metrics")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for Weekly Review CLI

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Weekly Review and Metrics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate weekly review checklist
  %(prog)s weekly-review
  
  # Export checklist
  %(prog)s weekly-review --export weekly-review.md
  
  # Generate enhanced metrics
  %(prog)s enhanced-metrics
  
  # JSON output for automation
  %(prog)s enhanced-metrics --format json
  
  # Export metrics report
  %(prog)s enhanced-metrics --export metrics.md
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

    # weekly-review subcommand
    weekly_review_parser = subparsers.add_parser(
        "weekly-review", help="Generate weekly review checklist"
    )
    weekly_review_parser.add_argument(
        "--preview",
        action="store_true",
        help="Dry-run mode - show what would be processed without modifying",
    )
    weekly_review_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )
    weekly_review_parser.add_argument(
        "--export", type=str, metavar="PATH", help="Export checklist to markdown file"
    )

    # enhanced-metrics subcommand
    metrics_parser = subparsers.add_parser(
        "enhanced-metrics", help="Generate enhanced metrics report"
    )
    metrics_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )
    metrics_parser.add_argument(
        "--export", type=str, metavar="PATH", help="Export report to file"
    )

    return parser


def main():
    """Main entry point for Weekly Review CLI"""
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
        cli = WeeklyReviewCLI(vault_path=args.vault)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1

    # Execute command
    try:
        if args.command == "weekly-review":
            return cli.weekly_review(
                preview=args.preview, output_format=args.format, export_path=args.export
            )
        elif args.command == "enhanced-metrics":
            return cli.enhanced_metrics(
                output_format=args.format, export_path=args.export
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
