"""
Quick interactive demo of the analytics and workflow systems.
Run this to see the features in action!
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ai.analytics import NoteAnalytics
    from ai.workflow_manager import WorkflowManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def create_demo_notes(base_dir):
    """Create sample notes for demonstration."""
    
    # Create directories
    for dir_name in ["Inbox", "Fleeting Notes", "Permanent Notes"]:
        (base_dir / dir_name).mkdir(exist_ok=True)
    
    # High-quality permanent note
    permanent_note = """---
type: permanent
created: 2024-01-15 09:30
tags: ["machine-learning", "ai", "algorithms"]
status: published
ai_summary: Overview of machine learning fundamentals and applications.
---

# Machine Learning Fundamentals

Machine learning enables computers to learn from data without explicit programming.

## Core Concepts

### Supervised Learning
- Uses labeled training data
- Predicts outcomes for new data
- Examples: classification, regression

### Unsupervised Learning
- Finds patterns in unlabeled data
- Discovers hidden structures
- Examples: clustering, dimensionality reduction

## Applications
- Healthcare: medical diagnosis
- Finance: fraud detection
- Technology: recommendation systems

## Related Topics
- [[deep-learning]] - Advanced neural networks
- [[data-science]] - Broader field of data analysis
- [[ai-ethics]] - Responsible AI development

This is a foundational topic that connects to many other areas of study.
"""
    
    # Medium-quality fleeting note
    fleeting_note = """---
type: fleeting
created: 2024-02-10 16:45
tags: ["productivity", "ideas"]
status: draft
---

# Productivity System Ideas

Some thoughts on improving personal productivity systems.

## Key Principles
- Capture everything in trusted system
- Regular review and processing
- Clear next actions for all items

## Tools to Explore
- Digital note-taking apps
- Task management systems
- Calendar integration

Needs more development and research into specific methodologies.
"""
    
    # Inbox notes (various quality)
    inbox_notes = [
        """---
status: inbox
created: 2024-02-16 22:30
---

Quick thought about creativity - sometimes constraints actually boost creative output rather than limit it.

Examples: haikus, budget limits, time constraints.

Need to research this more.""",
        
        """---
type: literature
created: 2024-02-14 15:45
tags: ["habits", "psychology"]
status: inbox
source: "Atomic Habits by James Clear"
---

# Atomic Habits - Key Insights

## The Four Laws
1. Make it obvious (cue)
2. Make it attractive (craving)
3. Make it easy (response)
4. Make it satisfying (reward)

## Implementation
- Start with 2-minute habits
- Use habit stacking
- Design environment for success

Excellent practical guide to behavior change.""",
        
        """---
status: inbox
---

Research topics to explore:
- Quantum computing applications
- Sustainable energy systems
- Network effects in platforms

Need to prioritize and create proper research plans."""
    ]
    
    # Write files
    (base_dir / "Permanent Notes" / "machine-learning-fundamentals.md").write_text(permanent_note)
    (base_dir / "Fleeting Notes" / "productivity-systems.md").write_text(fleeting_note)
    
    for i, content in enumerate(inbox_notes, 1):
        (base_dir / "Inbox" / f"inbox-note-{i}.md").write_text(content)
    
    print(f"📝 Created {4 + len(inbox_notes)} sample notes")


def demo_analytics(analytics):
    """Demonstrate analytics features."""
    print("\n" + "="*50)
    print("📊 ANALYTICS DEMONSTRATION")
    print("="*50)
    
    # Generate report
    print("\n🔍 Generating analytics report...")
    report = analytics.generate_report()
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return
    
    # Overview
    overview = report["overview"]
    print(f"""
📈 COLLECTION OVERVIEW:
   Total Notes: {overview['total_notes']}
   Total Words: {overview['total_words']:,}
   Average Quality Score: {overview['average_quality_score']:.2f}/1.0
   Notes with AI Summaries: {overview['notes_with_ai_summaries']}
   Internal Links: {overview['total_internal_links']}
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
    """)
    
    # Note types
    distributions = report["distributions"]
    print(f"""
