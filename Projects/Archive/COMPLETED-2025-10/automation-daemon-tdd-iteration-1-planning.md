# Automation Daemon TDD Iteration 1 - Planning Document

**Date**: 2025-10-07  
**Branch**: TBD (will create during RED phase)  
**Status**: 📋 PLANNING - Comprehensive architecture and test design  
**Reference**: `.windsurf/rules/automation-monitoring-requirements.md` (Phase 3 & 4 mandatory requirements)

---

## 🎯 Strategic Context

**Transformation Goal**: InnerOS from manual CLI-driven workflows → 24/7 automated knowledge processing platform

**Current State** (2025-10-07):
- ✅ 8 production systems operational (66+ tests passing)
- ✅ Zero technical debt achieved (27 days ahead of schedule)
- ✅ YouTube CLI integration complete (13/19 tests passing)
- ✅ Manual workflows proven and reliable

**Target State** (TDD Iteration 1):
- 🎯 Background daemon service running 24/7
- 🎯 APScheduler integration for cron-based automation
- 🎯 Health check endpoint for monitoring
- 🎯 Graceful start/stop with <1% crash rate
- 🎯 Foundation for Phase 4 monitoring integration

---

## 📐 Architecture Design (Following ADR-001)

### **Core Principles**:
- **No God Classes**: Max 500 LOC per class
- **Domain Separation**: Scheduler / Health / Config / Lifecycle
- **Adapter Pattern**: Clean integration with existing WorkflowManager
- **Single Responsibility**: Each class has ONE clear purpose

### **Class Structure** (<500 LOC Each):

#### **1. AutomationDaemon** (Main Orchestrator)
**Responsibility**: Daemon lifecycle management  
**Size Target**: ~300 LOC  
**Key Methods**:
```python
def start() -> None:
    """Start daemon with scheduler initialization"""
    
def stop() -> None:
    """Graceful shutdown with job cleanup"""
    
def restart() -> None:
    """Atomic restart without losing state"""
    
def status() -> DaemonStatus:
    """Current operational status"""
    
def is_healthy() -> bool:
    """Health check for monitoring"""
```

#### **2. SchedulerManager** (APScheduler Integration)
**Responsibility**: Job scheduling and execution  
**Size Target**: ~250 LOC  
**Key Methods**:
```python
def add_job(job_id: str, func: Callable, schedule: str) -> None:
    """Add cron-scheduled job"""
    
def remove_job(job_id: str) -> None:
    """Remove scheduled job"""
    
def list_jobs() -> List[JobInfo]:
    """Get all scheduled jobs"""
    
def pause_job(job_id: str) -> None:
    """Temporarily pause job"""
    
def resume_job(job_id: str) -> None:
    """Resume paused job"""
```

#### **3. HealthCheckManager** (Monitoring)
**Responsibility**: Health metrics and status reporting  
**Size Target**: ~200 LOC  
**Key Methods**:
```python
def get_health_status() -> HealthReport:
    """Comprehensive health check"""
    
def get_metrics() -> Dict[str, Any]:
    """Performance and operational metrics"""
    
def record_job_execution(job_id: str, success: bool, duration: float) -> None:
    """Track job execution history"""
```

#### **4. ConfigurationLoader** (Settings Management)
**Responsibility**: Config file loading and validation  
**Size Target**: ~150 LOC  
**Key Methods**:
```python
def load_config(path: Path) -> DaemonConfig:
    """Load and validate YAML/JSON config"""
    
def validate_config(config: DaemonConfig) -> List[str]:
    """Return validation errors"""
    
def get_default_config() -> DaemonConfig:
    """Return safe defaults"""
```

#### **5. JobRegistry** (Job Catalog)
**Responsibility**: Track registered jobs and their state  
**Size Target**: ~150 LOC  
**Key Methods**:
```python
def register_job(job: JobDefinition) -> None:
    """Add job to registry"""
    
def get_job(job_id: str) -> Optional[JobDefinition]:
    """Retrieve job by ID"""
    
def get_all_jobs() -> List[JobDefinition]:
    """Get all registered jobs"""
```

