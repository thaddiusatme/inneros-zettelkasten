"""
Automation Daemon TDD Iteration 1 - RED Phase

Complete test suite for 24/7 background daemon service with APScheduler integration.
Following Phase 3 requirements from automation-monitoring-requirements.md.

Test Coverage:
- P0.1: Daemon Lifecycle (5 tests) - start, stop, restart, status, error handling
- P0.2: Scheduler Integration (5 tests) - job management, execution tracking
- P0.3: Health Checks (3 tests) - monitoring, metrics, status reporting
- P0.4: Configuration (2 tests) - YAML loading, validation

Architecture Requirements (ADR-001):
- All classes <500 LOC
- Domain separation: Scheduler / Health / Config / Lifecycle
- No god classes
- Single responsibility per class

RED Phase Target: 15/15 tests failing with clear import/attribute errors
"""

import pytest
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from enum import Enum


# Type hints for expected classes (will be implemented in GREEN phase)
class DaemonState(Enum):
    """Daemon operational states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class DaemonStatus:
    """Daemon status information"""
    state: DaemonState
    scheduler_active: bool
    active_jobs: int
    uptime_seconds: float


class HealthReport:
    """Health check report"""
    is_healthy: bool
    status_code: int
    checks: Dict[str, bool]


class JobInfo:
    """Scheduled job information"""
    id: str
    schedule: str
    next_run: Optional[datetime]


class DaemonConfig:
    """Daemon configuration"""
    check_interval: int
    log_level: str
    jobs: List[Any]


class DaemonError(Exception):
    """Daemon-specific errors"""
    pass


# ============================================================================
# P0.1: Daemon Lifecycle Tests (5 tests)
# ============================================================================

class TestDaemonLifecycle:
    """Test daemon start, stop, restart, and status management."""
    
    def test_daemon_starts_successfully(self):
        """
        P0.1.1: Daemon initializes APScheduler and enters running state.
        
        Expected behavior:
        - Creates BackgroundScheduler instance
        - Initializes with default configuration
        - Transitions to RUNNING state
        - Scheduler becomes active
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        status = daemon.status()
        assert status.state == DaemonState.RUNNING, "Daemon should be in RUNNING state after start()"
        assert status.scheduler_active is True, "Scheduler should be active when daemon running"
        
        daemon.stop()
    
    def test_daemon_stops_gracefully(self):
        """
        P0.1.2: Daemon shuts down cleanly, finishing active jobs.
        
        Expected behavior:
        - Waits for current jobs to complete
        - Shuts down scheduler gracefully
        - Transitions to STOPPED state
        - Cleans up resources
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Verify running
        assert daemon.status().state == DaemonState.RUNNING
        
        # Stop gracefully
        daemon.stop()
        
        status = daemon.status()
        assert status.state == DaemonState.STOPPED, "Daemon should be STOPPED after stop()"
        assert status.active_jobs == 0, "No jobs should be active after graceful shutdown"
    
    def test_daemon_restart_preserves_jobs(self):
        """
        P0.1.3: Restart doesn't lose scheduled jobs.
        
        Expected behavior:
        - Captures current job definitions
        - Performs atomic shutdown/startup
        - Restores all previously scheduled jobs
        - Maintains job configuration and schedules
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Add a test job
        test_executed = False
        def test_job():
            nonlocal test_executed
            test_executed = True
        
        daemon.scheduler.add_job("test-job", test_job, "0 8 * * *")
        
        # Verify job exists
        jobs_before = daemon.scheduler.list_jobs()
        assert len(jobs_before) == 1, "Should have 1 scheduled job before restart"
        
        # Restart
        daemon.restart()
        
        # Verify job still exists
        jobs_after = daemon.scheduler.list_jobs()
        assert len(jobs_after) == 1, "Should still have 1 job after restart"
        assert jobs_after[0].id == "test-job", "Job ID should be preserved"
        
        daemon.stop()
    
    def test_daemon_status_reports_correctly(self):
        """
        P0.1.4: Status reflects actual daemon state transitions.
        
        Expected behavior:
        - Reports STOPPED when not started
        - Reports RUNNING when active
        - Tracks uptime accurately
        - Updates state on transitions
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        
        # Initial state should be STOPPED
        initial_status = daemon.status()
        assert initial_status.state == DaemonState.STOPPED, "New daemon should be STOPPED"
        
        # Start daemon
        daemon.start()
        running_status = daemon.status()
        assert running_status.state == DaemonState.RUNNING, "Started daemon should be RUNNING"
        assert running_status.uptime_seconds >= 0, "Uptime should be non-negative"
        
        # Wait a bit to verify uptime increases
        time.sleep(0.5)
        updated_status = daemon.status()
        assert updated_status.uptime_seconds >= 0.5, "Uptime should increase over time"
        
        # Stop daemon
        daemon.stop()
        stopped_status = daemon.status()
        assert stopped_status.state == DaemonState.STOPPED, "Stopped daemon should be STOPPED"
    
    def test_daemon_handles_start_when_already_running(self):
        """
        P0.1.5: Starting already-running daemon raises clear error.
        
        Expected behavior:
        - Detects daemon is already running
        - Raises DaemonError with descriptive message
        - Does not create duplicate scheduler
        - Leaves daemon in stable RUNNING state
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Attempt to start again
        with pytest.raises(DaemonError, match="already running"):
            daemon.start()
        
        # Verify daemon still running normally
        assert daemon.status().state == DaemonState.RUNNING
        
        daemon.stop()


