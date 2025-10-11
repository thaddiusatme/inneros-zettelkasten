#!/usr/bin/env python3
"""
Interactive CLI - Dedicated command-line interface for interactive workflow mode

Extracted from workflow_demo.py as part of ADR-004 CLI Layer Extraction (Iteration 5).
Provides interactive workflow management with command loop.

Architecture:
- Uses WorkflowManager for workflow operations
- Interactive command loop with user input
- Supports commands: status, inbox, promote, report, list, help, quit

Usage:
    # Start interactive mode
    python3 interactive_cli.py interactive
    
    # With specific vault path
    python3 interactive_cli.py interactive --vault /path/to/vault
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.workflow_manager import WorkflowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InteractiveCLI:
    """
    Dedicated CLI for interactive workflow management
    
    Responsibilities:
    - Interactive command loop
    - Workflow operations (status, inbox, promote, report, list)
    - User-friendly command interface
    
    Uses WorkflowManager for actual operations
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Interactive CLI
        
        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        self.workflow = WorkflowManager(self.vault_path)
        logger.info(f"Interactive CLI initialized with vault: {self.vault_path}")
    
    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "="*60)
        print(title)
        print("="*60 + "\n")
    
    def run_interactive(self) -> int:
        """
        Run interactive workflow management mode
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            self._print_header("INTERACTIVE WORKFLOW MODE")
            print("Available commands:")
            print("  'status' - Show workflow status")
            print("  'inbox' - Process inbox notes")
            print("  'promote <file> [type]' - Promote a note (type: permanent|fleeting)")
            print("  'report' - Generate full workflow report")
            print("  'list <directory>' - List notes in directory (inbox|fleeting|permanent)")
            print("  'help' - Show this help")
            print("  'quit' - Exit interactive mode")
            
            while True:
                try:
                    command = input("\n🔄 workflow> ").strip()
                    
                    if command == 'quit':
                        break
                    elif command == 'help':
                        print("Available commands:")
                        print("  status, inbox, promote <file> [type], report, list <dir>, help, quit")
                    elif command == 'status':
                        report = self.workflow.generate_workflow_report()
                        self._display_workflow_status(report.get("workflow_status", {}))
                    elif command == 'inbox':
                        print("Processing inbox notes...")
                        results = self.workflow.batch_process_inbox()
                        print(f"✅ Processed {len(results)} notes")
                    elif command.startswith('promote '):
                        self._handle_promote_command(command)
                    elif command.startswith('list '):
                        self._handle_list_command(command)
                    elif command == 'report':
                        print("Generating workflow report...")
                        report = self.workflow.generate_workflow_report()
                        self._display_workflow_status(report.get("workflow_status", {}))
                    else:
                        print("Unknown command. Type 'help' for available commands.")
                        
                except KeyboardInterrupt:
                    print("\nExiting interactive mode...")
                    break
                except Exception as e:
                    print(f"Error: {e}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error in interactive mode: {e}", file=sys.stderr)
            logger.exception("Error in run_interactive")
            return 1
    
    def _handle_promote_command(self, command: str) -> None:
        """Handle promote command parsing and execution."""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: promote <filename> [type]")
            return
        
        filename = parts[1]
        note_type = parts[2] if len(parts) > 2 else "permanent"
        
        # Find the file in inbox or fleeting
        inbox_path = Path(self.vault_path) / "Inbox" / filename
        fleeting_path = Path(self.vault_path) / "Fleeting Notes" / filename
        
        if inbox_path.exists():
            file_path = str(inbox_path)
        elif fleeting_path.exists():
            file_path = str(fleeting_path)
        else:
            print(f"File '{filename}' not found in inbox or fleeting notes")
            return
        
        try:
            result = self.workflow.promote_note(file_path, note_type)
            if result.get("success"):
                print(f"✅ Successfully promoted {filename} to {note_type}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Error promoting note: {e}")
    
    def _handle_list_command(self, command: str) -> None:
        """Handle list command parsing and execution."""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: list <directory>")
            print("Available directories: inbox, fleeting, permanent, archive")
            return
        
        directory = parts[1].lower()
        dir_map = {
            "inbox": Path(self.vault_path) / "Inbox",
            "fleeting": Path(self.vault_path) / "Fleeting Notes",
            "permanent": Path(self.vault_path) / "Permanent Notes",
            "archive": Path(self.vault_path) / "Archive"
        }
        
        if directory not in dir_map:
            print("Available directories: inbox, fleeting, permanent, archive")
            return
        
        target_dir = dir_map[directory]
        if target_dir.exists():
            md_files = list(target_dir.glob("*.md"))
            if md_files:
                print(f"Notes in {directory}:")
                for i, file_path in enumerate(md_files, 1):
                    print(f"   {i}. {file_path.name}")
            else:
                print(f"No notes found in {directory}")
        else:
            print(f"Directory {directory} does not exist")
    
    def _display_workflow_status(self, status: dict) -> None:
        """Display workflow status in readable format."""
        print("\n📊 Workflow Status:")
        print(f"  Inbox notes: {status.get('inbox_count', 0)}")
        print(f"  Fleeting notes: {status.get('fleeting_count', 0)}")
        print(f"  Permanent notes: {status.get('permanent_count', 0)}")
        print(f"  Total notes: {status.get('total_notes', 0)}")


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for Interactive CLI
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Interactive Workflow Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive mode
  %(prog)s interactive
  
  # With specific vault path
  %(prog)s interactive --vault /path/to/vault
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
    
    # interactive subcommand
    subparsers.add_parser(
        'interactive',
        help='Run interactive workflow management mode'
    )
    
    return parser


def main():
    """Main entry point for Interactive CLI"""
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
        cli = InteractiveCLI(vault_path=args.vault)
    except Exception as e:
        print(f"❌ Error initializing CLI: {e}", file=sys.stderr)
        return 1
    
    # Execute command
    try:
        if args.command == 'interactive':
            return cli.run_interactive()
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
