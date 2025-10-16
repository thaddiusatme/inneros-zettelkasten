#!/usr/bin/env python3
"""
Test Metrics HTTP Endpoint

Demonstrates the /metrics endpoint that can be accessed via HTTP.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring import MetricsCollector, MetricsStorage, MetricsEndpoint
import json


def test_metrics_endpoint():
    """Test the HTTP metrics endpoint."""
    print("\n" + "🌐 " * 20)
    print("Metrics HTTP Endpoint Test")
    print("🌐 " * 20 + "\n")
    
    # Setup metrics
    collector = MetricsCollector()
    storage = MetricsStorage()
    endpoint = MetricsEndpoint(collector, storage)
    
    print("Step 1: Collecting sample metrics...\n")
    
    # Simulate some activity
    collector.increment_counter("api_requests", 42)
    collector.increment_counter("notes_processed", 15)
    collector.set_gauge("active_connections", 3)
    collector.set_gauge("cpu_usage", 45.7)
    collector.record_histogram("response_time_ms", 125)
    collector.record_histogram("response_time_ms", 98)
    collector.record_histogram("response_time_ms", 203)
    
    print("  ✓ Collected 2 counters")
    print("  ✓ Collected 2 gauges")
    print("  ✓ Collected 3 histogram samples\n")
    
    # Store snapshot
    storage.store(collector.get_all_metrics())
    print("  ✓ Stored metrics snapshot\n")
    
    print("Step 2: Calling GET /metrics endpoint...\n")
    
    # Call the endpoint (simulates HTTP GET request)
    response = endpoint.get_metrics()
    
    print("=" * 60)
    print("📋 ENDPOINT RESPONSE")
    print("=" * 60 + "\n")
    
    # Pretty print the response
    print(json.dumps(response, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION")
    print("=" * 60 + "\n")
    
    # Verify response structure
    checks = [
        ("Has 'status' field", 'status' in response),
        ("Status is 'success'", response.get('status') == 'success'),
        ("Has 'timestamp' field", 'timestamp' in response),
        ("Has 'current' metrics", 'current' in response),
        ("Current has counters", 'counters' in response.get('current', {})),
        ("Current has gauges", 'gauges' in response.get('current', {})),
        ("Current has histograms", 'histograms' in response.get('current', {})),
        ("Has 'history' field", 'history' in response),
        ("Counters correct", response.get('current', {}).get('counters', {}).get('api_requests') == 42),
        ("Gauges correct", response.get('current', {}).get('gauges', {}).get('active_connections') == 3),
        ("Histogram samples", len(response.get('current', {}).get('histograms', {}).get('response_time_ms', [])) == 3)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        all_passed = all_passed and passed
    
    print("\n" + "=" * 60)
    print("📊 METRICS SUMMARY")
    print("=" * 60 + "\n")
    
    current = response.get('current', {})
    
    print("Counters:")
    for name, value in current.get('counters', {}).items():
        print(f"  • {name}: {value:,}")
    
    print("\nGauges:")
    for name, value in current.get('gauges', {}).items():
        print(f"  • {name}: {value:.1f}")
    
    print("\nHistograms:")
    for name, values in current.get('histograms', {}).items():
        if values:
            avg = sum(values) / len(values)
            print(f"  • {name}: {len(values)} samples, avg={avg:.1f}ms")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - ENDPOINT WORKING CORRECTLY")
    else:
        print("❌ SOME CHECKS FAILED - SEE OUTPUT ABOVE")
    print("=" * 60)
    
    print("\n💡 Integration Notes:")
    print("  • This endpoint can be exposed via Flask/FastAPI")
    print("  • Response format is JSON (ready for AJAX/fetch)")
    print("  • Includes both current metrics and history")
    print("  • Timestamp allows client-side caching")
    print("  • Ready for Prometheus/Grafana integration\n")
    
    return all_passed


if __name__ == '__main__':
    success = test_metrics_endpoint()
    sys.exit(0 if success else 1)
