"""
Interactive demo script showcasing real user journeys with analytics and workflow systems.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.analytics import NoteAnalytics
from ai.workflow_manager import WorkflowManager


class DemoEnvironment:
    """Creates realistic demo environment with sample notes."""
    
    def __init__(self):
        self.temp_dir = None
        self.zettel_dir = None
        
    def setup(self):
        """Set up demo environment."""
        print("🏗️  Setting up demo environment...")
        
        self.temp_dir = tempfile.mkdtemp(prefix="zettelkasten_demo_")
        self.zettel_dir = Path(self.temp_dir)
        
        # Create directories
        for dir_name in ["Inbox", "Fleeting Notes", "Permanent Notes", "Literature Notes"]:
            (self.zettel_dir / dir_name).mkdir()
        
        # Create sample notes
        self._create_sample_notes()
        
        print(f"✅ Demo environment: {self.temp_dir}")
        return self.temp_dir
    
    def cleanup(self):
        """Clean up demo environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print("🧹 Demo environment cleaned up")
    
    def _create_sample_notes(self):
        """Create realistic sample notes."""
        
        # High-quality permanent note
        permanent_note = """---
type: permanent
created: 2024-01-15 09:30
tags: ["machine-learning", "artificial-intelligence", "algorithms"]
status: published
ai_summary: Comprehensive overview of machine learning fundamentals.
---

# Machine Learning Fundamentals

Machine learning enables computers to learn from experience without explicit programming.

## Types of Learning

### Supervised Learning
- Uses labeled training data
- Linear regression, decision trees, SVMs
- Clear input-output relationships

### Unsupervised Learning  
- Finds patterns in unlabeled data
- Clustering, dimensionality reduction
- Discovers hidden structures

### Reinforcement Learning
- Learns through trial and error
- Agent-environment interaction
- Reward-based optimization

## Applications
- Healthcare: diagnosis, drug discovery
- Finance: fraud detection, trading
- Technology: recommendations, NLP

## Related Notes
- [[deep-learning-architectures]]
- [[data-preprocessing-techniques]]
- [[model-evaluation-metrics]]
"""
        
        # Medium-quality fleeting note
        fleeting_note = """---
type: fleeting
created: 2024-02-10 16:45
tags: ["blockchain", "voting"]
status: draft
---

# Blockchain Voting System Idea

Interesting concept for secure, transparent voting using blockchain.

## Benefits
- Immutable vote records
- Transparent verification
- Reduced tampering risk

## Challenges
- Voter privacy concerns
- Technical complexity
- Regulatory hurdles

Needs more research and development.
"""
        
        # Low-quality inbox notes
        inbox_notes = [
            """---
status: inbox
created: 2024-02-16 22:30
---

Quick thought about creativity and constraints. Sometimes limitations boost creative output.

Need to explore this more.""",
            
            """---
type: literature
created: 2024-02-14 15:45
tags: ["habits", "productivity"]
status: inbox
source: "James Clear, Atomic Habits"
---

# Atomic Habits - Key Insights

## Four Laws of Behavior Change
1. Cue: Make it obvious
2. Craving: Make it attractive
3. Response: Make it easy  
4. Reward: Make it satisfying

## Practical Applications
- Start with 2-minute habits
- Use habit stacking
- Design supportive environment

Great book with actionable strategies.""",
            
            """---
status: inbox
---

Research topics:
- Quantum computing
- Sustainable energy
- Network effects

Need to prioritize."""
        ]
        
        # Write notes to files
        (self.zettel_dir / "Permanent Notes" / "ml-fundamentals.md").write_text(permanent_note)
        (self.zettel_dir / "Fleeting Notes" / "blockchain-voting.md").write_text(fleeting_note)
        
        for i, content in enumerate(inbox_notes):
            (self.zettel_dir / "Inbox" / f"note-{i+1}.md").write_text(content)


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print formatted section."""
    print(f"\n🔍 {title}")
    print("-" * 40)


def wait_for_user(prompt: str = "Press Enter to continue..."):
    """Wait for user input."""
    input(f"\n💡 {prompt}")


def demo_journey_1_analytics():
    """Journey 1: New User Analytics Exploration"""
    
    print_header("Journey 1: New User Analytics")
    print("""
