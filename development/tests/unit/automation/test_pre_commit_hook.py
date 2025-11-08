"""
Tests for Pre-commit Hook - CLI Pattern Linter Integration

RED Phase: These tests validate that a pre-commit hook can prevent commits
with CLI pattern violations, enabling automated enforcement at commit time.

The hook should:
1. Run CLI pattern linter on staged files
2. Only check files in development/src/cli/
3. Exit with code 1 if violations found (block commit)
4. Exit with code 0 if no violations (allow commit)
5. Provide clear feedback to developer
6. Be installable via script

Test Strategy:
- Test hook installation process
- Test hook execution on clean/dirty files
- Test exit codes for different scenarios
- Validate hook only runs on CLI files

These tests will FAIL until the pre-commit hook is implemented.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

import pytest

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[4]
DEV_ROOT = REPO_ROOT / "development"


class TestPreCommitHookInstallation:
    """Test pre-commit hook installation and setup."""

    def test_install_script_exists(self):
        """RED: Installation script should exist.
        
        Should provide easy way to install the hook:
        ./development/scripts/install-pre-commit-hook.sh
        
        This test will FAIL until install script is created.
        """
        install_script = DEV_ROOT / "scripts" / "install-pre-commit-hook.sh"
        
        assert install_script.exists(), (
            f"Install script should exist at {install_script}"
        )
        
        # Should be executable
        assert os.access(install_script, os.X_OK), (
            "Install script should be executable"
        )

    def test_hook_script_exists(self):
        """RED: Pre-commit hook script should exist.
        
        Hook script template at:
        development/scripts/pre-commit-hook.sh
        
        This test will FAIL until hook script is created.
        """
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        assert hook_script.exists(), (
            f"Hook script should exist at {hook_script}"
        )
        
        # Should be executable
        assert os.access(hook_script, os.X_OK), (
            "Hook script should be executable"
        )

    def test_install_script_creates_hook(self):
        """RED: Install script should copy hook to .git/hooks/pre-commit.
        
        After running install script, .git/hooks/pre-commit should:
        1. Exist
        2. Be executable
        3. Contain reference to cli_pattern_linter.py
        
        This test will FAIL until installation works correctly.
        """
        install_script = DEV_ROOT / "scripts" / "install-pre-commit-hook.sh"
        git_hooks_dir = REPO_ROOT / ".git" / "hooks"
        pre_commit_hook = git_hooks_dir / "pre-commit"
        
        # Backup existing hook if present
        backup_path = None
        if pre_commit_hook.exists():
            backup_path = pre_commit_hook.with_suffix('.backup-test')
            pre_commit_hook.rename(backup_path)
        
        try:
            # Run install script
            result = subprocess.run(
                [str(install_script)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, (
                f"Install script should succeed. Error: {result.stderr}"
            )
            
            # Hook should exist
            assert pre_commit_hook.exists(), (
                "Install script should create .git/hooks/pre-commit"
            )
            
            # Hook should be executable
            assert os.access(pre_commit_hook, os.X_OK), (
                "Installed hook should be executable"
            )
            
            # Hook should reference linter
            hook_content = pre_commit_hook.read_text()
            assert "cli_pattern_linter.py" in hook_content, (
                "Hook should reference cli_pattern_linter.py"
            )
            
        finally:
            # Restore original hook
            if pre_commit_hook.exists():
                pre_commit_hook.unlink()
            if backup_path and backup_path.exists():
                backup_path.rename(pre_commit_hook)


class TestPreCommitHookExecution:
    """Test pre-commit hook execution behavior."""

    def test_hook_allows_commit_with_no_violations(self):
        """RED: Hook should exit 0 when no violations found.
        
        When checking a compliant CLI file (like core_workflow_cli.py),
        hook should exit with code 0 to allow commit.
        
        This test will FAIL until hook execution works correctly.
        """
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        # Test with a known compliant file
        compliant_file = DEV_ROOT / "src" / "cli" / "core_workflow_cli.py"
        
        # Simulate hook execution (it checks staged files)
        # We'll test the hook script directly
        result = subprocess.run(
            [str(hook_script)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env={**os.environ, "TEST_FILES": str(compliant_file)}
        )
        
        # Hook should allow commit (exit 0) for compliant files
        assert result.returncode == 0, (
            f"Hook should exit 0 for compliant files. "
            f"Output: {result.stdout}\nError: {result.stderr}"
        )

    def test_hook_blocks_commit_with_violations(self):
        """RED: Hook should exit 1 when violations found.
        
        When checking a non-compliant CLI file, hook should:
        1. Exit with code 1 to block commit
        2. Show violation details to developer
        3. Provide actionable suggestions
        
        This test will FAIL until hook violation detection works.
        """
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        # Create a temporary non-compliant CLI file
        cli_dir = DEV_ROOT / "src" / "cli"
        temp_file = cli_dir / "test_noncompliant_cli.py"
        
        # Write non-compliant CLI (missing epilog, description)
        temp_file.write_text("""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--test')
