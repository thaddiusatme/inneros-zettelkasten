# Next Session: System Observability Phase 2.2 - Dashboard-Daemon Integration

## The Prompt

Let's create a new branch for the next feature: **System Observability Phase 2.2 - Dashboard-Daemon Integration**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

**Context:** Just completed Phase 2.1: Daemon Management Enhancement (60 minutes, 12/12 tests passing, ADR-001 compliant). Successfully delivered `inneros daemon start/stop/status/logs` commands with PID management and graceful shutdown. Now integrating daemon status detection into dashboard launcher for unified system control.

**Assets Available:**
- Daemon Management CLI (94 LOC main, 158 LOC utils, production ready)
- Dashboard Launcher from Phase 2 (185 LOC main, 218 LOC utils, 14/14 tests)
- Status CLI from Phase 1 (209 LOC, DaemonDetector utility)
- Enhanced status checking with uptime calculation
- Proven TDD patterns (RED→GREEN→REFACTOR, 60min cycle achieved)

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `architectural-constraints.md` (critical path: Complete dashboard-daemon integration for intelligent system control).

### Current Status

**Completed:**
- ✅ Phase 1: System Status CLI (8/8 tests passing)
- ✅ Phase 2: Dashboard Launcher (14/14 tests passing)
- ✅ Phase 2.1: Daemon Management Enhancement (12/12 tests passing)
- Branch: `feat/system-observability-phase-2.1-daemon-management` merged to main

**In progress:**
- Phase 2.2: Dashboard-Daemon Integration (planning stage)
- Location: `development/src/cli/dashboard_cli.py` (needs daemon status detection)
- Location: `development/src/cli/dashboard_utils.py` (needs integration utilities)

**Lessons from last iteration:**
- TDD discipline enables 33% faster development (60min vs 90min previous phases)
- Utility extraction maintains ADR-001 compliance (<200 LOC)
- PID file management requires robust process existence checking
- Dictionary return patterns provide consistent interfaces
- Graceful error handling creates better UX than exceptions
- Integration-first approach delivers immediate value

### P0 — Critical System Control (Dashboard-Daemon Integration)

**Extend Dashboard CLI** (`development/src/cli/dashboard_cli.py`):
- Auto-detect daemon status before launching live dashboard
- Display daemon status in dashboard header/footer
- Show helpful messages if daemon not running
- Provide quick-start suggestion (`inneros daemon start`)

**Implementation Details:**
- Reuse `EnhancedDaemonStatus` from Phase 2.1 `daemon_cli_utils.py`
- Add status check to `DashboardLauncher.launch_live()` method
- Create `DashboardDaemonIntegration` utility class
- Display daemon PID, uptime in dashboard UI
- Color-coded status indicators (green=running, red=stopped)

**Error Handling:**
- Graceful degradation when daemon not running
- Clear instructions for starting daemon
- Option to continue without daemon (with warnings)
- Exit code handling for automation scripts

**Acceptance Criteria:**
- ✅ Dashboard auto-checks daemon status on launch
- ✅ Status displayed in dashboard UI with color coding
- ✅ Helpful error messages if daemon not running
- ✅ Main file remains <200 LOC (ADR-001 compliant)
- ✅ 8-10 comprehensive tests designed and passing
- ✅ Zero breaking changes to existing commands
- ✅ Complete TDD cycle in 60-75 minutes

### P1 — Enhanced Observability (Post-Integration)

**Enhanced Logging Display:**
- Log filtering by level (`--level INFO|WARNING|ERROR`)
- Component-based filtering (`--component daemon|automation`)
- Tail mode with auto-refresh (`--follow` flag)
- Structured log parsing (timestamp, level, component, message)

**Health Monitoring Integration:**
- Daemon health check endpoint
- Resource usage display (CPU, memory)
- Process tree visualization
- Alert if daemon crashed/restarted

