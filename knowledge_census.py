import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


_RE_WIKILINK = re.compile(r"!?\[\[([^\]]+?)\]\]")
_RE_HASHTAG = re.compile(r"(?<!\w)#([A-Za-z0-9][A-Za-z0-9\-_/]*)")


def _add_dev_src_to_syspath(repo_root: Path) -> None:
    dev_src = repo_root / "development" / "src"
    if dev_src.exists() and str(dev_src) not in sys.path:
        sys.path.insert(0, str(dev_src))


def _load_utils(repo_root: Path):
    _add_dev_src_to_syspath(repo_root)
    from utils.frontmatter import parse_frontmatter  # type: ignore
    from utils.tags import sanitize_tags  # type: ignore

    return parse_frontmatter, sanitize_tags


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _first_paragraph(body: str) -> str:
    lines = [ln.rstrip() for ln in body.splitlines()]

    start_idx: Optional[int] = None
    for i, ln in enumerate(lines):
        if ln.strip():
            start_idx = i
            break

    if start_idx is None:
        return ""

    para_lines: List[str] = []
    for ln in lines[start_idx:]:
        if not ln.strip():
            break
        para_lines.append(ln)

    para = " ".join(line.strip() for line in para_lines).strip()
    para = re.sub(r"\s+", " ", para)
    return para


def _extract_wikilinks(body: str) -> List[str]:
    targets: List[str] = []
    for raw in _RE_WIKILINK.findall(body):
        target = raw.strip()
        if not target:
            continue
        target = target.split("|", 1)[0].strip()
        target = target.split("#", 1)[0].strip()
        if target:
            targets.append(target)
    return targets


def _extract_body_hashtags(body: str) -> List[str]:
    return [m.group(1) for m in _RE_HASHTAG.finditer(body)]


def _word_count(text: str) -> int:
    return len([t for t in re.split(r"\s+", text.strip()) if t])


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return str(value)


def _repo_root_from_cwd() -> Path:
    return Path.cwd().resolve()


@dataclass(frozen=True)
class NoteRecord:
    key: str
    rel_path: str
    stem: str
    metadata: Dict[str, Any]
    first_paragraph: str
    outgoing_links_raw: List[str]
    outgoing_links_resolved: List[str]
    unresolved_links: List[str]
    tags_frontmatter: List[str]
    tags_body: List[str]
    template_id: Optional[str]
    template_version: Optional[str]
    file_stats: Dict[str, Any]


def _build_note_record(
    file_path: Path,
    vault_root: Path,
    parse_frontmatter,
    sanitize_tags,
    stem_to_key: Dict[str, str],
) -> NoteRecord:
    content = _read_text(file_path)
    metadata, body = parse_frontmatter(content)

    if isinstance(metadata, dict):
        metadata_safe = _json_safe(metadata)
        if isinstance(metadata_safe, dict):
            metadata = metadata_safe
        else:
            metadata = {}
    else:
        metadata = {}

    fm_tags = sanitize_tags(metadata.get("tags"))
    body_tags = sanitize_tags(_extract_body_hashtags(body))

    template_id = metadata.get("template_id")
    template_version = metadata.get("template_version")
    if template_id is not None:
        template_id = str(template_id)
    if template_version is not None:
        template_version = str(template_version)

    outgoing_raw = _extract_wikilinks(body)

    resolved: List[str] = []
    unresolved: List[str] = []
    for t in outgoing_raw:
        t_stem = Path(t).name
        target_key = stem_to_key.get(t_stem)
        if target_key is None:
            unresolved.append(t)
        else:
            resolved.append(target_key)

    st = file_path.stat()
    rel_path = str(file_path.relative_to(vault_root))

    return NoteRecord(
        key=rel_path,
        rel_path=rel_path,
        stem=file_path.stem,
        metadata=metadata,
        first_paragraph=_first_paragraph(body),
        outgoing_links_raw=outgoing_raw,
        outgoing_links_resolved=sorted(set(resolved)),
        unresolved_links=sorted(set(unresolved)),
        tags_frontmatter=fm_tags,
        tags_body=body_tags,
        template_id=template_id,
        template_version=template_version,
        file_stats={
            "size_bytes": st.st_size,
            "mtime_utc": _iso(st.st_mtime),
            "ctime_utc": _iso(st.st_ctime),
            "word_count": _word_count(body),
        },
    )


def _collect_md_files(vault_root: Path) -> List[Path]:
    return sorted([p for p in vault_root.rglob("*.md") if p.is_file()])


def generate_census(vault_root: Path, repo_root: Path) -> Dict[str, Any]:
    parse_frontmatter, sanitize_tags = _load_utils(repo_root)

    md_files = _collect_md_files(vault_root)

    stem_to_key: Dict[str, str] = {}
    for p in md_files:
        rel = str(p.relative_to(vault_root))
        stem_to_key.setdefault(p.stem, rel)

    notes: List[NoteRecord] = []
    for p in md_files:
        notes.append(
            _build_note_record(
                file_path=p,
                vault_root=vault_root,
                parse_frontmatter=parse_frontmatter,
                sanitize_tags=sanitize_tags,
                stem_to_key=stem_to_key,
            )
        )

    incoming_counts: Dict[str, int] = {n.key: 0 for n in notes}
    for n in notes:
        for target_key in n.outgoing_links_resolved:
            if target_key in incoming_counts:
                incoming_counts[target_key] += 1

    orphans: List[str] = []
    for n in notes:
        incoming = incoming_counts.get(n.key, 0)
        outgoing = len(n.outgoing_links_resolved)
        if incoming == 0 and outgoing == 0:
            orphans.append(n.key)

    notes_json: List[Dict[str, Any]] = []
    for n in notes:
        notes_json.append(
            {
                "key": n.key,
                "path": n.rel_path,
                "stem": n.stem,
                "metadata": n.metadata,
                "first_paragraph": n.first_paragraph,
                "outgoing_links": n.outgoing_links_resolved,
                "outgoing_links_raw": n.outgoing_links_raw,
                "unresolved_links": n.unresolved_links,
                "tags_frontmatter": n.tags_frontmatter,
                "tags_body": n.tags_body,
                "template_id": n.template_id,
                "template_version": n.template_version,
                "incoming_link_count": incoming_counts.get(n.key, 0),
                "file_stats": n.file_stats,
            }
        )

    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "vault_root": str(vault_root),
        "note_count": len(notes_json),
        "orphan_count": len(orphans),
        "orphans": sorted(orphans),
        "notes": notes_json,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vault_root", help="Path to vault root (directory)")
    parser.add_argument("output_json", help="Output JSON file")
    args = parser.parse_args(argv)

    vault_root = Path(args.vault_root).expanduser().resolve()
    output_path = Path(args.output_json).expanduser().resolve()

    if not vault_root.exists() or not vault_root.is_dir():
        raise SystemExit(f"vault_root must be an existing directory: {vault_root}")

    repo_root = _repo_root_from_cwd()

    census = generate_census(vault_root=vault_root, repo_root=repo_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(census, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
