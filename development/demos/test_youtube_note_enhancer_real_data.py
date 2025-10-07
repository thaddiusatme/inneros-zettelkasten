#!/usr/bin/env python3
"""
Real Data Validation: YouTubeNoteEnhancer
Tests with actual Templater-created notes from knowledge/Inbox/

This validates production readiness by testing with real user notes.
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.youtube_note_enhancer import YouTubeNoteEnhancer, QuotesData


def main():
    """Test YouTubeNoteEnhancer with real Templater-created note."""
    
    print("=" * 70)
    print("  YouTubeNoteEnhancer - Real Data Validation")
    print("=" * 70)
    print()
    
    # Real note from user's Inbox
    test_note = Path(__file__).parent.parent.parent / "knowledge" / "Inbox" / \
                "lit-20251003-0954-ai-channels-are-taking-over-warhammer-40k-lore-on-youtube.md.md"
    
    if not test_note.exists():
        print(f"❌ Test note not found: {test_note}")
        return 1
    
    print(f"📄 Test Note: {test_note.name}")
    print(f"📍 Location: {test_note.parent}")
    print()
    
    # Create sample quotes (simulating AI extraction)
    sample_quotes = QuotesData(
        key_insights=[
            {
                "timestamp": "02:15",
                "quote": "AI-generated content is becoming indistinguishable from human-created lore videos",
                "context": "Discussion of AI content quality in Warhammer 40k niche"
            },
            {
                "timestamp": "05:30",
                "quote": "The line between acceptable AI assistance and AI slop is about transparency and effort",
                "context": "Defining quality standards for AI content"
            }
        ],
        actionable=[
            {
                "timestamp": "08:45",
                "quote": "Content creators should disclose when using AI tools for script writing or voice generation",
                "context": "Transparency recommendations"
            }
        ],
        notable=[
            {
                "timestamp": "11:20",
                "quote": "AI voices are now good enough that viewers can't tell the difference without disclosure",
                "context": "Technical capabilities of modern AI"
            }
        ],
        definitions=[
            {
                "timestamp": "01:30",
                "quote": "AI slop: Low-effort content that's fully automated with no human creative input",
                "context": "Terminology definition"
            }
        ]
    )
    
    print("🤖 Sample Quotes Data:")
    print(f"   - Key Insights: {len(sample_quotes.key_insights)}")
    print(f"   - Actionable: {len(sample_quotes.actionable)}")
    print(f"   - Notable: {len(sample_quotes.notable)}")
    print(f"   - Definitions: {len(sample_quotes.definitions)}")
    print(f"   - Total Quotes: {sum([len(sample_quotes.key_insights), len(sample_quotes.actionable), len(sample_quotes.notable), len(sample_quotes.definitions)])}")
    print()
    
    # Initialize enhancer
    enhancer = YouTubeNoteEnhancer()
    
    # Test 1: Parse note structure
    print("=" * 70)
    print("Test 1: Parse Note Structure")
    print("=" * 70)
    
    original_content = test_note.read_text(encoding='utf-8')
    structure = enhancer.parse_note_structure(original_content)
    
    print(f"✅ Has Frontmatter: {structure.has_frontmatter}")
    print(f"✅ Has 'Why I'm Saving This': {structure.has_why_section}")
    print(f"✅ Title: {structure.title}")
    print(f"✅ Parse Errors: {structure.has_parse_errors}")
    if structure.has_why_section:
        print(f"✅ Why Section Content: {structure.why_section_content[:60]}...")
    print()
    
    # Test 2: Find insertion point
    print("=" * 70)
    print("Test 2: Identify Insertion Point")
    print("=" * 70)
    
    insertion_point = enhancer.identify_insertion_point(original_content)
    lines = original_content.split('\n')
    
    print(f"✅ Insertion Line: {insertion_point}")
    print(f"✅ Total Lines: {len(lines)}")
    print(f"✅ Context (before): {lines[insertion_point-1] if insertion_point > 0 else 'N/A'}")
    print(f"✅ Context (at): {lines[insertion_point] if insertion_point < len(lines) else 'END'}")
    print()
    
    # Test 3: Enhance note (dry-run preview)
    print("=" * 70)
    print("Test 3: Enhancement Preview (Dry-Run)")
    print("=" * 70)
    
    quotes_markdown = enhancer._format_quotes_markdown(sample_quotes)
    preview = enhancer.insert_quotes_section(original_content, quotes_markdown, insertion_point)
    
    print(f"✅ Preview Length: {len(preview)} chars (original: {len(original_content)})")
    print(f"✅ Added {len(preview) - len(original_content)} characters")
    print()
    print("📝 Preview of inserted section:")
    print("-" * 70)
    preview_lines = preview.split('\n')
    for i in range(max(0, insertion_point - 2), min(len(preview_lines), insertion_point + 20)):
        marker = ">>>" if i == insertion_point else "   "
        print(f"{marker} {i:3d}: {preview_lines[i][:65]}")
    print("-" * 70)
    print()
    
    # Test 4: Full enhancement (with backup)
    print("=" * 70)
    print("Test 4: Full Enhancement Workflow")
    print("=" * 70)
    print()
    
    user_input = input("⚠️  Perform actual enhancement on real note? (yes/no): ").strip().lower()
    
    if user_input == 'yes':
        print()
        print("🔄 Enhancing note...")
        
        result = enhancer.enhance_note(test_note, sample_quotes)
        
        if result.success:
            print(f"✅ Enhancement Successful!")
            print(f"   - Backup Created: {result.backup_path}")
            print(f"   - Quote Count: {result.quote_count}")
            print(f"   - Processing Time: {result.processing_time:.3f}s")
            print(f"   - Message: {result.message}")
            print()
            
            # Show the enhanced note preview
            enhanced_content = test_note.read_text(encoding='utf-8')
            print("📄 Enhanced Note Preview:")
            print("-" * 70)
            print(enhanced_content[:500])
            print("...")
            print("-" * 70)
            print()
            print(f"✅ Full enhanced note saved to: {test_note}")
            print(f"✅ Backup available at: {result.backup_path}")
            
        else:
            print(f"❌ Enhancement Failed: {result.error_message}")
            if result.skipped:
                print(f"   (Note was skipped: {result.message})")
    else:
        print("⏩ Skipping actual enhancement (dry-run mode)")
    
    print()
    print("=" * 70)
    print("✅ Real Data Validation Complete!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
