"""
Tests for media_audit.py — vault-wide broken embed and orphaned media detection.
Issue #130.
"""

import tempfile
import shutil
from pathlib import Path

import pytest

from src.utils.media_audit import audit_vault, AuditResult


def _make_vault(base: Path) -> Path:
    vault = base / "vault"
    vault.mkdir()
    (vault / "Permanent Notes").mkdir()
    (vault / "Content Pipeline").mkdir()
    (vault / "Fleeting Notes").mkdir()
    (vault / "Archive").mkdir()
    (vault / "Media").mkdir()
    return vault


class TestMediaAudit:

    def setup_method(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.vault = _make_vault(self.tmp)

    def teardown_method(self):
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_clean_vault_returns_empty_results(self):
        """No notes, no media → no broken refs, no orphans."""
        result = audit_vault(self.vault)
        assert isinstance(result, AuditResult)
        assert result.broken_embeds == []
        assert result.orphaned_media == []

    def test_detects_broken_wiki_embed(self):
        """A note with ![[ghost.png]] and no such file in Media/ is reported as broken."""
        note = self.vault / "Permanent Notes" / "my-note.md"
        note.write_text("# Note\n\n![[ghost.png]]\n")

        result = audit_vault(self.vault)

        assert len(result.broken_embeds) == 1
        entry = result.broken_embeds[0]
        assert entry["note_path"] == str(note)
        assert entry["image_path"] == "ghost.png"

    def test_detects_orphaned_media_file(self):
        """An image in Media/ with no note referencing it is reported as orphaned."""
        (self.vault / "Media" / "unused.png").write_bytes(b"fake")

        result = audit_vault(self.vault)

        assert len(result.orphaned_media) == 1
        assert result.orphaned_media[0].name == "unused.png"

    def test_linked_image_not_reported_broken_or_orphaned(self):
        """An image in Media/ that IS referenced by a note is neither broken nor orphaned."""
        img = self.vault / "Media" / "real.png"
        img.write_bytes(b"fake")
        note = self.vault / "Permanent Notes" / "linked-note.md"
        note.write_text("# Note\n\n![[real.png]]\n")

        result = audit_vault(self.vault)

        assert result.broken_embeds == []
        assert result.orphaned_media == []

    def test_counts_multiple_broken_embeds_across_notes(self):
        """Each broken embed in each note is counted individually."""
        (self.vault / "Permanent Notes" / "note-a.md").write_text(
            "![[missing-a.png]]\n![[missing-b.png]]\n"
        )
        (self.vault / "Content Pipeline" / "note-b.md").write_text(
            "![[missing-c.png]]\n"
        )

        result = audit_vault(self.vault)

        assert len(result.broken_embeds) == 3

    def test_audit_result_has_summary_counts(self):
        """AuditResult exposes total_broken and total_orphaned convenience counts."""
        (self.vault / "Media" / "orphan.png").write_bytes(b"fake")
        (self.vault / "Permanent Notes" / "bad-note.md").write_text("![[ghost.png]]\n")

        result = audit_vault(self.vault)

        assert result.total_broken == 1
        assert result.total_orphaned == 1
