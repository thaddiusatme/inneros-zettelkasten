"""
CLI demo for the workflow manager system.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.workflow_manager import WorkflowManager


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
    
    args = parser.parse_args()
    
    # Validate directory
    zettel_dir = Path(args.directory)
    if not zettel_dir.exists():
        print(f"❌ Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    if not zettel_dir.is_dir():
        print(f"❌ Error: '{args.directory}' is not a directory")
        sys.exit(1)
    
    # Initialize workflow manager
    print(f"🔄 Initializing workflow for: {args.directory}")
    workflow = WorkflowManager(args.directory)
    
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
        filename, note_type = args.promote
        
        # Find the file
        inbox_path = workflow.inbox_dir / filename
        fleeting_path = workflow.fleeting_dir / filename
        
        if inbox_path.exists():
            file_path = str(inbox_path)
        elif fleeting_path.exists():
            file_path = str(fleeting_path)
        else:
            print(f"❌ Error: File '{filename}' not found in inbox or fleeting notes")
            sys.exit(1)
        
        print(f"📈 Promoting {filename} to {note_type}...")
        result = workflow.promote_note(file_path, note_type)
        
        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get("success"):
                print(f"✅ Successfully promoted to {result['type']}")
                print(f"   From: {result['source']}")
                print(f"   To: {result['target']}")
                if result.get("has_summary"):
                    print(f"   Added AI summary")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
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
