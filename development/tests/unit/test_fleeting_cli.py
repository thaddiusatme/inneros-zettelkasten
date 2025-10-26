#!/usr/bin/env python3
"""
Test suite for Fleeting Notes CLI

Tests the dedicated fleeting_cli.py module extracted from workflow_demo.py.
Includes Bug #3 fix validation (AttributeError in fleeting_health).
"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestDedicatedFleetingCLI:
    """
    Test cases for the NEW dedicated fleeting_cli.py module.
    
    RED PHASE: These tests will fail until we create fleeting_cli.py
    """

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)

        # Create directory structure
        (self.base_dir / "Fleeting Notes").mkdir()
        (self.base_dir / "Permanent Notes").mkdir()
        (self.base_dir / "Literature Notes").mkdir()
        (self.base_dir / "Archive").mkdir()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_fleeting_cli_import(self):
        """TEST 1: Verify fleeting_cli module can be imported."""
        try:
            from src.cli import fleeting_cli
            assert fleeting_cli is not None
        except ImportError as e:
            pytest.fail(f"fleeting_cli module should exist and be importable: {e}")

    def test_fleeting_health_command_execution(self):
        """TEST 2: Verify fleeting-health command executes successfully."""
        from src.cli.fleeting_cli import FleetingCLI

        cli = FleetingCLI(vault_path=str(self.base_dir))

        # Execute fleeting health command
        exit_code = cli.fleeting_health(output_format='normal')

        # Should execute without errors
        assert exit_code == 0

    def test_fleeting_triage_command_execution(self):
        """TEST 3: Verify fleeting-triage command executes successfully."""
        from src.cli.fleeting_cli import FleetingCLI

        cli = FleetingCLI(vault_path=str(self.base_dir))

        # Execute fleeting triage command
        exit_code = cli.fleeting_triage(
            quality_threshold=0.7,
            fast=True,
            output_format='normal'
        )

        # Should execute without errors
        assert exit_code == 0

    def test_bug_3_fixed_no_attributeerror(self):
        """
        TEST 4: Verify Bug #3 is fixed (AttributeError: 'AnalyticsManager' object has no attribute 'analyze_fleeting_notes').
        
        Bug Report: Projects/ACTIVE/bug-fleeting-health-attributeerror-2025-10-10.md
        Root Cause: workflow_manager_adapter.py calls self.analytics.analyze_fleeting_notes() which doesn't exist
        Fix: Use WorkflowManager directly in dedicated CLI (bypass buggy adapter)
        """
        from src.cli.fleeting_cli import FleetingCLI
        from src.ai.workflow_manager import WorkflowManager

        # Initialize CLI (should use WorkflowManager, not adapter)
        cli = FleetingCLI(vault_path=str(self.base_dir))

        # Verify it's using WorkflowManager directly
        assert hasattr(cli, 'workflow')
        assert isinstance(cli.workflow, WorkflowManager), \
            "FleetingCLI should use WorkflowManager directly to avoid Bug #3"

        # Execute fleeting health command - should NOT raise AttributeError
        try:
            exit_code = cli.fleeting_health(output_format='normal')
            assert exit_code == 0, "fleeting_health should execute successfully"
        except AttributeError as e:
            if "analyze_fleeting_notes" in str(e):
                pytest.fail(f"Bug #3 NOT FIXED: Still hitting AttributeError: {e}")
            else:
                raise
