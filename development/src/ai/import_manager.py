from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import json
import csv
import re

from .import_schema import ImportItem, validate_item


class CSVImportAdapter:
    """Load ImportItem rows from a CSV file."""

    @staticmethod
    def load(path: Path) -> List[ImportItem]:
        items: List[ImportItem] = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for raw in reader:
                data = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw.items()}
                try:
                    items.append(validate_item(data))
                except Exception:
                    # Skip invalid rows for now; higher-level CLI can report counts
                    continue
        return items


class JSONImportAdapter:
    """Load ImportItem rows from a JSON file."""

    @staticmethod
    def load(path: Path) -> List[ImportItem]:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        rows: List[Dict[str, Any]]
        if isinstance(data, list):
            rows = [dict(x) for x in data]
        elif isinstance(data, dict) and isinstance(data.get("items"), list):
            rows = [dict(x) for x in data["items"]]
        else:
            raise ValueError("Unsupported JSON structure: expected a list or an object with 'items'.")
        items: List[ImportItem] = []
        for raw in rows:
            try:
                items.append(validate_item(raw))
            except Exception:
                continue
        return items


_FRONTMATTER_BOUNDARY = "---"
_YAML_KEY_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def _read_yaml_frontmatter(md_path: Path) -> Dict[str, Any]:
    """Very small YAML-like frontmatter reader for url/saved_at."""
    content = md_path.read_text(encoding='utf-8', errors='ignore').splitlines()
    if not content or content[0].strip() != _FRONTMATTER_BOUNDARY:
        return {}
    data: Dict[str, Any] = {}
    for line in content[1:]:
        s = line.strip()
        if s == _FRONTMATTER_BOUNDARY:
            break
        m = _YAML_KEY_RE.match(s)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        data[key] = val.strip()
    return data


class NoteWriter:
    """Write ImportItems as markdown notes with YAML frontmatter."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)

    def _dest_dir(self, dest_dir: Path | None) -> Path:
        return Path(dest_dir) if dest_dir else (self.base_dir / "knowledge" / "Inbox")

    @staticmethod
    def _date_part(item: ImportItem) -> str:
        return item.saved_at.strftime("%Y-%m-%d")

    @staticmethod
    def _base_filename(item: ImportItem) -> str:
        return f"literature--{NoteWriter._date_part(item)}.md"

    def _unique_filename(self, dest: Path, item: ImportItem) -> Path:
        base = self._base_filename(item)
        p = dest / base
        if not p.exists():
            return p
        # Suffix -2, -3, ...
        n = 2
        while True:
            candidate = dest / f"literature--{self._date_part(item)}-{n}.md"
            if not candidate.exists():
                return candidate
            n += 1

    @staticmethod
    def _yaml_frontmatter(item: ImportItem, created: datetime | None = None) -> str:
        created_dt = created or datetime.now()
        topics_block = "[]" if not item.topics else f"[{', '.join([repr(t) for t in item.topics])}]"
        # Ensure saved_at ISO format without microseconds
        saved_iso = item.saved_at.replace(microsecond=0).isoformat()
        return (
            "---\n"
            f"title: {item.title}\n"
            f"url: {item.url}\n"
            f"source: {item.source}\n"
            f"saved_at: {saved_iso}\n"
            f"type: {item.type}\n"
            f"topics: {topics_block}\n"
            f"status: inbox\n"
            f"created: {created_dt.strftime('%Y-%m-%d %H:%M')}\n"
            "---\n\n"
        )

    def _body(self, template_rel: Path | None = None) -> str:
        if template_rel:
            p = self.base_dir / template_rel
            if p.exists():
                try:
                    return p.read_text(encoding='utf-8')
                except Exception:
                    pass
        # Fallback scaffold
        return (
            "## Claims\n\n"
            "- \n\n"
            "## Quotes\n\n"
            "> \n\n"
            "## Links\n\n"
            "- \n"
        )

    def _is_duplicate(self, dest: Path, item: ImportItem) -> bool:
        # Quick scan for existing notes on the same date
        date_prefix = f"literature--{self._date_part(item)}"
        for md in dest.glob(f"{date_prefix}*.md"):
            fm = _read_yaml_frontmatter(md)
            if not fm:
                continue
            if fm.get("url") == item.url and fm.get("saved_at"):
                # Normalize saved_at for comparison up to seconds
                try:
                    existing_dt = datetime.fromisoformat(fm["saved_at"].replace("Z", "+00:00"))
                    if existing_dt.replace(microsecond=0) == item.saved_at.replace(microsecond=0):
                        return True
                except Exception:
                    pass
        return False

    def write_items(self, items: List[ImportItem], dest_dir: Path | None = None, force: bool = False) -> Tuple[int, int, List[Path]]:
        dest = self._dest_dir(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        written = 0
        skipped = 0
        paths: List[Path] = []
        for item in items:
            if not force and self._is_duplicate(dest, item):
                skipped += 1
                continue
            target = self._unique_filename(dest, item)
            content = self._yaml_frontmatter(item) + self._body(Path("Templates/literature.md"))
            target.write_text(content, encoding='utf-8')
            paths.append(target)
            written += 1
        return written, skipped, paths
