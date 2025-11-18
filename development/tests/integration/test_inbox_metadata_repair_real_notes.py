"""Integration tests for Inbox Metadata Repair with real historical blocked notes.

These tests use fixtures that mirror the 8 real Inbox notes that were originally
blocked from auto-promotion due to missing metadata. The goal is to validate
that repair + auto-promotion behaves correctly on realistic data:

- MetadataRepairEngine repairs all 8 notes (type/created/status normalized).
- auto_promote_ready_notes(dry_run=True) reports 0 metadata errors after repair.
- Repair remains idempotent when run a second time.
- auto_promote_ready_notes(dry_run=True) reports expected types and targets for all 8 notes.
"""

from pathlib import Path
import re
import shutil

import pytest

from src.ai.workflow_manager import WorkflowManager
from src.utils.frontmatter import parse_frontmatter


FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "inbox_metadata_real"


class TestInboxMetadataRepairRealNotes:
    """End-to-end tests for metadata repair + auto-promotion on real fixtures."""

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

    def _populate_inbox_with_real_fixtures(self, base_dir: Path) -> None:
        """Copy all real blocked-note fixtures into the temp Inbox."""
        inbox = base_dir / "Inbox"
        assert FIXTURE_DIR.exists(), f"Fixture directory not found: {FIXTURE_DIR}"

        for fixture_path in FIXTURE_DIR.glob("*.md"):
            target = inbox / fixture_path.name
            shutil.copy(fixture_path, target)

    def test_repair_and_auto_promote_real_blocked_notes_end_to_end(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Repair + auto-promotion should be clean for all 8 real fixtures.

        Before repair:
        - auto_promote_ready_notes should report metadata errors for missing type.

        After repair:
        - all 8 notes should have normalized metadata
        - auto_promote_ready_notes(dry_run=True) should report 0 metadata errors
        - all 8 candidates should be promotable (would_promote_count == 8)
        """
        # Arrange: populate Inbox with the 8 real fixtures
        self._populate_inbox_with_real_fixtures(temp_vault)
        inbox = temp_vault / "Inbox"
        inbox_files = sorted(inbox.glob("*.md"))
        assert len(inbox_files) == 8, "Expected 8 real fixtures in Inbox"

        # Precondition: auto-promotion sees metadata errors due to missing type/created
        before = workflow_manager.auto_promote_ready_notes(
            dry_run=True, quality_threshold=0.7
        )

        # All 8 real fixtures should be treated as candidates but blocked by metadata
        assert before["total_candidates"] == 8
        assert before["skipped_count"] == 8
        assert before["error_count"] == 8
        assert before.get("would_promote_count", 0) == 0
        assert before.get("preview", []) == []

        # Every error should be a missing-type style validation issue
        assert before["errors"], "Expected per-note error messages before repair"
        assert len(before["errors"]) == 8
        for msg in before["errors"].values():
            assert "type" in msg.lower()

        # Act: execute metadata repair and run auto-promotion again in dry-run mode
        repair_result = workflow_manager.repair_inbox_metadata(execute=True)

        # We expect all 8 notes to require and receive repairs on first pass
        assert repair_result["notes_scanned"] == 8
        assert repair_result["repairs_needed"] == 8
        assert repair_result["repairs_made"] == 8
        assert repair_result["errors"] == []

        # Verify repaired metadata on disk: types and timestamps match expectations
        expected_types = {
            "voice-note-prompts-for-knowledge-capture.md": "fleeting",
            "Study link between price risk and trust in decision-making.md": "fleeting",
            "sprint 2 8020.md": "fleeting",
            "newsletter-generator-prompt.md": "literature",
            "zettelkasten-voice-prompts-v1.md": "fleeting",
            "Progress-8-26.md": "fleeting",
            "enhanced-connections-live-data-analysis-report.md": "fleeting",
            "voice-prompts-quick-reference-card.md": "fleeting",
        }
        created_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")

        for note_path in inbox_files:
            updated = note_path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(updated)
            note_name = note_path.name

            # Type must be present and match the manifest-driven expectation
            assert frontmatter.get("type"), f"{note_name} should have type after repair"
            assert (
                frontmatter["type"] == expected_types[note_name]
            ), f"{note_name} should have expected type after repair"

            # created should be present and match YYYY-MM-DD HH:MM
            created_value = frontmatter.get("created")
            assert created_value, f"{note_name} should have created after repair"
            assert created_pattern.match(
                str(created_value)
            ), f"{note_name} created should match YYYY-MM-DD HH:MM"

            # status should remain normalized to inbox for all repaired notes
            assert frontmatter.get("status") == "inbox"

        after = workflow_manager.auto_promote_ready_notes(
            dry_run=True, quality_threshold=0.7
        )

        # After repair: no metadata-driven errors; all 8 candidates promotable
        assert after["total_candidates"] == 8
        assert after["error_count"] == 0
        assert after["skipped_count"] == 0
        assert after.get("would_promote_count", 0) == 8

        # Preview should include all 8 notes with correct inferred types and targets
        preview = after.get("preview", [])
        assert len(preview) == 8
        by_note = {entry["note"]: entry for entry in preview}

        # Newsletter prompt should be treated as literature in auto-promotion preview
        nl_entry = by_note["newsletter-generator-prompt.md"]
        assert nl_entry["type"] == "literature"
        assert nl_entry["target"] == "Literature Notes/"
        assert nl_entry["quality"] == pytest.approx(0.8)

        # All other real fixtures should be treated as fleeting notes
        fleeting_expected = {
            "voice-note-prompts-for-knowledge-capture.md": 0.85,
            "Study link between price risk and trust in decision-making.md": 0.8,
            "sprint 2 8020.md": 0.8,
            "zettelkasten-voice-prompts-v1.md": 0.85,
            "Progress-8-26.md": 0.75,
            "enhanced-connections-live-data-analysis-report.md": 0.85,
            "voice-prompts-quick-reference-card.md": 0.85,
        }
        for name, expected_quality in fleeting_expected.items():
            entry = by_note[name]
            assert entry["type"] == "fleeting"
            assert entry["target"] == "Fleeting Notes/"
            assert entry["quality"] == pytest.approx(expected_quality)

    def test_real_blocked_notes_repair_is_idempotent(
        self, workflow_manager: WorkflowManager, temp_vault: Path
    ) -> None:
        """Running repair twice for the real fixtures should be idempotent."""
        self._populate_inbox_with_real_fixtures(temp_vault)

        # First run repairs all 8 notes
        first = workflow_manager.repair_inbox_metadata(execute=True)
        assert first["notes_scanned"] == 8
        assert first["repairs_needed"] == 8
        assert first["repairs_made"] == 8

        # Second run should see no missing metadata and perform no additional repairs
        second = workflow_manager.repair_inbox_metadata(execute=True)
        assert second["notes_scanned"] == 8
        assert second["repairs_needed"] == 0
        assert second["repairs_made"] == 0
        assert second["errors"] == []
