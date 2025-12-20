#!/usr/bin/env python3
"""
TDD Iteration 4 - Core CLIs JSON Output Contract Tests

Tests for standardized JSON output schema across core workflow CLIs.
Part of Issue #39: Migrate Automation Scripts to Dedicated CLIs

Contract specification:
- success (bool): Whether the operation succeeded
- errors (list[str]): List of error messages (empty on success)
- data (dict): Command-specific payload with optional status field
- meta (dict): Metadata (cli, subcommand, timestamp)

Semantics:
- success=True + exit 0: Command executed successfully (may be no-op)
- success=False + exit non-zero: Error prevented execution
- No-op: data.status="noop", success=True, errors=[]

RED Phase: These tests define the contract that CLIs must implement.
"""

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestContractValidation:
    """Shared contract validation helper."""

    def _validate_contract(self, output: dict[str, Any]) -> None:
        """
        Validate that JSON output follows the contract.

        Required keys:
        - success (bool)
        - errors (list)
        - data (dict)
        - meta (dict) with cli, subcommand, timestamp
        """
        # Required keys
        assert "success" in output, "JSON output must contain 'success' key"
        assert "errors" in output, "JSON output must contain 'errors' key"
        assert "data" in output, "JSON output must contain 'data' key"
        assert "meta" in output, "JSON output must contain 'meta' key"

        # Type validation
        assert isinstance(output["success"], bool), "'success' must be a boolean"
        assert isinstance(output["errors"], list), "'errors' must be a list"
        assert isinstance(output["data"], dict), "'data' must be a dict"
        assert isinstance(output["meta"], dict), "'meta' must be a dict"

        # Validate errors list contains only strings
        for error in output["errors"]:
            assert isinstance(error, str), "Each error must be a string"

        # Validate meta has required fields
        assert "cli" in output["meta"], "meta must contain 'cli'"
        assert "subcommand" in output["meta"], "meta must contain 'subcommand'"
        assert "timestamp" in output["meta"], "meta must contain 'timestamp'"
        assert isinstance(output["meta"]["cli"], str), "meta.cli must be a string"
        assert isinstance(
            output["meta"]["subcommand"], str
        ), "meta.subcommand must be a string"
        assert isinstance(
            output["meta"]["timestamp"], str
        ), "meta.timestamp must be a string"

    def _extract_json_output(self, mock_print) -> dict[str, Any]:
        """Extract JSON output from mocked print calls."""
        json_calls = [
            call
            for call in mock_print.call_args_list
            if call[0] and "{" in str(call[0][0])
        ]
        assert len(json_calls) >= 1, "Should output JSON"
        return json.loads(json_calls[0][0][0])


