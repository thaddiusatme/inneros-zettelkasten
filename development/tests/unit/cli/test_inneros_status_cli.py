"""TDD tests for inneros-status CLI.

These tests define the behavior of the CLI wrapper that calls the
shared automation health check_all function.

RED Phase Goals (TDD Iteration 1):
- All 3 core daemons displayed in output
- Exit code 0 when all healthy
- Exit code 1 when any daemon is unhealthy
- Machine-parseable but human-readable format
"""

from typing import Any, Dict
import pytest

from src.cli.inneros_status_cli import main

pytestmark = pytest.mark.ci


# =============================================================================
# Test Fixtures: 3-Daemon Configurations
# =============================================================================

CORE_DAEMON_NAMES = ["youtube_watcher", "screenshot_processor", "health_monitor"]


def _three_daemon_all_healthy() -> Dict[str, Any]:
    """All 3 core daemons running and healthy."""
    return {
        "overall_status": "OK",
        "automations": [
            {
                "name": "youtube_watcher",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:00:00",
                "error_message": None,
            },
            {
                "name": "screenshot_processor",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:01:00",
                "error_message": None,
            },
            {
                "name": "health_monitor",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:02:00",
                "error_message": None,
            },
        ],
    }


def _three_daemon_one_unhealthy() -> Dict[str, Any]:
    """2 daemons healthy, 1 daemon unhealthy (screenshot_processor failed)."""
    return {
        "overall_status": "ERROR",
        "automations": [
            {
                "name": "youtube_watcher",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:00:00",
                "error_message": None,
            },
            {
                "name": "screenshot_processor",
                "running": False,
                "last_run_status": "failed",
                "last_run_timestamp": "2025-12-02 15:55:00",
                "error_message": "OneDrive path not accessible",
            },
            {
                "name": "health_monitor",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:02:00",
                "error_message": None,
            },
        ],
    }


def _three_daemon_warning_state() -> Dict[str, Any]:
    """1 daemon not running but last run was successful (warning state)."""
    return {
        "overall_status": "WARNING",
        "automations": [
            {
                "name": "youtube_watcher",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:00:00",
                "error_message": None,
            },
            {
                "name": "screenshot_processor",
                "running": False,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 15:55:00",
                "error_message": None,
            },
            {
                "name": "health_monitor",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-12-02 16:02:00",
                "error_message": None,
            },
        ],
    }


# Legacy fixtures (kept for existing tests)
def _ok_result() -> Dict[str, Any]:
    return {
        "overall_status": "OK",
        "automations": [
            {
                "name": "youtube_watcher",
                "running": True,
                "last_run_status": "success",
                "last_run_timestamp": "2025-10-23 19:05:15",
                "error_message": None,
            }
        ],
    }


def _error_result() -> Dict[str, Any]:
    return {
        "overall_status": "ERROR",
        "automations": [
            {
                "name": "youtube_watcher",
                "running": False,
                "last_run_status": "failed",
                "last_run_timestamp": "2025-10-23 19:10:00",
                "error_message": "Daemon not running",
            }
        ],
    }


def test_inneros_status_exits_zero_when_ok(monkeypatch, capsys) -> None:
    """inneros-status should exit with code 0 when all automations are OK."""

    def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
        return _ok_result()

    monkeypatch.setattr(
        "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
    )

    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Overall status: OK" in captured.out
    assert "youtube_watcher" in captured.out


def test_inneros_status_exits_non_zero_when_error(monkeypatch, capsys) -> None:
    """inneros-status should exit non zero when any automation has errors."""

    def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
        return _error_result()

    monkeypatch.setattr(
        "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
    )

    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert "Overall status: ERROR" in captured.out
    assert "Daemon not running" in captured.out


# =============================================================================
# RED Phase Tests: TDD Iteration 1 - 3-Daemon Output & Exit Codes
# =============================================================================


class TestThreeDaemonOutput:
    """Tests verifying all 3 core daemons are displayed in status output."""

    def test_all_three_daemons_displayed_when_healthy(
        self, monkeypatch, capsys
    ) -> None:
        """Output must include all 3 core daemon names when system is healthy."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_all_healthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        # All 3 daemon names must appear in output
        for daemon_name in CORE_DAEMON_NAMES:
            assert (
                daemon_name in captured.out
            ), f"Daemon '{daemon_name}' not found in output"

        assert exit_code == 0

    def test_all_three_daemons_displayed_when_one_unhealthy(
        self, monkeypatch, capsys
    ) -> None:
        """Output must include all 3 daemon names even when some are unhealthy."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_one_unhealthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        # All 3 daemon names must appear in output
        for daemon_name in CORE_DAEMON_NAMES:
            assert (
                daemon_name in captured.out
            ), f"Daemon '{daemon_name}' not found in output"

        # The specific error message should also be visible
        assert "OneDrive path not accessible" in captured.out
        assert exit_code != 0  # Unhealthy system should return non-zero

    def test_daemon_count_in_output(self, monkeypatch, capsys) -> None:
        """Output should indicate daemon count for quick health assessment."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_all_healthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        main([])
        captured = capsys.readouterr()

        # Should show running/total count (e.g., "3/3 running" or similar)
        assert "3" in captured.out  # At minimum, count should appear


class TestExitCodeSemantics:
    """Tests verifying exit code semantics: 0=healthy, 1=unhealthy."""

    def test_exit_zero_when_all_three_daemons_healthy(
        self, monkeypatch, capsys
    ) -> None:
        """Exit code 0 when all 3 required daemons are running and healthy."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_all_healthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        exit_code = main([])
        assert exit_code == 0, "Should exit 0 when all daemons healthy"

    def test_exit_one_when_any_daemon_failed(self, monkeypatch, capsys) -> None:
        """Exit code 1 when any required daemon has failed."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_one_unhealthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        exit_code = main([])
        assert exit_code == 1, "Should exit 1 when any daemon has errors"

    def test_exit_one_when_warning_state(self, monkeypatch, capsys) -> None:
        """Exit code 1 when system is in WARNING state (daemon stopped but OK)."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_warning_state()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        exit_code = main([])
        # WARNING should also return non-zero for shell script safety
        assert (
            exit_code != 0
        ), "Should exit non-zero when any daemon is in warning state"


class TestMachineParseable:
    """Tests for machine-parseable output format."""

    def test_output_contains_status_indicators(self, monkeypatch, capsys) -> None:
        """Output should contain clear status indicators (running/not running)."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_one_unhealthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        main([])
        captured = capsys.readouterr()

        # Should have recognizable status indicators
        assert "running" in captured.out.lower()
        assert "not running" in captured.out.lower()

    def test_overall_status_line_present(self, monkeypatch, capsys) -> None:
        """Output must have a clear 'Overall status:' line for parsing."""

        def fake_check_all(repo_root=None):  # type: ignore[no-untyped-def]
            return _three_daemon_all_healthy()

        monkeypatch.setattr(
            "src.cli.inneros_status_cli.check_all", fake_check_all, raising=True
        )

        main([])
        captured = capsys.readouterr()

        # Must have exactly one "Overall status:" line with valid status
        lines = captured.out.strip().split("\n")
        overall_lines = [line for line in lines if "Overall status:" in line]
        assert len(overall_lines) == 1, "Should have exactly one 'Overall status:' line"

        # Status must be one of OK, WARNING, ERROR
        overall_line = overall_lines[0]
        assert any(s in overall_line for s in ["OK", "WARNING", "ERROR"])
