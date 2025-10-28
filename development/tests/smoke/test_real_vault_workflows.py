"""
Smoke Tests - Real Vault Validation (TDD Iteration 6, Week 2)

⚠️  CRITICAL SAFETY REQUIREMENT ⚠️
====================================
ALL smoke tests MUST use --dry-run or READ-ONLY operations!
NEVER mutate production vault data in smoke tests!

Safety Rules:
1. Always use --dry-run flag for any write operations
2. Never modify files directly
3. Use file modification time checks to verify no mutations
4. If testing write operations, use a COPY of production vault

These tests validate real-world scenarios with the production vault.
They run NIGHTLY (not on every commit) and take minutes, not seconds.

Purpose:
- Validate against actual 300+ note production vault (READ-ONLY)
- Test edge cases that controlled test data might miss
- Verify performance with real vault size
- Ensure workflows work with actual user data (WITHOUT MODIFYING)

Performance: 5-10 minutes (acceptable for nightly runs)
Markers: @pytest.mark.smoke + @pytest.mark.slow
Command: pytest -m smoke -v

Part of Testing Infrastructure Revamp Week 2 (Oct 14-18, 2025)
"""

import subprocess
import time
from pathlib import Path
from typing import Optional

import pytest

# Production vault location
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"


def get_production_vault() -> Optional[Path]:
    """
    Get production vault path, skip test if unavailable.

    This enables smoke tests to run in environments without production data
    (e.g., CI/CD, fresh checkouts, teammate machines).
    """
    if not KNOWLEDGE_DIR.exists():
        pytest.skip(f"Production vault not available at {KNOWLEDGE_DIR}")

    if not (KNOWLEDGE_DIR / "Inbox").exists():
        pytest.skip("Production vault incomplete (missing Inbox/)")

    return KNOWLEDGE_DIR


