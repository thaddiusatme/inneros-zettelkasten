"""
TDD RED Phase: Tests for Note Lifecycle Status Management (PBI-001)

Critical Bug: Notes stuck in Inbox/ with `ai_processed: true` but `status: inbox`.
Expected: After AI processing, status should update to "promoted" with timestamp.

Test Coverage:
- Status updates from "inbox" to "promoted" after successful AI processing
- processed_date timestamp is added with correct format
- Results dict includes status_updated field
- Idempotence: re-running doesn't duplicate or break status
- Error handling: status only updates on successful AI processing
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
from unittest.mock import patch

from src.ai.workflow_manager import WorkflowManager


class TestWorkflowManagerStatusUpdate:
    """Test suite for status update functionality in process_inbox_note()."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault structure for testing."""
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir) / "test_vault"
        vault_path.mkdir()

        # Create required directories
        (vault_path / "Inbox").mkdir()
        (vault_path / "Permanent Notes").mkdir()
        (vault_path / "Fleeting Notes").mkdir()
        (vault_path / "Literature Notes").mkdir()

        yield vault_path

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def workflow_manager(self, temp_vault):
        """Create WorkflowManager instance for testing."""
        return WorkflowManager(base_directory=str(temp_vault))

    def create_test_note(self, base_dir: Path, directory: str, filename: str, content: str) -> Path:
        """Helper to create a test note in the proper directory structure."""
        note_path = base_dir / directory / filename
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def test_process_inbox_note_updates_status_to_promoted(self, workflow_manager, temp_vault):
        """
        CRITICAL: Status should update from 'inbox' to 'promoted' after AI processing.
        
        This is the core bug fix - 77 notes are stuck with ai_processed: true but status: inbox.
        """
        # Create test note in Inbox with status: inbox
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note

This is a test note with good quality content for AI processing."""

        note_path = self.create_test_note(temp_vault, "Inbox", "test-note.md", note_content)

        # Mock AI services to ensure they run
        with patch('src.ai.tagger.AITagger.generate_tags') as mock_tagger, \
             patch('src.ai.enhancer.AIEnhancer.enhance_note') as mock_enhancer:

            mock_tagger.return_value = ["test", "ai-generated"]
            mock_enhancer.return_value = {
                "quality": {"score": 0.85, "reason": "High quality content"},
                "summary": "Test summary"
            }

            # Process the note (AI processing should happen)
            results = workflow_manager.process_inbox_note(str(note_path), fast=False)

            # Verify status was updated in results
            assert "status_updated" in results, "Results should include status_updated field"
            assert results["status_updated"] == "promoted", "Status should be updated to 'promoted'"

            # Verify status was persisted to disk
            updated_content = note_path.read_text(encoding="utf-8")
            assert "status: promoted" in updated_content, "Status should be 'promoted' in file"
            assert "status: inbox" not in updated_content, "Old status 'inbox' should be gone"

    def test_process_inbox_note_adds_processed_date(self, workflow_manager, temp_vault):
        """
        Processed notes should have processed_date timestamp for tracking.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note

Quality content for processing."""

        note_path = self.create_test_note(temp_vault, "Inbox", "test-note-date.md", note_content)

        # Mock AI services
        with patch('src.ai.tagger.AITagger.generate_tags') as mock_tagger, \
             patch('src.ai.enhancer.AIEnhancer.enhance_note') as mock_enhancer:

            mock_tagger.return_value = ["test"]
            mock_enhancer.return_value = {
                "quality": {"score": 0.75, "reason": "Good quality"},
                "summary": "Test"
            }

            # Process the note
            results = workflow_manager.process_inbox_note(str(note_path), fast=False)

            # Verify processed_date was added
            updated_content = note_path.read_text(encoding="utf-8")

            # Check for processed_date in format YYYY-MM-DD HH:MM
            import re
            assert re.search(r'processed_date:\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', updated_content), \
                "processed_date should be added with correct format"

            # Verify it's a recent timestamp (within last minute)
            match = re.search(r'processed_date:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', updated_content)
            if match:
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                time_diff = abs((datetime.now() - timestamp).total_seconds())
                assert time_diff < 60, "processed_date should be current timestamp"

    def test_process_inbox_note_idempotent_status_update(self, workflow_manager, temp_vault):
        """
        Re-running process_inbox_note should be safe (idempotent).
        Should not duplicate timestamps or break existing status.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note

