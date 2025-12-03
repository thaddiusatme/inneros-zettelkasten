"""TDD tests for inneros-up CLI.

These tests define the behavior of the CLI that starts the automation daemon.

RED Phase Goals (TDD Iteration 2):
- Daemon starts successfully → exit code 0
- Idempotent: running twice is safe → exit code 0 (not error)
- Startup validation: daemon actually running after start
- Clear error messages on failure → exit code 1
- Integration with make up/status cycle

Following patterns from inneros_status_cli tests (TDD Iteration 1).
"""

from typing import Any, Dict


# =============================================================================
# Test Fixtures: Daemon Start Results
# =============================================================================


def _successful_start_result() -> Dict[str, Any]:
    """Daemon started successfully."""
    return {
        "success": True,
        "message": "Daemon started successfully",
        "pid": 12345,
    }


def _already_running_result() -> Dict[str, Any]:
    """Daemon already running (idempotent case)."""
    return {
        "success": True,
        "already_running": True,
        "message": "Daemon already running with PID 12345",
        "pid": 12345,
    }


def _start_failed_result() -> Dict[str, Any]:
    """Daemon failed to start."""
    return {
        "success": False,
        "message": "Failed to start daemon: Script not found",
        "error": "FileNotFoundError",
    }


def _validation_failed_result() -> Dict[str, Any]:
    """Daemon started but validation failed (crashed immediately)."""
    return {
        "success": False,
        "message": "Daemon started but failed validation - not running after startup",
        "pid": 12345,
        "validation_error": "Process exited immediately",
    }


# =============================================================================
# RED Phase Tests: TDD Iteration 2 - inneros-up CLI
# =============================================================================


class TestDaemonStartupSuccess:
    """Tests for successful daemon startup."""

    def test_exit_zero_on_successful_start(self, monkeypatch, capsys) -> None:
        """inneros-up should exit 0 when daemon starts successfully."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _successful_start_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "started" in captured.out.lower() or "running" in captured.out.lower()

    def test_output_shows_pid_on_success(self, monkeypatch, capsys) -> None:
        """Output should include PID when daemon starts."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _successful_start_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        main([])
        captured = capsys.readouterr()

        # PID should be visible for debugging/verification
        assert "12345" in captured.out or "pid" in captured.out.lower()


class TestIdempotentBehavior:
    """Tests for idempotent startup (running twice is safe)."""

    def test_exit_zero_when_already_running(self, monkeypatch, capsys) -> None:
        """inneros-up should exit 0 even if daemon already running."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _already_running_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        # Idempotent: already running is SUCCESS, not error
        assert exit_code == 0
        assert "already running" in captured.out.lower()

    def test_no_duplicate_processes_started(self, monkeypatch, capsys) -> None:
        """Running twice should not spawn duplicate daemon processes."""
        from src.cli.inneros_up_cli import main

        call_count = 0

        def fake_start_daemon():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _successful_start_result()
            else:
                return _already_running_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        # First call starts daemon
        exit_code_1 = main([])
        # Second call detects already running
        exit_code_2 = main([])

        assert exit_code_1 == 0
        assert exit_code_2 == 0  # Still success, no error


class TestStartupValidation:
    """Tests for post-startup validation."""

    def test_validates_daemon_actually_running(self, monkeypatch, capsys) -> None:
        """Should validate daemon is actually running after start."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _validation_failed_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        # Validation failure should return non-zero
        assert exit_code != 0
        assert "validation" in captured.out.lower() or "failed" in captured.out.lower()


class TestErrorHandling:
    """Tests for error handling during startup."""

    def test_exit_non_zero_on_failure(self, monkeypatch, capsys) -> None:
        """inneros-up should exit non-zero when startup fails."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _start_failed_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        assert exit_code != 0
        assert "failed" in captured.out.lower() or "error" in captured.out.lower()

    def test_error_message_is_actionable(self, monkeypatch, capsys) -> None:
        """Error messages should help user diagnose the problem."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _start_failed_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        main([])
        captured = capsys.readouterr()

        # Should include specific error info
        assert "Script not found" in captured.out or "script" in captured.out.lower()

    def test_exception_handling(self, monkeypatch, capsys) -> None:
        """Should handle unexpected exceptions gracefully."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            raise RuntimeError("Unexpected error during startup")

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        exit_code = main([])
        captured = capsys.readouterr()

        assert exit_code != 0
        assert "error" in captured.out.lower()


class TestMakeIntegration:
    """Tests for make up/status integration."""

    def test_output_format_matches_make_expectations(self, monkeypatch, capsys) -> None:
        """Output should be suitable for make target display."""
        from src.cli.inneros_up_cli import main

        def fake_start_daemon():
            return _successful_start_result()

        monkeypatch.setattr(
            "src.cli.inneros_up_cli.start_daemon", fake_start_daemon, raising=True
        )

        main([])
        captured = capsys.readouterr()

        # Should have a clear status line for make output
        output = captured.out
        # At least one meaningful line of output
        assert len(output.strip()) > 0
        # Should indicate success clearly
        assert any(word in output.lower() for word in ["started", "running", "success"])
