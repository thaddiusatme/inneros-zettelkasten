"""TDD tests for inneros-status CLI.

These tests define the behavior of the CLI wrapper that calls the
shared automation health check_all function.
"""

from typing import Dict, Any

from src.cli.inneros_status_cli import main


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