Content for idempotence testing."""

        note_path = self.create_test_note(temp_vault, "Inbox", "test-idempotent.md", note_content)

        # Mock AI services
        with patch('src.ai.tagger.AITagger.generate_tags') as mock_tagger, \
             patch('src.ai.enhancer.AIEnhancer.enhance_note') as mock_enhancer:

            mock_tagger.return_value = ["test"]
            mock_enhancer.return_value = {
                "quality": {"score": 0.80, "reason": "Good"},
                "summary": "Test"
            }

            # First processing
            results1 = workflow_manager.process_inbox_note(str(note_path), fast=False)
            content_after_first = note_path.read_text(encoding="utf-8")

            # Second processing (should be idempotent)
            results2 = workflow_manager.process_inbox_note(str(note_path), fast=False)
            content_after_second = note_path.read_text(encoding="utf-8")

            # Verify status is still correct
            assert "status: promoted" in content_after_second

            # Count occurrences of processed_date (should be 1, not duplicated)
            import re
            processed_date_count = len(re.findall(r'processed_date:', content_after_second))
            assert processed_date_count == 1, "processed_date should not be duplicated on re-run"

    def test_process_inbox_note_status_not_updated_on_error(self, workflow_manager, temp_vault):
        """
        Status should remain 'inbox' if AI processing fails.
        Prevents partial updates that could cause data loss.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note

Content that will fail processing."""

        note_path = self.create_test_note(temp_vault, "Inbox", "test-error.md", note_content)

        # Mock AI services to raise exception
        with patch('src.ai.tagger.AITagger.generate_tags') as mock_tagger, \
             patch('src.ai.enhancer.AIEnhancer.enhance_note') as mock_enhancer:

            mock_tagger.side_effect = Exception("AI service unavailable")
            mock_enhancer.return_value = {
                "quality": {"score": 0.50},
                "summary": "Test"
            }

            # Process the note (should handle error gracefully)
            results = workflow_manager.process_inbox_note(str(note_path), fast=False)

            # Verify status was NOT updated
            updated_content = note_path.read_text(encoding="utf-8")
            assert "status: inbox" in updated_content, "Status should remain 'inbox' on error"
            assert "status: promoted" not in updated_content, "Status should not be 'promoted' on error"
            assert "processed_date" not in updated_content, "processed_date should not be added on error"

    def test_process_inbox_note_status_update_preserves_other_metadata(self, workflow_manager, temp_vault):
        """
        Status update should not affect other frontmatter fields.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test, original]
created: 2025-01-01 10:00
custom_field: important_value
---

# Test Note

Content with various metadata."""

        note_path = self.create_test_note(temp_vault, "Inbox", "test-preserve.md", note_content)

        # Mock AI services
        with patch('src.ai.tagger.AITagger.generate_tags') as mock_tagger, \
             patch('src.ai.enhancer.AIEnhancer.enhance_note') as mock_enhancer:

            mock_tagger.return_value = ["test", "ai-added"]
            mock_enhancer.return_value = {
                "quality": {"score": 0.85, "reason": "Excellent"},
                "summary": "Test"
            }

            # Process the note
            results = workflow_manager.process_inbox_note(str(note_path), fast=False)

            # Verify status updated
            updated_content = note_path.read_text(encoding="utf-8")
            assert "status: promoted" in updated_content

            # Verify other fields preserved
            assert "type: fleeting" in updated_content
            assert "created: 2025-01-01 10:00" in updated_content
            assert "custom_field: important_value" in updated_content

    def test_process_inbox_note_fast_mode_skips_status_update(self, workflow_manager, temp_vault):
        """
        Fast mode (no AI processing) should not update status.
        Only full AI processing should trigger status update.
        """
        note_content = """---
type: fleeting
status: inbox
tags: [test]
---

# Test Note

Fast mode test content."""

        note_path = self.create_test_note(temp_vault, "Inbox", "test-fast.md", note_content)

        # Process in fast mode (no AI processing)
        results = workflow_manager.process_inbox_note(str(note_path), fast=True)

        # Verify status was NOT updated (fast mode doesn't do AI processing)
        updated_content = note_path.read_text(encoding="utf-8")
        assert "status: inbox" in updated_content, "Status should remain 'inbox' in fast mode"
        assert "status_updated" not in results, "Results should not include status_updated in fast mode"
        assert "processed_date" not in updated_content, "processed_date should not be added in fast mode"
