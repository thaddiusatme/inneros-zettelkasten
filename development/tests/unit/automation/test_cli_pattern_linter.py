"""
Tests for CLI Pattern Linter

RED Phase: These tests validate that a CLI pattern linter can detect violations
of the CLI Argument Standards documented in development/docs/CLI-ARGUMENT-STANDARDS.md

The linter should check:
1. --vault flag presence in workflow CLIs
2. Help text completeness (description, epilog with examples)
3. Argument naming conventions (lowercase-with-hyphens)
4. Boolean flags use store_true/store_false
5. Error handling patterns
6. Testing coverage

Test Strategy:
- Use real CLI files as test subjects (core_workflow_cli.py, safe_workflow_cli.py)
- Parse Python AST to analyze argparse patterns
- Validate against standards document requirements
- Report violations with file:line references

These tests will FAIL until the linter is implemented.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[4]
DEV_ROOT = REPO_ROOT / "development"

# Add scripts directory to path for imports
SCRIPTS_DIR = DEV_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class TestCLIPatternLinter:
    """Test CLI pattern linter validates standards compliance."""

    # CLI files to validate
    WORKFLOW_CLIS = [
        "development/src/cli/core_workflow_cli.py",
        "development/src/cli/safe_workflow_cli.py",
    ]

    def test_linter_can_parse_cli_files(self):
        """RED: Linter should parse Python CLI files using AST.
        
        Must be able to:
        1. Read CLI file contents
        2. Parse Python AST
        3. Identify argparse usage
        4. Extract argument definitions
        
        This test will FAIL until CLIPatternLinter class is created.
        """
        # Import will fail initially
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        for cli_file in self.WORKFLOW_CLIS:
            cli_path = REPO_ROOT / cli_file
            assert cli_path.exists(), f"CLI file not found: {cli_path}"
            
            # Should be able to parse the file
            parser_info = linter.parse_cli_file(cli_path)
            
            # Should extract basic info
            assert parser_info is not None, f"Failed to parse {cli_file}"
            assert "arguments" in parser_info, "Should extract arguments"
            assert "has_subparsers" in parser_info, "Should detect subparsers"

    def test_linter_detects_vault_flag_pattern(self):
        """RED: Linter should validate --vault flag in workflow CLIs.
        
        Per CLI-ARGUMENT-STANDARDS.md:
        - Workflow CLIs MUST have --vault flag
        - Should check for add_argument('--vault', ...)
        - Should report violation if missing
        
        This test will FAIL until vault flag validation is implemented.
        """
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        # Both workflow CLIs should have --vault flag
        for cli_file in self.WORKFLOW_CLIS:
            cli_path = REPO_ROOT / cli_file
            violations = linter.check_vault_flag(cli_path)
            
            # Should have no violations (both CLIs implement --vault)
            assert len(violations) == 0, (
                f"{cli_file} should have --vault flag. "
                f"Violations: {violations}"
            )

    def test_linter_validates_help_text_completeness(self):
        """RED: Linter should validate help text quality.
        
        Per CLI-ARGUMENT-STANDARDS.md:
        - ArgumentParser must have description
        - Should have epilog with usage examples
        - Subcommands should have help text
        
        This test will FAIL until help text validation is implemented.
        """
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        for cli_file in self.WORKFLOW_CLIS:
            cli_path = REPO_ROOT / cli_file
            violations = linter.check_help_text(cli_path)
            
            # Should have no violations (both CLIs have good help)
            assert len(violations) == 0, (
                f"{cli_file} should have complete help text. "
                f"Violations: {violations}"
            )

    def test_linter_validates_argument_naming_conventions(self):
        """RED: Linter should validate argument names follow conventions.
        
        Per CLI-ARGUMENT-STANDARDS.md:
        - Use lowercase-with-hyphens (--dry-run, not --dry_run or --dryRun)
        - Boolean flags should use store_true/store_false
        - Avoid abbreviations unless standard (-v for --verbose)
        
        This test will FAIL until naming validation is implemented.
        """
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        for cli_file in self.WORKFLOW_CLIS:
            cli_path = REPO_ROOT / cli_file
            violations = linter.check_naming_conventions(cli_path)
            
            # Should have minimal violations
            # (our CLIs follow conventions, but allow some flexibility)
            assert len(violations) == 0, (
                f"{cli_file} should follow naming conventions. "
                f"Violations: {violations}"
            )

    def test_linter_validates_boolean_flag_patterns(self):
        """RED: Linter should validate boolean flags use store_true/store_false.
        
        Per CLI-ARGUMENT-STANDARDS.md:
        - Boolean flags should use action='store_true' or action='store_false'
        - Should not use type=bool (causes confusion)
        
        This test will FAIL until boolean flag validation is implemented.
        """
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        for cli_file in self.WORKFLOW_CLIS:
            cli_path = REPO_ROOT / cli_file
            violations = linter.check_boolean_flags(cli_path)
            
            # Should have no violations (our CLIs use store_true correctly)
            assert len(violations) == 0, (
                f"{cli_file} should use store_true for boolean flags. "
                f"Violations: {violations}"
            )

    def test_linter_generates_comprehensive_report(self):
        """RED: Linter should generate report with all violations.
        
        Report should include:
        - File path
        - Line number
        - Violation type
        - Violation message
        - Suggestion for fix
        
        This test will FAIL until report generation is implemented.
        """
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        for cli_file in self.WORKFLOW_CLIS:
            cli_path = REPO_ROOT / cli_file
            report = linter.generate_report(cli_path)
            
            # Report should have standard structure
            assert "file" in report, "Report should include file path"
            assert "violations" in report, "Report should include violations list"
            assert "summary" in report, "Report should include summary"
            
            # Summary should have counts
            summary = report["summary"]
            assert "total_checks" in summary, "Summary should count checks"
            assert "total_violations" in summary, "Summary should count violations"
            assert "compliance_percentage" in summary, "Summary should show compliance %"

    def test_linter_can_validate_all_cli_files(self):
        """RED: Linter should validate all CLI files in src/cli/ directory.
        
        Should:
        1. Scan development/src/cli/ for *.py files
        2. Identify files with argparse usage
        3. Run all checks on each CLI
        4. Generate consolidated report
        
        This test will FAIL until batch validation is implemented.
        """
        from cli_pattern_linter import CLIPatternLinter
        
        linter = CLIPatternLinter()
        
        cli_dir = DEV_ROOT / "src" / "cli"
        assert cli_dir.exists(), f"CLI directory not found: {cli_dir}"
        
        # Should find multiple CLI files
        results = linter.validate_directory(cli_dir)
        
        assert "files_checked" in results, "Should report files checked"
        assert "total_violations" in results, "Should report total violations"
        assert "reports" in results, "Should include individual reports"
        
        # Should check at least our known workflow CLIs
        files_checked = results["files_checked"]
        assert files_checked >= 2, f"Should check at least 2 CLIs, found {files_checked}"


class TestCLIPatternLinterCLI:
    """Test CLI interface for the linter."""

    def test_linter_has_cli_interface(self):
        """RED: Linter should have command-line interface.
        
        Should support:
        - python cli_pattern_linter.py <file>  # Check single file
        - python cli_pattern_linter.py --dir <dir>  # Check directory
        - python cli_pattern_linter.py --all  # Check all CLIs
        - --format json|text  # Output format
        - --fail-on-violations  # Exit 1 if violations found (for CI)
        
        This test will FAIL until CLI interface is implemented.
        """
        import subprocess
        import sys
        
        linter_script = DEV_ROOT / "scripts" / "cli_pattern_linter.py"
        
        # Should be able to run with --help
        result = subprocess.run(
            [sys.executable, str(linter_script), "--help"],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0, f"Linter --help failed: {result.stderr}"
        assert "--dir" in result.stdout, "Should have --dir option"
        assert "--format" in result.stdout, "Should have --format option"
        assert "--fail-on-violations" in result.stdout, "Should have --fail-on-violations option"

    def test_linter_can_check_single_file(self):
        """RED: Linter should check a single CLI file.
        
        Usage: python cli_pattern_linter.py path/to/cli.py
        
        This test will FAIL until single-file checking is implemented.
        """
        import subprocess
        import sys
        
        linter_script = DEV_ROOT / "scripts" / "cli_pattern_linter.py"
        test_cli = REPO_ROOT / "development/src/cli/core_workflow_cli.py"
        
        result = subprocess.run(
            [sys.executable, str(linter_script), str(test_cli)],
            capture_output=True,
            text=True,
        )
        
        # Should complete successfully (our CLIs are compliant)
        assert result.returncode == 0, f"Linter failed: {result.stderr}"
        assert "Checking" in result.stdout, "Should show file being checked"
        assert "violations" in result.stdout.lower(), "Should report violations count"

    def test_linter_json_output_format(self):
        """RED: Linter should support JSON output for automation.
        
        Usage: python cli_pattern_linter.py --format json path/to/cli.py
        
        This test will FAIL until JSON output is implemented.
        """
        import json
        import subprocess
        import sys
        
        linter_script = DEV_ROOT / "scripts" / "cli_pattern_linter.py"
        test_cli = REPO_ROOT / "development/src/cli/core_workflow_cli.py"
        
        result = subprocess.run(
            [sys.executable, str(linter_script), "--format", "json", str(test_cli)],
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0, f"Linter failed: {result.stderr}"
        
        # Should be valid JSON
        output = json.loads(result.stdout)
        assert "file" in output, "JSON should include file path"
        assert "violations" in output, "JSON should include violations"
        assert "summary" in output, "JSON should include summary"
