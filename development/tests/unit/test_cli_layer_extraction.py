#!/usr/bin/env python3
"""
TDD Tests for Issue #39: CLI Layer Extraction

RED Phase Tests - These tests define the expected CLI surface for automation scripts.
The goal is to replace workflow_demo.py usage with dedicated CLIs.

Test Categories:
1. backup_cli.py - Add 'backup' command (create backup)
2. screenshot_cli.py - Add CLI entry point for evening screenshots
3. Automation script compatibility - Verify scripts can use new CLIs

Following ADR-004 CLI Layer Extraction direction.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestBackupCLICreateCommand:
    """Tests for backup_cli.py 'backup' command (create backup).

    Currently backup_cli.py only has 'prune-backups'.
    Automation scripts need 'backup' command to create timestamped backups.
    """

    def test_backup_cli_has_backup_subcommand(self):
        """backup_cli.py should have a 'backup' subcommand for creating backups."""
        from src.cli.backup_cli import create_parser

        parser = create_parser()
        # Get subparsers
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert subparsers_action is not None, "Parser should have subcommands"

        # Check that 'backup' subcommand exists
        choices = subparsers_action.choices
        assert "backup" in choices, (
            "backup_cli.py should have 'backup' subcommand for creating backups. "
            "Currently only has: " + ", ".join(choices.keys())
        )

    def test_backup_command_creates_timestamped_backup(self, tmp_path):
        """The 'backup' command should create a timestamped backup directory."""
        from src.cli.backup_cli import BackupCLI

        # Setup test vault
        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()
        (vault_path / "test_note.md").write_text("# Test Note\nContent here.")

        cli = BackupCLI(vault_path=str(vault_path))

        # The backup method should exist and return success
        assert hasattr(cli, "backup"), "BackupCLI should have 'backup' method"

        result = cli.backup(output_format="json")
        assert result == 0, "backup command should return 0 on success"

    def test_backup_command_returns_backup_path(self, tmp_path):
        """The 'backup' command should return the created backup path."""
        from src.cli.backup_cli import BackupCLI
        import json
        from io import StringIO

        # Setup test vault
        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()
        (vault_path / "test_note.md").write_text("# Test Note")

        cli = BackupCLI(vault_path=str(vault_path))

        # Capture output
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            exit_code = cli.backup(output_format="json")

        assert exit_code == 0, "backup should return 0 on success"
        output = mock_stdout.getvalue()
        # Should be valid JSON with backup_path
        backup_result = json.loads(output)
        assert "backup_path" in backup_result, "JSON output should include backup_path"


class TestScreenshotCLI:
    """Tests for screenshot CLI entry point.

    evening_screenshot_processor.py has the class but no CLI main().
    Automation scripts need a CLI entry point for --evening-screenshots.
    """

    def test_screenshot_cli_module_exists(self):
        """A dedicated screenshot CLI module should exist."""
        try:
            from src.cli import screenshot_cli

            assert hasattr(
                screenshot_cli, "main"
            ), "screenshot_cli should have main() function"
        except ImportError:
            pytest.fail(
                "screenshot_cli.py module should exist for evening screenshot automation. "
                "evening_screenshot_processor.py has the class but no CLI entry point."
            )

    def test_screenshot_cli_has_process_command(self):
        """screenshot_cli should have a command to process evening screenshots."""
        from src.cli.screenshot_cli import create_parser

        parser = create_parser()

        # Check for 'process' subcommand
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert subparsers_action is not None, "Parser should have subcommands"
        assert (
            "process" in subparsers_action.choices
        ), "screenshot_cli should have 'process' subcommand"

    def test_screenshot_cli_supports_dry_run(self):
        """screenshot_cli should support --dry-run for safe preview."""
        from src.cli.screenshot_cli import create_parser

        parser = create_parser()

        # Get 'process' subparser and check its options
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert subparsers_action is not None, "Parser should have subcommands"
        process_parser = subparsers_action.choices.get("process")
        assert process_parser is not None, "Should have 'process' subcommand"

        # Check for --dry-run in process subparser
        option_strings = []
        for action in process_parser._actions:
            if hasattr(action, "option_strings"):
                option_strings.extend(action.option_strings)

        assert (
            "--dry-run" in option_strings
        ), f"screenshot_cli process should support --dry-run. Found: {option_strings}"

    def test_screenshot_cli_supports_progress_flag(self):
        """screenshot_cli should support --progress for automation logging."""
        from src.cli.screenshot_cli import create_parser

        parser = create_parser()

        # Get 'process' subparser and check its options
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert subparsers_action is not None, "Parser should have subcommands"
        process_parser = subparsers_action.choices.get("process")
        assert process_parser is not None, "Should have 'process' subcommand"

        # Check for --progress in process subparser
        option_strings = []
        for action in process_parser._actions:
            if hasattr(action, "option_strings"):
                option_strings.extend(action.option_strings)

        assert (
            "--progress" in option_strings
        ), f"screenshot_cli process should support --progress. Found: {option_strings}"

    def test_screenshot_cli_returns_proper_exit_codes(self, tmp_path):
        """screenshot_cli should return proper exit codes for automation."""
        from src.cli.screenshot_cli import ScreenshotCLI

        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()

        cli = ScreenshotCLI(vault_path=str(vault_path))

        # Should return 0 on success (even with no screenshots to process)
        result = cli.process_evening_screenshots(dry_run=True)
        assert isinstance(result, int), "CLI should return integer exit code"
        assert result in [0, 1], "Exit code should be 0 (success) or 1 (error)"


class TestAutomationScriptCompatibility:
    """Tests to verify automation scripts can use the new dedicated CLIs.

    These tests verify the CLI surface matches what automation scripts need.
    """

    def test_core_workflow_cli_has_status_command(self):
        """core_workflow_cli.py should have 'status' command for health checks."""
        from src.cli.core_workflow_cli import create_parser

        parser = create_parser()
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert subparsers_action is not None
        assert (
            "status" in subparsers_action.choices
        ), "core_workflow_cli should have 'status' subcommand"

    def test_core_workflow_cli_has_process_inbox_command(self):
        """core_workflow_cli.py should have 'process-inbox' command."""
        from src.cli.core_workflow_cli import create_parser

        parser = create_parser()
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert (
            "process-inbox" in subparsers_action.choices
        ), "core_workflow_cli should have 'process-inbox' subcommand"

    def test_fleeting_cli_has_triage_command(self):
        """fleeting_cli.py should have 'fleeting-triage' command."""
        from src.cli.fleeting_cli import create_parser

        parser = create_parser()
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert (
            "fleeting-triage" in subparsers_action.choices
        ), "fleeting_cli should have 'fleeting-triage' subcommand"

    def test_weekly_review_cli_has_enhanced_metrics_command(self):
        """weekly_review_cli.py should have 'enhanced-metrics' command."""
        from src.cli.weekly_review_cli import create_parser

        parser = create_parser()
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, "_parser_class"):
                subparsers_action = action
                break

        assert (
            "enhanced-metrics" in subparsers_action.choices
        ), "weekly_review_cli should have 'enhanced-metrics' subcommand"

    def test_connections_demo_can_be_imported(self):
        """connections_demo.py should be importable for suggest-links."""
        try:
            from src.cli import connections_demo

            assert hasattr(connections_demo, "main") or hasattr(
                connections_demo, "handle_suggest_links_command"
            )
        except ImportError as e:
            pytest.fail(f"connections_demo should be importable: {e}")


class TestCLIExitCodeContract:
    """Tests to verify CLIs follow exit code contract for automation.

    Exit codes:
    - 0: Success
    - 1: Error/failure
    - 130: User cancelled (Ctrl+C)
    """

    def test_backup_cli_exit_code_success(self, tmp_path):
        """backup_cli should return 0 on success."""
        from src.cli.backup_cli import BackupCLI

        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()
        (vault_path / "note.md").write_text("# Test")

        cli = BackupCLI(vault_path=str(vault_path))
        result = cli.backup()
        assert result == 0, "Should return 0 on success"

    def test_core_workflow_cli_exit_code_success(self, tmp_path):
        """core_workflow_cli should return 0 on success."""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = CoreWorkflowCLI(vault_path=str(vault_path))
        result = cli.status()
        assert result == 0, "Should return 0 on success"


class TestCLIJSONOutputContract:
    """Tests to verify CLIs support JSON output for automation parsing."""

    def test_backup_cli_supports_json_output(self, tmp_path):
        """backup_cli backup command should support --format json."""
        from src.cli.backup_cli import BackupCLI

        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()
        (vault_path / "note.md").write_text("# Test")

        cli = BackupCLI(vault_path=str(vault_path))

        # Should accept output_format parameter
        assert hasattr(cli, "backup")
        import inspect

        sig = inspect.signature(cli.backup)
        params = list(sig.parameters.keys())
        assert (
            "output_format" in params
        ), "backup method should accept output_format parameter"

    def test_screenshot_cli_supports_json_output(self, tmp_path):
        """screenshot_cli should support --format json."""
        from src.cli.screenshot_cli import ScreenshotCLI

        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()

        cli = ScreenshotCLI(vault_path=str(vault_path))

        # Should accept output_format parameter
        import inspect

        sig = inspect.signature(cli.process_evening_screenshots)
        params = list(sig.parameters.keys())
        assert (
            "output_format" in params
        ), "process_evening_screenshots should accept output_format parameter"
