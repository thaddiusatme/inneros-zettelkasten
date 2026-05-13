# System Observability Integration - Project Manifest

**Created**: 2025-10-15  
**Priority**: P0 (Critical for usability)  
**Status**: Planning  
**Type**: Integration & Refactoring Project

---

## 🎯 Problem Statement

**You built sophisticated automation but have ZERO visibility into it.**

### User Pain Point
> "I don't have much visibility on what's running or not? When it ran? If it's currently running too."

### What We Found
- ✅ **3 dashboards built** (workflow, terminal, daemon)
- ✅ **Health monitoring system** complete
- ✅ **114 tests passing** for dashboard code
- ❌ **No unified entry point** to access any of it
- ❌ **Automation disabled** (cron jobs commented out)
- ❌ **No status command** to check system state
- ❌ **No documentation** on how to use dashboards

---

## 📦 Existing Assets to Integrate

### **Asset 1: Workflow Dashboard** ✅
- **File**: `development/src/cli/workflow_dashboard.py`
- **Features**: Interactive terminal UI with keyboard shortcuts
- **Shortcuts**: `[P]` process, `[W]` weekly, `[F]` fleeting, `[S]` status
- **Status**: Production ready (392 LOC, 21/21 tests)
- **Access**: `python3 development/demo_dashboard.py`

### **Asset 2: Terminal Dashboard** ✅
- **File**: `development/src/cli/terminal_dashboard.py`
- **Features**: Live daemon monitoring with health polling
- **Display**: Color-coded indicators (🟢/🔴), real-time updates
- **Status**: Production ready (136 LOC)
- **Access**: Unknown (needs investigation)

### **Asset 3: Automation Daemon** ✅
- **File**: `development/src/automation/daemon.py`
- **Features**: APScheduler, file watching, health checks
- **CLI**: `development/src/automation/daemon_cli.py`
- **Status**: Production ready (511 LOC)
- **Current State**: NOT RUNNING

### **Asset 4: Health System** ✅
- **File**: `development/src/automation/health.py`
- **Features**: Metrics collection, HTTP health endpoints
- **Status**: Production ready (145 LOC)
- **Integration**: Used by daemon

### **Asset 5: Cron Automation** ⚠️
- **File**: `.automation/cron/setup_automation.sh`
- **Features**: Screenshot import, inbox processing, weekly analysis
- **Status**: ALL DISABLED (see `#DISABLED#` markers in crontab)
- **Last Activity**: Oct 9, 13:39 (tests only, 6 days ago)

---

## 🎯 Project Objectives

### **P0: Unified Status Command** (2 hours)
Create single `inneros status` command showing:
- ✅ Daemon running/stopped
- ✅ Cron automation enabled/disabled
- ✅ Last activity timestamps
- ✅ Notes waiting for processing
- ✅ Quick actions available

### **P1: Dashboard Launcher** (1 hour)
Integrate existing dashboards into single CLI:
```bash
inneros dashboard          # Launch workflow dashboard
inneros dashboard --live   # Launch terminal dashboard
inneros dashboard --help   # Show available dashboards
```

### **P2: Daemon Management** (1 hour)
Make daemon easy to control:
```bash
inneros daemon start       # Start automation daemon
inneros daemon stop        # Stop daemon gracefully
inneros daemon status      # Check if daemon is running
inneros daemon logs        # Tail daemon logs
```

### **P3: Automation Controls** (2 hours)
Enable/disable automation easily:
```bash
inneros automation enable  # Enable cron jobs
inneros automation disable # Disable cron jobs
inneros automation status  # Show what's scheduled
inneros automation logs    # Show recent activity
```

---

## 📋 Implementation Phases

### **Phase 1: Status Command** (P0, 2 hours)

**Goal**: Know what's running with single command

**Tasks**:
1. Create `src/cli/status_cli.py` (new file)
   - Check daemon process running
   - Parse crontab for enabled jobs
   - Read last log entries
   - Count notes in Inbox/
   - Format beautiful status display

