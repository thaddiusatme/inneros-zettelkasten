#!/usr/bin/env python3
"""
YouTube CLI - Dedicated command-line interface for YouTube note processing

Built on top of YouTubeCLIProcessor and utility classes from TDD Iteration 3.
Provides clean, focused interface for YouTube workflow without bloating workflow_demo.py.

Architecture:
- Uses YouTubeCLIProcessor for all processing logic
- Uses CLIOutputFormatter for consistent display
- Uses CLIExportManager for report generation
- Argparse for clean command-line interface

Usage:
    # Process single note
    python3 youtube_cli.py process-note path/to/note.md
    
    # Batch process all YouTube notes in Inbox
    python3 youtube_cli.py batch-process
    
    # Preview mode (no modifications)
    python3 youtube_cli.py batch-process --preview
    
    # JSON output for automation
    python3 youtube_cli.py batch-process --format json
    
    # Export report
    python3 youtube_cli.py batch-process --export report.md
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.youtube_cli_utils import (
    YouTubeCLIProcessor,
    CLIOutputFormatter,
    CLIExportManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeCLI:
    """
    Dedicated CLI for YouTube note processing workflows
    
    Responsibilities:
    - Parse command-line arguments
    - Coordinate YouTubeCLIProcessor and formatters
    - Handle output formatting (normal/JSON)
    - Manage export functionality
    - Provide user-friendly error messages
    """

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize YouTube CLI
        
        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        self.processor = YouTubeCLIProcessor(self.vault_path)
        logger.info(f"YouTube CLI initialized with vault: {self.vault_path}")

    def process_single_note(self, note_path: str, preview: bool = False,
                          min_quality: Optional[float] = None,
                          categories: Optional[str] = None,
                          output_format: str = 'normal') -> int:
        """
        Process a single YouTube note
        
        Args:
            note_path: Path to note file
            preview: Show quotes without modifying
            min_quality: Minimum relevance score (0.0-1.0)
            categories: Comma-separated list of categories
            output_format: 'normal' or 'json'
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        note_path_obj = Path(note_path)

        # Parse categories if provided
        category_list = None
        if categories:
            category_list = [c.strip() for c in categories.split(',')]

        # Determine quiet mode (for JSON output)
        quiet_mode = (output_format == 'json')
        formatter = CLIOutputFormatter(quiet_mode=quiet_mode)

        # Process note
        if not quiet_mode:
            print(f"🔄 Processing YouTube note: {note_path_obj.name}")
            if preview:
                print("   ℹ️ Preview mode - no modifications will be made")

        result = self.processor.process_single_note(
            note_path_obj,
            preview=preview,
            min_quality=min_quality,
            categories=category_list
        )

        # Format output
        if output_format == 'json':
            import json
            print(json.dumps({
                'success': result.success,
                'note_path': str(result.note_path),
                'quotes_inserted': result.quotes_inserted,
                'error_message': result.error_message,
                'processing_time': result.processing_time
            }, indent=2))
        else:
            formatter.print_output(formatter.format_single_result(result))

        return 0 if result.success else 1

    def batch_process(self, preview: bool = False,
                     min_quality: Optional[float] = None,
                     categories: Optional[str] = None,
                     output_format: str = 'normal',
                     export_path: Optional[str] = None) -> int:
        """
        Batch process all YouTube notes in Inbox
        
        Args:
            preview: Show what would be processed without modifying
            min_quality: Minimum relevance score (0.0-1.0)
            categories: Comma-separated list of categories
            output_format: 'normal' or 'json'
            export_path: Optional path to export report
            
        Returns:
            Exit code (0 for success, 1 for any failures)
        """
        # Parse categories if provided
        category_list = None
        if categories:
            category_list = [c.strip() for c in categories.split(',')]

        # Determine quiet mode (for JSON output)
        quiet_mode = (output_format == 'json')
        formatter = CLIOutputFormatter(quiet_mode=quiet_mode)

        # Display header
        if not quiet_mode:
            print("🎬 YouTube Batch Processing")
            print(f"   📁 Vault: {self.vault_path}")
            print(f"   📥 Inbox: {self.processor.inbox_dir}")
            if preview:
                print("   ℹ️ Preview mode - no modifications will be made")
            print()

        # Create backup before apply operations (if not preview)
        if not preview:
            from src.automation.youtube_monitoring import backup_status_store
            status_file = Path(self.vault_path) / "youtube_status.json"
            backup_dir = Path(self.vault_path) / "backups"
            if status_file.exists():
                backup_path = backup_status_store(status_file, backup_dir)
                if backup_path and not quiet_mode:
                    print(f"💾 Status backup created: {backup_path.name}")

        # Process batch
        stats = self.processor.process_batch(
            preview=preview,
            min_quality=min_quality,
            categories=category_list,
            quiet_mode=quiet_mode
        )

        # Format output
        if output_format == 'json':
            print(formatter.format_json_output(stats))
        else:
            summary = formatter.format_batch_summary(stats)
            formatter.print_output(summary)

        # Export if requested
        if export_path and stats.total_notes > 0:
            export_path_obj = Path(export_path)
            success = CLIExportManager.export_markdown_report(
                stats,
                export_path_obj,
                []  # We don't track individual results in batch mode yet
            )
            if success and not quiet_mode:
                print(f"\n✅ Report exported to: {export_path}")
            elif not success and not quiet_mode:
                print(f"\n❌ Failed to export report to: {export_path}")

        # Return exit code (0 if all successful, 1 if any failures)
        return 0 if stats.failed == 0 else 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for YouTube CLI
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='YouTube Note Processing CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single note
  %(prog)s process-note knowledge/Inbox/youtube-note.md
  
  # Batch process with preview
  %(prog)s batch-process --preview
  
  # JSON output for automation
  %(prog)s batch-process --format json
  
  # Export report
  %(prog)s batch-process --export report.md
  
  # Quality filtering
  %(prog)s batch-process --min-quality 0.7
  
  # Category selection
  %(prog)s batch-process --categories "key_insights,actionable"
        """
    )

    # Global options
    parser.add_argument(
        '--vault',
        type=str,
        default='.',
        help='Path to vault root directory (default: current directory)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # process-note subcommand
    process_note_parser = subparsers.add_parser(
        'process-note',
        help='Process a single YouTube note'
    )
    process_note_parser.add_argument(
        'note_path',
        type=str,
        help='Path to YouTube note file'
    )
    process_note_parser.add_argument(
        '--preview',
        action='store_true',
        help='Show quotes without modifying note'
    )
    process_note_parser.add_argument(
        '--min-quality',
        type=float,
        help='Minimum relevance score (0.0-1.0)'
    )
    process_note_parser.add_argument(
        '--categories',
        type=str,
        help='Comma-separated list of categories (e.g., "key_insights,actionable")'
    )
    process_note_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format'
    )

    # batch-process subcommand
    batch_parser = subparsers.add_parser(
        'batch-process',
        help='Batch process all YouTube notes in Inbox'
    )
    batch_parser.add_argument(
        '--preview',
        action='store_true',
        help='Show what would be processed without modifying'
    )
    batch_parser.add_argument(
        '--min-quality',
        type=float,
        help='Minimum relevance score (0.0-1.0)'
    )
    batch_parser.add_argument(
        '--categories',
        type=str,
        help='Comma-separated list of categories'
    )
    batch_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format'
    )
    batch_parser.add_argument(
        '--export',
        type=str,
        metavar='PATH',
        help='Export report to markdown file'
    )

    return parser


def main():
    """Main entry point for YouTube CLI"""
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
        cli = YouTubeCLI(vault_path=args.vault)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1

    # Execute command
    try:
        if args.command == 'process-note':
            return cli.process_single_note(
                note_path=args.note_path,
                preview=args.preview,
                min_quality=args.min_quality,
                categories=args.categories,
                output_format=args.format
            )
        elif args.command == 'batch-process':
            return cli.batch_process(
                preview=args.preview,
                min_quality=args.min_quality,
                categories=args.categories,
                output_format=args.format,
                export_path=args.export
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


if __name__ == '__main__':
    sys.exit(main())