**Total LOC**: ~1,050 lines across 5 classes (all <500 LOC each)

---

## 🔴 RED Phase: 15 Comprehensive Failing Tests

### **Test File**: `development/tests/unit/test_automation_daemon.py`

### **P0.1: Daemon Lifecycle Tests (5 tests)**

```python
def test_daemon_starts_successfully():
    """Daemon initializes APScheduler and enters running state"""
    daemon = AutomationDaemon()
    daemon.start()
    assert daemon.status().state == DaemonState.RUNNING
    assert daemon.status().scheduler_active is True
    daemon.stop()

def test_daemon_stops_gracefully():
    """Daemon shuts down cleanly, finishing active jobs"""
    daemon = AutomationDaemon()
    daemon.start()
    daemon.stop()
    assert daemon.status().state == DaemonState.STOPPED
    assert daemon.status().active_jobs == 0

def test_daemon_restart_preserves_jobs():
    """Restart doesn't lose scheduled jobs"""
    daemon = AutomationDaemon()
    daemon.start()
    daemon.scheduler.add_job("test-job", lambda: None, "0 8 * * *")
    
    daemon.restart()
    
    jobs = daemon.scheduler.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "test-job"
    daemon.stop()

def test_daemon_status_reports_correctly():
    """Status reflects actual daemon state"""
    daemon = AutomationDaemon()
    
    # Initial state
    assert daemon.status().state == DaemonState.STOPPED
    
    # Running state
    daemon.start()
    assert daemon.status().state == DaemonState.RUNNING
    assert daemon.status().uptime_seconds >= 0
    
    daemon.stop()
    assert daemon.status().state == DaemonState.STOPPED

def test_daemon_handles_start_when_already_running():
    """Starting already-running daemon raises clear error"""
    daemon = AutomationDaemon()
    daemon.start()
    
    with pytest.raises(DaemonError, match="already running"):
        daemon.start()
    
    daemon.stop()
```

### **P0.2: Scheduler Integration Tests (5 tests)**

```python
def test_add_job_creates_scheduled_task():
    """Jobs are successfully registered with APScheduler"""
    daemon = AutomationDaemon()
    daemon.start()
    
    job_executed = False
    def test_func():
        nonlocal job_executed
        job_executed = True
    
    daemon.scheduler.add_job("test-job", test_func, "* * * * * */1")  # Every second
    
    # Wait for execution
    time.sleep(1.5)
    assert job_executed is True
    
    daemon.stop()

def test_remove_job_cancels_scheduled_task():
    """Removed jobs stop executing"""
    daemon = AutomationDaemon()
    daemon.start()
    
    execution_count = 0
    def test_func():
        nonlocal execution_count
        execution_count += 1
    
    daemon.scheduler.add_job("test-job", test_func, "* * * * * */1")
    time.sleep(1.5)
    
    daemon.scheduler.remove_job("test-job")
    initial_count = execution_count
    time.sleep(2)
    
    assert execution_count == initial_count  # No new executions
    daemon.stop()

def test_list_jobs_returns_all_scheduled():
    """Can retrieve all registered jobs"""
    daemon = AutomationDaemon()
    daemon.start()
    
    daemon.scheduler.add_job("job-1", lambda: None, "0 8 * * *")
    daemon.scheduler.add_job("job-2", lambda: None, "0 12 * * *")
    
    jobs = daemon.scheduler.list_jobs()
    assert len(jobs) == 2
    assert {job.id for job in jobs} == {"job-1", "job-2"}
    
    daemon.stop()

def test_job_execution_tracked():
    """Job executions are recorded with success/failure"""
    daemon = AutomationDaemon()
    daemon.start()
    
    def successful_job():
        return "success"
    
    daemon.scheduler.add_job("tracked-job", successful_job, "* * * * * */1")
    time.sleep(1.5)
    
    metrics = daemon.health.get_metrics()
    assert metrics["total_job_executions"] >= 1
    assert metrics["successful_executions"] >= 1
    
    daemon.stop()

def test_job_failure_handled_gracefully():
    """Failed jobs don't crash daemon"""
    daemon = AutomationDaemon()
    daemon.start()
    
    def failing_job():
        raise Exception("Intentional failure")
    
    daemon.scheduler.add_job("failing-job", failing_job, "* * * * * */1")
    time.sleep(1.5)
    
    # Daemon still running
    assert daemon.status().state == DaemonState.RUNNING
    
    metrics = daemon.health.get_metrics()
    assert metrics["failed_executions"] >= 1
    
    daemon.stop()
```

