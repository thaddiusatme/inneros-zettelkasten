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
from src.utils.directory_organizer import DirectoryOrganizer
from src.ai.import_manager import (
    CSVImportAdapter,
    JSONImportAdapter,
    NoteWriter,
)
from src.cli.evening_screenshot_processor import EveningScreenshotProcessor
from src.cli.evening_screenshot_cli_utils import (
    EveningScreenshotCLIOrchestrator,
    CLIProgressReporter,
    ConfigurationManager,
    CLIOutputFormatter,
    CLIExportManager
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


def display_fleeting_health_report(health_report):
    """Display fleeting notes health report."""
    # Health status with emoji
    status_emoji = {
        "HEALTHY": "✅",
        "ATTENTION": "⚠️", 
        "CRITICAL": "🚨"
    }
    
    status = health_report["health_status"]
    print(f"   Health Status: {status_emoji.get(status, '❓')} {status}")
    print(f"   Total Notes: {health_report['total_count']}")
    
    # Age distribution
    print_section("AGE DISTRIBUTION")
    distribution = health_report["age_distribution"]
    print(f"   New (0-7 days):     {distribution['new']:>3}")
    print(f"   Recent (8-30 days): {distribution['recent']:>3}")
    print(f"   Stale (31-90 days): {distribution['stale']:>3}")
    print(f"   Old (90+ days):     {distribution['old']:>3}")
    
    # Summary
    print_section("SUMMARY")
    print(f"   {health_report['summary']}")
    
    # Recommendations
    print_section("RECOMMENDATIONS")
    for i, rec in enumerate(health_report["recommendations"], 1):
        print(f"   {i}. {rec}")
    
    # Show oldest notes if any
    if health_report.get("oldest_notes"):
        print_section("OLDEST NOTES (Priority Processing)")
        for note in health_report["oldest_notes"][:3]:  # Show top 3
            created = note["created"]
            if isinstance(created, str):
                created = datetime.fromisoformat(created)
            age_days = (datetime.now() - created).days
            print(f"   📄 {note['name']} ({age_days} days old)")


def format_fleeting_health_report_markdown(health_report):
    """Format fleeting health report as markdown."""
    lines = []
    
    # Status
    status = health_report["health_status"]
    lines.append(f"**Health Status:** {status}")
    lines.append(f"**Total Notes:** {health_report['total_count']}")
    lines.append("")
    
    # Age Distribution
    lines.append("## Age Distribution")
    distribution = health_report["age_distribution"]
    lines.append(f"- New (0-7 days): {distribution['new']}")
    lines.append(f"- Recent (8-30 days): {distribution['recent']}")
    lines.append(f"- Stale (31-90 days): {distribution['stale']}")
    lines.append(f"- Old (90+ days): {distribution['old']}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append(health_report['summary'])
    lines.append("")
    
    # Recommendations
    lines.append("## Recommendations")
    for i, rec in enumerate(health_report["recommendations"], 1):
        lines.append(f"{i}. {rec}")
    lines.append("")
    
    # Oldest notes
    if health_report.get("oldest_notes"):
        lines.append("## Oldest Notes (Priority Processing)")
        for note in health_report["oldest_notes"][:5]:
            created = note["created"]
            if isinstance(created, str):
                created = datetime.fromisoformat(created)
            age_days = (datetime.now() - created).days
            lines.append(f"- {note['name']} ({age_days} days old)")
    
    return "\n".join(lines)


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


def display_fleeting_triage_report(triage_report):
    """Display a formatted fleeting triage report."""
    print_section("QUALITY ASSESSMENT")
    print(f"   Total notes processed: {triage_report['total_notes_processed']}")
    
    # Quality distribution
    quality_dist = triage_report["quality_distribution"]
    print(f"   High Quality (>0.7): {quality_dist.get('high', 0)}")
    print(f"   Medium Quality (0.4-0.7): {quality_dist.get('medium', 0)}")
    print(f"   Low Quality (<0.4): {quality_dist.get('low', 0)}")
    
    if triage_report.get("quality_threshold"):
        print(f"   Quality threshold: {triage_report['quality_threshold']}")
        filtered_count = triage_report.get("filtered_count", 0)
        print(f"   Notes filtered by quality threshold: {filtered_count}")
    
    print_section("TRIAGE RECOMMENDATIONS")
    recommendations = triage_report["recommendations"]
    
    # Group recommendations by action
    action_groups = {}
    for rec in recommendations:
        action = rec["action"]
        if action not in action_groups:
            action_groups[action] = []
        action_groups[action].append(rec)
    
    for action, recs in action_groups.items():
        action_emoji = "✅" if "Promote" in action else "⚠️" if "Enhancement" in action else "🚨"
        print(f"   {action_emoji} {action}: {len(recs)} notes")
        for rec in recs[:3]:  # Show top 3 per category
            note_name = Path(rec["note_path"]).stem
            quality = rec["quality_score"]
            print(f"      📄 {note_name} (quality: {quality:.2f})")
        if len(recs) > 3:
            print(f"      ... and {len(recs) - 3} more")
    
    print_section("BATCH PROCESSING RESULTS")
    processing_time = triage_report.get("processing_time", 0)
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Notes per second: {triage_report['total_notes_processed'] / max(processing_time, 0.1):.1f}")


def format_fleeting_triage_report_markdown(triage_report):
    """Format fleeting triage report for markdown export."""
    lines = []
    lines.append("# Fleeting Notes Triage Report")
    lines.append("")
    lines.append(f"**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # Quality Assessment
    lines.append("## Quality Assessment")
    lines.append("")
    lines.append(f"**Total notes processed**: {triage_report['total_notes_processed']}")
    
    quality_dist = triage_report["quality_distribution"]
    lines.append(f"- High Quality (>0.7): {quality_dist.get('high', 0)}")
    lines.append(f"- Medium Quality (0.4-0.7): {quality_dist.get('medium', 0)}")
    lines.append(f"- Low Quality (<0.4): {quality_dist.get('low', 0)}")
    lines.append("")
    
    if triage_report.get("quality_threshold"):
        lines.append(f"**Quality threshold applied**: {triage_report['quality_threshold']}")
        lines.append("")
    
    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    
    for rec in triage_report["recommendations"]:
        note_name = Path(rec["note_path"]).stem
        quality = rec["quality_score"]
        action = rec["action"]
        rationale = rec["rationale"]
        
        lines.append(f"### {note_name}")
        lines.append(f"- **Quality Score**: {quality:.2f}")
        lines.append(f"- **Recommended Action**: {action}")
        lines.append(f"- **Rationale**: {rationale}")
        lines.append("")
    
    return "\n".join(lines)


def display_promotion_results(promotion_result):
    """Display formatted promotion results."""
    print_section("PROMOTION SUMMARY")
    
    if promotion_result.get("preview_mode"):
        print("   🔍 PREVIEW MODE - No changes made")
        
    if promotion_result.get("batch_mode"):
        print(f"   Batch promotion with quality threshold: {promotion_result.get('quality_threshold', 0.7)}")
    
    promoted_notes = promotion_result.get("promoted_notes", [])
    print(f"   Total notes processed: {len(promoted_notes)}")
    
    if not promoted_notes:
        print("   ⚠️  No notes were promoted")
        return
        
    print_section("PROMOTED NOTES")
    for note in promoted_notes:
        note_name = Path(note["note_path"]).stem
        target_type = note.get("target_type", "permanent")
        quality_score = note.get("quality_score", 0)
        
        print(f"   ✅ {note_name}")
        print(f"      📄 Promoted to: {target_type.title()} Notes")
        print(f"      ⭐ Quality score: {quality_score:.2f}")
        if note.get("target_path"):
            print(f"      📁 New location: {note['target_path']}")
        
        # Show any errors or warnings
        if note.get("error"):
            print(f"      ❌ Error: {note['error']}")
        elif note.get("warning"):
            print(f"      ⚠️  Warning: {note['warning']}")
    
    print_section("OPERATION RESULTS")
    processing_time = promotion_result.get("processing_time", 0)
    print(f"   Processing time: {processing_time:.2f} seconds")
    
    if promotion_result.get("backup_created"):
        print(f"   📦 Backup created: {promotion_result.get('backup_path', 'Unknown')}")


def format_promotion_report_markdown(promotion_result):
    """Format promotion report as markdown."""
    lines = []
    lines.append("# Fleeting Note Promotion Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    promoted_notes = promotion_result.get('promoted_notes', [])
    stats = promotion_result.get('statistics', {})
    
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Notes processed**: {stats.get('notes_processed', 0)}")
    lines.append(f"- **Successfully promoted**: {stats.get('successful_promotions', 0)}")
    lines.append(f"- **Errors encountered**: {stats.get('promotion_errors', 0)}")
    lines.append(f"- **Processing time**: {promotion_result.get('processing_time', 0):.2f} seconds")
    lines.append("")
    
    if promoted_notes:
        lines.append("## Promoted Notes")
        lines.append("")
        for note in promoted_notes:
            status = "✅" if not note.get('error') else "❌"
            lines.append(f"### {status} {note['original_path']}")
            lines.append("")
            if note.get('error'):
                lines.append(f"**Error**: {note['error']}")
            else:
                lines.append(f"**New location**: {note['new_path']}")
                lines.append(f"**Target type**: {note['target_type'].title()} Note")
            lines.append("")
    
    return "\n".join(lines)


def display_backup_list(backups):
    """Display list of backups with details."""
    print_section("BACKUP LIST")
    
    if not backups:
        print("   📁 No backups found")
        return
        
    print(f"   📁 Found {len(backups)} backup(s):")
    print("")
    
    for i, backup in enumerate(backups, 1):
        # Extract timestamp from backup name
        backup_name = backup.name
        timestamp_match = re.search(r'(\d{8})-(\d{6})', backup_name)
        if timestamp_match:
            date_str = timestamp_match.group(1)
            time_str = timestamp_match.group(2)
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            print(f"   {i:2d}. {backup_name}")
            print(f"       📅 Created: {formatted_date} {formatted_time}")
            print(f"       📂 Path: {backup}")
        else:
            print(f"   {i:2d}. {backup_name}")
            print(f"       📂 Path: {backup}")
        print("")


def display_prune_plan(prune_result):
    """Display backup pruning plan and results."""
    if prune_result.get("plan"):
        print_section("BACKUP PRUNING PLAN")
    else:
        print_section("BACKUP PRUNING RESULTS")
    
    found = prune_result["found"]
    keep = prune_result["keep"]
    to_prune = prune_result["to_prune"]
    to_keep = prune_result["to_keep"]
    
    print(f"   📊 Backups found: {found}")
    print(f"   🔒 Backups to keep: {len(to_keep)} (newest {keep})")
    print(f"   🗑️  Backups to prune: {len(to_prune)}")
    print("")
    
    if to_keep:
        print("   📁 Backups to KEEP:")
        for backup in to_keep:
            print(f"      ✅ {backup.name}")
        print("")
    
    if to_prune:
        print("   🗑️  Backups to DELETE:")
        for backup in to_prune:
            print(f"      ❌ {backup.name}")
        print("")
    
    # Show results if this was an actual run
    if not prune_result.get("plan"):
        deleted = prune_result.get("deleted", [])
        errors = prune_result.get("errors", [])
        deleted_count = prune_result.get("deleted_count", 0)
        
        if deleted:
            print("   ✅ Successfully deleted:")
            total_size = 0
            for item in deleted:
                size_mb = item.get("size_mb", 0)
                total_size += size_mb
                print(f"      📦 {item['name']} ({size_mb:.2f} MB)")
            print(f"      💾 Total space freed: {total_size:.2f} MB")
            print("")
        
        if errors:
            print("   ❌ Errors encountered:")
            for error in errors:
                print(f"      ⚠️  {error}")
            print("")
        
        success = prune_result.get("success", False)
        status_emoji = "✅" if success else "⚠️"
        print(f"   {status_emoji} Operation completed: {deleted_count} backup(s) deleted")


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
        "--fleeting-health",
        action="store_true",
        help="Generate fleeting notes health report with age analysis and recommendations"
    )
    
    action_group.add_argument(
        "--fleeting-triage",
        action="store_true",
        help="Generate AI-powered triage report for fleeting notes with quality assessment and recommendations"
    )
    
    action_group.add_argument(
        "--promote-note",
        metavar="NOTE_PATH",
        nargs="?",
        const="BATCH_MODE",
        help="Promote fleeting note to permanent/literature note with safe file operations"
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
    
    # Fleeting triage specific options
    parser.add_argument(
        "--min-quality",
        type=float,
        metavar="THRESHOLD",
        help="Minimum quality threshold for triage filtering (0.0-1.0)"
    )
    
    # Promotion specific options
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch promotion mode (use with --promote-note and --min-quality)"
    )
    
    parser.add_argument(
        "--to",
        choices=["permanent", "literature"],
        help="Target directory for promotion (permanent|literature)"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview promotion plan without executing (dry-run mode)"
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
    
    # Backup management commands
    action_group.add_argument(
        "--backup",
        action="store_true",
        help="Create a timestamped backup of the vault"
    )
    
    action_group.add_argument(
        "--list-backups",
        action="store_true", 
        help="List all existing backups (newest first)"
    )
    
    action_group.add_argument(
        "--prune-backups",
        action="store_true",
        help="Remove old backup directories (use with --keep)"
    )
    
    # TDD Iteration 4: Safe Workflow Processing Commands (GREEN Phase)
    action_group.add_argument(
        "--process-inbox-safe",
        action="store_true",
        help="Process inbox notes with image preservation and atomic operations"
    )
    
    action_group.add_argument(
        "--batch-process-safe", 
        action="store_true",
        help="Batch process notes with comprehensive safety guarantees and image preservation"
    )
    
    action_group.add_argument(
        "--performance-report",
        action="store_true",
        help="Generate comprehensive performance metrics report for safe workflow processing"
    )
    
    action_group.add_argument(
        "--integrity-report",
        action="store_true", 
        help="Generate comprehensive image integrity report with monitoring details"
    )
    
    action_group.add_argument(
        "--start-safe-session",
        metavar="SESSION_NAME",
        help="Start a new concurrent safe processing session"
    )
    
    action_group.add_argument(
        "--process-in-session",
        nargs=2,
        metavar=("SESSION_ID", "NOTE_PATH"),
        help="Process note within specified session"
    )
    
    # TDD Iteration 2: Samsung Screenshot Evening Workflow CLI Integration
    action_group.add_argument(
        "--evening-screenshots",
        action="store_true",
        help="Process Samsung S3 screenshots from OneDrive into daily notes with OCR and smart linking"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        default=None,
        help="Limit number of screenshots to process (most recent N)"
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
    
    # Backup management options
    parser.add_argument(
        "--keep",
        type=int,
        metavar="N",
        help="Number of recent backups to keep when pruning (use with --prune-backups)"
    )
    
    # TDD Iteration 4: Safe Processing Options (GREEN Phase)
    parser.add_argument(
        "--performance-metrics",
        action="store_true",
        help="Include performance metrics in safe processing operations"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=2,
        metavar="N",
        help="Maximum number of concurrent processing sessions (default: 2)"
    )
    
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress indicators during batch processing"
    )
    
    parser.add_argument(
        "--benchmark-mode",
        action="store_true",
        help="Enable benchmark mode for performance testing"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        metavar="N",
        help="Number of notes to process per batch (default: 10)"
    )
    
    parser.add_argument(
        "--note",
        metavar="PATH",
        help="Specific note path for session-based processing"
    )
    
    # TDD Iteration 2: Samsung Screenshot Evening Workflow Options
    parser.add_argument(
        "--onedrive-path",
        metavar="PATH",
        default="/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots/",
        help="Path to OneDrive Samsung Screenshots directory"
    )
    
    parser.add_argument(
        "--max-screenshots",
        type=int,
        metavar="N",
        help="Maximum number of screenshots to process"
    )
    
    parser.add_argument(
        "--quality-threshold",
        type=float,
        metavar="THRESHOLD",
        help="Quality threshold for filtering (0.0-1.0)"
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

    # Suppress initialization messages for JSON output
    if args.format != "json":
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
    
    elif args.promote:
        # Non-interactive promotion handler
        file_arg, note_type = args.promote
        print("🚀 Promoting note...")
        print(f"   File arg: {file_arg}")
        print(f"   Target type: {note_type}")
        
        # Resolve file path robustly: absolute, CWD-relative, base_dir-relative, or by filename in Inbox/Fleeting
        candidate = Path(file_arg)
        resolved_path = None
        try:
            if not candidate.is_absolute():
                # Try CWD-relative
                cwd_path = (Path.cwd() / candidate)
                if cwd_path.exists():
                    resolved_path = cwd_path
            if resolved_path is None:
                # Try base_dir-relative
                base_path = (Path(workflow.base_dir) / candidate)
                if base_path.exists():
                    resolved_path = base_path
            if resolved_path is None:
                # Fall back to searching by filename in Inbox and Fleeting
                name_only = candidate.name
                inbox_candidate = workflow.inbox_dir / name_only
                fleeting_candidate = workflow.fleeting_dir / name_only
                if inbox_candidate.exists():
                    resolved_path = inbox_candidate
                elif fleeting_candidate.exists():
                    resolved_path = fleeting_candidate
        except Exception:
            resolved_path = None
        
        if resolved_path is None or not resolved_path.exists():
            print(f"❌ Error: File not found in inbox/fleeting or at provided path: {file_arg}")
            sys.exit(1)
        
        result = workflow.promote_note(str(resolved_path), note_type.lower())
        if result.get("success"):
            print(f"✅ Successfully promoted to {result.get('type')}:\n   {result.get('source')} → {result.get('target')}")
            if result.get("has_summary"):
                print("   Added AI summary")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
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
        
        recommendations = workflow.generate_weekly_recommendations(candidates)
        
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
    
    elif args.fleeting_health:
        if args.format != "json":
            print("📊 Generating fleeting notes health report...")
        health_report = workflow.generate_fleeting_health_report()
        
        if args.format == "json":
            print(json.dumps(health_report, indent=2, default=str))
        else:
            print_header("FLEETING NOTES HEALTH REPORT")
            display_fleeting_health_report(health_report)
        
        # Export if requested
        if args.export:
            export_path = Path(args.export)
            with open(export_path, 'w', encoding='utf-8') as f:
                if args.format == "json":
                    json.dump(health_report, f, indent=2, default=str)
                else:
                    f.write("# FLEETING NOTES HEALTH REPORT\n\n")
                    f.write(format_fleeting_health_report_markdown(health_report))
            print(f"\n📄 Health report exported to: {export_path}")
    
    elif args.fleeting_triage:
        # Validate quality threshold if provided
        if args.min_quality is not None and (args.min_quality < 0.0 or args.min_quality > 1.0):
            print("❌ Error: Quality threshold must be between 0.0 and 1.0")
            return 1
        
        if args.format != "json":
            print("📊 Generating AI-powered fleeting notes triage report...")
        
        triage_report = workflow.generate_fleeting_triage_report(
            quality_threshold=args.min_quality,
            fast=True  # Use fast mode for better performance
        )
        
        if args.format == "json":
            print(json.dumps(triage_report, indent=2, default=str))
        else:
            print_header("FLEETING NOTES TRIAGE REPORT")
            display_fleeting_triage_report(triage_report)
        
        # Export if requested
        if args.export:
            export_path = Path(args.export)
            with open(export_path, 'w', encoding='utf-8') as f:
                if args.format == "json":
                    json.dump(triage_report, f, indent=2, default=str)
                else:
                    f.write(format_fleeting_triage_report_markdown(triage_report))
            print(f"\n📄 Triage report exported to: {export_path}")
    
    elif args.promote_note:
        # Promote fleeting note(s) to permanent/literature status
        if args.format != "json":
            if args.batch:
                print("🚀 Initiating batch promotion workflow...")
            else:
                print(f"🚀 Promoting fleeting note: {args.promote_note}")
        
        try:
            if args.batch or args.promote_note == "BATCH_MODE":
                # Batch promotion based on triage results
                promotion_result = workflow.promote_fleeting_notes_batch(
                    quality_threshold=args.min_quality or 0.7,
                    target_type=args.to,
                    preview_mode=args.preview
                )
            else:
                # Single note promotion
                if not args.promote_note or args.promote_note == "BATCH_MODE":
                    print("❌ Error: --promote-note requires a note path unless using --batch mode")
                    return 1
                    
                promotion_result = workflow.promote_fleeting_note(
                    note_path=args.promote_note,
                    target_type=args.to,
                    preview_mode=args.preview
                )
                
            # Check if any promotions had errors and return appropriate exit code
            promoted_notes = promotion_result.get('promoted_notes', [])
            has_errors = any(note.get('error') for note in promoted_notes)
                
            if args.format == "json":
                print(json.dumps(promotion_result, indent=2, default=str))
            else:
                print_header("FLEETING NOTE PROMOTION RESULTS")
                display_promotion_results(promotion_result)
                
            # Export if requested
            if args.export:
                export_path = Path(args.export)
                with open(export_path, 'w', encoding='utf-8') as f:
                    if args.format == "json":
                        json.dump(promotion_result, f, indent=2, default=str)
                    else:
                        f.write(format_promotion_report_markdown(promotion_result))
                print(f"\n📄 Promotion report exported to: {export_path}")
            
            # Return error code if there were errors
            if has_errors:
                return 1
                
        except Exception as e:
            print(f"❌ Error during promotion: {e}")
            return 1
    
    elif args.backup:
        # Create a timestamped backup
        print("📦 Creating backup...")
        try:
            organizer = DirectoryOrganizer(vault_root=str(base_dir))
            backup_path = organizer.create_backup()
            
            print_header("BACKUP CREATED")
            print(f"   ✅ Backup successful")
            print(f"   📂 Location: {backup_path}")
            print(f"   📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return 1
    
    elif args.list_backups:
        # List all existing backups
        print("📋 Listing backups...")
        try:
            organizer = DirectoryOrganizer(vault_root=str(base_dir))
            backups = organizer.list_backups()
            
            print_header("BACKUP INVENTORY")
            display_backup_list(backups)
            
        except Exception as e:
            print(f"❌ Error listing backups: {e}")
            return 1
    
    elif args.prune_backups:
        # Prune old backups
        if args.keep is None:
            print("❌ Error: --prune-backups requires --keep N parameter")
            print("💡 Example: python3 src/cli/workflow_demo.py . --prune-backups --keep 5")
            return 1
        
        print(f"🗑️  Pruning backups (keeping {args.keep} most recent)...")
        if args.dry_run:
            print("🔍 Dry run mode - no files will be deleted")
        
        try:
            organizer = DirectoryOrganizer(vault_root=str(base_dir))
            prune_result = organizer.prune_backups(keep=args.keep, dry_run=args.dry_run)
            
            print_header("BACKUP PRUNING")
            display_prune_plan(prune_result)
            
            if args.dry_run and prune_result["to_prune"]:
                print("\n💡 Run without --dry-run to actually delete these backups")
            
        except Exception as e:
            print(f"❌ Error pruning backups: {e}")
            return 1
    
    # TDD Iteration 4 REFACTOR: Safe Workflow Processing Commands (using CLI utilities)
    elif args.process_inbox_safe:
        print("🛡️ Processing inbox notes with image preservation...")
        try:
            # REFACTOR: Use extracted CLI utility classes
            from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI
            
            cli = SafeWorkflowCLI(str(base_dir), max_concurrent=args.max_concurrent)
            result = cli.execute_command("process-inbox-safe", {
                "progress": args.progress,
                "performance_metrics": args.performance_metrics,
                "batch_size": args.batch_size
            })
            
            if args.format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print_header("SAFE INBOX PROCESSING COMPLETE")
                if result.get("success"):
                    processing_result = result.get("result", {})
                    print(f"   ✅ Processed: {processing_result.get('successful_notes', 0)}/{processing_result.get('total_notes', 0)} notes")
                    print(f"   🖼️ Images preserved: {processing_result.get('total_images_preserved', 0)}")
                    print(f"   🛡️ Atomic operations: Enabled")
                    print(f"   ⏱️ Execution time: {result.get('execution_time', 0):.2f}s")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during safe processing: {e}")
            return 1
    
    elif args.batch_process_safe:
        print("🛡️ Batch processing with comprehensive safety guarantees...")
        try:
            # REFACTOR: Use extracted CLI utility classes
            from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI
            
            cli = SafeWorkflowCLI(str(base_dir), max_concurrent=args.max_concurrent)
            result = cli.execute_command("batch-process-safe", {
                "batch_size": args.batch_size,
                "progress": args.progress,
                "performance_metrics": args.performance_metrics
            })
            
            if args.format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print_header("SAFE BATCH PROCESSING COMPLETE")
                if result.get("success"):
                    batch_result = result.get("result", {})
                    print(f"   ✅ Total files processed: {batch_result.get('total_files', 0)}")
                    print(f"   🖼️ Total images preserved: {batch_result.get('images_preserved_total', 0)}")
                    print(f"   ⏱️ Processing time: {result.get('execution_time', 0):.2f}s") 
                    print(f"   🛡️ Image integrity: {batch_result.get('image_integrity_report', {}).get('successful_image_preservation', 0)} successful")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during batch processing: {e}")
            return 1
    
    elif args.performance_report:
        print("📊 Generating performance metrics report...")
        try:
            # REFACTOR: Use extracted CLI utility classes
            from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI
            
            cli = SafeWorkflowCLI(str(base_dir))
            result = cli.execute_command("performance-report", {
                "format": args.format,
                "performance_metrics": args.performance_metrics
            })
            
            if args.format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print_header("PERFORMANCE METRICS REPORT")
                if result.get("success"):
                    stats = result.get("result", {})
                    print(f"   📈 Total operations: {stats.get('total_operations', 0)}")
                    print(f"   ✅ Success rate: {stats.get('success_rate', 0):.2%}")
                    print(f"   ⏱️ Average processing time: {stats.get('average_processing_time', 0):.2f}s")
                    print(f"   🖼️ Total images preserved: {stats.get('total_images_preserved', 0)}")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error generating performance report: {e}")
            return 1
    
    elif args.integrity_report:
        print("🔍 Generating image integrity report...")
        try:
            # REFACTOR: Use extracted CLI utility classes
            from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI
            
            cli = SafeWorkflowCLI(str(base_dir))
            result = cli.execute_command("integrity-report", {
                "format": args.format,
                "export": args.export if hasattr(args, 'export') else None
            })
            
            if args.format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print_header("IMAGE INTEGRITY REPORT")
                if result.get("success"):
                    report = result.get("result", {})
                    print(f"   🖼️ Images tracked: {len(report.get('tracked_images', {}))}")
                    print(f"   📊 Monitoring enabled: Yes")
                    print(f"   🔍 Scan complete: {report.get('scan_timestamp', 'N/A')}")
                    
                    # Export notification if requested
                    if result.get("exported"):
                        print(f"\n📄 Integrity report exported to: {result.get('export_path')}")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error generating integrity report: {e}")
            return 1
    
    elif args.start_safe_session:
        print(f"🚀 Starting safe processing session: {args.start_safe_session}")
        try:
            # REFACTOR: Use extracted CLI utility classes
            from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI
            
            cli = SafeWorkflowCLI(str(base_dir))
            result = cli.execute_command("start-safe-session", {
                "session_name": args.start_safe_session,
                "format": args.format
            })
            
            if args.format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print_header("SAFE SESSION STARTED")
                if result.get("success"):
                    session_data = result.get("result", {})
                    print(f"   🆔 Session ID: {session_data.get('session_id', 'N/A')}")
                    print(f"   📝 Session Name: {args.start_safe_session}")
                    print(f"   ✅ Status: Active")
                    print(f"\n💡 Use --process-in-session {session_data.get('session_id')} <note_path> to process notes")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
            return 1
    
    elif args.process_in_session:
        session_id, note_path = args.process_in_session
        print(f"🔄 Processing note in session {session_id}: {note_path}")
        try:
            # REFACTOR: Use extracted CLI utility classes
            from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI
            
            cli = SafeWorkflowCLI(str(base_dir))
            result = cli.execute_command("process-in-session", {
                "session_id": session_id,
                "note_path": note_path,
                "format": args.format
            })
            
            if args.format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print_header("SESSION PROCESSING COMPLETE")
                if result.get("success"):
                    processing_data = result.get("result", {})
                    print(f"   ✅ Success: {processing_data.get('success', False)}")
                    print(f"   🆔 Session ID: {processing_data.get('session_id', session_id)}")
                    print(f"   🖼️ Images preserved: {processing_data.get('processing_result', {}).get('image_preservation', {}).get('images_preserved', 0)}")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing in session: {e}")
            return 1
    
    elif args.evening_screenshots:
        print("📸 Processing Samsung Screenshot Evening Workflow...")
        try:
            # REFACTOR: Use extracted utility classes
            config_manager = ConfigurationManager()
            config = config_manager.apply_configuration(args)
            
            # Validate OneDrive path
            path_validation = config["path_validation"]
            if not path_validation["valid"]:
                formatter = CLIOutputFormatter(args.format)
                error_output = formatter.format_error(
                    path_validation["error"],
                    [path_validation.get("suggestion", "")]
                )
                print(error_output)
                return 1
            
            # Initialize CLI orchestrator
            orchestrator = EveningScreenshotCLIOrchestrator(
                knowledge_path=str(base_dir),
                onedrive_path=config["onedrive_path"]
            )
            
            # Initialize progress reporter if requested
            progress_reporter = CLIProgressReporter() if config["progress"] else None
            
            # Execute command based on mode
            if config["dry_run"]:
                if progress_reporter:
                    progress_reporter.start_progress(1, "Scanning screenshots")
                
                result = orchestrator.execute_command("dry-run", config)
                
                if progress_reporter:
                    progress_reporter.update_progress(1, "Scan complete")
                    progress_reporter.complete_progress()
            else:
                if progress_reporter:
                    progress_reporter.start_progress(4, "Processing screenshots")
                    progress_reporter.update_progress(1, "Initializing processor")
                
                result = orchestrator.execute_command("process", config)
                
                if progress_reporter:
                    progress_reporter.update_progress(4, "Processing complete")
                    metrics = progress_reporter.complete_progress()
                    if config["performance_metrics"]:
                        progress_reporter.report_performance_metrics(result.get("result", {}))
            
            # Handle results
            if not result["success"]:
                formatter = CLIOutputFormatter(args.format)
                error_output = formatter.format_error(result["error"])
                print(error_output)
                return 1
            
            # Format output
            formatter = CLIOutputFormatter(args.format)
            
            if config["dry_run"]:
                output = formatter.format_dry_run_results(result["result"])
            else:
                output = formatter.format_processing_results(result["result"])
                
                # Performance metrics if requested
                if config["performance_metrics"] and not progress_reporter:
                    reporter = CLIProgressReporter()
                    reporter.report_performance_metrics(result["result"])
            
            print(output)
            
            # Export if requested
            if args.export:
                export_manager = CLIExportManager()
                export_success = export_manager.export_results(
                    result["result"], 
                    args.export, 
                    "json"
                )
                if export_success:
                    print(f"\n📄 Results exported to: {args.export}")
                else:
                    print(f"\n❌ Export failed to: {args.export}")
            
            # Return result dictionary for testing
            return {
                'processed_screenshots': result["result"].get('processed_count', 0),
                'processing_time': result["result"].get('processing_time', 0),
                'daily_note_generated': result["result"].get('daily_note_path') is not None
            }
                    
        except Exception as e:
            print(f"❌ Error during evening screenshot processing: {e}")
            return 1
    
    else:
        # No action specified, show basic status
        print("📊 Showing basic workflow status...")
        report = workflow.generate_workflow_report()
        
        print_header("WORKFLOW OVERVIEW")
        display_workflow_status(report["workflow_status"])
        
        print("\n💡 Use --help to see available actions")
        print("💡 Use --interactive for full workflow management")


if __name__ == "__main__":
    import sys
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)
