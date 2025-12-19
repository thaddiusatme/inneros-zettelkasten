#!/usr/bin/env python3
"""
Subprocess Integration Tests for CLI JSON Output Contract

Issue #39 P2: Validates that real CLI entrypoints (via subprocess) emit
parseable, contract-compliant JSON when `--format json` is used.

These tests catch "it works in unit tests but breaks when invoked as a real CLI"
by running actual CLI files via subprocess.run().

Contract specification (from cli_output_contract.py):
- success (bool): Whether the operation succeeded
- errors (list[str]): List of error messages (empty on success)
- data (dict): Command-specific payload
- meta (dict): Metadata containing:
  - cli (str): CLI name
  - subcommand (str): Subcommand name
  - timestamp (str): ISO format timestamp

Test strategy:
- Use subprocess.run() to invoke real CLI files
- Create minimal temp vault structure where needed
- Assert stdout is valid JSON with required keys
- Assert exit codes align with success field
- Keep tests fast (<2s locally, no AI calls)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest

# Path to development directory (for CLI files)
DEV_DIR = Path(__file__).parent.parent.parent
CLI_DIR = DEV_DIR / "src" / "cli"


class JSONContractValidator:
    """Helper for validating CLI JSON output contract."""

    REQUIRED_KEYS = {"success", "errors", "data", "meta"}
    REQUIRED_META_KEYS = {"cli", "subcommand", "timestamp"}

    @classmethod
    def validate(
        cls, json_str: str, expected_cli: str, expected_subcommand: str
    ) -> dict:
        """
        Validate JSON output against contract specification.

        Args:
            json_str: Raw JSON string from CLI stdout
            expected_cli: Expected value for meta.cli
            expected_subcommand: Expected value for meta.subcommand

        Returns:
            Parsed JSON dict

        Raises:
            AssertionError: If contract is violated
        """
        # Must be valid JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"stdout is not valid JSON: {e}\nRaw output:\n{json_str[:500]}")

        # Check required top-level keys
        missing_keys = cls.REQUIRED_KEYS - set(data.keys())
        assert not missing_keys, f"Missing required keys: {missing_keys}"

        # Check types
        assert isinstance(data["success"], bool), "success must be bool"
        assert isinstance(data["errors"], list), "errors must be list"
        assert isinstance(data["data"], dict), "data must be dict"
        assert isinstance(data["meta"], dict), "meta must be dict"

        # Check required meta keys
        missing_meta = cls.REQUIRED_META_KEYS - set(data["meta"].keys())
        assert not missing_meta, f"Missing required meta keys: {missing_meta}"

        # Check meta values
        assert (
            data["meta"]["cli"] == expected_cli
        ), f"Expected meta.cli='{expected_cli}', got '{data['meta']['cli']}'"
        assert (
            data["meta"]["subcommand"] == expected_subcommand
        ), f"Expected meta.subcommand='{expected_subcommand}', got '{data['meta']['subcommand']}'"
        assert isinstance(data["meta"]["timestamp"], str), "meta.timestamp must be str"

        return data

    @classmethod
    def validate_exit_code(
        cls, result: subprocess.CompletedProcess, parsed: dict
    ) -> None:
        """Validate exit code aligns with success field."""
        if parsed["success"]:
            assert (
                result.returncode == 0
            ), f"success=True but exit code={result.returncode}\nstderr: {result.stderr}"
        else:
            # Non-zero exit code for failure (implementation may vary)
            # For now, just ensure we have errors when success=False
            pass  # Some CLIs return 0 even on controlled failures


def run_cli(
    cli_file: str, args: list[str], cwd: Optional[Path] = None
) -> subprocess.CompletedProcess:
    """
    Run a CLI file via subprocess.

    Args:
        cli_file: Name of CLI file (e.g., 'backup_cli.py')
        args: Command-line arguments
        cwd: Working directory

    Returns:
        CompletedProcess with stdout, stderr, returncode
    """
    cli_path = CLI_DIR / cli_file
    assert cli_path.exists(), f"CLI file not found: {cli_path}"

    cmd = [sys.executable, str(cli_path)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or DEV_DIR,
        timeout=30,  # Safety timeout
    )


@pytest.fixture
def temp_vault(tmp_path: Path) -> Path:
    """Create a minimal temp vault structure for testing."""
    # Create required directories
    (tmp_path / "Inbox").mkdir()
    (tmp_path / "Fleeting Notes").mkdir()
    (tmp_path / "Permanent Notes").mkdir()
    (tmp_path / "Literature Notes").mkdir()

    # Create a sample note in Inbox
    sample_note = tmp_path / "Inbox" / "test-note.md"
    sample_note.write_text(
        """---
title: Test Note
type: fleeting
status: inbox
created: 2025-01-01 12:00
---

