"""
Test the analytics system on your actual notes directory.
This will analyze your real Zettelkasten collection.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.analytics import NoteAnalytics


def analyze_real_notes(notes_path):
    """Analyze real notes and display results."""
    
    notes_dir = Path(notes_path)
    if not notes_dir.exists():
        print(f"❌ Directory not found: {notes_path}")
        return False
    
    print(f"🔍 Analyzing notes in: {notes_path}")
    
    try:
        # Initialize analytics
        analytics = NoteAnalytics(str(notes_dir))
        
        # Generate report
        print("📊 Generating analytics report...")
        report = analytics.generate_report()
        
        if "error" in report:
            print(f"❌ Error: {report['error']}")
            return False
        
        # Display results
        print("\n" + "="*60)
        print("📈 YOUR ZETTELKASTEN ANALYTICS")
        print("="*60)
        
        overview = report["overview"]
        print(f"""
📊 COLLECTION OVERVIEW:
   Total Notes: {overview['total_notes']}
   Total Words: {overview['total_words']:,}
   Average Words per Note: {overview['average_words_per_note']:.1f}
   Average Quality Score: {overview['average_quality_score']:.2f}/1.0
   Notes with AI Summaries: {overview['notes_with_ai_summaries']}
   Total Internal Links: {overview['total_internal_links']}
   Average Links per Note: {overview['average_links_per_note']:.1f}
        """)
        
        # Quality breakdown
        quality = report["quality_metrics"]
        print(f"""
⭐ QUALITY ANALYSIS:
   High Quality (>0.7): {quality['high_quality_notes']} notes
   Medium Quality (0.4-0.7): {quality['medium_quality_notes']} notes
   Low Quality (<0.4): {quality['low_quality_notes']} notes
   
   Quality Range: {quality['quality_distribution']['min']:.2f} - {quality['quality_distribution']['max']:.2f}
   Average Quality: {quality['quality_distribution']['avg']:.2f}
        """)
        
        # Note distributions
        distributions = report["distributions"]
        print(f"""
📁 NOTE TYPE DISTRIBUTION:""")
        for note_type, count in distributions["note_types"].items():
            percentage = (count / overview['total_notes']) * 100 if overview['total_notes'] > 0 else 0
            print(f"   {note_type.title()}: {count} ({percentage:.1f}%)")
        
        print(f"""
📋 NOTE STATUS DISTRIBUTION:""")
        for status, count in distributions["note_status"].items():
            percentage = (count / overview['total_notes']) * 100 if overview['total_notes'] > 0 else 0
            print(f"   {status.title()}: {count} ({percentage:.1f}%)")
        
        # Temporal analysis
        temporal = report["temporal_analysis"]
        if temporal["notes_with_dates"] > 0:
            print(f"""
📅 TEMPORAL ANALYSIS:
   Notes with Creation Dates: {temporal['notes_with_dates']}/{overview['total_notes']}
            """)
            
            if temporal["date_range"]["earliest"] and temporal["date_range"]["latest"]:
                from datetime import datetime
                earliest = datetime.fromisoformat(temporal["date_range"]["earliest"])
                latest = datetime.fromisoformat(temporal["date_range"]["latest"])
                span = (latest - earliest).days
                
                print(f"""   Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}
   Time Span: {span} days""")
        
        # Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print(f"""
💡 ACTIONABLE RECOMMENDATIONS:""")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print(f"""
✅ EXCELLENT! No specific recommendations - your notes are well-organized!""")
        
        # AI insights
        print(f"""
🤖 AI FEATURE INSIGHTS:""")
        ai_summary_rate = (overview["notes_with_ai_summaries"] / overview["total_notes"]) * 100 if overview["total_notes"] > 0 else 0
        print(f"   AI Summary Adoption: {ai_summary_rate:.1f}%")
        
        if ai_summary_rate < 30:
            print("   💡 Consider enabling auto-summarization for long notes")
        elif ai_summary_rate > 70:
            print("   ✅ Excellent AI summary adoption!")
        
        if overview["average_links_per_note"] < 1:
            print("   🔗 Low link density - consider adding more connections")
        elif overview["average_links_per_note"] > 3:
            print("   ✅ Great note connectivity!")
        
        print("\n" + "="*60)
        print("📊 Analysis Complete!")
        print("="*60)
        
        # Export option
        export_path = notes_dir / "analytics_report.json"
        analytics.export_report(str(export_path))
        print(f"📄 Full report exported to: {export_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing notes: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("🔍 Real Notes Analytics Test")
    print("="*40)
    
    # Check for command line argument
    if len(sys.argv) > 1:
        notes_path = sys.argv[1]
    else:
        # Default paths to try
        possible_paths = [
            ".",  # Current directory
            "notes",  # Notes subdirectory
            "Inbox",  # Just inbox
            "Permanent Notes",  # Just permanent notes
        ]
        
        print("No path specified. Trying common locations...")
        notes_path = None
        
        for path in possible_paths:
            if Path(path).exists() and any(Path(path).glob("*.md")):
                notes_path = path
                print(f"✅ Found notes in: {path}")
                break
        
        if not notes_path:
            print("""
❌ No notes directory found.

Usage: python3 test_real_analytics.py [path_to_notes]

Example:
  python3 test_real_analytics.py .
  python3 test_real_analytics.py /path/to/your/zettelkasten
  python3 test_real_analytics.py "Permanent Notes"
            """)
            return
    
    # Analyze the notes
    success = analyze_real_notes(notes_path)
    
    if success:
        print(f"""
🚀 Next Steps:
   • Try interactive analytics: python3 src/cli/analytics_demo.py "{notes_path}" --interactive
   • Try workflow management: python3 src/cli/workflow_demo.py "{notes_path}" --status
   • Run user journey demos: python3 demo_user_journeys.py
        """)
    else:
        print("❌ Analysis failed. Please check the path and try again.")


if __name__ == "__main__":
    main()
