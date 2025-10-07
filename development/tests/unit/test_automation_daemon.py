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

# Import real implementation classes (GREEN phase completed)
from src.automation.daemon import DaemonState, DaemonStatus, DaemonError
from src.automation.health import HealthReport
from src.automation.scheduler import JobInfo
from src.automation.config import DaemonConfig


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

# ============================================================================
# TDD Iteration 2 P1.1: File Watcher Integration Tests (5 tests)
# ============================================================================

class TestDaemonFileWatcherIntegration:
    """Test FileWatcher lifecycle integration with AutomationDaemon."""
    
    @pytest.fixture
    def temp_watch_dir(self, tmp_path):
        """Create temporary watch directory."""
        watch_dir = tmp_path / "inbox"
        watch_dir.mkdir()
        return watch_dir
    
    @pytest.fixture
    def config_with_file_watching(self, temp_watch_dir):
        """
        Create config with file watching enabled.
        
        Will fail: AttributeError - DaemonConfig has no attribute 'file_watching'
        """
        from src.automation.config import FileWatchConfig
        
        return DaemonConfig(
            check_interval=60,
            log_level="INFO",
            file_watching=FileWatchConfig(
                enabled=True,
                watch_path=str(temp_watch_dir),
                patterns=["*.md"],
                ignore_patterns=[".obsidian/*", "*.tmp"],
                debounce_seconds=2
            )
        )
    
    def test_daemon_starts_file_watcher_when_enabled(self, config_with_file_watching):
        """
        P0.1.1: Daemon initializes and starts FileWatcher on start().
        
        Expected behavior:
        - Daemon creates FileWatcher instance when config.file_watching.enabled=True
        - FileWatcher started after scheduler initialization
        - Watcher actively monitoring the configured path
        - Watcher callback registered for event handling
        
        Will fail: AttributeError - AutomationDaemon has no attribute 'file_watcher'
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon(config=config_with_file_watching)
        daemon.start()
        
        # Verify file watcher created and started
        assert daemon.file_watcher is not None, "Should create file_watcher when enabled"
        assert daemon.file_watcher.is_running() is True, "Watcher should be running"
        assert daemon.file_watcher.watch_path == Path(config_with_file_watching.file_watching.watch_path)
        
        daemon.stop()
    
    def test_daemon_stops_file_watcher_gracefully(self, config_with_file_watching):
        """
        P0.1.2: Daemon stops FileWatcher on stop().
        
        Expected behavior:
        - FileWatcher stopped BEFORE scheduler shutdown (reverse start order)
        - Observer threads cleaned up gracefully
        - No orphaned watchdog threads
        - Watcher state reflects stopped status
        
        Will fail: AttributeError - daemon.file_watcher not yet defined
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon(config=config_with_file_watching)
        daemon.start()
        
        # Verify watcher running
        assert daemon.file_watcher.is_running() is True
        
        # Stop daemon
        daemon.stop()
        
        # Verify watcher stopped
        assert daemon.file_watcher.is_running() is False, "Watcher should be stopped"
    
    def test_daemon_status_includes_watcher_state(self, config_with_file_watching):
        """
        P0.1.3: status() reports watcher running/stopped in DaemonStatus.
        
        Expected behavior:
        - DaemonStatus includes watcher_active field
        - watcher_active=True when watcher running
        - watcher_active=False when watcher stopped
        - watcher_active=False when file watching disabled
        
        Will fail: AttributeError - DaemonStatus missing 'watcher_active' field
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon(config=config_with_file_watching)
        daemon.start()
        
        # Check status reports watcher active
        status = daemon.status()
        assert hasattr(status, 'watcher_active'), "DaemonStatus should have watcher_active field"
        assert status.watcher_active is True, "Should report watcher as active when running"
        
        # Stop and verify status updated
        daemon.stop()
        status = daemon.status()
        assert status.watcher_active is False, "Should report watcher as inactive when stopped"
    
    def test_daemon_respects_config_file_watching_disabled(self, temp_watch_dir):
        """
        P0.1.4: Watcher not started when config.file_watching.enabled=False.
        
        Expected behavior:
        - No FileWatcher created when enabled=False
        - Daemon starts normally without watcher
        - Status reports watcher_active=False
        - No watchdog threads created
        
        Will fail: AttributeError - DaemonConfig has no 'file_watching' attribute
        """
        from src.automation.daemon import AutomationDaemon
        from src.automation.config import FileWatchConfig
        
        # Config with file watching disabled
        config = DaemonConfig(
            check_interval=60,
            log_level="INFO",
            file_watching=FileWatchConfig(
                enabled=False,
                watch_path=str(temp_watch_dir),
                patterns=["*.md"],
                ignore_patterns=[],
                debounce_seconds=2
            )
        )
        
        daemon = AutomationDaemon(config=config)
        daemon.start()
        
        # Verify no watcher created
        assert daemon.file_watcher is None or not daemon.file_watcher.is_running(), \
            "Should not start watcher when disabled"
        
        # Status should reflect no watcher
        status = daemon.status()
        assert status.watcher_active is False, "Status should show watcher inactive"
        
        daemon.stop()
    
    def test_health_check_includes_watcher_status(self, config_with_file_watching):
        """
        P0.1.5: Health report includes watcher health check.
        
        Expected behavior:
        - HealthReport.checks includes 'file_watcher' key
        - file_watcher check shows status when watcher enabled
        - file_watcher check handles watcher disabled gracefully
        - Health check validates watcher thread is alive
        
        Will fail: KeyError - HealthReport.checks missing 'file_watcher' key
        """
        from src.automation.daemon import AutomationDaemon
        
        daemon = AutomationDaemon(config=config_with_file_watching)
        daemon.start()
        
        health = daemon.health.get_health_status()
        
        # Verify file_watcher in checks
        assert "file_watcher" in health.checks, "Health report should include file_watcher check"
        assert health.checks["file_watcher"] is True, "Watcher should report healthy when running"
        
        daemon.stop()


# ============================================================================
# Test Execution Summary
# ============================================================================

"""
RED Phase Test Summary:

TDD Iteration 1 (COMPLETED): 15/15 tests passing
- P0.1 Daemon Lifecycle: 5 tests ✅
- P0.2 Scheduler Integration: 5 tests ✅
- P0.3 Health Checks: 3 tests ✅
- P0.4 Configuration: 2 tests ✅

TDD Iteration 2 P1.1 (RED PHASE): 5/5 tests WILL FAIL
- File Watcher Integration: 5 tests ❌

Expected Failures:
1. test_daemon_starts_file_watcher_when_enabled - AttributeError: daemon.file_watcher not defined
2. test_daemon_stops_file_watcher_gracefully - AttributeError: daemon.file_watcher not defined
3. test_daemon_status_includes_watcher_state - AttributeError: DaemonStatus missing watcher_active
4. test_daemon_respects_config_file_watching_disabled - AttributeError: DaemonConfig missing file_watching
5. test_health_check_includes_watcher_status - KeyError: 'file_watcher' not in health.checks

Next Phase: GREEN - Implement daemon-watcher integration (~30 LOC)
Required changes:
- src/automation/config.py: Add FileWatchConfig dataclass
- src/automation/daemon.py: Add file_watcher lifecycle management
- src/automation/health.py: Add watcher health check
"""
