#!/usr/bin/env python3
"""
Safe Workflow CLI - Dedicated command-line interface for safe workflow operations

Extracted from workflow_demo.py as part of ADR-004 CLI Layer Extraction (Iteration 3+).
Provides clean, focused interface for safe processing with backup/rollback capabilities.

Architecture:
- Wraps existing SafeWorkflowCLI utilities (safe_workflow_cli_utils.py)
- Uses WorkflowManager for core operations
- Uses DirectoryOrganizer for backup management
- Argparse for clean command-line interface

Usage:
    # Process inbox with image preservation
    python3 safe_workflow_cli.py process-inbox-safe

    # Batch process with safety guarantees
    python3 safe_workflow_cli.py batch-process-safe --batch-size 20

    # Generate performance report
    python3 safe_workflow_cli.py performance-report

    # Create backup
    python3 safe_workflow_cli.py backup

    # JSON output for automation
    python3 safe_workflow_cli.py performance-report --format json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI as UtilsCLI
from src.cli.safe_workflow_formatter import SafeWorkflowFormatter
from src.utils.directory_organizer import DirectoryOrganizer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


class SafeWorkflowCLI:
    """
    Dedicated CLI for safe workflow operations

    Responsibilities:
    - Safe inbox processing with image preservation
    - Batch processing with safety guarantees
    - Performance and integrity reporting
    - Backup management
    - Handle output formatting (normal/JSON)

    Wraps existing SafeWorkflowCLI utilities for actual implementation
    """

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Safe Workflow CLI

        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        self.safe_cli = UtilsCLI(self.vault_path)
        self.organizer = DirectoryOrganizer(vault_root=self.vault_path)
        self.formatter = SafeWorkflowFormatter()
        logger.info(f"Safe Workflow CLI initialized with vault: {self.vault_path}")

    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60 + "\n")

    def _is_quiet_mode(self, output_format: str) -> bool:
        """Check if output should be suppressed (JSON mode)."""
        return output_format == "json"

    def process_inbox_safe(
        self,
        preserve_images: bool = True,
        show_progress: bool = False,
        output_format: str = "normal",
    ) -> int:
        """
        Process inbox notes with image preservation

        Args:
            preserve_images: Whether to preserve linked images
            show_progress: Show progress during processing
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("🛡️ Processing inbox notes with image preservation...")

            # Execute using utilities
            result = self.safe_cli.execute_command(
                "process-inbox-safe",
                {"progress": show_progress, "preserve_images": preserve_images},
            )

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header("SAFE INBOX PROCESSING COMPLETE")
                print(self.formatter.format_process_inbox_result(result))

            return 0

        except Exception as e:
            print(f"❌ Error processing inbox: {e}", file=sys.stderr)
            logger.exception("Error in process_inbox_safe")
            return 1

    def batch_process_safe(
        self,
        batch_size: int = 10,
        max_concurrent: int = 2,
        output_format: str = "normal",
    ) -> int:
        """
        Batch process with comprehensive safety guarantees

        Args:
            batch_size: Number of notes per batch
            max_concurrent: Maximum concurrent operations
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("🛡️ Batch processing with comprehensive safety guarantees...")

            # Execute using utilities
            result = self.safe_cli.execute_command(
                "batch-process-safe",
                {"batch_size": batch_size, "max_concurrent": max_concurrent},
            )

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header("SAFE BATCH PROCESSING COMPLETE")
                print(self.formatter.format_batch_process_result(result))

            return 0

        except Exception as e:
            print(f"❌ Error in batch processing: {e}", file=sys.stderr)
            logger.exception("Error in batch_process_safe")
            return 1

    def performance_report(self, output_format: str = "normal") -> int:
        """
        Generate performance metrics report

        Args:
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("📊 Generating performance metrics report...")

            # Execute using utilities
            result = self.safe_cli.execute_command(
                "performance-report", {"format": output_format}
            )

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header("PERFORMANCE METRICS REPORT")
                print(self.formatter.format_performance_report(result))

            return 0

        except Exception as e:
            print(f"❌ Error generating performance report: {e}", file=sys.stderr)
            logger.exception("Error in performance_report")
            return 1

    def integrity_report(self, output_format: str = "normal") -> int:
        """
        Generate image integrity report

        Args:
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("🔍 Generating image integrity report...")

            # Execute using utilities
            result = self.safe_cli.execute_command(
                "integrity-report", {"format": output_format}
            )

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header("IMAGE INTEGRITY REPORT")
                print(self.formatter.format_integrity_report(result))

            return 0

        except Exception as e:
            print(f"❌ Error generating integrity report: {e}", file=sys.stderr)
            logger.exception("Error in integrity_report")
            return 1

    def create_backup(self, output_format: str = "normal") -> int:
        """
        Create timestamped backup of vault

        Args:
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("📦 Creating backup...")

            # Use DirectoryOrganizer for backup
            backup_path = self.organizer.create_backup()

            result = {
                "success": True,
                "backup_path": str(backup_path),
                "timestamp": (
                    backup_path.name.split("-backup-")[1]
                    if "-backup-" in backup_path.name
                    else "unknown"
                ),
            }

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header("BACKUP CREATED")
                print(self.formatter.format_backup_created(result))

            return 0

        except Exception as e:
            print(f"❌ Error creating backup: {e}", file=sys.stderr)
            logger.exception("Error in create_backup")
            return 1

    def list_backups(self, output_format: str = "normal") -> int:
        """
        List all existing backups

        Args:
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("📋 Listing backups...")

            # Use DirectoryOrganizer for backup listing
            backups = self.organizer.list_backups()

            result = {
                "success": True,
                "count": len(backups),
                "backups": [{"name": b.name, "path": str(b)} for b in backups],
            }

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header("BACKUP INVENTORY")
                print(self.formatter.format_backup_list(result))

            return 0

        except Exception as e:
            print(f"❌ Error listing backups: {e}", file=sys.stderr)
            logger.exception("Error in list_backups")
            return 1

    def start_safe_session(
        self, session_name: str = "default", output_format: str = "normal"
    ) -> int:
        """
        Start a new concurrent safe processing session (ADR-004 Iteration 5)

        Args:
            session_name: Name for the processing session
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print(f"🚀 Starting safe processing session: {session_name}")

            # Execute using utilities (wraps existing safe_workflow_cli_utils.py)
            result = self.safe_cli.execute_command(
                "start-safe-session",
                {"session_name": session_name, "format": output_format},
            )

            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                self._print_header(f"SAFE SESSION STARTED: {session_name}")
                session_id = result.get("session_id", "unknown")
                print(f"✅ Session ID: {session_id}")
                print(f"📝 Session Name: {session_name}")
                print(f"⏰ Started at: {result.get('start_time', 'unknown')}")
                print("\n💡 Session is now active for concurrent processing")

            return 0

        except Exception as e:
            print(f"❌ Error starting safe session: {e}", file=sys.stderr)
            logger.exception("Error in start_safe_session")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for Safe Workflow CLI

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Safe Workflow Processing CLI with Backup/Rollback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process inbox with image preservation
  %(prog)s process-inbox-safe
  
  # Batch process with safety guarantees
  %(prog)s batch-process-safe --batch-size 20
  
  # Generate performance report
  %(prog)s performance-report
  
  # Create backup
  %(prog)s backup
  
  # JSON output for automation
  %(prog)s performance-report --format json
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

    # process-inbox-safe subcommand
    process_parser = subparsers.add_parser(
        "process-inbox-safe", help="Process inbox notes with image preservation"
    )
    process_parser.add_argument(
        "--no-preserve-images", action="store_true", help="Disable image preservation"
    )
    process_parser.add_argument(
        "--progress", action="store_true", help="Show progress during processing"
    )
    process_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    # batch-process-safe subcommand
    batch_parser = subparsers.add_parser(
        "batch-process-safe", help="Batch process with comprehensive safety guarantees"
    )
    batch_parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of notes per batch (default: 10)",
    )
    batch_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=2,
        help="Maximum concurrent operations (default: 2)",
    )
    batch_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    # performance-report subcommand
    perf_parser = subparsers.add_parser(
        "performance-report", help="Generate performance metrics report"
    )
    perf_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    # integrity-report subcommand
    integrity_parser = subparsers.add_parser(
        "integrity-report", help="Generate image integrity report"
    )
    integrity_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    # backup subcommand
    backup_parser = subparsers.add_parser(
        "backup", help="Create timestamped backup of vault"
    )
    backup_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    # list-backups subcommand
    list_parser = subparsers.add_parser(
        "list-backups", help="List all existing backups"
    )
    list_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    # start-safe-session subcommand (ADR-004 Iteration 5)
    session_parser = subparsers.add_parser(
        "start-safe-session", help="Start a new concurrent safe processing session"
    )
    session_parser.add_argument(
        "session_name",
        type=str,
        nargs="?",
        default="default",
        help="Name for the processing session (default: default)",
    )
    session_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    return parser


def main():
    """Main entry point for Safe Workflow CLI"""
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
        cli = SafeWorkflowCLI(vault_path=args.vault)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1

    # Execute command
    try:
        if args.command == "process-inbox-safe":
            return cli.process_inbox_safe(
                preserve_images=not args.no_preserve_images,
                show_progress=args.progress,
                output_format=args.format,
            )
        elif args.command == "batch-process-safe":
            return cli.batch_process_safe(
                batch_size=args.batch_size,
                max_concurrent=args.max_concurrent,
                output_format=args.format,
            )
        elif args.command == "performance-report":
            return cli.performance_report(output_format=args.format)
        elif args.command == "integrity-report":
            return cli.integrity_report(output_format=args.format)
        elif args.command == "backup":
            return cli.create_backup(output_format=args.format)
        elif args.command == "list-backups":
            return cli.list_backups(output_format=args.format)
        elif args.command == "start-safe-session":
            return cli.start_safe_session(
                session_name=args.session_name, output_format=args.format
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
