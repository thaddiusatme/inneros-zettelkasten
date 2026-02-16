"""
Tests for Issue #20: inneros status subcommand with --automation flag.

RED Phase: Verify the inneros wrapper accepts `status` and `status --automation`.
"""

import subprocess
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class TestInnerosStatusSubcommand:
    """inneros status should show basic system status."""

    def test_status_subcommand_exists(self):
        """inneros status should be a recognized subcommand."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "inneros"), "status", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        assert result.returncode == 0, f"status --help failed: {result.stderr}"
        assert (
            "automation" in result.stdout.lower()
        ), "status --help should mention --automation flag"

    def test_status_default_shows_summary(self):
        """inneros status (no flags) should show a compact summary."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "inneros"), "status"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env={
                **__import__("os").environ,
                "PYTHONPATH": str(PROJECT_ROOT / "development"),
            },
            timeout=15,
        )
        # Should succeed or soft-fail (exit 0 or 1 based on health)
        assert result.returncode in (
            0,
            1,
        ), f"Unexpected exit code: {result.returncode}\n{result.stderr}"
        assert (
            "status" in result.stdout.lower() or "daemon" in result.stdout.lower()
        ), f"Expected status output, got: {result.stdout[:200]}"


class TestInnerosStatusAutomation:
    """inneros status --automation should show detailed daemon health."""

    def test_automation_flag_accepted(self):
        """inneros status --automation should be a valid flag."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "inneros"), "status", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        assert (
            "--automation" in result.stdout
        ), "status --help should list --automation flag"

    def test_automation_shows_daemon_details(self):
        """inneros status --automation should show per-daemon status."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "inneros"), "status", "--automation"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env={
                **__import__("os").environ,
                "PYTHONPATH": str(PROJECT_ROOT / "development"),
            },
            timeout=15,
        )
        assert result.returncode in (0, 1)
        output = result.stdout.lower()
        # Should show daemon names from registry
        assert (
            "daemon" in output or "automation" in output
        ), f"Expected daemon/automation info, got: {result.stdout[:300]}"

    def test_automation_json_format(self):
        """inneros status --automation --format json should return JSON."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "inneros"),
                "status",
                "--automation",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env={
                **__import__("os").environ,
                "PYTHONPATH": str(PROJECT_ROOT / "development"),
            },
            timeout=15,
        )
        assert result.returncode in (0, 1)
        import json

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON output, got: {result.stdout[:300]}")
        assert "overall_status" in data, "JSON should include overall_status"
        assert "automations" in data, "JSON should include automations list"