args = parser.parse_args()
""")
        
        try:
            # Run hook on this file (use relative path from repo root)
            relative_path = temp_file.relative_to(REPO_ROOT)
            
            result = subprocess.run(
                [str(hook_script)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                env={**os.environ, "TEST_FILES": str(relative_path)}
            )
            
            # Hook should block commit (exit 1) for non-compliant files
            assert result.returncode == 1, (
                f"Hook should exit 1 for non-compliant files. "
                f"Exit code: {result.returncode}\n"
                f"Output: {result.stdout}\nError: {result.stderr}"
            )
            
            # Output should mention violations
            output = result.stdout + result.stderr
            assert "violation" in output.lower() or "blocked" in output.lower(), (
                f"Hook output should mention violations or blocking. Got: {output}"
            )
            
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    def test_hook_only_checks_cli_files(self):
        """RED: Hook should only run linter on CLI files.
        
        Should only check files in development/src/cli/*.py
        Should ignore other Python files in the repository.
        
        This test will FAIL until file filtering works correctly.
        """
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        # Test with a non-CLI Python file
        non_cli_file = DEV_ROOT / "src" / "utils" / "file_ops.py"
        
        if non_cli_file.exists():
            result = subprocess.run(
                [str(hook_script)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                env={**os.environ, "TEST_FILES": str(non_cli_file)}
            )
            
            # Hook should skip non-CLI files (exit 0)
            assert result.returncode == 0, (
                f"Hook should skip non-CLI files. "
                f"Exit code: {result.returncode}"
            )
            
            # Output should indicate file was skipped
            output = result.stdout + result.stderr
            assert "cli" in output.lower() or "skip" in output.lower(), (
                "Hook should indicate non-CLI files are skipped"
            )

    def test_hook_provides_helpful_output(self):
        """RED: Hook should provide clear feedback to developer.
        
        Output should include:
        1. Which files were checked
        2. Number of violations found
        3. How to fix violations
        4. How to bypass hook if needed (--no-verify)
        
        This test will FAIL until output formatting is implemented.
        """
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        # Run hook on a compliant file
        compliant_file = DEV_ROOT / "src" / "cli" / "safe_workflow_cli.py"
        
        result = subprocess.run(
            [str(hook_script)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env={**os.environ, "TEST_FILES": str(compliant_file)}
        )
        
        output = result.stdout + result.stderr
        
        # Should show what was checked
        assert "cli" in output.lower() or "check" in output.lower(), (
            "Output should indicate what was checked"
        )
        
        # Should be helpful
        assert len(output) > 0, (
            "Hook should provide output to developer"
        )


class TestPreCommitHookConfiguration:
    """Test pre-commit hook configuration options."""

    def test_hook_respects_config_file(self):
        """RED: Hook should respect configuration file if present.
        
        Config file at .cli-lint-config.json should allow:
        1. Disabling specific checks
        2. Setting custom thresholds
        3. Excluding specific files
        
        This test will FAIL until config support is implemented.
        """
        config_file = REPO_ROOT / ".cli-lint-config.json"
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        # Create test config that disables all checks
        test_config = {
            "enabled": False,
            "checks": {
                "vault_flag": False,
                "help_text": False,
                "naming": False,
                "boolean_flags": False
            }
        }
        
        # Backup existing config
        backup_content = None
        if config_file.exists():
            backup_content = config_file.read_text()
        
        try:
            # Write test config
            import json
            config_file.write_text(json.dumps(test_config, indent=2))
            
            # Run hook - should be disabled
            result = subprocess.run(
                [str(hook_script)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True
            )
            
            # Hook should exit 0 when disabled in config
            assert result.returncode == 0, (
                f"Hook should respect config disable. Exit code: {result.returncode}"
            )
            
            output = result.stdout + result.stderr
            assert "disabled" in output.lower() or "skipped" in output.lower(), (
                "Hook should indicate it's disabled via config"
            )
            
        finally:
            # Restore original config
            if backup_content is not None:
                config_file.write_text(backup_content)
            elif config_file.exists():
                config_file.unlink()

    def test_hook_can_be_bypassed(self):
        """RED: Hook can be bypassed with git commit --no-verify.
        
        This is a standard Git feature, but documentation should mention it.
        Test verifies hook documentation includes bypass instructions.
        
        This test will FAIL until documentation is complete.
        """
        # Check hook script has helpful comments
        hook_script = DEV_ROOT / "scripts" / "pre-commit-hook.sh"
        
        if hook_script.exists():
            hook_content = hook_script.read_text()
            
            # Should document bypass option
            assert "--no-verify" in hook_content or "bypass" in hook_content.lower(), (
                "Hook should document --no-verify bypass option"
            )
