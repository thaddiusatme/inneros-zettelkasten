#!/usr/bin/env python3
"""
Phase 3.1 Metrics Collection Demo

Demonstrates:
1. MetricsCollector tracking workflow operations
2. MetricsDisplayFormatter output
3. Terminal dashboard integration
4. HTTP metrics endpoint

Usage:
    python3 demos/phase_3_1_metrics_demo.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring import (
    MetricsCollector,
    MetricsStorage,
    MetricsDisplayFormatter,
    MetricsEndpoint
)


def simulate_workflow_operations(metrics: MetricsCollector):
    """Simulate WorkflowManager operations with metrics."""
    print("🔧 Simulating workflow operations...\n")
    
    # Simulate processing 5 notes with varying times
    for i in range(5):
        start_time = time.time()
        
        # Simulate processing work
        time.sleep(0.05 + (i * 0.01))  # 50-90ms
        
        # Record metrics (like WorkflowManager does)
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.increment_counter("notes_processed")
        metrics.record_histogram("processing_time_ms", elapsed_ms)
        
        print(f"  ✓ Processed note {i+1} in {elapsed_ms:.1f}ms")
    
    # Simulate some AI API calls
    print("\n🤖 Simulating AI API calls...\n")
    for i in range(3):
        metrics.increment_counter("ai_api_calls")
        print(f"  ✓ AI API call {i+1}")
        time.sleep(0.02)
    
    # Set some gauge metrics
    metrics.set_gauge("active_watchers", 3)
    metrics.set_gauge("daemon_status", 1)  # 1 = running
    
    print("\n✅ Simulation complete!\n")


def display_metrics(collector: MetricsCollector, storage: MetricsStorage):
    """Display metrics using MetricsDisplayFormatter."""
    print("=" * 60)
    print("📊 METRICS DISPLAY OUTPUT")
    print("=" * 60)
    
    display = MetricsDisplayFormatter(collector, storage)
    
    # Show formatted summary
    summary = display.format_metrics_summary()
    print(summary)
    
    # Show table data format (for Rich tables)
    print("\n" + "─" * 60)
    print("TABLE FORMAT (for Rich display):")
    print("─" * 60)
    
    table_data = display.format_metrics_table_data()
    print(f"{'Metric':<25} {'Type':<12} {'Value':<20}")
    print("─" * 60)
    for row in table_data:
        print(f"{row[0]:<25} {row[1]:<12} {row[2]:<20}")
    
    # Show JSON format (for web/API)
    print("\n" + "─" * 60)
    print("JSON FORMAT (for API):")
    print("─" * 60)
    
    import json
    json_data = display.get_metrics_json()
    print(json.dumps(json_data["current"], indent=2))


def test_metrics_endpoint(collector: MetricsCollector, storage: MetricsStorage):
    """Test the HTTP metrics endpoint."""
    print("\n" + "=" * 60)
    print("🌐 HTTP METRICS ENDPOINT TEST")
    print("=" * 60)
    
    endpoint = MetricsEndpoint(collector, storage)
    response = endpoint.get_metrics()
    
    print("\nEndpoint Response:")
    print("─" * 60)
    
    import json
    print(json.dumps(response, indent=2))


def show_storage_info(storage: MetricsStorage):
    """Show storage statistics."""
    print("\n" + "=" * 60)
    print("💾 STORAGE INFORMATION")
    print("=" * 60)
    
    recent = storage.get_last_24h()
    print(f"\nStored snapshots (24h): {len(recent)}")
    
    if recent:
        latest = storage.get_latest()
        print(f"Latest snapshot time: {latest['timestamp']}")
        print(f"Metrics in snapshot: {len(latest['metrics']['counters'])} counters, "
              f"{len(latest['metrics']['gauges'])} gauges, "
              f"{len(latest['metrics']['histograms'])} histograms")


def test_rich_integration():
    """Test Rich table integration (if available)."""
    print("\n" + "=" * 60)
    print("🎨 RICH TABLE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from rich.console import Console
        from rich.table import Table
        from src.cli.terminal_dashboard_utils import TableRenderer, StatusFormatter
        
        # Create metrics
        collector = MetricsCollector()
        collector.increment_counter("notes_processed", 42)
        collector.increment_counter("ai_api_calls", 127)
        collector.set_gauge("daemon_status", 1.0)
        collector.set_gauge("active_watchers", 3.0)
        collector.record_histogram("processing_time_ms", 150)
        collector.record_histogram("processing_time_ms", 200)
        collector.record_histogram("processing_time_ms", 175)
        
        # Create Rich table
        formatter = StatusFormatter()
        renderer = TableRenderer(formatter, metrics_collector=collector)
        
        metrics_table = renderer.create_metrics_table()
        
        if metrics_table:
            console = Console()
            print("\n✓ Rich library available - displaying formatted table:\n")
            console.print(metrics_table)
        else:
            print("\n⚠ Rich library not available (install with: pip install rich)")
            
    except ImportError as e:
        print(f"\n⚠ Rich integration test skipped: {e}")
        print("  Install Rich with: pip install rich")


def main():
    """Run complete metrics demo."""
    print("\n" + "🚀 " * 20)
    print("Phase 3.1: Real-Time Metrics Collection Demo")
    print("🚀 " * 20 + "\n")
    
    # Initialize metrics system
    collector = MetricsCollector()
    storage = MetricsStorage()
    
    # 1. Simulate workflow operations
    simulate_workflow_operations(collector)
    
    # Store metrics snapshot
    storage.store(collector.get_all_metrics())
    
    # 2. Display metrics in various formats
    display_metrics(collector, storage)
    
    # 3. Test HTTP endpoint
    test_metrics_endpoint(collector, storage)
    
    # 4. Show storage info
    show_storage_info(storage)
    
    # 5. Test Rich integration
    test_rich_integration()
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE - ALL SYSTEMS OPERATIONAL")
    print("=" * 60)
    print("\nNext Steps:")
    print("  • View live dashboard: python3 -m src.cli.terminal_dashboard")
    print("  • Test with real WorkflowManager")
    print("  • Deploy to production")
    print("\n")


if __name__ == '__main__':
    main()
