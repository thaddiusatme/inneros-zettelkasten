#!/usr/bin/env python3
"""
Test suite for Auto-Promote CLI Command (TDD RED Phase)

Tests the auto-promotion CLI integration:
- Command argument parsing (--auto-promote, --dry-run, --quality-threshold)
- Backend integration with WorkflowManager.auto_promote_ready_notes()
- Output formatting with emoji enhancement
- Error handling and validation
- Exit code behavior

Backend: WorkflowManager.auto_promote_ready_notes() (already implemented)
CLI: CoreWorkflowCLI.auto_promote() (to be implemented)
"""

import unittest
import json
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil


class TestAutoPromoteCLI(unittest.TestCase):
    """Test suite for auto-promote CLI command"""

    def setUp(self):
        """Set up test environment with temp directory and test notes"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.inbox_dir = self.test_dir / "Inbox"
        self.fleeting_dir = self.test_dir / "Fleeting Notes"
        self.permanent_dir = self.test_dir / "Permanent Notes"
        self.literature_dir = self.test_dir / "Literature Notes"

        # Create directories
        self.inbox_dir.mkdir()
        self.fleeting_dir.mkdir()
        self.permanent_dir.mkdir()
        self.literature_dir.mkdir()

        # Create test notes with different quality scores
        self.high_quality_note = self.inbox_dir / "high-quality.md"
        self.high_quality_note.write_text(
            """---
title: High Quality Note
type: fleeting
status: inbox
quality_score: 0.85
---

# High Quality Content
This note has excellent quality and should be promoted.
"""
        )

        self.low_quality_note = self.inbox_dir / "low-quality.md"
        self.low_quality_note.write_text(
            """---
title: Low Quality Note
type: fleeting
status: inbox
quality_score: 0.45
---

