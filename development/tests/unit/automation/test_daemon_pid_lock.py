"""
TDD RED Phase: Tests for daemon PID file locking

These tests verify that the daemon properly manages process locking to prevent
multiple instances from running simultaneously.

Issue #51: Daemon reliability - prevent zombie processes through PID file locking.

Test Cases:
1. Daemon acquires PID lock on start
2. Daemon refuses to start if lock is already held
3. Daemon releases lock on shutdown
4. Stale lock file (process dead) allows new daemon to start
"""

import os
import tempfile
from pathlib import Path

import pytest


class TestDaemonPIDLocking:
    """Test suite for daemon PID file locking functionality."""

    def setup_method(self):
        """Create temporary directory for PID files."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = Path(self.temp_dir) / "daemon.pid"

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_daemon_acquires_pid_lock_on_start(self):
        """
        Daemon should create PID file with current process ID on start.

        Expected behavior:
        - PID file created at configured location
        - File contains current process PID
        - File has exclusive lock held
        """
        from src.automation.pid_lock import PIDLock

        # Create daemon with custom PID file location
        lock = PIDLock(self.pid_file)

        # Acquire lock should succeed
        lock.acquire()

        # PID file should exist and contain our PID
        assert self.pid_file.exists(), "PID file should be created"
        assert self.pid_file.read_text().strip() == str(
            os.getpid()
        ), "PID file should contain current process ID"

        # Clean up
        lock.release()

    def test_daemon_refuses_start_if_lock_held(self):
        """
        RED: Daemon should refuse to start if another process holds the lock.

        Expected behavior:
        - Second daemon start attempt raises PIDLockError
        - Error message includes PID of existing daemon
        - No zombie processes created
        """
        from src.automation.pid_lock import PIDLock, PIDLockError

        # First lock acquisition
        lock1 = PIDLock(self.pid_file)
        lock1.acquire()

        # Second lock attempt should fail
        lock2 = PIDLock(self.pid_file)
        with pytest.raises(PIDLockError) as exc_info:
            lock2.acquire()

        assert (
            "already running" in str(exc_info.value).lower()
        ), "Error should indicate daemon is already running"

        # Clean up
        lock1.release()

    def test_daemon_releases_lock_on_shutdown(self):
        """
        RED: Daemon should release lock and remove PID file on graceful shutdown.

        Expected behavior:
        - PID file removed after release
        - Lock released so new daemon can start
        """
        from src.automation.pid_lock import PIDLock

        lock = PIDLock(self.pid_file)
        lock.acquire()

        # PID file should exist
        assert self.pid_file.exists()

        # Release lock
        lock.release()

        # PID file should be removed
        assert not self.pid_file.exists(), "PID file should be removed on release"

        # New lock should be acquirable
        lock2 = PIDLock(self.pid_file)
        lock2.acquire()  # Should not raise
        lock2.release()

    def test_stale_lock_allows_new_daemon(self):
        """
        RED: If PID file exists but process is dead, new daemon should start.

        Expected behavior:
        - Stale PID file (dead process) is detected
        - Stale lock is cleaned up
        - New daemon can acquire lock
        """
        from src.automation.pid_lock import PIDLock

        # Create stale PID file with non-existent PID
        stale_pid = 99999999  # Very high PID unlikely to exist
        self.pid_file.write_text(str(stale_pid))

        # New lock should succeed after detecting stale lock
        lock = PIDLock(self.pid_file)
        lock.acquire()  # Should not raise, should clean up stale lock

        # Verify our PID is now in the file
        assert self.pid_file.read_text().strip() == str(os.getpid())

        lock.release()

    def test_lock_context_manager(self):
        """
        RED: PIDLock should support context manager protocol for safe usage.

        Expected behavior:
        - Lock acquired on __enter__
        - Lock released on __exit__ (even on exception)
        """
        from src.automation.pid_lock import PIDLock

        with PIDLock(self.pid_file) as lock:
            assert self.pid_file.exists()
            assert self.pid_file.read_text().strip() == str(os.getpid())

        # After context, lock should be released
        assert not self.pid_file.exists()

    def test_lock_is_process_running(self):
        """
        RED: PIDLock should be able to check if locked process is still running.

        Expected behavior:
        - is_process_running() returns True for active process
        - is_process_running() returns False for dead process
        """
        from src.automation.pid_lock import PIDLock

        lock = PIDLock(self.pid_file)

        # Write our own PID - should be running
        self.pid_file.write_text(str(os.getpid()))
        assert lock.is_process_running() is True

        # Write non-existent PID - should not be running
        self.pid_file.write_text("99999999")
        assert lock.is_process_running() is False

        # Clean up
        self.pid_file.unlink()


class TestDaemonIntegrationWithPIDLock:
    """Integration tests for daemon with PID locking."""

    def setup_method(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.pid_file = Path(self.temp_dir) / "daemon.pid"

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_daemon_start_creates_pid_file(self):
        """
        RED: AutomationDaemon.start() should create PID file.

        This tests the integration of PIDLock with the daemon start method.
        """
        from src.automation.daemon import AutomationDaemon
        from src.automation.config import DaemonConfig

        # Create daemon with PID file configuration
        config = DaemonConfig()
        config.pid_file = str(self.pid_file)

        daemon = AutomationDaemon(config=config)
        daemon.start()

        try:
            # PID file should exist
            assert self.pid_file.exists(), "Daemon should create PID file on start"

            # PID file should contain our process ID
            pid_content = self.pid_file.read_text().strip()
            assert pid_content.isdigit(), "PID file should contain numeric PID"
        finally:
            daemon.stop()

    def test_daemon_stop_removes_pid_file(self):
        """
        RED: AutomationDaemon.stop() should remove PID file.
        """
        from src.automation.daemon import AutomationDaemon
        from src.automation.config import DaemonConfig

        config = DaemonConfig()
        config.pid_file = str(self.pid_file)

        daemon = AutomationDaemon(config=config)
        daemon.start()
        daemon.stop()

        assert not self.pid_file.exists(), "Daemon should remove PID file on stop"

    def test_second_daemon_fails_to_start(self):
        """
        RED: Second daemon instance should fail to start with clear error.
        """
        from src.automation.daemon import AutomationDaemon, DaemonError
        from src.automation.config import DaemonConfig

        config = DaemonConfig()
        config.pid_file = str(self.pid_file)

        daemon1 = AutomationDaemon(config=config)
        daemon1.start()

        try:
            daemon2 = AutomationDaemon(config=config)
            with pytest.raises(DaemonError) as exc_info:
                daemon2.start()

            assert "already running" in str(exc_info.value).lower()
        finally:
            daemon1.stop()
