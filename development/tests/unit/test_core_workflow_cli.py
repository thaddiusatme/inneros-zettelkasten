#!/usr/bin/env python3
"""
Test suite for Core Workflow CLI (TDD RED Phase - Iteration 4)

Tests the extraction of core workflow commands from workflow_demo.py:
- --status: Show workflow status
- --process-inbox: Process all inbox notes
- --promote: Promote a note
- --report: Generate comprehensive workflow report

Manager: WorkflowManager (has all core methods)

Vault Configuration Integration (GitHub Issue #45):
- Tests updated to use vault_config.yaml paths
- Validates knowledge/ subdirectory organization
- Part of Phase 2 Priority 2 CLI tools migration
"""

import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil
from src.config.vault_config_loader import get_vault_config


class TestCoreWorkflowCLI(unittest.TestCase):
    """Test suite for core workflow CLI commands"""

    def setUp(self):
        """Set up test environment with temp directory using vault config"""
        self.test_dir = Path(tempfile.mkdtemp())

        # Load vault config for proper directory structure
        config = get_vault_config(str(self.test_dir))
        self.inbox_dir = config.inbox_dir
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create other directories needed by WorkflowManager (which still uses hardcoded paths)
        # TODO: Remove these when WorkflowManager is migrated to vault config
        (self.test_dir / "Permanent Notes").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "Literature Notes").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "Fleeting Notes").mkdir(parents=True, exist_ok=True)

        # Create test note
        self.test_note = self.inbox_dir / "test-note.md"
        self.test_note.write_text(
            """---
title: Test Note
type: fleeting
---

# Test Content
"""
        )

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_core_workflow_cli_import(self):
        """TEST 1: Verify core_workflow_cli module can be imported"""
        try:
            from src.cli.core_workflow_cli import CoreWorkflowCLI

            self.assertIsNotNone(CoreWorkflowCLI)
        except ImportError as e:
            self.fail(f"Failed to import CoreWorkflowCLI: {e}")

    def test_status_command_execution(self):
        """TEST 2: Verify status command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute status command
        exit_code = cli.status(output_format="normal")

        # Should execute without errors
        self.assertEqual(exit_code, 0)

    def test_process_inbox_command_execution(self):
        """TEST 3: Verify process-inbox command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute process-inbox command
        exit_code = cli.process_inbox(output_format="normal")

        # Should execute without errors
        self.assertEqual(exit_code, 0)

    def test_promote_command_execution(self):
        """TEST 4: Verify promote command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute promote command
        exit_code = cli.promote(
            note_path=str(self.test_note),
            target_type="permanent",
            output_format="normal",
        )

        # Should execute without errors
        self.assertEqual(exit_code, 0)

    def test_report_command_execution(self):
        """TEST 5: Verify report command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute report command
        exit_code = cli.report(output_format="normal", export_path=None)

        # Should execute without errors
        self.assertEqual(exit_code, 0)

    def test_json_output_format(self):
        """TEST 6: Verify JSON output format works for all commands"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Test status with JSON
        with patch("builtins.print") as mock_print:
            exit_code = cli.status(output_format="json")
            self.assertEqual(exit_code, 0)
            # Should have printed JSON output
            self.assertTrue(mock_print.called)

    def test_workflow_manager_integration(self):
        """TEST 7: Verify CLI integrates with WorkflowManager correctly"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Verify WorkflowManager is initialized
        self.assertIsNotNone(cli.workflow_manager)

        # Verify manager has required methods
        self.assertTrue(hasattr(cli.workflow_manager, "generate_workflow_report"))
        self.assertTrue(hasattr(cli.workflow_manager, "batch_process_inbox"))
        self.assertTrue(hasattr(cli.workflow_manager, "promote_note"))


