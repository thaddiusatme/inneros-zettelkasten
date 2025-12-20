# Issue #39 P1 + Issue #48: CLI Logging Context + Pre-commit Fix — Lessons Learned

**Date**: 2025-12-19  
**Branch**: `feat/issue-39-p1-cli-logging-precommit-fix`  
**Commit**: `cd7a2b4`  
**Duration**: ~45 minutes  
**Status**: ✅ **COMPLETE** — TDD iteration successful

---

## 🎯 Objectives Achieved

### Issue #48: Pre-commit Pytest Hook Fix
- **Root Cause**: Hook used `-m "ci and not wip and not slow"` but `ci` marker was never defined in pytest.ini
- **Result**: 0 tests selected, forcing developers to use `--no-verify`
- **Fix**: Changed to `-m "not slow"` — now selects **1892 tests**

### Issue #39 P1: CLI Logging Standardization
- Created shared `cli_logging.py` module with:
  - `configure_cli_logging()`: Configures logger to write to **stderr** (not stdout)
  - `log_cli_context()`: Logs consistent `key=value` startup context
- Wired into 3 core CLIs: `backup_cli.py`, `screenshot_cli.py`, `core_workflow_cli.py`

---

## 📊 TDD Metrics

| Phase | Tests | Result |
|-------|-------|--------|
| RED | 10 tests written | 7 failed (expected), 3 passed (existing behavior) |
| GREEN | Implementation | 10/10 passing |
| REFACTOR | Wire into CLIs | 26/26 passing (including subprocess integration) |

---

## 🔑 Key Technical Insights

### 1. Pre-commit Marker Must Exist
```yaml
# WRONG: 'ci' marker undefined = 0 tests selected
-m "ci and not wip and not slow"

# RIGHT: 'slow' is defined in pytest.ini
-m "not slow"
```

### 2. Ruff Args Gotcha
```yaml
# WRONG: 'check' interpreted as filename
args: ["check", "development/src", ...]
# Error: check:1:1: E902 No such file or directory

# RIGHT: Use files pattern, ruff hook runs check by default
args: ["--select", "E,F,W", ...]
files: ^development/(src|tests)/
```

### 3. CLI Logging to stderr for JSON Purity
```python
# Configure logger to write to stderr (not stdout)
handler = logging.StreamHandler(sys.stderr)  # Critical!

# This prevents log lines from contaminating JSON output:
# BAD: INFO - backup_cli - Starting...{"success": true, ...}
# GOOD: stdout is pure JSON, logs go to stderr
```

### 4. Consistent Context Format
```python
log_cli_context(
    logger=logger,
    cli_name="backup_cli",
    subcommand="backup",
    vault_path=self.vault_path,
    dry_run=dry_run,
    output_format=output_format,
)
# Output: cli=backup_cli subcommand=backup vault=/path dry_run=True format=json
```

---

## 🚧 Pre-existing Issues Discovered (Out of Scope)

1. **Failing test**: `test_read_last_activity_timestamp` — returns None unexpectedly
2. **Black formatting**: 6+ unrelated files need reformatting
3. **Unused variable warnings**: Minor lint issues in existing code

These are separate work items and were not addressed in this iteration.

---

## 📁 Files Changed

| File | Change |
|------|--------|
| `.pre-commit-config.yaml` | Fixed pytest marker, ruff config |
| `development/src/cli/cli_logging.py` | **NEW** — shared logging helper |
| `development/src/cli/backup_cli.py` | Wired cli_logging |
| `development/src/cli/screenshot_cli.py` | Wired cli_logging |
| `development/src/cli/core_workflow_cli.py` | Wired cli_logging |
| `development/tests/unit/cli/test_cli_logging_context.py` | **NEW** — 10 unit tests |
| `development/tests/unit/cli/test_dashboard_daemon_integration.py` | Marked slow test |

---

## 🎯 Next Steps

1. **Wire remaining CLIs**: `fleeting_cli.py`, `weekly_review_cli.py` could use `cli_logging`
2. **Fix pre-existing test failure**: `test_read_last_activity_timestamp`
3. **Run black formatting**: Address the 6 unrelated files
4. **Consider adding `wip` marker**: For work-in-progress tests that shouldn't run in pre-commit

---

## 💡 Pattern: TDD for DevOps/Config Changes

This iteration proved TDD works well for infrastructure changes:

1. **Write tests first** that verify desired behavior (marker selects tests, logs don't leak to stdout)
2. **Minimal implementation** to make tests pass
3. **Refactor** to integrate with existing code
4. **Commit** documents the "why" for future maintainers

The subprocess integration tests (`test_cli_json_output_contract_subprocess.py`) were invaluable for catching real CLI invocation issues.