class TestCoreWorkflowCLIJsonContract(TestContractValidation):
    """Tests for core_workflow_cli.py JSON output contract."""

    # =========================================================================
    # Status Command Tests
    # =========================================================================

    def test_status_success_json_contract(self, tmp_path):
        """
        Test that core_workflow_cli.py status --format json returns valid contract.

        Expected: success=True, errors=[], data contains workflow report, meta.subcommand="status"
        """
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        # Create a minimal vault structure
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()
        (vault_path / "test.md").write_text("# Test")

        cli = CoreWorkflowCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.status(output_format="json")

        output = self._extract_json_output(mock_print)

        # Validate contract
        self._validate_contract(output)

        # Success-specific assertions
        assert output["success"] is True
        assert output["errors"] == []
        assert output["meta"]["cli"] == "core_workflow_cli"
        assert output["meta"]["subcommand"] == "status"
        assert exit_code == 0

    def test_status_failure_json_contract(self, tmp_path):
        """
        Test that status command returns valid contract on failure.

        Expected: success=False, errors contains message, exit_code != 0
        """
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = CoreWorkflowCLI(vault_path=str(vault_path))

        # Mock generate_workflow_report to raise an exception
        with patch.object(
            cli.workflow_manager,
            "generate_workflow_report",
            side_effect=Exception("Simulated status failure"),
        ):
            with patch("builtins.print") as mock_print:
                exit_code = cli.status(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is False
        assert len(output["errors"]) > 0
        assert "Simulated status failure" in output["errors"][0]
        assert exit_code != 0

    # =========================================================================
    # Process-Inbox Command Tests
    # =========================================================================

    def test_process_inbox_success_json_contract(self, tmp_path):
        """
        Test that process-inbox --format json returns valid contract.

        Expected: success=True, data contains processing results, meta.subcommand="process-inbox"
        """
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        inbox_path = vault_path / "Inbox"
        inbox_path.mkdir()

        cli = CoreWorkflowCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.process_inbox(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert output["meta"]["cli"] == "core_workflow_cli"
        assert output["meta"]["subcommand"] == "process-inbox"
        assert exit_code == 0

    def test_process_inbox_noop_json_contract(self, tmp_path):
        """
        Test that process-inbox with empty inbox returns noop status.

        Expected: success=True, data.status="noop" or "ok", errors=[]
        """
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        inbox_path = vault_path / "Inbox"
        inbox_path.mkdir()
        # Empty inbox - no notes to process

        cli = CoreWorkflowCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.process_inbox(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        # No-op should still return success, may have data.status
        assert exit_code == 0


class TestFleetingCLIJsonContract(TestContractValidation):
    """Tests for fleeting_cli.py JSON output contract."""

    # =========================================================================
    # Fleeting-Health Command Tests
    # =========================================================================

    def test_fleeting_health_success_json_contract(self, tmp_path):
        """
        Test that fleeting-health --format json returns valid contract.

        Expected: success=True, errors=[], data contains health report, meta.subcommand="fleeting-health"
        """
        from src.cli.fleeting_cli import FleetingCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Fleeting Notes").mkdir()

        cli = FleetingCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.fleeting_health(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert output["meta"]["cli"] == "fleeting_cli"
        assert output["meta"]["subcommand"] == "fleeting-health"
        assert exit_code == 0

    def test_fleeting_health_failure_json_contract(self, tmp_path):
        """
        Test that fleeting-health returns valid contract on failure.
        """
        from src.cli.fleeting_cli import FleetingCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Fleeting Notes").mkdir()

        cli = FleetingCLI(vault_path=str(vault_path))

        with patch.object(
            cli.workflow,
            "generate_fleeting_health_report",
            side_effect=Exception("Simulated health check failure"),
        ):
            with patch("builtins.print") as mock_print:
                exit_code = cli.fleeting_health(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is False
        assert len(output["errors"]) > 0
        assert exit_code != 0

    # =========================================================================
    # Fleeting-Triage Command Tests
    # =========================================================================

    def test_fleeting_triage_success_json_contract(self, tmp_path):
        """
        Test that fleeting-triage --format json returns valid contract.

        Expected: success=True, data contains triage report, meta.subcommand="fleeting-triage"
        """
        from src.cli.fleeting_cli import FleetingCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Fleeting Notes").mkdir()

        cli = FleetingCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.fleeting_triage(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert output["meta"]["cli"] == "fleeting_cli"
        assert output["meta"]["subcommand"] == "fleeting-triage"
        assert exit_code == 0


class TestWeeklyReviewCLIJsonContract(TestContractValidation):
    """Tests for weekly_review_cli.py JSON output contract."""

    # =========================================================================
    # Weekly-Review Command Tests
    # =========================================================================

    def test_weekly_review_success_json_contract(self, tmp_path):
        """
        Test that weekly-review --format json returns valid contract.

        Expected: success=True, data contains recommendations, meta.subcommand="weekly-review"
        """
        from src.cli.weekly_review_cli import WeeklyReviewCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = WeeklyReviewCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.weekly_review(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert output["meta"]["cli"] == "weekly_review_cli"
        assert output["meta"]["subcommand"] == "weekly-review"
        assert exit_code == 0

    def test_weekly_review_failure_json_contract(self, tmp_path):
        """
        Test that weekly-review returns valid contract on failure.
        """
        from src.cli.weekly_review_cli import WeeklyReviewCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = WeeklyReviewCLI(vault_path=str(vault_path))

        with patch.object(
            cli.workflow,
            "scan_review_candidates",
            side_effect=Exception("Simulated weekly review failure"),
        ):
            with patch("builtins.print") as mock_print:
                exit_code = cli.weekly_review(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is False
        assert len(output["errors"]) > 0
        assert exit_code != 0

    # =========================================================================
    # Enhanced-Metrics Command Tests
    # =========================================================================

    def test_enhanced_metrics_success_json_contract(self, tmp_path):
        """
        Test that enhanced-metrics --format json returns valid contract.

        Expected: success=True, data contains metrics, meta.subcommand="enhanced-metrics"
        """
        from src.cli.weekly_review_cli import WeeklyReviewCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = WeeklyReviewCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.enhanced_metrics(output_format="json")

        output = self._extract_json_output(mock_print)

        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert output["meta"]["cli"] == "weekly_review_cli"
        assert output["meta"]["subcommand"] == "enhanced-metrics"
        assert exit_code == 0


class TestExitCodeSemantics(TestContractValidation):
    """Tests for exit code / success field alignment across CLIs."""

    def test_core_workflow_exit_code_matches_success(self, tmp_path):
        """Test exit code aligns with success field for core_workflow_cli."""
        from src.cli.core_workflow_cli import CoreWorkflowCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = CoreWorkflowCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.status(output_format="json")

        output = self._extract_json_output(mock_print)

        if output["success"]:
            assert exit_code == 0, "success=True must return exit code 0"
        else:
            assert exit_code != 0, "success=False must return non-zero exit code"

    def test_fleeting_exit_code_matches_success(self, tmp_path):
        """Test exit code aligns with success field for fleeting_cli."""
        from src.cli.fleeting_cli import FleetingCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Fleeting Notes").mkdir()

        cli = FleetingCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.fleeting_health(output_format="json")

        output = self._extract_json_output(mock_print)

        if output["success"]:
            assert exit_code == 0, "success=True must return exit code 0"
        else:
            assert exit_code != 0, "success=False must return non-zero exit code"

    def test_weekly_review_exit_code_matches_success(self, tmp_path):
        """Test exit code aligns with success field for weekly_review_cli."""
        from src.cli.weekly_review_cli import WeeklyReviewCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()

        cli = WeeklyReviewCLI(vault_path=str(vault_path))

        with patch("builtins.print") as mock_print:
            exit_code = cli.enhanced_metrics(output_format="json")

        output = self._extract_json_output(mock_print)

        if output["success"]:
            assert exit_code == 0, "success=True must return exit code 0"
        else:
            assert exit_code != 0, "success=False must return non-zero exit code"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
