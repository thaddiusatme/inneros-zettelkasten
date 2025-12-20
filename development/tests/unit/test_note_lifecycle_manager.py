"""
TDD RED Phase: Tests for NoteLifecycleManager (ADR-002)

Extracted from WorkflowManager to fix architectural constraint violation.
Handles note status transitions: inbox → promoted → published → archived

Test Coverage:
- Status updates with validation
- Timestamp management (processed_date, promoted_date, etc.)
- Status transition validation (prevent invalid transitions)
- Idempotence (re-running status updates is safe)
- Metadata preservation
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.ai.note_lifecycle_manager import NoteLifecycleManager

pytestmark = pytest.mark.ci


class TestNoteLifecycleManager:
    """Test suite for NoteLifecycleManager class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def lifecycle_manager(self, temp_dir):
        """Create NoteLifecycleManager instance for testing."""
        return NoteLifecycleManager(base_dir=temp_dir)

    def create_test_note(self, temp_dir: Path, filename: str, content: str) -> Path:
        """Helper to create a test note file."""
        note_path = temp_dir / filename
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def test_update_status_inbox_to_promoted(self, lifecycle_manager, temp_dir):
        """
        CORE: Status should update from 'inbox' to 'promoted'.

        This is the primary use case - notes processed by AI get promoted.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note

This is a test note."""

        note_path = self.create_test_note(temp_dir, "test-note.md", note_content)

        # Update status to promoted
        result = lifecycle_manager.update_status(
            note_path,
            new_status="promoted",
            reason="AI processing completed",
            metadata={"quality_score": 0.85},
        )

        # Verify result
        assert (
            result["status_updated"] == "promoted"
        ), "Status should be updated to 'promoted'"
        assert result["validation_passed"] is True, "Transition should be valid"
        assert "timestamp" in result, "Should include timestamp"

        # Verify file was updated
        updated_content = note_path.read_text(encoding="utf-8")
        assert (
            "status: promoted" in updated_content
        ), "Status should be 'promoted' in file"
        assert "status: inbox" not in updated_content, "Old status should be removed"

    def test_update_status_adds_processed_date(self, lifecycle_manager, temp_dir):
        """
        Promoted notes should have processed_date timestamp.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note"""

        note_path = self.create_test_note(temp_dir, "test-date.md", note_content)

        # Update status to promoted
        result = lifecycle_manager.update_status(
            note_path, new_status="promoted", reason="AI processing completed"
        )

        # Verify processed_date was added
        updated_content = note_path.read_text(encoding="utf-8")

        import re

        assert re.search(
            r"processed_date:\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", updated_content
        ), "processed_date should be added with correct format (YYYY-MM-DD HH:MM)"

        # Verify timestamp is recent (within last minute)
        match = re.search(
            r"processed_date:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", updated_content
        )
        if match:
            timestamp_str = match.group(1)
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            time_diff = abs((datetime.now() - timestamp).total_seconds())
            assert time_diff < 60, "processed_date should be current timestamp"

    def test_validate_transition_inbox_to_promoted_allowed(self, lifecycle_manager):
        """
        Validate that inbox → promoted transition is allowed.
        """
        is_valid, error_message = lifecycle_manager.validate_transition(
            "inbox", "promoted"
        )

        assert is_valid is True, "inbox → promoted should be allowed"
        assert error_message == "", "No error message for valid transition"

    def test_validate_transition_promoted_to_inbox_forbidden(self, lifecycle_manager):
        """
        Validate that promoted → inbox transition is forbidden (can't go backwards).
        """
        is_valid, error_message = lifecycle_manager.validate_transition(
            "promoted", "inbox"
        )

        assert is_valid is False, "promoted → inbox should be forbidden"
        assert (
            "not allowed" in error_message.lower()
        ), "Should explain why transition forbidden"

    def test_update_status_preserves_other_metadata(self, lifecycle_manager, temp_dir):
        """
        Status update should not affect other frontmatter fields.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test, original]
created: 2025-01-01 10:00
custom_field: important_value
quality_score: 0.75
---

# Test Note"""

        note_path = self.create_test_note(temp_dir, "test-preserve.md", note_content)

        # Update status
        result = lifecycle_manager.update_status(
            note_path, new_status="promoted", reason="AI processing"
        )

        # Verify status updated
        updated_content = note_path.read_text(encoding="utf-8")
        assert "status: promoted" in updated_content

        # Verify other fields preserved
        assert "type: fleeting" in updated_content
        assert "created: 2025-01-01 10:00" in updated_content
        assert "custom_field: important_value" in updated_content
        assert "quality_score: 0.75" in updated_content
        assert (
            "tags:\n- test\n- original" in updated_content
            or "tags: [test, original]" in updated_content
        )

    def test_update_status_idempotent(self, lifecycle_manager, temp_dir):
        """
        Re-running update_status should be safe (idempotent).
        Should not duplicate timestamps or break existing status.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note"""

        note_path = self.create_test_note(temp_dir, "test-idempotent.md", note_content)

        # First update
        result1 = lifecycle_manager.update_status(
            note_path, new_status="promoted", reason="First run"
        )
        content_after_first = note_path.read_text(encoding="utf-8")

        # Second update (should be safe, no duplicate timestamps)
        result2 = lifecycle_manager.update_status(
            note_path, new_status="promoted", reason="Second run (idempotent)"
        )
        content_after_second = note_path.read_text(encoding="utf-8")

        # Verify status is still correct
        assert "status: promoted" in content_after_second

        # Count occurrences of processed_date (should be 1, not duplicated)
        import re

        processed_date_count = len(re.findall(r"processed_date:", content_after_second))
        assert (
            processed_date_count == 1
        ), "processed_date should not be duplicated on re-run"

        # Both results should indicate success
        assert result1["status_updated"] == "promoted"
        assert result2["status_updated"] == "promoted"

    def test_update_status_invalid_status_rejected(self, lifecycle_manager, temp_dir):
        """
        Invalid status values should be rejected.
        """
        note_content = """---
type: fleeting
status: inbox
---

# Test Note"""

        note_path = self.create_test_note(temp_dir, "test-invalid.md", note_content)

        # Try to update to invalid status
        result = lifecycle_manager.update_status(
            note_path, new_status="invalid_status", reason="Testing validation"
        )

        # Verify rejection
        assert result["status_updated"] is False, "Invalid status should be rejected"
        assert result["validation_passed"] is False, "Validation should fail"
        assert "error" in result, "Should include error message"

        # Verify file unchanged
        updated_content = note_path.read_text(encoding="utf-8")
        assert "status: inbox" in updated_content, "Status should remain 'inbox'"
        assert (
            "invalid_status" not in updated_content
        ), "Invalid status should not be written"

    def test_update_status_file_not_found(self, lifecycle_manager, temp_dir):
        """
        Handle missing file gracefully.
        """
        nonexistent_path = temp_dir / "nonexistent.md"

        result = lifecycle_manager.update_status(
            nonexistent_path, new_status="promoted", reason="Testing error handling"
        )

        assert result["status_updated"] is False, "Should fail for nonexistent file"
        assert "error" in result, "Should include error message"
        assert (
            "not found" in result["error"].lower()
        ), "Error should mention file not found"

    def test_get_valid_transitions(self, lifecycle_manager):
        """
        Verify valid transitions are correctly defined.
        """
        # Test all valid transitions
        valid_transitions = [
            ("inbox", "promoted"),
            ("inbox", "archived"),
            ("promoted", "published"),
            ("promoted", "archived"),
            ("published", "archived"),
            ("archived", "inbox"),  # Allow resurrection
        ]

        for from_status, to_status in valid_transitions:
            is_valid, _ = lifecycle_manager.validate_transition(from_status, to_status)
            assert is_valid, f"{from_status} → {to_status} should be valid"

    def test_invalid_transitions_rejected(self, lifecycle_manager):
        """
        Verify invalid transitions are correctly rejected.
        """
        invalid_transitions = [
            ("promoted", "inbox"),  # Can't go backwards
            ("published", "inbox"),  # Can't go backwards
            ("published", "promoted"),  # Can't go backwards
            ("inbox", "published"),  # Must go through promoted first
        ]

        for from_status, to_status in invalid_transitions:
            is_valid, error = lifecycle_manager.validate_transition(
                from_status, to_status
            )
            assert is_valid is False, f"{from_status} → {to_status} should be invalid"
            assert (
                len(error) > 0
            ), f"Should provide error message for {from_status} → {to_status}"

    def test_promote_note_permanent_type(self, lifecycle_manager, temp_dir):
        """
        RED: promote_note() should move notes with type: permanent to Permanent Notes/ directory.

        This addresses the orphaned notes problem where ai_processed=true notes
        remain stuck in Inbox/ instead of being promoted to their correct directory.
        """
        # Create directory structure
        inbox_dir = temp_dir / "Inbox"
        permanent_dir = temp_dir / "Permanent Notes"
        inbox_dir.mkdir()
        permanent_dir.mkdir()

        # Create test note in Inbox with type: permanent
        note_content = """---
type: permanent
status: inbox
ai_processed: true
quality_score: 0.85
tags: [test, permanent]
---

# Test Permanent Note

This should move to Permanent Notes directory."""

        source_path = inbox_dir / "test-permanent-note.md"
        source_path.write_text(note_content, encoding="utf-8")

        # Promote the note
        result = lifecycle_manager.promote_note(source_path)

        # Assertions
        assert result["promoted"] is True, "Note should be successfully promoted"
        assert result["destination_dir"] == str(
            permanent_dir
        ), "Should move to Permanent Notes/"
        assert not source_path.exists(), "Source file should be moved (not copied)"

        # Check destination file exists and has correct status
        dest_path = permanent_dir / "test-permanent-note.md"
        assert dest_path.exists(), "Note should exist in Permanent Notes/"

        dest_content = dest_path.read_text(encoding="utf-8")
        assert (
            "status: promoted" in dest_content
        ), "Status should be updated to 'promoted'"
        assert "processed_date:" in dest_content, "Should add processed_date timestamp"

    def test_promote_note_literature_type(self, lifecycle_manager, temp_dir):
        """
        RED: promote_note() should move notes with type: literature to Literature Notes/ directory.

        Addresses the missing literature directory integration.
        """
        # Create directory structure
        inbox_dir = temp_dir / "Inbox"
        literature_dir = temp_dir / "Literature Notes"
        inbox_dir.mkdir()
        literature_dir.mkdir()

        # Create test note in Inbox with type: literature
        note_content = """---
type: literature
status: inbox
ai_processed: true
source: "Test Book"
author: "Test Author"
tags: [test, literature]
---

# Literature Note

Summary of key concepts."""

        source_path = inbox_dir / "lit-test-note.md"
        source_path.write_text(note_content, encoding="utf-8")

        # Promote the note
        result = lifecycle_manager.promote_note(source_path)

        # Assertions
        assert result["promoted"] is True, "Note should be successfully promoted"
        assert result["destination_dir"] == str(
            literature_dir
        ), "Should move to Literature Notes/"
        assert not source_path.exists(), "Source file should be moved"

        dest_path = literature_dir / "lit-test-note.md"
        assert dest_path.exists(), "Note should exist in Literature Notes/"

        dest_content = dest_path.read_text(encoding="utf-8")
        assert (
            "status: promoted" in dest_content
        ), "Status should be updated to 'promoted'"

    def test_promote_note_fleeting_type(self, lifecycle_manager, temp_dir):
        """
        RED: promote_note() should move notes with type: fleeting to Fleeting Notes/ directory.

        Ensures all 3 note types are handled correctly.
        """
        # Create directory structure
        inbox_dir = temp_dir / "Inbox"
        fleeting_dir = temp_dir / "Fleeting Notes"
        inbox_dir.mkdir()
        fleeting_dir.mkdir()

        # Create test note in Inbox with type: fleeting
        note_content = """---
type: fleeting
status: inbox
ai_processed: true
tags: [test, fleeting]
---

# Quick Thought

Capture of a fleeting idea."""

        source_path = inbox_dir / "fleeting-test-note.md"
        source_path.write_text(note_content, encoding="utf-8")

        # Promote the note
        result = lifecycle_manager.promote_note(source_path)

        # Assertions
        assert result["promoted"] is True, "Note should be successfully promoted"
        assert result["destination_dir"] == str(
            fleeting_dir
        ), "Should move to Fleeting Notes/"
        assert not source_path.exists(), "Source file should be moved"

        dest_path = fleeting_dir / "fleeting-test-note.md"
        assert dest_path.exists(), "Note should exist in Fleeting Notes/"

        dest_content = dest_path.read_text(encoding="utf-8")
        assert (
            "status: promoted" in dest_content
        ), "Status should be updated to 'promoted'"