🎭 PERSONA: Sarah, Research Assistant
🎯 GOAL: Understand her note collection
📚 CONTEXT: Just started, has ~6 notes
    """)
    
    # Setup environment
    demo_env = DemoEnvironment()
    demo_path = demo_env.setup()
    analytics = NoteAnalytics(demo_path)
    
    try:
        wait_for_user("Ready to explore Sarah's analytics?")
        
        # Step 1: Overview
        print_section("Getting the Big Picture")
        report = analytics.generate_report()
        overview = report["overview"]
        
        print(f"""
📊 COLLECTION OVERVIEW:
   Total Notes: {overview['total_notes']}
   Total Words: {overview['total_words']:,}
   Average Quality: {overview['average_quality_score']:.2f}/1.0
   AI Summaries: {overview['notes_with_ai_summaries']}
   Internal Links: {overview['total_internal_links']}
        """)
        
        wait_for_user("Sarah sees mixed quality. Let's analyze...")
        
        # Step 2: Quality breakdown
        print_section("Quality Analysis")
        quality = report["quality_metrics"]
        
        print(f"""
⭐ QUALITY BREAKDOWN:
   High Quality (>0.7): {quality['high_quality_notes']} notes
   Medium Quality (0.4-0.7): {quality['medium_quality_notes']} notes
   Low Quality (<0.4): {quality['low_quality_notes']} notes
   
   Range: {quality['quality_distribution']['min']:.2f} - {quality['quality_distribution']['max']:.2f}
        """)
        
        wait_for_user("Now let's see recommendations...")
        
        # Step 3: Recommendations
        print_section("System Recommendations")
        recommendations = report["recommendations"]
        
        print("💡 ACTIONABLE RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"""
        
✅ SARAH'S TAKEAWAYS:
   • Focus on improving {quality['low_quality_notes']} low-quality notes
   • Add more descriptive tags
   • Create connections between related concepts
   • Use AI summaries for longer notes
        """)
        
        print_section("Journey 1 Complete! 🎉")
        print("Sarah has a clear improvement roadmap!")
        
    finally:
        demo_env.cleanup()


def demo_journey_2_workflow():
    """Journey 2: Power User Workflow Optimization"""
    
    print_header("Journey 2: Workflow Optimization")
    print("""
🎭 PERSONA: Marcus, Academic Researcher
🎯 GOAL: Optimize workflow and process inbox
📚 CONTEXT: Heavy user, wants efficiency
    """)
    
    # Setup environment
    demo_env = DemoEnvironment()
    demo_path = demo_env.setup()
    workflow = WorkflowManager(demo_path)
    
    try:
        wait_for_user("Ready to optimize Marcus's workflow?")
        
        # Step 1: Workflow status
        print_section("Workflow Health Check")
        report = workflow.generate_workflow_report()
        status = report["workflow_status"]
        
        print(f"""
🏥 WORKFLOW STATUS: {status['health'].upper()}
📁 DISTRIBUTION:
   Inbox: {status['directory_counts']['Inbox']} notes ⚠️
   Fleeting: {status['directory_counts']['Fleeting Notes']} notes
   Permanent: {status['directory_counts']['Permanent Notes']} notes
   Total: {status['total_notes']} notes
        """)
        
        wait_for_user("Inbox needs attention! Let's process it...")
        
        # Step 2: Batch processing simulation
        print_section("AI-Powered Inbox Processing")
        print("🔄 PROCESSING INBOX NOTES...\n")
        
        # Simulate processing results
        processing_results = [
            ("note-1.md", "0.32", "creativity", "Needs development"),
            ("note-2.md", "0.78", "habits, productivity", "Ready for permanent"),
            ("note-3.md", "0.25", "research", "Needs structure")
        ]
        
        for filename, quality, tags, recommendation in processing_results:
            print(f"""📄 {filename}
   ⭐ Quality: {quality}/1.0
   🏷️  Tags: {tags}
   💡 Recommendation: {recommendation}
""")
        
        wait_for_user("Great results! Let's promote the best note...")
        
        # Step 3: Note promotion
        print_section("Intelligent Note Promotion")
        print("""
📈 PROMOTING HIGH-QUALITY NOTE...

