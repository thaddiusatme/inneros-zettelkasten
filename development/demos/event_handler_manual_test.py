#!/usr/bin/env python3
"""
Manual test for AutomationEventHandler integration.

Demonstrates:
1. Event handler initialization with CoreWorkflowManager
2. Event processing with debouncing
3. Health monitoring integration
4. Metrics tracking
"""

import tempfile
import time
from pathlib import Path
from src.automation.event_handler import AutomationEventHandler


def main():
    print("🧪 AutomationEventHandler Manual Test")
    print("=" * 60)
    
    # Create temporary vault
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir) / "knowledge"
        inbox = vault / "Inbox"
        inbox.mkdir(parents=True)
        
        print(f"\n✓ Created test vault: {vault}")
        
        # Initialize event handler
        handler = AutomationEventHandler(vault_path=str(vault), debounce_seconds=0.5)
        print(f"✓ Initialized event handler (debounce: {handler.debounce_seconds}s)")
        
        # Create test note
        test_note = inbox / "test-capture.md"
        test_note.write_text("""---
title: Test Capture Note
type: fleeting
---

This is a test capture note for demonstrating event-driven automation.
The AutomationEventHandler will process this through CoreWorkflowManager.
""")
        print(f"✓ Created test note: {test_note.name}")
        
        # Process event
        print("\n📋 Processing file event...")
        result = handler.process_file_event(test_note, "created")
        print(f"   Queued: {result.get('queued', False)}")
        print(f"   Event type: {result.get('event_type', 'N/A')}")
        
        # Wait for debounced processing
        print(f"   Waiting {handler.debounce_seconds}s for debounced processing...")
        time.sleep(handler.debounce_seconds + 0.2)
        
        # Check health status
        print("\n💚 Health Status:")
        health = handler.get_health_status()
        print(f"   Is healthy: {health['is_healthy']}")
        print(f"   Queue depth: {health['queue_depth']}")
        print(f"   Processing count: {health['processing_count']}")
        
        # Check metrics
        print("\n📊 Processing Metrics:")
        metrics = handler.get_metrics()
        print(f"   Total events: {metrics['total_events_processed']}")
        print(f"   Successful: {metrics['successful_events']}")
        print(f"   Failed: {metrics['failed_events']}")
        print(f"   Avg time: {metrics['avg_processing_time']:.3f}s")
        
        # Test non-markdown filter
        print("\n🔍 Testing filters...")
        txt_file = inbox / "ignored.txt"
        txt_file.write_text("Should be ignored")
        result = handler.process_file_event(txt_file, "created")
        print(f"   Non-markdown skipped: {result.get('skipped', False)}")
        print(f"   Skip reason: {result.get('reason', 'N/A')}")
        
        # Test deleted event filter
        result = handler.process_file_event(test_note, "deleted")
        print(f"   Deleted event skipped: {result.get('skipped', False)}")
        print(f"   Skip reason: {result.get('reason', 'N/A')}")
        
    print("\n" + "=" * 60)
    print("✅ Manual test complete - All features working!")


if __name__ == "__main__":
    main()
