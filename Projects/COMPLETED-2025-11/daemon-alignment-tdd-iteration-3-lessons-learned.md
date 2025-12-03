# TDD Iteration 3: Daemon Alignment Lessons Learned

**Date**: 2025-12-02
**Branch**: `feat/phase1-core-automation-daemon-alignment`
**Duration**: ~45 minutes
**Status**: ✅ COMPLETE

## Problem Statement

Critical architecture mismatch between `make up` and `make status`:
- `make up` started Python daemon (`AutomationDaemon`) → writes PID to `~/.inneros/daemon.pid`
- `make status` checked for shell scripts via `ps aux` pattern matching → never found them
- Result: `make status` always showed `0/3 running` even when daemon was running

## Root Cause Analysis

1. **daemon_registry.yaml** defined 3 shell scripts as "daemons" (`youtube_watcher.sh`, `screenshot_processor.sh`, `health_monitor.sh`)
2. **DaemonDetector.check_daemon_status()** searched `ps aux` for script paths in process command lines
3. **AutomationDaemon** (Python) used PID file at `~/.inneros/daemon.pid`, not detectable via script path matching
4. One script (`health_monitor.sh`) didn't even exist

## Solution

### Simplified to 1-Daemon Model
Changed from tracking 3 non-existent shell scripts to 1 Python daemon that actually runs.

### PID File Detection
Added `DaemonDetector.check_daemon_by_pid_file()` method that:
1. Reads PID from file
2. Validates process is actually running (`os.kill(pid, 0)`)
3. Handles stale PID files gracefully

### Updated Registry
```yaml
# Before: 3 shell scripts that don't run as daemons
daemons:
  - name: youtube_watcher
    script_path: process_youtube_note.sh
  - name: screenshot_processor  
    script_path: .automation/scripts/automated_screenshot_import.sh
  - name: health_monitor
    script_path: .automation/scripts/health_monitor.sh  # DIDN'T EXIST!

# After: 1 Python daemon with PID file detection
daemons:
  - name: automation_daemon
    script_path: src.automation.daemon
    pid_file: ~/.inneros/daemon.pid
```

## TDD Cycle Summary

### RED Phase (8 failing, 3 passing)
- Tests expecting `_get_daemon_pid_file()` function
- Tests expecting `check_daemon_by_pid_file()` method
- Tests for stale PID file handling

### GREEN Phase (11/11 passing)
Minimal implementation:
1. Added `_get_daemon_pid_file()` to `system_health.py`
2. Added `check_daemon_by_pid_file()` to `DaemonDetector`
3. Updated `_build_automation_entry()` to use PID file when `pid_file` field present

### REFACTOR Phase
1. Updated `daemon_registry.yaml` to single Python daemon
2. Added tilde expansion for `~/.inneros/daemon.pid`
3. Cleaned up unused imports in tests
4. Verified 11 + 28 = 39 total tests passing

## Verification

```bash
# Before fix
$ make status
Daemons: 0/3 running  # Always 0 even when daemon running!

# After fix
$ make up
Daemon started with PID 74232

$ make status  
Daemons: 1/1 running
- automation_daemon: running
Overall status: OK

$ make down && make status
Daemons: 0/1 running
- automation_daemon: not running
Overall status: ERROR
```

## Key Learnings

### 1. Registry vs Reality Mismatch
The daemon registry documented an aspirational architecture (3 specialized daemons) while the actual implementation was different (1 unified Python daemon). Code should reflect reality, not wishful thinking.

### 2. PID File > Process Scanning
PID file detection is more reliable than `ps aux` pattern matching for Python daemons because:
- Python module paths don't appear in command line the same way as script paths
- Background subprocesses may have different parent/child relationships
- PID files are the canonical "daemon is running" signal

### 3. Tilde Expansion Required
YAML config with `~/.inneros/daemon.pid` requires explicit `Path.expanduser()` call. Easy to miss!

### 4. Architecture Simplification
Going from 3-daemon to 1-daemon model:
- Reduced cognitive complexity
- Eliminated non-existent script references
- Made status output cleaner and more accurate

## Files Changed

| File | Change |
|------|--------|
| `.automation/config/daemon_registry.yaml` | 3 → 1 daemon, Python module + PID file |
| `development/src/cli/automation_status_cli.py` | Added `check_daemon_by_pid_file()` |
| `development/src/automation/system_health.py` | Added PID file support + tilde expansion |
| `development/tests/unit/automation/test_daemon_alignment.py` | 11 comprehensive tests (NEW) |

## Acceptance Criteria Met

- ✅ `make up && make status` shows daemon running, exits 0
- ✅ `make down && make status` shows daemon stopped, exits non-zero

## Next Steps (P1)

1. **Clean shutdown verification**: Ensure `make down` sends SIGTERM properly
2. **Integration test**: Full up/status/down cycle test with actual make targets
3. **Log file creation**: Daemon should write to `.automation/logs/daemon.log`
