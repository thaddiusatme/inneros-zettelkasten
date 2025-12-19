#!/usr/bin/env python3
"""
Screenshot CLI - Dedicated command-line interface for screenshot processing

Extracted from workflow_demo.py as part of ADR-004 CLI Layer Extraction (Issue #39).
Provides clean, focused interface for evening screenshot import automation.

Architecture:
- Uses EveningScreenshotProcessor for screenshot processing
- Argparse for clean command-line interface
- Supports automation requirements: dry-run, progress, JSON output

Usage:
    # Process evening screenshots
    python3 screenshot_cli.py process

    # Dry-run mode (preview without processing)
    python3 screenshot_cli.py process --dry-run

    # With progress reporting
    python3 screenshot_cli.py process --progress

    # Custom OneDrive path
    python3 screenshot_cli.py process --onedrive-path "/path/to/screenshots"

    # JSON output for automation
    python3 screenshot_cli.py process --format json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.cli_output_contract import build_json_response
from src.cli.evening_screenshot_processor import EveningScreenshotProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Default OneDrive screenshot path for Samsung S23
DEFAULT_ONEDRIVE_PATH = str(
    Path.home() / "Library/CloudStorage/OneDrive-Personal/Pictures/Screenshots"
)


class ScreenshotCLI:
    """
    Dedicated CLI for screenshot processing operations

    Responsibilities:
    - Evening screenshot batch processing
    - Handle output formatting (normal/JSON)
    - Support dry-run mode for safe automation
    - Progress reporting for long-running operations

    Uses EveningScreenshotProcessor for actual implementation
    """

    def __init__(
        self, vault_path: Optional[str] = None, onedrive_path: Optional[str] = None
    ):
        """
        Initialize Screenshot CLI

        Args:
            vault_path: Path to vault root (defaults to current directory)
            onedrive_path: Path to OneDrive screenshots folder
        """
        self.vault_path = vault_path or "."
        self.onedrive_path = onedrive_path or DEFAULT_ONEDRIVE_PATH

        # Initialize processor (may be None if OneDrive path doesn't exist)
        try:
            self.processor = EveningScreenshotProcessor(
                onedrive_path=self.onedrive_path, knowledge_path=self.vault_path
            )
        except Exception as e:
            logger.warning(f"Could not initialize processor: {e}")
            self.processor = None

        logger.info(f"Screenshot CLI initialized with vault: {self.vault_path}")

    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60 + "\n")

    def _is_quiet_mode(self, output_format: str) -> bool:
        """Check if output should be suppressed (JSON mode)."""
        return output_format == "json"

    def process_evening_screenshots(
        self,
        dry_run: bool = False,
        progress: bool = False,
        limit: Optional[int] = None,
        output_format: str = "normal",
    ) -> int:
        """
        Process evening screenshots from OneDrive

        Args:
            dry_run: Preview changes without processing
            progress: Show progress reporting
            limit: Maximum number of screenshots to process
            output_format: 'normal' or 'json'

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)

        try:
            if not quiet:
                print("📸 Processing evening screenshots...")
                if dry_run:
                    print("🔍 DRY RUN MODE - No files will be modified")
                if progress:
                    print("📊 Progress reporting enabled")

            # Check if processor is available
            if self.processor is None:
                response = build_json_response(
                    success=False,
                    data={
                        "onedrive_path": self.onedrive_path,
                        "processed_count": 0,
                    },
                    errors=[
                        "Screenshot processor not initialized - OneDrive path not found"
                    ],
                    cli_name="screenshot_cli",
                    subcommand="process",
                )
                if quiet:
                    print(json.dumps(response, indent=2, default=str))
                else:
                    print(f"⚠️ OneDrive path not found: {self.onedrive_path}")
                    print("   Configure --onedrive-path or check OneDrive sync")
                return 0  # Not an error, just no screenshots to process

            # Dry-run mode: just scan and report
            if dry_run:
                screenshots = self.processor.scan_todays_screenshots(limit=limit)
                response = build_json_response(
                    success=True,
                    data={
                        "dry_run": True,
                        "screenshots_found": len(screenshots),
                        "screenshot_paths": [str(p) for p in screenshots[:10]],
                        "onedrive_path": self.onedrive_path,
                    },
                    errors=[],
                    cli_name="screenshot_cli",
                    subcommand="process",
                )

                if quiet:
                    print(json.dumps(response, indent=2, default=str))
                else:
                    self._print_header("SCREENSHOT SCAN (DRY RUN)")
                    print(f"📊 Screenshots found: {len(screenshots)}")
                    if screenshots:
                        print("\nScreenshots to process:")
                        for i, path in enumerate(screenshots[:10], 1):
                            print(f"  {i}. {path.name}")
                        if len(screenshots) > 10:
                            print(f"  ... and {len(screenshots) - 10} more")
                    else:
                        print("   No screenshots found for today")
                    print("\n💡 Run without --dry-run to process these screenshots")

                return 0

            # Actual processing
            if progress and not quiet:
                print("⏳ Starting batch processing...")

            process_result = self.processor.process_evening_batch(limit=limit)

            # Build contract-compliant response
            response = build_json_response(
                success=True,
                data={
                    "processed_count": process_result.get("processed_count", 0),
                    "daily_note_path": str(process_result.get("daily_note_path", "")),
                    "processing_time": process_result.get("processing_time", 0),
                    "backup_path": str(process_result.get("backup_path", "")),
                },
                errors=[],
                cli_name="screenshot_cli",
                subcommand="process",
            )

            if quiet:
                print(json.dumps(response, indent=2, default=str))
            else:
                self._print_header("SCREENSHOT PROCESSING COMPLETE")
                print(
                    f"✅ Screenshots processed: {response['data']['processed_count']}"
                )
                print(f"📄 Daily note: {response['data']['daily_note_path']}")
                print(f"⏱️  Processing time: {response['data']['processing_time']:.1f}s")
                if response["data"].get("backup_path"):
                    print(f"💾 Backup: {response['data']['backup_path']}")

            return 0

        except Exception as e:
            error_msg = str(e)
            if quiet:
                response = build_json_response(
                    success=False,
                    data={"processed_count": 0},
                    errors=[error_msg],
                    cli_name="screenshot_cli",
                    subcommand="process",
                )
                print(json.dumps(response, indent=2, default=str))
            else:
                print(f"❌ Error processing screenshots: {e}", file=sys.stderr)
            logger.exception("Error in process_evening_screenshots")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for Screenshot CLI

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Screenshot Processing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process evening screenshots
  %(prog)s process
  
  # Dry-run mode (preview)
  %(prog)s process --dry-run
  
  # With progress reporting
  %(prog)s process --progress
  
  # Custom OneDrive path
  %(prog)s process --onedrive-path "/path/to/screenshots"
  
  # JSON output for automation
  %(prog)s process --format json
        """,
    )

    # Global options
    parser.add_argument(
        "--vault",
        type=str,
        default=".",
        help="Path to vault root directory (default: current directory)",
    )
    parser.add_argument(
        "--onedrive-path",
        type=str,
        default=None,
        help=f"Path to OneDrive screenshots folder (default: {DEFAULT_ONEDRIVE_PATH})",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # process subcommand
    process_parser = subparsers.add_parser(
        "process", help="Process evening screenshots from OneDrive"
    )
    process_parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without processing"
    )
    process_parser.add_argument(
        "--progress", action="store_true", help="Show progress reporting"
    )
    process_parser.add_argument(
        "--limit", type=int, default=None, help="Maximum screenshots to process"
    )
    process_parser.add_argument(
        "--format", choices=["normal", "json"], default="normal", help="Output format"
    )

    return parser


def main() -> int:
    """Main entry point for Screenshot CLI"""
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
        cli = ScreenshotCLI(vault_path=args.vault, onedrive_path=args.onedrive_path)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1

    # Execute command
    try:
        if args.command == "process":
            return cli.process_evening_screenshots(
                dry_run=args.dry_run,
                progress=args.progress,
                limit=args.limit,
                output_format=args.format,
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
