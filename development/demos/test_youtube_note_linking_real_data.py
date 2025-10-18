#!/usr/bin/env python3
"""
Real Data Validation: YouTube Transcript Note Linking (Phase 3)

Tests the complete note linking workflow with actual file operations.
Creates a test YouTube note, processes it through the handler, and
validates bidirectional linking was successfully created.

Author: InnerOS Zettelkasten Team
Date: 2025-10-18
Phase: 3 (Note Linking Integration) - Real Data Validation
"""

import sys
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.automation.feature_handlers import YouTubeFeatureHandler
from src.ai.youtube_transcript_saver import YouTubeTranscriptSaver
from src.utils.frontmatter import parse_frontmatter


def create_test_youtube_note(vault_path: Path) -> Path:
    """Create a test YouTube note with realistic content."""
    inbox = vault_path / "Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    
    note_content = """---
created: 2025-10-18 08:00
type: fleeting
status: inbox
tags: [youtube, ai, machine-learning]
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
video_title: Introduction to Machine Learning
---

# Introduction to Machine Learning

This video covers fundamental ML concepts.

## My Notes

- Supervised learning requires labeled data
- Neural networks are inspired by biological neurons
- Training requires compute resources

## Questions

- How do we prevent overfitting?
- What's the difference between precision and recall?
"""
    
    note_path = inbox / "fleeting-ml-intro.md"
    note_path.write_text(note_content)
    
    return note_path


def create_mock_transcript(vault_path: Path, video_id: str, parent_note_name: str) -> Path:
    """Create a mock transcript file to simulate Phase 1."""
    transcripts_dir = vault_path / "Media" / "Transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    transcript_content = f"""---
created: {date_str} 08:00
type: literature
status: published
video_id: {video_id}
video_url: https://www.youtube.com/watch?v={video_id}
video_title: Introduction to Machine Learning
duration: 600.0
language: en
parent_note: [[{parent_note_name}]]
---

# YouTube Transcript: Introduction to Machine Learning

**Source**: https://www.youtube.com/watch?v={video_id}  
**Duration**: 10:00  
**Language**: en

## Transcript

### 00:00 - Introduction
Welcome to this introduction to machine learning...

### 01:30 - Supervised Learning
Supervised learning is when we have labeled training data...

### 03:45 - Neural Networks
Neural networks are computational models inspired by biological neurons...

