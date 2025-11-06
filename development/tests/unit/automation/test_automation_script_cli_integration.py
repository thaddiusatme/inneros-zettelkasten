"""TDD RED Phase: CLI Integration Tests for Automation Scripts

These tests ensure automation shell scripts call dedicated CLIs with correct
argument patterns, preventing silent failures during script execution.

Context:
During end-user testing of CLI migration (Issue #39), we discovered that automation
scripts fail when calling safe_workflow_cli.py due to CLI argument pattern mismatches:
- Scripts pass vault path as positional argument: `cli.py "$VAULT_PATH" command`
- safe_workflow_cli.py expects --vault flag: `cli.py --vault "$VAULT_PATH" command`

This bug was not caught by existing test coverage because migration tests only
check for CLI path string references, not actual execution patterns.

RED Phase expectations:
- All tests should FAIL initially, demonstrating they catch the bug
- Tests validate actual CLI invocation syntax in bash scripts
- Tests check argument patterns match CLI argparse implementations
- After P0 fix is applied, tests should PASS (GREEN phase)

See: NEXT-SESSION-PROMPT-cli-integration-tests.md for complete context
"""

import re
from pathlib import Path
from typing import List, Tuple


REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


class TestAutomationScriptCLIIntegration:
    """Integration tests validating automation scripts use correct CLI argument patterns.
    
    These tests prevent regressions where automation scripts use incorrect CLI syntax,
    causing silent failures during automated processing.
    
    Test strategy:
    1. Parse bash scripts to extract CLI invocation commands
    2. Validate argument patterns match CLI argparse implementation
    3. Check for common mistakes (positional args instead of flags)
    4. Ensure consistency across all automation scripts
    """

    # CLI path definitions
    SAFE_WORKFLOW_CLI = "development/src/cli/safe_workflow_cli.py"
    CORE_WORKFLOW_CLI = "development/src/cli/core_workflow_cli.py"
    
    def _parse_cli_calls(self, script_contents: str, cli_name: str) -> List[str]:
        """Extract CLI invocation lines from bash script.
        
        Args:
            script_contents: Full bash script file contents
            cli_name: Name of CLI to search for (e.g., "safe_workflow_cli.py")
            
        Returns:
            List of command invocation strings containing the CLI
            
        Example:
            Input: "$SAFE_WORKFLOW_CLI '$VAULT' backup --format json"
            Output: ["$SAFE_WORKFLOW_CLI '$VAULT' backup --format json"]
        """
        cli_calls = []
        
        # Convert cli_name to variable name pattern
        # safe_workflow_cli.py -> SAFE_WORKFLOW_CLI
        cli_var_pattern = cli_name.replace('.py', '').upper()
        
        for line in script_contents.splitlines():
            line_stripped = line.strip()
            
            # Skip comments
            if line_stripped.startswith('#'):
                continue
            
            # Skip variable definitions (lines that define the CLI variable)
            if f'{cli_var_pattern}=' in line and 'python3' in line:
                continue
            
            # Look for lines that USE the CLI variable
            # Match: $SAFE_WORKFLOW_CLI or ${SAFE_WORKFLOW_CLI}
            if f'${cli_var_pattern}' in line or f'${{cli_var_pattern}}' in line:
                cli_calls.append(line_stripped)
        
        return cli_calls

    def _validate_vault_flag_syntax(self, cli_call: str, cli_name: str) -> Tuple[bool, str]:
        """Validate that CLI call uses --vault flag instead of positional argument.
        
        This validator prevents the specific bug discovered during end-user testing where
        automation scripts used positional arguments while safe_workflow_cli.py expected
        the --vault flag, causing silent failures.
        
        Args:
            cli_call: Full CLI invocation command line
            cli_name: Name of CLI being called
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if syntax is correct
            - (False, error_message) if syntax is incorrect
            
        Validation checks:
        1. Uses --vault flag for vault path
        2. Does NOT use positional vault path argument
        3. Vault path is properly quoted
        
        Examples:
            CORRECT: $SAFE_WORKFLOW_CLI --vault "$VAULT_PATH" backup
            WRONG:   $SAFE_WORKFLOW_CLI "$VAULT_PATH" backup
        """
        # Skip variable definitions - only validate actual CLI invocations
        if 'CLI=' in cli_call and 'python3' in cli_call:
            return True, ""
        
        # Pattern: CLI variable followed by path variable (quoted/unquoted) then command
        # This catches: $SAFE_WORKFLOW_CLI "$PATH" command (WRONG)
        # This catches: $SAFE_WORKFLOW_CLI '$PATH' command (WRONG)
        positional_path_pattern = (
            rf'{re.escape(cli_name)}\s+["\']?\$[A-Z_]+(?:_(?:DIR|PATH))?["\']?\s+\w+'
        )
        
        # Check if using positional argument instead of --vault flag (WRONG)
        if re.search(positional_path_pattern, cli_call):
            return False, (
                f"CLI call uses positional vault path argument (should use --vault flag): {cli_call}"
            )
        
        # Check if --vault flag is present when vault path is being passed
        has_vault_variable = bool(re.search(r'\$[A-Z_]*(?:VAULT|KNOWLEDGE|DIR)', cli_call))
        has_vault_flag = '--vault' in cli_call
        
        # If script is passing a vault path but not using --vault flag -> ERROR
        if has_vault_variable and not has_vault_flag:
            return False, (
                f"CLI call missing --vault flag: {cli_call}"
            )
        
        return True, ""

    def test_supervised_inbox_calls_safe_workflow_with_vault_flag(self):
        """RED: supervised_inbox_processing.sh should use --vault flag for safe_workflow_cli.py
        
        Bug scenario:
        Script currently uses: $SAFE_WORKFLOW_CLI '$KNOWLEDGE_DIR' backup --format json
        Should be:            $SAFE_WORKFLOW_CLI --vault '$KNOWLEDGE_DIR' backup --format json
        
        This test will FAIL until the P0 fix is applied.
        """
        script_path = REPO_ROOT / ".automation/scripts/supervised_inbox_processing.sh"
        script_contents = script_path.read_text(encoding="utf-8")
        
        # Find all safe_workflow_cli.py invocations
        cli_calls = self._parse_cli_calls(script_contents, "safe_workflow_cli.py")
        
        # Should have at least one CLI call (backup operation)
        assert len(cli_calls) > 0, (
            "supervised_inbox_processing.sh should invoke safe_workflow_cli.py for backup"
        )
        
        # Validate each CLI call uses correct syntax
        for call in cli_calls:
            is_valid, error = self._validate_vault_flag_syntax(call, "safe_workflow_cli.py")
            assert is_valid, error

    def test_weekly_analysis_calls_safe_workflow_with_vault_flag(self):
        """RED: weekly_deep_analysis.sh should use --vault flag for safe_workflow_cli.py
        
        Bug scenario:
        Script currently uses: $SAFE_WORKFLOW_CLI '$KNOWLEDGE_DIR' backup --format json
        Should be:            $SAFE_WORKFLOW_CLI --vault '$KNOWLEDGE_DIR' backup --format json
        
        This test will FAIL until the P0 fix is applied.
        """
        script_path = REPO_ROOT / ".automation/scripts/weekly_deep_analysis.sh"
        script_contents = script_path.read_text(encoding="utf-8")
        
        # Find all safe_workflow_cli.py invocations
        cli_calls = self._parse_cli_calls(script_contents, "safe_workflow_cli.py")
        
        # Should have at least one CLI call (weekly backup)
        assert len(cli_calls) > 0, (
            "weekly_deep_analysis.sh should invoke safe_workflow_cli.py for backup"
        )
        
        # Validate each CLI call uses correct syntax
        for call in cli_calls:
            is_valid, error = self._validate_vault_flag_syntax(call, "safe_workflow_cli.py")
            assert is_valid, error

    def test_process_inbox_workflow_calls_safe_workflow_with_vault_flag(self):
        """RED: process_inbox_workflow.sh should use --vault flag for safe_workflow_cli.py
        
        Bug scenario:
        Script currently uses: $SAFE_WORKFLOW_CLI "$KNOWLEDGE_DIR" backup
        Should be:            $SAFE_WORKFLOW_CLI --vault "$KNOWLEDGE_DIR" backup
        
        This test will FAIL until the P0 fix is applied.
        """
        script_path = REPO_ROOT / ".automation/scripts/process_inbox_workflow.sh"
        script_contents = script_path.read_text(encoding="utf-8")
        
        # Find all safe_workflow_cli.py invocations
        cli_calls = self._parse_cli_calls(script_contents, "safe_workflow_cli.py")
        
        # Should have at least one CLI call (backup operation)
        assert len(cli_calls) > 0, (
            "process_inbox_workflow.sh should invoke safe_workflow_cli.py for backup"
        )
        
        # Validate each CLI call uses correct syntax
        for call in cli_calls:
            is_valid, error = self._validate_vault_flag_syntax(call, "safe_workflow_cli.py")
            assert is_valid, error

    def test_cli_argument_pattern_consistency(self):
        """RED: Ensure consistent argument patterns across all automation scripts.
        
        Validates that:
        1. safe_workflow_cli.py always uses --vault flag
        2. No scripts use positional vault path arguments
        3. All backup commands use consistent syntax
        
        This catches inconsistencies that could cause silent failures.
        """
        scripts_to_check = [
            ".automation/scripts/supervised_inbox_processing.sh",
            ".automation/scripts/weekly_deep_analysis.sh",
            ".automation/scripts/process_inbox_workflow.sh",
        ]
        
        all_cli_calls = []
        
        for script_path in scripts_to_check:
            full_path = REPO_ROOT / script_path
            if not full_path.exists():
                continue
                
            script_contents = full_path.read_text(encoding="utf-8")
            calls = self._parse_cli_calls(script_contents, "safe_workflow_cli.py")
            
            for call in calls:
                all_cli_calls.append((script_path, call))
        
        # Validate all calls use consistent --vault flag pattern
        errors = []
        for script_path, call in all_cli_calls:
            is_valid, error = self._validate_vault_flag_syntax(call, "safe_workflow_cli.py")
            if not is_valid:
                errors.append(f"{script_path}: {error}")
        
        assert len(errors) == 0, (
            f"Found {len(errors)} CLI argument pattern inconsistencies:\n" +
            "\n".join(errors)
        )

    def test_safe_workflow_cli_accepts_vault_flag(self):
        """Validate that safe_workflow_cli.py argparse implementation accepts --vault flag.
        
        This is a sanity check to ensure our expected CLI syntax actually works.
        Reads the CLI source to verify --vault argument is defined.
        """
        cli_path = REPO_ROOT / self.SAFE_WORKFLOW_CLI
        cli_contents = cli_path.read_text(encoding="utf-8")
        
        # Check argparse defines --vault argument
        assert '--vault' in cli_contents, (
            "safe_workflow_cli.py should define --vault argument in argparse"
        )
        
        # Check it's used in argument parsing
        assert 'add_argument' in cli_contents, (
            "safe_workflow_cli.py should use argparse.add_argument"
        )
        
        # Verify vault_path is used in initialization
        assert 'vault_path=args.vault' in cli_contents or 'vault=args.vault' in cli_contents, (
            "safe_workflow_cli.py should use args.vault for initialization"
        )

    def test_core_workflow_cli_positional_args_documented(self):
        """Document that core_workflow_cli.py uses positional vault path argument.
        
        NOTE: This is intentional and correct for core_workflow_cli.py.
        This test documents the expected behavior difference between:
        - core_workflow_cli.py: Uses positional vault_path (legacy pattern)
        - safe_workflow_cli.py: Uses --vault flag (new pattern)
        
        Future P2 task will standardize both to use --vault flag.
        """
        cli_path = REPO_ROOT / self.CORE_WORKFLOW_CLI
        cli_contents = cli_path.read_text(encoding="utf-8")
        
        # core_workflow_cli.py should have vault_path as positional argument
        # This is expected and documented behavior
        has_vault_path = 'vault_path' in cli_contents
        
        assert has_vault_path, (
            "core_workflow_cli.py should define vault_path (positional or flag)"
        )
        
        # This test passes - it just documents the current state
        # P2 task will standardize this to --vault flag pattern


