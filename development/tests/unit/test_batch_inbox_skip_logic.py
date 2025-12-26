"""
Unit tests for batch inbox processing with skip logic (Phase 4-5).

RED Phase: Tests for determining which notes need processing.
Skip logic: Notes with BOTH ai_processed=true AND triage_recommendation present are skipped.
"""

import pytest
from pathlib import Path
from unittest.mock import patch


# Mark all tests in this module for CI
pytestmark = [pytest.mark.ci]


class TestNoteEligibilityDetection:
    """Tests for determining if a note needs processing."""

    def test_note_missing_ai_processed_is_eligible(self, tmp_path: Path):
        """A note without ai_processed field should be eligible for processing."""
        # Create note without ai_processed
        note = tmp_path / "Inbox" / "test-note.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            """---
title: Test Note
type: fleeting
---
# Content
"""
        )

        from src.ai.batch_inbox_processor import is_note_eligible_for_processing

        assert is_note_eligible_for_processing(note) is True

    def test_note_missing_triage_recommendation_is_eligible(self, tmp_path: Path):
        """A note with ai_processed but missing triage_recommendation should be eligible."""
        note = tmp_path / "Inbox" / "test-note.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            """---
title: Test Note
type: fleeting
ai_processed: true
---
# Content
"""
        )

        from src.ai.batch_inbox_processor import is_note_eligible_for_processing

        assert is_note_eligible_for_processing(note) is True

    def test_note_with_both_fields_is_not_eligible(self, tmp_path: Path):
        """A note with BOTH ai_processed and triage_recommendation should be skipped."""
        note = tmp_path / "Inbox" / "test-note.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            """---
title: Test Note
type: fleeting
ai_processed: true
triage_recommendation: promote_to_permanent
---
# Content
"""
        )

        from src.ai.batch_inbox_processor import is_note_eligible_for_processing

        assert is_note_eligible_for_processing(note) is False

    def test_note_with_ai_processed_false_is_eligible(self, tmp_path: Path):
        """A note with ai_processed: false should be eligible."""
        note = tmp_path / "Inbox" / "test-note.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            """---
title: Test Note
type: fleeting
ai_processed: false
triage_recommendation: promote_to_permanent
---
# Content
"""
        )

        from src.ai.batch_inbox_processor import is_note_eligible_for_processing

        assert is_note_eligible_for_processing(note) is True


class TestBatchInboxScanner:
    """Tests for scanning inbox and filtering eligible notes."""

    def test_scan_returns_only_eligible_notes(self, tmp_path: Path):
        """scan_eligible_notes should return only notes needing processing."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        # Eligible: missing ai_processed
        (inbox / "note1.md").write_text(
            """---
title: Note 1
---
Content
"""
        )

        # Eligible: missing triage_recommendation
        (inbox / "note2.md").write_text(
            """---
title: Note 2
ai_processed: true
---
Content
"""
        )

        # NOT eligible: has both
        (inbox / "note3.md").write_text(
            """---
title: Note 3
ai_processed: true
triage_recommendation: move_to_fleeting
---
Content
"""
        )

        from src.ai.batch_inbox_processor import scan_eligible_notes

        eligible = scan_eligible_notes(inbox)

        assert len(eligible) == 2
        eligible_names = {p.name for p in eligible}
        assert "note1.md" in eligible_names
        assert "note2.md" in eligible_names
        assert "note3.md" not in eligible_names

    def test_scan_handles_empty_inbox(self, tmp_path: Path):
        """scan_eligible_notes should return empty list for empty inbox."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        from src.ai.batch_inbox_processor import scan_eligible_notes

        eligible = scan_eligible_notes(inbox)
        assert eligible == []

    def test_scan_ignores_non_markdown_files(self, tmp_path: Path):
        """scan_eligible_notes should only process .md files."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        (inbox / "note.md").write_text("---\ntitle: Note\n---\nContent")
        (inbox / "readme.txt").write_text("Not a note")
        (inbox / "image.png").write_bytes(b"fake image")

        from src.ai.batch_inbox_processor import scan_eligible_notes

        eligible = scan_eligible_notes(inbox)
        assert len(eligible) == 1
        assert eligible[0].name == "note.md"


