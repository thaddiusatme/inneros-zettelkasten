"""
Orphan Remediation Coordinator for bidirectional link insertion.

ADR-002 Phase 8: Extracted from WorkflowManager (~242 LOC reduction).

Responsibilities:
- Detect and filter orphaned notes by scope (permanent/fleeting/all)
- Resolve target notes (explicit path, Home Note, MOC fallback)
- Insert bidirectional wiki-links between orphans and target notes
- Create backups before modifications
- Support dry-run and checklist modes
- Handle wiki-link detection and section appending
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from src.utils.io import safe_write


class OrphanRemediationCoordinator:
    """
    Coordinates orphan note remediation through bidirectional link insertion.
    
    Follows composition pattern established in ADR-002 phases 1-7.
    """
    
    def __init__(self, base_dir: str, analytics_coordinator):
        """
        Initialize coordinator with required dependencies.
        
        Args:
            base_dir: Base directory of the Zettelkasten vault
            analytics_coordinator: AnalyticsCoordinator for orphan detection
        """
        self.base_dir = base_dir
        self.analytics_coordinator = analytics_coordinator
    
    def remediate_orphaned_notes(
        self,
        mode: str = "link",
        scope: str = "permanent",
        limit: int = 10,
        target: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict:
        """
        Remediate orphaned notes by inserting bidirectional links.
        
        Args:
            mode: "link" (insert links) or "checklist" (output markdown checklist)
            scope: "permanent", "fleeting", or "all"
            limit: maximum number of orphaned notes to process
            target: explicit path to target MOC/note for inserting links
            dry_run: when True, do not modify files; preview only
        
        Returns:
            Dictionary with summary and actions performed or planned.
        """
        mode = (mode or "link").lower()
        scope = (scope or "permanent").lower()
        if mode not in {"link", "checklist"}:
            mode = "link"
        if scope not in {"permanent", "fleeting", "all"}:
            scope = "permanent"
        
        vault_root = self._vault_root()
        
        # Determine target note
        target_path: Optional[Path]
        if target:
            t = Path(target)
            target_path = t if t.is_absolute() else (vault_root / t)
        else:
            target_path = self._find_default_link_target()
        
        result: Dict = {
            "mode": mode,
            "scope": scope,
            "limit": int(limit),
            "dry_run": bool(dry_run),
            "target": str(target_path) if target_path else None,
            "actions": [],
            "summary": {
                "considered": 0,
                "processed": 0,
                "skipped": 0,
                "errors": 0,
            },
        }
        
        if not target_path or not target_path.exists():
            return {
                **result,
                "error": f"Target note not found: {target_path if target_path else 'None'}",
            }
        
        # Gather orphaned notes by scope and apply limit
        orphans = self.list_orphans_by_scope(scope)
        result["summary"]["considered"] = len(orphans)
        selected = orphans[: max(0, int(limit))] if limit else orphans
        
        if mode == "checklist":
            checklist = [
                f"- [ ] Add link [[{Path(o['path']).stem}]] to [[{target_path.stem}]] and reciprocal link"
                for o in selected
            ]
            md = [
                "# Orphan Remediation Checklist",
                f"Generated: {datetime.now().isoformat(timespec='seconds')}",
                f"Target: [[{target_path.stem}]]",
                "",
            ] + checklist
            result["checklist_markdown"] = "\n".join(md) + "\n"
            return result
        
        # link mode
        for o in selected:
            orphan_fp = Path(o["path"])
            try:
                changed = self.insert_bidirectional_links(orphan_fp, target_path, dry_run=dry_run)
                result["actions"].append(
                    {
                        "orphan": str(orphan_fp),
                        "target": str(target_path),
                        "modified_target": changed.get("modified_target", False),
                        "modified_orphan": changed.get("modified_orphan", False),
                        "backups": changed.get("backups", {}),
                    }
                )
                result["summary"]["processed"] += 1
            except Exception as e:
                result["actions"].append(
                    {"orphan": str(orphan_fp), "target": str(target_path), "error": str(e)}
                )
                result["summary"]["errors"] += 1
        
        result["summary"]["skipped"] = max(0, result["summary"]["considered"] - result["summary"]["processed"])
        return result
    
    def list_orphans_by_scope(self, scope: str) -> List[Dict]:
        """
        Return orphaned notes filtered by scope and sorted deterministically.
        
        Args:
            scope: "permanent", "fleeting", or "all"
        
        Returns:
            List of orphaned note dictionaries with path, title, last_modified
        """
        # Use comprehensive detector to be robust to vault layouts
        all_orphans = self.analytics_coordinator.detect_orphaned_notes_comprehensive()
        root = self._vault_root()
        
        def in_dir(p: str, name: str) -> bool:
            try:
                return (root / name) in Path(p).parents or Path(p).parent == (root / name)
            except Exception:
                return False
        
        if scope == "permanent":
            filtered = [o for o in all_orphans if in_dir(o["path"], "Permanent Notes")]
        elif scope == "fleeting":
            filtered = [o for o in all_orphans if in_dir(o["path"], "Fleeting Notes")]
        else:
            filtered = [
                o
                for o in all_orphans
                if in_dir(o["path"], "Permanent Notes") or in_dir(o["path"], "Fleeting Notes")
            ]
        
        # Sort: Permanent first, then by title
        def sort_key(o: Dict):
            dir_weight = 0 if in_dir(o["path"], "Permanent Notes") else 1
            return (dir_weight, o.get("title", ""))
        
        return sorted(filtered, key=sort_key)
    
    def resolve_target_note(self, target: Optional[str] = None) -> Optional[Path]:
        """
        Resolve target note for link insertion.
        
        Args:
            target: Optional explicit path to target note
        
        Returns:
            Path to target note, or None if not found
        """
        if target:
            t = Path(target)
            target_path = t if t.is_absolute() else (self._vault_root() / t)
            return target_path if target_path.exists() else None
        
        return self._find_default_link_target()
    
    def insert_bidirectional_links(
        self, orphan_path: Path, target_path: Path, dry_run: bool = True
    ) -> Dict:
        """
        Insert [[orphan]] in target and [[target]] in orphan, creating backups if not dry-run.
        
        Args:
            orphan_path: Path to orphan note
            target_path: Path to target note
            dry_run: If True, don't modify files
        
        Returns:
            Dict with modified flags and backup paths
        """
        orphan_key = orphan_path.stem
        target_key = target_path.stem
        
        result = {"modified_target": False, "modified_orphan": False, "backups": {}}
        
        # Update target file
        tgt_text = self._read_text(target_path)
        if not self.has_wikilink(tgt_text, orphan_key):
            new_tgt_text = self.append_to_section(tgt_text, f"[[{orphan_key}]]")
            if not dry_run:
                bk = self.backup_file(target_path)
                result["backups"]["target"] = str(bk) if bk else None
                self._write_text(target_path, new_tgt_text)
            result["modified_target"] = True
        
        # Update orphan file
        orphan_text = self._read_text(orphan_path)
        if not self.has_wikilink(orphan_text, target_key):
            new_orphan_text = self.append_to_section(orphan_text, f"[[{target_key}]]")
            if not dry_run:
                bk = self.backup_file(orphan_path)
                result["backups"]["orphan"] = str(bk) if bk else None
                self._write_text(orphan_path, new_orphan_text)
            result["modified_orphan"] = True
        
        return result
    
    def has_wikilink(self, text: str, key: str) -> bool:
        """
        Check if text contains wiki-link to key.
        
        Args:
            text: Content to search
            key: Note key to find (matches [[key]] or [[key|alias]])
        
        Returns:
            True if wiki-link found, False otherwise
        """
        try:
            pattern = rf"\[\[\s*{re.escape(key)}(?:\|[^\]]+)?\s*\]\]"
            return re.search(pattern, text) is not None
        except Exception:
            return False
    
    def append_to_section(
        self, text: str, bullet_line: str, section_title: str = "## Linked Notes"
    ) -> str:
        """
        Append a bullet to a dedicated section, creating it if missing.
        
        Args:
            text: Original note content
            bullet_line: Link text to append (e.g., "[[note-name]]")
            section_title: Section heading to append to
        
        Returns:
            Modified text with link appended
        """
        lines = text.splitlines()
        # Find section heading index
        heading_re = re.compile(rf"^#+\s+{re.escape(section_title.lstrip('#').strip())}$", re.IGNORECASE)
        idx = None
        for i, ln in enumerate(lines):
            if heading_re.match(ln.strip()):
                idx = i
                break
        bullet = f"- {bullet_line}"
        if idx is None:
            # Append new section at end
            new = []
            if lines and lines[-1].strip() != "":
                new = lines + ["", section_title, "", bullet, ""]
            else:
                new = lines + [section_title, "", bullet, ""]
            return "\n".join(new)
        else:
            # Insert after heading
            insert_at = idx + 1
            # skip leading blank after heading
            while insert_at < len(lines) and lines[insert_at].strip() == "":
                insert_at += 1
            new_lines = lines[:insert_at] + ["", bullet] + lines[insert_at:]
            return "\n".join(new_lines)
    
    def backup_file(self, path: Path) -> Optional[Path]:
        """
        Create timestamped backup of file.
        
        Args:
            path: File to backup
        
        Returns:
            Path to backup file, or None if backup failed
        """
        try:
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = path.parent / f"{path.name}.bak.{ts}"
            shutil.copy2(path, backup)
            return backup
        except Exception:
            return None
    
    # Private helper methods
    
    def _vault_root(self) -> Path:
        """Resolve the root folder that actually contains the note collections."""
        base = Path(self.base_dir)
        knowledge = base / "knowledge"
        return knowledge if knowledge.exists() else base
    
    def _find_default_link_target(self) -> Optional[Path]:
        """Pick a sensible default target note (Home Note or an MOC)."""
        root = self._vault_root()
        # 1) Home Note.md
        home = root / "Home Note.md"
        if home.exists():
            return home
        # 2) Zettelkasten MOC in Permanent Notes
        z_moc = root / "Permanent Notes" / "Zettelkasten MOC.md"
        if z_moc.exists():
            return z_moc
        # 3) any MOC file under vault
        moc_candidates = list(root.rglob("*MOC*.md"))
        if moc_candidates:
            moc_candidates.sort()
            return moc_candidates[0]
        return None
    
    def _read_text(self, path: Path) -> str:
        """Read text from file, returning empty string if not found."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _write_text(self, path: Path, text: str) -> None:
        """Write text to file using atomic write."""
        safe_write(path, text)
