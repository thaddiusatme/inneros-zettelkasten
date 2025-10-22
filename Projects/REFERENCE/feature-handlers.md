# Feature-Specific Handlers Integration

## Overview

Feature-specific handlers have been added to the AutomationDaemon system, enabling event-driven automation for specialized workflows beyond core AI processing.

## Components

### 1. ScreenshotEventHandler
**File**: `src/automation/feature_handlers.py`

Handles OneDrive screenshot events for evening workflow processing.

**Features**:
- Monitors Samsung Galaxy S23 screenshot naming patterns
- Filters for `Screenshot_YYYYMMDD-HHmmss*.jpg/png` files
- Triggers OCR processing and daily note generation
- Dedicated logging: `.automation/logs/screenshot_handler_YYYY-MM-DD.log`

**Configuration**:
```python
ScreenshotHandlerConfig(
    enabled=True,
    onedrive_path="/path/to/OneDrive/Pictures/Screenshots"
)
```

### 2. SmartLinkEventHandler
**File**: `src/automation/feature_handlers.py`

Handles automatic link suggestion and insertion for notes.

**Features**:
- Monitors markdown file changes
- Triggers smart link discovery and analysis
- Integrates with semantic similarity engine
- Dedicated logging: `.automation/logs/smart_link_handler_YYYY-MM-DD.log`

**Configuration**:
```python
SmartLinkHandlerConfig(
    enabled=True
)
```

## Integration Architecture

### Daemon Integration
**File**: `src/automation/daemon.py`

The `AutomationDaemon._setup_feature_handlers()` method:
1. Checks if file watcher is initialized
2. Creates handlers based on configuration
3. Registers handler callbacks with FileWatcher
4. Logs initialization success/failure

### Configuration Schema
**File**: `src/automation/config.py`

New dataclasses:
- `ScreenshotHandlerConfig`: Screenshot handler settings
- `SmartLinkHandlerConfig`: Smart link handler settings
- `DaemonConfig`: Extended with handler configuration fields

## Usage Examples

### Programmatic Setup

```python
from src.automation.daemon import AutomationDaemon
from src.automation.config import (
    DaemonConfig,
    FileWatchConfig,
    ScreenshotHandlerConfig,
    SmartLinkHandlerConfig
)

# Configure with handlers
config = DaemonConfig(
    file_watching=FileWatchConfig(
        enabled=True,
        watch_path="knowledge/Inbox"
    ),
    screenshot_handler=ScreenshotHandlerConfig(
        enabled=True,
        onedrive_path="/Users/username/OneDrive/Pictures/Screenshots"
    ),
    smart_link_handler=SmartLinkHandlerConfig(
        enabled=True
    )
)

# Start daemon with handlers
daemon = AutomationDaemon(config=config)
daemon.start()
```

### YAML Configuration

```yaml
file_watching:
  enabled: true
  watch_path: "knowledge/Inbox"

screenshot_handler:
  enabled: true
  onedrive_path: "/Users/USERNAME/OneDrive/Pictures/Screenshots"

smart_link_handler:
  enabled: true
```

### Manual Handler Usage

```python
from src.automation.feature_handlers import (
    ScreenshotEventHandler,
    SmartLinkEventHandler
)

# Create handlers
screenshot_handler = ScreenshotEventHandler(onedrive_path="...")
smart_link_handler = SmartLinkEventHandler(vault_path="...")

# Register with FileWatcher
daemon.file_watcher.register_callback(screenshot_handler.process)
daemon.file_watcher.register_callback(smart_link_handler.process)
```

## Event Flow

```
File System Event (watchdog)
        ↓
FileWatcher (debouncing)
        ↓
    Callbacks (parallel execution)
        ├→ AutomationEventHandler (AI processing)
        ├→ ScreenshotEventHandler (if screenshot)
        └→ SmartLinkEventHandler (if markdown)
```

## Handler Specifications

### Callback Signature
All handlers must implement:
```python
def process(self, file_path: Path, event_type: str) -> None:
    """FileWatcher callback signature."""
    pass
```

### Event Types
- `created`: File was created
- `modified`: File was modified
- `deleted`: File was deleted (usually filtered out)

### Filtering Strategy
Each handler implements its own filtering:
- **ScreenshotHandler**: Screenshot filename patterns + creation events only
- **SmartLinkHandler**: Markdown files (.md) + non-deletion events

## Logging

Each handler creates daily log files:
- `.automation/logs/screenshot_handler_YYYY-MM-DD.log`
- `.automation/logs/smart_link_handler_YYYY-MM-DD.log`

Log format:
```
YYYY-MM-DD HH:MM:SS [LEVEL] module.HandlerClass: message
```

## Architecture Compliance

**ADR-001 Compliance**:
- `feature_handlers.py`: ~160 LOC (<500 LOC limit)
- Single responsibility: Event filtering and feature-specific processing
- Modular: Each handler is independent
- Testable: Simple callback interface

## Future Integration

### Current Placeholders
Both handlers contain TODO comments for full integration:

```python
# TODO: Integrate with EveningScreenshotProcessor
# TODO: Integrate with LinkSuggestionEngine and LinkInsertionEngine
```

### Next Steps
1. Implement actual OCR processing in ScreenshotEventHandler
2. Integrate semantic analysis in SmartLinkEventHandler
3. Add handler-specific metrics and health checks
4. Implement configurable handler behavior (thresholds, filters)
5. Add handler-specific scheduled jobs

## Testing

### Demo Script
Run the feature handlers demo:
```bash
python development/demos/feature_handlers_demo.py
```

### Real Data Test
The existing `event_handler_real_data_test.py` validates the daemon integration infrastructure that handlers build upon.

## Files Modified/Created

### Created
- `development/src/automation/feature_handlers.py` (160 LOC)
- `development/examples/daemon_config_with_handlers.yaml`
- `development/demos/feature_handlers_demo.py`
- `development/docs/FEATURE-HANDLERS.md`

### Modified
- `development/src/automation/daemon.py`: Added `_setup_feature_handlers()` method
- `development/src/automation/config.py`: Added handler configuration classes

## Benefits

1. **Modularity**: Feature-specific logic isolated from core daemon
2. **Extensibility**: Easy to add new handlers following the pattern
3. **Configuration**: Enable/disable handlers without code changes
4. **Logging**: Separate logs for debugging feature-specific issues
5. **Parallel Processing**: Multiple handlers process events concurrently
6. **Type Safety**: Full type hints with Optional guards

## Summary

The feature-specific handlers system extends the AutomationDaemon with pluggable, event-driven automation for specialized workflows. Handlers can be enabled via configuration and automatically register with the FileWatcher for real-time event processing.
