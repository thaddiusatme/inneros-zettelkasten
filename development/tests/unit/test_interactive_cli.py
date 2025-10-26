#!/usr/bin/env python3
"""
ADR-004 Iteration 5: Interactive CLI Tests (RED PHASE)

Test suite for interactive_cli.py - dedicated CLI for interactive workflow mode.
Extracts --interactive command and interactive_mode() function from workflow_demo.py.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestInteractiveCLI:
    """
    RED PHASE: Tests for interactive_cli.py (currently failing - module doesn't exist)
    
    Commands to test:
    - interactive: Run interactive workflow management mode
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
        (self.base_dir / "Archive").mkdir()
        (self.base_dir / "Media").mkdir()

        # Create test notes
        (self.base_dir / "Inbox" / "test-note-1.md").write_text("# Test 1\n\ntype: permanent\n")
        (self.base_dir / "Fleeting Notes" / "fleeting-1.md").write_text("# Fleeting 1\n\ntype: fleeting\n")

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_interactive_cli_import(self):
        """TEST 1: Verify interactive_cli module can be imported (RED PHASE)."""
        try:
            from src.cli import interactive_cli
            assert interactive_cli is not None
        except ImportError as e:
            pytest.fail(f"interactive_cli module should exist and be importable: {e}")

    @patch('builtins.input', side_effect=['status', 'quit'])
    def test_interactive_mode_basic_execution(self, mock_input):
        """TEST 2: Verify interactive mode starts and accepts commands."""
        from src.cli.interactive_cli import InteractiveCLI

        cli = InteractiveCLI(vault_path=str(self.base_dir))

        # Run interactive mode (should exit after 'quit' command)
        exit_code = cli.run_interactive()

        # Should execute without errors
        assert exit_code == 0

    @patch('builtins.input', side_effect=['help', 'quit'])
    def test_interactive_help_command(self, mock_input):
        """TEST 3: Verify 'help' command displays available commands."""
        from src.cli.interactive_cli import InteractiveCLI
        from io import StringIO

        cli = InteractiveCLI(vault_path=str(self.base_dir))

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            cli.run_interactive()
            output = captured_output.getvalue()

            # Should show available commands
            assert 'status' in output.lower()
            assert 'inbox' in output.lower()
            assert 'promote' in output.lower()
            assert 'quit' in output.lower()

        finally:
            sys.stdout = sys.__stdout__

    @patch('builtins.input', side_effect=['list inbox', 'quit'])
    def test_interactive_list_command(self, mock_input):
        """TEST 4: Verify 'list' command works for different directories."""
        from src.cli.interactive_cli import InteractiveCLI
        from io import StringIO

        cli = InteractiveCLI(vault_path=str(self.base_dir))

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            cli.run_interactive()
            output = captured_output.getvalue()

            # Should list inbox notes
            assert 'test-note-1.md' in output

        finally:
            sys.stdout = sys.__stdout__

    @patch('builtins.input', side_effect=['invalid-command', 'quit'])
    def test_interactive_invalid_command(self, mock_input):
        """TEST 5: Verify graceful handling of invalid commands."""
        from src.cli.interactive_cli import InteractiveCLI
        from io import StringIO

        cli = InteractiveCLI(vault_path=str(self.base_dir))

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            cli.run_interactive()
            output = captured_output.getvalue()

            # Should show error message
            assert 'unknown' in output.lower() or 'help' in output.lower()

        finally:
            sys.stdout = sys.__stdout__

    @patch('builtins.input', side_effect=[KeyboardInterrupt()])
    def test_interactive_keyboard_interrupt(self, mock_input):
        """TEST 6: Verify Ctrl+C exits gracefully."""
        from src.cli.interactive_cli import InteractiveCLI

        cli = InteractiveCLI(vault_path=str(self.base_dir))

        # Should handle KeyboardInterrupt gracefully
        exit_code = cli.run_interactive()
        assert exit_code == 0

    def test_workflow_manager_integration(self):
        """TEST 7: Verify CLI uses WorkflowManager for operations."""
        from src.cli.interactive_cli import InteractiveCLI
        from src.ai.workflow_manager import WorkflowManager

        cli = InteractiveCLI(vault_path=str(self.base_dir))

        # Verify it's using WorkflowManager
        assert hasattr(cli, 'workflow'), \
            "InteractiveCLI should have WorkflowManager instance"
        assert isinstance(cli.workflow, WorkflowManager), \
            "InteractiveCLI should use WorkflowManager for operations"

    def test_argparse_integration(self):
        """TEST 8: Verify CLI has proper argparse structure."""
        from src.cli.interactive_cli import create_parser

        parser = create_parser()

        # Should have program name
        assert parser.prog is not None

        # Test parsing interactive command
        args = parser.parse_args(['interactive'])
        assert args.command == 'interactive'
