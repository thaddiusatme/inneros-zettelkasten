"""
TDD Iteration 3: Daemon Alignment Tests

RED Phase: Tests that verify `make status` correctly detects the Python daemon
started by `make up`. The Python daemon writes its PID to ~/.inneros/daemon.pid.

Architecture Problem Being Fixed:
- daemon_registry.yaml defines shell scripts as "daemons"
- DaemonDetector searches ps aux for script paths
- AutomationDaemon (Python) writes to ~/.inneros/daemon.pid
- These don't align, so `make status` always shows 0/3 running

Solution: Update system_health.py to detect the Python daemon via PID file.
"""

import os
from pathlib import Path
from unittest.mock import patch


class TestPythonDaemonDetection:
    """Tests for detecting the Python automation daemon via PID file."""

    def test_status_shows_running_when_pid_file_exists_and_process_alive(
        self, tmp_path
    ):
        """When PID file exists with valid running process, status should show running.

        This is the core fix: check ~/.inneros/daemon.pid instead of ps aux script matching.
        """
        from src.automation.system_health import check_all

        # Create a fake PID file with our test process PID
        pid_file = tmp_path / ".inneros" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()))  # Use current process as "running"

        # Mock the daemon registry to return our Python daemon entry
        with patch("src.automation.system_health._load_daemons") as mock_load:
            mock_load.return_value = [
                {
                    "name": "automation_daemon",
                    "script_path": "src.automation.daemon",  # Python module, not shell script
                    "log_path": ".automation/logs/daemon.log",
                    "pid_file": str(pid_file),
                    "description": "Main InnerOS automation daemon",
                }
            ]

            with patch("src.automation.system_health._get_daemon_pid_file") as mock_pid:
                mock_pid.return_value = pid_file

                result = check_all(repo_root=tmp_path)

        # Expect the daemon to show as running
        assert result["overall_status"] == "OK", f"Expected OK, got {result}"
        assert len(result["automations"]) >= 1

        daemon_status = result["automations"][0]
        assert (
            daemon_status["running"] is True
        ), f"Daemon should be running: {daemon_status}"
        assert daemon_status["name"] == "automation_daemon"

    def test_status_shows_not_running_when_pid_file_missing(self, tmp_path):
        """When PID file doesn't exist, status should show not running."""
        from src.automation.system_health import check_all

        # No PID file created
        pid_file = tmp_path / ".inneros" / "daemon.pid"

        with patch("src.automation.system_health._load_daemons") as mock_load:
            mock_load.return_value = [
                {
                    "name": "automation_daemon",
                    "script_path": "src.automation.daemon",
                    "log_path": ".automation/logs/daemon.log",
                    "pid_file": str(pid_file),
                    "description": "Main InnerOS automation daemon",
                }
            ]

            with patch("src.automation.system_health._get_daemon_pid_file") as mock_pid:
                mock_pid.return_value = pid_file

                result = check_all(repo_root=tmp_path)

        # Expect daemon to show as not running
        assert len(result["automations"]) >= 1
        daemon_status = result["automations"][0]
        assert (
            daemon_status["running"] is False
        ), f"Daemon should not be running: {daemon_status}"

    def test_status_shows_not_running_when_pid_file_has_stale_process(self, tmp_path):
        """When PID file exists but process is not running, status shows not running."""
        from src.automation.system_health import check_all

        # Create PID file with a non-existent PID
        pid_file = tmp_path / ".inneros" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text("999999")  # Very unlikely to be a real running process

        with patch("src.automation.system_health._load_daemons") as mock_load:
            mock_load.return_value = [
                {
                    "name": "automation_daemon",
                    "script_path": "src.automation.daemon",
                    "log_path": ".automation/logs/daemon.log",
                    "pid_file": str(pid_file),
                    "description": "Main InnerOS automation daemon",
                }
            ]

            with patch("src.automation.system_health._get_daemon_pid_file") as mock_pid:
                mock_pid.return_value = pid_file

                result = check_all(repo_root=tmp_path)

        # Expect daemon to show as not running (stale PID)
        assert len(result["automations"]) >= 1
        daemon_status = result["automations"][0]
        assert (
            daemon_status["running"] is False
        ), f"Daemon should not be running (stale): {daemon_status}"


class TestDaemonDetectorPIDSupport:
    """Tests for enhanced DaemonDetector with PID file support."""

    def test_detector_checks_pid_file_when_provided(self, tmp_path):
        """DaemonDetector should check PID file in addition to ps aux matching."""
        from src.cli.automation_status_cli import DaemonDetector

        # Create a PID file with current process
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text(str(os.getpid()))

        detector = DaemonDetector()

        # New method that should be added: check_daemon_by_pid_file
        status = detector.check_daemon_by_pid_file(pid_file)

        assert status["running"] is True
        assert status["pid"] == os.getpid()

    def test_detector_returns_not_running_for_missing_pid_file(self, tmp_path):
        """DaemonDetector should handle missing PID file gracefully."""
        from src.cli.automation_status_cli import DaemonDetector

        pid_file = tmp_path / "nonexistent.pid"

        detector = DaemonDetector()
        status = detector.check_daemon_by_pid_file(pid_file)

        assert status["running"] is False
        assert status["pid"] is None

    def test_detector_returns_not_running_for_stale_pid_file(self, tmp_path):
        """DaemonDetector should detect stale PID files (process not running)."""
        from src.cli.automation_status_cli import DaemonDetector

        # Create PID file with non-existent process
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("999999")  # Very unlikely to be running

        detector = DaemonDetector()
        status = detector.check_daemon_by_pid_file(pid_file)

        assert status["running"] is False
        assert status["pid"] is None


