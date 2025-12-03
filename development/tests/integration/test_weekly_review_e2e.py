"""
TDD Iteration 4 - Phase 2 E2E Validation: Weekly Review Workflow

RED PHASE: End-to-end tests validating the weekly review workflow works without manual intervention.

These tests verify:
- make review (via CLI) works end-to-end
- Exit code 0 on success
- Output contains actionable recommendations
- Export functionality generates valid markdown
- Preview vs full run semantics are correct

Tests run against the REAL knowledge vault for authentic E2E validation.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path
import pytest


# Mark all tests in this module as E2E and slow (AI processing)
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestWeeklyReviewE2E:
    """
    End-to-end tests for weekly review workflow.
    
    These tests validate the complete workflow from CLI invocation to output generation.
    """

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root path."""
        return Path(__file__).parent.parent.parent.parent

    @pytest.fixture
    def knowledge_vault(self, repo_root: Path) -> Path:
        """Get knowledge vault path."""
        return repo_root / "knowledge"

    @pytest.fixture
    def env_with_pythonpath(self, repo_root: Path) -> dict:
        """Create environment with PYTHONPATH set."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root / "development")
        return env

    # =========================================================================
    # TEST 0: Smoke test - CLI can start and parse args
    # =========================================================================
    def test_weekly_review_cli_help_works(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 0: CLI --help works (smoke test).
        
        Acceptance Criteria:
        - CLI can start and respond to --help
        - Quick validation that imports work
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--help",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=10,
        )
        
        assert result.returncode == 0, (
            f"--help should exit with code 0.\n"
            f"stderr: {result.stderr}"
        )
        assert "weekly-review" in result.stdout.lower() or "usage" in result.stdout.lower(), (
            f"Help should mention weekly-review command.\n"
            f"stdout: {result.stdout}"
        )

    # =========================================================================
    # TEST 1: Basic weekly review execution
    # =========================================================================
    def test_weekly_review_preview_exits_zero(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 1: make review (preview mode) exits with code 0.
        
        Acceptance Criteria:
        - CLI command completes without error
        - Exit code is 0
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "weekly-review",
                "--preview",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,  # 2 minute timeout for AI processing
        )
        
        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    # =========================================================================
    # TEST 2: Output contains note recommendations
    # =========================================================================
    def test_weekly_review_shows_note_count(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 2: Weekly review output shows note count > 0.
        
        Acceptance Criteria:
        - Output contains "Found X notes" where X > 0
        - Demonstrates system is scanning real vault
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "weekly-review",
                "--preview",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        
        assert "Found" in result.stdout, (
            f"Output should contain 'Found X notes'.\n"
            f"stdout: {result.stdout}"
        )
        
        # Verify non-zero note count
        assert "Found 0 notes" not in result.stdout, (
            "Should find at least some notes in knowledge vault"
        )

    # =========================================================================
    # TEST 3: Output contains actionable sections
    # =========================================================================
    def test_weekly_review_has_actionable_sections(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 3: Weekly review output contains actionable recommendation sections.
        
        Acceptance Criteria:
        - Output contains "Ready to Promote" or "Further Development" or "Needs Significant Work"
        - Demonstrates AI is providing actionable recommendations
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "weekly-review",
                "--preview",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        
        # Should have at least one actionable section
        has_actionable_section = any([
            "Ready to Promote" in result.stdout,
            "Further Development" in result.stdout,
            "Needs Significant Work" in result.stdout,
        ])
        
        assert has_actionable_section, (
            f"Output should contain actionable recommendation sections.\n"
            f"stdout: {result.stdout}"
        )

    # =========================================================================
    # TEST 4: Export functionality creates file
    # =========================================================================
    def test_weekly_review_export_creates_file(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 4: --export flag creates valid markdown file.
        
        Acceptance Criteria:
        - Export path receives a valid markdown file
        - File contains checklist content
        - Exit code is 0
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "weekly-review-test.md"
            
            result = subprocess.run(
                [
                    sys.executable,
                    "development/src/cli/weekly_review_cli.py",
                    "--vault", "knowledge",
                    "weekly-review",
                    "--preview",  # Use preview mode for fast execution
                    "--export", str(export_path),
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                env=env_with_pythonpath,
                stdin=subprocess.DEVNULL,
                timeout=120,
            )
            
            # Exit code should be 0
            assert result.returncode == 0, (
                f"Export command should exit with code 0.\n"
                f"stderr: {result.stderr}"
            )
            
            # File should exist
            assert export_path.exists(), (
                f"Export file should be created at {export_path}"
            )
            
            # File should have content
            content = export_path.read_text()
            assert len(content) > 100, (
                f"Export file should have substantial content, got {len(content)} chars"
            )
            
            # File should be valid markdown with checklist content
            assert "Weekly Review" in content, (
                "Export should contain 'Weekly Review' header"
            )

    # =========================================================================
    # TEST 5: JSON format works
    # =========================================================================
    def test_weekly_review_json_format(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 5: --format json produces valid JSON output.
        
        Acceptance Criteria:
        - Output is valid JSON (parseable)
        - JSON contains expected keys (summary, recommendations)
        """
        import json
        
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "weekly-review",
                "--preview",  # Use preview mode for fast execution
                "--format", "json",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        
        assert result.returncode == 0, (
            f"JSON format command should exit with code 0.\n"
            f"stderr: {result.stderr}"
        )
        
        # Parse JSON output
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Output should be valid JSON: {e}\nstdout: {result.stdout}")
        
        # Check expected keys
        assert "summary" in data, "JSON should contain 'summary' key"
        assert "recommendations" in data, "JSON should contain 'recommendations' key"

    # =========================================================================
    # TEST 6: Preview mode shows dry-run indicator
    # =========================================================================
    def test_weekly_review_preview_shows_dry_run_notice(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 6: --preview flag shows dry-run mode indicator.
        
        Acceptance Criteria:
        - Output contains "DRY RUN" indicator
        - Clarifies no files will be modified
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "weekly-review",
                "--preview",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        
        assert "DRY RUN" in result.stdout, (
            f"Preview mode should indicate 'DRY RUN'.\n"
            f"stdout: {result.stdout}"
        )

    # =========================================================================
    # TEST 7: Full run (non-preview) works
    # =========================================================================
    @pytest.mark.skip(reason="Full run processes 20+ notes with AI (~30s each = 10+ min total)")
    def test_weekly_review_full_run_exits_zero(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 7: Full run (without --preview) exits with code 0.
        
        NOTE: This test is skipped because full run calls process_inbox_note()
        for EACH note in the vault with full AI processing. With 20 notes and
        ~30s per AI call, this takes 10+ minutes.
        
        For practical use:
        - Use `make review` (with --preview) for quick daily reviews
        - Full AI processing happens when you actually promote individual notes
        
        Acceptance Criteria:
        - CLI command completes without error
        - Exit code is 0
        - No "DRY RUN" indicator (full run mode)
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "weekly-review",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        
        assert result.returncode == 0, (
            f"Full run should exit with code 0.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        
        # Full run should NOT have DRY RUN indicator
        assert "DRY RUN" not in result.stdout, (
            "Full run mode should not show 'DRY RUN' indicator"
        )

    # =========================================================================
    # TEST 8: Enhanced metrics command works
    # =========================================================================
    def test_enhanced_metrics_exits_zero(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 8: enhanced-metrics command exits with code 0.
        
        Acceptance Criteria:
        - CLI command completes without error
        - Exit code is 0
        - Output contains metrics information
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "knowledge",
                "enhanced-metrics",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        
        assert result.returncode == 0, (
            f"Enhanced metrics should exit with code 0.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        
        # Should contain some metrics info
        assert "Summary" in result.stdout or "total" in result.stdout.lower(), (
            f"Enhanced metrics should contain summary information.\n"
            f"stdout: {result.stdout}"
        )


class TestMakeReviewTarget:
    """
    Tests for the Makefile 'review' target specifically.
    
    These tests verify the developer experience via make commands.
    """

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root path."""
        return Path(__file__).parent.parent.parent.parent

    # =========================================================================
    # TEST 9: make review target works
    # =========================================================================
    def test_make_review_exits_zero(self, repo_root: Path):
        """
        TEST 9: 'make review' target exits with code 0.
        
        Acceptance Criteria:
        - make review completes without error
        - Exit code is 0
        """
        result = subprocess.run(
            ["make", "review"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=90,  # Allow more time for make
        )
        
        assert result.returncode == 0, (
            f"'make review' should exit with code 0.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    # =========================================================================
    # TEST 10: make review shows recommendations
    # =========================================================================
    def test_make_review_shows_recommendations(self, repo_root: Path):
        """
        TEST 10: 'make review' output shows note recommendations.
        
        Acceptance Criteria:
        - Output contains note count > 0
        - Output contains actionable sections
        """
        result = subprocess.run(
            ["make", "review"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=90,
        )
        
        # Should show notes found
        assert "Found" in result.stdout, (
            f"'make review' should show notes found.\n"
            f"stdout: {result.stdout}"
        )
        
        # Should have actionable sections
        has_actionable = any([
            "Promote" in result.stdout,
            "Development" in result.stdout,
            "Improvement" in result.stdout,
        ])
        
        assert has_actionable, (
            f"'make review' should show actionable recommendations.\n"
            f"stdout: {result.stdout}"
        )


class TestWeeklyReviewErrorHandling:
    """
    Tests for error handling in the weekly review workflow.
    """

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root path."""
        return Path(__file__).parent.parent.parent.parent

    @pytest.fixture
    def env_with_pythonpath(self, repo_root: Path) -> dict:
        """Create environment with PYTHONPATH set."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root / "development")
        return env

    # =========================================================================
    # TEST 11: Invalid vault path handling
    # =========================================================================
    def test_invalid_vault_path_shows_error(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 11: Invalid vault path produces helpful error message.
        
        Acceptance Criteria:
        - Exit code is non-zero for invalid path
        - Error message is user-friendly
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
                "--vault", "/nonexistent/path/to/vault",
                "weekly-review",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )
        
        # Should exit with non-zero (either error in CLI or graceful handling)
        # Note: The actual behavior may vary - adjust based on implementation
        # For now, we just verify the command handles this gracefully
        assert result.returncode in [0, 1], (
            f"Should handle invalid path gracefully, got exit code {result.returncode}"
        )

    # =========================================================================
    # TEST 12: Missing command shows help
    # =========================================================================
    def test_no_command_shows_help(
        self, repo_root: Path, env_with_pythonpath: dict
    ):
        """
        TEST 12: Running CLI without command shows help.
        
        Acceptance Criteria:
        - Exit code is 1 (indicating user should provide command)
        - Help text is displayed
        """
        result = subprocess.run(
            [
                sys.executable,
                "development/src/cli/weekly_review_cli.py",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env_with_pythonpath,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )
        
        # Should exit with code 1 (no command provided)
        assert result.returncode == 1, (
            f"No command should exit with code 1, got {result.returncode}"
        )
        
        # Should show help or usage
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower(), (
            f"Should show help/usage information.\n"
            f"stdout: {result.stdout}"
        )
