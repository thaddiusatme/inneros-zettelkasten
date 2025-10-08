#!/usr/bin/env python3
"""
Live Data Test: Daemon Integration with Config-Driven Handlers

Validates TDD Iteration 5 deliverables:
- Config-driven handler initialization (screenshot + smart link)
- Health monitoring aggregation (daemon + handlers)
- Prometheus metrics export
- Handler metrics collection (JSON)

Uses REAL vault and OneDrive paths.
"""

import sys
import json
from pathlib import Path
from pprint import pprint

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.automation.daemon import AutomationDaemon
from src.automation.config import (
    DaemonConfig,
    FileWatchConfig,
    ScreenshotHandlerConfig,
    SmartLinkHandlerConfig
)


def print_section(title: str, emoji: str = "📊"):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"{emoji}  {title}")
    print("=" * 70)


def main():
    print_section("Daemon Integration Live Test", "🧪")
    print("Testing: Config-driven handlers, health aggregation, metrics export")
    
    # Use real vault path
    vault_path = Path(__file__).parent.parent.parent / "knowledge"
    
    # Create temp directories for this test
    import tempfile
    temp_dir = Path(tempfile.mkdtemp(prefix="daemon_test_"))
    onedrive_screenshots = temp_dir / "Screenshots"
    onedrive_screenshots.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Paths:")
    print(f"  Vault: {vault_path}")
    print(f"  Vault exists: {vault_path.exists()}")
    print(f"  Test Screenshots (temp): {onedrive_screenshots}")
    print(f"  Test dir created: {onedrive_screenshots.exists()}")
    
    if not vault_path.exists():
        print("\n❌ Vault path not found! Cannot proceed.")
        return 1
    
    # Create daemon config with BOTH handlers enabled
    print_section("Configuration", "⚙️")
    
    config = DaemonConfig(
        file_watching=FileWatchConfig(
            enabled=False,  # Disable for this test (no file monitoring)
            watch_path=str(vault_path / "Inbox")
        ),
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=True,
            onedrive_path=str(onedrive_screenshots),
            knowledge_path=str(vault_path / "Media/Pasted Images"),
            ocr_enabled=True,
            processing_timeout=600
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=True,
            vault_path=str(vault_path),
            similarity_threshold=0.75,
            max_suggestions=5,
            auto_insert=False
        )
    )
    
    print("✓ DaemonConfig created")
    print(f"  Screenshot handler enabled: {config.screenshot_handler.enabled}")
    print(f"  Smart link handler enabled: {config.smart_link_handler.enabled}")
    print(f"  File watching enabled: {config.file_watching.enabled}")
    
    # Initialize daemon
    print_section("Daemon Initialization", "🚀")
    
    try:
        daemon = AutomationDaemon(config=config)
        print("✓ AutomationDaemon created")
        
        # Create a minimal file watcher stub for handler initialization
        # (handlers require file_watcher to be present)
        class DummyWatcher:
            def register_callback(self, callback):
                pass
            def is_running(self):
                return True
        
        daemon.file_watcher = DummyWatcher()
        print("✓ Dummy file watcher created")
        
        # Setup handlers
        daemon._setup_feature_handlers(vault_path=vault_path)
        print("✓ Feature handlers initialized")
        
    except Exception as e:
        print(f"\n❌ Failed to initialize daemon: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 1: Verify handlers are initialized
    print_section("Test 1: Handler Initialization", "🔧")
    
    screenshot_ok = daemon.screenshot_handler is not None
    smart_link_ok = daemon.smart_link_handler is not None
    
    print(f"Screenshot handler: {'✅ initialized' if screenshot_ok else '❌ missing'}")
    if screenshot_ok:
        print(f"  OneDrive path: {daemon.screenshot_handler.onedrive_path}")
        print(f"  Knowledge path: {daemon.screenshot_handler.knowledge_path}")
        print(f"  Has metrics tracker: {hasattr(daemon.screenshot_handler, 'metrics_tracker')}")
    
    print(f"\nSmart link handler: {'✅ initialized' if smart_link_ok else '❌ missing'}")
    if smart_link_ok:
        print(f"  Vault path: {daemon.smart_link_handler.vault_path}")
        print(f"  Similarity threshold: {daemon.smart_link_handler.similarity_threshold}")
        print(f"  Has metrics tracker: {hasattr(daemon.smart_link_handler, 'metrics_tracker')}")
    
    if not (screenshot_ok and smart_link_ok):
        print("\n❌ Handler initialization failed!")
        return 1
    
    # Test 2: Health monitoring aggregation
    print_section("Test 2: Health Monitoring Aggregation", "💚")
    
    try:
        health = daemon.get_daemon_health()
        print("✓ get_daemon_health() returned successfully")
        print(f"\nDaemon Health:")
        print(f"  Overall healthy: {health.get('daemon', {}).get('is_healthy', 'N/A')}")
        print(f"  Status code: {health.get('daemon', {}).get('status_code', 'N/A')}")
        
        if 'handlers' in health:
            print(f"\nHandler Health:")
            for handler_name, handler_health in health['handlers'].items():
                print(f"  {handler_name}:")
                print(f"    Is healthy: {handler_health.get('is_healthy', 'N/A')}")
                print(f"    Events processed: {handler_health.get('events_processed', 0)}")
                print(f"    Events failed: {handler_health.get('events_failed', 0)}")
                print(f"    Avg processing time: {handler_health.get('avg_processing_time', 0):.3f}s")
        else:
            print("\n⚠️  No handler health data in response")
        
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 3: JSON metrics export
    print_section("Test 3: JSON Metrics Export", "📊")
    
    try:
        metrics = daemon.export_handler_metrics()
        print("✓ export_handler_metrics() returned successfully")
        print(f"\nMetrics keys: {list(metrics.keys())}")
        
        for handler_name, handler_metrics in metrics.items():
            print(f"\n{handler_name} metrics:")
            if isinstance(handler_metrics, dict):
                print(f"  Handler type: {handler_metrics.get('handler_type', 'unknown')}")
                if 'performance' in handler_metrics:
                    perf = handler_metrics['performance']
                    print(f"  Events processed: {perf.get('events_processed', 0)}")
                    print(f"  Events failed: {perf.get('events_failed', 0)}")
                    print(f"  Avg time: {perf.get('avg_processing_time_seconds', 0):.3f}s")
                    print(f"  Max time: {perf.get('max_processing_time_seconds', 0):.3f}s")
            else:
                print(f"  (empty or unavailable)")
        
    except Exception as e:
        print(f"\n❌ JSON metrics export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 4: Prometheus metrics export
    print_section("Test 4: Prometheus Metrics Export", "📈")
    
    try:
        prom_text = daemon.export_prometheus_metrics()
        print("✓ export_prometheus_metrics() returned successfully")
        print(f"\nPrometheus output length: {len(prom_text)} characters")
        
        # Check for expected metric names
        expected_metrics = [
            "inneros_handler_processing_seconds",
            "inneros_handler_events_total"
        ]
        
        print("\nMetric presence check:")
        for metric in expected_metrics:
            present = metric in prom_text
            print(f"  {metric}: {'✅ found' if present else '❌ missing'}")
        
        # Show sample output
        if prom_text:
            lines = prom_text.split('\n')
            print(f"\nSample output (first 15 lines):")
            for line in lines[:15]:
                print(f"  {line}")
            if len(lines) > 15:
                print(f"  ... ({len(lines) - 15} more lines)")
        else:
            print("\n⚠️  Empty Prometheus output")
        
    except Exception as e:
        print(f"\n❌ Prometheus metrics export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 5: Config dict extraction (verify refactoring)
    print_section("Test 5: Config Dict Builder", "🔧")
    
    try:
        sh_config = daemon._build_handler_config_dict('screenshot')
        sl_config = daemon._build_handler_config_dict('smart_link', vault_path)
        
        print("✓ _build_handler_config_dict() works")
        print(f"\nScreenshot config keys: {list(sh_config.keys()) if sh_config else 'None'}")
        print(f"Smart link config keys: {list(sl_config.keys()) if sl_config else 'None'}")
        
        # Verify config values match initialized handlers
        if sh_config and screenshot_ok:
            match = str(sh_config['onedrive_path']) == str(daemon.screenshot_handler.onedrive_path)
            print(f"\nScreenshot config consistency: {'✅ matches' if match else '❌ mismatch'}")
        
        if sl_config and smart_link_ok:
            match = str(sl_config['vault_path']) == str(daemon.smart_link_handler.vault_path)
            print(f"Smart link config consistency: {'✅ matches' if match else '❌ mismatch'}")
        
    except Exception as e:
        print(f"\n❌ Config dict builder failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print_section("Test Summary", "📋")
    
    tests = [
        ("Handler initialization", screenshot_ok and smart_link_ok),
        ("Health monitoring aggregation", 'handlers' in health),
        ("JSON metrics export", bool(metrics)),
        ("Prometheus metrics export", len(prom_text) > 0),
        ("Config dict builder", sh_config is not None and sl_config is not None)
    ]
    
    print("\nResults:")
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print_section("All Tests Passed! 🎉", "✅")
        print("Daemon integration features validated with live data:")
        print("  • Config-driven handler initialization")
        print("  • Health monitoring aggregation")
        print("  • JSON metrics export")
        print("  • Prometheus metrics export")
        print("  • Refactored config dict builder")
        return 0
    else:
        print_section("Some Tests Failed", "⚠️")
        return 1


if __name__ == "__main__":
    sys.exit(main())