class TestSystemHealthPIDFileIntegration:
    """Integration tests for system_health using PID file detection."""

    def test_check_all_uses_pid_file_for_python_daemon(self, tmp_path):
        """check_all should use PID file detection for the Python daemon."""
        from src.automation.system_health import check_all

        # Setup: create daemon registry YAML with Python daemon entry
        config_dir = tmp_path / ".automation" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        registry_file = config_dir / "daemon_registry.yaml"
        registry_file.write_text(
            """
daemons:
  - name: automation_daemon
    script_path: src.automation.daemon
    log_path: .automation/logs/daemon.log
    pid_file: .inneros/daemon.pid
    description: Main InnerOS automation daemon
"""
        )

        # Create running daemon PID file
        pid_file = tmp_path / ".inneros" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()))

        result = check_all(repo_root=tmp_path)

        # Verify Python daemon is detected via PID file
        assert len(result["automations"]) == 1
        daemon_status = result["automations"][0]
        assert daemon_status["name"] == "automation_daemon"
        assert (
            daemon_status["running"] is True
        ), f"Should detect running daemon: {daemon_status}"
        assert result["overall_status"] == "OK"

    def test_check_all_returns_ok_with_single_running_daemon(self, tmp_path):
        """Simplified 1-daemon model: overall_status OK when daemon is running."""
        from src.automation.system_health import check_all

        # Setup registry with single Python daemon
        config_dir = tmp_path / ".automation" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        registry_file = config_dir / "daemon_registry.yaml"
        registry_file.write_text(
            """
daemons:
  - name: automation_daemon
    script_path: src.automation.daemon
    log_path: .automation/logs/daemon.log
    pid_file: .inneros/daemon.pid
    description: Main InnerOS automation daemon
"""
        )

        # Daemon running
        pid_file = tmp_path / ".inneros" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()))

        result = check_all(repo_root=tmp_path)

        assert result["overall_status"] == "OK"

    def test_check_all_returns_warning_when_daemon_not_running(self, tmp_path):
        """Simplified 1-daemon model: overall_status WARNING when daemon stopped."""
        from src.automation.system_health import check_all

        # Setup registry with single Python daemon
        config_dir = tmp_path / ".automation" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        registry_file = config_dir / "daemon_registry.yaml"
        registry_file.write_text(
            """
daemons:
  - name: automation_daemon
    script_path: src.automation.daemon
    log_path: .automation/logs/daemon.log
    pid_file: .inneros/daemon.pid
    description: Main InnerOS automation daemon
"""
        )

        # No PID file = daemon not running

        result = check_all(repo_root=tmp_path)

        # Not running without errors should be WARNING (not ERROR)
        assert result["overall_status"] in ["WARNING", "ERROR"]


class TestMakeUpMakeStatusCycleAlignment:
    """Tests ensuring make up && make status cycle works correctly."""

    def test_status_uses_same_pid_file_as_daemon_start(self, tmp_path):
        """Status checker must use same PID file location as daemon starter."""
        from src.cli.daemon_cli_utils import DaemonStarter

        # Get default PID file path from DaemonStarter
        starter = DaemonStarter()
        expected_pid_path = starter.pid_file

        # Verify it's ~/.inneros/daemon.pid
        assert expected_pid_path == Path.home() / ".inneros" / "daemon.pid"

        # Now verify system_health can be configured to check this location
        # This will fail until we implement the fix
        from src.automation import system_health

        # New function we need to add
        pid_file = system_health._get_daemon_pid_file()
        assert (
            pid_file == expected_pid_path
        ), f"PID file mismatch: {pid_file} vs {expected_pid_path}"

    def test_integration_daemon_start_then_status_shows_running(self, tmp_path):
        """Full integration: start daemon, check status shows running."""
        from src.cli.daemon_cli_utils import EnhancedDaemonStatus
        from src.automation.system_health import check_all

        # Use tmp_path for PID file in test
        pid_file = tmp_path / ".inneros" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)

        # Simulate daemon start (just write PID, don't actually fork)
        pid_file.write_text(str(os.getpid()))

        # Check via EnhancedDaemonStatus (daemon CLI)
        status_checker = EnhancedDaemonStatus(pid_file_path=pid_file)
        status = status_checker.get_status()
        assert (
            status["running"] is True
        ), f"EnhancedDaemonStatus should detect running: {status}"

        # Check via system_health (make status path)
        # This requires the fix we're implementing
        config_dir = tmp_path / ".automation" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        registry_file = config_dir / "daemon_registry.yaml"
        registry_file.write_text(
            f"""
daemons:
  - name: automation_daemon
    script_path: src.automation.daemon
    log_path: .automation/logs/daemon.log
    pid_file: {pid_file}
    description: Main InnerOS automation daemon
"""
        )

        result = check_all(repo_root=tmp_path)

        assert len(result["automations"]) == 1
        assert result["automations"][0]["running"] is True
        assert result["overall_status"] == "OK"
