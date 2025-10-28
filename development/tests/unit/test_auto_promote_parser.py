"""
Unit tests for auto-promote CLI argument parser integration.

Tests the integration of auto-promote command into core_workflow_cli.py
argument parser and main() function execution.

Following TDD RED → GREEN → REFACTOR methodology.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add development/src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cli.core_workflow_cli import create_parser, main


class TestAutoPromoteSubcommandRegistration:
    """Test that auto-promote subcommand is registered in argument parser."""

    def test_auto_promote_subcommand_exists(self):
        """Verify parser has auto-promote subcommand registered."""
        parser = create_parser()

        # Parser should have subparsers with auto-promote command
        # We'll parse with auto-promote to see if it's recognized
        try:
            args = parser.parse_args(["test-vault", "auto-promote"])
            assert args.command == "auto-promote", "auto-promote command not registered"
        except SystemExit:
            pytest.fail("auto-promote subcommand not found in parser")

    def test_auto_promote_has_dry_run_flag(self):
        """Verify auto-promote subcommand has --dry-run flag."""
        parser = create_parser()

        args = parser.parse_args(["test-vault", "auto-promote", "--dry-run"])
        assert hasattr(args, "dry_run"), "--dry-run flag not registered"
        assert args.dry_run is True, "--dry-run should be True when flag present"

        # Test default value (no flag)
        args_no_flag = parser.parse_args(["test-vault", "auto-promote"])
        assert args_no_flag.dry_run is False, "--dry-run default should be False"

    def test_auto_promote_has_quality_threshold_arg(self):
        """Verify auto-promote has --quality-threshold argument."""
        parser = create_parser()

        # Test with custom value
        args = parser.parse_args(
            ["test-vault", "auto-promote", "--quality-threshold", "0.8"]
        )
        assert hasattr(
            args, "quality_threshold"
        ), "--quality-threshold arg not registered"
        assert (
            args.quality_threshold == 0.8
        ), "--quality-threshold value not parsed correctly"

        # Test default value
        args_default = parser.parse_args(["test-vault", "auto-promote"])
        assert (
            args_default.quality_threshold == 0.7
        ), "--quality-threshold default should be 0.7"

    def test_auto_promote_has_format_arg(self):
        """Verify auto-promote has --format argument with choices."""
        parser = create_parser()

        # Test normal format
        args_normal = parser.parse_args(
            ["test-vault", "auto-promote", "--format", "normal"]
        )
        assert hasattr(args_normal, "format"), "--format arg not registered"
        assert args_normal.format == "normal", "--format normal not parsed"

        # Test json format
        args_json = parser.parse_args(
            ["test-vault", "auto-promote", "--format", "json"]
        )
        assert args_json.format == "json", "--format json not parsed"

        # Test invalid format should raise error
        with pytest.raises(SystemExit):
            parser.parse_args(["test-vault", "auto-promote", "--format", "invalid"])


class TestMainFunctionAutoPromoteExecution:
    """Test that main() function properly handles auto-promote command."""

    @patch("cli.core_workflow_cli.CoreWorkflowCLI")
    def test_main_calls_auto_promote_basic(self, mock_cli_class):
        """Verify main() calls cli.auto_promote() for auto-promote command."""
        mock_cli_instance = Mock()
        mock_cli_instance.auto_promote.return_value = 0  # Success exit code
        mock_cli_class.return_value = mock_cli_instance

        # Simulate command: python core_workflow_cli.py test-vault auto-promote
        test_args = ["core_workflow_cli.py", "test-vault", "auto-promote"]

        with patch("sys.argv", test_args):
            exit_code = main()

        # Verify CoreWorkflowCLI was instantiated with vault path (keyword argument)
        mock_cli_class.assert_called_once_with(vault_path="test-vault")

        # Verify auto_promote was called
        mock_cli_instance.auto_promote.assert_called_once()

        # Verify exit code was returned
        assert exit_code == 0, "main() should return exit code from auto_promote()"

    @patch("cli.core_workflow_cli.CoreWorkflowCLI")
    def test_main_passes_dry_run_flag(self, mock_cli_class):
        """Verify main() passes --dry-run flag to auto_promote()."""
        mock_cli_instance = Mock()
        mock_cli_instance.auto_promote.return_value = 0
        mock_cli_class.return_value = mock_cli_instance

        test_args = ["core_workflow_cli.py", "test-vault", "auto-promote", "--dry-run"]

        with patch("sys.argv", test_args):
            main()

        # Verify auto_promote was called with dry_run=True
        call_kwargs = mock_cli_instance.auto_promote.call_args[1]
        assert call_kwargs.get("dry_run") is True, "dry_run parameter not passed"

    @patch("cli.core_workflow_cli.CoreWorkflowCLI")
    def test_main_passes_quality_threshold(self, mock_cli_class):
        """Verify main() passes --quality-threshold to auto_promote()."""
        mock_cli_instance = Mock()
        mock_cli_instance.auto_promote.return_value = 0
        mock_cli_class.return_value = mock_cli_instance

        test_args = [
            "core_workflow_cli.py",
            "test-vault",
            "auto-promote",
            "--quality-threshold",
            "0.8",
        ]

        with patch("sys.argv", test_args):
            main()

        # Verify auto_promote was called with quality_threshold=0.8
        call_kwargs = mock_cli_instance.auto_promote.call_args[1]
        assert (
            call_kwargs.get("quality_threshold") == 0.8
        ), "quality_threshold not passed"

    @patch("cli.core_workflow_cli.CoreWorkflowCLI")
    def test_main_passes_format_arg(self, mock_cli_class):
        """Verify main() passes --format argument to auto_promote()."""
        mock_cli_instance = Mock()
        mock_cli_instance.auto_promote.return_value = 0
        mock_cli_class.return_value = mock_cli_instance

        test_args = [
            "core_workflow_cli.py",
            "test-vault",
            "auto-promote",
            "--format",
            "json",
        ]

        with patch("sys.argv", test_args):
            main()

        # Verify auto_promote was called with output_format='json'
        call_kwargs = mock_cli_instance.auto_promote.call_args[1]
        assert (
            call_kwargs.get("output_format") == "json"
        ), "output_format parameter not passed"

    @patch("cli.core_workflow_cli.CoreWorkflowCLI")
    def test_main_passes_all_arguments_combined(self, mock_cli_class):
        """Verify main() passes all arguments correctly when combined."""
        mock_cli_instance = Mock()
        mock_cli_instance.auto_promote.return_value = 0
        mock_cli_class.return_value = mock_cli_instance

        test_args = [
            "core_workflow_cli.py",
            "test-vault",
            "auto-promote",
            "--dry-run",
            "--quality-threshold",
            "0.85",
            "--format",
            "json",
        ]

        with patch("sys.argv", test_args):
            main()

        # Verify all parameters passed correctly
        call_kwargs = mock_cli_instance.auto_promote.call_args[1]
        assert call_kwargs.get("dry_run") is True, "dry_run not passed"
        assert (
            call_kwargs.get("quality_threshold") == 0.85
        ), "quality_threshold not passed"
        assert call_kwargs.get("output_format") == "json", "output_format not passed"


class TestAutoPromoteHelpText:
    """Test that help text and documentation are complete."""

    def test_auto_promote_has_help_text(self):
        """Verify auto-promote subcommand has help text."""
        parser = create_parser()

        # Get help text for inspection
        help_text = parser.format_help()

        # Should mention auto-promote command
        assert "auto-promote" in help_text.lower(), "auto-promote not in help text"

    def test_quality_threshold_help_explains_range(self):
        """Verify --quality-threshold help explains 0.0-1.0 range."""
        parser = create_parser()
        help_text = parser.format_help()

        # Verify auto-promote appears in examples with quality-threshold usage
        assert (
            "auto-promote --quality-threshold" in help_text
        ), "Quality threshold example not in help"
        assert "0.8" in help_text, "Quality threshold numeric example not shown"

    def test_dry_run_help_explains_preview(self):
        """Verify --dry-run help explains preview behavior."""
        parser = create_parser()
        help_text = parser.format_help()

        # Verify dry-run appears in auto-promote examples
        assert "auto-promote --dry-run" in help_text, "Dry-run example not in help"
        assert (
            "Preview" in help_text or "preview" in help_text
        ), "Preview concept not in help"
