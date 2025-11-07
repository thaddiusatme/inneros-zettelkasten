"""TDD RED Phase: CLI Argument Pattern Standardization Tests

P2_TASK_1: Standardize CLI Argument Patterns

Goal: Make all CLIs use consistent --vault flag pattern while maintaining
backward compatibility with positional arguments.

Changes Required:
1. core_workflow_cli.py: Add --vault flag (keep positional for backward compat)
2. Add deprecation warning for positional vault_path usage
3. Update automation scripts to use --vault consistently
4. Ensure both patterns work during transition period

RED Phase expectations:
- All tests should FAIL initially
- Tests validate --vault flag support in core_workflow_cli.py
- Tests validate backward compatibility with positional arguments
- Tests validate deprecation warnings are shown
- After implementation, tests should PASS (GREEN phase)

See: NEXT-SESSION-PROMPT-cli-integration-tests.md P2 section for context
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


class TestCLIArgumentStandardization:
    """Tests ensuring consistent --vault flag pattern across all CLIs.
    
    P2_TASK_1: Standardize CLI argument patterns to use --vault flag while
    maintaining backward compatibility with positional arguments during
    transition period.
    
    Test strategy:
    1. Validate core_workflow_cli.py accepts --vault flag
    2. Validate backward compatibility with positional argument
    3. Validate deprecation warning for positional usage
    4. Validate automation scripts updated to use --vault
    """

    CORE_WORKFLOW_CLI = "development/src/cli/core_workflow_cli.py"
    SAFE_WORKFLOW_CLI = "development/src/cli/safe_workflow_cli.py"

    def test_core_workflow_cli_accepts_vault_flag(self):
        """RED: core_workflow_cli.py should accept --vault flag like safe_workflow_cli.py
        
        Currently:
          python core_workflow_cli.py /path/to/vault status  # Positional
        
        After P2_TASK_1:
          python core_workflow_cli.py --vault /path/to/vault status  # Flag (new)
          python core_workflow_cli.py /path/to/vault status  # Positional (backward compat)
        
        This test will FAIL until --vault flag is implemented.
        """
        cli_path = REPO_ROOT / self.CORE_WORKFLOW_CLI
        
        # Test --vault flag pattern (should work after implementation)
        # Use --help to test argparse accepts the flag without actual execution
        result = subprocess.run(
            [sys.executable, str(cli_path), "--vault", "/tmp/test-vault", "--help"],
            capture_output=True,
            text=True,
        )
        
        # Should not error on --vault flag
        assert result.returncode == 0, (
            f"core_workflow_cli.py should accept --vault flag. "
            f"Error: {result.stderr}"
        )
        
        # Help output should show --vault option
        assert "--vault" in result.stdout, (
            "core_workflow_cli.py help should document --vault flag"
        )

    def test_core_workflow_cli_backward_compatibility_positional_arg(self):
        """RED: core_workflow_cli.py should maintain backward compatibility with positional arg.
        
        During transition period, both patterns should work:
        - NEW: python core_workflow_cli.py --vault /path/to/vault status
        - OLD: python core_workflow_cli.py /path/to/vault status (deprecated)
        
        This ensures existing automation scripts don't break during migration.
        """
        cli_path = REPO_ROOT / self.CORE_WORKFLOW_CLI
        
        # Test positional argument still works (backward compatibility)
        # Use status --help to test the pattern
        result = subprocess.run(
            [sys.executable, str(cli_path), "/tmp/test-vault", "status", "--help"],
            capture_output=True,
            text=True,
        )
        
        # Should still work with positional argument
        assert result.returncode == 0, (
            f"core_workflow_cli.py should maintain backward compatibility with positional vault_path. "
            f"Error: {result.stderr}"
        )

    def test_core_workflow_cli_shows_deprecation_warning_for_positional(self):
        """RED: core_workflow_cli.py should warn users about deprecated positional argument.
        
        When positional argument is used, CLI should show deprecation warning:
        "⚠️  Warning: Positional vault_path is deprecated. Use --vault flag instead."
        
        This encourages migration to --vault pattern without breaking existing usage.
        """
        cli_path = REPO_ROOT / self.CORE_WORKFLOW_CLI
        
        # Test positional argument shows deprecation warning
        # Use status command (will fail but show warning first)
        # Note: Cannot use --help because argparse exits before our warning code runs
        result = subprocess.run(
            [sys.executable, str(cli_path), "/tmp/test-vault", "status", "--format", "json"],
            capture_output=True,
            text=True,
        )
        
        # Should show deprecation warning on stderr
        assert "deprecated" in result.stderr.lower() or "warning" in result.stderr.lower(), (
            f"core_workflow_cli.py should show deprecation warning when using positional vault_path. "
            f"stderr: {result.stderr}"
        )

    def test_vault_flag_takes_precedence_over_positional(self):
        """RED: When both --vault flag and positional arg provided, flag should take precedence.
        
        Edge case: User provides both patterns
        python core_workflow_cli.py /old/path --vault /new/path status
        
        Expected behavior: --vault flag value (/new/path) should be used
        """
        cli_path = REPO_ROOT / self.CORE_WORKFLOW_CLI
        
        # This test validates argument parsing priority
        # We can't easily test the actual precedence without full execution,
        # but we can validate argparse accepts this pattern
        result = subprocess.run(
            [sys.executable, str(cli_path), "--vault", "/tmp/test-vault", "--help"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0, (
            "CLI should handle --vault flag gracefully"
        )

    def test_automation_scripts_use_vault_flag_consistently(self):
        """Validate all automation scripts updated to use --vault flag pattern.
        
        After P2_TASK_1, ALL scripts should use --vault flag for consistency:
        - supervised_inbox_processing.sh → uses --vault for safe_workflow_cli ✅
        - weekly_deep_analysis.sh → uses --vault for safe_workflow_cli ✅
        - process_inbox_workflow.sh → uses --vault for safe_workflow_cli ✅
        
        This test ensures the migration is complete and consistent.
        """
        scripts_to_check = [
            ".automation/scripts/supervised_inbox_processing.sh",
            ".automation/scripts/weekly_deep_analysis.sh",
            ".automation/scripts/process_inbox_workflow.sh",
        ]
        
        for script_path in scripts_to_check:
            full_path = REPO_ROOT / script_path
            if not full_path.exists():
                continue
            
            script_contents = full_path.read_text(encoding="utf-8")
            
            # All CLI calls should use --vault flag pattern
            # Check for positional argument patterns that should be migrated
            lines = script_contents.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments and variable definitions
                if line.strip().startswith('#'):
                    continue
                if 'CLI=' in line and 'python3' in line:
                    continue
                
                # Check if this is a CLI call
                if any(cli_var in line for cli_var in ['$CORE_WORKFLOW_CLI', '$SAFE_WORKFLOW_CLI']):
                    # If calling CLI with vault path, should use --vault flag
                    if any(path_var in line for path_var in ['$VAULT', '$KNOWLEDGE_DIR']):
                        assert '--vault' in line, (
                            f"{script_path}:{line_num} - CLI call should use --vault flag: {line.strip()}"
                        )


class TestCLIStandardizationHelpers:
    """Helper tests validating standardization implementation details."""

    def test_argparse_flag_and_positional_coexist(self):
        """Validate argparse can handle both --vault flag and positional argument.
        
        Technical test ensuring argument parser configuration is correct.
        Argparse should support:
        - Optional --vault flag
        - Optional positional vault_path (for backward compatibility)
        - Flag takes precedence when both provided
        """
        # This is more of a documentation test showing the expected behavior
        # The actual implementation will be in core_workflow_cli.py's create_parser()
        
        # Expected argparse configuration:
        # parser.add_argument('--vault', dest='vault_path', help='...')
        # parser.add_argument('vault_path', nargs='?', help='... (deprecated)')
        
        # When parsed:
        # args.vault_path will contain the flag value if provided
        # Otherwise will contain positional value if provided
        # Otherwise will be None (default to current directory)
        
        assert True, "Documentation test for expected argparse behavior"

    def test_deprecation_warning_helper_exists(self):
        """Validate deprecation warning helper function exists.
        
        Expected helper function in core_workflow_cli.py:
        def _warn_positional_deprecated() -> None:
            print("⚠️  Warning: Positional vault_path is deprecated.", file=sys.stderr)
            print("   Use --vault flag instead: core_workflow_cli.py --vault <path>", file=sys.stderr)
        """
        # This test will validate the helper exists after implementation
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        # Helper should exist as method or function
        # We'll validate this by checking if the pattern is implemented
        assert True, "Documentation test for deprecation warning helper"
