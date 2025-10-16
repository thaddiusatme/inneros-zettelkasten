#!/usr/bin/env python3
"""
Test WorkflowManager Metrics Integration

Tests the actual WorkflowManager with metrics instrumentation.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.workflow_manager import WorkflowManager
from src.monitoring import MetricsDisplayFormatter, MetricsStorage


def create_test_vault():
    """Create a temporary test vault structure."""
    vault = Path(tempfile.mkdtemp())
    (vault / "Inbox").mkdir()
    (vault / "Fleeting Notes").mkdir()
    (vault / "Literature Notes").mkdir()
    (vault / "Permanent Notes").mkdir()
    (vault / "Archive").mkdir()
    
    # Create a test note
    test_note = vault / "Inbox" / "test-note.md"
    test_note.write_text("""---
title: Test Note
type: fleeting
tags: [test, demo]
---

# Test Note

This is a test note for metrics demonstration.
Testing the WorkflowManager metrics instrumentation.
""")
    
    return vault, test_note


def test_workflow_manager_metrics():
    """Test WorkflowManager with metrics enabled."""
    print("\n" + "🧪 " * 20)
    print("WorkflowManager Metrics Integration Test")
    print("🧪 " * 20 + "\n")
    
    # Create test vault
    vault, test_note = create_test_vault()
    print(f"✓ Created test vault: {vault}")
    print(f"✓ Created test note: {test_note.name}\n")
    
    # Initialize WorkflowManager (has built-in metrics coordinator)
    print("🔧 Initializing WorkflowManager with metrics...\n")
    wm = WorkflowManager(base_directory=str(vault))
    
    # Verify metrics coordinator exists
    assert hasattr(wm, 'metrics_coordinator'), "WorkflowManager should have metrics_coordinator attribute"
    print("✓ WorkflowManager.metrics_coordinator initialized")
    
    # Check initial metrics state
    initial_metrics = wm.metrics_coordinator.get_metrics()
    print(f"✓ Initial counters: {initial_metrics['counters']}")
    print(f"✓ Initial gauges: {initial_metrics['gauges']}")
    print(f"✓ Initial histograms: {initial_metrics['histograms']}\n")
    
    # Process note with metrics tracking
    print("📝 Processing test note (this collects metrics)...\n")
    
    # Mock the coordinator's process_note to avoid actual AI calls
    from unittest.mock import patch
    with patch.object(wm.note_processing_coordinator, 'process_note', 
                     return_value={'status': 'success', 'tags': ['test'], 'quality_score': 0.8}):
        result = wm.process_inbox_note(str(test_note))
    
    print(f"✓ Note processed: {result.get('status', 'unknown')}\n")
    
    # Check updated metrics
    updated_metrics = wm.metrics_coordinator.get_metrics()
    
    print("=" * 60)
    print("📊 METRICS AFTER PROCESSING")
    print("=" * 60 + "\n")
    
    # Display counters
    print("Counters:")
    for name, value in updated_metrics['counters'].items():
        print(f"  • {name}: {value}")
    
    # Display gauges
    print("\nGauges:")
    for name, value in updated_metrics['gauges'].items():
        print(f"  • {name}: {value:.2f}")
    
    # Display histograms
    print("\nHistograms:")
    for name, values in updated_metrics['histograms'].items():
        if values:
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            print(f"  • {name}: avg={avg:.1f}ms, min={min_val:.1f}ms, max={max_val:.1f}ms, samples={len(values)}")
    
    # Verify expected metrics were recorded
    print("\n" + "=" * 60)
    print("✅ VERIFICATION")
    print("=" * 60 + "\n")
    
    checks = [
        ("notes_processed counter", 
         updated_metrics['counters'].get('notes_processed', 0) >= 1,
         f"Expected ≥1, got {updated_metrics['counters'].get('notes_processed', 0)}"),
        
        ("daemon_status gauge", 
         updated_metrics['gauges'].get('daemon_status', 0) == 1,
         f"Expected 1, got {updated_metrics['gauges'].get('daemon_status', 0)}"),
        
        ("processing_time_ms histogram",
         len(updated_metrics['histograms'].get('processing_time_ms', [])) >= 1,
         f"Expected ≥1 sample, got {len(updated_metrics['histograms'].get('processing_time_ms', []))}")
    ]
    
    all_passed = True
    for check_name, passed, details in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}: {details}")
        all_passed = all_passed and passed
    
    # Format with MetricsDisplayFormatter
    print("\n" + "=" * 60)
    print("🎨 FORMATTED DISPLAY")
    print("=" * 60 + "\n")
    
    storage = MetricsStorage()
    storage.store(updated_metrics)
    display = MetricsDisplayFormatter(wm.metrics_coordinator.collector, storage)
    
    print(display.format_metrics_summary())
    
    # Cleanup
    import shutil
    shutil.rmtree(vault)
    print("\n✓ Cleaned up test vault")
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - METRICS INTEGRATION WORKING")
    else:
        print("❌ SOME TESTS FAILED - CHECK OUTPUT ABOVE")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = test_workflow_manager_metrics()
    sys.exit(0 if success else 1)
