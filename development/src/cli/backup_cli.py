#!/usr/bin/env python3
"""
Backup CLI - Dedicated command-line interface for backup management operations

Extracted from workflow_demo.py as part of ADR-004 CLI Layer Extraction (Iteration 5).
Provides clean, focused interface for backup pruning and management.

Architecture:
- Uses DirectoryOrganizer for backup operations
- Argparse for clean command-line interface
- Minimal wrapping of existing functionality

Usage:
    # Prune old backups (keep 5 most recent)
    python3 backup_cli.py prune-backups --keep 5
    
    # Dry-run mode
    python3 backup_cli.py prune-backups --keep 3 --dry-run
    
    # JSON output for automation
    python3 backup_cli.py prune-backups --keep 5 --format json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.directory_organizer import DirectoryOrganizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupCLI:
    """
    Dedicated CLI for backup management operations
    
    Responsibilities:
    - Backup pruning (keep N most recent)
    - Handle output formatting (normal/JSON)
    
    Uses DirectoryOrganizer for actual implementation
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Backup CLI
        
        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        self.organizer = DirectoryOrganizer(vault_root=self.vault_path)
        logger.info(f"Backup CLI initialized with vault: {self.vault_path}")
    
    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "="*60)
        print(title)
        print("="*60 + "\n")
    
    def _is_quiet_mode(self, output_format: str) -> bool:
        """Check if output should be suppressed (JSON mode)."""
        return output_format == 'json'
    
    def prune_backups(self, keep: int = 5, dry_run: bool = False,
                     output_format: str = 'normal') -> int:
        """
        Remove old backup directories (keeping N most recent)
        
        Args:
            keep: Number of recent backups to keep
            dry_run: Preview changes without deleting
            output_format: 'normal' or 'json'
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        quiet = self._is_quiet_mode(output_format)
        
        try:
            if not quiet:
                print(f"🗑️  Pruning backups (keeping {keep} most recent)...")
                if dry_run:
                    print("🔍 Dry run mode - no files will be deleted")
            
            # Execute using DirectoryOrganizer
            prune_result = self.organizer.prune_backups(keep=keep, dry_run=dry_run)
            
            # Format and display output
            if quiet:
                print(json.dumps(prune_result, indent=2, default=str))
            else:
                self._print_header("BACKUP PRUNING RESULT")
                print(f"📊 Total backups found: {prune_result.get('total_backups', 0)}")
                print(f"✅ Backups to keep: {keep}")
                print(f"🗑️  Backups to prune: {len(prune_result.get('to_prune', []))}")
                
                if prune_result.get('to_prune'):
                    print("\nBackups marked for deletion:")
                    for backup in prune_result['to_prune']:
                        print(f"  - {backup}")
                    
                    if dry_run:
                        print("\n💡 Run without --dry-run to actually delete these backups")
                else:
                    print("\n✅ No backups need pruning")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error pruning backups: {e}", file=sys.stderr)
            logger.exception("Error in prune_backups")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for Backup CLI
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Backup Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Prune backups (keep 5 most recent)
  %(prog)s prune-backups --keep 5
  
  # Dry-run mode
  %(prog)s prune-backups --keep 3 --dry-run
  
  # JSON output for automation
  %(prog)s prune-backups --keep 5 --format json
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
    
    # prune-backups subcommand
    prune_parser = subparsers.add_parser(
        'prune-backups',
        help='Remove old backup directories'
    )
    prune_parser.add_argument(
        '--keep',
        type=int,
        required=True,
        help='Number of recent backups to keep'
    )
    prune_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without deleting'
    )
    prune_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format'
    )
    
    return parser


def main():
    """Main entry point for Backup CLI"""
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
        cli = BackupCLI(vault_path=args.vault)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1
    
    # Execute command
    try:
        if args.command == 'prune-backups':
            return cli.prune_backups(
                keep=args.keep,
                dry_run=args.dry_run,
                output_format=args.format
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