### **P0.3: Health Check Tests (3 tests)**

```python
def test_health_check_returns_healthy_when_running():
    """Healthy daemon returns positive health status"""
    daemon = AutomationDaemon()
    daemon.start()
    
    health = daemon.health.get_health_status()
    assert health.is_healthy is True
    assert health.status_code == 200
    assert "scheduler" in health.checks
    assert health.checks["scheduler"] is True
    
    daemon.stop()

def test_health_check_unhealthy_when_stopped():
    """Stopped daemon reports unhealthy"""
    daemon = AutomationDaemon()
    
    health = daemon.health.get_health_status()
    assert health.is_healthy is False
    assert health.status_code == 503

def test_metrics_track_uptime_and_jobs():
    """Metrics include uptime, job counts, execution stats"""
    daemon = AutomationDaemon()
    daemon.start()
    time.sleep(0.5)
    
    metrics = daemon.health.get_metrics()
    assert "uptime_seconds" in metrics
    assert metrics["uptime_seconds"] >= 0.5
    assert "total_jobs" in metrics
    assert "active_jobs" in metrics
    assert "total_job_executions" in metrics
    
    daemon.stop()
```

### **P0.4: Configuration Tests (2 tests)**

```python
def test_load_valid_config():
    """Valid YAML config loads successfully"""
    config_path = Path("/tmp/test_daemon_config.yml")
    config_path.write_text("""
daemon:
  check_interval: 60
  log_level: INFO
  
jobs:
  inbox_processing:
    schedule: "0 8 * * *"
    enabled: true
""")
    
    loader = ConfigurationLoader()
    config = loader.load_config(config_path)
    
    assert config.check_interval == 60
    assert config.log_level == "INFO"
    assert len(config.jobs) == 1
    assert config.jobs[0].name == "inbox_processing"

def test_invalid_config_raises_validation_error():
    """Malformed config returns clear validation errors"""
    config_path = Path("/tmp/invalid_config.yml")
    config_path.write_text("""
daemon:
  check_interval: -1  # Invalid: must be positive
  log_level: INVALID  # Invalid: not a valid level
""")
    
    loader = ConfigurationLoader()
    errors = loader.validate_config_file(config_path)
    
    assert len(errors) >= 2
    assert any("check_interval" in err for err in errors)
    assert any("log_level" in err for err in errors)
```

**Total Tests**: 15 comprehensive tests covering all core functionality

---

## 🟢 GREEN Phase: Minimal APScheduler Integration

### **Implementation Strategy**:
1. ✅ Install APScheduler: `pip install apscheduler`
2. ✅ Create `AutomationDaemon` class with BackgroundScheduler
3. ✅ Implement basic start/stop/status methods
4. ✅ Add simple job registration
5. ✅ Basic health check endpoint
6. ✅ Minimal config loading (YAML)

### **Target LOC**: ~400 lines total (GREEN phase minimal implementation)

### **Dependencies**:
```python
# requirements.txt additions
apscheduler==3.10.4  # Proven cron scheduling
pyyaml==6.0.1        # Config file parsing
```

---

## 🔄 REFACTOR Phase: Utility Extraction

### **Utility Classes to Extract** (Following proven TDD patterns):

1. **SchedulerUtils** (~100 LOC)
   - Cron expression validation
   - Schedule parsing helpers
   - Timezone handling

2. **HealthMetricsCollector** (~100 LOC)
   - Execution history tracking
   - Performance statistics
   - Error rate calculations

3. **ConfigValidator** (~80 LOC)
   - Schema validation
   - Type checking
   - Default value injection

4. **JobExecutionTracker** (~120 LOC)
   - Execution history storage
   - Success/failure logging
   - Performance metrics

