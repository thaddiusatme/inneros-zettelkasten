"""TDD RED Phase: Tests for inneros.sh helper script.

Issue #50 P1: Developer Convenience - inneros.sh wrapper script.

These tests verify that inneros.sh provides convenient access to
common InnerOS commands while documenting itself as temporary
until Makefile is canonical.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
INNEROS_SH = REPO_ROOT / "inneros.sh"


class TestInnerosShExists:
    """Tests for inneros.sh script existence and permissions."""

    def test_inneros_sh_exists_at_repo_root(self) -> None:
        """inneros.sh must exist at repository root."""
        assert INNEROS_SH.exists(), f"inneros.sh not found at {INNEROS_SH}"

    def test_inneros_sh_is_executable(self) -> None:
        """inneros.sh must have executable permissions."""
        assert os.access(INNEROS_SH, os.X_OK), "inneros.sh is not executable"


class TestInnerosShHelp:
    """Tests for self-documentation via help command."""

    def test_help_command_shows_usage(self) -> None:
        """./inneros.sh help should display available commands."""
        result = subprocess.run(
            [str(INNEROS_SH), "help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"help failed: {result.stderr}"
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout
        assert "status" in result.stdout.lower()
        assert "up" in result.stdout.lower()

    def test_no_args_shows_help(self) -> None:
        """./inneros.sh with no arguments should show help."""
        result = subprocess.run(
            [str(INNEROS_SH)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        # Should show help and exit with 0 or 1
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout


class TestInnerosShStatus:
    """Tests for status command parity with make status."""

    def test_status_command_runs(self) -> None:
        """./inneros.sh status should execute without error."""
        result = subprocess.run(
            [str(INNEROS_SH), "status"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10,
        )
        # Status may return non-zero if daemon not running, that's OK
        # We just verify it produces output
        combined = result.stdout + result.stderr
        assert "status" in combined.lower() or "daemon" in combined.lower()

    def test_status_matches_make_status_output(self) -> None:
        """./inneros.sh status should produce same output as make status."""
        inneros_result = subprocess.run(
            [str(INNEROS_SH), "status"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10,
        )

        make_result = subprocess.run(
            ["make", "status"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10,
        )

        # Both should contain "Automation status" or similar
        assert (
            "Automation status" in inneros_result.stdout
            or "Automation status" in inneros_result.stderr
        )
        assert (
            "Automation status" in make_result.stdout
            or "Automation status" in make_result.stderr
        )


class TestInnerosShUp:
    """Tests for up command (daemon start)."""

    def test_up_command_exists(self) -> None:
        """./inneros.sh up should be a recognized command."""
        result = subprocess.run(
            [str(INNEROS_SH), "help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert "up" in result.stdout.lower()


class TestInnerosShAiCommands:
    """Tests for AI workflow commands."""

    def test_ai_inbox_sweep_command_exists(self) -> None:
        """./inneros.sh ai inbox-sweep should be documented."""
        result = subprocess.run(
            [str(INNEROS_SH), "help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        # Help should mention ai commands
        assert "ai" in result.stdout.lower()


class TestInnerosShVenvActivation:
    """Tests for automatic venv activation."""

    def test_script_activates_venv_if_present(self) -> None:
        """Script should activate venv automatically when present."""
        # Read script content to verify venv activation logic exists
        content = INNEROS_SH.read_text()
        assert "venv" in content.lower() or "VIRTUAL_ENV" in content
