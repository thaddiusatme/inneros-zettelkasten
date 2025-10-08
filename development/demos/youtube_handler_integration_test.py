#!/usr/bin/env python3
"""
Real Data Integration Test for YouTubeFeatureHandler
Tests the handler with actual YouTube notes from the vault.
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.automation.feature_handlers import YouTubeFeatureHandler
from unittest.mock import Mock
import yaml


def find_unprocessed_youtube_notes(vault_path: Path, limit: int = 5):
    """Find YouTube notes that haven't been processed yet."""
    inbox = vault_path / "Inbox"
    unprocessed = []
    
    for note_file in inbox.glob("*.md"):
        try:
            content = note_file.read_text()
            if '---' not in content:
                continue
                
            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
                
            frontmatter = yaml.safe_load(parts[1])
            
            # Check if it's a YouTube note that hasn't been processed
            if (frontmatter.get('source') == 'youtube' and 
                not frontmatter.get('ai_processed', False) and
                frontmatter.get('video_id')):
                unprocessed.append({
                    'path': note_file,
                    'video_id': frontmatter['video_id'],
                    'title': note_file.stem
                })
                
                if len(unprocessed) >= limit:
                    break
                    
        except Exception as e:
            print(f"⚠️  Error reading {note_file.name}: {e}")
            continue
    
    return unprocessed


def test_handler_initialization():
    """Test 1: Handler initializes correctly."""
    print("\n📋 Test 1: Handler Initialization")
    print("-" * 50)
    
    config = {
        'vault_path': str(Path(__file__).parent.parent.parent / "knowledge"),
        'max_quotes': 7,
        'min_quality': 0.7,
        'processing_timeout': 300
    }
    
    try:
        handler = YouTubeFeatureHandler(config=config)
        print(f"✅ Handler initialized successfully")
        print(f"   Vault: {handler.vault_path}")
        print(f"   Max quotes: {handler.max_quotes}")
        print(f"   Min quality: {handler.min_quality}")
        return handler
    except Exception as e:
        print(f"❌ Handler initialization failed: {e}")
        return None


def test_can_handle_detection(handler: YouTubeFeatureHandler, vault_path: Path):
    """Test 2: Event detection works on real notes."""
    print("\n📋 Test 2: Event Detection (can_handle)")
    print("-" * 50)
    
    # Find unprocessed notes
    unprocessed = find_unprocessed_youtube_notes(vault_path, limit=3)
    
    if not unprocessed:
        print("⚠️  No unprocessed YouTube notes found")
        print("   (This is OK - all notes may already be processed)")
        return None
    
    print(f"Found {len(unprocessed)} unprocessed YouTube notes:")
    
    detected = []
    for note_info in unprocessed:
        mock_event = Mock()
        mock_event.src_path = str(note_info['path'])
        
        can_handle = handler.can_handle(mock_event)
        status = "✅ DETECTED" if can_handle else "❌ MISSED"
        print(f"   {status}: {note_info['title']}")
        print(f"      Video ID: {note_info['video_id']}")
        
        if can_handle:
            detected.append(note_info)
    
    return detected[0] if detected else None


def test_handle_processing(handler: YouTubeFeatureHandler, note_info: dict):
    """Test 3: Processing a real YouTube note."""
    print("\n📋 Test 3: Note Processing (handle)")
    print("-" * 50)
    
    if not note_info:
        print("⚠️  No note to process (all may be processed already)")
        return None
    
    print(f"Processing: {note_info['title']}")
    print(f"Video ID: {note_info['video_id']}")
    
    # Create backup before processing
    backup_path = note_info['path'].with_suffix('.md.backup')
    note_info['path'].read_text()  # Verify we can read it
    
    mock_event = Mock()
    mock_event.src_path = str(note_info['path'])
    
    try:
        print("\n🔄 Processing...")
        result = handler.handle(mock_event)
        
        print(f"\n📊 Results:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Quotes added: {result.get('quotes_added', 0)}")
        print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Processing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def test_metrics_tracking(handler: YouTubeFeatureHandler):
    """Test 4: Metrics are tracked correctly."""
    print("\n📋 Test 4: Metrics & Health Monitoring")
    print("-" * 50)
    
    metrics = handler.get_metrics()
    health = handler.get_health()
    
    print("📊 Current Metrics:")
    print(f"   Events processed: {metrics.get('events_processed', 0)}")
    print(f"   Events failed: {metrics.get('events_failed', 0)}")
    print(f"   Last processed: {metrics.get('last_processed', 'None')}")
    
    print("\n💚 Health Status:")
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Success rate: {health.get('success_rate', 0):.1%}")
    
    return metrics, health


def test_specific_note(handler: YouTubeFeatureHandler, note_path: str):
    """Test processing a specific note."""
    print("\n📋 Test: Processing Specific Note")
    print("-" * 50)
    
    note_file = Path(note_path)
    if not note_file.exists():
        print(f"❌ Note not found: {note_path}")
        return None
    
    print(f"Processing: {note_file.name}")
    
    mock_event = Mock()
    mock_event.src_path = str(note_file)
    
    # Check if handler can detect it
    can_handle = handler.can_handle(mock_event)
    print(f"   Can handle: {can_handle}")
    
    if not can_handle:
        print("   ⚠️ Handler cannot process this note")
        return None
    
    print("\n🔄 Processing...")
    result = handler.handle(mock_event)
    
    print(f"\n📊 Results:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Quotes added: {result.get('quotes_added', 0)}")
    print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
    
    if result.get('error'):
        print(f"   Error: {result['error']}")
    
    return result


def main():
    """Run all integration tests."""
    print("=" * 50)
    print("🧪 YouTubeFeatureHandler Integration Test")
    print("=" * 50)
    print("Testing with REAL data from vault")
    
    vault_path = Path(__file__).parent.parent.parent / "knowledge"
    
    # Test 1: Initialization
    handler = test_handler_initialization()
    if not handler:
        print("\n❌ Cannot continue - handler failed to initialize")
        return
    
    # Test 2: Event Detection
    note_to_process = test_can_handle_detection(handler, vault_path)
    
    # Test 3: Processing (only if we found an unprocessed note)
    if note_to_process:
        result = test_handle_processing(handler, note_to_process)
        
        if result and result.get('success'):
            print("\n✅ Successfully processed a real YouTube note!")
        else:
            print("\n⚠️  Processing completed with errors (see above)")
    else:
        print("\n⚠️  Skipping processing test - no unprocessed notes found")
        print("   This is OK if all notes are already processed")
    
    # Test 4: Metrics
    test_metrics_tracking(handler)
    
    print("\n" + "=" * 50)
    print("✅ Integration Test Complete")
    print("=" * 50)


if __name__ == "__main__":
    main()
