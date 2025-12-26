#!/usr/bin/env python3
"""Backfill frontmatter fields for YouTube notes in Inbox/YouTube.

Purpose
- Ensure YouTube notes have canonical `url` in frontmatter.
- Fill `url` from existing `video_id` when missing.
- Optionally ensure `source: youtube` and `ready_for_processing` exist.

Safety
- Dry-run by default (prints planned changes, does not write files).
- When --apply is used, a backup copy is created for each changed file.
- Frontmatter-only: does not modify note body content.

Scope
- Only scans: <vault>/Inbox/YouTube/*.md

Usage
- Dry run:
    python development/scripts/backfill_youtube_note_frontmatter.py /path/to/knowledge
- Apply changes (with backups):
    python development/scripts/backfill_youtube_note_frontmatter.py /path/to/knowledge --apply

"""

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import shutil

# Add development to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.frontmatter import build_frontmatter, parse_frontmatter


@dataclass
class ChangePlan:
    path: Path
    planned_updates: Dict[str, Tuple[Any, Any]]  # key -> (old, new)


def _canonical_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def plan_updates(frontmatter: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
    updates: Dict[str, Tuple[Any, Any]] = {}

    # If source is present and not youtube, do not touch.
    source = frontmatter.get("source")
    if source is not None and str(source).strip().lower() != "youtube":
        return {"__skip__": (source, source)}

    if source is None:
        updates["source"] = (None, "youtube")

    if "ready_for_processing" not in frontmatter:
        updates["ready_for_processing"] = (None, False)

    url = frontmatter.get("url")
    if not url:
        video_id = frontmatter.get("video_id")
        if isinstance(video_id, str) and video_id.strip():
            updates["url"] = (url, _canonical_youtube_url(video_id.strip()))

    return updates


def apply_updates(
    frontmatter: Dict[str, Any], updates: Dict[str, Tuple[Any, Any]]
) -> Dict[str, Any]:
    out = dict(frontmatter)
    for key, (_, new_val) in updates.items():
        if key == "__skip__":
            continue
        out[key] = new_val
    return out


def create_backup_dir(vault_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = vault_path / "backups" / f"youtube-frontmatter-backfill-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def backup_file(note_path: Path, vault_path: Path, backup_dir: Path) -> Path:
    relative = note_path.relative_to(vault_path)
    target = backup_dir / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(note_path, target)
    return target


def process_note(
    note_path: Path, vault_path: Path
) -> Tuple[Optional[ChangePlan], Optional[str]]:
    try:
        raw = note_path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"read_error: {e}"

    frontmatter, body = parse_frontmatter(raw)
    updates = plan_updates(frontmatter)

    if "__skip__" in updates:
        return None, "skipped_non_youtube_source"

    if not updates:
        return None, None

    return ChangePlan(path=note_path, planned_updates=updates), None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill YouTube note frontmatter (Inbox/YouTube only). Dry-run by default."
    )
    parser.add_argument(
        "vault_path",
        help="Path to knowledge vault root (e.g. /Users/thaddius/repos/inneros-zettelkasten/knowledge)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes to files (creates backups for changed files)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files processed (useful for testing)",
    )

    args = parser.parse_args()

    vault_path = Path(args.vault_path).expanduser().resolve()
    if not vault_path.exists():
        print(f"❌ Vault path does not exist: {vault_path}")
        return 2

    youtube_dir = vault_path / "Inbox" / "YouTube"
    if not youtube_dir.exists():
        print(f"❌ YouTube inbox directory not found: {youtube_dir}")
        return 2

    md_files = sorted(youtube_dir.glob("*.md"))
    if args.limit is not None:
        md_files = md_files[: args.limit]

    dry_run = not args.apply

    print(f"{'[DRY RUN] ' if dry_run else ''}YouTube Frontmatter Backfill")
    print(f"Vault: {vault_path}")
    print(f"Scan:  {youtube_dir}")
    print()

    plans: List[ChangePlan] = []
    skipped_non_youtube = 0
    errors: List[str] = []

    for p in md_files:
        plan, err = process_note(p, vault_path)
        if err == "skipped_non_youtube_source":
            skipped_non_youtube += 1
            continue
        if err:
            errors.append(f"{p}: {err}")
            continue
        if plan:
            plans.append(plan)

    print(f"Files scanned: {len(md_files)}")
    print(f"Planned changes: {len(plans)}")
    print(f"Skipped (non-youtube source): {skipped_non_youtube}")
    print(f"Errors: {len(errors)}")
    if errors:
        for e in errors[:10]:
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... {len(errors) - 10} more")
    print()

    if not plans:
        print("✅ No changes needed")
        return 0

    # Show plan details
    for plan in plans:
        rel = plan.path.relative_to(vault_path)
        print(f"- {rel}")
        for k, (old, new) in plan.planned_updates.items():
            print(f"  - {k}: {old!r} -> {new!r}")

    if dry_run:
        print()
        print("DRY RUN: no files modified. Re-run with --apply to write changes.")
        return 0

    # Apply changes
    backup_dir = create_backup_dir(vault_path)
    print()
    print(f"📦 Backups: {backup_dir}")

    changed = 0
    write_errors: List[str] = []

    for plan in plans:
        try:
            raw = plan.path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(raw)
            updated_frontmatter = apply_updates(frontmatter, plan.planned_updates)

            # Backup before write
            backup_file(plan.path, vault_path, backup_dir)

            updated = build_frontmatter(updated_frontmatter, body)
            plan.path.write_text(updated, encoding="utf-8")
            changed += 1
        except Exception as e:
            write_errors.append(f"{plan.path}: write_error: {e}")

    print(f"\n✅ Updated files: {changed}")
    if write_errors:
        print(f"❌ Write errors: {len(write_errors)}")
        for e in write_errors[:10]:
            print(f"  - {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
