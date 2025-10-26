"""
Integration tests for auto-promote CLI command with real vault operations.

Tests the complete end-to-end workflow:
- Actual file moves from Inbox to target directories
- YAML frontmatter updates
- CLI flag combinations
- Error handling with real scenarios

TDD Iteration: PBI-004 P1 Integration Tests
Phase: RED (Expected to FAIL - infrastructure not yet implemented)
"""

import json
import subprocess
from pathlib import Path
from typing import List, Optional

import pytest


class TestAutoPromoteIntegration:
    """Integration tests for auto-promote command with real vault."""

    @pytest.fixture
    def temp_vault(self, tmp_path):
        """
        Create temporary vault with realistic directory structure.
        
        Structure:
        - Inbox/ (with notes of varying quality)
        - Fleeting Notes/
        - Permanent Notes/
        - Literature Notes/
        """
        vault_path = tmp_path / "test_vault"

        # Create directories
        (vault_path / "Inbox").mkdir(parents=True)
        (vault_path / "Fleeting Notes").mkdir(parents=True)
        (vault_path / "Permanent Notes").mkdir(parents=True)
        (vault_path / "Literature Notes").mkdir(parents=True)

        # Create notes with different quality scores in Inbox
        self._create_test_note(
            vault_path / "Inbox" / "high-quality-note.md",
            status="inbox",
            quality_score=0.85,
            content="# High Quality Note\n\nThis is a well-formed note with good structure.\n\n## Section\nWith detailed content and [[connections]]."
        )

        self._create_test_note(
            vault_path / "Inbox" / "medium-quality-note.md",
            status="inbox",
            quality_score=0.75,
            content="# Medium Quality\n\nDecent note with some structure."
        )

        self._create_test_note(
            vault_path / "Inbox" / "low-quality-note.md",
            status="inbox",
            quality_score=0.50,
            content="# Low Quality\n\nBrief note."
        )

        self._create_test_note(
            vault_path / "Inbox" / "no-score-note.md",
            status="inbox",
            quality_score=None,
            content="# No Score\n\nNote without quality score."
        )

        return vault_path

    def _create_test_note(self, path: Path, status: str, quality_score: Optional[float] = None, content: str = "", note_type: str = "permanent"):
        """Helper to create test note with YAML frontmatter."""
        frontmatter = f"""---
status: {status}
type: {note_type}
created: 2025-10-14 20:00
"""
        if quality_score is not None:
            frontmatter += f"quality_score: {quality_score}\n"

        frontmatter += "---\n\n"

        path.write_text(frontmatter + content)

    def _run_cli_command(self, vault_path: Path, args: List[str]) -> subprocess.CompletedProcess:
        """Execute CLI command and return result."""
        cmd = [
            "python",
            str(Path(__file__).parent.parent.parent / "src" / "cli" / "core_workflow_cli.py"),
            str(vault_path),
            "auto-promote"
        ] + args

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result

    def test_auto_promote_moves_notes_end_to_end(self, temp_vault):
        """
        Test that auto-promote actually moves files from Inbox to target directories.
        
        Expected behavior:
        - Notes with quality ≥0.7 moved to Permanent Notes/
        - Notes with quality <0.7 remain in Inbox
        - YAML status updated to 'permanent'
        - File contents preserved exactly
        """
        # Execute CLI command
        result = self._run_cli_command(temp_vault, [])

        # Should exit successfully
        assert result.returncode == 0

        # High quality note should be in Permanent Notes
        high_quality_dest = temp_vault / "Permanent Notes" / "high-quality-note.md"
        assert high_quality_dest.exists(), "High quality note should be moved"

        # Medium quality note should be in Permanent Notes (≥0.7)
        medium_quality_dest = temp_vault / "Permanent Notes" / "medium-quality-note.md"
        assert medium_quality_dest.exists(), "Medium quality note should be moved"

        # Low quality note should remain in Inbox
        low_quality_inbox = temp_vault / "Inbox" / "low-quality-note.md"
        assert low_quality_inbox.exists(), "Low quality note should remain in Inbox"

        # Original files should NOT exist in Inbox
        assert not (temp_vault / "Inbox" / "high-quality-note.md").exists()
        assert not (temp_vault / "Inbox" / "medium-quality-note.md").exists()

        # Verify status updated in frontmatter
        high_quality_content = high_quality_dest.read_text()
        assert "status: published" in high_quality_content  # Status is lifecycle state

        # Verify file content preserved
        assert "This is a well-formed note" in high_quality_content
        assert "[[connections]]" in high_quality_content

    def test_auto_promote_dry_run_no_file_changes(self, temp_vault):
        """
        Test that --dry-run prevents ANY file system modifications.
        
        Expected behavior:
        - No files moved
        - Preview output shown
        - Exit code 0
        """
        # Execute with --dry-run
        result = self._run_cli_command(temp_vault, ["--dry-run"])

        assert result.returncode == 0

        # All notes should still be in Inbox
        assert (temp_vault / "Inbox" / "high-quality-note.md").exists()
        assert (temp_vault / "Inbox" / "medium-quality-note.md").exists()
        assert (temp_vault / "Inbox" / "low-quality-note.md").exists()

        # No notes in target directories
        permanent_notes = list((temp_vault / "Permanent Notes").glob("*.md"))
        assert len(permanent_notes) == 0, "Dry-run should not move any files"

        # Output should indicate dry-run mode
        assert "DRY RUN" in result.stdout or "dry-run" in result.stdout.lower()

    def test_auto_promote_quality_threshold_filtering(self, temp_vault):
        """
        Test that --quality-threshold correctly filters notes.
        
        Expected behavior:
        - threshold 0.8: Only 0.85 note promoted
        - threshold 0.6: Both 0.75 and 0.85 promoted
        """
        # Test with threshold 0.8 (only highest quality)
        result = self._run_cli_command(temp_vault, ["--quality-threshold", "0.8"])
        assert result.returncode == 0

        assert (temp_vault / "Permanent Notes" / "high-quality-note.md").exists()
        assert not (temp_vault / "Permanent Notes" / "medium-quality-note.md").exists()
        assert (temp_vault / "Inbox" / "medium-quality-note.md").exists()

        # Reset vault for second test
        (temp_vault / "Permanent Notes" / "high-quality-note.md").unlink()
        self._create_test_note(
            temp_vault / "Inbox" / "high-quality-note.md",
            status="inbox",
            quality_score=0.85,
            content="# High Quality Note\n\nContent"
        )

        # Test with threshold 0.6 (both high and medium)
        result = self._run_cli_command(temp_vault, ["--quality-threshold", "0.6"])
        assert result.returncode == 0

        assert (temp_vault / "Permanent Notes" / "high-quality-note.md").exists()
        assert (temp_vault / "Permanent Notes" / "medium-quality-note.md").exists()

    def test_auto_promote_json_output_valid(self, temp_vault):
        """
        Test that --format json produces valid JSON with correct structure.
        
        Expected structure:
        {
            "promoted": [...],
            "skipped": [...],
            "summary": {...}
        }
        """
        result = self._run_cli_command(temp_vault, ["--format", "json"])

        assert result.returncode == 0

        # Parse JSON output
        output_data = json.loads(result.stdout)

        # Verify structure
        assert "promoted" in output_data
        assert "skipped_notes" in output_data
        assert "summary" in output_data

        # Verify promoted notes
        assert len(output_data["promoted"]) == 2  # high + medium quality

        promoted_titles = [note["title"] for note in output_data["promoted"]]
        assert "high-quality-note.md" in promoted_titles
        assert "medium-quality-note.md" in promoted_titles

        # Verify summary
        assert output_data["summary"]["total_candidates"] >= 2
        assert output_data["summary"]["promoted_count"] == 2

    def test_auto_promote_error_invalid_vault_path(self):
        """
        Test error handling with non-existent vault path.
        
        Expected behavior:
        - Exit code 1
        - Error message in stderr
        """
        result = self._run_cli_command(Path("/nonexistent/vault"), [])

        assert result.returncode == 1
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()

    def test_auto_promote_error_malformed_yaml(self, temp_vault):
        """
        Test handling of malformed YAML frontmatter.
        
        Expected behavior:
        - Skip malformed notes gracefully
        - Continue processing valid notes
        - Report skipped notes
        """
        # Create note with malformed YAML
        malformed_path = temp_vault / "Inbox" / "malformed.md"
        malformed_path.write_text("---\nstatus: inbox\nbad yaml: [unclosed\n---\n\nContent")

        result = self._run_cli_command(temp_vault, [])

        # Should still succeed (skip malformed note)
        assert result.returncode == 0

        # Valid notes should still be promoted
        assert (temp_vault / "Permanent Notes" / "high-quality-note.md").exists()

        # Malformed note should remain in Inbox
        assert malformed_path.exists()

    def test_auto_promote_empty_inbox(self, tmp_path):
        """
        Test behavior with empty Inbox.
        
        Expected behavior:
        - Exit code 0
        - Report zero candidates
        - Friendly message
        """
        vault_path = tmp_path / "empty_vault"
        (vault_path / "Inbox").mkdir(parents=True)
        (vault_path / "Permanent Notes").mkdir(parents=True)

        result = self._run_cli_command(vault_path, [])

        assert result.returncode == 0
        assert "0" in result.stdout or "no notes" in result.stdout.lower()

    def test_auto_promote_combined_flags(self, temp_vault):
        """
        Test combined flag scenarios.
        
        Test: --dry-run --quality-threshold 0.8 --format json
        Expected: JSON output, no file moves, only high quality in results
        """
        result = self._run_cli_command(
            temp_vault,
            ["--dry-run", "--quality-threshold", "0.8", "--format", "json"]
        )

        assert result.returncode == 0

        # Parse JSON
        output_data = json.loads(result.stdout)

        # Dry-run mode - check preview instead
        if output_data.get("dry_run"):
            assert "preview" in output_data
            assert len(output_data["preview"]) == 1
            assert "high-quality-note.md" in output_data["preview"][0]["note"]
        else:
            # Regular mode
            assert len(output_data["promoted"]) == 1
            assert "high-quality-note.md" in output_data["promoted"][0]["title"]

        # No files should be moved (dry-run)
        assert (temp_vault / "Inbox" / "high-quality-note.md").exists()
        assert not (temp_vault / "Permanent Notes" / "high-quality-note.md").exists()

    def test_auto_promote_preserves_file_content_exactly(self, temp_vault):
        """
        Test that file contents are preserved exactly (no data loss).
        
        Expected behavior:
        - All markdown content preserved
        - Wiki-links preserved
        - Formatting preserved
        - Only status field updated in frontmatter
        """
        # Get original content
        original_path = temp_vault / "Inbox" / "high-quality-note.md"
        original_content = original_path.read_text()

        result = self._run_cli_command(temp_vault, [])
        assert result.returncode == 0

        # Get promoted content
        promoted_path = temp_vault / "Permanent Notes" / "high-quality-note.md"
        promoted_content = promoted_path.read_text()

        # Verify content preservation
        assert "This is a well-formed note with good structure" in promoted_content
        assert "[[connections]]" in promoted_content
        assert "## Section" in promoted_content
        assert "With detailed content" in promoted_content

        # Verify only status changed
        assert "status: published" in promoted_content  # Status is lifecycle state
        assert "quality_score: 0.85" in promoted_content
        assert "created: 2025-10-14 20:00" in promoted_content


