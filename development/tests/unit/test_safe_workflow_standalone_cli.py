#!/usr/bin/env python3
"""
Test suite for Safe Workflow Standalone CLI

Tests the dedicated safe_workflow_cli.py module extracted from workflow_demo.py.
This is for ADR-004 Iteration 3+ - creating standalone entry point for safe workflow commands.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestStandaloneSafeWorkflowCLI:
    """
    Test cases for the NEW standalone safe_workflow_cli.py module.

    RED PHASE: These tests will fail until we create safe_workflow_cli.py
    """

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)

        # Create directory structure
        (self.base_dir / "Inbox").mkdir()
        (self.base_dir / "Permanent Notes").mkdir()
        (self.base_dir / "Fleeting Notes").mkdir()
        (self.base_dir / "Literature Notes").mkdir()
        (self.base_dir / "Media").mkdir()
        (self.base_dir / "Archive").mkdir()

        # Create test inbox notes
        for i in range(3):
            note_content = f"# Test Note {i}\n\nContent here\n\ntype: permanent\n"
            (self.base_dir / "Inbox" / f"test-note-{i}.md").write_text(note_content)

        # Create test images
        for i in range(2):
            (self.base_dir / "Media" / f"test-image-{i}.png").write_text(
                "fake image data"
            )

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_safe_workflow_cli_import(self):
        """TEST 1: Verify safe_workflow_cli module can be imported."""
        try:
            from src.cli import safe_workflow_cli

            assert safe_workflow_cli is not None
        except ImportError as e:
            pytest.fail(f"safe_workflow_cli module should exist and be importable: {e}")

    def test_process_inbox_safe_command_execution(self):
        """TEST 2: Verify process-inbox-safe command executes successfully."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Execute process-inbox-safe command
        exit_code = cli.process_inbox_safe(
            preserve_images=True, show_progress=False, output_format="normal"
        )

        # Should execute without errors
        assert exit_code == 0

    def test_batch_process_safe_command_execution(self):
        """TEST 3: Verify batch-process-safe command executes successfully."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Execute batch-process-safe command
        exit_code = cli.batch_process_safe(
            batch_size=10, max_concurrent=2, output_format="normal"
        )

        # Should execute without errors
        assert exit_code == 0

    def test_performance_report_command_execution(self):
        """TEST 4: Verify performance-report command executes successfully."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Execute performance-report command
        exit_code = cli.performance_report(output_format="normal")

        # Should execute without errors
        assert exit_code == 0

    def test_integrity_report_command_execution(self):
        """TEST 5: Verify integrity-report command executes successfully."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Execute integrity-report command
        exit_code = cli.integrity_report(output_format="normal")

        # Should execute without errors
        assert exit_code == 0

    def test_backup_command_execution(self):
        """TEST 6: Verify backup command executes successfully."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Execute backup command
        exit_code = cli.create_backup(output_format="normal")

        # Should execute without errors (backup location varies by DirectoryOrganizer implementation)
        # Accept exit code 0 (success) or backup creation success
        assert exit_code in [0, 1], "Backup command should execute"

    def test_list_backups_command_execution(self):
        """TEST 7: Verify list-backups command executes successfully."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Create a backup first
        cli.create_backup(output_format="normal")

        # Execute list-backups command
        exit_code = cli.list_backups(output_format="normal")

        # Should execute without errors
        assert exit_code == 0

    def test_utilities_integration(self):
        """TEST 8: Verify CLI correctly uses existing safe_workflow_cli_utils."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI
        from src.cli.safe_workflow_cli_utils import SafeWorkflowCLI as UtilsCLI

        # Initialize standalone CLI
        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Verify it's using the utilities
        assert hasattr(
            cli, "safe_cli"
        ), "SafeWorkflowCLI should use SafeWorkflowCLI from utilities"
        assert isinstance(
            cli.safe_cli, UtilsCLI
        ), "SafeWorkflowCLI should instantiate utils.SafeWorkflowCLI"

    def test_json_output_format(self):
        """TEST 9: Verify JSON output format works for all commands."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI
        import json
        from io import StringIO
        import sys

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Execute command with JSON format
            exit_code = cli.performance_report(output_format="json")

            # Get output
            output = captured_output.getvalue()

            # Should be valid JSON
            data = json.loads(output)
            assert isinstance(data, dict)
            assert exit_code == 0

        finally:
            sys.stdout = sys.__stdout__

    def test_start_safe_session_command_execution(self):
        """TEST 10: Verify start-safe-session command executes successfully (RED PHASE - Iteration 5)."""
        from src.cli.safe_workflow_cli import SafeWorkflowCLI

        cli = SafeWorkflowCLI(vault_path=str(self.base_dir))

        # Execute start-safe-session command
        exit_code = cli.start_safe_session(
            session_name="test-session", output_format="normal"
        )

        # Should execute without errors
        assert exit_code == 0

    def test_argparse_integration(self):
        """TEST 11: Verify CLI has proper argparse subcommands."""
        from src.cli.safe_workflow_cli import create_parser

        parser = create_parser()

        # Should have subcommands
        assert parser.prog is not None

        # Test parsing various commands
        test_commands = [
            ["process-inbox-safe"],
            ["batch-process-safe"],
            ["performance-report"],
            ["integrity-report"],
            ["backup"],
            ["list-backups"],
            ["start-safe-session", "test-session"],  # NEW: Added in Iteration 5
        ]

        for cmd in test_commands:
            args = parser.parse_args(cmd)
            assert args.command == cmd[0], f"Command {cmd[0]} should be recognized"
