"""
TDD RED Phase: Tests for Auto-Promotion System (PBI-004)

Implements quality-gated automatic promotion of notes from Inbox to appropriate
directories based on type and quality score.

Test Coverage:
- Quality threshold filtering (default: 0.7)
- Type-based directory routing (fleeting/literature/permanent)
- Status transitions (promoted → published)
- Timestamp management (promoted_date)
- Dry-run mode (preview without changes)
- Batch processing with summary statistics
- Error handling (low quality, missing type, invalid status)
- Integration with NoteLifecycleManager
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.ai.workflow_manager import WorkflowManager


class TestAutoPromotionSystem:
    """Test suite for auto-promotion system in WorkflowManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory structure for testing."""
        temp_path = tempfile.mkdtemp()
        temp_path_obj = Path(temp_path)

        # Create directory structure
        (temp_path_obj / "Inbox").mkdir()
        (temp_path_obj / "Fleeting Notes").mkdir()
        (temp_path_obj / "Literature Notes").mkdir()
        (temp_path_obj / "Permanent Notes").mkdir()

        yield temp_path_obj
        shutil.rmtree(temp_path)

    @pytest.fixture
    def workflow_manager(self, temp_dir):
        """Create WorkflowManager instance with temp vault."""
        manager = WorkflowManager(base_directory=str(temp_dir))
        return manager

    def create_test_note(self, temp_dir: Path, filename: str, content: str) -> Path:
        """Helper to create a test note file in Inbox."""
        note_path = temp_dir / "Inbox" / filename
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def test_auto_promote_filters_by_quality_threshold(
        self, workflow_manager, temp_dir
    ):
        """
        RED: Only notes with quality_score >= 0.7 should be promoted.

        Notes below threshold should be skipped with clear reason.
        """
        # Create high-quality note (should be promoted)
        high_quality = """---
type: fleeting
status: promoted
quality_score: 0.85
tags: [test]
---

# High Quality Note
This note has good quality."""

        # Create low-quality note (should be skipped)
        low_quality = """---
type: fleeting
status: promoted
quality_score: 0.45
tags: [test]
---

# Low Quality Note
This note needs more work."""

        self.create_test_note(temp_dir, "high-quality.md", high_quality)
        self.create_test_note(temp_dir, "low-quality.md", low_quality)

        # Run auto-promotion with default threshold (0.7)
        result = workflow_manager.auto_promote_ready_notes()

        # Assertions
        assert result["promoted_count"] == 1, "Should promote 1 high-quality note"
        assert result["skipped_count"] == 1, "Should skip 1 low-quality note"
        assert (
            "low-quality.md" in result["skipped_notes"]
        ), "Low quality note should be in skipped list"
        assert (
            "threshold" in result["skipped_notes"]["low-quality.md"].lower()
        ), "Skip reason should mention threshold"

    def test_auto_promote_routes_by_type_fleeting(self, workflow_manager, temp_dir):
        """
        RED: Fleeting notes should be routed to 'Fleeting Notes/' directory.
        """
        note_content = """---
type: fleeting
status: promoted
quality_score: 0.85
tags: [test]
---

