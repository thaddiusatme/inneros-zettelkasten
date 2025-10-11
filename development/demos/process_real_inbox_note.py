#!/usr/bin/env python3
"""
Test automation system on a real Inbox note.
Demonstrates event-driven processing with CoreWorkflowManager integration.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from automation.daemon import AutomationDaemon
from automation.event_handler import AutomationEventHandler

def main():
    vault_path = Path(__file__).parent.parent.parent / 'knowledge'
    
    print("\n" + "="*70)
    print("  🧪 Real Inbox Note Processing Test")
    print("="*70)
    
    # Create event handler (this is what daemon uses)
    print("\n📋 Initializing AutomationEventHandler...")
    handler = AutomationEventHandler(
        vault_path=str(vault_path),
        debounce_seconds=0.5  # Shorter for testing
    )
    print(f"✓ Handler initialized")
    print(f"  Vault: {vault_path}")
    print(f"  Debounce: 0.5s")
    
    # Find a real note to process
    inbox_path = vault_path / 'Inbox'
    test_notes = [
        'lit-20251003-0925-ai-channels-are-taking-over-warhammer-40k-lore-on-youtube.md',
        'fleeting-20251006-1642-flowchart-3.md.md',
        'capture-20250926-0954-management.md'
    ]
    
    test_note = None
    for note_name in test_notes:
        note_path = inbox_path / note_name
        if note_path.exists():
            test_note = note_path
            break
    
    if not test_note:
        # Fallback to any .md file
        md_files = list(inbox_path.glob('*.md'))
        if md_files:
            test_note = md_files[0]
    
    if not test_note:
        print("❌ No markdown files found in Inbox")
        return 1
    
    print(f"\n📝 Processing real note:")
    print(f"  File: {test_note.name}")
    print(f"  Size: {test_note.stat().st_size} bytes")
    
    # Simulate file event (what FileWatcher would do)
    print(f"\n⚡ Simulating file 'modified' event...")
    result = handler.process_file_event(test_note, 'modified')
    
    if result.get('queued'):
        print(f"✓ Event queued for debounced processing")
        print(f"  Waiting {handler.debounce_seconds}s for processing...")
        time.sleep(handler.debounce_seconds + 0.5)  # Wait for debounce + processing
    elif result.get('skipped'):
        print(f"⚠️  Event skipped: {result.get('reason')}")
        return 0
    
    # Check metrics
    print(f"\n📊 Processing Results:")
    metrics = handler.get_metrics()
    print(f"  Total events: {metrics['total_events_processed']}")
    print(f"  Successful: {metrics['successful_events']}")
    print(f"  Failed: {metrics['failed_events']}")
    
    if metrics.get('processing_times') and len(metrics['processing_times']) > 0:
        avg_time = sum(metrics['processing_times']) / len(metrics['processing_times'])
        print(f"  Avg processing time: {avg_time:.3f}s")
    elif metrics.get('average_processing_time'):
        print(f"  Avg processing time: {metrics['average_processing_time']:.3f}s")
    
    # Health status
    print(f"\n💚 Health Check:")
    health = handler.get_health_status()
    print(f"  Is healthy: {health['is_healthy']}")
    print(f"  Queue depth: {health['queue_depth']}")
    print(f"  Total processed: {health['processing_count']}")
    
    if metrics['successful_events'] > 0:
        print(f"\n✅ Real note processed successfully!")
        print(f"\n🎉 Event-driven automation working on real data!")
    else:
        print(f"\n⚠️  Note was queued but processing may still be in progress")
    
    print("\n" + "="*70)
    print("  ✅ Real Inbox Test Complete")
    print("="*70 + "\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