**Dashboard Enhancements:**
- Real-time daemon status updates in live mode
- Process metrics in dashboard cards
- Log streaming in dashboard panel
- Quick actions: start/stop/restart from dashboard

**Acceptance Criteria:**
- ✅ Log filtering works with multiple criteria
- ✅ Health metrics displayed accurately
- ✅ Dashboard shows real-time updates
- ✅ Integration tests validate all features

### P2 — Future System Observability (Backlog)

**Automation Controls:**
- `inneros automation enable/disable` - Toggle automation jobs
- `inneros automation schedule` - View/modify cron schedule
- `inneros automation status` - Show job execution history

**Notifications System:**
- macOS notifications for processing completion
- Desktop notifications for errors/warnings
- Configurable notification preferences

**Remote Monitoring:**
- Optional web dashboard for remote access
- API endpoints for external monitoring tools
- Prometheus/Grafana integration support

### Task Tracker

- ✅ Phase 1: System Status CLI (COMPLETED)
- ✅ Phase 2: Dashboard Launcher (COMPLETED)
- ✅ Phase 2.1: Daemon Management Enhancement (COMPLETED)
- **[In progress]** Phase 2.2: Dashboard-Daemon Integration
- [Pending] P1: Enhanced Logging Features
- [Pending] P1: Health Monitoring Integration
- [Pending] P1: Real-time Dashboard Updates
- [Pending] P2: Automation Controls
- [Pending] P2: Notifications System

### TDD Cycle Plan

**Red Phase (20-25 minutes):**

Create `development/tests/unit/cli/test_dashboard_daemon_integration.py`:
- Write 8-10 failing tests:
  - `test_dashboard_detects_daemon_running`
  - `test_dashboard_detects_daemon_stopped`
  - `test_dashboard_displays_daemon_status`
  - `test_dashboard_shows_uptime_in_ui`
  - `test_dashboard_handles_missing_pid_file`
  - `test_dashboard_provides_start_instructions`
  - `test_dashboard_color_codes_status`
  - `test_integration_orchestrator_status_check`

Create stub implementations in `dashboard_cli.py` and `dashboard_utils.py`
Verify all stubs raise `NotImplementedError`

**Green Phase (25-30 minutes):**

Implement core classes:
- `DashboardDaemonIntegration` - Status checking and UI display
- `DaemonStatusFormatter` - Color-coded status messages
- `DashboardHealthMonitor` - Combined system health view
- Extend `DashboardLauncher` with status check on launch
- Add daemon status to dashboard header/footer
- Implement graceful error handling

Verify pragmatic tests passing (aim for 8/10+ passing)

**Refactor Phase (20-25 minutes):**

Extract utilities to `dashboard_daemon_utils.py` if needed
Ensure main file <200 LOC (ADR-001 compliance)
Apply facade pattern for clean architecture
Optimize status checking performance
Add performance logging
Run verification: `python3 tests/verify_refactor_phase.py`

### Next Action (for this session)

**Option 1 - New branch (recommended):**
- Create branch: `feat/system-observability-phase-2.2-dashboard-daemon-integration`
- Start RED phase for dashboard-daemon integration
- Create test file: `development/tests/unit/cli/test_dashboard_daemon_integration.py`
- Write 8-10 failing tests for status detection and UI display

**Files to modify:**
- `development/src/cli/dashboard_cli.py` (add daemon status detection)
- `development/src/cli/dashboard_utils.py` (add integration utilities)
- `development/tests/unit/cli/test_dashboard_daemon_integration.py` (new test suite)

**Files to reference:**
- `development/src/cli/daemon_cli_utils.py` (reuse EnhancedDaemonStatus)
- `development/src/cli/status_utils.py` (existing DaemonDetector pattern)

**Expected imports:**
```python
from development.src.cli.daemon_cli_utils import EnhancedDaemonStatus
from development.src.cli.dashboard_utils import DashboardLauncher
```

Would you like me to implement the RED phase now (8-10 failing tests for dashboard-daemon integration)?
