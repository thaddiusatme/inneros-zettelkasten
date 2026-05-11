# Issue #92 Test Suite Speed — TDD Iteration 1 Lessons Learned

**Date**: 2026-02-14
**Branch**: `fix/test-suite-speed-issue-92`
**Commit**: `4bbab63`
**Duration**: ~30 minutes
**Status**: ✅ PRODUCTION READY — P0 + P1 complete

## Problem Statement

2,124 unit tests + 255 integration tests with a 300s global timeout causing stalls and indefinite hangs when Ollama is unavailable. This blocked practical development velocity.

## TDD Cycle Summary

### RED Phase (13 failing → 1 passing)
- 14 tests covering: tiered timeouts (2), network guard (4), addopts exclusion (2), Makefile targets (6)
- All failed as expected except 1 pre-existing pass on `collect_only` subprocess test

### GREEN Phase (14/14 passing)
- `development/pytest.ini`: Added `timeout = 10` default
- `conftest.py`: Added tiered timeout auto-apply (integration=60s, smoke=300s) + `ollama_available` fixture with 2s socket timeout
- Integration tests: Added `@pytest.mark.network` to both Ollama-dependent files
- `addopts`: Updated to `-m "not wip and not network"`
- `development/Makefile`: Created with 5 test targets

### REFACTOR Phase
- Scoped `test-fast` Makefile target to `tests/unit` to avoid pre-existing collection errors in root-level test files
- Updated `pytest.ini` workflow comments to document new commands
- Verified wip marker auto-application: 478 tests correctly deselected

## Key Measurements

| Metric | Before | After |
|--------|--------|-------|
| Default timeout | 300s (inherited from root) | 10s (unit), 60s (integration), 300s (smoke) |
| Ollama test hang risk | Indefinite | Eliminated (excluded + 2s socket guard) |
| Tests deselected by default | ~467 (wip only) | 478 (wip + network) |
| Makefile targets | None | 5 (`test-fast`, `test-unit`, `test-integration`, `test-all`, `test-network`) |
| Unit suite wall time | >5min with hangs | ~3m25s (no hangs) |

## Technical Insights

1. **`pytest-timeout` was already installed** in `.venv` (v2.4.0) but never configured in `development/pytest.ini`. The root `pytest.ini` had `timeout = 300` which was the only active timeout — way too generous for unit tests.

2. **Tiered timeouts via `conftest.py` auto-markers** are more maintainable than per-file `@pytest.mark.timeout()` decorators. The `pytest_collection_modifyitems` hook already handled directory-based marker assignment, so adding timeout tiers there was a natural extension.

3. **Socket-based Ollama check** (`sock.settimeout(2)`) is faster and more reliable than HTTP health checks for a skip fixture. No dependency on `requests` and guaranteed 2s max wait.

4. **Pre-existing failures**: 50-53 unit test failures exist across the suite (mostly `test_daemon_cli_enhanced.py` and `test_workflow_manager.py`). These are not regressions — they predate this work. Separating them into their own issue was the right call.

5. **Makefile `test-fast` <30s target not achievable** without `pytest-xdist` parallel execution. With 1379+ passing unit tests, sequential execution takes ~3.5min. This is a P2 item.

6. **`black` pre-commit hook** caught formatting issues in the test file. Always run formatters before committing.

## Files Changed (6 files, ~250 insertions)

- `development/pytest.ini` — timeout + addopts + comments
- `development/tests/conftest.py` — tiered timeouts + `ollama_available` fixture
- `development/tests/integration/test_ai_summarizer_integration.py` — `@pytest.mark.network`
- `development/tests/integration/test_ai_connections_integration.py` — `@pytest.mark.network`
- `development/tests/unit/devex/test_test_suite_speed_issue_92.py` — 14 regression tests
- `development/Makefile` — 5 test targets with help

## P2 Deferred Items

1. **Parallel execution** (`pytest-xdist`) to hit <30s `test-fast` target
2. **Consolidate TDD iteration tests** — reduce 478 deselected WIP tests
3. **CI integration** with tiered test stages (fast gate → full suite)
4. **Fix pre-existing test failures** (50+ across daemon CLI and workflow manager)