class TestBatchProcessInbox:
    """Tests for the main batch processing function."""

    def test_batch_process_returns_summary(self, tmp_path: Path):
        """batch_process_unprocessed_inbox should return processing summary."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        (inbox / "note1.md").write_text("---\ntitle: Note 1\n---\nContent")

        from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox

        # Mock the actual processing to avoid AI calls
        with patch("src.ai.batch_inbox_processor.process_single_note") as mock_process:
            mock_process.return_value = {
                "success": True,
                "triage_recommendation": "promote_to_permanent",
            }

            result = batch_process_unprocessed_inbox(inbox, dry_run=False)

        assert "processed" in result
        assert "skipped" in result
        assert "errors" in result
        assert "summary" in result

    def test_batch_process_dry_run_makes_no_changes(self, tmp_path: Path):
        """batch_process_unprocessed_inbox with dry_run=True should not modify files."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        original_content = "---\ntitle: Note 1\n---\nContent"
        note = inbox / "note1.md"
        note.write_text(original_content)

        from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox

        result = batch_process_unprocessed_inbox(inbox, dry_run=True)

        # File should be unchanged
        assert note.read_text() == original_content
        # Result should indicate what WOULD be processed
        assert result.get("dry_run") is True
        assert result.get("would_process", 0) >= 1

    def test_batch_process_skips_already_processed(self, tmp_path: Path):
        """Already processed notes should be skipped and counted."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        # Already processed
        (inbox / "processed.md").write_text(
            """---
title: Processed
ai_processed: true
triage_recommendation: promote_to_permanent
---
Content
"""
        )

        # Not processed
        (inbox / "new.md").write_text("---\ntitle: New\n---\nContent")

        from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox

        with patch("src.ai.batch_inbox_processor.process_single_note") as mock_process:
            mock_process.return_value = {"success": True}
            result = batch_process_unprocessed_inbox(inbox, dry_run=False)

        assert result["skipped"] == 1
        assert result["processed"] == 1


class TestTriageBreakdown:
    """Tests for triage breakdown in summary output."""

    def test_summary_includes_triage_breakdown(self, tmp_path: Path):
        """Summary should include breakdown by triage_recommendation."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        (inbox / "note1.md").write_text("---\ntitle: Note 1\n---\nContent")
        (inbox / "note2.md").write_text("---\ntitle: Note 2\n---\nContent")

        from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox

        with patch("src.ai.batch_inbox_processor.process_single_note") as mock_process:
            # Simulate different recommendations
            mock_process.side_effect = [
                {"success": True, "triage_recommendation": "promote_to_permanent"},
                {"success": True, "triage_recommendation": "move_to_fleeting"},
            ]

            result = batch_process_unprocessed_inbox(inbox, dry_run=False)

        summary = result.get("summary", {})
        assert "by_recommendation" in summary
        assert summary["by_recommendation"].get("promote_to_permanent", 0) == 1
        assert summary["by_recommendation"].get("move_to_fleeting", 0) == 1


class TestErrorHandling:
    """Tests for error handling in batch processing."""

    def test_errors_are_captured_and_reported(self, tmp_path: Path):
        """Processing errors should be captured in the result."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        (inbox / "bad-note.md").write_text("---\ntitle: Bad Note\n---\nContent")

        from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox

        with patch("src.ai.batch_inbox_processor.process_single_note") as mock_process:
            mock_process.side_effect = Exception("AI service unavailable")

            result = batch_process_unprocessed_inbox(inbox, dry_run=False)

        assert result["errors"] == 1
        assert len(result.get("error_details", [])) == 1
        assert "AI service unavailable" in result["error_details"][0]["error"]

    def test_batch_continues_after_single_note_error(self, tmp_path: Path):
        """Batch processing should continue even if one note fails."""
        inbox = tmp_path / "Inbox"
        inbox.mkdir(parents=True)

        (inbox / "note1.md").write_text("---\ntitle: Note 1\n---\nContent")
        (inbox / "note2.md").write_text("---\ntitle: Note 2\n---\nContent")

        from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox

        with patch("src.ai.batch_inbox_processor.process_single_note") as mock_process:
            # First note fails, second succeeds
            mock_process.side_effect = [
                Exception("Failed"),
                {"success": True, "triage_recommendation": "promote_to_permanent"},
            ]

            result = batch_process_unprocessed_inbox(inbox, dry_run=False)

        assert result["processed"] == 1
        assert result["errors"] == 1
