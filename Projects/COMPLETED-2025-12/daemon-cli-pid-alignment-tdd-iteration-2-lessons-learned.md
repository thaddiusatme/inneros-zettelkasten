# TDD Iteration 2: CLI PID File Alignment - Lessons Learned

**Date**: 2025-12-27
**Duration**: ~20 minutes
**Branch**: `fix/daemon-process-management`
**Commit**: `1645c5c`
**Issue**: #51 - Daemon reliability

---

## Problem Statement

Investigation revealed CLI and daemon used **different PID files**:
- **CLI**: `~/.inneros/daemon.pid`
- **Daemon**: `.automation/daemon.pid`

This mismatch caused zombie processes because:
1. `make up` couldn't detect running daemon (wrong PID file)
2. Multiple calls spawned new daemons without stopping existing ones
3. `make status` reported "not running" even when daemon was active

## TDD Cycle Summary

### RED Phase (1 failing test initially)
Created test requiring `.automation` in PID file path:

```python
def test_daemon_starter_uses_automation_pid_file(self):
    assert ".automation" in str(starter.pid_file)
    assert daemon_config.pid_file in str(starter.pid_file)
```

Initial test was too permissive (any "daemon.pid" passed). Tightened to require `.automation/`.

### GREEN Phase (3-line change)
Updated default PID file path in three classes:

```python
# Before
self.pid_file = pid_file_path or (Path.home() / ".inneros" / "daemon.pid")

# After
self.pid_file = pid_file_path or (Path.cwd() / ".automation" / "daemon.pid")
```

### REFACTOR Phase
Minimal - the change was already clean and focused.

## Key Technical Decisions

### 1. Path.cwd() vs Absolute Path
**Decision**: Use `Path.cwd() / ".automation" / "daemon.pid"`
**Rationale**:
- Matches daemon's relative path approach
- Works when CLI is run from repo root (standard usage)
- Consistent with `DaemonConfig.pid_file` default

### 2. Single Source of Truth
**Decision**: Align CLI with daemon's config, not vice versa
**Rationale**:
- Daemon has the authoritative PID lock implementation
- CLI is consumer of daemon's state
- Less risk of breaking daemon's internal locking

## Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `src/cli/daemon_cli_utils.py` | 3 | Updated 3 default PID paths |
| `tests/unit/cli/test_daemon_cli_pid_integration.py` | 200 | 7 new integration tests |

## Metrics

- **Tests**: 7 new CLI tests, 16 total daemon tests
- **Time**: ~20 minutes (fast iteration building on Iteration 1)
- **Changes**: 3 lines of production code

## Root Cause Analysis

The original CLI used `~/.inneros/daemon.pid` because:
1. It was designed before the daemon module existed
2. User home directory seemed "safer" for PID files
3. No coordination with daemon's internal PID management

The daemon used `.automation/daemon.pid` because:
1. Keeps all automation state in `.automation/`
2. Relative to repo root for portability
3. Consistent with other automation files

**Lesson**: When adding process management, coordinate PID file locations from the start.

## Key Insights

1. **Test specificity matters**: Initial test passed with wrong behavior because assertion was too loose
2. **Integration gaps hide in plain sight**: CLI and daemon worked individually but failed together
3. **3-line fixes can solve big problems**: Root cause was simple path mismatch
4. **TDD caught coordination issues**: Without tests, this mismatch would persist

## Sprint Progress

### Completed (P0)
- [x] Kill 14 zombie processes
- [x] Archive 180 stale ALERT files
- [x] Add PIDLock class to daemon module (Iteration 1)
- [x] Align CLI PID file with daemon (Iteration 2)

### Remaining (P0)
- [ ] Test `make up` / `make down` / `make status` end-to-end

### Ready (P1)
- [ ] Smart link vault corpus loading fix
- [ ] Smart link review CLI