2. Integration with `workflow_demo.py`
   - Add `--status` flag
   - Use existing `core_workflow_cli.py status` data
   - Enhance with daemon/cron checks

3. Testing (RED → GREEN → REFACTOR)
   - Test daemon detection
   - Test cron parsing
   - Test log reading
   - Test display formatting

**Success Criteria**:
- ✅ Single command shows complete system state
- ✅ Clear indicators (🟢/🔴/⚠️)
- ✅ Actionable next steps shown
- ✅ <5 seconds execution time

**Example Output**:
```
📊 InnerOS System Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Automation Status
  ❌ Daemon: NOT RUNNING
  ❌ Cron: DISABLED (5 jobs configured)
  ⏰ Last Activity: 6 days ago (Oct 9, 13:39)

📝 Notes Status
  • Inbox: 12 notes waiting
  • Ready for promotion: 3 notes (≥0.7 quality)
  • Fleeting health: 8 stale notes (>30 days)

🔧 Quick Actions
  Start automation: inneros daemon start
  Manual process: inneros process-inbox
  View dashboard: inneros dashboard
  
📋 Details
  Logs: .automation/logs/
  Config: .automation/config/
  Dashboards: inneros dashboard --help
```

---

### **Phase 2: Dashboard Integration** (P1, 1 hour)

**Goal**: Easy access to existing dashboards

**Tasks**:
1. Create `src/cli/dashboard_launcher.py`
   - Wrapper for `workflow_dashboard.py`
   - Wrapper for `terminal_dashboard.py`
   - Flag-based selection

2. Add to `workflow_demo.py`
   - `--dashboard` launches workflow UI
   - `--dashboard-live` launches terminal UI
   - Help text explains both

3. Testing
   - Test dashboard detection
   - Test subprocess launching
   - Test error handling

**Success Criteria**:
- ✅ `inneros dashboard` works
- ✅ Both dashboards accessible
- ✅ Graceful Rich library check
- ✅ Help text clear

---

### **Phase 3: Daemon Management** (P1, 1 hour)

**Goal**: Start/stop/status daemon easily

**Tasks**:
1. Enhance `daemon_cli.py`
   - Add start/stop/status commands
   - Add logs command (tail -f)
   - PID file management

2. Integration with main CLI
   - `inneros daemon start`
   - `inneros daemon stop`
   - `inneros daemon status`

3. Testing
   - Test daemon lifecycle
   - Test PID file handling
   - Test logs tailing

**Success Criteria**:
- ✅ Daemon starts/stops reliably
- ✅ Status shows accurate state
- ✅ Logs command works
- ✅ Background process management

---

### **Phase 4: Automation Controls** (P2, 2 hours)

**Goal**: Enable/disable cron automation

**Tasks**:
1. Create `automation_manager.py`
   - Parse crontab
   - Enable/disable jobs (remove/add `#DISABLED#`)
   - Show schedule
   - Read automation logs

2. Add CLI commands
   - `inneros automation enable`
   - `inneros automation disable`
   - `inneros automation status`
   - `inneros automation logs`

3. Testing
   - Test crontab parsing
   - Test enable/disable
   - Test log reading

**Success Criteria**:
- ✅ Cron jobs toggleable
- ✅ Schedule displayed clearly
- ✅ Last run timestamps shown
- ✅ Logs accessible

---

## 🏗️ Architecture Decisions

### **Refactor Strategy: Integration Over Rewrite**
- ✅ **Reuse existing dashboards** (392 LOC workflow, 136 LOC terminal)
- ✅ **Reuse health system** (145 LOC)
- ✅ **Reuse daemon** (511 LOC)
- ✅ **Add thin CLI wrappers** (<200 LOC new code)

