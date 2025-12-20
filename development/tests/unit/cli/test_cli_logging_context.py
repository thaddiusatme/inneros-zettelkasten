#!/usr/bin/env python3
"""
Unit Tests for CLI Logging Context Standardization

Issue #39 P1: Standardize CLI logging context across dedicated CLIs.
This module tests the shared logging context helper that provides
consistent startup logging for all CLI tools.

Requirements:
1. Log CLI name, subcommand, vault path, and mode flags
2. Logs go to stderr (not stdout) to avoid JSON contamination
3. Consistent format: key=value pairs for machine parseability

TDD RED Phase: These tests define the expected behavior before implementation.
"""

import io
import logging
import sys
from pathlib import Path
import pytest

# Import will fail until implementation exists (RED phase)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestCLILoggingContextHelper:
    """Tests for the shared CLI logging context helper."""

    def test_cli_logging_context_helper_exists(self):
        """The cli_logging module should exist with log_cli_context function."""
        from src.cli.cli_logging import log_cli_context

        assert callable(log_cli_context), "log_cli_context should be callable"

    def test_log_cli_context_logs_required_fields(self):
        """log_cli_context should log cli_name, subcommand, vault_path."""
        from src.cli.cli_logging import log_cli_context

        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)

        test_logger = logging.getLogger("test_cli_context")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)

        log_cli_context(
            logger=test_logger,
            cli_name="backup_cli",
            subcommand="backup",
            vault_path="/path/to/vault",
        )

        log_output = log_stream.getvalue()
        assert "cli=backup_cli" in log_output, "Should log cli name"
        assert "subcommand=backup" in log_output, "Should log subcommand"
        assert "vault=/path/to/vault" in log_output, "Should log vault path"

    def test_log_cli_context_logs_optional_mode_flags(self):
        """log_cli_context should log optional mode flags like dry_run, format."""
        from src.cli.cli_logging import log_cli_context

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)

        test_logger = logging.getLogger("test_cli_context_modes")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)

        log_cli_context(
            logger=test_logger,
            cli_name="backup_cli",
            subcommand="prune-backups",
            vault_path="/vault",
            dry_run=True,
            output_format="json",
        )

        log_output = log_stream.getvalue()
        assert "dry_run=True" in log_output, "Should log dry_run flag"
        assert "format=json" in log_output, "Should log output format"

    def test_log_cli_context_uses_info_level(self):
        """log_cli_context should use INFO level by default."""
        from src.cli.cli_logging import log_cli_context

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        test_logger = logging.getLogger("test_cli_context_level")
        test_logger.setLevel(logging.DEBUG)
        test_logger.addHandler(handler)

        log_cli_context(
            logger=test_logger,
            cli_name="test_cli",
            subcommand="test",
            vault_path="/vault",
        )

        log_output = log_stream.getvalue()
        assert "INFO" in log_output, "Should log at INFO level"


class TestCLILoggingStderrConfiguration:
    """Tests for CLI logging configuration that sends logs to stderr."""

    def test_configure_cli_logging_exists(self):
        """configure_cli_logging function should exist."""
        from src.cli.cli_logging import configure_cli_logging

        assert callable(configure_cli_logging)

    def test_configure_cli_logging_returns_logger(self):
        """configure_cli_logging should return a configured logger."""
        from src.cli.cli_logging import configure_cli_logging

        logger = configure_cli_logging("test_cli")
        assert isinstance(logger, logging.Logger)

    def test_configure_cli_logging_logs_to_stderr(self):
        """configure_cli_logging should configure logger to use stderr."""
        from src.cli.cli_logging import configure_cli_logging

        # Create a fresh logger
        logger = configure_cli_logging("test_stderr_cli")

        # Check that at least one handler writes to stderr
        stderr_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and h.stream == sys.stderr
        ]
        assert len(stderr_handlers) > 0, "Logger should have stderr handler"


class TestJSONOutputPurity:
    """Tests ensuring JSON output mode doesn't have log contamination."""

    def test_json_mode_stdout_is_valid_json_without_logs(self, tmp_path: Path):
        """In JSON mode, stdout should contain only valid JSON, no log lines."""
        import json
        import subprocess

        # Create minimal vault
        (tmp_path / "Inbox").mkdir()

        cli_path = (
            Path(__file__).parent.parent.parent.parent / "src" / "cli" / "backup_cli.py"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(cli_path),
                "--vault",
                str(tmp_path),
                "backup",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # stdout should be parseable as JSON with no prefix/suffix garbage
        stdout_stripped = result.stdout.strip()
        try:
            parsed = json.loads(stdout_stripped)
            assert isinstance(parsed, dict), "stdout should be a JSON object"
        except json.JSONDecodeError as e:
            pytest.fail(
                f"stdout is not pure JSON (log leakage?): {e}\n"
                f"stdout:\n{result.stdout[:500]}\n"
                f"stderr:\n{result.stderr[:500]}"
            )

    def test_json_mode_logs_appear_in_stderr_not_stdout(self, tmp_path: Path):
        """Logs should appear in stderr when using JSON mode, not stdout."""
        import subprocess

        # Create minimal vault
        (tmp_path / "Inbox").mkdir()

        cli_path = (
            Path(__file__).parent.parent.parent.parent / "src" / "cli" / "backup_cli.py"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(cli_path),
                "--verbose",  # Enable verbose logging
                "--vault",
                str(tmp_path),
                "backup",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # stdout should NOT contain log prefixes like "INFO" or "DEBUG"
        assert "INFO -" not in result.stdout, "INFO logs should not be in stdout"
        assert "DEBUG -" not in result.stdout, "DEBUG logs should not be in stdout"

        # If verbose, stderr SHOULD contain logs
        # (This is optional - implementation may or may not log in verbose mode)


class TestPreCommitMarkerConfiguration:
    """Tests for pre-commit pytest marker configuration."""

    def test_fast_unit_tests_are_selectable(self):
        """Verify that fast unit tests can be selected by the pre-commit hook marker."""
        import subprocess

        dev_dir = Path(__file__).parent.parent.parent.parent

        # The pre-commit uses: -m "ci and not wip and not slow"
        # After fix, it should use: -m "not slow" or just run all unit tests
        # This test verifies SOME tests are selected with the new marker
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "-m",
                "not slow",  # Expected fixed marker
                str(dev_dir / "tests" / "unit"),
            ],
            capture_output=True,
            text=True,
            cwd=dev_dir,
            timeout=60,
        )

        # Should collect at least some tests (not "0 selected")
        assert "0 selected" not in result.stdout, (
            f"Pre-commit marker should select tests.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
