"""
Test Suite for Daemon CLI Enhancement - TDD RED Phase

Tests for daemon management commands:
- inneros daemon start
- inneros daemon stop
- inneros daemon status
- inneros daemon logs

Following TDD methodology: RED → GREEN → REFACTOR
Phase: RED - Comprehensive failing tests
"""

from unittest.mock import patch


class TestDaemonStarter:
    """Tests for daemon start command."""

    def test_start_daemon_creates_pid_file(self, tmp_path):
        """Test that starting daemon creates PID file."""
        from development.src.cli.daemon_cli import DaemonStarter

        pid_file = tmp_path / "daemon.pid"
        starter = DaemonStarter(pid_file_path=pid_file)

        result = starter.start()

        assert result["success"] is True
        assert pid_file.exists()
        assert pid_file.read_text().strip().isdigit()

    def test_start_daemon_detects_already_running(self, tmp_path):
        """Test that starting detects already running daemon."""
        from development.src.cli.daemon_cli import DaemonStarter

        pid_file = tmp_path / "daemon.pid"
        # Create existing PID file with running process (our own PID)
        import os

        pid_file.write_text(str(os.getpid()))

        starter = DaemonStarter(pid_file_path=pid_file)
        result = starter.start()

        assert result["success"] is False
        assert "already running" in result["message"].lower()

    def test_start_daemon_subprocess_launch(self, tmp_path):
        """Test that daemon launches as subprocess."""
        from development.src.cli.daemon_cli import DaemonStarter

        daemon_script = tmp_path / "test_daemon.py"
        daemon_script.write_text("import time; time.sleep(0.1)")

        pid_file = tmp_path / "daemon.pid"
        starter = DaemonStarter(
            pid_file_path=pid_file, daemon_script=str(daemon_script)
        )

        result = starter.start()

        assert result["success"] is True
        assert "pid" in result
        assert isinstance(result["pid"], int)


class TestDaemonStopper:
    """Tests for daemon stop command."""

    def test_stop_daemon_removes_pid_file(self, tmp_path):
        """Test that stopping daemon removes PID file."""
        from development.src.cli.daemon_cli import DaemonStopper

        pid_file = tmp_path / "daemon.pid"
        # Create dummy PID file
        pid_file.write_text("99999")

        stopper = DaemonStopper(pid_file_path=pid_file)
        result = stopper.stop()

        # Should attempt cleanup even if PID doesn't exist
        assert not pid_file.exists()

    def test_stop_daemon_handles_not_running(self, tmp_path):
        """Test graceful handling when daemon not running."""
        from development.src.cli.daemon_cli import DaemonStopper

        pid_file = tmp_path / "daemon.pid"
        stopper = DaemonStopper(pid_file_path=pid_file)

        result = stopper.stop()

        assert result["success"] is False
        assert "not running" in result["message"].lower()

    def test_stop_daemon_graceful_shutdown(self, tmp_path):
        """Test graceful shutdown with SIGTERM."""
        from development.src.cli.daemon_cli import DaemonStopper

        pid_file = tmp_path / "daemon.pid"
        # Use our own PID for testing
        import os

        pid_file.write_text(str(os.getpid()))

        stopper = DaemonStopper(pid_file_path=pid_file)

        with patch("os.kill") as mock_kill:
            result = stopper.stop()

            # Should send SIGTERM (15) for graceful shutdown
            mock_kill.assert_called()


class TestEnhancedDaemonStatus:
    """Tests for enhanced daemon status command."""

    def test_status_shows_enhanced_details(self, tmp_path):
        """Test that status shows comprehensive daemon details."""
        from development.src.cli.daemon_cli import EnhancedDaemonStatus

        pid_file = tmp_path / "daemon.pid"
        import os

        pid_file.write_text(str(os.getpid()))

        status_checker = EnhancedDaemonStatus(pid_file_path=pid_file)
        result = status_checker.get_status()

        assert "running" in result
        assert "pid" in result
        assert "uptime" in result or "start_time" in result


class TestLogReader:
    """Tests for daemon log reading."""

    def test_logs_displays_recent_activity(self, tmp_path):
        """Test that logs command reads and displays recent log entries."""
        from development.src.cli.daemon_cli import LogReader

        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        log_file = logs_dir / "daemon.log"
        log_file.write_text(
            "2025-10-15 20:00:00 INFO: Starting daemon\n"
            "2025-10-15 20:01:00 INFO: Processing complete\n"
        )

        reader = LogReader(logs_dir=logs_dir)
        result = reader.read_recent(lines=10)

        assert result["success"] is True
        assert len(result["entries"]) > 0
        assert "Starting daemon" in str(result["entries"])

    def test_logs_handles_missing_log_file(self, tmp_path):
        """Test graceful handling of missing log files."""
        from development.src.cli.daemon_cli import LogReader

        logs_dir = tmp_path / "logs"
        # Don't create logs_dir

        reader = LogReader(logs_dir=logs_dir)
        result = reader.read_recent(lines=10)

        assert result["success"] is False
        assert (
            "no logs" in result["message"].lower()
            or "not found" in result["message"].lower()
        )


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_error_handling_permission_denied(self, tmp_path):
        """Test handling of permission errors."""
        from development.src.cli.daemon_cli import DaemonStarter

        # Create read-only directory
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir(mode=0o444)
        pid_file = restricted_dir / "daemon.pid"

        starter = DaemonStarter(pid_file_path=pid_file)
        result = starter.start()

        # Should handle permission error gracefully
        assert result["success"] is False
        assert (
            "permission" in result["message"].lower()
            or "error" in result["message"].lower()
        )

    def test_error_handling_invalid_pid(self, tmp_path):
        """Test handling of invalid PID in file."""
        from development.src.cli.daemon_cli import DaemonStopper

        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("invalid_pid_data")

        stopper = DaemonStopper(pid_file_path=pid_file)
        result = stopper.stop()

        # Should handle gracefully
        assert "pid" in str(result).lower() or "invalid" in str(result).lower()


class TestDaemonOrchestrator:
    """Tests for main orchestrator and command routing."""

    def test_orchestrator_integration(self, tmp_path):
        """Test that orchestrator routes commands correctly."""
        from development.src.cli.daemon_cli import DaemonOrchestrator

        pid_file = tmp_path / "daemon.pid"
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        orchestrator = DaemonOrchestrator(pid_file_path=pid_file, logs_dir=logs_dir)

        # Test command routing
        assert hasattr(orchestrator, "start")
        assert hasattr(orchestrator, "stop")
        assert hasattr(orchestrator, "status")
        assert hasattr(orchestrator, "logs")

        # Test status when not running
        status_result = orchestrator.status()
        assert "running" in status_result or "status" in status_result
