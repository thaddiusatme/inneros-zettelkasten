"""
CLI demo for the analytics system.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.analytics import NoteAnalytics


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n📊 {title}")
    print("-" * 40)


def format_number(num):
    """Format numbers with commas."""
    if isinstance(num, (int, float)):
        return f"{num:,}" if isinstance(num, int) else f"{num:,.2f}"
    return str(num)


def display_overview(overview):
    """Display overview statistics."""
    print_section("OVERVIEW STATISTICS")
    
    stats = [
        ("Total Notes", overview["total_notes"]),
        ("Total Words", overview["total_words"]),
        ("Average Words/Note", overview["average_words_per_note"]),
        ("Average Quality Score", f"{overview['average_quality_score']:.2f}/1.0"),
        ("Notes with AI Summaries", overview["notes_with_ai_summaries"]),
        ("Total Internal Links", overview["total_internal_links"]),
        ("Average Links/Note", overview["average_links_per_note"])
    ]
    
    for label, value in stats:
        formatted_value = format_number(value) if isinstance(value, (int, float)) else value
        print(f"   {label:<25}: {formatted_value}")


def display_distributions(distributions):
    """Display distribution statistics."""
    print_section("CONTENT DISTRIBUTIONS")
    
    print("   Note Types:")
    for note_type, count in distributions["note_types"].items():
        percentage = (count / sum(distributions["note_types"].values())) * 100
        print(f"     {note_type:<15}: {count:>3} ({percentage:>5.1f}%)")
    
    print("\n   Note Status:")
    for status, count in distributions["note_status"].items():
        percentage = (count / sum(distributions["note_status"].values())) * 100
        print(f"     {status:<15}: {count:>3} ({percentage:>5.1f}%)")


def display_quality_metrics(quality):
    """Display quality metrics."""
    print_section("QUALITY ANALYSIS")
    
    total_notes = (quality["high_quality_notes"] + 
                  quality["medium_quality_notes"] + 
                  quality["low_quality_notes"])
    
    quality_levels = [
        ("High Quality (>0.7)", quality["high_quality_notes"]),
        ("Medium Quality (0.4-0.7)", quality["medium_quality_notes"]),
        ("Low Quality (<0.4)", quality["low_quality_notes"])
    ]
    
    for label, count in quality_levels:
        percentage = (count / total_notes * 100) if total_notes > 0 else 0
        print(f"   {label:<25}: {count:>3} ({percentage:>5.1f}%)")
    
    print(f"\n   Quality Score Range:")
    dist = quality["quality_distribution"]
    print(f"     Minimum: {dist['min']:.3f}")
    print(f"     Maximum: {dist['max']:.3f}")
    print(f"     Average: {dist['avg']:.3f}")


def display_temporal_analysis(temporal):
    """Display temporal analysis."""
    print_section("TEMPORAL ANALYSIS")
    
    print(f"   Notes with Creation Dates: {temporal['notes_with_dates']}")
    
    if temporal["date_range"]["earliest"] and temporal["date_range"]["latest"]:
        earliest = datetime.fromisoformat(temporal["date_range"]["earliest"])
        latest = datetime.fromisoformat(temporal["date_range"]["latest"])
        
        print(f"   Date Range:")
        print(f"     Earliest: {earliest.strftime('%Y-%m-%d %H:%M')}")
        print(f"     Latest:   {latest.strftime('%Y-%m-%d %H:%M')}")
        
        # Calculate time span
        time_span = latest - earliest
        print(f"     Span:     {time_span.days} days")


def display_recommendations(recommendations):
    """Display actionable recommendations."""
    print_section("RECOMMENDATIONS")
    
    if not recommendations:
        print("   ✅ No specific recommendations - your notes are well-organized!")
        return
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")


def display_ai_insights(report):
    """Display AI-specific insights."""
    print_section("AI FEATURE INSIGHTS")
    
    overview = report["overview"]
    total_notes = overview["total_notes"]
    
    if total_notes == 0:
        print("   No notes to analyze.")
        return
    
    ai_summary_rate = (overview["notes_with_ai_summaries"] / total_notes) * 100
    
    print(f"   AI Summary Adoption: {ai_summary_rate:.1f}%")
    
    if ai_summary_rate < 30:
        print("   💡 Consider enabling auto-summarization for long notes")
    elif ai_summary_rate > 70:
        print("   ✅ Excellent AI summary adoption!")
    
    # Link density analysis
    avg_links = overview["average_links_per_note"]
    if avg_links < 1:
        print("   🔗 Low link density - consider adding more connections between notes")
    elif avg_links > 3:
        print("   ✅ Great note connectivity!")
    
    # Quality insights
    quality = report["quality_metrics"]
    high_quality_rate = (quality["high_quality_notes"] / total_notes) * 100
    
    print(f"   High-Quality Notes: {high_quality_rate:.1f}%")
    
    if high_quality_rate < 30:
        print("   📈 Focus on improving note quality through better tagging and content")
    elif high_quality_rate > 60:
        print("   ✅ Excellent note quality!")


def interactive_mode(analytics):
    """Run interactive exploration mode."""
    print_header("INTERACTIVE ANALYTICS MODE")
    print("Available commands:")
    print("  'overview' - Show overview statistics")
    print("  'quality' - Show quality analysis")
    print("  'types' - Show note type distribution")
    print("  'recommendations' - Show improvement recommendations")
    print("  'export <filename>' - Export full report to JSON")
    print("  'quit' - Exit interactive mode")
    
    while True:
        try:
            command = input("\n📊 analytics> ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'overview':
                report = analytics.generate_report()
                display_overview(report["overview"])
            elif command == 'quality':
                report = analytics.generate_report()
                display_quality_metrics(report["quality_metrics"])
            elif command == 'types':
                report = analytics.generate_report()
                display_distributions(report["distributions"])
            elif command == 'recommendations':
                report = analytics.generate_report()
                display_recommendations(report["recommendations"])
            elif command.startswith('export '):
                filename = command.split(' ', 1)[1]
                result = analytics.export_report(filename)
                print(f"   {result}")
            else:
                print("   Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            print("\n   Exiting interactive mode...")
            break
        except Exception as e:
            print(f"   Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analytics Demo for InnerOS Zettelkasten",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analytics_demo.py /path/to/notes
  python analytics_demo.py /path/to/notes --format json
  python analytics_demo.py /path/to/notes --export report.json
  python analytics_demo.py /path/to/notes --interactive
        """
    )
    
    parser.add_argument(
        "directory",
        help="Path to the notes directory to analyze"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--export",
        metavar="FILENAME",
        help="Export full report to JSON file"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--section",
        choices=["overview", "distributions", "quality", "temporal", "recommendations", "insights"],
        help="Show only specific section"
    )
    
    args = parser.parse_args()
    
    # Validate directory
    notes_dir = Path(args.directory)
    if not notes_dir.exists():
        print(f"❌ Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    if not notes_dir.is_dir():
        print(f"❌ Error: '{args.directory}' is not a directory")
        sys.exit(1)
    
    # Initialize analytics
    print(f"🔍 Analyzing notes in: {args.directory}")
    analytics = NoteAnalytics(args.directory)
    
    # Interactive mode
    if args.interactive:
        interactive_mode(analytics)
        return
    
    # Generate report
    print("📊 Generating analytics report...")
    report = analytics.generate_report()
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        sys.exit(1)
    
    # Export if requested
    if args.export:
        result = analytics.export_report(args.export)
        print(f"📄 {result}")
    
    # Display results
    if args.format == "json":
        print(json.dumps(report, indent=2, default=str))
    else:
        print_header("ZETTELKASTEN ANALYTICS REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Directory: {args.directory}")
        
        if args.section:
            # Show specific section
            if args.section == "overview":
                display_overview(report["overview"])
            elif args.section == "distributions":
                display_distributions(report["distributions"])
            elif args.section == "quality":
                display_quality_metrics(report["quality_metrics"])
            elif args.section == "temporal":
                display_temporal_analysis(report["temporal_analysis"])
            elif args.section == "recommendations":
                display_recommendations(report["recommendations"])
            elif args.section == "insights":
                display_ai_insights(report)
        else:
            # Show all sections
            display_overview(report["overview"])
            display_distributions(report["distributions"])
            display_quality_metrics(report["quality_metrics"])
            display_temporal_analysis(report["temporal_analysis"])
            display_ai_insights(report)
            display_recommendations(report["recommendations"])
        
        print(f"\n{'='*60}")
        print("📊 Analysis complete!")
        
        if not args.export:
            print("💡 Use --export filename.json to save this report")
        
        if not args.interactive:
            print("💡 Use --interactive for exploratory analysis")


if __name__ == "__main__":
    main()
