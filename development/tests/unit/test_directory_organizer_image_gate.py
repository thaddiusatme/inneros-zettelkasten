"""
Tests for the pre-migration image validation gate in execute_moves().
Issue #129: surface broken image embeds before a note is moved.
"""

import logging
import tempfile
import shutil
from pathlib import Path

import pytest

from src.utils.directory_organizer import DirectoryOrganizer


def _make_vault(base: Path) -> Path:
    vault = base / "vault"
    vault.mkdir(parents=True)
    for d in ["Inbox", "Permanent Notes", "Fleeting Notes", "Media"]:
        (vault / d).mkdir()
    return vault


def _permanent_note_with_broken_embed(vault: Path) -> Path:
    """A permanent-type note sitting in Inbox/ (will be planned for a move)."""
    note = vault / "Inbox" / "misplaced-note.md"
    note.write_text(
        "---\ntype: permanent\nstatus: inbox\n---\n\n# Title\n\n![[ghost.png]]\n"
    )
    return note


def _permanent_note_clean(vault: Path) -> Path:
    """A permanent-type note with no image embeds."""
    note = vault / "Inbox" / "clean-note.md"
    note.write_text(
        "---\ntype: permanent\nstatus: inbox\n---\n\n# Clean\n\nNo images here.\n"
    )
    return note


class TestExecuteMovesImageGate:

    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.vault = _make_vault(self.tmp)
        self.backup_root = self.tmp / "backups"
        self.backup_root.mkdir()

    def teardown_method(self):
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_execute_moves_warns_on_broken_image_refs(self, caplog):
        """Pre-flight check logs a warning when a source note has broken embeds."""
        _permanent_note_with_broken_embed(self.vault)

        organizer = DirectoryOrganizer(
            vault_root=str(self.vault), backup_root=str(self.backup_root)
        )

        with caplog.at_level(logging.WARNING, logger="src.utils.directory_organizer"):
            organizer.execute_moves(create_backup=False)

        broken_warnings = [
            r for r in caplog.records if "broken image" in r.message.lower()
        ]
        assert broken_warnings, (
            "Expected a warning about broken image refs in misplaced-note.md, got none. "
            f"All warnings: {[r.message for r in caplog.records if r.levelno >= logging.WARNING]}"
        )

    def test_execute_moves_proceeds_despite_broken_refs(self, caplog):
        """Move completes even when source note has broken image embeds (warn, don't abort)."""
        note = _permanent_note_with_broken_embed(self.vault)

        organizer = DirectoryOrganizer(
            vault_root=str(self.vault), backup_root=str(self.backup_root)
        )

        with caplog.at_level(logging.WARNING, logger="src.utils.directory_organizer"):
            result = organizer.execute_moves(create_backup=False)

        dest = self.vault / "Permanent Notes" / note.name
        assert dest.exists(), "Note should have been moved despite broken image refs"
        assert not note.exists(), "Source note should be gone after the move"
        assert result["moves_executed"] >= 1

    def test_execute_moves_no_warning_when_images_present(self, caplog):
        """No broken-image warning when the referenced image actually exists in Media/."""
        vault = self.vault
        (vault / "Media" / "real.png").write_bytes(b"fake image")

        note = vault / "Inbox" / "good-note.md"
        note.write_text(
            "---\ntype: permanent\nstatus: inbox\n---\n\n# Title\n\n![[real.png]]\n"
        )

        organizer = DirectoryOrganizer(
            vault_root=str(vault), backup_root=str(self.backup_root)
        )

        with caplog.at_level(logging.WARNING, logger="src.utils.directory_organizer"):
            organizer.execute_moves(create_backup=False)

        broken_warnings = [
            r for r in caplog.records if "broken image" in r.message.lower()
        ]
        assert (
            not broken_warnings
        ), f"Unexpected broken-image warning: {broken_warnings}"