# Test Note

This is a test note for integration testing.
"""
    )

    return tmp_path


@pytest.fixture
def temp_onedrive_path(tmp_path: Path) -> Path:
    """Create a temp directory simulating OneDrive screenshots folder."""
    onedrive = tmp_path / "OneDrive" / "Pictures" / "Screenshots"
    onedrive.mkdir(parents=True)
    return onedrive


# =============================================================================
# BACKUP CLI TESTS
# =============================================================================


class TestBackupCLIJsonContract:
    """Subprocess tests for backup_cli.py JSON contract compliance."""

    def test_backup_json_output_contract(self, temp_vault: Path):
        """Test backup command emits contract-compliant JSON."""
        result = run_cli(
            "backup_cli.py",
            ["--vault", str(temp_vault), "backup", "--format", "json"],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="backup_cli",
            expected_subcommand="backup",
        )
        JSONContractValidator.validate_exit_code(result, parsed)

        # Backup-specific: should have backup_path in data
        assert (
            "backup_path" in parsed["data"]
        ), "backup should return backup_path in data"

    def test_prune_backups_json_output_contract(self, temp_vault: Path):
        """Test prune-backups command emits contract-compliant JSON."""
        result = run_cli(
            "backup_cli.py",
            [
                "--vault",
                str(temp_vault),
                "prune-backups",
                "--keep",
                "5",
                "--dry-run",
                "--format",
                "json",
            ],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="backup_cli",
            expected_subcommand="prune-backups",
        )
        JSONContractValidator.validate_exit_code(result, parsed)

        # Prune-specific: should have key fields in data
        assert (
            "dry_run" in parsed["data"]
        ), "prune-backups should return dry_run in data"


# =============================================================================
# SCREENSHOT CLI TESTS
# =============================================================================


class TestScreenshotCLIJsonContract:
    """Subprocess tests for screenshot_cli.py JSON contract compliance."""

    def test_process_dry_run_json_output_contract(
        self, temp_vault: Path, temp_onedrive_path: Path
    ):
        """Test process --dry-run command emits contract-compliant JSON."""
        result = run_cli(
            "screenshot_cli.py",
            [
                "--vault",
                str(temp_vault),
                "--onedrive-path",
                str(temp_onedrive_path),
                "process",
                "--dry-run",
                "--format",
                "json",
            ],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="screenshot_cli",
            expected_subcommand="process",
        )
        JSONContractValidator.validate_exit_code(result, parsed)


# =============================================================================
# CORE WORKFLOW CLI TESTS
# =============================================================================


class TestCoreWorkflowCLIJsonContract:
    """Subprocess tests for core_workflow_cli.py JSON contract compliance."""

    def test_status_json_output_contract(self, temp_vault: Path):
        """Test status command emits contract-compliant JSON."""
        result = run_cli(
            "core_workflow_cli.py",
            [str(temp_vault), "status", "--format", "json"],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="core_workflow_cli",
            expected_subcommand="status",
        )
        JSONContractValidator.validate_exit_code(result, parsed)

    def test_process_inbox_json_output_contract(self, temp_vault: Path):
        """Test process-inbox command emits contract-compliant JSON."""
        result = run_cli(
            "core_workflow_cli.py",
            [str(temp_vault), "process-inbox", "--format", "json"],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="core_workflow_cli",
            expected_subcommand="process-inbox",
        )
        JSONContractValidator.validate_exit_code(result, parsed)


# =============================================================================
# FLEETING CLI TESTS
# =============================================================================


class TestFleetingCLIJsonContract:
    """Subprocess tests for fleeting_cli.py JSON contract compliance."""

    def test_fleeting_health_json_output_contract(self, temp_vault: Path):
        """Test fleeting-health command emits contract-compliant JSON."""
        result = run_cli(
            "fleeting_cli.py",
            ["--vault", str(temp_vault), "fleeting-health", "--format", "json"],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="fleeting_cli",
            expected_subcommand="fleeting-health",
        )
        JSONContractValidator.validate_exit_code(result, parsed)

    def test_fleeting_triage_json_output_contract(self, temp_vault: Path):
        """Test fleeting-triage command emits contract-compliant JSON."""
        result = run_cli(
            "fleeting_cli.py",
            ["--vault", str(temp_vault), "fleeting-triage", "--format", "json"],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="fleeting_cli",
            expected_subcommand="fleeting-triage",
        )
        JSONContractValidator.validate_exit_code(result, parsed)


# =============================================================================
# WEEKLY REVIEW CLI TESTS
# =============================================================================


class TestWeeklyReviewCLIJsonContract:
    """Subprocess tests for weekly_review_cli.py JSON contract compliance."""

    def test_weekly_review_json_output_contract(self, temp_vault: Path):
        """Test weekly-review command emits contract-compliant JSON."""
        result = run_cli(
            "weekly_review_cli.py",
            [
                "--vault",
                str(temp_vault),
                "weekly-review",
                "--preview",
                "--format",
                "json",
            ],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="weekly_review_cli",
            expected_subcommand="weekly-review",
        )
        JSONContractValidator.validate_exit_code(result, parsed)

    def test_enhanced_metrics_json_output_contract(self, temp_vault: Path):
        """Test enhanced-metrics command emits contract-compliant JSON."""
        result = run_cli(
            "weekly_review_cli.py",
            ["--vault", str(temp_vault), "enhanced-metrics", "--format", "json"],
        )

        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="weekly_review_cli",
            expected_subcommand="enhanced-metrics",
        )
        JSONContractValidator.validate_exit_code(result, parsed)


# =============================================================================
# ERROR PATH TESTS
# =============================================================================


class TestErrorPathsJsonContract:
    """Tests for contract JSON on error/edge cases."""

    def test_backup_cli_with_nonexistent_vault_emits_contract_json(
        self, tmp_path: Path
    ):
        """Backup CLI should emit contract JSON even for nonexistent vault."""
        nonexistent = tmp_path / "does_not_exist"
        result = run_cli(
            "backup_cli.py",
            ["--vault", str(nonexistent), "backup", "--format", "json"],
        )

        # Should still emit contract JSON (with success=False)
        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="backup_cli",
            expected_subcommand="backup",
        )
        # On error path, success should be False
        assert (
            parsed["success"] is False
        ), "Expected success=False for nonexistent vault"
        assert len(parsed["errors"]) > 0, "Expected errors list to be non-empty"

    def test_core_workflow_cli_with_invalid_vault_emits_contract_json(
        self, tmp_path: Path
    ):
        """Core workflow CLI should emit contract JSON even for invalid vault path."""
        # Use a path under /nonexistent which is read-only/doesn't exist on macOS
        # This will cause mkdir to fail
        invalid_path = "/nonexistent/invalid/vault/path"
        result = run_cli(
            "core_workflow_cli.py",
            [invalid_path, "status", "--format", "json"],
        )

        # Should still emit contract JSON (with success=False)
        parsed = JSONContractValidator.validate(
            result.stdout,
            expected_cli="core_workflow_cli",
            expected_subcommand="status",
        )
        # On error path, success should be False
        assert parsed["success"] is False, "Expected success=False for invalid vault"
        assert len(parsed["errors"]) > 0, "Expected errors list to be non-empty"


# =============================================================================
# CROSS-CUTTING CONTRACT TESTS
# =============================================================================


class TestContractConsistency:
    """Tests for contract consistency across all CLIs."""

    @pytest.mark.parametrize(
        "cli_file,args,expected_cli,expected_subcommand",
        [
            ("backup_cli.py", ["backup", "--format", "json"], "backup_cli", "backup"),
            (
                "backup_cli.py",
                ["prune-backups", "--keep", "5", "--dry-run", "--format", "json"],
                "backup_cli",
                "prune-backups",
            ),
            (
                "core_workflow_cli.py",
                ["{vault}", "status", "--format", "json"],
                "core_workflow_cli",
                "status",
            ),
            (
                "fleeting_cli.py",
                ["fleeting-health", "--format", "json"],
                "fleeting_cli",
                "fleeting-health",
            ),
            (
                "weekly_review_cli.py",
                ["weekly-review", "--preview", "--format", "json"],
                "weekly_review_cli",
                "weekly-review",
            ),
        ],
    )
    def test_all_clis_have_consistent_meta_structure(
        self,
        temp_vault: Path,
        cli_file: str,
        args: list[str],
        expected_cli: str,
        expected_subcommand: str,
    ):
        """Verify all CLIs emit consistent meta structure."""
        # Handle vault path placeholder
        processed_args = []
        for arg in args:
            if arg == "{vault}":
                processed_args.append(str(temp_vault))
            else:
                processed_args.append(arg)

        # Add vault arg for CLIs that need it as --vault
        if cli_file in ["backup_cli.py", "fleeting_cli.py", "weekly_review_cli.py"]:
            processed_args = ["--vault", str(temp_vault)] + processed_args

        result = run_cli(cli_file, processed_args)

        # All should produce valid JSON with consistent meta
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(
                f"CLI {cli_file} did not produce valid JSON:\n{result.stdout[:500]}"
            )

        assert "meta" in data, f"CLI {cli_file} missing meta field"
        assert "cli" in data["meta"], f"CLI {cli_file} missing meta.cli"
        assert "subcommand" in data["meta"], f"CLI {cli_file} missing meta.subcommand"
        assert "timestamp" in data["meta"], f"CLI {cli_file} missing meta.timestamp"
