#!/usr/bin/env python3
"""
TDD Iteration 3 - CLI JSON Output Contract Tests

Tests for standardized JSON output schema across automation CLIs.
Part of Issue #39: Migrate Automation Scripts to Dedicated CLIs

Contract specification:
- success (bool): Whether the operation succeeded
- errors (list[str]): List of error messages (empty on success)
- data (dict): Command-specific payload
- meta (dict): Optional metadata (cli, subcommand, timestamp)

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


class TestCLIJsonOutputContract:
    """Tests for standardized JSON output contract across CLIs."""

    def _validate_contract(self, output: dict[str, Any]) -> None:
        """
        Validate that JSON output follows the contract.
        
        Required keys:
        - success (bool)
        - errors (list)
        - data (dict)
        
        Optional keys:
        - meta (dict)
        """
        # Required keys
        assert "success" in output, "JSON output must contain 'success' key"
        assert "errors" in output, "JSON output must contain 'errors' key"
        assert "data" in output, "JSON output must contain 'data' key"
        
        # Type validation
        assert isinstance(output["success"], bool), "'success' must be a boolean"
        assert isinstance(output["errors"], list), "'errors' must be a list"
        assert isinstance(output["data"], dict), "'data' must be a dict"
        
        # Validate errors list contains only strings
        for error in output["errors"]:
            assert isinstance(error, str), "Each error must be a string"
        
        # Validate meta if present
        if "meta" in output:
            assert isinstance(output["meta"], dict), "'meta' must be a dict"

    # =========================================================================
    # Backup CLI Contract Tests
    # =========================================================================
    
    def test_backup_cli_backup_success_json_contract(self, tmp_path):
        """
        Test that backup_cli.py backup --format json returns valid contract.
        
        Expected: success=True, errors=[], data contains backup_path
        """
        from src.cli.backup_cli import BackupCLI
        
        # Create a minimal vault structure
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "test.md").write_text("# Test")
        
        cli = BackupCLI(vault_path=str(vault_path))
        
        # Capture JSON output
        with patch("builtins.print") as mock_print:
            exit_code = cli.backup(output_format="json")
        
        # Parse the JSON output
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        assert len(json_calls) >= 1, "Should output JSON"
        
        output = json.loads(json_calls[0][0][0])
        
        # Validate contract
        self._validate_contract(output)
        
        # Success-specific assertions
        assert output["success"] is True
        assert output["errors"] == []
        assert "backup_path" in output["data"]
        assert exit_code == 0

    def test_backup_cli_backup_failure_json_contract(self, tmp_path):
        """
        Test that backup_cli.py returns valid contract on failure.
        
        Expected: success=False, errors contains message, exit_code != 0
        """
        from src.cli.backup_cli import BackupCLI
        
        # Create valid vault but mock backup failure
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "test.md").write_text("# Test")
        
        cli = BackupCLI(vault_path=str(vault_path))
        
        # Mock create_backup to raise an exception
        with patch.object(cli.organizer, "create_backup", side_effect=Exception("Simulated backup failure")):
            with patch("builtins.print") as mock_print:
                exit_code = cli.backup(output_format="json")
        
        # Should output JSON even on failure
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        
        assert len(json_calls) >= 1, "Should output JSON on failure"
        output = json.loads(json_calls[0][0][0])
        
        self._validate_contract(output)
        assert output["success"] is False
        assert len(output["errors"]) > 0
        assert "Simulated backup failure" in output["errors"][0]
        assert exit_code != 0

    def test_backup_cli_prune_success_json_contract(self, tmp_path):
        """
        Test that backup_cli.py prune-backups --format json returns valid contract.
        """
        from src.cli.backup_cli import BackupCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        cli = BackupCLI(vault_path=str(vault_path))
        
        with patch("builtins.print") as mock_print:
            exit_code = cli.prune_backups(keep=5, dry_run=True, output_format="json")
        
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        assert len(json_calls) >= 1, "Should output JSON"
        
        output = json.loads(json_calls[0][0][0])
        
        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert exit_code == 0

    # =========================================================================
    # Screenshot CLI Contract Tests
    # =========================================================================
    
    def test_screenshot_cli_process_dryrun_json_contract(self, tmp_path):
        """
        Test that screenshot_cli.py process --dry-run --format json returns valid contract.
        """
        from src.cli.screenshot_cli import ScreenshotCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        # Use tmp_path as fake OneDrive (empty is fine for dry-run)
        cli = ScreenshotCLI(
            vault_path=str(vault_path), 
            onedrive_path=str(tmp_path)
        )
        
        with patch("builtins.print") as mock_print:
            exit_code = cli.process_evening_screenshots(
                dry_run=True, 
                output_format="json"
            )
        
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        assert len(json_calls) >= 1, "Should output JSON"
        
        output = json.loads(json_calls[0][0][0])
        
        self._validate_contract(output)
        assert output["success"] is True
        assert output["errors"] == []
        assert exit_code == 0

    def test_screenshot_cli_unavailable_processor_json_contract(self, tmp_path):
        """
        Test JSON contract when screenshot processor is unavailable.
        
        This is NOT a failure - it's a valid state (no screenshots to process).
        """
        from src.cli.screenshot_cli import ScreenshotCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        # Non-existent OneDrive path - processor won't initialize
        cli = ScreenshotCLI(
            vault_path=str(vault_path),
            onedrive_path="/nonexistent/onedrive/path"
        )
        
        with patch("builtins.print") as mock_print:
            exit_code = cli.process_evening_screenshots(
                dry_run=False,
                output_format="json"
            )
        
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        assert len(json_calls) >= 1, "Should output JSON"
        
        output = json.loads(json_calls[0][0][0])
        
        # Validate contract - even this edge case must follow it
        self._validate_contract(output)
        # Note: success could be True (no work to do) or False (config issue)
        # The key is the contract is followed

    # =========================================================================
    # Exit Code Contract Tests
    # =========================================================================
    
    def test_exit_code_matches_success_field(self, tmp_path):
        """
        Test that exit codes are consistent with success field.
        
        success=True → exit 0
        success=False → exit non-zero
        """
        from src.cli.backup_cli import BackupCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "test.md").write_text("# Test")
        
        cli = BackupCLI(vault_path=str(vault_path))
        
        with patch("builtins.print") as mock_print:
            exit_code = cli.backup(output_format="json")
        
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        output = json.loads(json_calls[0][0][0])
        
        if output["success"]:
            assert exit_code == 0, "success=True must return exit code 0"
        else:
            assert exit_code != 0, "success=False must return non-zero exit code"

    # =========================================================================
    # Meta Field Tests (Optional but recommended)
    # =========================================================================
    
    def test_meta_field_contains_cli_info(self, tmp_path):
        """
        Test that meta field (when present) contains useful context.
        
        Expected meta keys: cli, subcommand, timestamp (all optional)
        """
        from src.cli.backup_cli import BackupCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "test.md").write_text("# Test")
        
        cli = BackupCLI(vault_path=str(vault_path))
        
        with patch("builtins.print") as mock_print:
            cli.backup(output_format="json")
        
        json_calls = [call for call in mock_print.call_args_list 
                      if call[0] and "{" in str(call[0][0])]
        output = json.loads(json_calls[0][0][0])
        
        # Meta is optional but if present, should have valid structure
        if "meta" in output:
            meta = output["meta"]
            # If these keys exist, they should be strings
            if "cli" in meta:
                assert isinstance(meta["cli"], str)
            if "subcommand" in meta:
                assert isinstance(meta["subcommand"], str)
            if "timestamp" in meta:
                assert isinstance(meta["timestamp"], str)


class TestCLILoggingContext:
    """Tests for consistent logging context at CLI startup."""
    
    def test_backup_cli_logs_context_on_init(self, tmp_path, caplog):
        """
        Test that backup CLI logs context information on initialization.
        
        Should log: CLI name, vault path
        """
        import logging
        from src.cli.backup_cli import BackupCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        with caplog.at_level(logging.INFO):
            cli = BackupCLI(vault_path=str(vault_path))
        
        # Should log vault path context
        log_text = caplog.text.lower()
        assert "vault" in log_text or str(vault_path).lower() in log_text, \
            "Should log vault path context"

    def test_screenshot_cli_logs_context_on_init(self, tmp_path, caplog):
        """
        Test that screenshot CLI logs context information on initialization.
        
        Should log: CLI name, vault path
        """
        import logging
        from src.cli.screenshot_cli import ScreenshotCLI
        
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        with caplog.at_level(logging.INFO):
            cli = ScreenshotCLI(vault_path=str(vault_path), onedrive_path=str(tmp_path))
        
        log_text = caplog.text.lower()
        assert "vault" in log_text or str(vault_path).lower() in log_text, \
            "Should log vault path context"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