**Total Utility LOC**: ~400 lines

---

## 📊 Success Criteria

### **P0 (Must Have)**:
- ✅ Daemon starts/stops cleanly (<1s)
- ✅ APScheduler operational with cron schedules
- ✅ 15/15 tests passing (100% success rate)
- ✅ Health check endpoint responding
- ✅ Config file loading from YAML
- ✅ Zero crashes during 5-minute stress test

### **P1 (Should Have)**:
- ✅ Graceful restart without job loss
- ✅ Job execution tracking and metrics
- ✅ Error recovery (failed jobs don't crash daemon)
- ✅ Comprehensive logging with levels

### **P2 (Nice to Have)**:
- Job prioritization
- Concurrent execution limits
- Web UI for status monitoring

---

## 🔗 Integration Points

### **Existing Systems**:
- `CoreWorkflowManager`: Inbox processing jobs
- `WorkflowManager (legacy)`: Backward compatibility adapter
- `.automation/scripts/`: Migration path for cron scripts
- Directory organization, image processing, screenshot workflows

### **Future Integrations** (Post-Iteration 1):
- Week 2: File watching with debouncing
- Week 3: Scheduled inbox processing automation
- Week 4: Evening screenshot auto-processing
- Phase 4: Metrics collection and alerting

---

## 📋 Implementation Checklist

### **Pre-RED**:
- [x] Review automation-monitoring-requirements.md
- [x] Review ADR-001 architectural constraints
- [x] Design class structure (<500 LOC each)
- [x] Define 15 comprehensive tests
- [ ] Create branch: `feat/automation-daemon-tdd-iteration-1`

### **RED Phase**:
- [ ] Create test file with 15 failing tests
- [ ] Verify all tests fail for expected reasons
- [ ] Document test expectations
- [ ] Commit: "RED phase: 15 comprehensive daemon tests"

### **GREEN Phase**:
- [ ] Install APScheduler dependency
- [ ] Implement AutomationDaemon class (~300 LOC)
- [ ] Implement SchedulerManager (~200 LOC)
- [ ] Implement minimal health checks
- [ ] Basic config loading
- [ ] Verify 15/15 tests passing
- [ ] Commit: "GREEN phase: Minimal APScheduler integration"

### **REFACTOR Phase**:
- [ ] Extract SchedulerUtils
- [ ] Extract HealthMetricsCollector
- [ ] Extract ConfigValidator
- [ ] Extract JobExecutionTracker
- [ ] Improve error messages and logging
- [ ] Verify 15/15 tests still passing
- [ ] Commit: "REFACTOR: Extracted 4 utility classes"

### **DOCUMENTATION**:
- [ ] Create `automation-daemon-tdd-iteration-1-lessons-learned.md`
- [ ] Update `FEATURE-STATUS.md`
- [ ] Update `next-iterations-roadmap-2025-10-07.md`

---

## ⚠️ Risk Mitigation

### **Known Risks**:
1. **APScheduler complexity**: Mitigate with minimal GREEN phase
2. **Process management**: Use BackgroundScheduler (in-process, simpler than daemon)
3. **Testing async jobs**: Use time.sleep() with generous timeouts
4. **Config file location**: Default to `.automation/config/daemon_config.yml`

### **Fallback Strategy**:
If APScheduler proves problematic, pivot to simpler `schedule` library for Iteration 1.

---

## 📅 Estimated Timeline

**Planning**: 1 hour (completed)  
**RED Phase**: 1-2 hours (15 tests)  
**GREEN Phase**: 3-4 hours (APScheduler integration)  
**REFACTOR Phase**: 2-3 hours (utility extraction)  
**Documentation**: 1 hour

**Total**: ~8-11 hours (~1-2 days)

---

## 🎯 Next Iteration Preview (TDD Iteration 2)

**Focus**: File Watching Integration with Watchdog
- Real-time inbox file detection
- Debouncing strategy (5-minute window)
- Integration with CoreWorkflowManager.process_inbox_note()
- Event-based vs scheduled processing

---

**Status**: ✅ PLANNING COMPLETE - Ready for RED phase execution
