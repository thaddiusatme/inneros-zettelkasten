"""
Vault-wide media audit: detect broken image embeds and orphaned media files.

Usage:
    python -m src.utils.media_audit <vault_path>
    python development/src/utils/media_audit.py knowledge/
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict

from .image_link_manager import ImageLinkManager

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".m4a", ".mp4"}
MEDIA_DIRS = {"Media", "attachments"}


@dataclass
class AuditResult:
    broken_embeds: List[Dict] = field(default_factory=list)
    orphaned_media: List[Path] = field(default_factory=list)

    @property
    def total_broken(self) -> int:
        return len(self.broken_embeds)

    @property
    def total_orphaned(self) -> int:
        return len(self.orphaned_media)


def audit_vault(vault_path: Path) -> AuditResult:
    result = AuditResult()
    manager = ImageLinkManager(base_path=vault_path)

    # Collect all media files
    all_media: List[Path] = []
    for media_dir_name in MEDIA_DIRS:
        media_dir = vault_path / media_dir_name
        if media_dir.exists():
            for f in media_dir.rglob("*"):
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                    all_media.append(f)

    referenced_filenames: set[str] = set()

    # Walk all notes, collect broken embeds and referenced filenames
    for note in vault_path.rglob("*.md"):
        try:
            content = note.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        broken = manager.validate_image_links(note, content)
        result.broken_embeds.extend(broken)

        # Track which filenames are referenced (for orphan detection)
        for link in manager.parse_image_links(content):
            referenced_filenames.add(
                link.get("filename") or Path(link.get("path", "")).name
            )

    # Orphaned = media file with no note referencing its filename
    for media_file in all_media:
        if media_file.name not in referenced_filenames:
            result.orphaned_media.append(media_file)

    return result


def _print_report(vault_path: Path, result: AuditResult) -> None:
    print(f"\nMedia audit: {vault_path}\n{'─' * 50}")
    print(f"Broken embeds:   {result.total_broken}")
    print(f"Orphaned media:  {result.total_orphaned}")

    if result.broken_embeds:
        print("\n── Broken embeds ──")
        folder_order = ["Permanent Notes", "Content Pipeline", "Fleeting Notes"]

        def sort_key(e):
            p = e["note_path"]
            for i, folder in enumerate(folder_order):
                if folder in p:
                    return i
            return len(folder_order)

        for entry in sorted(result.broken_embeds, key=sort_key):
            rel = (
                Path(entry["note_path"]).relative_to(vault_path)
                if vault_path in Path(entry["note_path"]).parents
                else entry["note_path"]
            )
            print(f"  {rel}  →  {entry['image_path']}")

    if result.orphaned_media:
        print("\n── Orphaned media ──")
        for f in result.orphaned_media:
            try:
                rel = f.relative_to(vault_path)
            except ValueError:
                rel = f
            print(f"  {rel}")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cd development && python -m src.utils.media_audit <vault_path>")
        sys.exit(1)
    vault = Path(sys.argv[1]).resolve()
    if not vault.is_dir():
        print(f"Error: {vault} is not a directory")
        sys.exit(1)
    _print_report(vault, audit_vault(vault))