@pytest.mark.smoke
@pytest.mark.slow
class TestWeeklyReviewProduction:
    """
    Smoke tests for weekly review command with production vault.

    RED Phase: These tests should fail initially because:
    - Weekly review CLI might not handle 300+ notes correctly
    - Performance baselines not yet established
    - Need to verify real-world edge cases
    """

    @pytest.fixture
    def production_vault(self):
        """Fixture providing production vault with skip if unavailable."""
        return get_production_vault()

    def test_weekly_review_on_production_vault(self, production_vault):
        """
        RED Phase: Validate weekly review command against actual vault.

        SAFETY: Uses --dry-run to prevent data mutation!

        This test should initially fail to drive:
        - Performance validation (should complete in reasonable time)
        - Real note parsing (handle all edge cases in production)
        - Output validation (verify meaningful results)

        Expected: Should process 300+ notes and complete in <5 minutes
        """
        start_time = time.time()

        # ⚠️ CRITICAL: Always use --dry-run with production vault!
        result = subprocess.run(
            [
                "python",
                "workflow_demo.py",
                str(production_vault),
                "--weekly-review",
                "--dry-run",
            ],
            cwd=production_vault.parent / "development" / "src" / "cli",
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        duration = time.time() - start_time

        # RED Phase: This will fail initially
        assert result.returncode == 0, (
            f"Weekly review failed on production vault:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Verify reasonable performance (<5 minutes for production vault)
        assert duration < 300, (
            f"Weekly review took {duration:.1f}s (>5min timeout). "
            f"Performance regression on production vault?"
        )

        # Verify meaningful output
        assert (
            "notes" in result.stdout.lower()
        ), "Weekly review output missing note count"

        print(f"✅ Weekly review completed in {duration:.2f}s on production vault")

    def test_weekly_review_dry_run_production(self, production_vault):
        """
        RED Phase: Validate dry-run mode doesn't mutate production vault.

        Critical safety test - verify dry-run never modifies files.
        """
        # Get modification times of all files before
        file_mtimes_before = {}
        for md_file in production_vault.rglob("*.md"):
            file_mtimes_before[md_file] = md_file.stat().st_mtime

        # Run dry-run
        result = subprocess.run(
            [
                "python",
                "workflow_demo.py",
                str(production_vault),
                "--weekly-review",
                "--dry-run",
            ],
            cwd=production_vault.parent / "development" / "src" / "cli",
            capture_output=True,
            text=True,
            timeout=300,
        )

        # RED Phase: Verify no files modified
        for md_file, mtime_before in file_mtimes_before.items():
            mtime_after = md_file.stat().st_mtime
            assert mtime_before == mtime_after, (
                f"Dry-run modified {md_file}! "
                f"CRITICAL: Dry-run must never mutate files."
            )

        print("✅ Dry-run verified safe - no files modified")


@pytest.mark.smoke
@pytest.mark.slow
class TestConnectionDiscoveryProduction:
    """
    Smoke tests for connection discovery with real vault.

    RED Phase: Validate semantic link discovery on production data.
    """

    @pytest.fixture
    def production_vault(self):
        return get_production_vault()

    def test_connection_discovery_finds_real_links(self, production_vault):
        """
        RED Phase: Validate connection discovery on production vault.

        Expected: Should find semantic connections between actual notes
        """
        # RED Phase: This will fail - drive implementation
        pytest.fail("Not implemented - RED phase placeholder")


@pytest.mark.smoke
@pytest.mark.slow
class TestOrphanedNotesProduction:
    """
    Smoke tests for orphaned note detection with real vault.

    RED Phase: Validate orphaned note detection on 300+ notes.
    """

    @pytest.fixture
    def production_vault(self):
        return get_production_vault()

    def test_orphaned_notes_detection_production(self, production_vault):
        """
        RED Phase: Validate orphaned note detection on production vault.

        Expected: Should build link graph from 300+ notes in reasonable time
        """
        # RED Phase: This will fail - drive implementation
        pytest.fail("Not implemented - RED phase placeholder")


@pytest.mark.smoke
@pytest.mark.slow
class TestBackupSystemProduction:
    """
    Smoke tests for backup system with actual vault size.

    RED Phase: Validate backup/restore on production-sized vault.
    """

    @pytest.fixture
    def production_vault(self):
        return get_production_vault()

    def test_backup_creates_complete_copy(self, production_vault):
        """
        RED Phase: Validate backup system with production vault size.

        Expected: Should backup 300+ notes + media in reasonable time
        """
        # RED Phase: This will fail - drive implementation
        pytest.fail("Not implemented - RED phase placeholder")


@pytest.mark.smoke
@pytest.mark.slow
class TestImageLinkPreservationProduction:
    """
    Smoke tests for image link preservation with real vault.

    RED Phase: Validate image links remain intact with production data.
    """

    @pytest.fixture
    def production_vault(self):
        return get_production_vault()

    def test_image_links_preserved_after_workflow(self, production_vault):
        """
        RED Phase: Validate image link preservation on production vault.

        Expected: All image references should remain valid after workflows
        """
        # RED Phase: This will fail - drive implementation
        pytest.fail("Not implemented - RED phase placeholder")


@pytest.mark.smoke
@pytest.mark.slow
class TestSmokeTestInfrastructure:
    """
    Meta-tests validating smoke test infrastructure itself.

    RED Phase: Verify smoke tests are properly separated from fast tests.
    """

    def test_smoke_tests_not_in_fast_suite(self):
        """
        RED Phase: Verify smoke tests don't run with fast tests.

        Critical: Smoke tests must not slow down TDD cycles.
        """
        # Run fast tests, verify no smoke tests included
        result = subprocess.run(
            ["pytest", "-m", "not slow", "--collect-only", "-q"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )

        # RED Phase: Verify no smoke test files in collection
        assert "test_real_vault_workflows.py" not in result.stdout, (
            "Smoke tests appearing in fast test collection! "
            "This will slow down TDD cycles."
        )

        print("✅ Smoke tests properly excluded from fast suite")

    def test_smoke_tests_have_markers(self):
        """
        RED Phase: Verify all smoke tests have proper markers.

        Expected: Every smoke test should have @pytest.mark.smoke
        """
        # RED Phase: This validates marker infrastructure
        # Will fail if markers not properly applied

        # Count smoke tests
        result = subprocess.run(
            ["pytest", "-m", "smoke", "--collect-only", "-q"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )

        # Should find our smoke tests
        assert "test_real_vault_workflows.py" in result.stdout, (
            "Smoke tests not found with -m smoke filter. "
            "Verify @pytest.mark.smoke decorators applied."
        )

        print("✅ Smoke test markers verified")
