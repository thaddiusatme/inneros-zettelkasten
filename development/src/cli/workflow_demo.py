"""
CLI demo for the workflow manager system.
"""

import argparse
import json
import sys
import csv
import re
from pathlib import Path
from datetime import datetime

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.workflow_manager import WorkflowManager
from src.cli.weekly_review_formatter import WeeklyReviewFormatter
from src.ai.import_manager import (
    CSVImportAdapter,
    JSONImportAdapter,
    NoteWriter,
)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n🔄 {title}")
    print("-" * 40)


def display_workflow_status(status):
    """Display workflow status information."""
    print_section("WORKFLOW STATUS")
    
    health_emoji = {
        "healthy": "✅",
        "needs_attention": "⚠️",
        "critical": "🚨"
    }
    
    health = status["health"]
    print(f"   Health Status: {health_emoji.get(health, '❓')} {health.upper()}")
    print(f"   Total Notes: {status['total_notes']:,}")
    
    print(f"\n   Directory Distribution:")
    for directory, count in status["directory_counts"].items():
        print(f"     {directory:<20}: {count:>4}")


def display_ai_features(ai_features):
    """Display AI feature usage statistics."""
    print_section("AI FEATURE USAGE")
    
    total = ai_features["total_analyzed"]
    if total == 0:
        print("   No notes analyzed yet.")
        return
    
    features = [
        ("AI Summaries", ai_features["notes_with_ai_summaries"]),
        ("AI Processing", ai_features["notes_with_ai_processing"]),
        ("AI Tags", ai_features["notes_with_ai_tags"])
    ]
    
    for feature_name, count in features:
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"   {feature_name:<15}: {count:>3}/{total} ({percentage:>5.1f}%)")


def display_recommendations(recommendations):
    """Display workflow recommendations."""
    print_section("WORKFLOW RECOMMENDATIONS")
    
    if not recommendations:
        print("   ✅ No specific recommendations - workflow is running smoothly!")
        return
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")


def display_processing_results(results):
    """Display batch processing results."""
    print_section("PROCESSING RESULTS")
    
    print(f"   Total Files: {results['total_files']}")
    print(f"   Processed: {results['processed']}")
    print(f"   Failed: {results['failed']}")
    
    if results['processed'] > 0:
        print(f"\n   Recommendations Summary:")
        summary = results['summary']
        print(f"     Promote to Permanent: {summary['promote_to_permanent']}")
        print(f"     Move to Fleeting: {summary['move_to_fleeting']}")
        print(f"     Needs Improvement: {summary['needs_improvement']}")


def display_note_processing_result(result):
    """Display individual note processing result."""
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return
    
    print(f"   📄 File: {Path(result['original_file']).name}")
    
    # Display processing results
    processing = result.get("processing", {})
    
    if "tags" in processing:
        tags_info = processing["tags"]
        if "error" in tags_info:
            print(f"      🏷️  Tags: Error - {tags_info['error']}")
        else:
            added_tags = tags_info.get("added", [])
            total_tags = tags_info.get("total", 0)
            if added_tags:
                print(f"      🏷️  Tags: Added {len(added_tags)} tags (total: {total_tags})")
                print(f"           New: {', '.join(added_tags[:3])}{'...' if len(added_tags) > 3 else ''}")
            else:
                print(f"      🏷️  Tags: No new tags added (total: {total_tags})")
    
    if "quality" in processing:
        quality_info = processing["quality"]
        if "error" in quality_info:
            print(f"      ⭐ Quality: Error - {quality_info['error']}")
        else:
            score = quality_info.get("score", 0)
            suggestions = quality_info.get("suggestions", [])
            print(f"      ⭐ Quality: {score:.2f}/1.0")
            if suggestions:
                print(f"           Suggestions: {suggestions[0]}")
    
    if "connections" in processing:
        conn_info = processing["connections"]
        if "error" in conn_info:
            print(f"      🔗 Connections: Error - {conn_info['error']}")
        else:
            similar_notes = conn_info.get("similar_notes", [])
            if similar_notes:
                print(f"      🔗 Connections: Found {len(similar_notes)} similar notes")
                top_match = similar_notes[0]
                print(f"           Top match: {top_match['file']} ({top_match['similarity']:.2f})")
    
    # Display recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"      💡 Recommendations:")
        for rec in recommendations[:2]:  # Show top 2
            action = rec.get("action", "unknown")
            reason = rec.get("reason", "")
            print(f"           • {action.replace('_', ' ').title()}: {reason}")