✅ note-2.md → Permanent Notes
   📝 Added AI summary
   🔗 Suggested connections found
   ⭐ Quality improved to 0.85/1.0
        """)
        
        print(f"""
        
⚡ MARCUS'S EFFICIENCY GAINS:
   "What used to take 2 hours now happens in minutes!
   The AI suggestions are spot-on, and automatic promotion
   saves tremendous time. My workflow is finally optimized."
        """)
        
        print_section("Journey 2 Complete! 🎉")
        print("Marcus has transformed his workflow!")
        
    finally:
        demo_env.cleanup()


def demo_journey_3_maintenance():
    """Journey 3: Regular Maintenance Routine"""
    
    print_header("Journey 3: Weekly Maintenance")
    print("""
🎭 PERSONA: Lisa, Management Consultant  
🎯 GOAL: Weekly maintenance and optimization
📚 CONTEXT: Daily user, systematic approach
    """)
    
    demo_env = DemoEnvironment()
    demo_path = demo_env.setup()
    analytics = NoteAnalytics(demo_path)
    
    try:
        wait_for_user("Ready for Lisa's maintenance routine?")
        
        # Health check
        print_section("Weekly Health Check")
        report = analytics.generate_report()
        
        print(f"""
🩺 SYSTEM HEALTH:
   Growth: +12 notes this week
   Quality Trend: ↗️ Improving
   AI Adoption: 75% (good)
   Connection Density: {report['overview']['average_links_per_note']:.1f} links/note
        """)
        
        wait_for_user("Health check complete. Finding connections...")
        
        # Connection discovery
        print_section("Connection Discovery")
        print("""
🔗 DISCOVERED CONNECTIONS:

📝 "ml-fundamentals.md" ↔️ "blockchain-voting.md"
   Similarity: 0.65 | Both involve algorithms
   💡 Add cross-reference about algorithmic trust

📝 "atomic-habits.md" ↔️ "productivity-systems.md"  
   Similarity: 0.84 | Complementary approaches
   💡 Link habit formation to system design
        """)
        
        wait_for_user("Excellent insights! Creating action plan...")
        
        # Action plan
        print_section("Weekly Action Plan")
        print("""
📋 THIS WEEK'S PRIORITIES:

🔥 HIGH PRIORITY (15 min):
   • Add connections between related notes
   • Generate AI summaries for 2 long notes

📝 MEDIUM PRIORITY (20 min):
   • Improve 1 low-quality note
   • Add tags to sparse notes

🔄 MAINTENANCE (10 min):
   • Review and backup
   • Update workflow config

⏱️  Total Time: 45 minutes
📊 Expected Impact: +0.15 quality score
        """)
        
        print(f"""
        
🔧 LISA'S REFLECTION:
   "This weekly routine keeps my knowledge base healthy.
   The AI insights reveal connections I'd never find manually.
   45 minutes maintains my entire knowledge system!"
        """)
        
        print_section("Journey 3 Complete! 🎉")
        print("Lisa has a sustainable maintenance routine!")
        
    finally:
        demo_env.cleanup()


def main():
    """Main demo runner."""
    print_header("🚀 InnerOS Zettelkasten: User Journey Demos")
    
    print("""
Welcome to the interactive demo of advanced analytics and workflow management!

Choose a user journey to experience:

1. 👋 New User Analytics (Sarah's first exploration)
2. ⚡ Power User Workflow (Marcus's optimization)  
3. 🔧 Regular Maintenance (Lisa's weekly routine)
4. 🎬 Run All Journeys

Each demo creates a temporary environment with realistic sample notes.
    """)
    
    while True:
        try:
            choice = input("\nSelect journey (1-4) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Thanks for exploring the demos! 👋")
                break
            elif choice == '1':
                demo_journey_1_analytics()
            elif choice == '2':
                demo_journey_2_workflow()
            elif choice == '3':
                demo_journey_3_maintenance()
            elif choice == '4':
                print("🎬 Running all journeys...")
                demo_journey_1_analytics()
                demo_journey_2_workflow() 
                demo_journey_3_maintenance()
                print_header("🎉 All Journeys Complete!")
                print("You've experienced the full power of the AI-enhanced Zettelkasten!")
            else:
                print("Please enter 1, 2, 3, 4, or 'q'")
                
        except KeyboardInterrupt:
            print("\n\nDemo interrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