# Fleeting Test Note"""

        note_path = self.create_test_note(temp_dir, "fleeting-note.md", note_content)

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()

        # Verify note moved to correct directory
        assert result["promoted_count"] == 1, "Should promote 1 note"

        expected_path = temp_dir / "Fleeting Notes" / "fleeting-note.md"
        assert expected_path.exists(), "Note should be in Fleeting Notes/ directory"
        assert not note_path.exists(), "Original note should be moved (not copied)"

    def test_auto_promote_routes_by_type_literature(self, workflow_manager, temp_dir):
        """
        RED: Literature notes should be routed to 'Literature Notes/' directory.
        """
        note_content = """---
type: literature
status: promoted
quality_score: 0.90
tags: [research, paper]
---

# Literature Note from Research Paper"""

        note_path = self.create_test_note(
            temp_dir, "lit-research-paper.md", note_content
        )

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()

        # Verify note moved to correct directory
        assert result["promoted_count"] == 1, "Should promote 1 note"

        expected_path = temp_dir / "Literature Notes" / "lit-research-paper.md"
        assert expected_path.exists(), "Note should be in Literature Notes/ directory"
        assert not note_path.exists(), "Original note should be moved (not copied)"

    def test_auto_promote_routes_by_type_permanent(self, workflow_manager, temp_dir):
        """
        RED: Permanent notes should be routed to 'Permanent Notes/' directory.
        """
        note_content = """---
type: permanent
status: promoted
quality_score: 0.95
tags: [concept, atomic]
---

# Permanent Concept Note"""

        note_path = self.create_test_note(
            temp_dir, "permanent-concept.md", note_content
        )

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()

        # Verify note moved to correct directory
        assert result["promoted_count"] == 1, "Should promote 1 note"

        expected_path = temp_dir / "Permanent Notes" / "permanent-concept.md"
        assert expected_path.exists(), "Note should be in Permanent Notes/ directory"
        assert not note_path.exists(), "Original note should be moved (not copied)"

    def test_auto_promote_updates_status_to_published(self, workflow_manager, temp_dir):
        """
        RED: Status should transition from 'promoted' to 'published' after successful move.

        Uses NoteLifecycleManager for consistent status management.
        """
        note_content = """---
type: fleeting
status: promoted
quality_score: 0.85
tags: [test]
---

# Test Note for Status Update"""

        self.create_test_note(temp_dir, "status-test.md", note_content)

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()
        assert result["promoted_count"] == 1, "Should promote 1 note"

        # Verify status updated in moved file
        moved_path = temp_dir / "Fleeting Notes" / "status-test.md"
        moved_content = moved_path.read_text(encoding="utf-8")

        assert (
            "status: published" in moved_content
        ), "Status should be updated to 'published'"
        assert "status: promoted" not in moved_content, "Old status should be removed"

    def test_auto_promote_adds_promoted_date_timestamp(
        self, workflow_manager, temp_dir
    ):
        """
        RED: Promoted notes should have 'promoted_date' timestamp added.

        Timestamp should be in format: YYYY-MM-DD HH:MM
        """
        note_content = """---
type: permanent
status: promoted
quality_score: 0.92
tags: [test]
---

# Test Note for Timestamp"""

        self.create_test_note(temp_dir, "timestamp-test.md", note_content)

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()
        assert result["promoted_count"] == 1, "Should promote 1 note"

        # Verify promoted_date was added
        moved_path = temp_dir / "Permanent Notes" / "timestamp-test.md"
        moved_content = moved_path.read_text(encoding="utf-8")

        import re

        assert re.search(
            r"promoted_date:\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", moved_content
        ), "promoted_date should be added with correct format (YYYY-MM-DD HH:MM)"

        # Verify timestamp is recent (within last minute)
        match = re.search(
            r"promoted_date:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", moved_content
        )
        if match:
            timestamp_str = match.group(1)
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            time_diff = abs((datetime.now() - timestamp).total_seconds())
            assert time_diff < 60, "promoted_date should be current timestamp"

    def test_auto_promote_dry_run_no_changes(self, workflow_manager, temp_dir):
        """
        RED: Dry-run mode should preview promotions without making any changes.

        No files should be moved, no statuses updated, but results should show what would happen.
        """
        note_content = """---
type: fleeting
status: promoted
quality_score: 0.88
tags: [test]
---

# Dry Run Test Note"""

        note_path = self.create_test_note(temp_dir, "dry-run-test.md", note_content)

        # Run auto-promotion in dry-run mode
        result = workflow_manager.auto_promote_ready_notes(dry_run=True)

        # Verify no changes made
        assert note_path.exists(), "Original note should still exist in Inbox"

        moved_path = temp_dir / "Fleeting Notes" / "dry-run-test.md"
        assert not moved_path.exists(), "Note should NOT be moved in dry-run mode"

        # Verify dry-run results
        assert result["dry_run"] is True, "Result should indicate dry-run mode"
        assert (
            result["would_promote_count"] == 1
        ), "Should show 1 note would be promoted"
        assert any(
            p["note"] == "dry-run-test.md" for p in result["preview"]
        ), "Preview should include note name"

    def test_auto_promote_custom_quality_threshold(self, workflow_manager, temp_dir):
        """
        RED: Custom quality threshold should be respected.

        Allow configurable threshold (e.g., 0.8 instead of default 0.7).
        """
        # Create note with quality 0.75 (above 0.7, below 0.8)
        note_content = """---
type: fleeting
status: promoted
quality_score: 0.75
tags: [test]
---

# Threshold Test Note"""

        self.create_test_note(temp_dir, "threshold-test.md", note_content)

        # Should be promoted with default threshold (0.7)
        result_default = workflow_manager.auto_promote_ready_notes(
            quality_threshold=0.7
        )
        assert (
            result_default["promoted_count"] == 1
        ), "Should promote with threshold 0.7"

        # Create another note for second test
        self.create_test_note(temp_dir, "threshold-test-2.md", note_content)

        # Should be skipped with higher threshold (0.8)
        result_high = workflow_manager.auto_promote_ready_notes(quality_threshold=0.8)
        assert result_high["skipped_count"] == 1, "Should skip with threshold 0.8"

    def test_auto_promote_batch_processing_multiple_notes(
        self, workflow_manager, temp_dir
    ):
        """
        RED: Batch processing should handle multiple notes with summary statistics.

        Process all ready notes in Inbox and return comprehensive summary.
        """
        # Create 3 notes of different types and quality
        notes = [
            ("fleeting-1.md", "fleeting", 0.85),
            ("literature-1.md", "literature", 0.90),
            ("permanent-1.md", "permanent", 0.95),
            ("low-quality.md", "fleeting", 0.45),  # Should be skipped
        ]

        for filename, note_type, quality in notes:
            content = f"""---
type: {note_type}
status: promoted
quality_score: {quality}
tags: [test]
---

# Test Note {filename}"""
            self.create_test_note(temp_dir, filename, content)

        # Run batch auto-promotion
        result = workflow_manager.auto_promote_ready_notes()

        # Verify batch results
        assert result["total_candidates"] == 4, "Should find 4 candidate notes"
        assert result["promoted_count"] == 3, "Should promote 3 high-quality notes"
        assert result["skipped_count"] == 1, "Should skip 1 low-quality note"

        # Verify by type
        assert result["by_type"]["fleeting"] == 1, "Should promote 1 fleeting note"
        assert result["by_type"]["literature"] == 1, "Should promote 1 literature note"
        assert result["by_type"]["permanent"] == 1, "Should promote 1 permanent note"

    def test_auto_promote_handles_missing_type_field(self, workflow_manager, temp_dir):
        """
        RED: Notes without 'type' field should be skipped with clear error.

        Error handling for malformed notes.
        """
        note_content = """---
status: promoted
quality_score: 0.85
tags: [test]
---

# Note Without Type Field"""

        self.create_test_note(temp_dir, "no-type.md", note_content)

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()

        # Verify error handling
        assert result["error_count"] == 1, "Should count 1 error"
        assert "no-type.md" in result["errors"], "Error should be tracked"
        assert (
            "type" in result["errors"]["no-type.md"].lower()
        ), "Error message should mention missing 'type' field"

    def test_auto_promote_skips_non_promoted_status(self, workflow_manager, temp_dir):
        """
        RED: Only notes with status='promoted' should be candidates.

        Notes with 'inbox' or 'published' status should be ignored.
        """
        # Create notes with different statuses
        inbox_note = """---
type: fleeting
status: inbox
quality_score: 0.85
---

# Inbox Note (should be skipped)"""

        published_note = """---
type: fleeting
status: published
quality_score: 0.85
---

# Already Published Note (should be skipped)"""

        self.create_test_note(temp_dir, "inbox-status.md", inbox_note)
        self.create_test_note(temp_dir, "published-status.md", published_note)

        # Run auto-promotion
        result = workflow_manager.auto_promote_ready_notes()

        # Verify only promoted notes are candidates
        assert (
            result["total_candidates"] == 0
        ), "Should find 0 candidate notes (none have status='promoted')"
        assert result["promoted_count"] == 0, "Should promote 0 notes"
