"""
TDD RED Phase: Tests for daemon CLI integration with PIDLock

These tests verify that the daemon CLI properly uses the PIDLock mechanism
to prevent duplicate daemon spawning.

Issue #51: Daemon reliability - integrate PID lock into CLI commands.

Test Cases:
1. DaemonStarter uses daemon's PID file location (not separate file)
2. DaemonStarter checks PIDLock before spawning subprocess
3. Second start attempt returns "already running" without spawning
4. DaemonStopper removes PID file correctly
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestDaemonStarterPIDIntegration:
    """Test suite for DaemonStarter integration with PIDLock."""

    def setup_method(self):
        """Create temporary directory for PID files."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = Path(self.temp_dir) / "daemon.pid"

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_daemon_starter_uses_automation_pid_file(self):
        """
        DaemonStarter should use .automation/daemon.pid by default,
        matching the daemon's internal PIDLock location.

        CRITICAL: CLI and daemon must use SAME PID file to prevent zombie processes.
        """
        from src.cli.daemon_cli_utils import DaemonStarter
        from src.automation.config import DaemonConfig

        starter = DaemonStarter()
        daemon_config = DaemonConfig()

        # CLI's PID file must match daemon's configured PID file
        # The daemon uses .automation/daemon.pid (from DaemonConfig.pid_file)
        assert ".automation" in str(
            starter.pid_file
        ), f"DaemonStarter should use .automation/daemon.pid, not {starter.pid_file}"

        # Verify alignment with daemon config
        assert daemon_config.pid_file in str(
            starter.pid_file
        ), f"CLI PID file {starter.pid_file} doesn't match daemon config {daemon_config.pid_file}"

    def test_daemon_starter_checks_pid_lock_before_spawn(self):
        """
        DaemonStarter should use PIDLock to check if daemon is running
        before attempting to spawn a new process.
        """
        from src.cli.daemon_cli_utils import DaemonStarter

        # Create a PID file with our own PID (simulating running daemon)
        self.pid_file.write_text(str(os.getpid()))

        starter = DaemonStarter(pid_file_path=self.pid_file)

        # Mock subprocess to prevent actual daemon spawn
        with patch("src.cli.daemon_cli_utils.subprocess.Popen") as mock_popen:
            result = starter.start()

        # Should NOT spawn subprocess
        mock_popen.assert_not_called()

        # Should return "already running" message
        assert result["success"] is False
        assert "already running" in result["message"].lower()

    def test_daemon_starter_returns_existing_pid_on_duplicate(self):
        """
        When daemon is already running, start() should return the existing PID
        so user knows which process to check.
        """
        from src.cli.daemon_cli_utils import DaemonStarter

        existing_pid = os.getpid()
        self.pid_file.write_text(str(existing_pid))

        starter = DaemonStarter(pid_file_path=self.pid_file)

        with patch("src.cli.daemon_cli_utils.subprocess.Popen"):
            result = starter.start()

        assert str(existing_pid) in result["message"]

    def test_daemon_starter_cleans_stale_pid_and_starts(self):
        """
        If PID file exists but process is dead, DaemonStarter should
        clean up and allow new daemon to start.
        """
        from src.cli.daemon_cli_utils import DaemonStarter

        # Write stale PID (non-existent process)
        self.pid_file.write_text("99999999")

        starter = DaemonStarter(pid_file_path=self.pid_file)

        # Mock subprocess to simulate successful spawn
        mock_proc = MagicMock()
        mock_proc.pid = 12345

        with patch(
            "src.cli.daemon_cli_utils.subprocess.Popen", return_value=mock_proc
        ) as mock_popen:
            result = starter.start()

        # Should spawn new daemon
        mock_popen.assert_called_once()
        assert result["success"] is True


class TestDaemonStopperPIDIntegration:
    """Test suite for DaemonStopper integration with PIDLock."""

    def setup_method(self):
        """Create temporary directory for PID files."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = Path(self.temp_dir) / "daemon.pid"

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_daemon_stopper_removes_pid_file(self):
        """
        DaemonStopper should remove PID file after stopping daemon.
        """
        from src.cli.daemon_cli_utils import DaemonStopper

        # Create PID file with a fake PID
        self.pid_file.write_text("12345")

        stopper = DaemonStopper(pid_file_path=self.pid_file)

        with patch("os.kill") as mock_kill:
            # Simulate process not found (already stopped)
            mock_kill.side_effect = ProcessLookupError()
            result = stopper.stop()

        # PID file should be removed
        assert not self.pid_file.exists()

    def test_daemon_stopper_uses_automation_pid_file(self):
        """
        DaemonStopper should use same PID file location as DaemonStarter.
        """
        from src.cli.daemon_cli_utils import DaemonStarter, DaemonStopper

        starter = DaemonStarter()
        stopper = DaemonStopper()

        # Both should use the same default PID file
        assert starter.pid_file == stopper.pid_file


class TestMakeUpDownIntegration:
    """Integration tests for make up/down commands."""

    def setup_method(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = Path(self.temp_dir) / "daemon.pid"

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_make_up_twice_does_not_spawn_duplicate(self):
        """
        Calling 'make up' twice should not spawn duplicate daemons.
        Second call should exit with "already running" message.
        """
        from src.cli.daemon_cli_utils import DaemonStarter

        starter = DaemonStarter(pid_file_path=self.pid_file)

        # First start - mock successful spawn
        mock_proc = MagicMock()
        mock_proc.pid = 12345

        with patch("src.cli.daemon_cli_utils.subprocess.Popen", return_value=mock_proc):
            result1 = starter.start()

        assert result1["success"] is True

        # Simulate the PID file exists with running process
        self.pid_file.write_text("12345")

        # Mock os.kill to indicate process is running
        with patch("os.kill") as mock_kill:
            mock_kill.return_value = None  # Process exists

            # Second start should fail without spawning
            with patch("src.cli.daemon_cli_utils.subprocess.Popen") as mock_popen:
                result2 = starter.start()

            mock_popen.assert_not_called()

        assert result2["success"] is False
        assert "already running" in result2["message"].lower()