# ===== Reading Intake Pipeline (PR1 Skeleton) Helpers =====
def _safe_parse_iso_date(value: str) -> datetime:
    """Parse an ISO-like date string; fall back to now on failure."""
    if not value:
        return datetime.now()
    try:
        # Try strict ISO 8601 first
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        # Common fallback patterns (YYYY-MM-DD)
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", value)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception:
                pass
    return datetime.now()


def _plan_filename_for_row(row: dict) -> str:
    """Plan filename according to policy: literature--<saved_at-date>.md"""
    saved_at_raw = row.get("saved_at") or row.get("date") or ""
    dt = _safe_parse_iso_date(saved_at_raw)
    date_part = dt.strftime("%Y-%m-%d")
    return f"literature--{date_part}.md"


def _load_csv_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items()})
    return rows


def _load_json_rows(path: Path) -> list[dict]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return [dict(item) for item in data]
    if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        return [dict(item) for item in data["items"]]
    raise ValueError("Unsupported JSON structure: expected a list or an object with 'items'.")


def interactive_mode(workflow):
    """Run interactive workflow management mode."""
    print_header("INTERACTIVE WORKFLOW MODE")
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
                report = workflow.generate_workflow_report()
                display_workflow_status(report["workflow_status"])
                display_ai_features(report["ai_features"])
            elif command == 'inbox':
                print("Processing inbox notes...")
                results = workflow.batch_process_inbox()
                display_processing_results(results)
            elif command.startswith('promote '):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: promote <filename> [type]")
                    continue
                
                filename = parts[1]
                note_type = parts[2] if len(parts) > 2 else "permanent"
                
                # Find the file in inbox or fleeting
                inbox_path = workflow.inbox_dir / filename
                fleeting_path = workflow.fleeting_dir / filename
                
                if inbox_path.exists():
                    file_path = str(inbox_path)
                elif fleeting_path.exists():
                    file_path = str(fleeting_path)
                else:
                    print(f"File '{filename}' not found in inbox or fleeting notes")
                    continue
                
                result = workflow.promote_note(file_path, note_type)
                if result.get("success"):
                    print(f"✅ Successfully promoted {filename} to {note_type}")
                    if result.get("has_summary"):
                        print("   Added AI summary")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            elif command.startswith('list '):
                directory = command.split()[1].lower()
                dir_map = {
                    "inbox": workflow.inbox_dir,
                    "fleeting": workflow.fleeting_dir,
                    "permanent": workflow.permanent_dir,
                    "archive": workflow.archive_dir
                }
                
                if directory not in dir_map:
                    print("Available directories: inbox, fleeting, permanent, archive")
                    continue
                
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
            elif command == 'report':
                print("Generating workflow report...")
                report = workflow.generate_workflow_report()
                display_workflow_status(report["workflow_status"])
                display_ai_features(report["ai_features"])
                display_recommendations(report["recommendations"])
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Workflow Demo for InnerOS Zettelkasten",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python workflow_demo.py /path/to/zettelkasten --status
  python workflow_demo.py /path/to/zettelkasten --process-inbox
  python workflow_demo.py /path/to/zettelkasten --promote note.md permanent
  python workflow_demo.py /path/to/zettelkasten --interactive
  python workflow_demo.py /path/to/zettelkasten --weekly-review
  python workflow_demo.py /path/to/zettelkasten --weekly-review --export-checklist weekly-review.md
  python workflow_demo.py /path/to/zettelkasten --enhanced-metrics
  python workflow_demo.py /path/to/zettelkasten --enhanced-metrics --format json --export metrics.json
        """
    )
    
    parser.add_argument(
        "directory",
        help="Path to the Zettelkasten root directory"
    )
    
    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group()
    
    action_group.add_argument(
        "--status",
        action="store_true",
        help="Show workflow status"
    )
    
    action_group.add_argument(
        "--process-inbox",
        action="store_true",
        help="Process all inbox notes"
    )
    
    action_group.add_argument(
        "--promote",
        nargs=2,
        metavar=("FILE", "TYPE"),
        help="Promote a note (TYPE: permanent|fleeting)"
    )
    
    action_group.add_argument(
        "--report",
        action="store_true",
        help="Generate full workflow report"
    )
    
    action_group.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    action_group.add_argument(
        "--weekly-review",
        action="store_true",
        help="Generate weekly review checklist"
    )
    
    action_group.add_argument(
        "--enhanced-metrics",
        action="store_true",
        help="Generate enhanced metrics report with orphaned notes, stale notes, and analytics"
    )
    
    action_group.add_argument(
        "--comprehensive-orphaned",
        action="store_true", 
        help="Find ALL orphaned notes across the entire repository (not just workflow directories)"
    )
    
    action_group.add_argument(
        "--remediate-orphans",
        action="store_true",
        help="Remediate orphaned notes by inserting bidirectional links into a target note or generate a checklist"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for reports (default: text)"
    )
    
    parser.add_argument(
        "--export",
        metavar="FILENAME",
        help="Export report to JSON file"
    )
    
    # Weekly review specific options
    parser.add_argument(
        "--export-checklist",
        metavar="PATH",
        help="Export weekly review checklist to markdown file"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview recommendations without processing notes"
    )
    
    # Orphan remediation options
    parser.add_argument(
        "--remediate-mode",
        choices=["link", "checklist"],
        default="link",
        help="Remediation mode: insert links directly (link) or generate a checklist (checklist)"
    )
    parser.add_argument(
        "--remediate-scope",
        choices=["permanent", "fleeting", "all"],
        default="permanent",
        help="Which orphaned notes to consider (default: permanent)"
    )
    parser.add_argument(
        "--remediate-limit",
        type=int,
        default=10,
        help="Maximum number of orphaned notes to remediate (default: 10)"
    )
    parser.add_argument(
        "--target-note",
        metavar="PATH",
        default=None,
        help="Explicit target note/MOC path (relative to vault root or absolute). Defaults to 'Home Note.md' or first MOC."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (disable dry-run) for orphan remediation"
    )
    
    # Reading Intake Pipeline (PR1 Skeleton) options
    action_group.add_argument(
        "--import-csv",
        metavar="PATH",
        help="Import CSV reading list into Inbox (skeleton: validate/dry-run only)"
    )
    action_group.add_argument(
        "--import-json",
        metavar="PATH",
        help="Import JSON reading list into Inbox (skeleton: validate/dry-run only)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate inputs only (no file writes)"
    )
    parser.add_argument(
        "--dest-dir",
        metavar="PATH",
        default=None,
        help="Destination directory for notes (default: knowledge/Inbox)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force write even if (url, saved_at) duplicate detected"
    )
    
    args = parser.parse_args()
    
    # Validate directory
    zettel_dir = Path(args.directory)
    if not zettel_dir.exists():
        print(f"❌ Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    if not zettel_dir.is_dir():
        print(f"❌ Error: '{args.directory}' is not a directory")
        sys.exit(1)
    
    # Initialize workflow manager (with auto-detected vault root when needed)
    def _has_vault_markers(p: Path) -> bool:
        return any((p / d).exists() for d in ["Inbox", "Fleeting Notes", "Permanent Notes"])  # type: ignore

    base_dir = zettel_dir
    auto_note = None

    if not _has_vault_markers(base_dir):
        # Case 1: repo root that contains knowledge/Inbox
        if (zettel_dir / "knowledge" / "Inbox").exists():
            base_dir = zettel_dir / "knowledge"
            auto_note = f"Auto-detected vault root at '{base_dir}' (from '{args.directory}')"
        # Case 2: user passed a subdirectory like Inbox/Fleeting Notes/Permanent Notes
        elif zettel_dir.name in ("Inbox", "Fleeting Notes", "Permanent Notes") and _has_vault_markers(zettel_dir.parent):
            base_dir = zettel_dir.parent
            auto_note = f"Auto-detected vault root at '{base_dir}' (from '{args.directory}')"
        # Case 3: user passed '.' and cwd has knowledge/Inbox
        elif args.directory in (".", "./") and (Path.cwd() / "knowledge" / "Inbox").exists():
            base_dir = Path.cwd() / "knowledge"
            auto_note = f"Auto-detected vault root at '{base_dir}' (from '{args.directory}')"

    print(f"🔄 Initializing workflow for: {base_dir}")
    if auto_note:
        print(f"   ℹ️ {auto_note}")
    workflow = WorkflowManager(str(base_dir))
    
    # Interactive mode
    if args.interactive:
        interactive_mode(workflow)
        return
    
    # Execute actions
    if args.status:
        print("📊 Generating workflow status...")
        report = workflow.generate_workflow_report()
        
        if args.format == "json":
            print(json.dumps(report, indent=2, default=str))
        else:
            print_header("WORKFLOW STATUS REPORT")
            display_workflow_status(report["workflow_status"])
            display_ai_features(report["ai_features"])
            display_recommendations(report["recommendations"])
    
    elif args.process_inbox:
        print("📥 Processing inbox notes...")
        results = workflow.batch_process_inbox()
        
        if args.format == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print_header("INBOX PROCESSING RESULTS")
            display_processing_results(results)
            
            # Show detailed results for first few notes
            if results["results"]:
                print_section("DETAILED RESULTS (First 3)")
                for i, result in enumerate(results["results"][:3], 1):
                    print(f"\n   Note {i}:")
                    display_note_processing_result(result)
    
    elif args.import_csv:
        source_path = Path(args.import_csv)
        if not source_path.exists():
            print(f"❌ Error: CSV file not found: {source_path}")
            sys.exit(1)
        print("📥 Reading Intake (CSV)")
        print(f"   Source: {source_path}")
        try:
            raw_rows = _load_csv_rows(source_path)
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            sys.exit(1)

        print(f"   Loaded {len(raw_rows)} rows")

        # Basic validation preview (as in PR1)
        missing_required = sum(1 for r in raw_rows if not r.get("title") or not r.get("url"))
        if args.validate_only:
            print("   🔎 VALIDATE-ONLY: Basic checks complete")
            if missing_required:
                print(f"   ⚠️  Rows missing required fields (title/url): {missing_required}")
            print("   ✅ No files written (validate-only)")
            return

        # Parse/validate into ImportItem objects
        items = CSVImportAdapter.load(source_path)
        print(f"   Parsed {len(items)} valid items")

        dest_dir = Path(args.dest_dir) if args.dest_dir else (workflow.base_dir / "knowledge" / "Inbox")
        if args.dry_run:
            print("   🔍 DRY RUN MODE - Planned files (no write):")
            writer = NoteWriter(workflow.base_dir)
            preview = [writer._base_filename(it) for it in items][:5]
            for name in preview:
                print(f"      → {dest_dir / name}")
            extra = max(0, len(items) - len(preview))
            if extra:
                print(f"      … and {extra} more")
            return

        # Real write
        writer = NoteWriter(workflow.base_dir)
        written, skipped, paths = writer.write_items(items, dest_dir=dest_dir, force=args.force)
        print("   ✅ Write complete")
        print(f"   Written: {written}, Skipped (duplicates): {skipped}")
        if paths:
            for p in paths[:3]:
                print(f"      + {p}")
            if len(paths) > 3:
                print(f"      … and {len(paths) - 3} more")
        
    elif args.import_json:
        source_path = Path(args.import_json)
        if not source_path.exists():
            print(f"❌ Error: JSON file not found: {source_path}")
            sys.exit(1)
        print("📥 Reading Intake (JSON)")
        print(f"   Source: {source_path}")
        try:
            raw_rows = _load_json_rows(source_path)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            sys.exit(1)

        print(f"   Loaded {len(raw_rows)} items")
        missing_required = sum(1 for r in raw_rows if not r.get("title") or not r.get("url"))
        if args.validate_only:
            print("   🔎 VALIDATE-ONLY: Basic checks complete")
            if missing_required:
                print(f"   ⚠️  Items missing required fields (title/url): {missing_required}")
            print("   ✅ No files written (validate-only)")
            return

        items = JSONImportAdapter.load(source_path)
        print(f"   Parsed {len(items)} valid items")

        dest_dir = Path(args.dest_dir) if args.dest_dir else (workflow.base_dir / "knowledge" / "Inbox")
        if args.dry_run:
            print("   🔍 DRY RUN MODE - Planned files (no write):")
            writer = NoteWriter(workflow.base_dir)
            preview = [writer._base_filename(it) for it in items][:5]
            for name in preview:
                print(f"      → {dest_dir / name}")
            extra = max(0, len(items) - len(preview))
            if extra:
                print(f"      … and {extra} more")
            return

        writer = NoteWriter(workflow.base_dir)
        written, skipped, paths = writer.write_items(items, dest_dir=dest_dir, force=args.force)
        print("   ✅ Write complete")
        print(f"   Written: {written}, Skipped (duplicates): {skipped}")
        if paths:
            for p in paths[:3]:
                print(f"      + {p}")
            if len(paths) > 3:
                print(f"      … and {len(paths) - 3} more")
    
    elif args.report:
        print("📊 Generating comprehensive workflow report...")
        report = workflow.generate_workflow_report()
        
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Report exported to: {args.export}")
        
        if args.format == "json":
            print(json.dumps(report, indent=2, default=str))
        else:
            print_header("COMPREHENSIVE WORKFLOW REPORT")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            display_workflow_status(report["workflow_status"])
            display_ai_features(report["ai_features"])
            display_recommendations(report["recommendations"])
            
            # Show analytics summary
            if "analytics" in report:
                analytics = report["analytics"]
                if "overview" in analytics:
                    print_section("ANALYTICS SUMMARY")
                    overview = analytics["overview"]
                    print(f"   Total Words: {overview.get('total_words', 0):,}")
                    print(f"   Average Quality: {overview.get('average_quality_score', 0):.2f}/1.0")
                    print(f"   High Quality Notes: {analytics.get('quality_metrics', {}).get('high_quality_notes', 0)}")
    
    elif args.weekly_review:
        print("📋 Generating weekly review checklist...")
        
        # Scan for review candidates
        candidates = workflow.scan_review_candidates()
        print(f"   Found {len(candidates)} notes requiring review")
        
        # Generate recommendations (with dry-run consideration)
        if args.dry_run:
            print("   🔍 DRY RUN MODE - No files will be modified")
        
        recommendations = workflow.generate_weekly_recommendations(candidates, dry_run=args.dry_run)
        
        # Format and display checklist
        formatter = WeeklyReviewFormatter()
        
        if args.format == "json":
            print(json.dumps(recommendations, indent=2, default=str))
        else:
            print_header("WEEKLY REVIEW CHECKLIST")
            checklist = formatter.format_checklist(recommendations)
            print(checklist)
        
        # Export checklist if requested
        if args.export_checklist:
            export_path = Path(args.export_checklist)
            result_path = formatter.export_checklist(recommendations, export_path)
            print(f"\n📄 Checklist exported to: {result_path}")
        
        # Show completion message
        summary = recommendations["summary"]
        if summary["total_notes"] > 0:
            print(f"\n✨ Review {summary['total_notes']} notes above and check them off as you complete each action.")
        else:
            print("\n🎉 No notes require review - your workflow is up to date!")
    
    elif args.remediate_orphans:
        print("🔗 Orphaned note remediation...")
        # Default to dry-run unless --apply is provided
        effective_dry_run = not args.apply
        if effective_dry_run:
            print("   🔍 DRY RUN MODE - No files will be modified")
        print(f"   Mode: {args.remediate_mode}, Scope: {args.remediate_scope}, Limit: {args.remediate_limit}")
        if args.target_note:
            print(f"   Target: {args.target_note}")
        
        result = workflow.remediate_orphaned_notes(
            mode=args.remediate_mode,
            scope=args.remediate_scope,
            limit=args.remediate_limit,
            target=args.target_note,
            dry_run=effective_dry_run,
        )
        
        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get("error"):
                print(f"❌ Error: {result['error']}")
            else:
                if args.remediate_mode == "checklist":
                    print_header("ORPHAN REMEDIATION CHECKLIST")
                    print(result.get("checklist_markdown", "(no items)"))
                else:
                    print_header("ORPHAN REMEDIATION RESULTS")
                    summary = result.get("summary", {})
                    print(f"   Considered: {summary.get('considered', 0)}")
                    print(f"   Processed:  {summary.get('processed', 0)}")
                    print(f"   Errors:     {summary.get('errors', 0)}")
                    # Show first few actions
                    actions = result.get("actions", [])
                    if actions:
                        print_section("ACTIONS (First 3)")
                        for a in actions[:3]:
                            if a.get("error"):
                                print(f"   ⚠️  {a['orphan']} → {a['target']} :: {a['error']}")
                            else:
                                print(f"   ✅ {a['orphan']} ↔ {a['target']} (orphan:{a.get('modified_orphan')}, target:{a.get('modified_target')})")
        
        # Export results if requested
        if args.export:
            export_path = Path(args.export)
            with open(export_path, 'w', encoding='utf-8') as f:
                if args.format == "json" or args.remediate_mode == "link":
                    json.dump(result, f, indent=2, default=str)
                else:
                    f.write(result.get("checklist_markdown", ""))
            print(f"\n📄 Remediation output exported to: {export_path}")
    
    elif args.enhanced_metrics:
        print("📊 Generating enhanced metrics report...")
        metrics = workflow.generate_enhanced_metrics()
        formatter = WeeklyReviewFormatter()
        
        if args.format == "json":
            print(json.dumps(metrics, indent=2, default=str))
        else:
            print_header("ENHANCED METRICS REPORT")
            metrics_report = formatter.format_enhanced_metrics(metrics)
            print(metrics_report)
        
        # Export if requested
        if args.export:
            export_path = Path(args.export)
            with open(export_path, 'w', encoding='utf-8') as f:
                if args.format == "json":
                    json.dump(metrics, f, indent=2, default=str)
                else:
                    f.write(metrics_report)
            print(f"\n📄 Enhanced metrics exported to: {export_path}")
        
        # Show summary insights
        summary = metrics["summary"]
        print(f"\n📈 Summary: {summary['total_notes']} total notes, {summary['total_orphaned']} orphaned, {summary['total_stale']} stale")
        if summary['total_orphaned'] > 0 or summary['total_stale'] > 0:
            print("💡 Consider addressing orphaned and stale notes to improve your knowledge graph")
    
    elif args.comprehensive_orphaned:
        print("� Finding ALL orphaned notes across the entire repository...")
        orphaned_notes = workflow.detect_orphaned_notes_comprehensive()
        
        print(f"\n📊 Found {len(orphaned_notes)} orphaned notes:")
        if orphaned_notes:
            for note in orphaned_notes:
                relative_path = note['path'].replace(str(workflow.base_dir) + '/', '')
                print(f"   📄 {note['title']} ({relative_path})")
        else:
            print("   🎉 No orphaned notes found!")
        
        print(f"\n💡 Comparison: Standard detection found 17 orphaned notes in workflow directories")
        print(f"💡 Comprehensive detection found {len(orphaned_notes)} orphaned notes across entire repository")
    
    else:
        # No action specified, show basic status
        print("📊 Showing basic workflow status...")
        report = workflow.generate_workflow_report()
        
        print_header("WORKFLOW OVERVIEW")
        display_workflow_status(report["workflow_status"])
        
        print("\n💡 Use --help to see available actions")
        print("💡 Use --interactive for full workflow management")


if __name__ == "__main__":
    main()
