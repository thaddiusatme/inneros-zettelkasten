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
    
    def _format_auto_promote_preview(self, results: dict) -> None:
        """Format and display auto-promotion preview (dry-run mode)."""
        self._print_header("AUTO-PROMOTION PREVIEW (DRY RUN)")
        would_promote = results.get('would_promote_count', 0)
        print(f"   Would promote: {would_promote} notes")
        
        # Show preview list
        if results.get('preview'):
            self._print_section("NOTES TO BE PROMOTED")
            for item in results['preview']:
                note_name = item.get('note', 'Unknown')
                note_type = item.get('type', 'Unknown')
                quality = item.get('quality', 0.0)
                target = item.get('target', 'Unknown')
                print(f"   📄 {note_name}")
                print(f"      Type: {note_type} → {target}")
                print(f"      Quality: {quality:.2f}")
    
    def _format_auto_promote_results(self, results: dict) -> None:
        """Format and display auto-promotion results."""
        self._print_header("AUTO-PROMOTION RESULTS")
        
        # Summary statistics
        total = results.get('total_candidates', 0)
        promoted = results.get('promoted_count', 0)
        skipped = results.get('skipped_count', 0)
        errors = results.get('error_count', 0)
        
        print(f"   📊 Candidates: {total} notes")
        print(f"   ✅ Promoted: {promoted} notes")
        print(f"   ⚠️  Skipped: {skipped} notes (below threshold)")
        print(f"   🚨 Errors: {errors} notes")
        
        # By-type breakdown
        if results.get('by_type'):
            self._print_section("BY TYPE")
            for note_type, counts in results['by_type'].items():
                promoted_count = counts.get('promoted', 0)
                skipped_count = counts.get('skipped', 0)
                print(f"   {note_type.title()}:")
                print(f"      ✅ Promoted: {promoted_count}")
                print(f"      ⚠️  Skipped: {skipped_count}")
        
        # Show skipped notes
        if results.get('skipped_notes'):
            self._print_section("SKIPPED NOTES")
            for skip in results['skipped_notes'][:5]:  # Show first 5
                note_path = skip.get('path', 'Unknown')
                quality = skip.get('quality', 0.0)
                note_type = skip.get('type', 'Unknown')
                print(f"   📄 {note_path}")
                print(f"      Type: {note_type}, Quality: {quality:.2f}")
        
        # Show errors
        if results.get('errors'):
            self._print_section("ERRORS")
            for error in results['errors']:
                note = error.get('note', 'Unknown')
                error_msg = error.get('error', 'Unknown error')
                print(f"   🚨 {note}: {error_msg}")
    
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
    
    def process_inbox(self, output_format: str = 'normal', fast_mode: bool = False) -> int:
        """
        Process all inbox notes
        
        Args:
            output_format: Output format ('normal' or 'json')
            fast_mode: If True, skip slow AI processing (faster but less analysis)
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                mode_str = " (fast mode - skipping AI)" if fast_mode else ""
                print(f"📥 Processing inbox notes{mode_str}...")
            
            # Process inbox
            results = self.workflow_manager.batch_process_inbox(show_progress=not quiet)
            
            # Format and display output
            if quiet:
                print(json.dumps(results, indent=2, default=str))
            else:
                self._print_header("INBOX PROCESSING RESULTS")
                
                # Display summary (use correct keys from WorkflowManager)
                print(f"   ✅ Processed: {results.get('processed', 0)} notes")
                print(f"   ❌ Failed: {results.get('failed', 0)} notes")
                print(f"   📊 Total: {results.get('total_files', 0)} notes")
                
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
    
    def auto_promote(self, dry_run: bool = False, quality_threshold: float = 0.7,
                     output_format: str = 'normal') -> int:
        """
        Auto-promote notes that meet quality threshold
        
        Args:
            dry_run: If True, show preview without making changes
            quality_threshold: Minimum quality score (0.0-1.0) for promotion
            output_format: Output format ('normal' or 'json')
            
        Returns:
            Exit code (0=success, 1=errors occurred, 2=invalid arguments)
        """
        try:
            # Validate threshold
            if not (0.0 <= quality_threshold <= 1.0):
                print(f"❌ Error: Quality threshold must be between 0.0 and 1.0 (got {quality_threshold})",
                      file=sys.stderr)
                return 2
            
            # Validate vault path exists
            from pathlib import Path
            vault_path_obj = Path(self.vault_path)
            if not vault_path_obj.exists():
                print(f"❌ Error: Vault path does not exist: {self.vault_path}",
                      file=sys.stderr)
                return 1
            
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                mode_str = " (DRY RUN - Preview Only)" if dry_run else ""
                print(f"🚀 Auto-promoting ready notes{mode_str}...")
                print(f"   Quality threshold: {quality_threshold}")
            
            # Call backend
            results = self.workflow_manager.auto_promote_ready_notes(
                dry_run=dry_run,
                quality_threshold=quality_threshold
            )
            
            # Format and display output
            if quiet:
                print(json.dumps(results, indent=2, default=str))
            else:
                # Dry-run preview mode or actual results
                if results.get('dry_run'):
                    self._format_auto_promote_preview(results)
                else:
                    self._format_auto_promote_results(results)
            
            # Exit code based on results
            if results.get('error_count', 0) > 0:
                return 1  # Errors occurred
            return 0  # Success
            
        except Exception as e:
            print(f"❌ Error in auto-promotion: {e}", file=sys.stderr)
            logger.exception("Error in auto_promote command")
            return 1
    
    def repair_metadata(self, execute: bool = False, output_format: str = 'normal') -> int:
        """
        Repair missing frontmatter metadata in Inbox notes
        
        Fixes critical issue where notes missing 'type:' field block auto-promotion.
        Delegates to WorkflowManager.repair_inbox_metadata() following ADR-002 Phase 13.
        
        Args:
            execute: If True, actually modify files. If False (default), preview only.
            output_format: Output format ('normal' or 'json')
            
        Returns:
            Exit code (0=success, 1=errors occurred)
        """
        try:
            quiet = self._is_quiet_mode(output_format)
            
            if not quiet:
                mode_str = " (DRY RUN - Preview Only)" if not execute else ""
                print(f"🔧 Repairing inbox metadata{mode_str}...")
            
            # Call backend
            results = self.workflow_manager.repair_inbox_metadata(execute=execute)
            
            # Format and display output
            if quiet:
                print(json.dumps(results, indent=2, default=str))
            else:
                self._print_header("METADATA REPAIR RESULTS")
                
                # Summary statistics
                scanned = results.get('notes_scanned', 0)
                needed = results.get('repairs_needed', 0)
                made = results.get('repairs_made', 0)
                errors = results.get('errors', [])
                
                print(f"   📊 Notes scanned: {scanned}")
                print(f"   🔍 Repairs needed: {needed}")
                
                if execute:
                    print(f"   ✅ Repairs made: {made}")
                else:
                    print(f"   📝 Would repair: {needed} notes (dry-run mode)")
                
                if errors:
                    print(f"   🚨 Errors: {len(errors)}")
                    self._print_section("ERROR DETAILS")
                    for error in errors[:5]:  # Show first 5 errors
                        note = error.get('note', 'Unknown')
                        error_msg = error.get('error', 'Unknown error')
                        print(f"   ❌ {note}: {error_msg}")
                
                # Helpful message
                if needed > 0 and not execute:
                    print("\n💡 Tip: Add --execute flag to apply repairs")
                elif needed == 0:
                    print("\n✨ All notes have valid metadata!")
            
            # Exit code based on errors
            if len(results.get('errors', [])) > 0:
                return 1  # Errors occurred
            return 0  # Success
            
        except Exception as e:
            print(f"❌ Error repairing metadata: {e}", file=sys.stderr)
            logger.exception("Error in repair_metadata command")
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
  
  # Auto-promote high quality notes
  python core_workflow_cli.py /path/to/vault auto-promote
  
  # Preview auto-promotion (dry-run)
  python core_workflow_cli.py /path/to/vault auto-promote --dry-run
  
  # Custom quality threshold
  python core_workflow_cli.py /path/to/vault auto-promote --quality-threshold 0.8
  
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
        help='Output format'
    )
    process_parser.add_argument(
        '--fast',
        action='store_true',
        help='Skip AI processing for faster execution (basic metadata only)'
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
    
    # Auto-promote command
    auto_promote_parser = subparsers.add_parser(
        'auto-promote',
        help='Automatically promote high-quality notes from Inbox to appropriate directories'
    )
    auto_promote_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview which notes would be promoted without making changes'
    )
    auto_promote_parser.add_argument(
        '--quality-threshold',
        type=float,
        default=0.7,
        help='Minimum quality score (0.0-1.0) required for auto-promotion (default: 0.7)'
    )
    auto_promote_parser.add_argument(
        '--format',
        choices=['normal', 'json'],
        default='normal',
        help='Output format (default: normal)'
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
            return cli.process_inbox(
                output_format=args.format,
                fast_mode=getattr(args, 'fast', False)
            )
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
        elif args.command == 'auto-promote':
            return cli.auto_promote(
                dry_run=args.dry_run,
                quality_threshold=args.quality_threshold,
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


if __name__ == "__main__":
    sys.exit(main())