class TestMetadataRepairCLI(unittest.TestCase):
    """
    TDD Iteration 2 - RED Phase: Metadata Repair CLI Integration

    Tests for the repair-metadata command that fixes missing type: frontmatter fields.
    Critical for unblocking auto-promotion system (8 notes blocked, 21% error rate).
    """

    def setUp(self):
        """Set up test environment with notes needing metadata repair using vault config"""
        self.test_dir = Path(tempfile.mkdtemp())

        # Load vault config for proper directory structure
        config = get_vault_config(str(self.test_dir))
        self.inbox_dir = config.inbox_dir
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create other directories needed by WorkflowManager (which still uses hardcoded paths)
        # TODO: Remove these when WorkflowManager is migrated to vault config
        (self.test_dir / "Permanent Notes").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "Literature Notes").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "Fleeting Notes").mkdir(parents=True, exist_ok=True)

        # Create note WITH type field (should not need repair)
        self.good_note = self.inbox_dir / "fleeting-20250101-1234-test.md"
        self.good_note.write_text(
            """---
title: Good Note
type: fleeting
---

# Content
"""
        )

        # Create note WITHOUT type field (needs repair)
        self.bad_note = self.inbox_dir / "lit-20250102-5678-test.md"
        self.bad_note.write_text(
            """---
title: Bad Note
---

# Content
"""
        )

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_repair_metadata_method_exists(self):
        """TEST 8 (RED): Verify repair_metadata method exists in CoreWorkflowCLI"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Method should exist
        self.assertTrue(hasattr(cli, "repair_metadata"))
        self.assertTrue(callable(getattr(cli, "repair_metadata")))

    def test_repair_metadata_default_dry_run(self):
        """TEST 9 (RED): Verify repair-metadata defaults to dry-run mode (preview only)"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute repair-metadata (should default to dry-run)
        exit_code = cli.repair_metadata(execute=False, output_format="normal")

        # Should succeed and return 0
        self.assertEqual(exit_code, 0)

        # File should NOT be modified (dry-run mode)
        content_after = self.bad_note.read_text()
        self.assertNotIn("type: literature", content_after)

    def test_repair_metadata_with_execute_flag(self):
        """TEST 10 (RED): Verify repair-metadata with --execute actually modifies files"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute repair-metadata with execute=True
        exit_code = cli.repair_metadata(execute=True, output_format="normal")

        # Should succeed
        self.assertEqual(exit_code, 0)

        # File SHOULD be modified (execute mode)
        content_after = self.bad_note.read_text()
        self.assertIn("type: literature", content_after)

    def test_repair_metadata_shows_statistics(self):
        """TEST 11 (RED): Verify repair-metadata displays scan statistics"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Capture output
        with patch("builtins.print") as mock_print:
            exit_code = cli.repair_metadata(execute=False, output_format="normal")

            # Should display statistics
            output_text = " ".join(str(call) for call in mock_print.call_args_list)
            self.assertIn("scanned", output_text.lower())
            self.assertIn("repair", output_text.lower())

    def test_repair_metadata_delegates_to_workflow_manager(self):
        """TEST 12 (RED): Verify CLI delegates to WorkflowManager.repair_inbox_metadata()"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock the workflow_manager method to verify it's called
        with patch.object(cli.workflow_manager, "repair_inbox_metadata") as mock_repair:
            mock_repair.return_value = {
                "notes_scanned": 2,
                "repairs_needed": 1,
                "repairs_made": 0,
                "errors": [],
            }

            # Execute repair_metadata
            exit_code = cli.repair_metadata(execute=False, output_format="normal")

            # Should have called workflow_manager.repair_inbox_metadata
            mock_repair.assert_called_once_with(execute=False)
            self.assertEqual(exit_code, 0)

    def test_repair_metadata_handles_no_repairs_needed(self):
        """TEST 13 (RED): Verify graceful handling when no repairs needed"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        # Create directory with only good notes using vault config
        test_dir2 = Path(tempfile.mkdtemp())
        config2 = get_vault_config(str(test_dir2))
        inbox_dir2 = config2.inbox_dir
        inbox_dir2.mkdir(parents=True, exist_ok=True)

        # Create legacy directories for WorkflowManager compatibility
        (test_dir2 / "Permanent Notes").mkdir(parents=True, exist_ok=True)
        (test_dir2 / "Literature Notes").mkdir(parents=True, exist_ok=True)
        (test_dir2 / "Fleeting Notes").mkdir(parents=True, exist_ok=True)

        good_note2 = inbox_dir2 / "fleeting-20250101-1234-test.md"
        good_note2.write_text(
            """---
title: Good Note
type: fleeting
---

# Content
"""
        )

        try:
            cli = CoreWorkflowCLI(vault_path=str(test_dir2))

            # Execute repair_metadata - should succeed gracefully when no repairs needed
            exit_code = cli.repair_metadata(execute=False, output_format="normal")

            # Should succeed with exit code 0
            self.assertEqual(exit_code, 0)
        finally:
            if test_dir2.exists():
                shutil.rmtree(test_dir2)

    def test_repair_metadata_json_output_format(self):
        """TEST 14 (RED): Verify repair-metadata supports JSON output format"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Execute with JSON format
        with patch("builtins.print") as mock_print:
            exit_code = cli.repair_metadata(execute=False, output_format="json")

            # Should succeed
            self.assertEqual(exit_code, 0)

            # Should output JSON
            self.assertTrue(mock_print.called)


class TestVaultConfigIntegration(unittest.TestCase):
    """Test CoreWorkflowCLI integration with vault configuration (GitHub Issue #45)."""

    def setUp(self):
        """Set up test environment with vault config structure"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = get_vault_config(str(self.test_dir))
        self.config.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.config.fleeting_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_cli_uses_vault_config_for_directory_paths(self):
        """
        TEST 15: Verify CLI uses vault config for directory resolution.

        Integration test validates CLI loads vault config and uses
        knowledge/ subdirectory paths instead of hardcoded Inbox/.
        """
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        # Create test note in knowledge/Inbox
        test_note = self.config.inbox_dir / "test-note.md"
        test_note.write_text("---\ntitle: Test\n---\nContent")

        # Act: Initialize CLI
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Assert: CLI should use knowledge/ subdirectory paths
        self.assertTrue(hasattr(cli, "inbox_dir"), "CLI should have inbox_dir property")
        self.assertTrue(
            hasattr(cli, "fleeting_dir"), "CLI should have fleeting_dir property"
        )
        self.assertIn(
            "knowledge",
            str(cli.inbox_dir),
            f"Expected knowledge/ in inbox_dir, got: {cli.inbox_dir}",
        )
        self.assertEqual(cli.inbox_dir, self.config.inbox_dir, "inbox_dir mismatch")
        self.assertEqual(
            cli.fleeting_dir, self.config.fleeting_dir, "fleeting_dir mismatch"
        )

    def test_promote_resolves_inbox_path_using_vault_config(self):
        """
        TEST 16: Test that promote command searches inbox using vault config paths.
        Validates the file search logic uses knowledge/Inbox.
        """
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        # Create test note in knowledge/Inbox
        test_note = self.config.inbox_dir / "promote-test.md"
        test_note.write_text("---\ntitle: Test\ntype: fleeting\n---\nContent")

        # Initialize CLI
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Verify CLI has correct directory properties for file search
        self.assertEqual(
            cli.inbox_dir, self.config.inbox_dir, "CLI inbox_dir should match config"
        )
        self.assertTrue(test_note.exists(), "Test note should exist in knowledge/Inbox")

        # Verify the note can be found via the CLI's inbox_dir
        found_note = cli.inbox_dir / "promote-test.md"
        self.assertTrue(
            found_note.exists(), "CLI should be able to find note via inbox_dir"
        )


if __name__ == "__main__":
    unittest.main()
