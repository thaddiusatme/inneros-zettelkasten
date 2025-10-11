#!/usr/bin/env python3
"""
Feature Handlers Demo - Shows how to use ScreenshotEventHandler and SmartLinkEventHandler

Demonstrates:
1. Manual handler initialization
2. Direct handler registration with FileWatcher
3. Configuration-based handler setup via AutomationDaemon
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.automation.daemon import AutomationDaemon
from src.automation.config import (
    DaemonConfig, 
    FileWatchConfig,
    ScreenshotHandlerConfig,
    SmartLinkHandlerConfig
)
from src.automation.feature_handlers import ScreenshotEventHandler, SmartLinkEventHandler


def demo_manual_handler_setup():
    """Demo 1: Manual handler initialization and usage."""
    print("\n" + "=" * 70)
    print("DEMO 1: Manual Handler Initialization")
    print("=" * 70)
    
    # Create handlers manually
    screenshot_handler = ScreenshotEventHandler(
        onedrive_path="/Users/username/OneDrive/Pictures/Screenshots"
    )
    
    smart_link_handler = SmartLinkEventHandler(
        vault_path="/Users/username/repos/inneros-zettelkasten/knowledge"
    )
    
    print(f"✓ Screenshot handler initialized: {screenshot_handler.onedrive_path}")
    print(f"✓ Smart link handler initialized: {smart_link_handler.vault_path}")
    
    # Simulate file events
    test_screenshot = Path("/Users/username/OneDrive/Pictures/Screenshots/Screenshot_20251007-190000.jpg")
    test_note = Path("/Users/username/repos/inneros-zettelkasten/knowledge/Inbox/fleeting-test.md")
    
    print("\nSimulating file events:")
    screenshot_handler.process(test_screenshot, "created")
    smart_link_handler.process(test_note, "modified")
    
    print("\n✅ Manual handler demo complete")


def demo_daemon_integration():
    """Demo 2: Handler integration via AutomationDaemon configuration."""
    print("\n" + "=" * 70)
    print("DEMO 2: Daemon Integration with Feature Handlers")
    print("=" * 70)
    
    # Create configuration with handlers enabled
    config = DaemonConfig(
        check_interval=60,
        log_level="INFO",
        file_watching=FileWatchConfig(
            enabled=True,
            watch_path="knowledge/Inbox",
            debounce_seconds=2.0,
            ignore_patterns=[".obsidian/*", "*.tmp"]
        ),
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=True,
            onedrive_path="/Users/username/OneDrive/Pictures/Screenshots"
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=True
        )
    )
    
    # Create daemon with configuration
    daemon = AutomationDaemon(config=config)
    
    print("✓ Daemon created with feature handlers configured")
    print(f"  - Screenshot handler: {'enabled' if config.screenshot_handler.enabled else 'disabled'}")
    print(f"  - Smart link handler: {'enabled' if config.smart_link_handler.enabled else 'disabled'}")
    
    print("\nDaemon configuration:")
    print(f"  - File watching: {config.file_watching.enabled}")
    print(f"  - Watch path: {config.file_watching.watch_path}")
    print(f"  - Debounce: {config.file_watching.debounce_seconds}s")
    
    print("\n✅ Daemon integration demo complete")
    print("\nNote: Call daemon.start() to begin monitoring with handlers active")


def demo_usage_example():
    """Demo 3: Show typical usage patterns."""
    print("\n" + "=" * 70)
    print("DEMO 3: Typical Usage Example")
    print("=" * 70)
    
    print("""
Typical usage in your automation workflow:

```python
from src.automation.daemon import AutomationDaemon
from src.automation.config import (
    DaemonConfig,
    FileWatchConfig, 
    ScreenshotHandlerConfig,
    SmartLinkHandlerConfig
)

# Configure daemon with feature handlers
config = DaemonConfig(
    file_watching=FileWatchConfig(
        enabled=True,
        watch_path="knowledge/Inbox"
    ),
    screenshot_handler=ScreenshotHandlerConfig(
        enabled=True,
        onedrive_path="/path/to/onedrive/screenshots"
    ),
    smart_link_handler=SmartLinkHandlerConfig(
        enabled=True
    )
)

# Start daemon - handlers will be automatically registered
daemon = AutomationDaemon(config=config)
daemon.start()

# Handlers are now active:
# - New Samsung screenshots → OCR processing
# - Modified notes → Smart link analysis
# - All files → AI workflow processing

# When done:
daemon.stop()
```

Feature-specific behaviors:
- **ScreenshotEventHandler**: Monitors for Samsung Galaxy S23 screenshots
  - Pattern: Screenshot_YYYYMMDD-HHmmss*.jpg/png
  - Action: OCR extraction + daily note generation
  
- **SmartLinkEventHandler**: Monitors markdown notes
  - Pattern: *.md files
  - Action: Semantic similarity analysis + link suggestions
    """)
    
    print("\n✅ Usage example demo complete")


def main():
    print("\n🚀 Feature Handlers Demo")
    print("=" * 70)
    print("Demonstrating ScreenshotEventHandler and SmartLinkEventHandler")
    print("=" * 70)
    
    try:
        demo_manual_handler_setup()
        demo_daemon_integration()
        demo_usage_example()
        
        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70)
        
        print("\nNext steps:")
        print("1. Update OneDrive path in configuration to match your system")
        print("2. Enable handlers in .automation/config/automation_config.yaml")
        print("3. Start daemon: AutomationDaemon(config=config).start()")
        print("4. Monitor logs in .automation/logs/ for handler activity")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
