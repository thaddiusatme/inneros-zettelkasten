#!/usr/bin/env python3
"""
Interactive demo for InnerOS AI Integration MVP.
Allows users to test the AI tagger with their own content.
"""

from src.ai.tagger import AITagger
import readline


def print_banner():
    """Print a welcome banner."""
    print("\n" + "="*70)
    print("🎯 InnerOS AI Integration - Interactive Demo")
    print("="*70)
    print("Type your note content and see AI-generated tags in real-time!")
    print("Commands:")
    print("  • Enter your note content")
    print("  • Type 'quit' or 'exit' to leave")
    print("  • Type 'config' to see current settings")
    print("  • Type 'help' for more options")
    print("="*70)


def demo_interactive():
    """Run the interactive demo."""
    tagger = AITagger()
    
    print_banner()
    
    sample_notes = [
        "# Machine Learning Basics\n\nMachine learning is a subset of artificial intelligence that enables systems to learn from data and make predictions without explicit programming.",
        "# Python Data Analysis\n\nPandas and NumPy are essential libraries for data manipulation and analysis in Python. They provide powerful tools for working with structured data.",
        "# Knowledge Management\n\nEffective knowledge management systems help organize, store, and retrieve information efficiently. Zettelkasten is a proven method for building personal knowledge bases.",
    ]
    
    print("\n📋 Sample notes you can try:")
    for i, note in enumerate(sample_notes, 1):
        preview = note.replace('\n', ' ').replace('#', '').strip()[:60] + "..."
        print(f"  {i}. {preview}")
    
    while True:
        try:
            print("\n" + "-"*50)
            user_input = input("📝 Enter note content (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for trying the demo!")
                break
            elif user_input.lower() == 'config':
                print(f"⚙️  Current configuration:")
                print(f"   Min confidence: {tagger.min_confidence}")
                print(f"   Max tags: {tagger.max_tags}")
                continue
            elif user_input.lower() == 'help':
                print("📖 Help:")
                print("   • Just paste your note content to see AI tags")
                print("   • Use 'config' to see current settings")
                print("   • Use 'quit' to exit")
                continue
            elif user_input.lower() in ['1', '2', '3']:
                try:
                    idx = int(user_input) - 1
                    user_input = sample_notes[idx]
                    print(f"📝 Using sample note {idx+1}...")
                except (IndexError, ValueError):
                    continue
            
            if not user_input:
                print("⚠️  Please enter some content!")
                continue
            
            # Generate tags
            import time
            start_time = time.time()
            tags = tagger.generate_tags(user_input)
            processing_time = time.time() - start_time
            
            # Display results
            print(f"\n🎯 AI Analysis Results:")
            print(f"   Content length: {len(user_input)} characters")
            print(f"   Processing time: {processing_time:.3f} seconds")
            print(f"   Generated tags ({len(tags)}): {', '.join(tags)}")
            
            if tags:
                print(f"   Tag quality: {'✅ High' if len(tags) >= 3 else '⚠️  Moderate'}")
            else:
                print(f"   Tag quality: ⚠️  No tags generated (content may be too short)")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    demo_interactive()