### **CLI Structure**
```
inneros
├── status              # P0: System overview
├── dashboard           # P1: Launch workflow dashboard
│   └── --live          #     Launch terminal dashboard
├── daemon              # P1: Daemon management
│   ├── start
│   ├── stop
│   ├── status
│   └── logs
└── automation          # P2: Cron management
    ├── enable
    ├── disable
    ├── status
    └── logs
```

### **File Organization**
```
development/src/cli/
├── status_cli.py          # NEW: P0 status command
├── dashboard_launcher.py  # NEW: P1 dashboard wrapper
├── daemon_manager.py      # NEW: P1 daemon controls
├── automation_manager.py  # NEW: P2 cron controls
├── workflow_dashboard.py  # EXISTING: Reuse as-is
└── terminal_dashboard.py  # EXISTING: Reuse as-is
```

---

## ✅ Success Metrics

### **User Experience**
- ✅ `inneros status` shows system state in <5 seconds
- ✅ Clear what's running vs not running
- ✅ Actionable next steps provided
- ✅ Easy access to dashboards

### **Technical**
- ✅ Reuse 100% of existing dashboard code
- ✅ Add <300 LOC new integration code
- ✅ Maintain ADR-001 compliance (<500 LOC per file)
- ✅ Zero breaking changes to existing systems
- ✅ Comprehensive test coverage

### **Adoption**
- ✅ User can check status without asking AI
- ✅ User knows when automation last ran
- ✅ User can start/stop automation confidently
- ✅ Documentation explains all commands

---

## 🚀 Getting Started

### **Current State Audit** (30 min)
1. ✅ Discovered 3 production-ready dashboards
2. ✅ Found daemon system (not running)
3. ✅ Found cron automation (disabled)
4. ⏳ Need to test terminal dashboard access
5. ⏳ Need to verify HTTP health endpoints

### **Next Immediate Action**
**Start Phase 1: Status Command**

1. Create `status_cli.py` with RED tests
2. Implement system state detection
3. Format beautiful output
4. Integration test with real vault

**Time Estimate**: 2 hours  
**Files to Create**: 1 new file (~200 LOC)  
**Files to Modify**: 1 (workflow_demo.py integration)  
**Tests to Write**: 8-10 tests

---

## 📊 Integration Checklist

### **Assets Audit**
- [x] Workflow Dashboard discovered
- [x] Terminal Dashboard discovered
- [x] Automation Daemon discovered
- [x] Health System discovered
- [x] Cron automation discovered
- [ ] Test terminal dashboard HTTP endpoint
- [ ] Test daemon startup
- [ ] Verify log file locations

### **Phase 1: Status Command**
- [ ] Create status_cli.py
- [ ] Implement daemon detection
- [ ] Implement cron parsing
- [ ] Implement log reading
- [ ] Format status display
- [ ] Write 8-10 tests
- [ ] Integration with workflow_demo.py

### **Phase 2: Dashboard Integration**
- [ ] Create dashboard_launcher.py
- [ ] Test workflow dashboard launch
- [ ] Test terminal dashboard launch
- [ ] Add CLI flags
- [ ] Write integration tests

### **Phase 3: Daemon Management**
- [ ] Enhance daemon_cli.py
- [ ] Add start/stop commands
- [ ] Add status command
- [ ] Add logs command
- [ ] Test lifecycle

### **Phase 4: Automation Controls**
- [ ] Create automation_manager.py
- [ ] Implement crontab parsing
- [ ] Implement enable/disable
- [ ] Add status display
- [ ] Add logs command

---

## 📚 Documentation Needs

### **User Guide** (Create alongside Phase 1)
- Daily workflow (Obsidian + automation)
- How to check system status
- How to start/stop automation
- How to access dashboards
- How to read logs

### **Developer Docs** (Update existing)
- Architecture diagram showing integration
- CLI command reference
- Dashboard capabilities
- Daemon configuration

---

**Ready to start**: Phase 1 Status Command (2 hours, P0 critical path)

**Expected Outcome**: User types `inneros status` and immediately knows:
- Is automation running?
- When did it last run?
- What notes need processing?
- What to do next?
