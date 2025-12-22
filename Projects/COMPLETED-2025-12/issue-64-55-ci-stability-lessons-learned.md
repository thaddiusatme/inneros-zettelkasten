# CI Stability Fix - Lessons Learned

**Issue**: #64 (CI unit suite failing on main), #55 (test suite stalling)  
**Commit**: `e9e2ece`  
**Date**: 2025-12-09

## Problem Summary

The `make cov` command (used by Nightly Coverage CI) was failing with 43+ test failures due to:
1. **Demo script collection**: Pytest collected `*test*.py` files from `development/demos/` as tests
2. **WIP test execution**: TDD RED-phase tests ran without WIP marker filtering
3. **Template test regression**: Trigger template missing expected `tp.file.move()` call

## Root Causes

1. **Makefile gap**: `make cov` didn't specify test path or marker filters like `make unit` does
2. **Naming convention**: Demo scripts named `*_test.py` or `test_*.py` triggered pytest collection
3. **Missing auto-detection**: conftest.py didn't auto-mark TDD iteration files as WIP

## Solution Applied

| Change | File | Purpose |
|--------|------|---------|
| Fix test path + filters | `Makefile` | Target `development/tests/unit`, exclude demos, filter WIP |
| TDD auto-marking | `conftest.py` | Regex `_tdd_\d+` → auto-add `@pytest.mark.wip` |
| Explicit WIP markers | 10 test files | Module-level `pytestmark = pytest.mark.wip` |
| Rename demos | 2 files | `*_test.py` → `*_demo.py` |
| Skip trigger templates | `test_templates_auto_inbox.py` | Trigger templates don't need file relocation |

## Key Lessons

### 1. CI Commands Must Match
```makefile
# BEFORE: make cov had no path/filters
cov: pytest --cov=development/src

# AFTER: matches make unit's targeting
cov: pytest --cov=... -m "not wip" --ignore=development/demos development/tests/unit
```

### 2. Demo Files Need Non-Test Names
Files with `test` in the name get collected by pytest. Use `*_demo.py` or `*_example.py` for non-test scripts.

### 3. Auto-Mark TDD Files
The regex `_tdd_\d+` catches iteration-numbered TDD files (e.g., `test_foo_tdd_5.py`) and auto-marks them as WIP.

### 4. Run Both CI Commands Locally
```bash
make unit  # Fast CI check (155 tests, ~17s)
make cov   # Nightly coverage (1414 tests, ~7min)
```

## Metrics

| Before | After |
|--------|-------|
| 43 failures | 0 failures |
| Collection errors | Clean collection |
| ~10min with errors | ~7min clean run |

## Future Prevention

1. **Pre-commit validation**: Consider adding `make cov` to pre-push hooks for coverage changes
2. **Demo directory exclusion**: Already in Makefile; maintain when adding new demo locations
3. **TDD naming convention**: Use `_tdd_N` suffix for iteration tests (auto-marked as WIP)
