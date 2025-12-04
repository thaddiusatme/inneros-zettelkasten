"""Phase 1 Core Automation - E2E tests for inneros-up / make up.

Goal: Verify that `make up` starts the automation daemon and `make status`
reports it as running, using the real daemon/CLI stack.

These tests intentionally mirror the developer experience:
- `make up` to start automation
- `make status` to verify health
- `make down` to stop automation cleanly

Tests run with an isolated HOME so ~/.inneros/daemon.pid does not interfere
with the real user environment.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


# Mark as end-to-end and potentially slow due to daemon startup
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestMakeUpStatusDownCycle:
    """End-to-end test for the make up → make status → make down cycle."""

    @pytest.fixture
    def repo_root(self) -> Path:
        """Repository root (same pattern as other integration tests)."""

        return Path(__file__).parent.parent.parent.parent

    @pytest.fixture
    def env_with_pythonpath_and_home(self, repo_root: Path, tmp_path: Path) -> dict:
        """Environment with PYTHONPATH and isolated HOME for the daemon PID.

        - PYTHONPATH points at `development`.
        - HOME points at a temp directory so ~/.inneros/daemon.pid is test-only.
        """

        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root / "development")

        home_dir = tmp_path / "home-daemon-cycle"
        home_dir.mkdir(parents=True, exist_ok=True)
        env["HOME"] = str(home_dir)

        return env

    def test_make_up_then_status_reports_running_and_make_down_stops(
        self,
        repo_root: Path,
        env_with_pythonpath_and_home: dict,
    ) -> None:
        """`make up` should start the daemon and `make status` should see it.

        After `make down`, status should report the daemon as not running and
        return a non-zero exit code (unhealthy state).
        """

        env = dict(env_with_pythonpath_and_home)

        # Ensure .automation/logs exists at repo root for status/log parsing
        logs_dir = repo_root / ".automation" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Ensure there is no stale PID file in the isolated HOME
        pid_file = Path(env["HOME"]) / ".inneros" / "daemon.pid"
        if pid_file.exists():
            pid_file.unlink()

        # Helper to run make commands with consistent settings
        def _run_make(target: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["make", target],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                env=env,
                stdin=subprocess.DEVNULL,
                timeout=timeout,
            )

        # Start daemon
        up_result = _run_make("up", timeout=60)

        try:
            assert up_result.returncode == 0, (
                "`make up` should exit with code 0 when starting the daemon.\n"
                f"stdout: {up_result.stdout}\n"
                f"stderr: {up_result.stderr}"
            )

            # Verify status reports daemon running and exits with 0
            status_result = _run_make("status", timeout=60)

            assert status_result.returncode == 0, (
                "`make status` should exit with code 0 after successful `make up`.\n"
                f"stdout: {status_result.stdout}\n"
                f"stderr: {status_result.stderr}"
            )

            # Expect summary line to show 1/1 daemon running
            assert "Daemons:" in status_result.stdout, (
                "Status output should include a 'Daemons:' summary line.\n"
                f"stdout: {status_result.stdout}"
            )
            assert "1/1" in status_result.stdout or "1/1 running" in status_result.stdout, (
                "Expected 1/1 running daemon after `make up`.\n"
                f"stdout: {status_result.stdout}"
            )

            # Daemon name from registry should appear
            assert "automation_daemon" in status_result.stdout, (
                "Status output should mention 'automation_daemon' after startup.\n"
                f"stdout: {status_result.stdout}"
            )

            # Now stop the daemon
            down_result = _run_make("down", timeout=60)

            assert down_result.returncode in (0, 1), (
                "`make down` should complete cleanly (0 or 1 if already stopped).\n"
                f"stdout: {down_result.stdout}\n"
                f"stderr: {down_result.stderr}"
            )

            # After down, status should no longer report running and should
            # return non-zero to indicate unhealthy automation.
            status_after_down = _run_make("status", timeout=60)

            assert status_after_down.returncode != 0, (
                "`make status` should return non-zero after `make down` stops the daemon.\n"
                f"stdout: {status_after_down.stdout}\n"
                f"stderr: {status_after_down.stderr}"
            )

            assert "Daemons:" in status_after_down.stdout, (
                "Status output should still include daemon summary after shutdown.\n"
                f"stdout: {status_after_down.stdout}"
            )
            assert "0/1" in status_after_down.stdout or "0/1 running" in status_after_down.stdout, (
                "Expected 0/1 running daemon after `make down`.\n"
                f"stdout: {status_after_down.stdout}"
            )

        finally:
            # Best-effort cleanup: ensure daemon is not left running
            try:
                _run_make("down", timeout=30)
            except Exception:
                # Ignore cleanup failures – main assertions already captured
                pass
