# TDD Iteration 1: Daemon PID File Locking - Lessons Learned

**Date**: 2025-12-27
**Duration**: ~45 minutes
**Branch**: `fix/daemon-process-management`
**Commit**: `a0f1a00`
**Issue**: #51 - Daemon reliability

---

## Problem Statement

Investigation revealed critical daemon reliability issues:
- **14 zombie daemon processes** running simultaneously
- `inneros-up` spawned duplicates without checking existing daemon
- Health check only validated one PID exists, ignored others
- Screenshot handler logs stopped Nov 30 (daemon not processing events)

## TDD Cycle Summary

### RED Phase (9 failing tests)
Created comprehensive test suite in `test_daemon_pid_lock.py`:

**Unit Tests (6)**:
1. `test_daemon_acquires_pid_lock_on_start` - PID file creation
2. `test_daemon_refuses_start_if_lock_held` - Duplicate prevention
3. `test_daemon_releases_lock_on_shutdown` - Clean shutdown
4. `test_stale_lock_allows_new_daemon` - Dead process cleanup
5. `test_lock_context_manager` - Safe usage pattern
6. `test_lock_is_process_running` - Process liveness check

**Integration Tests (3)**:
1. `test_daemon_start_creates_pid_file` - Daemon integration
2. `test_daemon_stop_removes_pid_file` - Cleanup on stop
3. `test_second_daemon_fails_to_start` - End-to-end duplicate prevention

### GREEN Phase (minimal implementation)
Created `src/automation/pid_lock.py` with `PIDLock` class:
- `fcntl.flock()` for exclusive file locking
- Stale lock detection via `os.kill(pid, 0)`
- Context manager protocol (`__enter__`/`__exit__`)
- Clean error messages with existing PID

Integrated into `AutomationDaemon`:
- Lock acquired in `start()` before scheduler initialization
- Lock released in `stop()` after scheduler shutdown
- Added `pid_file` config option to `DaemonConfig`

### REFACTOR Phase
Architecture was already clean - `PIDLock` as separate module with single responsibility. No additional refactoring needed.

## Key Technical Decisions

### 1. `fcntl.flock()` vs `filelock` library
**Decision**: Use standard library `fcntl.flock()`
**Rationale**: 
- No external dependency
- Sufficient for single-process daemon
- macOS/Linux compatible

### 2. Stale Lock Detection
**Decision**: Check if process is running via `os.kill(pid, 0)`
**Rationale**:
- Signal 0 doesn't kill, just checks existence
- Automatically clean up after crashes
- No manual intervention needed

### 3. PID Lock Placement in Daemon Lifecycle
**Decision**: Acquire lock FIRST in `start()`, before scheduler
**Rationale**:
- Fail fast if duplicate detected
- No partial state if lock fails
- Clean error message to user

## Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `src/automation/pid_lock.py` | 156 | New PIDLock class |
| `src/automation/daemon.py` | +20 | Lock integration |
| `src/automation/config.py` | +1 | pid_file config |
| `tests/unit/automation/test_daemon_pid_lock.py` | 255 | 9 comprehensive tests |

## Metrics

- **Tests**: 9 new, 14 total daemon tests, 0 regressions
- **Coverage**: PIDLock class fully covered
- **Performance**: Lock acquisition <1ms

## Acceptance Criteria Status

- [x] `make up` starts exactly ONE daemon process
- [x] `make up` (second call) raises error with existing PID
- [x] `make down` kills daemon and removes PID file
- [x] Stale locks from dead processes cleaned up automatically

## Cleanup Performed

- Killed 14 zombie daemon processes
- Archived 180 stale ALERT files to `.automation/review_queue/archive-20251227/`

## Next Iteration Readiness

**P0 Remaining**:
- [ ] Fix `inneros-up` script to use new PID locking
- [ ] Update `make status` to report PID lock state

**P1 Ready**:
- [ ] Smart link vault corpus loading fix
- [ ] Smart link review CLI

## Key Insights

1. **TDD caught integration gap**: Unit tests passed but integration tests failed - revealed daemon wasn't actually using PIDLock
2. **Pre-commit hooks work**: Black formatting caught before commit
3. **Single responsibility pays off**: PIDLock as separate module made testing trivial
4. **Stale lock handling is critical**: Without it, daemon would be stuck after crashes
