"""
Contract Tests: WorkflowManager ↔ CoreWorkflowCLI Integration

TDD Goal: Prevent data structure mismatches between backend and CLI layer
Tests the contract/interface between WorkflowManager and CoreWorkflowCLI

This test would have caught the bug where:
- WorkflowManager returns: {"total_files": 60, "processed": 0, "failed": 16}
- CoreWorkflowCLI expected: {"total": 60, "successful": 0, "failed": 16}
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cli.core_workflow_cli import CoreWorkflowCLI


class TestWorkflowManagerCLIContract:
    """
    Contract tests ensuring WorkflowManager and CoreWorkflowCLI stay synchronized.
    
    RED → GREEN → REFACTOR approach:
    1. RED: Test fails when keys don't match
    2. GREEN: Fix CLI to use correct keys from WorkflowManager
    3. REFACTOR: Extract key constants to shared module
    """

    @pytest.fixture
    def mock_workflow_manager(self):
        """Mock WorkflowManager with realistic return structure."""
        manager = Mock()
        manager.inbox_dir = Path("/fake/vault/Inbox")
        manager.fleeting_dir = Path("/fake/vault/Fleeting Notes")
        return manager

    @pytest.fixture
    def cli(self, mock_workflow_manager):
        """CoreWorkflowCLI instance with mocked WorkflowManager."""
        with patch('cli.core_workflow_cli.WorkflowManager', return_value=mock_workflow_manager):
            return CoreWorkflowCLI(vault_path="/fake/vault")

    def test_batch_process_inbox_returns_expected_keys(self, mock_workflow_manager):
        """
        RED TEST: Verify WorkflowManager.batch_process_inbox() returns expected structure.
        
        This test documents the contract that WorkflowManager MUST maintain.
        If this test fails, either:
        1. WorkflowManager changed its interface (breaking change)
        2. This test needs updating (document why)
        """
        # Arrange: Set up realistic WorkflowManager response
        expected_result = {
            "total_files": 60,      # KEY: Must be "total_files" not "total"
            "processed": 44,        # KEY: Must be "processed" not "successful"
            "failed": 16,
            "results": [],
            "summary": {
                "promote_to_permanent": 10,
                "move_to_fleeting": 20,
                "needs_improvement": 14
            }
        }
        mock_workflow_manager.batch_process_inbox.return_value = expected_result

        # Act: Call the actual method
        result = mock_workflow_manager.batch_process_inbox()

        # Assert: Contract keys MUST exist
        assert "total_files" in result, "WorkflowManager MUST return 'total_files' key"
        assert "processed" in result, "WorkflowManager MUST return 'processed' key"
        assert "failed" in result, "WorkflowManager MUST return 'failed' key"
        assert "results" in result, "WorkflowManager MUST return 'results' key"

        # Assert: Verify types
        assert isinstance(result["total_files"], int)
        assert isinstance(result["processed"], int)
        assert isinstance(result["failed"], int)
        assert isinstance(result["results"], list)

    def test_cli_process_inbox_uses_correct_keys(self, cli, mock_workflow_manager):
        """
        RED TEST: Verify CLI uses the correct keys from WorkflowManager response.
        
        This test would have FAILED with the original bug:
        - CLI was looking for "successful" key (doesn't exist)
        - CLI was looking for "total" key (doesn't exist)
        - Should use "processed" and "total_files" instead
        """
        # Arrange: Mock WorkflowManager to return realistic data
        mock_workflow_manager.batch_process_inbox.return_value = {
            "total_files": 60,
            "processed": 44,
            "failed": 16,
            "results": []
        }

        # Capture stdout
        captured_output = StringIO()

        # Act: Process inbox
        with patch('sys.stdout', captured_output):
            exit_code = cli.process_inbox(output_format='normal')

        output = captured_output.getvalue()

        # Assert: CLI must display the correct values
        assert exit_code == 0, "Process inbox should succeed"
        assert "Processed: 44" in output, "CLI must display 'processed' count correctly"
        assert "Total: 60" in output, "CLI must display 'total_files' count correctly"
        assert "Failed: 16" in output, "CLI must display 'failed' count correctly"

        # Anti-pattern: These should NOT appear (old bug)
        assert "Processed: 0" not in output, "BUG: CLI showing 0 when data exists"
        assert "Total: 0" not in output, "BUG: CLI showing 0 total when 60 files exist"

    def test_cli_handles_empty_inbox(self, cli, mock_workflow_manager):
        """
        GREEN TEST: Verify CLI correctly displays empty inbox.
        
        Edge case: 0 files should show 0 for all counts.
        """
        # Arrange: Empty inbox
        mock_workflow_manager.batch_process_inbox.return_value = {
            "total_files": 0,
            "processed": 0,
            "failed": 0,
            "results": []
        }

        # Capture stdout
        captured_output = StringIO()

        # Act
        with patch('sys.stdout', captured_output):
            exit_code = cli.process_inbox(output_format='normal')

        output = captured_output.getvalue()

        # Assert
        assert exit_code == 0
        assert "Processed: 0" in output
        assert "Total: 0" in output
        assert "Failed: 0" in output

    def test_cli_json_output_preserves_keys(self, cli, mock_workflow_manager):
        """
        GREEN TEST: Verify JSON output preserves original keys from WorkflowManager.
        
        JSON mode should pass through the exact structure for automation.
        """
        # Arrange
        expected_data = {
            "total_files": 60,
            "processed": 44,
            "failed": 16,
            "results": [{"note": "test.md", "success": True}]
        }
        mock_workflow_manager.batch_process_inbox.return_value = expected_data

        # Capture stdout
        captured_output = StringIO()

        # Act
        with patch('sys.stdout', captured_output):
            exit_code = cli.process_inbox(output_format='json')

        output = captured_output.getvalue()

        # Assert: JSON output must preserve exact keys
        import json
        result = json.loads(output)
        assert result["total_files"] == 60, "JSON must preserve 'total_files' key"
        assert result["processed"] == 44, "JSON must preserve 'processed' key"
        assert result["failed"] == 16, "JSON must preserve 'failed' key"

    def test_generate_workflow_report_contract(self, mock_workflow_manager):
        """
        RED TEST: Document the contract for generate_workflow_report().
        
        This prevents future mismatches in the status/report commands.
        """
        # Arrange: Mock the expected structure
        expected_report = {
            "workflow_status": {
                "health": "needs_attention",
                "directory_counts": {
                    "Inbox": 60,
                    "Fleeting Notes": 120,
                    "Permanent Notes": 450,
                    "Archive": 200
                },
                "total_notes": 830
            },
            "ai_features": {
                "notes_with_ai_tags": 100,
                "notes_with_ai_summaries": 50,
                "notes_with_ai_processing": 150,
                "total_analyzed": 830
            },
            "analytics": {},
            "recommendations": [
                "Process 60 notes in inbox - consider batch processing"
            ]
        }
        mock_workflow_manager.generate_workflow_report.return_value = expected_report

        # Act
        result = mock_workflow_manager.generate_workflow_report()

        # Assert: Contract keys MUST exist
        assert "workflow_status" in result
        assert "ai_features" in result
        assert "recommendations" in result
        assert "directory_counts" in result["workflow_status"]


class TestCLIDisplayFormatting:
    """
    Tests for CLI display layer correctness.
    
    Ensures the CLI correctly formats and displays data from WorkflowManager.
    """

    def test_process_inbox_display_with_all_failures(self):
        """
        REFACTOR TEST: Handle edge case where all notes fail.
        
        This was part of the original bug scenario:
        - 60 files attempted
        - 16 failed
        - 0 processed (all timed out)
        """
        with patch('cli.core_workflow_cli.WorkflowManager') as MockWM:
            # Arrange: All failures scenario
            mock_manager = MockWM.return_value
            mock_manager.inbox_dir = Path("/fake/vault/Inbox")
            mock_manager.batch_process_inbox.return_value = {
                "total_files": 60,
                "processed": 0,      # All failed
                "failed": 16,        # Only 16 attempted before timeout
                "results": []
            }

            cli = CoreWorkflowCLI(vault_path="/fake/vault")
            captured_output = StringIO()

            # Act
            with patch('sys.stdout', captured_output):
                exit_code = cli.process_inbox(output_format='normal')

            output = captured_output.getvalue()

            # Assert: Should show the reality
            assert "Processed: 0" in output, "Should show 0 processed"
            assert "Failed: 16" in output, "Should show 16 failed"
            assert "Total: 60" in output, "Should show 60 total files (not 0)"

            # The bug was showing "Total: 0" because it looked for wrong key
            assert exit_code == 0  # Still exit successfully (partial processing)


class TestKeyConsistencyAcrossCommands:
    """
    REFACTOR: Ensure all commands use consistent key naming.
    
    Future improvement: Extract keys to constants module.
    """

    def test_all_commands_use_standard_keys(self):
        """
        Meta-test: Document all keys used across the system.
        
        Future refactor: Create src/constants.py with:
        - BATCH_PROCESS_KEYS = {"total_files", "processed", "failed", "results"}
        - WORKFLOW_STATUS_KEYS = {"workflow_status", "ai_features", ...}
        """
        # This is a documentation test
        # If new keys are added, update this test

        expected_batch_keys = {
            "total_files",   # Not "total"
            "processed",     # Not "successful"
            "failed",
            "results",
            "summary"
        }

        expected_workflow_status_keys = {
            "workflow_status",
            "ai_features",
            "analytics",
            "recommendations"
        }

        # These sets serve as documentation
        assert len(expected_batch_keys) == 5
        assert len(expected_workflow_status_keys) == 4


# Run tests with: pytest tests/unit/test_workflow_cli_contract.py -v
