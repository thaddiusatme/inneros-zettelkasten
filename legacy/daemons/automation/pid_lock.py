"""
PID File Locking - Prevent duplicate daemon processes

Provides process-level locking using PID files with stale lock detection.
Follows ADR-001: <500 LOC, single responsibility, domain separation.

Issue #51: Daemon reliability - prevent zombie processes through PID file locking.
"""

import os
import fcntl
from pathlib import Path
from typing import Optional


class PIDLockError(Exception):
    """Raised when PID lock cannot be acquired."""

    pass


class PIDLock:
    """
    PID file-based process lock with stale detection.

    Provides mutual exclusion for daemon processes using PID files.
    Automatically detects and cleans up stale locks from dead processes.

    Usage:
        lock = PIDLock(Path("/var/run/daemon.pid"))
        lock.acquire()
        try:
            # daemon work
        finally:
            lock.release()

    Or as context manager:
        with PIDLock(Path("/var/run/daemon.pid")):
            # daemon work
    """

    def __init__(self, pid_file: Path):
        """
        Initialize PID lock.

        Args:
            pid_file: Path to PID file for locking
        """
        self._pid_file = Path(pid_file)
        self._lock_fd: Optional[int] = None
        self._acquired = False

    @property
    def pid_file(self) -> Path:
        """Get PID file path."""
        return self._pid_file

    def acquire(self) -> None:
        """
        Acquire PID lock.

        Creates PID file with exclusive lock. If lock file exists,
        checks if owning process is still running. Cleans up stale locks.

        Raises:
            PIDLockError: If lock cannot be acquired (another daemon running)
        """
        # Check for existing lock
        if self._pid_file.exists():
            if self.is_process_running():
                existing_pid = self._read_pid()
                raise PIDLockError(
                    f"Daemon already running with PID {existing_pid}. "
                    f"Use 'make down' to stop it first."
                )
            else:
                # Stale lock - clean up
                self._pid_file.unlink()

        # Create parent directories if needed
        self._pid_file.parent.mkdir(parents=True, exist_ok=True)

        # Open file for writing with exclusive lock
        try:
            self._lock_fd = os.open(
                str(self._pid_file),
                os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
                0o644,
            )

            # Try to acquire exclusive lock (non-blocking)
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Write our PID
            os.write(self._lock_fd, f"{os.getpid()}\n".encode())
            os.fsync(self._lock_fd)

            self._acquired = True

        except (OSError, IOError) as e:
            if self._lock_fd is not None:
                os.close(self._lock_fd)
                self._lock_fd = None
            raise PIDLockError(f"Failed to acquire PID lock: {e}")

    def release(self) -> None:
        """
        Release PID lock and remove PID file.

        Safe to call multiple times. Does nothing if lock not held.
        """
        if not self._acquired:
            return

        try:
            if self._lock_fd is not None:
                # Release lock
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
                self._lock_fd = None

            # Remove PID file
            if self._pid_file.exists():
                self._pid_file.unlink()

        except (OSError, IOError):
            pass  # Best effort cleanup

        self._acquired = False

    def is_process_running(self) -> bool:
        """
        Check if process in PID file is still running.

        Returns:
            True if PID file exists and process is running, False otherwise
        """
        pid = self._read_pid()
        if pid is None:
            return False

        try:
            # Signal 0 doesn't kill, just checks if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def _read_pid(self) -> Optional[int]:
        """
        Read PID from PID file.

        Returns:
            PID as integer, or None if file doesn't exist or invalid
        """
        try:
            if not self._pid_file.exists():
                return None
            content = self._pid_file.read_text().strip()
            return int(content)
        except (ValueError, OSError):
            return None

    def __enter__(self) -> "PIDLock":
        """Context manager entry - acquire lock."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - release lock."""
        self.release()