class TestAutoPromotePerformance:
    """Performance validation tests for auto-promote."""

    @pytest.fixture
    def large_vault(self, tmp_path):
        """Create vault with 50+ notes for performance testing."""
        vault_path = tmp_path / "large_vault"
        (vault_path / "Inbox").mkdir(parents=True)
        (vault_path / "Permanent Notes").mkdir(parents=True)

        # Create 50 notes with varying quality
        for i in range(50):
            quality = 0.5 + (i % 5) * 0.1  # Range: 0.5 to 0.9
            self._create_test_note(
                vault_path / "Inbox" / f"note-{i:03d}.md",
                status="inbox",
                quality_score=quality,
                content=f"# Note {i}\n\nTest content for note {i}."
            )

        return vault_path

    def _create_test_note(self, path: Path, status: str, quality_score: float, content: str, note_type: str = "permanent"):
        """Helper to create test note."""
        frontmatter = f"""---
status: {status}
type: {note_type}
quality_score: {quality_score}
created: 2025-10-14 20:00
---

"""
        path.write_text(frontmatter + content)

    def test_auto_promote_performance_50_notes(self, large_vault):
        """
        Test that auto-promote completes within performance target.
        
        Target: <10 seconds for 50 notes
        """
        import time

        start_time = time.time()

        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent.parent / "src" / "cli" / "core_workflow_cli.py"),
                str(large_vault),
                "auto-promote"
            ],
            capture_output=True,
            text=True
        )

        elapsed = time.time() - start_time

        assert result.returncode == 0
        assert elapsed < 10.0, f"Performance target exceeded: {elapsed:.2f}s > 10s"

        # Verify correct number of promotions
        promoted_notes = list((large_vault / "Permanent Notes").glob("*.md"))
        expected_promotions = sum(1 for i in range(50) if 0.5 + (i % 5) * 0.1 >= 0.7)
        assert len(promoted_notes) == expected_promotions