# ============================================================================
# P0.2: Scheduler Integration Tests (5 tests)
# ============================================================================

class TestSchedulerIntegration:
    """Test APScheduler integration for job management and execution."""
    
    def test_add_job_creates_scheduled_task(self):
        """
        P0.2.1: Jobs are successfully registered with APScheduler.
        
        Expected behavior:
        - Job registered with BackgroundScheduler
        - Cron expression parsed correctly
        - Job executes on schedule
        - Function called with correct timing
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Track execution
        job_executed = False
        def test_func():
            nonlocal job_executed
            job_executed = True
        
        # Schedule job every second for testing
        daemon.scheduler.add_job("test-job", test_func, "* * * * * */1")
        
        # Wait for execution
        time.sleep(1.5)
        assert job_executed is True, "Job should have executed within 1.5 seconds"
        
        daemon.stop()
    
    def test_remove_job_cancels_scheduled_task(self):
        """
        P0.2.2: Removed jobs stop executing.
        
        Expected behavior:
        - Job removed from scheduler
        - No further executions occur
        - Removal is immediate
        - No errors on removal
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Track executions
        execution_count = 0
        def test_func():
            nonlocal execution_count
            execution_count += 1
        
        # Schedule every second
        daemon.scheduler.add_job("test-job", test_func, "* * * * * */1")
        time.sleep(1.5)
        
        # Remove job
        initial_count = execution_count
        daemon.scheduler.remove_job("test-job")
        
        # Wait and verify no new executions
        time.sleep(2)
        assert execution_count == initial_count, "No executions should occur after removal"
        
        daemon.stop()
    
    def test_list_jobs_returns_all_scheduled(self):
        """
        P0.2.3: Can retrieve all registered jobs.
        
        Expected behavior:
        - Returns complete list of scheduled jobs
        - Includes job metadata (ID, schedule, next_run)
        - List updates when jobs added/removed
        - Empty list when no jobs scheduled
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Initially no jobs
        initial_jobs = daemon.scheduler.list_jobs()
        assert len(initial_jobs) == 0, "New daemon should have no jobs"
        
        # Add jobs
        daemon.scheduler.add_job("job-1", lambda: None, "0 8 * * *")
        daemon.scheduler.add_job("job-2", lambda: None, "0 12 * * *")
        
        # Verify both listed
        jobs = daemon.scheduler.list_jobs()
        assert len(jobs) == 2, "Should list both scheduled jobs"
        job_ids = {job.id for job in jobs}
        assert job_ids == {"job-1", "job-2"}, "Should return correct job IDs"
        
        daemon.stop()
    
    def test_job_execution_tracked(self):
        """
        P0.2.4: Job executions are recorded with success/failure metrics.
        
        Expected behavior:
        - Tracks total execution count
        - Records successful executions
        - Tracks execution duration
        - Updates metrics in real-time
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Schedule successful job
        def successful_job():
            return "success"
        
        daemon.scheduler.add_job("tracked-job", successful_job, "* * * * * */1")
        
        # Wait for execution
        time.sleep(1.5)
        
        # Check metrics
        metrics = daemon.health.get_metrics()
        assert metrics["total_job_executions"] >= 1, "Should track execution"
        assert metrics["successful_executions"] >= 1, "Should track success"
        
        daemon.stop()
    
    def test_job_failure_handled_gracefully(self):
        """
        P0.2.5: Failed jobs don't crash daemon.
        
        Expected behavior:
        - Job exception caught and logged
        - Daemon continues running
        - Failure recorded in metrics
        - Other jobs continue executing
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        # Schedule failing job
        def failing_job():
            raise Exception("Intentional failure for testing")
        
        daemon.scheduler.add_job("failing-job", failing_job, "* * * * * */1")
        
        # Wait for execution
        time.sleep(1.5)
        
        # Daemon should still be running
        assert daemon.status().state == DaemonState.RUNNING, "Daemon should survive job failure"
        
        # Failure should be tracked
        metrics = daemon.health.get_metrics()
        assert metrics["failed_executions"] >= 1, "Should track failures"
        
        daemon.stop()


# ============================================================================
# P0.3: Health Check Tests (3 tests)
# ============================================================================

class TestHealthChecks:
    """Test health monitoring and metrics collection."""
    
    def test_health_check_returns_healthy_when_running(self):
        """
        P0.3.1: Healthy daemon returns positive health status.
        
        Expected behavior:
        - Returns HealthReport with is_healthy=True
        - HTTP 200 status code
        - All component checks passing
        - Scheduler check included
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        
        health = daemon.health.get_health_status()
        
        assert health.is_healthy is True, "Running daemon should be healthy"
        assert health.status_code == 200, "Healthy status should return 200"
        assert "scheduler" in health.checks, "Should check scheduler status"
        assert health.checks["scheduler"] is True, "Scheduler should be healthy"
        
        daemon.stop()
    
    def test_health_check_unhealthy_when_stopped(self):
        """
        P0.3.2: Stopped daemon reports unhealthy.
        
        Expected behavior:
        - Returns HealthReport with is_healthy=False
        - HTTP 503 status code
        - Component checks reflect stopped state
        - Clear reason for unhealthy status
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        
        health = daemon.health.get_health_status()
        
        assert health.is_healthy is False, "Stopped daemon should be unhealthy"
        assert health.status_code == 503, "Unhealthy status should return 503"
    
    def test_metrics_track_uptime_and_jobs(self):
        """
        P0.3.3: Metrics include uptime, job counts, and execution stats.
        
        Expected behavior:
        - Tracks uptime in seconds
        - Counts total/active jobs
        - Records execution statistics
        - Updates metrics in real-time
        
        Will fail: ImportError - AutomationDaemon not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon()
        daemon.start()
        time.sleep(0.5)
        
        metrics = daemon.health.get_metrics()
        
        # Verify required metrics exist
        assert "uptime_seconds" in metrics, "Should track uptime"
        assert metrics["uptime_seconds"] >= 0.5, "Uptime should be at least 0.5 seconds"
        
        assert "total_jobs" in metrics, "Should track total jobs"
        assert "active_jobs" in metrics, "Should track active jobs"
        assert "total_job_executions" in metrics, "Should track executions"
        
        daemon.stop()


