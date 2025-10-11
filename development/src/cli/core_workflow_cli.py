#!/usr/bin/env python3
"""
Core Workflow CLI - Standalone interface for core workflow operations

Extracted from workflow_demo.py (ADR-004 Iteration 4)
Provides core workflow commands: status, process-inbox, promote, report

Manager: WorkflowManager (has all core workflow methods)
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.workflow_manager import WorkflowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CoreWorkflowCLI:
    """
    Core Workflow CLI - Interface for essential workflow operations
    
    Commands:
    - status: Show workflow status
    - process-inbox: Process all inbox notes
    - promote: Promote a note to permanent/literature
    - report: Generate comprehensive workflow report
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Core Workflow CLI
        
        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path or "."
        self.workflow_manager = WorkflowManager(base_directory=self.vault_path)
        logger.info(f"Core Workflow CLI initialized with vault: {self.vault_path}")
    
    def _print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print("\n" + "="*60)
        print(title)
        print("="*60 + "\n")
    
    def _print_section(self, title: str) -> None:
        """Print a formatted section title."""
        print(f"\n{title}")
        print("-" * len(title))
    
    def _is_quiet_mode(self, output_format: str) -> bool:
        """Check if output should be suppressed (JSON mode)."""
        return output_format == 'json'
    
    def status(self, output_format: str = 'normal') -> int:
        """
        Show workflow status
        
        Args:
            output_format: Output format ('normal' or 'json')
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                print("📊 Generating workflow status...")
            
            # Generate workflow report
            report = self.workflow_manager.generate_workflow_report()
            
            # Format and display output
            if quiet:
                print(json.dumps(report, indent=2, default=str))
            else:
                self._print_header("WORKFLOW STATUS REPORT")
                
                # Display workflow status
                if "workflow_status" in report:
                    status = report["workflow_status"]
                    self._print_section("WORKFLOW STATUS")
                    print(f"   Inbox: {status.get('inbox_count', 0)} notes")
                    print(f"   Fleeting: {status.get('fleeting_count', 0)} notes")
                    print(f"   Permanent: {status.get('permanent_count', 0)} notes")
                    print(f"   Literature: {status.get('literature_count', 0)} notes")
                
                # Display AI features
                if "ai_features" in report:
                    features = report["ai_features"]
                    self._print_section("AI FEATURES")
                    for feature, enabled in features.items():
                        status_icon = "✅" if enabled else "❌"
                        print(f"   {status_icon} {feature}")
                
                # Display recommendations
                if "recommendations" in report:
                    recs = report["recommendations"]
                    if recs:
                        self._print_section("RECOMMENDATIONS")
                        for i, rec in enumerate(recs, 1):
                            print(f"   {i}. {rec}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error generating status: {e}", file=sys.stderr)
            logger.exception("Error in status command")
            return 1
    
    def process_inbox(self, output_format: str = 'normal') -> int:
        """
        Process all inbox notes
        
        Args:
            output_format: Output format ('normal' or 'json')
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                print("📥 Processing inbox notes...")
            
            # Process inbox
            results = self.workflow_manager.batch_process_inbox()
            
            # Format and display output
            if quiet:
                print(json.dumps(results, indent=2, default=str))
            else:
                self._print_header("INBOX PROCESSING RESULTS")
                
                # Display summary
                print(f"   ✅ Processed: {results.get('successful', 0)} notes")
                print(f"   ❌ Failed: {results.get('failed', 0)} notes")
                print(f"   📊 Total: {results.get('total', 0)} notes")
                
                # Show detailed results for first few notes
                if results.get("results"):
                    self._print_section("DETAILED RESULTS (First 3)")
                    for i, result in enumerate(results["results"][:3], 1):
                        print(f"\n   Note {i}:")
                        if result.get("success"):
                            print(f"      ✅ {result.get('note', 'Unknown')}")
                            if result.get("summary"):
                                print(f"      📝 Summary added")
                        else:
                            print(f"      ❌ {result.get('note', 'Unknown')}")
                            print(f"      Error: {result.get('error', 'Unknown error')}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error processing inbox: {e}", file=sys.stderr)
            logger.exception("Error in process_inbox command")
            return 1
    
    def promote(self, note_path: str, target_type: str = 'permanent', 
                output_format: str = 'normal') -> int:
        """
        Promote a note to permanent or literature status
        
        Args:
            note_path: Path to note to promote
            target_type: Target type ('permanent' or 'literature')
            output_format: Output format ('normal' or 'json')
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                print("🚀 Promoting note...")
                print(f"   File: {note_path}")
                print(f"   Target type: {target_type}")
            
            # Resolve file path (absolute, CWD-relative, vault-relative, or by filename)
            candidate = Path(note_path)
            resolved_path = None
            
            try:
                if not candidate.is_absolute():
                    # Try CWD-relative
                    cwd_path = Path.cwd() / candidate
                    if cwd_path.exists():
                        resolved_path = cwd_path
                
                if resolved_path is None:
                    # Try vault-relative
                    vault_path = Path(self.vault_path) / candidate
                    if vault_path.exists():
                        resolved_path = vault_path
                
                if resolved_path is None:
                    # Search by filename in Inbox and Fleeting
                    name_only = candidate.name
                    inbox_candidate = self.workflow_manager.inbox_dir / name_only
                    fleeting_candidate = self.workflow_manager.fleeting_dir / name_only
                    
                    if inbox_candidate.exists():
                        resolved_path = inbox_candidate
                    elif fleeting_candidate.exists():
                        resolved_path = fleeting_candidate
            except Exception:
                resolved_path = None
            
            if resolved_path is None or not resolved_path.exists():
                print(f"❌ Error: File not found: {note_path}", file=sys.stderr)
                return 1
            
            # Promote note
            result = self.workflow_manager.promote_note(str(resolved_path), target_type.lower())
            
            # Format and display output
            if quiet:
                print(json.dumps(result, indent=2, default=str))
            else:
                if result.get("success"):
                    self._print_header("PROMOTION SUCCESSFUL")
                    print(f"   ✅ Promoted to {result.get('type', target_type)}")
                    print(f"   📄 Source: {result.get('source', note_path)}")
                    print(f"   📂 Target: {result.get('target', 'Unknown')}")
                    if result.get("has_summary"):
                        print("   📝 AI summary added")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
                    return 1
            
            return 0
            
        except Exception as e:
            print(f"❌ Error promoting note: {e}", file=sys.stderr)
            logger.exception("Error in promote command")
            return 1
    
    def report(self, output_format: str = 'normal', export_path: Optional[str] = None) -> int:
        """
        Generate comprehensive workflow report
        
        Args:
            output_format: Output format ('normal' or 'json')
            export_path: Optional path to export JSON report
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                print("📊 Generating comprehensive workflow report...")
            
            # Generate workflow report
            report = self.workflow_manager.generate_workflow_report()
            
            # Export if requested
            if export_path:
                with open(export_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                if not quiet:
                    print(f"📄 Report exported to: {export_path}")
            
            # Format and display output
            if quiet:
                print(json.dumps(report, indent=2, default=str))
            else:
                self._print_header("COMPREHENSIVE WORKFLOW REPORT")
                print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Display workflow status
                if "workflow_status" in report:
                    status = report["workflow_status"]
                    self._print_section("WORKFLOW STATUS")
                    print(f"   Inbox: {status.get('inbox_count', 0)} notes")
                    print(f"   Fleeting: {status.get('fleeting_count', 0)} notes")
                    print(f"   Permanent: {status.get('permanent_count', 0)} notes")
                    print(f"   Literature: {status.get('literature_count', 0)} notes")
                
                # Display AI features
                if "ai_features" in report:
                    features = report["ai_features"]
                    self._print_section("AI FEATURES")
                    for feature, enabled in features.items():
                        status_icon = "✅" if enabled else "❌"
                        print(f"   {status_icon} {feature}")
                
                # Display recommendations
                if "recommendations" in report:
                    recs = report["recommendations"]
                    if recs:
                        self._print_section("RECOMMENDATIONS")
                        for i, rec in enumerate(recs, 1):
                            print(f"   {i}. {rec}")
                
                # Display analytics summary
                if "analytics" in report and "overview" in report["analytics"]:
                    analytics = report["analytics"]["overview"]
                    self._print_section("ANALYTICS SUMMARY")
                    print(f"   Total notes: {analytics.get('total_notes', 0)}")
                    print(f"   Total links: {analytics.get('total_links', 0)}")
                    print(f"   Avg quality: {analytics.get('avg_quality', 0):.2f}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error generating report: {e}", file=sys.stderr)
            logger.exception("Error in report command")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for core workflow CLI"""
    parser = argparse.ArgumentParser(
        description="Core Workflow CLI - Essential workflow operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show workflow status
  python core_workflow_cli.py /path/to/vault status
  
  # Process all inbox notes
  python core_workflow_cli.py /path/to/vault process-inbox
  
  # Promote a note
  python core_workflow_cli.py /path/to/vault promote note.md permanent
  
  # Generate comprehensive report
  python core_workflow_cli.py /path/to/vault report --export report.json
        """
    )
    
    parser.add_argument(
        "vault_path",
        help="Path to the Zettelkasten vault root directory"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show workflow status')
    status_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format (default: normal)'
    )
    
    # Process-inbox command
    process_parser = subparsers.add_parser('process-inbox', help='Process all inbox notes')
    process_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format (default: normal)'
    )
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote a note')
    promote_parser.add_argument(
        'note_path',
        help='Path to note to promote'
    )
    promote_parser.add_argument(
        'target_type',
        choices=['permanent', 'literature'],
        help='Target type for promotion'
    )
    promote_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format (default: normal)'
    )
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate comprehensive report')
    report_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format (default: normal)'
    )
    report_parser.add_argument(
        '--export',
        metavar='PATH',
        help='Export report to JSON file'
    )
    
    return parser


def main() -> int:
    """Main entry point for core workflow CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize CLI
        cli = CoreWorkflowCLI(vault_path=args.vault_path)
        
        # Execute command
        if args.command == 'status':
            return cli.status(output_format=args.format)
        elif args.command == 'process-inbox':
            return cli.process_inbox(output_format=args.format)
        elif args.command == 'promote':
            return cli.promote(
                note_path=args.note_path,
                target_type=args.target_type,
                output_format=args.format
            )
        elif args.command == 'report':
            return cli.report(
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


if __name__ == "__main__":
    sys.exit(main())