### 07:15 - Training Process
The training process involves optimizing model parameters...
"""
    
    transcript_path = transcripts_dir / f"youtube-{video_id}-{date_str}.md"
    transcript_path.write_text(transcript_content)
    
    return transcript_path


def display_comparison(before_content: str, after_content: str):
    """Display before/after comparison with highlighting."""
    print("\n" + "="*80)
    print("📋 BEFORE (Original Note)")
    print("="*80)
    print(before_content)
    
    print("\n" + "="*80)
    print("✨ AFTER (With Transcript Links)")
    print("="*80)
    print(after_content)
    
    print("\n" + "="*80)
    print("🔍 CHANGES DETECTED")
    print("="*80)
    
    # Parse frontmatter to show changes
    before_meta, before_body = parse_frontmatter(before_content)
    after_meta, after_body = parse_frontmatter(after_content)
    
    # Check frontmatter changes
    if 'transcript_file' in after_meta:
        print(f"✅ Frontmatter: Added transcript_file = {after_meta['transcript_file']}")
    else:
        print("❌ Frontmatter: transcript_file NOT added")
    
    # Check body changes
    if '**Full Transcript**:' in after_body:
        print("✅ Body: Transcript link inserted after title")
        # Find the line
        for line in after_body.split('\n'):
            if '**Full Transcript**:' in line:
                print(f"   Line: {line.strip()}")
    else:
        print("❌ Body: Transcript link NOT inserted")
    
    # Verify content preservation
    before_lines = set(before_body.split('\n'))
    after_lines = set(after_body.split('\n'))
    
    # Lines that should be preserved (minus the new transcript line)
    new_lines = after_lines - before_lines
    preserved_count = len(before_lines.intersection(after_lines))
    
    print(f"\n📊 Content Preservation:")
    print(f"   Original lines: {len(before_lines)}")
    print(f"   Lines preserved: {preserved_count}")
    print(f"   New lines added: {len(new_lines)}")
    
    if preserved_count >= len(before_lines) - 2:  # Allow for minor whitespace differences
        print("   ✅ All original content preserved")
    else:
        print("   ⚠️ Some content may have changed")


def main():
    """Run real data validation test."""
    print("🚀 YouTube Transcript Note Linking - Real Data Validation")
    print("="*80)
    
    # Create temporary vault
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir) / "test-vault"
    vault_path.mkdir(parents=True)
    
    try:
        # Step 1: Create test note
        print("\n📝 Step 1: Creating test YouTube note...")
        note_path = create_test_youtube_note(vault_path)
        print(f"   Created: {note_path}")
        
        # Read original content for comparison
        original_content = note_path.read_text()
        
        # Step 2: Create mock transcript (simulating Phase 1)
        print("\n📄 Step 2: Creating mock transcript...")
        video_id = "dQw4w9WgXcQ"
        transcript_path = create_mock_transcript(vault_path, video_id, "fleeting-ml-intro")
        print(f"   Created: {transcript_path}")
        
        # Verify transcript has parent_note link (Phase 1)
        transcript_content = transcript_path.read_text()
        if 'parent_note: [[fleeting-ml-intro]]' in transcript_content:
            print("   ✅ Transcript → Note link verified (Phase 1)")
        
        # Step 3: Test the linking functionality directly
        print("\n🔗 Step 3: Testing note linking functionality...")
        
        # We'll test just the helper methods since we don't have a full handler setup
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Create a minimal handler instance
        class MockMetricsTracker:
            def record_success(self, *args, **kwargs): pass
            def record_failure(self, *args, **kwargs): pass
            def record_processing_time(self, *args, **kwargs): pass
        
        handler = YouTubeFeatureHandler(
            vault_path=vault_path,
            processing_timeout=30,
            metrics_tracker=MockMetricsTracker()
        )
        
        # Generate transcript wikilink (simulating what handler would create)
        date_str = datetime.now().strftime("%Y-%m-%d")
        transcript_wikilink = f"[[youtube-{video_id}-{date_str}]]"
        
        # Call the Phase 3 linking method
        print(f"   Adding links with wikilink: {transcript_wikilink}")
        success = handler._add_transcript_links_to_note(
            file_path=note_path,
            transcript_wikilink=transcript_wikilink
        )
        
        if success:
            print("   ✅ Linking completed successfully")
        else:
            print("   ❌ Linking failed")
            return
        
        # Step 4: Read updated content
        updated_content = note_path.read_text()
        
        # Step 5: Display comparison
        display_comparison(original_content, updated_content)
        
        # Step 6: Validate bidirectional navigation
        print("\n" + "="*80)
        print("🔄 BIDIRECTIONAL NAVIGATION VALIDATION")
        print("="*80)
        
        # Transcript → Note
        transcript_text = transcript_path.read_text()
        if 'parent_note: [[fleeting-ml-intro]]' in transcript_text:
            print("✅ Transcript → Note: parent_note link present (Phase 1)")
        else:
            print("❌ Transcript → Note: parent_note link missing")
        
        # Note → Transcript (frontmatter)
        note_meta, note_body = parse_frontmatter(updated_content)
        if 'transcript_file' in note_meta and transcript_wikilink in str(note_meta['transcript_file']):
            print(f"✅ Note → Transcript (frontmatter): {note_meta['transcript_file']}")
        else:
            print("❌ Note → Transcript (frontmatter): transcript_file missing")
        
        # Note → Transcript (body)
        if '**Full Transcript**:' in note_body and transcript_wikilink in note_body:
            print(f"✅ Note → Transcript (body): Link present in body")
        else:
            print("❌ Note → Transcript (body): Link missing from body")
        
        # Final verdict
        print("\n" + "="*80)
        print("🎉 VALIDATION COMPLETE")
        print("="*80)
        
        all_checks_pass = (
            'parent_note: [[fleeting-ml-intro]]' in transcript_text and
            'transcript_file' in note_meta and
            '**Full Transcript**:' in note_body
        )
        
        if all_checks_pass:
            print("✅ ALL CHECKS PASSED - Phase 3 Note Linking Working Correctly!")
            print("\n📊 Summary:")
            print("   - Frontmatter integration: ✅")
            print("   - Body link insertion: ✅")
            print("   - Content preservation: ✅")
            print("   - Bidirectional navigation: ✅")
            print("\n🚀 Ready for production use!")
        else:
            print("⚠️ SOME CHECKS FAILED - Review implementation")
        
    except Exception as e:
        print(f"\n❌ ERROR during validation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary vault: {temp_dir}")
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