# ============================================================================
# P0.4: Configuration Tests (2 tests)
# ============================================================================

class TestConfiguration:
    """Test YAML configuration loading and validation."""
    
    def test_load_valid_config(self):
        """
        P0.4.1: Valid YAML config loads successfully.
        
        Expected behavior:
        - Parses YAML file correctly
        - Validates configuration schema
        - Returns DaemonConfig object
        - All fields properly typed
        
        Will fail: ImportError - ConfigurationLoader not yet defined
        """
        from src.automation.config import ConfigurationLoader
        
        # Create test config file
        config_path = Path("/tmp/test_daemon_config.yml")
        config_path.write_text("""
daemon:
  check_interval: 60
  log_level: INFO
  
jobs:
  - name: inbox_processing
    schedule: "0 8 * * *"
    enabled: true
""")
        
        loader = ConfigurationLoader()
        config = loader.load_config(config_path)
        
        assert config.check_interval == 60, "Should load check_interval"
        assert config.log_level == "INFO", "Should load log_level"
        assert len(config.jobs) == 1, "Should load job definitions"
        assert config.jobs[0].name == "inbox_processing", "Should parse job name"
        
        # Cleanup
        config_path.unlink()
    
    def test_invalid_config_raises_validation_error(self):
        """
        P0.4.2: Malformed config returns clear validation errors.
        
        Expected behavior:
        - Validates configuration values
        - Returns list of specific errors
        - Includes field names in errors
        - Provides actionable error messages
        
        Will fail: ImportError - ConfigurationLoader not yet defined
        """
        from src.automation.config import ConfigurationLoader
        
        # Create invalid config
        config_path = Path("/tmp/invalid_daemon_config.yml")
        config_path.write_text("""
daemon:
  check_interval: -1  # Invalid: must be positive
  log_level: INVALID  # Invalid: not a valid log level
""")
        
        loader = ConfigurationLoader()
        errors = loader.validate_config_file(config_path)
        
        assert len(errors) >= 2, "Should return validation errors"
        assert any("check_interval" in err for err in errors), "Should flag check_interval"
        assert any("log_level" in err for err in errors), "Should flag log_level"
        
        # Cleanup
        config_path.unlink()


# ============================================================================
# Test Execution Summary
# ============================================================================

"""
RED Phase Test Summary:

Expected Failures: 15/15 tests
Failure Reason: ImportError (modules not yet created)

Test Breakdown:
- P0.1 Daemon Lifecycle: 5 tests
- P0.2 Scheduler Integration: 5 tests  
- P0.3 Health Checks: 3 tests
- P0.4 Configuration: 2 tests

All tests will fail with clear import errors until GREEN phase implements:
- src/automation/daemon.py (AutomationDaemon class)
- src/automation/scheduler.py (SchedulerManager class)
- src/automation/health.py (HealthCheckManager class)
- src/automation/config.py (ConfigurationLoader class)

Next Phase: GREEN - Minimal APScheduler integration (~400 LOC)
"""
