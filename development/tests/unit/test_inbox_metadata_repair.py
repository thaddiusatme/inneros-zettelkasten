"""Inbox metadata repair integration tests.

Red-phase tests for a higher-level inbox metadata repair flow that
coordinates MetadataRepairEngine with auto-promotion.

Goals for this suite:
- Encode real-world "broken → repaired" inbox metadata patterns.
- Ensure repair is idempotent and non-destructive.
- Prove that auto-promotion can run without metadata errors after repair.
"""

from pathlib import Path

import pytest

from src.ai.workflow_manager import WorkflowManager
from src.utils.frontmatter import parse_frontmatter


class TestInboxMetadataRepairIntegration:
    """Integration tests for inbox metadata repair + auto-promotion."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """Create a temporary vault with standard directories."""
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()

        (base_dir / "Inbox").mkdir()
        (base_dir / "Fleeting Notes").mkdir()
        (base_dir / "Literature Notes").mkdir()
        (base_dir / "Permanent Notes").mkdir()

        return base_dir

    @pytest.fixture
    def workflow_manager(self, temp_vault: Path) -> WorkflowManager:
        """WorkflowManager bound to the temporary vault."""
        return WorkflowManager(base_directory=str(temp_vault))

    def _write_inbox_note(self, base_dir: Path, filename: str, content: str) -> Path:
        inbox = base_dir / "Inbox"
        note_path = inbox / filename
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def test_repair_adds_type_created_and_status_when_missing(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Repair should add type, created, and status for broken inbox notes.

        This drives the requirement that inbox metadata repair normalizes
        the core lifecycle fields expected by auto-promotion and other
        workflows: status, type, and created.
        """

        broken_content = """---
quality_score: 0.85
---

# Broken Note

Content without type/created/status.
"""
        note_path = self._write_inbox_note(
            temp_vault, "voice-note-prompts-for-knowledge-capture.md", broken_content
        )

        # Act: execute repair (not dry-run)
        result = workflow_manager.repair_inbox_metadata(execute=True)

        # Assert: repair should have run on exactly one note
        assert result["notes_scanned"] == 1
        assert result["repairs_needed"] == 1
        assert result["repairs_made"] == 1

        # Verify frontmatter now includes core fields
        updated = note_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(updated)

        # Red-phase expectations (these currently do not all hold):
        # - type is present and non-empty
        # - created is present and has a timestamp-like value
        # - status is present and normalized to "inbox" for Inbox notes
        assert frontmatter.get("type"), "type should be added for broken notes"
        assert frontmatter.get("created"), "created should be added for broken notes"
        assert frontmatter.get("status") == "inbox"

    def test_repair_is_idempotent_on_already_fixed_notes(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Second repair run should report zero additional repairs.

        This test enforces idempotence at the stats level: once a note has
        been repaired, running repair again should not count it as a new
        repair operation.
        """

        broken_content = """---
quality_score: 0.80
---

# Broken Note

Another note without metadata.
"""
        note_path = self._write_inbox_note(temp_vault, "sprint-2-8020.md", broken_content)

        # First run: should repair the note
        first = workflow_manager.repair_inbox_metadata(execute=True)
        assert first["notes_scanned"] == 1
        assert first["repairs_needed"] == 1
        assert first["repairs_made"] == 1

        # Second run: should detect no further repairs needed
        second = workflow_manager.repair_inbox_metadata(execute=True)
        assert second["notes_scanned"] == 1
        # Red-phase expectation: no new repairs should be counted on second run
        assert (
            second["repairs_made"] == 0
        ), "repair should be idempotent for already-fixed notes"

        # File content should remain valid and unchanged on second run
        updated = note_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(updated)
        assert frontmatter.get("type") is not None
        assert frontmatter.get("created") is not None

    def test_repair_does_not_change_notes_with_complete_metadata(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Notes with complete metadata should be left untouched."""

        complete_content = """---
type: fleeting
status: inbox
created: 2025-10-15 14:00
quality_score: 0.85
---

# Complete Note

Already valid frontmatter.
"""
        note_path = self._write_inbox_note(
            temp_vault, "complete-note.md", complete_content
        )

        before = note_path.read_text(encoding="utf-8")

        result = workflow_manager.repair_inbox_metadata(execute=True)

        # Should scan, but not need or make repairs
        assert result["notes_scanned"] == 1
        assert result["repairs_needed"] == 0
        assert result["repairs_made"] == 0

        after = note_path.read_text(encoding="utf-8")
        assert after == before

    def test_repair_enables_auto_promote_for_missing_type_notes(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Repair should unblock auto-promotion for notes missing type.

        Before repair: auto-promote should report validation errors for
        missing 'type' field. After repair: the same notes should be
        promotable with zero metadata errors.
        """

        # Two representative notes from the historical blocked set
        broken_notes = {
            "voice-note-prompts-for-knowledge-capture.md": """---
status: inbox
quality_score: 0.85
---

# Voice Note Prompts

Content without type/created.
""",
            "newsletter-generator-prompt.md": """---
status: inbox
quality_score: 0.80
---

# Newsletter Generator Prompt

Source: https://example.com/newsletter
""",
        }

        for filename, content in broken_notes.items():
            self._write_inbox_note(temp_vault, filename, content)

        # Precondition: auto-promote should see metadata errors due to missing type
        before = workflow_manager.auto_promote_ready_notes(dry_run=True, quality_threshold=0.7)
        assert before["total_candidates"] == 2
        assert before["error_count"] >= 1
        # At least one error message should reference 'type'
        assert any("type" in msg.lower() for msg in before["errors"].values())

        # Act: repair metadata (execute mode) and re-run auto-promotion
        workflow_manager.repair_inbox_metadata(execute=True)
        after = workflow_manager.auto_promote_ready_notes(dry_run=True, quality_threshold=0.7)

        # After repair: no metadata errors; both notes should be promotable
        assert after["total_candidates"] == 2
        assert after["error_count"] == 0
        assert after.get("would_promote_count", 0) == 2

    def test_repair_dry_run_does_not_modify_files(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Dry-run mode should preview repairs without touching disk."""

        broken_content = """---
status: inbox
quality_score: 0.75
---

# Dry Run Note

Needs metadata repair.
"""
        note_path = self._write_inbox_note(temp_vault, "progress-8-26.md", broken_content)

        before = note_path.read_text(encoding="utf-8")

        result = workflow_manager.repair_inbox_metadata(execute=False)

        # Should report repairs needed but not made
        assert result["notes_scanned"] == 1
        assert result["repairs_needed"] == 1
        assert result["repairs_made"] == 0

        # File content untouched in dry-run mode
        after = note_path.read_text(encoding="utf-8")
        assert after == before