📁 NOTE TYPES:
   Permanent: {distributions['note_types'].get('permanent', 0)}
   Fleeting: {distributions['note_types'].get('fleeting', 0)}
   Literature: {distributions['note_types'].get('literature', 0)}
   Unknown: {distributions['note_types'].get('unknown', 0)}
    """)
    
    # Recommendations
    recommendations = report["recommendations"]
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
    else:
        print(f"\n✅ No specific recommendations - collection looks good!")


def demo_workflow(workflow):
    """Demonstrate workflow features."""
    print("\n" + "="*50)
    print("🔄 WORKFLOW DEMONSTRATION")
    print("="*50)
    
    # Workflow status
    print("\n🏥 Checking workflow health...")
    report = workflow.generate_workflow_report()
    
    status = report["workflow_status"]
    print(f"""
🏥 WORKFLOW STATUS: {status['health'].upper()}
📁 DIRECTORY COUNTS:
   Inbox: {status['directory_counts']['Inbox']} notes
   Fleeting Notes: {status['directory_counts']['Fleeting Notes']} notes
   Permanent Notes: {status['directory_counts']['Permanent Notes']} notes
   Total: {status['total_notes']} notes
    """)
    
    # AI feature usage
    ai_features = report["ai_features"]
    total = ai_features["total_analyzed"]
    if total > 0:
        print(f"""
🤖 AI FEATURE USAGE:
   Notes with AI Summaries: {ai_features['notes_with_ai_summaries']}/{total} ({ai_features['notes_with_ai_summaries']/total*100:.1f}%)
   Notes with AI Processing: {ai_features['notes_with_ai_processing']}/{total} ({ai_features['notes_with_ai_processing']/total*100:.1f}%)
   Notes with AI Tags: {ai_features['notes_with_ai_tags']}/{total} ({ai_features['notes_with_ai_tags']/total*100:.1f}%)
        """)
    
    # Workflow recommendations
    workflow_recs = report.get("recommendations", [])
    if workflow_recs:
        print(f"\n🎯 WORKFLOW RECOMMENDATIONS:")
        for i, rec in enumerate(workflow_recs[:3], 1):
            print(f"   {i}. {rec}")
    
    # Simulate inbox processing if there are inbox notes
    inbox_count = status['directory_counts']['Inbox']
    if inbox_count > 0:
        print(f"\n📥 INBOX PROCESSING SIMULATION:")
        print(f"   Found {inbox_count} notes in inbox")
        print(f"   🔄 Would process each note with AI assistance")
        print(f"   📊 Would provide quality scores and recommendations")
        print(f"   📈 Would suggest promotion paths based on content quality")


def main():
    """Run the quick demo."""
    print("🚀 InnerOS Zettelkasten: Quick Demo")
    print("="*50)
    print("""
This demo showcases the analytics and workflow management features
using a temporary collection of sample notes.
    """)
    
    # Create temporary environment
    temp_dir = tempfile.mkdtemp(prefix="zettelkasten_quick_demo_")
    demo_path = Path(temp_dir)
    
    try:
        print(f"🏗️  Setting up demo environment at: {temp_dir}")
        
        # Create sample notes
        create_demo_notes(demo_path)
        
        # Initialize systems
        print("🤖 Initializing analytics and workflow systems...")
        analytics = NoteAnalytics(str(demo_path))
        workflow = WorkflowManager(str(demo_path))
        
        # Run demos
        demo_analytics(analytics)
        demo_workflow(workflow)
        
        # Summary
        print("\n" + "="*50)
        print("🎉 DEMO COMPLETE!")
        print("="*50)
        print(f"""
✅ Successfully demonstrated:
   • Note collection analysis and quality scoring
   • Comprehensive analytics reporting
   • Workflow health monitoring
   • AI feature usage tracking
   • Actionable recommendations

🚀 Next Steps:
   • Try the full interactive demos: python3 demo_user_journeys.py
   • Use analytics on your real notes: python3 src/cli/analytics_demo.py /path/to/notes
   • Manage your workflow: python3 src/cli/workflow_demo.py /path/to/zettelkasten
        """)
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up demo environment...")
        shutil.rmtree(temp_dir)
        print("✅ Cleanup complete!")


if __name__ == "__main__":
    main()
