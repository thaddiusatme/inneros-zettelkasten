# Daemon Registry Maintenance Guide

**File**: `.automation/config/daemon_registry.yaml`  
**Owner**: InnerOS Automation Team  
**Last Updated**: 2025-10-23

## Overview

The daemon registry is the single source of truth for all automation daemons in the InnerOS system. It enables the Automation Visibility CLI to monitor daemon status, logs, and health.

## When to Update

Add a new daemon entry when:
- ✅ Creating a new background automation script
- ✅ Converting an existing script to daemon mode
- ✅ Adding cron-scheduled automation that should be monitored

Do NOT add entries for:
- ❌ One-time scripts or manual operations
- ❌ Non-background processes (CLI commands)
- ❌ External services (GitHub Actions, etc.)

## Adding a New Daemon

### Step 1: Copy Template

```yaml
  - name: my_new_daemon
    script_path: .automation/scripts/my_new_daemon.py
    log_path: .automation/logs/my_new_daemon.log
    pid_file: .automation/logs/my_new_daemon.pid
    description: Brief description of what this daemon does
```

### Step 2: Update Fields

| Field | Rules | Example |
|-------|-------|---------|
| `name` | Lowercase, underscore-separated, unique | `reading_intake_processor` |
| `script_path` | Relative to repo root, must exist | `.automation/scripts/reading_intake.py` |
| `log_path` | Relative to repo root, in `.automation/logs/` | `.automation/logs/reading_intake.log` |
| `pid_file` | Relative to repo root, in `.automation/logs/` | `.automation/logs/reading_intake.pid` |
| `description` | Present tense, concise (under 80 chars) | `Processes reading intake from Notion` |

### Step 3: Validate

Run the validation test:

```bash
cd development
PYTHONPATH=/Users/thaddius/repos/inneros-zettelkasten/development \
pytest tests/unit/cli/test_automation_status_cli.py::TestDaemonRegistry::test_validates_daemon_config -v
```

### Step 4: Test Integration

Test that the new daemon appears in status:

```bash
cd development
python3 -c "
from pathlib import Path
from src.cli.automation_status_cli import AutomationStatusCLI

cli = AutomationStatusCLI(
    registry_path=Path('../.automation/config/daemon_registry.yaml'),
    workspace_root=Path('..')
)
result = cli.status()
print(f'Total daemons: {result[\"total_daemons\"]}')
for status in result['daemon_statuses']:
    print(f'  - {status[\"name\"]}: {\"running\" if status[\"running\"] else \"stopped\"}')
"
```

### Step 5: Update Documentation

Update the following:
- `daemon_registry.yaml` - Update "Last updated" date
- This file - Add to "Current Daemons" section below
- Any relevant project docs mentioning automation

### Step 6: Commit

```bash
git add .automation/config/daemon_registry.yaml
git commit -m "config: Add [daemon_name] to daemon registry

- Added monitoring for [daemon_name]
- Updates automation visibility CLI
- Tested with test_automation_status_cli.py"
```

## Current Daemons (as of 2025-10-23)

| Name | Script | Description |
|------|--------|-------------|
| `health_monitor` | `.automation/scripts/health_monitor.py` | System health monitoring daemon |
| `screenshot_processor` | `.automation/scripts/process_screenshots.py` | Processes Samsung screenshot imports |
| `youtube_watcher` | `.automation/scripts/automated_screenshot_import.sh` | Monitors YouTube content for processing |

## Schema Validation

The `DaemonRegistry` class automatically validates entries on load. Required fields:

```python
REQUIRED_FIELDS = ['name', 'script_path', 'log_path', 'pid_file', 'description']
```

Missing fields will raise `ValueError` with details.

## Troubleshooting

### "Unknown daemon" error

**Problem**: Added daemon but CLI can't find it  
**Solution**: Check for typos in `name` field - names are case-sensitive

### Validation fails

**Problem**: `pytest` shows "Missing required fields"  
**Solution**: Ensure all 5 required fields are present with proper indentation (2 spaces)

### Daemon shows as "stopped" when running

**Problem**: Status shows 🔴 but process is active  
**Solution**: Check `script_path` matches actual running process command line exactly

## Best Practices

1. **Alphabetical Order** - Keep daemons sorted by `name` for easy discovery
2. **Consistent Naming** - Use `_daemon` or `_processor` suffixes
3. **Descriptive Names** - `description` should be actionable (what it does, not what it is)
4. **Path Consistency** - All logs in `.automation/logs/`, all scripts in `.automation/scripts/`
5. **Test First** - Run validation tests before committing
6. **Update README** - Keep documentation in sync with actual daemons

## Future Enhancements

Planned improvements (P1/P2 features):

- **Auto-discovery**: Script to scan `.automation/scripts/` and suggest missing entries
- **Schema validation**: JSON Schema or Pydantic model for strict validation
- **Health checks**: Integration with health_monitor.py for daemon-specific checks
- **Status dashboard**: Web UI showing all daemon statuses in real-time
- **Alert integration**: Notifications when daemons fail or stop unexpectedly

## Related Files

- **Implementation**: `development/src/cli/automation_status_cli.py`
- **Tests**: `development/tests/unit/cli/test_automation_status_cli.py`
- **Daemon Scripts**: `.automation/scripts/`
- **Logs**: `.automation/logs/`
- **Lessons Learned**: `Projects/ACTIVE/automation-visibility-cli-tdd-iteration-1-lessons-learned.md`

## Questions?

If you're unsure whether to add a daemon or how to configure it:

1. Check existing entries for similar patterns
2. Run the validation tests
3. Ask in project documentation or issues

---

**Maintenance Cadence**: Review quarterly or when adding new automation features