# Low Quality Content
This note needs improvement.
"""
        )

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_auto_promote_command_exists(self):
        """TEST 1: Verify auto_promote method exists in CoreWorkflowCLI"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Should have auto_promote method
        self.assertTrue(
            hasattr(cli, "auto_promote"),
            "CoreWorkflowCLI should have auto_promote method",
        )

    def test_auto_promote_basic_execution(self):
        """TEST 2: Verify auto-promote command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock backend to return success results
        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = {
                "total_candidates": 2,
                "promoted_count": 1,
                "skipped_count": 1,
                "error_count": 0,  # No errors
                "by_type": {"fleeting": {"promoted": 1, "skipped": 1}},
                "skipped_notes": [],
                "errors": [],
            }

            # Execute auto-promote command
            exit_code = cli.auto_promote(
                dry_run=False, quality_threshold=0.7, output_format="normal"
            )

            # Should execute without errors
            self.assertEqual(
                exit_code, 0, "Auto-promote should return exit code 0 on success"
            )

    def test_auto_promote_dry_run_no_changes(self):
        """TEST 3: Verify dry-run mode prevents actual file changes"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Count files before
        inbox_files_before = list(self.inbox_dir.glob("*.md"))
        permanent_files_before = list(self.permanent_dir.glob("*.md"))

        # Execute auto-promote in dry-run mode
        exit_code = cli.auto_promote(
            dry_run=True, quality_threshold=0.7, output_format="normal"
        )

        # Count files after
        inbox_files_after = list(self.inbox_dir.glob("*.md"))
        permanent_files_after = list(self.permanent_dir.glob("*.md"))

        # Should not have moved any files
        self.assertEqual(
            len(inbox_files_before),
            len(inbox_files_after),
            "Dry-run should not change file counts in Inbox",
        )
        self.assertEqual(
            len(permanent_files_before),
            len(permanent_files_after),
            "Dry-run should not change file counts in Permanent Notes",
        )
        self.assertEqual(exit_code, 0)

    def test_auto_promote_custom_threshold(self):
        """TEST 4: Verify custom quality threshold is respected"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock the backend to verify threshold is passed
        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = {
                "total_candidates": 2,
                "promoted_count": 0,
                "skipped_count": 2,
                "error_count": 0,
                "by_type": {},
                "skipped_notes": [],
                "errors": [],
            }

            # Execute with custom threshold
            exit_code = cli.auto_promote(
                dry_run=False,
                quality_threshold=0.9,  # Very high threshold
                output_format="normal",
            )

            # Verify backend was called with correct threshold
            mock_promote.assert_called_once_with(dry_run=False, quality_threshold=0.9)
            self.assertEqual(exit_code, 0)

    def test_auto_promote_output_formatting(self):
        """TEST 5: Verify rich output formatting with emojis and statistics"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock backend to return results
        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = {
                "total_candidates": 5,
                "promoted_count": 3,
                "skipped_count": 2,
                "error_count": 0,
                "by_type": {
                    "fleeting": {"promoted": 2, "skipped": 1},
                    "literature": {"promoted": 1, "skipped": 1},
                },
                "skipped_notes": [
                    {"path": "note1.md", "quality": 0.65, "type": "fleeting"}
                ],
                "errors": [],
            }

            # Capture output
            with patch("builtins.print") as mock_print:
                exit_code = cli.auto_promote(
                    dry_run=False, quality_threshold=0.7, output_format="normal"
                )

                # Verify output contains emojis and statistics
                output_calls = [str(call) for call in mock_print.call_args_list]
                output_text = " ".join(output_calls)

                # Should contain success emoji
                self.assertTrue(
                    "✅" in output_text, "Output should contain success emoji"
                )

                # Should contain promoted count
                self.assertTrue(
                    any("3" in call for call in output_calls),
                    "Output should show promoted count (3)",
                )

                self.assertEqual(exit_code, 0)

    def test_auto_promote_json_output(self):
        """TEST 6: Verify JSON output format works correctly"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock backend
        expected_results = {
            "total_candidates": 2,
            "promoted_count": 1,
            "skipped_count": 1,
            "error_count": 0,
            "by_type": {"fleeting": {"promoted": 1, "skipped": 1}},
            "skipped_notes": [],
            "errors": [],
        }

        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = expected_results

            # Capture output
            with patch("builtins.print") as mock_print:
                exit_code = cli.auto_promote(
                    dry_run=False, quality_threshold=0.7, output_format="json"
                )

                # Should have printed JSON
                self.assertTrue(mock_print.called)

                # Verify JSON is valid
                printed_args = mock_print.call_args_list[0][0]
                if printed_args:
                    json_output = printed_args[0]
                    # Should be valid JSON
                    parsed = json.loads(json_output)
                    self.assertEqual(parsed["promoted_count"], 1)

                self.assertEqual(exit_code, 0)

    def test_auto_promote_threshold_validation(self):
        """TEST 7: Verify quality threshold validation (0.0-1.0 range)"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Test invalid threshold (too high)
        with patch("builtins.print") as mock_print:
            exit_code = cli.auto_promote(
                dry_run=False,
                quality_threshold=1.5,  # Invalid: > 1.0
                output_format="normal",
            )

            # Should fail with exit code 2 (invalid arguments)
            self.assertEqual(
                exit_code, 2, "Invalid threshold should return exit code 2"
            )

            # Should print error message
            error_output = " ".join(str(call) for call in mock_print.call_args_list)
            self.assertTrue(
                "threshold" in error_output.lower(),
                "Error message should mention threshold",
            )

        # Test invalid threshold (negative)
        with patch("builtins.print") as mock_print:
            exit_code = cli.auto_promote(
                dry_run=False,
                quality_threshold=-0.1,  # Invalid: < 0.0
                output_format="normal",
            )

            self.assertEqual(exit_code, 2)

    def test_auto_promote_with_errors(self):
        """TEST 8: Verify error handling and reporting"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock backend to return errors
        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = {
                "total_candidates": 3,
                "promoted_count": 1,
                "skipped_count": 1,
                "error_count": 1,
                "by_type": {"fleeting": {"promoted": 1, "skipped": 1}},
                "skipped_notes": [],
                "errors": [{"note": "error-note.md", "error": "File locked"}],
            }

            # Capture output
            with patch("builtins.print") as mock_print:
                exit_code = cli.auto_promote(
                    dry_run=False, quality_threshold=0.7, output_format="normal"
                )

                # Should contain error emoji
                output_calls = [str(call) for call in mock_print.call_args_list]
                output_text = " ".join(output_calls)

                self.assertTrue(
                    "🚨" in output_text or "❌" in output_text,
                    "Output should contain error emoji",
                )

                # Exit code should be 1 (errors occurred)
                self.assertEqual(
                    exit_code, 1, "Should return exit code 1 when errors occurred"
                )

    def test_auto_promote_dry_run_preview(self):
        """TEST 9: Verify dry-run shows preview of what would be promoted"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Mock backend with dry-run results
        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = {
                "total_candidates": 3,
                "promoted_count": 0,
                "skipped_count": 0,
                "error_count": 0,
                "dry_run": True,
                "would_promote_count": 2,
                "preview": [
                    {
                        "note": "note1.md",
                        "type": "fleeting",
                        "quality": 0.85,
                        "target": "permanent",
                    },
                    {
                        "note": "note2.md",
                        "type": "literature",
                        "quality": 0.78,
                        "target": "literature",
                    },
                ],
                "by_type": {},
                "skipped_notes": [],
                "errors": [],
            }

            # Capture output
            with patch("builtins.print") as mock_print:
                exit_code = cli.auto_promote(
                    dry_run=True, quality_threshold=0.7, output_format="normal"
                )

                output_calls = [str(call) for call in mock_print.call_args_list]
                output_text = " ".join(output_calls)

                # Should show "Would promote"
                self.assertTrue(
                    "would" in output_text.lower() or "preview" in output_text.lower(),
                    "Dry-run output should indicate preview/would promote",
                )

                # Should show note names
                self.assertTrue(
                    "note1.md" in output_text or "note2.md" in output_text,
                    "Preview should show note names",
                )

                self.assertEqual(exit_code, 0)

    def test_auto_promote_backend_integration(self):
        """TEST 10: Verify CLI correctly calls WorkflowManager backend"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))

        # Verify backend method exists
        self.assertTrue(
            hasattr(cli.workflow_manager, "auto_promote_ready_notes"),
            "WorkflowManager should have auto_promote_ready_notes method",
        )

        # Mock backend and verify it's called correctly
        with patch.object(
            cli.workflow_manager, "auto_promote_ready_notes"
        ) as mock_promote:
            mock_promote.return_value = {
                "total_candidates": 0,
                "promoted_count": 0,
                "skipped_count": 0,
                "error_count": 0,
                "by_type": {},
                "skipped_notes": [],
                "errors": [],
            }

            # Execute command
            cli.auto_promote(
                dry_run=True, quality_threshold=0.8, output_format="normal"
            )

            # Verify backend was called with correct parameters
            mock_promote.assert_called_once()
            call_args = mock_promote.call_args
            self.assertEqual(call_args.kwargs["dry_run"], True)
            self.assertEqual(call_args.kwargs["quality_threshold"], 0.8)


if __name__ == "__main__":
    unittest.main()
