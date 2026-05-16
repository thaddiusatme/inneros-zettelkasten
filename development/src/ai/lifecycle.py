"""
lifecycle — note state transitions and import management for Zettelkasten.

Consolidated self-contained module (issue #120). Inlines:
  note_lifecycle_manager.py, promotion_engine.py,
  fleeting_note_coordinator.py, fleeting_analysis_coordinator.py,
  review_triage_coordinator.py, import_manager.py, import_schema.py

Manages the full note lifecycle: fleeting → permanent → archive transitions,
promotion decisions, import ingestion, and review triage.

Import boundary: may import from llm_client and connections_discovery.
Does NOT import from enrichment, connections_insertion, or batch.
"""

# ---------------------------------------------------------------------------
# import_schema (no internal deps — must come first)
# ---------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Callable
import re
import json
import csv
import time
import logging
from pathlib import Path

from src.ai.llm_client import OllamaClient


@dataclass
class ImportItem:
    title: str
    url: str
    source: str
    saved_at: datetime
    type: str = "literature"
    topics: List[str] = None

    def key(self) -> str:
        """Unique key based on (url, saved_at ISO date-time)."""
        return f"{self.url}::{self.saved_at.isoformat()}"


_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")


def _parse_saved_at(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        m = _ISO_DATE_RE.match(value)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception:
                pass
    return datetime.now()


def _coerce_topics(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    s = str(value)
    if "," in s:
        return [t.strip() for t in s.split(",") if t.strip()]
    return [s.strip()] if s.strip() else []


def validate_item(data: Dict[str, Any]) -> ImportItem:
    """Validate incoming row dict and coerce to ImportItem.

    Required: title, url, source, saved_at (coerced), topics (coerced) optional.
    """
    title = (data.get("title") or "").strip()
    url = (data.get("url") or "").strip()
    source = (data.get("source") or "").strip()
    saved_at_raw = (data.get("saved_at") or data.get("date") or "").strip()
    if not title or not url:
        raise ValueError("Missing required fields: title and url")
    saved_at = _parse_saved_at(saved_at_raw)
    topics = _coerce_topics(data.get("topics"))
    return ImportItem(
        title=title,
        url=url,
        source=source or "unknown",
        saved_at=saved_at,
        type="literature",
        topics=topics,
    )


# ---------------------------------------------------------------------------
# import_manager
# ---------------------------------------------------------------------------

_FRONTMATTER_BOUNDARY = "---"
_YAML_KEY_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def _read_yaml_frontmatter(md_path: Path) -> Dict[str, Any]:
    """Very small YAML-like frontmatter reader for url/saved_at."""
    content = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()
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


class CSVImportAdapter:
    """Load ImportItem rows from a CSV file."""

    @staticmethod
    def load(path: Path) -> List[ImportItem]:
        items: List[ImportItem] = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                data = {
                    k.strip(): (v.strip() if isinstance(v, str) else v)
                    for k, v in raw.items()
                }
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
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rows: List[Dict[str, Any]]
        if isinstance(data, list):
            rows = [dict(x) for x in data]
        elif isinstance(data, dict) and isinstance(data.get("items"), list):
            rows = [dict(x) for x in data["items"]]
        else:
            raise ValueError(
                "Unsupported JSON structure: expected a list or an object with 'items'."
            )
        items: List[ImportItem] = []
        for raw in rows:
            try:
                items.append(validate_item(raw))
            except Exception:
                continue
        return items


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
        topics_block = (
            "[]"
            if not item.topics
            else f"[{', '.join([repr(t) for t in item.topics])}]"
        )
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
                    return p.read_text(encoding="utf-8")
                except Exception:
                    pass
        # Fallback scaffold
        return "## Claims\n\n" "- \n\n" "## Quotes\n\n" "> \n\n" "## Links\n\n" "- \n"

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
                    existing_dt = datetime.fromisoformat(
                        fm["saved_at"].replace("Z", "+00:00")
                    )
                    if existing_dt.replace(microsecond=0) == item.saved_at.replace(
                        microsecond=0
                    ):
                        return True
                except Exception:
                    pass
        return False

    def write_items(
        self, items: List[ImportItem], dest_dir: Path | None = None, force: bool = False
    ) -> Tuple[int, int, List[Path]]:
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
            content = self._yaml_frontmatter(item) + self._body(
                Path("Templates/literature.md")
            )
            target.write_text(content, encoding="utf-8")
            paths.append(target)
            written += 1
        return written, skipped, paths


# ---------------------------------------------------------------------------
# note_lifecycle_manager
# ---------------------------------------------------------------------------

from src.utils.frontmatter import parse_frontmatter, build_frontmatter
from src.utils.io import safe_write


@dataclass
class StatusTransition:
    """Represents a status transition event."""

    from_status: str
    to_status: str
    timestamp: str
    reason: str
    metadata: Dict


class NoteLifecycleManager:
    """
    Manages note lifecycle status transitions.

    Responsibilities:
    - Validate status transitions
    - Update note frontmatter with new status
    - Track status history
    - Provide status query methods

    Valid Status Flow:
        inbox → promoted → published → archived
        archived → inbox (resurrection)

    Forbidden Transitions:
        - Backwards (promoted → inbox, published → promoted)
        - Skipping steps (inbox → published without promoted)
    """

    VALID_STATUSES = ["inbox", "promoted", "published", "archived"]

    VALID_TRANSITIONS = {
        "inbox": ["promoted", "archived"],
        "promoted": ["published", "archived"],
        "published": ["archived"],
        "archived": ["inbox"],  # Allow resurrection
    }

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize lifecycle manager.

        Args:
            base_dir: Base directory containing note directories (Inbox/, Permanent Notes/, etc.)
                     If None, directories are not initialized (for status-only operations).
        """
        self.base_dir = base_dir

        # Initialize directory paths if base_dir provided
        if base_dir:
            self.inbox_dir = base_dir / "Inbox"
            self.permanent_dir = base_dir / "Permanent Notes"
            self.literature_dir = base_dir / "Literature Notes"
            self.fleeting_dir = base_dir / "Fleeting Notes"
        else:
            self.inbox_dir = None
            self.permanent_dir = None
            self.literature_dir = None
            self.fleeting_dir = None

    def update_status(
        self,
        note_path: Path,
        new_status: str,
        reason: str = "",
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Update note status with validation and history tracking.

        Args:
            note_path: Path to the note file
            new_status: Target status (inbox/promoted/published/archived)
            reason: Human-readable reason for transition
            metadata: Additional metadata (quality_score, ai_processed, etc.)

        Returns:
            Result dict with status_updated, timestamp, validation_passed
        """
        # Check if file exists
        if not note_path.exists():
            return {
                "status_updated": False,
                "validation_passed": False,
                "error": "Note file not found",
            }

        # Validate new status is valid
        if new_status not in self.VALID_STATUSES:
            return {
                "status_updated": False,
                "validation_passed": False,
                "error": f"Invalid status '{new_status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            }

        try:
            # Read note content
            with open(note_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter
            frontmatter, body = parse_frontmatter(content)

            # Get current status
            current_status = frontmatter.get("status", "inbox")

            # Validate transition (only if status is changing)
            if current_status != new_status:
                is_valid, error_message = self.validate_transition(
                    current_status, new_status
                )
                if not is_valid:
                    return {
                        "status_updated": False,
                        "validation_passed": False,
                        "error": error_message,
                    }

            # Update status
            frontmatter["status"] = new_status

            # Add appropriate timestamp (idempotent - only add if not already present)
            timestamp = self._add_timestamp_field(frontmatter, new_status)

            # Add any additional metadata
            if metadata:
                for key, value in metadata.items():
                    if key not in frontmatter:  # Don't overwrite existing fields
                        frontmatter[key] = value

            # Rebuild content
            updated_content = build_frontmatter(frontmatter, body)

            # Write back to file
            safe_write(note_path, updated_content)

            return {
                "status_updated": new_status,
                "validation_passed": True,
                "timestamp": timestamp,
                "previous_status": current_status,
            }

        except Exception as e:
            return {
                "status_updated": False,
                "validation_passed": False,
                "error": f"Failed to update status: {str(e)}",
            }

    def validate_transition(
        self, current_status: str, new_status: str
    ) -> Tuple[bool, str]:
        """
        Validate if status transition is allowed.

        Args:
            current_status: Current note status
            new_status: Desired new status

        Returns:
            (is_valid, error_message)
        """
        # If statuses are the same, it's valid (idempotent)
        if current_status == new_status:
            return (True, "")

        # Check if current status has valid transitions defined
        if current_status not in self.VALID_TRANSITIONS:
            return (
                False,
                f"Invalid current status '{current_status}'. Cannot determine valid transitions.",
            )

        # Check if transition is in valid transitions list
        valid_next_statuses = self.VALID_TRANSITIONS[current_status]
        if new_status not in valid_next_statuses:
            return (
                False,
                f"Transition from '{current_status}' to '{new_status}' is not allowed. "
                f"Valid transitions from '{current_status}': {', '.join(valid_next_statuses)}",
            )

        return (True, "")

    def _add_timestamp_field(self, frontmatter: Dict, status: str) -> str:
        """
        Add appropriate timestamp field for status.
        Idempotent - won't duplicate if field already exists.

        Args:
            frontmatter: Frontmatter dictionary to modify
            status: Status being set

        Returns:
            Timestamp string that was added/preserved
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Map status to timestamp field name
        timestamp_fields = {
            "promoted": "processed_date",
            "published": "promoted_date",
            "archived": "archived_date",
        }

        # Add timestamp if this status has an associated field
        if status in timestamp_fields:
            field_name = timestamp_fields[status]
            # Only add if not already present (idempotence)
            if field_name not in frontmatter:
                frontmatter[field_name] = timestamp
            else:
                # Return existing timestamp
                timestamp = frontmatter[field_name]

        return timestamp

    def promote_note(self, note_path: Path) -> Dict:
        """
        Promote a note from Inbox to its type-specific directory.

        Reads the note's 'type' field and moves it to the appropriate directory:
        - type: permanent → Permanent Notes/
        - type: literature → Literature Notes/
        - type: fleeting → Fleeting Notes/

        Also updates status to 'promoted' and adds processed_date timestamp.

        Args:
            note_path: Path to the note file in Inbox/

        Returns:
            Result dict with promoted, destination_dir, error
        """
        import shutil

        # Validate base_dir was provided
        if not self.base_dir:
            return {
                "promoted": False,
                "error": "NoteLifecycleManager requires base_dir for promote_note()",
            }

        # Check if file exists
        if not note_path.exists():
            return {"promoted": False, "error": "Note file not found"}

        try:
            # Read note content
            with open(note_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter
            frontmatter, body = parse_frontmatter(content)

            # Get note type
            note_type = frontmatter.get("type", "fleeting")

            # Map type to destination directory
            type_to_dir = {
                "permanent": self.permanent_dir,
                "literature": self.literature_dir,
                "fleeting": self.fleeting_dir,
            }

            destination_dir = type_to_dir.get(note_type)
            if not destination_dir:
                return {"promoted": False, "error": f"Unknown note type: {note_type}"}

            # Update status to promoted (adds processed_date automatically)
            status_result = self.update_status(
                note_path,
                new_status="promoted",
                reason="Auto-promotion based on note type",
            )

            if not status_result.get("validation_passed"):
                return {
                    "promoted": False,
                    "error": status_result.get("error", "Failed to update status"),
                }

            # Also add promoted_date for explicit promotion tracking
            try:
                with open(note_path, "r", encoding="utf-8") as f:
                    content = f.read()
                frontmatter, body = parse_frontmatter(content)
                if "promoted_date" not in frontmatter:
                    frontmatter["promoted_date"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    updated_content = build_frontmatter(frontmatter, body)
                    with open(note_path, "w", encoding="utf-8") as f:
                        f.write(updated_content)
            except Exception as e:
                # Continue even if timestamp addition fails
                pass

            # Move file to destination directory
            destination_path = destination_dir / note_path.name
            shutil.move(str(note_path), str(destination_path))

            return {
                "promoted": True,
                "destination_dir": str(destination_dir),
                "destination_path": str(destination_path),
                "note_type": note_type,
            }

        except Exception as e:
            return {"promoted": False, "error": f"Failed to promote note: {str(e)}"}


# ---------------------------------------------------------------------------
# promotion_engine
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


class PromotionEngine:
    """
    Handles note promotion between directories based on quality thresholds.

    Key Responsibilities:
    - Single note promotion
    - Batch promotion workflows
    - Auto-promotion based on quality scores
    - Validation of promotion eligibility
    - Integration with DirectoryOrganizer for safe operations
    """

    # Constants for auto-promotion configuration
    DEFAULT_QUALITY_THRESHOLD = 0.7
    VALID_NOTE_TYPES = ["fleeting", "literature", "permanent"]
    AUTO_PROMOTION_STATUS = (
        "promoted"  # Notes must have this status to be auto-promoted
    )
    AUTO_PROMOTION_TARGET_STATUS = "published"  # Final status after auto-promotion

    def __init__(
        self,
        base_dir: Path,
        lifecycle_manager: NoteLifecycleManager,
        config: Optional[Dict] = None,
    ):
        """
        Initialize PromotionEngine.

        Args:
            base_dir: Base directory for the knowledge vault
            lifecycle_manager: NoteLifecycleManager instance for lifecycle operations
            config: Optional configuration dictionary
        """
        self.base_dir = Path(base_dir)
        self.lifecycle_manager = lifecycle_manager
        self.config = config or {}

        # Set up directory paths
        self.inbox_dir = self.base_dir / "Inbox"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.literature_dir = self.base_dir / "Literature Notes"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"

        # Ensure target directories exist
        self.permanent_dir.mkdir(parents=True, exist_ok=True)
        self.literature_dir.mkdir(parents=True, exist_ok=True)
        self.fleeting_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"PromotionEngine initialized with base_dir: {base_dir}, "
            f"quality_threshold: {self.DEFAULT_QUALITY_THRESHOLD}"
        )

    def promote_note(self, note_path: str, target_type: str = "permanent") -> Dict:
        """
        Promote a note from inbox/fleeting to appropriate directory.

        This method now delegates to NoteLifecycleManager for unified promotion logic.
        If target_type is specified, it updates the note's type field before promotion.

        Args:
            note_path: Path to the note to promote
            target_type: Target note type ("permanent", "literature", or "fleeting")
                        If provided, overrides the note's existing type field.

        Returns:
            Promotion results dictionary with keys:
            - success: bool
            - source: str (original path)
            - target: str (new path)
            - type: str (note type)
            - error: str (if failed)
        """
        source_file = Path(note_path)

        if not source_file.exists():
            return {"error": "Source note not found"}

        # Validate target type
        if target_type not in ["permanent", "literature", "fleeting"]:
            return {"error": f"Invalid target type: {target_type}"}

        try:
            # If target_type specified, update note's type field before promotion
            if target_type:
                with open(source_file, "r", encoding="utf-8") as f:
                    content = f.read()

                frontmatter, body = parse_frontmatter(content)

                # Update type field to match target
                frontmatter["type"] = target_type

                # Write updated type back to note
                updated_content = build_frontmatter(frontmatter, body)
                safe_write(source_file, updated_content)

            # Delegate to NoteLifecycleManager for unified promotion logic
            result = self.lifecycle_manager.promote_note(source_file)

            if result.get("promoted"):
                # Check if promoted note has AI summary
                has_summary = False
                try:
                    promoted_path = Path(result["destination_path"])
                    if promoted_path.exists():
                        promoted_content = promoted_path.read_text()
                        has_summary = "ai_summary:" in promoted_content
                except Exception:
                    pass  # Default to False if can't read

                # Transform result to match expected format
                return {
                    "success": True,
                    "source": str(source_file),
                    "target": result["destination_path"],
                    "type": result["note_type"],
                    "has_summary": has_summary,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Promotion failed"),
                }

        except Exception as e:
            return {"success": False, "error": f"Failed to promote note: {e}"}

    def _validate_note_for_promotion(
        self, note_path: Path, frontmatter: Dict, quality_threshold: float
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate if a note is eligible for auto-promotion.

        Args:
            note_path: Path to the note
            frontmatter: Parsed frontmatter metadata
            quality_threshold: Minimum quality score required

        Returns:
            Tuple of (is_valid, note_type, error_message)
        """
        # Check quality score
        quality_score = frontmatter.get("quality_score", 0.0)
        if quality_score < quality_threshold:
            return (
                False,
                None,
                f"Quality score {quality_score:.2f} below threshold {quality_threshold}",
            )

        # Check for required type field
        note_type = frontmatter.get("type")
        if not note_type:
            return False, None, "Missing 'type' field in frontmatter"

        # Validate type is one of the expected values
        valid_types = ["permanent", "literature", "fleeting"]
        if note_type not in valid_types:
            return (
                False,
                None,
                f"Invalid type '{note_type}', must be one of: {valid_types}",
            )

        return True, note_type, None

    def _execute_note_promotion(
        self, note_path: Path, note_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute the actual file promotion operation.

        Args:
            note_path: Path to the note to promote
            note_type: Target note type

        Returns:
            Tuple of (success, error_message)
        """
        try:
            result = self.promote_note(str(note_path), target_type=note_type)

            if "error" in result:
                return False, result["error"]

            # Auto-promotion requires additional status update from 'promoted' → 'published'
            if result.get("success") and result.get("target"):
                promoted_path = Path(result["target"])
                try:
                    status_result = self.lifecycle_manager.update_status(
                        promoted_path,
                        new_status=self.AUTO_PROMOTION_TARGET_STATUS,
                        reason="Auto-promotion completed successfully",
                    )
                    if not status_result.get("validation_passed"):
                        logger.warning(
                            f"Status update to '{self.AUTO_PROMOTION_TARGET_STATUS}' failed for {promoted_path.name}: "
                            f"{status_result.get('error', 'Unknown error')}"
                        )
                except Exception as e:
                    logger.warning(
                        f"Could not update status to '{self.AUTO_PROMOTION_TARGET_STATUS}' for {promoted_path.name}: {e}"
                    )

            return True, None

        except Exception as e:
            error_msg = f"Promotion execution failed: {e}"
            logger.exception(error_msg)
            return False, error_msg

    def _get_target_directory(self, note_type: str) -> Path:
        """
        Get target directory path for a given note type.

        Args:
            note_type: Note type ('fleeting', 'literature', or 'permanent')

        Returns:
            Path to target directory

        Raises:
            ValueError: If note_type is invalid
        """
        if note_type not in self.VALID_NOTE_TYPES:
            raise ValueError(
                f"Invalid note type: '{note_type}'. "
                f"Must be one of: {', '.join(self.VALID_NOTE_TYPES)}"
            )

        type_to_dir = {
            "fleeting": self.fleeting_dir,
            "literature": self.literature_dir,
            "permanent": self.permanent_dir,
        }

        return type_to_dir[note_type]

    def auto_promote_ready_notes(
        self, dry_run: bool = False, quality_threshold: float = 0.7
    ) -> Dict:
        """
        Automatically promote notes that meet quality threshold.

        Scans Inbox/ for notes with quality_score >= threshold,
        then promotes them to appropriate directories based on type field.

        Args:
            dry_run: If True, preview promotions without making changes
            quality_threshold: Minimum quality score required (default: 0.7)

        Returns:
            Dict with promotion results including counts and details
        """
        results = {
            "total_candidates": 0,
            "promoted_count": 0,
            "skipped_count": 0,
            "error_count": 0,
            "promoted": [],
            "skipped_notes": {},  # Dict with filename as key, reason as value
            "errors": {},  # Dict with filename as key, error message as value
            "by_type": {
                "fleeting": {"promoted": 0, "skipped": 0},
                "literature": {"promoted": 0, "skipped": 0},
                "permanent": {"promoted": 0, "skipped": 0},
            },
            "dry_run": dry_run,
        }

        if dry_run:
            results["would_promote_count"] = 0
            results["preview"] = []
            logger.info(
                f"Auto-promotion running in DRY-RUN mode (no changes will be made) "
                f"with quality_threshold={quality_threshold}"
            )

        # Scan inbox for candidate notes (including subdirectories)
        if not self.inbox_dir.exists():
            logger.warning(
                f"Inbox directory does not exist: {self.inbox_dir}. "
                f"Auto-promotion cannot proceed."
            )
            return results

        inbox_files = list(self.inbox_dir.rglob("*.md"))
        logger.info(
            f"Auto-promotion scan starting: {len(inbox_files)} notes in Inbox/ "
            f"(quality_threshold={quality_threshold}, dry_run={dry_run})"
        )

        for note_path in inbox_files:
            try:
                # Read note metadata
                content = note_path.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)

                # Skip notes without quality scores
                quality_score = frontmatter.get("quality_score")
                if quality_score is None:
                    logger.debug(
                        f"Skipping {note_path.name}: No quality_score field in frontmatter"
                    )
                    continue

                # Process notes with status='inbox' or 'promoted'
                status = frontmatter.get("status", "inbox")
                valid_statuses = ["inbox", self.AUTO_PROMOTION_STATUS]
                if status not in valid_statuses:
                    logger.debug(
                        f"Skipping {note_path.name}: Status '{status}' not in {valid_statuses}"
                    )
                    continue

                results["total_candidates"] += 1
                logger.info(
                    f"Evaluating candidate {results['total_candidates']}: {note_path.name} "
                    f"(quality: {quality_score:.2f}, threshold: {quality_threshold})"
                )

                # Validate note eligibility
                is_valid, note_type, error_msg = self._validate_note_for_promotion(
                    note_path, frontmatter, quality_threshold
                )

                if not is_valid:
                    results["skipped_count"] += 1
                    results["skipped_notes"][note_path.name] = (
                        error_msg or "Validation failed"
                    )

                    if note_type and note_type in results["by_type"]:
                        results["by_type"][note_type]["skipped"] += 1

                    if error_msg and "type" in error_msg.lower():
                        results["error_count"] += 1
                        results["errors"][note_path.name] = error_msg
                        logger.error(
                            f"Validation error for {note_path.name}: {error_msg}"
                        )
                    else:
                        logger.info(
                            f"Skipped {note_path.name}: {error_msg} (quality: {quality_score:.2f})"
                        )
                    continue

                assert (
                    note_type is not None
                ), "note_type should not be None after successful validation"

                # Dry-run mode: preview only
                if dry_run:
                    quality_score = frontmatter.get("quality_score", 0.0)
                    results["would_promote_count"] += 1
                    results["preview"].append(
                        {
                            "note": note_path.name,
                            "type": note_type,
                            "quality": quality_score,
                            "target": f"{note_type.title()} Notes/",
                        }
                    )
                    logger.info(
                        f"Would promote: {note_path.name} → {note_type.title()} Notes/"
                    )
                    continue

                # Execute promotion
                success, error_msg = self._execute_note_promotion(note_path, note_type)

                if success:
                    results["promoted_count"] += 1
                    results["by_type"][note_type]["promoted"] += 1
                    quality = frontmatter.get("quality_score", 0.0)
                    results["promoted"].append(
                        {
                            "title": note_path.name,
                            "type": note_type,
                            "quality": quality,
                            "target": f"{note_type.title()} Notes/",
                        }
                    )
                    logger.info(
                        f"Auto-promoted [{results['promoted_count']}/{results['total_candidates']}]: "
                        f"{note_path.name} → {note_type.title()} Notes/ "
                        f"(quality: {quality:.2f}, status: {self.AUTO_PROMOTION_STATUS}→{self.AUTO_PROMOTION_TARGET_STATUS})"
                    )
                else:
                    results["error_count"] += 1
                    results["errors"][note_path.name] = error_msg
                    logger.error(
                        f"Promotion failed for {note_path.name}: {error_msg} "
                        f"(candidate {results['total_candidates']}, type: {note_type})"
                    )

            except Exception as e:
                results["error_count"] += 1
                results["errors"][note_path.name] = str(e)
                logger.exception(
                    f"Exception processing {note_path.name} during auto-promotion: {e}"
                )

        # Add summary section
        results["summary"] = {
            "total_candidates": results["total_candidates"],
            "promoted_count": results["promoted_count"],
            "skipped_count": results["skipped_count"],
            "error_count": results["error_count"],
        }

        by_type_summary = ", ".join(
            f"{type_name}: {counts['promoted']}"
            for type_name, counts in results["by_type"].items()
            if counts["promoted"] > 0
        )
        logger.info(
            f"Auto-promotion complete: {results['promoted_count']}/{results['total_candidates']} promoted "
            f"({by_type_summary}), {results['skipped_count']} skipped, {results['error_count']} errors"
        )

        return results

    def promote_fleeting_note(
        self,
        note_path: str,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
    ) -> Dict:
        """
        Promote a single fleeting note to permanent or literature status.

        Args:
            note_path: Path to the fleeting note to promote
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes

        Returns:
            Dict: Promotion results with details of operations performed
        """
        start_time = time.time()

        try:
            # Import DirectoryOrganizer
            from ..utils.directory_organizer import DirectoryOrganizer

            # Resolve note path
            if not note_path.startswith("/"):
                if note_path.startswith("knowledge/"):
                    relative_path = note_path.replace("knowledge/", "", 1)
                    note_path_obj = self.base_dir / relative_path
                else:
                    note_path_obj = self.base_dir / note_path
            else:
                note_path_obj = Path(note_path)

            if not note_path_obj.exists():
                raise ValueError(f"Note not found: {note_path}")

            # Validate note is fleeting type
            content = note_path_obj.read_text(encoding="utf-8")
            metadata, body = parse_frontmatter(content)

            if metadata.get("type") != "fleeting":
                raise ValueError(
                    f"Note is not a fleeting note (type: {metadata.get('type')})"
                )

            # Get quality score
            quality_score = metadata.get("quality_score", 0.5)

            # Auto-detect target type if not specified
            if target_type is None:
                if metadata.get("source") or metadata.get("url"):
                    target_type = "literature"
                else:
                    target_type = "permanent"

            # Determine target directory
            if target_type == "literature":
                target_dir = self.literature_dir
            else:
                target_dir = self.permanent_dir

            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            # Create target path
            target_path = target_dir / note_path_obj.name

            promotion_result = {
                "promoted_notes": [
                    {
                        "note_path": str(note_path_obj),
                        "target_type": target_type,
                        "target_path": str(target_path),
                        "quality_score": quality_score,
                        "preview_mode": preview_mode,
                    }
                ],
                "batch_mode": False,
                "preview_mode": preview_mode,
                "target_directory": str(target_dir),
                "promotion_time": datetime.now().isoformat(),
                "processing_time": 0,
                "backup_created": False,
            }

            if preview_mode:
                promotion_result["processing_time"] = time.time() - start_time
                return promotion_result

            # Create backup
            organizer = DirectoryOrganizer(self.base_dir.parent)
            backup_path = organizer.create_backup()
            promotion_result["backup_created"] = True
            promotion_result["backup_path"] = str(backup_path)

            # Update metadata for promotion
            updated_metadata = metadata.copy()
            updated_metadata["type"] = target_type
            updated_metadata["promoted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            updated_metadata["promotion_quality_score"] = quality_score

            # Reconstruct file content
            updated_content = "---\n"
            for key, value in updated_metadata.items():
                if isinstance(value, list):
                    updated_content += f"{key}: {value}\n"
                elif isinstance(value, str) and " " in value:
                    updated_content += f'{key}: "{value}"\n'
                else:
                    updated_content += f"{key}: {value}\n"
            updated_content += f"---\n\n{body}"

            # Write to target location
            target_path.write_text(updated_content, encoding="utf-8")

            # Remove original file
            note_path_obj.unlink()

            promotion_result["processing_time"] = time.time() - start_time
            return promotion_result

        except Exception as e:
            return {
                "promoted_notes": [
                    {
                        "note_path": note_path,
                        "error": str(e),
                        "quality_score": 0,
                        "preview_mode": preview_mode,
                    }
                ],
                "batch_mode": False,
                "preview_mode": preview_mode,
                "target_directory": "unknown",
                "promotion_time": datetime.now().isoformat(),
                "processing_time": time.time() - start_time,
                "backup_created": False,
            }

    def promote_fleeting_notes_batch(
        self,
        quality_threshold: float = 0.7,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
    ) -> Dict:
        """
        Promote multiple fleeting notes based on quality threshold.

        Args:
            quality_threshold: Minimum quality score for promotion
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes

        Returns:
            Dict: Batch promotion results
        """
        start_time = time.time()

        try:
            # Scan fleeting notes directory for high-quality notes
            fleeting_notes = []
            if self.fleeting_dir.exists():
                for note_path in self.fleeting_dir.glob("*.md"):
                    try:
                        content = note_path.read_text(encoding="utf-8")
                        metadata, _ = parse_frontmatter(content)
                        quality = metadata.get("quality_score", 0.0)

                        if quality >= quality_threshold:
                            fleeting_notes.append(
                                {
                                    "note_path": str(note_path),
                                    "quality_score": quality,
                                    "action": "Promote to Permanent",
                                }
                            )
                    except Exception:
                        continue

            if not fleeting_notes:
                return {
                    "promoted_notes": [],
                    "batch_mode": True,
                    "preview_mode": preview_mode,
                    "quality_threshold": quality_threshold,
                    "processing_time": time.time() - start_time,
                    "backup_created": False,
                }

            # Create single backup for batch operation
            backup_created = False
            backup_path = None

            if not preview_mode:
                try:
                    from ..utils.directory_organizer import DirectoryOrganizer

                    organizer = DirectoryOrganizer(self.base_dir.parent)
                    backup_path = organizer.create_backup()
                    backup_created = True
                except Exception as e:
                    logger.warning(f"Could not create backup: {e}")

            # Process each eligible note
            promoted_notes = []
            for note_rec in fleeting_notes:
                try:
                    # Determine target type for this note
                    note_target = target_type
                    if note_target is None:
                        try:
                            note_path_obj = Path(note_rec["note_path"])
                            content = note_path_obj.read_text(encoding="utf-8")
                            metadata, _ = parse_frontmatter(content)
                            if metadata.get("source") or metadata.get("url"):
                                note_target = "literature"
                            else:
                                note_target = "permanent"
                        except Exception:
                            note_target = "permanent"

                    if not preview_mode:
                        result = self.promote_note(
                            note_rec["note_path"], target_type=note_target
                        )
                        if "success" in result and result["success"]:
                            promoted_notes.append(
                                {
                                    "note_path": note_rec["note_path"],
                                    "target_type": note_target,
                                    "target_path": result.get("target", ""),
                                    "quality_score": note_rec["quality_score"],
                                    "batch_promotion": True,
                                    "preview_mode": False,
                                }
                            )
                        else:
                            promoted_notes.append(
                                {
                                    "note_path": note_rec["note_path"],
                                    "error": result.get("error", "Unknown error"),
                                    "quality_score": note_rec["quality_score"],
                                    "batch_promotion": True,
                                    "preview_mode": False,
                                }
                            )
                    else:
                        promoted_notes.append(
                            {
                                "note_path": note_rec["note_path"],
                                "target_type": note_target,
                                "quality_score": note_rec["quality_score"],
                                "batch_promotion": True,
                                "preview_mode": True,
                            }
                        )

                except Exception as e:
                    promoted_notes.append(
                        {
                            "note_path": note_rec["note_path"],
                            "error": str(e),
                            "quality_score": note_rec["quality_score"],
                            "batch_promotion": True,
                            "preview_mode": preview_mode,
                        }
                    )

            return {
                "promoted_notes": promoted_notes,
                "batch_mode": True,
                "preview_mode": preview_mode,
                "quality_threshold": quality_threshold,
                "processing_time": time.time() - start_time,
                "backup_created": backup_created,
                "backup_path": str(backup_path) if backup_path else None,
            }

        except Exception as e:
            return {
                "promoted_notes": [],
                "batch_mode": True,
                "preview_mode": preview_mode,
                "quality_threshold": quality_threshold,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "backup_created": False,
            }


# ---------------------------------------------------------------------------
# fleeting_analysis_coordinator
# ---------------------------------------------------------------------------

from src.utils.frontmatter import parse_frontmatter as _parse_frontmatter
from dataclasses import dataclass as _dc, field


@_dc
class FleetingAnalysis:
    """Data structure for fleeting note analysis results."""

    total_count: int = 0
    age_distribution: Dict[str, int] = field(
        default_factory=lambda: {
            "new": 0,  # 0-7 days
            "recent": 0,  # 8-30 days
            "stale": 0,  # 31-90 days
            "old": 0,  # 90+ days
        }
    )
    oldest_note: Optional[Dict[str, any]] = None
    newest_note: Optional[Dict[str, any]] = None
    notes_by_age: List[Dict[str, any]] = field(default_factory=list)


class FleetingAnalysisCoordinator:
    """
    Coordinates fleeting note analysis and health reporting.

    Extracted from WorkflowManager (ADR-002 Phase 9) to reduce god class complexity.
    Handles age categorization, statistics aggregation, and health report generation.
    """

    def __init__(self, fleeting_dir: Path):
        """
        Initialize FleetingAnalysisCoordinator.

        Args:
            fleeting_dir: Path to fleeting notes directory

        Raises:
            TypeError: If fleeting_dir is None
            ValueError: If fleeting_dir is invalid
        """
        if fleeting_dir is None:
            raise TypeError("fleeting_dir cannot be None")

        if not isinstance(fleeting_dir, Path):
            fleeting_dir = Path(fleeting_dir)

        self.fleeting_dir = fleeting_dir

    def analyze_fleeting_notes(self) -> FleetingAnalysis:
        """
        Analyze fleeting notes collection for age distribution and health metrics.

        Returns:
            FleetingAnalysis: Data structure with age analysis results
        """
        analysis = FleetingAnalysis()
        notes_data = []

        # Scan fleeting notes directory
        if not self.fleeting_dir.exists():
            return analysis

        current_date = datetime.now()

        for note_path in self.fleeting_dir.glob("*.md"):
            try:
                # Get note age from metadata or file stats
                content = note_path.read_text(encoding="utf-8")
                frontmatter, _ = _parse_frontmatter(content)

                # Try to get created date from frontmatter
                created_str = frontmatter.get("created", "")
                if created_str and not any(
                    placeholder in created_str for placeholder in ["{{", "<%", "tp."]
                ):
                    # Parse the date
                    try:
                        created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            created_date = datetime.strptime(created_str, "%Y-%m-%d")
                        except ValueError:
                            # Fall back to file modification time
                            created_date = datetime.fromtimestamp(
                                note_path.stat().st_mtime
                            )
                else:
                    # Use file modification time as fallback
                    created_date = datetime.fromtimestamp(note_path.stat().st_mtime)

                # Calculate age in days
                age_delta = current_date - created_date
                days_old = age_delta.days

                # Store note data
                note_info = {
                    "name": note_path.name,
                    "path": str(note_path),
                    "days_old": days_old,
                    "created": created_date,
                }
                notes_data.append(note_info)

                # Categorize by age
                if days_old <= 7:
                    analysis.age_distribution["new"] += 1
                elif days_old <= 30:
                    analysis.age_distribution["recent"] += 1
                elif days_old <= 90:
                    analysis.age_distribution["stale"] += 1
                else:
                    analysis.age_distribution["old"] += 1

            except Exception:
                # Skip notes that can't be processed
                continue

        # Sort notes by age
        notes_data.sort(key=lambda x: x["days_old"], reverse=True)

        # Set analysis results
        analysis.total_count = len(notes_data)
        analysis.notes_by_age = notes_data

        if notes_data:
            analysis.oldest_note = notes_data[0]
            analysis.newest_note = notes_data[-1]

        return analysis

    def generate_fleeting_health_report(self) -> Dict:
        """
        Generate a health report for fleeting notes with recommendations.

        Returns:
            Dict: Health report with status, distribution, and recommendations
        """
        # Get analysis
        analysis = self.analyze_fleeting_notes()

        # Calculate health status
        if analysis.total_count == 0:
            health_status = "HEALTHY"
            summary = "No fleeting notes found. Your fleeting notes are well-managed."
        else:
            old_percentage = (
                (analysis.age_distribution["old"] / analysis.total_count * 100)
                if analysis.total_count > 0
                else 0
            )
            stale_percentage = (
                (analysis.age_distribution["stale"] / analysis.total_count * 100)
                if analysis.total_count > 0
                else 0
            )

            if old_percentage >= 50:
                health_status = "CRITICAL"
                summary = f"Critical: {old_percentage:.0f}% of fleeting notes are over 90 days old and require immediate attention."
            elif old_percentage >= 30 or stale_percentage >= 40:
                health_status = "ATTENTION"
                summary = f"Attention needed: {stale_percentage + old_percentage:.0f}% of fleeting notes are stale or old."
            else:
                health_status = "HEALTHY"
                summary = f'Healthy: Most fleeting notes ({analysis.age_distribution["new"] + analysis.age_distribution["recent"]}/{analysis.total_count}) are being actively processed.'

        # Generate recommendations
        recommendations = []
        if analysis.age_distribution["old"] > 0:
            recommendations.append(
                f"Process {analysis.age_distribution['old']} old notes (90+ days) for promotion or archival"
            )
        if analysis.age_distribution["stale"] > 0:
            recommendations.append(
                f"Review {analysis.age_distribution['stale']} stale notes (31-90 days) for relevance"
            )
        if analysis.total_count > 20:
            recommendations.append(
                "Consider batch processing to reduce fleeting note backlog"
            )
        if analysis.age_distribution["new"] == 0 and analysis.total_count > 0:
            recommendations.append(
                "No new notes in the last week - consider if capture process is working"
            )

        # Get oldest notes for priority processing
        oldest_notes = (
            analysis.notes_by_age[:5]
            if len(analysis.notes_by_age) >= 5
            else analysis.notes_by_age
        )

        # Get newest notes to show recent activity
        newest_notes = (
            analysis.notes_by_age[-5:]
            if len(analysis.notes_by_age) >= 5
            else analysis.notes_by_age
        )
        newest_notes.reverse()  # Show newest first

        return {
            "summary": summary,
            "health_status": health_status,
            "total_count": analysis.total_count,
            "age_distribution": analysis.age_distribution,
            "recommendations": (
                recommendations
                if recommendations
                else ["Keep up the good work maintaining your fleeting notes!"]
            ),
            "oldest_notes": oldest_notes,
            "newest_notes": newest_notes,
            "oldest_note": analysis.oldest_note,
            "newest_note": analysis.newest_note,
        }


# ---------------------------------------------------------------------------
# fleeting_note_coordinator
# ---------------------------------------------------------------------------


class FleetingNoteCoordinator:
    """
    Coordinates fleeting note management workflows.

    ADR-002 Phase 12b: Extracts fleeting note triage and promotion to reduce WorkflowManager complexity.
    """

    def __init__(
        self,
        fleeting_dir: Path,
        inbox_dir: Path,
        permanent_dir: Path,
        literature_dir: Path,
        process_callback: Optional[Callable] = None,
        default_quality_threshold: float = 0.7,
    ):
        """
        Initialize fleeting note coordinator.

        Args:
            fleeting_dir: Path to Fleeting Notes directory
            inbox_dir: Path to Inbox directory
            permanent_dir: Path to Permanent Notes directory
            literature_dir: Path to Literature Notes directory
            process_callback: Callback to WorkflowManager.process_inbox_note for quality assessment
            default_quality_threshold: Default quality threshold for promotion
        """
        self.fleeting_dir = Path(fleeting_dir)
        self.inbox_dir = Path(inbox_dir)
        self.permanent_dir = Path(permanent_dir)
        self.literature_dir = Path(literature_dir)
        self.process_callback = process_callback
        self.default_quality_threshold = default_quality_threshold

        # Ensure directories exist
        self.fleeting_dir.mkdir(parents=True, exist_ok=True)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def find_fleeting_notes(self) -> List[Path]:
        """
        Find all fleeting notes for triage processing.

        Returns:
            List of Path objects for fleeting notes
        """
        fleeting_notes = []

        # Check both Fleeting Notes and Inbox directories
        for directory in [self.fleeting_dir, self.inbox_dir]:
            if directory.exists():
                for note_file in directory.glob("*.md"):
                    try:
                        content = note_file.read_text(encoding="utf-8")
                        metadata, _ = _parse_frontmatter(content)

                        # Include notes that are explicitly fleeting type or in fleeting directory
                        if (
                            metadata.get("type") == "fleeting"
                            or directory.name == "Fleeting Notes"
                        ):
                            fleeting_notes.append(note_file)

                    except Exception:
                        # Skip files that can't be read or parsed
                        continue

        return fleeting_notes

    def generate_triage_report(
        self, quality_threshold: Optional[float] = None, fast: bool = True
    ) -> Dict:
        """
        Generate AI-powered triage report for fleeting notes with quality assessment.

        Args:
            quality_threshold: Optional minimum quality threshold (0.0-1.0) for filtering
            fast: If True, use fast mode for quality assessment

        Returns:
            Dict: Triage report with quality assessment and recommendations
        """
        start_time = time.time()

        # Get fleeting notes for processing
        fleeting_notes = self.find_fleeting_notes()

        if not fleeting_notes:
            return {
                "total_notes_processed": 0,
                "quality_distribution": {"high": 0, "medium": 0, "low": 0},
                "recommendations": [],
                "processing_time": time.time() - start_time,
                "quality_threshold": quality_threshold,
            }

        # Process each note for quality assessment
        recommendations = []
        quality_scores = []

        for note_path in fleeting_notes:
            try:
                # Use callback for quality assessment
                result = self.process_callback(note_path, fast=fast)

                quality_score = result.get("quality_score", 0.5)
                quality_scores.append(quality_score)

                # Generate recommendation based on quality
                if quality_score >= 0.7:
                    action = "Promote to Permanent"
                    rationale = "High quality content with clear insights and good structure. Ready for promotion."
                elif quality_score >= 0.4:
                    action = "Needs Enhancement"
                    rationale = "Medium quality with potential. Consider adding more detail or connections."
                else:
                    action = "Consider Archiving"
                    rationale = "Low quality content. May need significant work or could be archived."

                # Apply quality threshold filter if specified
                if quality_threshold is None or quality_score >= quality_threshold:
                    recommendations.append(
                        {
                            "note_path": str(note_path),
                            "quality_score": quality_score,
                            "action": action,
                            "rationale": rationale,
                            "ai_tags": result.get("ai_tags", []),
                            "created": result.get("metadata", {}).get(
                                "created", "Unknown"
                            ),
                        }
                    )

            except Exception as e:
                # Handle individual note processing errors gracefully
                recommendations.append(
                    {
                        "note_path": str(note_path),
                        "quality_score": 0.0,
                        "action": "Processing Error",
                        "rationale": f"Error processing note: {str(e)}",
                        "ai_tags": [],
                        "created": "Unknown",
                    }
                )

        # Calculate quality distribution
        quality_distribution = {"high": 0, "medium": 0, "low": 0}
        for score in quality_scores:
            if score >= 0.7:
                quality_distribution["high"] += 1
            elif score >= 0.4:
                quality_distribution["medium"] += 1
            else:
                quality_distribution["low"] += 1

        # Sort recommendations by quality score (highest first)
        recommendations.sort(key=lambda x: x["quality_score"], reverse=True)

        processing_time = time.time() - start_time
        total_processed = len(fleeting_notes)
        filtered_count = (
            total_processed - len(recommendations) if quality_threshold else 0
        )

        return {
            "total_notes_processed": total_processed,
            "quality_distribution": quality_distribution,
            "recommendations": recommendations,
            "processing_time": processing_time,
            "quality_threshold": quality_threshold,
            "filtered_count": filtered_count,
        }

    def promote_fleeting_note(
        self,
        note_path: str,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
        base_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Promote a single fleeting note to permanent or literature status.

        Args:
            note_path: Path to the fleeting note to promote
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes
            base_dir: Base directory for path resolution (optional)

        Returns:
            Dict: Promotion results with details of operations performed
        """
        start_time = time.time()

        try:
            # Import DirectoryOrganizer from production-ready infrastructure
            from src.utils.directory_organizer import DirectoryOrganizer

            # Resolve note path
            if not note_path.startswith("/"):
                # If path starts with 'knowledge/', it's relative to the vault root
                if note_path.startswith("knowledge/") and base_dir:
                    # Remove 'knowledge/' prefix since base_dir already points to knowledge/
                    relative_path = note_path.replace("knowledge/", "", 1)
                    note_path_obj = base_dir / relative_path
                elif base_dir:
                    note_path_obj = base_dir / note_path
                else:
                    note_path_obj = Path(note_path)
            else:
                note_path_obj = Path(note_path)

            if not note_path_obj.exists():
                raise ValueError(f"Note not found: {note_path}")

            # Validate note is fleeting type
            content = note_path_obj.read_text(encoding="utf-8")
            metadata, body = _parse_frontmatter(content)

            if metadata.get("type") != "fleeting":
                raise ValueError(
                    f"Note is not a fleeting note (type: {metadata.get('type')})"
                )

            # Get AI quality assessment for the note
            ai_result = self.process_callback(note_path_obj, fast=True)
            quality_score = ai_result.get("quality_score", 0.5)

            # Auto-detect target type if not specified
            if target_type is None:
                # Use simple heuristic: literature if it has source/url, otherwise permanent
                if metadata.get("source") or metadata.get("url"):
                    target_type = "literature"
                else:
                    target_type = "permanent"

            # Determine target directory
            if target_type == "literature":
                target_dir = self.literature_dir
            else:
                target_dir = self.permanent_dir

            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            # Create target path
            target_path = target_dir / note_path_obj.name

            promotion_result = {
                "success": True,
                "promoted_notes": [
                    {
                        "note_path": str(note_path_obj),
                        "target_type": target_type,
                        "target_path": str(target_path),
                        "quality_score": quality_score,
                        "preview_mode": preview_mode,
                    }
                ],
                "batch_mode": False,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "target_directory": str(target_dir),
                "promotion_time": datetime.now().isoformat(),
                "processing_time": 0,
                "backup_created": False,
                "metadata_updated": True,
            }

            if preview_mode:
                # Preview mode - don't actually move files
                promotion_result["processing_time"] = time.time() - start_time
                return promotion_result

            # Create backup using DirectoryOrganizer
            if base_dir:
                organizer = DirectoryOrganizer(
                    base_dir.parent if base_dir.parent else base_dir
                )
                backup_path = organizer.create_backup()
                promotion_result["backup_created"] = True
                promotion_result["backup_path"] = str(backup_path)

            # Update metadata for promotion
            updated_metadata = metadata.copy()
            updated_metadata["type"] = target_type
            updated_metadata["promoted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            updated_metadata["promoted_date"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
            updated_metadata["promotion_quality_score"] = quality_score

            # Reconstruct file content with updated metadata
            updated_content = "---\n"
            for key, value in updated_metadata.items():
                if isinstance(value, list):
                    updated_content += f"{key}: {value}\n"
                elif isinstance(value, str) and " " in value:
                    updated_content += f'{key}: "{value}"\n'
                else:
                    updated_content += f"{key}: {value}\n"
            updated_content += f"---\n\n{body}"

            # Write to target location
            target_path.write_text(updated_content, encoding="utf-8")

            # Remove original file
            note_path_obj.unlink()

            promotion_result["processing_time"] = time.time() - start_time
            return promotion_result

        except Exception as e:
            return {
                "success": False,
                "promoted_notes": [
                    {
                        "note_path": note_path,
                        "error": str(e),
                        "quality_score": 0,
                        "preview_mode": preview_mode,
                    }
                ],
                "batch_mode": False,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "target_directory": "unknown",
                "promotion_time": datetime.now().isoformat(),
                "processing_time": time.time() - start_time,
                "backup_created": False,
                "error": str(e),
            }

    def promote_fleeting_notes_batch(
        self,
        quality_threshold: float = 0.7,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
        base_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Promote multiple fleeting notes based on quality threshold.

        Args:
            quality_threshold: Minimum quality score for promotion
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes
            base_dir: Base directory for path resolution (optional)

        Returns:
            Dict: Batch promotion results
        """
        start_time = time.time()

        try:
            # Get triage results to identify high-quality notes
            triage_report = self.generate_triage_report(
                quality_threshold=quality_threshold, fast=True
            )

            # Find notes eligible for promotion
            eligible_notes = [
                rec
                for rec in triage_report["recommendations"]
                if rec["action"] == "Promote to Permanent"
                and rec["quality_score"] >= quality_threshold
            ]

            if not eligible_notes:
                return {
                    "total_promoted": 0,
                    "total_skipped": triage_report["total_notes_processed"],
                    "promoted_notes": [],
                    "batch_mode": True,
                    "preview": preview_mode,
                    "preview_mode": preview_mode,
                    "quality_threshold": quality_threshold,
                    "processing_time": time.time() - start_time,
                    "backup_created": False,
                }

            # Create single backup for batch operation
            backup_created = False
            backup_path = None

            if not preview_mode and base_dir:
                try:
                    from src.utils.directory_organizer import DirectoryOrganizer

                    organizer = DirectoryOrganizer(
                        base_dir.parent if base_dir.parent else base_dir
                    )
                    backup_path = organizer.create_backup()
                    backup_created = True
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")

            # Process each eligible note
            promoted_notes = []
            for note_rec in eligible_notes:
                try:
                    single_result = self.promote_fleeting_note(
                        note_path=note_rec["note_path"],
                        target_type=target_type,
                        preview_mode=preview_mode,
                        base_dir=base_dir,
                    )

                    # Extract the promoted note info and add batch context
                    if single_result.get("promoted_notes"):
                        promoted_note = single_result["promoted_notes"][0]
                        promoted_note["batch_promotion"] = True
                        promoted_notes.append(promoted_note)

                except Exception as e:
                    # Add failed note to results
                    promoted_notes.append(
                        {
                            "note_path": note_rec["note_path"],
                            "error": str(e),
                            "quality_score": note_rec["quality_score"],
                            "batch_promotion": True,
                            "preview_mode": preview_mode,
                        }
                    )

            total_processed = triage_report["total_notes_processed"]
            total_promoted = len([n for n in promoted_notes if "error" not in n])
            total_skipped = total_processed - len(eligible_notes)

            return {
                "total_promoted": total_promoted,
                "total_skipped": total_skipped,
                "promoted_notes": promoted_notes,
                "batch_mode": True,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "quality_threshold": quality_threshold,
                "processing_time": time.time() - start_time,
                "backup_created": backup_created,
                "backup_path": str(backup_path) if backup_path else None,
            }

        except Exception as e:
            return {
                "total_promoted": 0,
                "total_skipped": 0,
                "promoted_notes": [],
                "batch_mode": True,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "quality_threshold": quality_threshold,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "backup_created": False,
            }


# ---------------------------------------------------------------------------
# review_triage_coordinator
# ---------------------------------------------------------------------------

from src.utils.tags import sanitize_tags

# Prompt used when vault's fleeting-triage-llm-prompt file is absent.
_DEFAULT_TRIAGE_SYSTEM_PROMPT = """\
You are a Zettelkasten triage assistant. Evaluate the fleeting note provided \
and return a JSON object with exactly three keys:
  "action"     — one of: "promote_to_permanent", "needs_enhancement", "consider_archiving"
  "reasoning"  — 1–2 sentences explaining your recommendation
  "confidence" — one of: "high", "medium", "low"

Criteria: clarity of insight, uniqueness, actionability, connection potential.
Return ONLY valid JSON. No preamble, no markdown fences.\
"""

# Relative path inside the vault root where the validated prompt may live.
_VAULT_TRIAGE_PROMPT_PATH = "knowledge/Prompts/fleeting-triage-llm-prompt-20260511.md"


class ReviewTriageCoordinator:
    """
    Coordinates review and triage operations for weekly review and fleeting notes.

    ADR-002 Phase 5: Extracted from WorkflowManager (~371 LOC reduction).

    Responsibilities:
    - Scan directories for review candidates
    - Generate AI-powered weekly recommendations
    - Assess fleeting note quality and generate triage reports
    - Categorize notes by quality thresholds

    Integration:
    - Uses WorkflowManager.process_inbox_note() for AI quality assessment
    - Consumed by CLI layer (workflow_demo.py)
    - Independent of other coordinators (Lifecycle, Connection, Analytics, Promotion)
    """

    def __init__(self, base_dir: Path, workflow_manager):
        """
        Initialize ReviewTriageCoordinator.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            workflow_manager: WorkflowManager instance for AI processing delegation
        """
        self.base_dir = Path(base_dir)
        self.workflow_manager = workflow_manager
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"

    def scan_review_candidates(self) -> List[Dict]:
        """
        Scan for notes that need weekly review attention.

        Finds all notes that require review:
        - All .md files in Inbox/ directory (regardless of status)
        - Files in Fleeting Notes/ directory with status: inbox

        Returns:
            List of candidate dictionaries with:
                - path: Path object to the note file
                - source: "inbox" or "fleeting" indicating origin
                - metadata: Parsed YAML frontmatter (empty dict if invalid)
        """
        candidates = []

        # Scan inbox directory - all .md files are candidates
        candidates.extend(
            self._scan_directory_for_candidates(
                self.inbox_dir,
                source_type="inbox",
                filter_func=None,  # All inbox files are candidates
            )
        )

        # Scan fleeting notes directory - only notes with status: inbox
        candidates.extend(
            self._scan_directory_for_candidates(
                self.fleeting_dir,
                source_type="fleeting",
                filter_func=lambda metadata: metadata.get("status") == "inbox",
            )
        )

        return candidates

    def _scan_directory_for_candidates(
        self, directory: Path, source_type: str, filter_func: Optional[callable] = None
    ) -> List[Dict]:
        """
        Helper method to scan a directory for review candidates.

        Args:
            directory: Path to scan
            source_type: Type identifier ("inbox" or "fleeting")
            filter_func: Optional function to filter candidates based on metadata

        Returns:
            List of candidate dictionaries
        """
        candidates = []

        if not directory.exists():
            return candidates

        try:
            for note_path in directory.glob("*.md"):
                try:
                    candidate = self._create_candidate_dict(note_path, source_type)

                    # Apply filter if provided
                    if filter_func is None or filter_func(candidate["metadata"]):
                        candidates.append(candidate)

                except Exception as e:
                    candidates.append(
                        {
                            "path": note_path,
                            "source": source_type,
                            "metadata": {},
                            "error": str(e),
                        }
                    )
        except Exception:
            # Handle directory access errors gracefully
            pass

        return candidates

    def _create_candidate_dict(self, note_path: Path, source_type: str) -> Dict:
        """
        Create a candidate dictionary from a note file.

        Args:
            note_path: Path to the note file
            source_type: Source type ("inbox" or "fleeting")

        Returns:
            Dictionary with path, source, and metadata

        Raises:
            Exception: If file cannot be read or processed
        """
        with open(note_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata, _ = _parse_frontmatter(content)

        return {"path": note_path, "source": source_type, "metadata": metadata}

    def generate_weekly_recommendations(
        self, candidates: List[Dict], dry_run: bool = False
    ) -> Dict:
        """
        Generate AI-powered recommendations for weekly review candidates.

        Args:
            candidates: List of candidate dictionaries from scan_review_candidates()
            dry_run: If True, use fast mode to skip external AI calls

        Returns:
            Dictionary with:
                - summary: Counts by recommendation type
                - recommendations: List of detailed recommendation objects
                - generated_at: ISO timestamp of generation
        """
        result = self._initialize_recommendations_result(len(candidates))

        # Process each candidate with error handling
        for candidate in candidates:
            recommendation = self._process_candidate_for_recommendation(
                candidate, dry_run=dry_run
            )
            result["recommendations"].append(recommendation)

            # Update summary counts based on action
            self._update_summary_counts(result["summary"], recommendation["action"])

        return result

    def _initialize_recommendations_result(self, total_candidates: int) -> Dict:
        """
        Initialize the weekly recommendations result structure.

        Args:
            total_candidates: Number of candidates being processed

        Returns:
            Initialized result dictionary
        """
        return {
            "summary": {
                "total_notes": total_candidates,
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0,
                "processing_errors": 0,
            },
            "recommendations": [],
            "generated_at": datetime.now().isoformat(),
        }

    def _process_candidate_for_recommendation(
        self, candidate: Dict, dry_run: bool = False
    ) -> Dict:
        """
        Process a single candidate and generate its recommendation.

        Args:
            candidate: Candidate dictionary with path, source, metadata
            dry_run: If True, use fast mode to avoid external AI calls

        Returns:
            Recommendation dictionary for the candidate
        """
        try:
            # Use existing AI processing for quality assessment
            if dry_run:
                processing_result = self.workflow_manager.process_inbox_note(
                    str(candidate["path"]), dry_run=True, fast=True
                )
            else:
                processing_result = self.workflow_manager.process_inbox_note(
                    str(candidate["path"])
                )

            if "error" in processing_result:
                return self._create_error_recommendation(
                    candidate,
                    "Processing failed - manual review required",
                    processing_result["error"],
                )

            # Extract and format the recommendation
            return self._extract_weekly_recommendation(candidate, processing_result)

        except Exception as e:
            return self._create_error_recommendation(
                candidate, "Unexpected error during processing", str(e)
            )

    def _create_error_recommendation(
        self, candidate: Dict, reason: str, error: str
    ) -> Dict:
        """
        Create a recommendation for a candidate that failed processing.

        Args:
            candidate: Original candidate dictionary
            reason: Human-readable reason for the error
            error: Technical error message

        Returns:
            Error recommendation dictionary
        """
        return {
            "file_name": candidate["path"].name,
            "source": candidate["source"],
            "action": "manual_review",
            "reason": reason,
            "error": error,
            "quality_score": None,
            "confidence": None,
            "ai_tags": [],
            "metadata": candidate.get("metadata", {}),
        }

    def _update_summary_counts(self, summary: Dict, action: str) -> None:
        """
        Update summary counts based on recommendation action.

        Args:
            summary: Summary dictionary to update
            action: Recommendation action type
        """
        if action == "promote_to_permanent":
            summary["promote_to_permanent"] += 1
        elif action == "move_to_fleeting":
            summary["move_to_fleeting"] += 1
        elif action == "improve_or_archive":
            summary["needs_improvement"] += 1
        elif action == "manual_review":
            summary["processing_errors"] += 1

    def _extract_weekly_recommendation(
        self, candidate: Dict, processing_result: Dict
    ) -> Dict:
        """
        Extract weekly recommendation from processing result.

        Args:
            candidate: Original candidate dictionary
            processing_result: Result from process_inbox_note()

        Returns:
            Formatted recommendation dictionary
        """
        # Get first recommendation (most important)
        recommendations = processing_result.get("recommendations", [])
        primary_rec = (
            recommendations[0]
            if recommendations
            else {
                "action": "manual_review",
                "reason": "No specific recommendation generated",
                "confidence": 0.5,
            }
        )

        # Sanitize metadata tags for clean display in weekly outputs (non-destructive)
        metadata = (
            candidate["metadata"] if isinstance(candidate.get("metadata"), dict) else {}
        )
        if metadata:
            try:
                if "tags" in metadata:
                    metadata = {
                        **metadata,
                        "tags": sanitize_tags(metadata.get("tags", [])),
                    }
            except Exception:
                # If anything goes wrong, fall back to original metadata
                metadata = candidate.get("metadata", {})

        return {
            "file_name": candidate["path"].name,
            "source": candidate["source"],
            "action": primary_rec["action"],
            "reason": primary_rec["reason"],
            "quality_score": processing_result.get("quality_score"),
            "confidence": primary_rec.get("confidence", 0.5),
            "ai_tags": processing_result.get("processing", {}).get("ai_tags", []),
            "metadata": metadata,
        }

    def _load_triage_system_prompt(self) -> str:
        """Return the validated triage prompt from the vault, or the built-in default."""
        vault_root = (
            self.base_dir.parent
        )  # base_dir is knowledge/, vault root is one up
        prompt_path = vault_root / _VAULT_TRIAGE_PROMPT_PATH
        if prompt_path.exists():
            try:
                return prompt_path.read_text(encoding="utf-8").strip()
            except OSError:
                pass
        return _DEFAULT_TRIAGE_SYSTEM_PROMPT

    def _score_note_with_llm(
        self, note_path: Path, content: str, ollama: OllamaClient, system_prompt: str
    ) -> Dict[str, Any]:
        """Call Ollama with the triage prompt and return parsed JSON result.

        Raises ValueError on malformed JSON so the caller surfaces it loudly.
        """
        raw = ollama.generate_completion(prompt=content, system_prompt=system_prompt)
        try:
            result = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            raise ValueError(
                f"LLM returned malformed JSON for '{note_path.name}': {raw[:120]!r}"
            )
        if "action" not in result or "reasoning" not in result:
            raise ValueError(
                f"LLM JSON missing required keys for '{note_path.name}': {result}"
            )
        return result

    def generate_fleeting_triage_report(
        self, quality_threshold: Optional[float] = None, mutate: bool = False
    ) -> Dict:
        """Generate LLM-powered triage report for fleeting notes.

        Args:
            quality_threshold: Optional minimum quality filter (0.0-1.0).
            mutate: If True, write triage_recommendation back to note frontmatter.
                    Default False — read-only (never modifies files).

        Raises:
            RuntimeError: If Ollama is unavailable (no silent fallback).
            ValueError: If any note returns malformed JSON from the LLM.
        """
        from src.utils.frontmatter import parse_frontmatter, build_frontmatter
        from src.utils.io import safe_write

        start_time = time.time()

        # Pre-flight: fail loudly if Ollama is down.
        ollama = OllamaClient()
        if not ollama.health_check():
            raise RuntimeError(
                "Ollama service is not available. "
                "Run `ollama serve` and ensure your model is pulled, then retry."
            )

        system_prompt = self._load_triage_system_prompt()
        fleeting_notes = self._find_fleeting_notes()

        if not fleeting_notes:
            return {
                "total_notes_processed": 0,
                "quality_distribution": {"high": 0, "medium": 0, "low": 0},
                "recommendations": [],
                "processing_time": time.time() - start_time,
                "quality_threshold": quality_threshold,
            }

        recommendations: List[Dict] = []
        action_counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}

        for note_path in fleeting_notes:
            content = note_path.read_text(encoding="utf-8")
            llm_result = self._score_note_with_llm(
                note_path, content, ollama, system_prompt
            )

            action = llm_result.get("action", "needs_enhancement")
            reasoning = llm_result.get("reasoning", "")
            confidence = llm_result.get("confidence", "medium")

            # Map action to a quality tier for distribution tracking.
            if action == "promote_to_permanent":
                tier = "high"
            elif action == "consider_archiving":
                tier = "low"
            else:
                tier = "medium"
            action_counts[tier] += 1

            # Write recommendation back to frontmatter only when explicitly requested.
            if mutate:
                try:
                    frontmatter, body = parse_frontmatter(content)
                    frontmatter["triage_recommendation"] = action
                    safe_write(note_path, build_frontmatter(frontmatter, body))
                except Exception as write_err:
                    logging.getLogger(__name__).warning(
                        "triage: failed to write frontmatter for %s: %s",
                        note_path.name,
                        write_err,
                    )

            quality_score = {"high": 0.8, "medium": 0.5, "low": 0.2}[tier]
            rec = {
                "note_path": str(note_path),
                "action": action,
                "reasoning": reasoning,
                "confidence": confidence,
                "tier": tier,
                "quality_score": quality_score,
            }
            if quality_threshold is None or quality_score >= (quality_threshold or 0.0):
                recommendations.append(rec)

        filtered_count = len(fleeting_notes) - len(recommendations)
        recommendations.sort(
            key=lambda r: ("low", "medium", "high").index(r["tier"]), reverse=True
        )

        return {
            "total_notes_processed": len(fleeting_notes),
            "quality_distribution": action_counts,
            "recommendations": recommendations,
            "processing_time": time.time() - start_time,
            "quality_threshold": quality_threshold,
            "filtered_count": filtered_count,
        }

    def _find_fleeting_notes(self) -> List[Path]:
        """Find all fleeting notes for triage processing."""
        fleeting_notes = []

        # Check both Fleeting Notes and Inbox directories
        fleeting_dir = self.base_dir / "Fleeting Notes"
        inbox_dir = self.base_dir / "Inbox"

        for directory in [fleeting_dir, inbox_dir]:
            if directory.exists():
                for note_file in directory.glob("*.md"):
                    try:
                        content = note_file.read_text(encoding="utf-8")
                        metadata, _ = _parse_frontmatter(content)

                        # Include notes that are explicitly fleeting type or in fleeting directory
                        if (
                            metadata.get("type") == "fleeting"
                            or directory.name == "Fleeting Notes"
                        ):
                            fleeting_notes.append(note_file)

                    except Exception:
                        # Skip files that can't be read or parsed
                        continue

        return fleeting_notes


__all__ = [
    # note lifecycle
    "StatusTransition",
    "NoteLifecycleManager",
    # promotion
    "PromotionEngine",
    # fleeting coordination
    "FleetingNoteCoordinator",
    # fleeting analysis
    "FleetingAnalysis",
    "FleetingAnalysisCoordinator",
    # review triage
    "ReviewTriageCoordinator",
    # import
    "CSVImportAdapter",
    "JSONImportAdapter",
    "NoteWriter",
    # import schema
    "ImportItem",
    "validate_item",
]