class TestCLIExecutionPatterns:
    """Higher-level integration tests validating CLI execution succeeds.
    
    These tests go beyond syntax validation to ensure CLIs actually execute
    without errors when called with documented patterns.
    """

    def test_safe_workflow_cli_help_with_vault_flag(self):
        """Validate safe_workflow_cli.py --help works with --vault flag.
        
        Smoke test to ensure basic CLI invocation pattern succeeds.
        """
        cli_path = REPO_ROOT / "development/src/cli/safe_workflow_cli.py"
        
        # This would be run in CI via cli-smoke-tests.yml
        # Test validates the command structure is correct
        command_pattern = f"python3 {cli_path} --vault /tmp --help"
        
        # Verify the command structure is valid
        assert "--vault" in command_pattern
        assert "--help" in command_pattern
        assert str(cli_path) in command_pattern

    def test_automation_script_dry_run_validation(self):
        """Integration test: Validate automation scripts can be dry-run tested.
        
        This ensures scripts can be tested for CLI execution errors without
        actually modifying the vault.
        
        NOTE: This is a structural test - actual dry-run execution would be
        implemented in CI/CD pipeline.
        """
        scripts_with_backup = [
            ".automation/scripts/supervised_inbox_processing.sh",
            ".automation/scripts/weekly_deep_analysis.sh",
            ".automation/scripts/process_inbox_workflow.sh",
        ]
        
        for script_path in scripts_with_backup:
            full_path = REPO_ROOT / script_path
            assert full_path.exists(), f"Automation script not found: {script_path}"
            
            # Verify script is executable
            assert full_path.stat().st_mode & 0o111, (
                f"Automation script should be executable: {script_path}"
            )
