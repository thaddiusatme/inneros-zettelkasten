#!/usr/bin/env python3
"""
Process a single YouTube note through the complete handler pipeline.

Shows PBI-001/002/003 in action:
- Checks for approval gate (PBI-002)
- Updates status synchronization (PBI-003)
- Actually processes the note with YouTube API

Usage:
    python3 process_single_youtube_note.py <path_to_note.md>
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.automation.feature_handlers import YouTubeFeatureHandler
from src.utils.frontmatter import parse_frontmatter


def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_frontmatter(note_path):
    """Extract and print current frontmatter."""
    content = note_path.read_text(encoding='utf-8')
    frontmatter, _ = parse_frontmatter(content)
    
    print("📋 Current Frontmatter:")
    for key in ['status', 'ready_for_processing', 'ai_processed', 
                'processing_started_at', 'processing_completed_at']:
        value = frontmatter.get(key, '(not set)')
        print(f"   {key}: {value}")
    print()


def main():
    """Process a single YouTube note."""
    
    if len(sys.argv) < 2:
        print("Usage: python3 process_single_youtube_note.py <path_to_note.md>")
        print("\nExample:")
        print("  python3 process_single_youtube_note.py demos/youtube-demo-status-sync.md")
        return 1
    
    note_path = Path(sys.argv[1])
    
    if not note_path.exists():
        print(f"❌ Error: Note not found: {note_path}")
        return 1
    
    print_section(f"Processing YouTube Note: {note_path.name}")
    
    # Check initial state
    print("📊 BEFORE PROCESSING:")
    print_frontmatter(note_path)
    
    # Read and validate
    content = note_path.read_text(encoding='utf-8')
    frontmatter, _ = parse_frontmatter(content)
    
    # Check for required fields
    if frontmatter.get('source') != 'youtube':
        print("❌ Error: Not a YouTube note (source: youtube missing)")
        return 1
    
    if not frontmatter.get('video_id'):
        print("❌ Error: video_id missing from frontmatter")
        return 1
    
    # Check approval status (PBI-002)
    ready = frontmatter.get('ready_for_processing', False)
    if not ready:
        print("⏸️  Note is NOT approved for processing")
        print("   ready_for_processing: false")
        print("\n💡 To approve:")
        print("   1. Edit the note")
        print("   2. Change 'ready_for_processing: false' → 'ready_for_processing: true'")
        print("   3. Check the approval checkbox")
        print("   4. Save and run this script again")
        return 0
    
    print("✅ Note approved for processing (ready_for_processing: true)")
    print(f"   Video ID: {frontmatter.get('video_id')}")
    print(f"   Status: {frontmatter.get('status', 'not set')}")
    
    # Initialize handler
    print_section("Initializing YouTube Feature Handler")
    
    config = {
        'vault_path': str(note_path.parent.parent),
        'max_quotes': 10,
        'min_quality': 0.7
    }
    
    handler = YouTubeFeatureHandler(config=config)
    print(f"✅ Handler initialized")
    print(f"   Vault path: {config['vault_path']}")
    print(f"   Max quotes: {config['max_quotes']}")
    print(f"   Min quality: {config['min_quality']}")
    
    # Create mock event
    mock_event = Mock()
    mock_event.src_path = str(note_path.absolute())
    mock_event.event_type = 'modified'
    
    # Check if handler can process
    print_section("Checking Handler Approval (PBI-002)")
    
    can_handle = handler.can_handle(mock_event)
    print(f"   can_handle() returned: {can_handle}")
    
    if not can_handle:
        print("\n❌ Handler will NOT process this note")
        print("   Possible reasons:")
        print("   - Already processed (ai_processed: true)")
        print("   - Not approved (ready_for_processing: false)")
        print("   - Missing required fields")
        return 0
    
    print("✅ Handler will process this note!")
    
    # Process the note
    print_section("Processing Note (PBI-003 Status Sync)")
    
    print("🚀 Starting processing...")
    print("   This will:")
    print("   1. Update status: draft → processing")
    print("   2. Add processing_started_at timestamp")
    print("   3. Fetch YouTube transcript")
    print("   4. Extract AI quotes")
    print("   5. Insert quotes into note")
    print("   6. Update status: processing → processed")
    print("   7. Add processing_completed_at timestamp")
    print("   8. Set ai_processed: true")
    print()
    
    try:
        result = handler.handle(mock_event)
        
        print_section("Processing Complete!")
        
        print(f"✅ Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"   Quotes added: {result.get('quotes_added', 0)}")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            
            if result.get('transcript_file'):
                print(f"   Transcript saved: {result.get('transcript_file')}")
            if result.get('transcript_wikilink'):
                print(f"   Transcript link: {result.get('transcript_wikilink')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print("\n📊 AFTER PROCESSING:")
        print_frontmatter(note_path)
        
        if result.get('success'):
            print("🎉 Note successfully processed!")
            print("\n📝 Check the note file to see:")
            print("   ✅ AI-extracted quotes inserted")
            print("   ✅ Status updated to 'processed'")
            print("   ✅ Timestamps added")
            print("   ✅ Transcript archived")
            print("   ✅ ready_for_processing: true preserved")
        
        return 0 if result.get('success') else 1
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
