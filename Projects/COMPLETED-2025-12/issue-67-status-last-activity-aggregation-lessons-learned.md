# Issue #67: Status Last-Activity Aggregation - Lessons Learned

**Date**: 2025-12-19  
**Duration**: ~15 minutes  
**Branch**: `fix/issue-67-status-last-activity-aggregation`  
**Commit**: `d945bf7`  
**Status**: ✅ **COMPLETE** - TDD iteration successful

---

## 🎯 Problem Statement

`inneros-status` last-activity was inaccurate because `LogTimestampReader` only scanned `.automation/logs/*.log` (main logs directory) and ignored handler-specific subdirectories like:
- `.automation/logs/handlers/screenshot/*.log`
- `.automation/logs/handlers/smart_link/*.log`
- `.automation/logs/handlers/health_monitor/*.log`

This meant the CLI reported stale timestamps when handler activity was more recent than daemon activity.

---

## 🏆 TDD Cycle Summary

### RED Phase (3 min)
- **Test**: `test_aggregates_handler_logs_for_last_activity`
- **Assertion**: When handler logs exist with newer mtimes than main logs, `get_last_activity()` returns the handler timestamp
- **Key design**: Used temp directories with explicit `os.utime()` for deterministic, non-flaky tests

### GREEN Phase (5 min)
- **Implementation**: Modified `LogTimestampReader.get_last_activity()` to:
  1. Collect logs from main directory: `logs_dir.glob("*.log")`
  2. Collect logs from handlers: `handlers_dir.rglob("*.log")`
  3. Return `max(mtime)` across all sources
- **New method**: `iter_activity_log_paths(logs_dir) -> List[Path]`

### REFACTOR Phase (5 min)
- **Bug found**: Existing test `test_read_last_activity_timestamp` had incorrect path handling
  - Passed `logs_dir.parent` (`.automation`) instead of vault root (`tmpdir`)
  - This caused path computation: `tmpdir/.automation/.automation/logs` (doesn't exist)
- **Fix**: Changed to pass `tmpdir` directly as vault root

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Tests passing | 9/9 (100%) |
| Pre-commit | ✅ pytest-unit-fast passed |
| Lines changed | ~60 (impl) + ~55 (test) |
| Execution time | 0.11s for full suite |

---

## 💡 Key Insights

### 1. Path Handling in Tests Requires Care
The existing test was working by accident due to path computation bugs canceling out. When refactoring, always verify test paths are semantically correct:
```python
# Wrong: logs_dir.parent = .automation (not vault root)
reader.get_last_activity(str(logs_dir.parent))

# Correct: tmpdir = vault root
reader.get_last_activity(tmpdir)
```

### 2. Recursive Glob for Handler Discovery
Using `rglob("*.log")` on the handlers directory provides future-proof discovery of any handler subdirectory structure without hardcoding paths:
```python
handlers_dir = logs_dir / "handlers"
if handlers_dir.exists():
    log_files.extend(handlers_dir.rglob("*.log"))
```

### 3. Deterministic Timestamp Tests
Explicit `os.utime()` calls ensure tests don't depend on filesystem timing:
```python
os.utime(log_file, (mtime, mtime))  # Set both atime and mtime
```

### 4. TDD Catches Pre-existing Bugs
The GREEN phase revealed the existing test's path bug that was previously undetected. This validates TDD's value for improving code quality beyond just new features.

---

## 📁 Files Changed

| File | Changes |
|------|---------|
| `development/src/cli/status_utils.py` | Added `iter_activity_log_paths()`, updated `get_last_activity()` |
| `development/tests/unit/cli/test_status_cli.py` | Added aggregation test, fixed path bug in existing test |

---

## 🚀 Next Steps

1. **P1**: Add graceful handling for missing directories/permission errors
2. **P2**: Consider adding observability smoke test with real `.automation/logs/` layout
3. **Future**: Evaluate if handler log locations should be configurable via registry

---

## ✅ Acceptance Criteria Met

- [x] `pytest development/tests/unit/cli/test_status_cli.py -q` passes (9/9)
- [x] Handler logs included in last-activity calculation
- [x] Missing directories handled gracefully (returns None)
- [x] No network calls, no background threads
- [x] Deterministic in unit tests
