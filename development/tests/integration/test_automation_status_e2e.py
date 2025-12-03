"""Phase 1 Core Automation Status - E2E tests for inneros-status.

These tests validate the end-to-end behavior of the `inneros-status` CLI
and, indirectly, `make status`:

- CLI exit code semantics (0 = healthy, 1 = unhealthy)
- Output includes all daemon names from daemon_registry.yaml
- Integration between CLI wrapper and system_health/daemon registry

Notes:
- These tests do NOT start the real automation daemon.
- Instead, they simulate a running daemon by writing the current test
  process PID into a temporary HOME-scoped PID file.
- HOME is overridden per test so ~/.inneros/daemon.pid is isolated.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


pytestmark = [pytest.mark.e2e]


class TestInnerOSStatusCLI:
    """E2E tests for the inneros-status CLI script.

    These tests call the CLI as a subprocess, mirroring real usage via
    `PYTHONPATH=development python3 development/src/cli/inneros_status_cli.py`.
    """

    @pytest.fixture
    def repo_root(self) -> Path:
        """Repository root (same pattern as other integration tests)."""

        return Path(__file__).parent.parent.parent.parent

    @pytest.fixture
    def env_with_pythonpath_and_home(self, repo_root: Path, tmp_path: Path) -> dict:
        """Base env with PYTHONPATH and an isolated HOME for PID files.

        - PYTHONPATH points at `development` so src imports work.
        - HOME points at a temp directory so ~/.inneros/daemon.pid does not
          touch the real user environment.
        """

        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root / "development")

        home_dir = tmp_path / "home"
        home_dir.mkdir(parents=True, exist_ok=True)
        env["HOME"] = str(home_dir)

        return env

    @pytest.fixture
    def registry_daemon_names(self, repo_root: Path) -> list[str]:
        """Daemon names from the real daemon registry.

        This keeps the tests aligned with `.automation/config/daemon_registry.yaml`
        so adding new daemons automatically updates expectations.
        """

        registry_path = repo_root / ".automation" / "config" / "daemon_registry.yaml"
        config = yaml.safe_load(registry_path.read_text()) or {}
        daemons = config.get("daemons", []) or []
        return [d.get("name", "") for d in daemons if d.get("name")]

    def _create_pid_file_for_current_process(self, env: dict) -> Path:
        """Write the current test process PID into ~/.inneros/daemon.pid.

        The CLI process will use this PID file (via Path.home()) to decide
        that the daemon is running.
        """

        home_dir = Path(env["HOME"])
        pid_file = home_dir / ".inneros" / "daemon.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(os.getpid()))
        return pid_file

    def _ensure_success_log_for_first_daemon(self, repo_root: Path) -> None:
        """Create a minimal SUCCESS log entry for the first daemon in the registry.

        This ensures `LogParser.parse_last_run` sees a successful run so
        overall_status can be OK when the PID file indicates a running daemon.
        """

        registry_path = repo_root / ".automation" / "config" / "daemon_registry.yaml"
        config = yaml.safe_load(registry_path.read_text()) or {}
        daemons = config.get("daemons", []) or []
        if not daemons:
            return

        first = daemons[0]
        log_rel = first.get("log_path", ".automation/logs/daemon.log")
        log_path = repo_root / log_rel
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("2025-12-02 16:00:00 - SUCCESS - automation daemon started\n")

    def test_cli_exit_zero_and_lists_daemons_when_healthy(
        self,
        repo_root: Path,
        env_with_pythonpath_and_home: dict,
        registry_daemon_names: list[str],
    ) -> None:
        """inneros-status exits 0 and lists all registry daemons when healthy.

        Healthy == PID file exists and points at a running process, and the
        last log entry is SUCCESS.
        """

        env = dict(env_with_pythonpath_and_home)
        # Simulate running daemon and successful last run
        self._create_pid_file_for_current_process(env)
        self._ensure_success_log_for_first_daemon(repo_root)

        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/inneros_status_cli.py",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
            stdin=subprocess.DEVNULL,
            timeout=15,
        )

        assert result.returncode == 0, (
            f"Expected exit code 0 when daemon is healthy, got {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # Output should show an overall OK line
        assert "Overall status: OK" in result.stdout, (
            f"Expected 'Overall status: OK' in output.\nstdout: {result.stdout}"
        )

        # Output should include all daemon names from the registry
        for name in registry_daemon_names:
            assert name in result.stdout, (
                f"Daemon '{name}' from daemon_registry.yaml should appear in output.\n"
                f"stdout: {result.stdout}"
            )

    def test_cli_exit_one_when_daemon_unhealthy(
        self,
        repo_root: Path,
        env_with_pythonpath_and_home: dict,
        registry_daemon_names: list[str],
    ) -> None:
        """inneros-status exits 1 when daemon is not running.

        Unhealthy == no PID file under the (isolated) HOME directory.
        """

        env = dict(env_with_pythonpath_and_home)
        # Do NOT create a PID file -> detector will report not running

        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/inneros_status_cli.py",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
            stdin=subprocess.DEVNULL,
            timeout=15,
        )

        assert result.returncode == 1, (
            f"Expected exit code 1 when daemon is unhealthy, got {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # Output should still list all known daemons so the user sees coverage
        for name in registry_daemon_names:
            assert name in result.stdout, (
                f"Daemon '{name}' from daemon_registry.yaml should appear in output even when unhealthy.\n"
                f"stdout: {result.stdout}"
            )


class TestMakeStatusTarget:
    """Developer UX tests for the `make status` target.

    These are lighter-weight than the CLI tests: they only assert that the
    Make target succeeds in the healthy path and returns non-zero when
    automation is unhealthy.
    """

    @pytest.fixture
    def repo_root(self) -> Path:
        return Path(__file__).parent.parent.parent.parent

    def test_make_status_exits_non_zero_when_unhealthy(self, repo_root: Path, tmp_path: Path) -> None:
        """`make status` should return a non-zero code when daemon is unhealthy.

        We override HOME so this does not depend on any real ~/.inneros state.
        """

        env = os.environ.copy()
        home_dir = tmp_path / "home-unhealthy"
        home_dir.mkdir(parents=True, exist_ok=True)
        env["HOME"] = str(home_dir)

        result = subprocess.run(
            ["make", "status"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )

        assert result.returncode != 0, (
            "`make status` should fail (non-zero) when daemon is not running.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
