"""
Batch Inbox Processor with Skip Logic (Phase 4-5).

Provides idempotent batch processing for Inbox notes, skipping already-processed notes.
Skip logic: Notes with BOTH ai_processed=true AND triage_recommendation present are skipped.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.frontmatter import parse_frontmatter

logger = logging.getLogger(__name__)


def is_note_eligible_for_processing(note_path: Path) -> bool:
    """
    Determine if a note needs processing.

    A note is eligible if:
    - ai_processed is missing OR false, OR
    - triage_recommendation is missing

    A note is NOT eligible (should be skipped) if:
    - ai_processed is true AND triage_recommendation is present

    Args:
        note_path: Path to the note file

    Returns:
        True if note should be processed, False if it should be skipped
    """
    try:
        content = note_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)

        if frontmatter is None:
            return True

        ai_processed = frontmatter.get("ai_processed")
        triage_recommendation = frontmatter.get("triage_recommendation")

        processed = False
        if isinstance(ai_processed, bool):
            processed = ai_processed
        elif ai_processed is None:
            processed = False
        elif isinstance(ai_processed, str):
            normalized = ai_processed.strip().lower()
            processed = normalized not in {"", "false", "no", "0", "none", "null"}
        else:
            processed = True

        if processed is True and triage_recommendation is not None:
            logger.debug(f"Skipping already processed note: {note_path.name}")
            return False

        return True

    except Exception as e:
        logger.warning(f"Error reading note {note_path}: {e}")
        return True


def scan_eligible_notes(inbox_dir: Path) -> List[Path]:
    """
    Scan inbox directory and return only notes that need processing.

    Args:
        inbox_dir: Path to the Inbox directory

    Returns:
        List of Path objects for eligible notes
    """
    if not inbox_dir.exists():
        logger.warning(f"Inbox directory does not exist: {inbox_dir}")
        return []

    eligible = []
    for note_path in inbox_dir.glob("*.md"):
        if is_note_eligible_for_processing(note_path):
            eligible.append(note_path)

    logger.info(f"Found {len(eligible)} eligible notes in {inbox_dir}")
    return eligible


def process_single_note(
    note_path: Path,
    workflow_manager: Optional[Any] = None,
) -> Dict:
    """
    Process a single note using the workflow manager.

    Args:
        note_path: Path to the note to process
        workflow_manager: Optional WorkflowManager instance

    Returns:
        Processing result dict with success, triage_recommendation, etc.
    """
    if workflow_manager is None:
        from src.ai.workflow_manager import WorkflowManager

        vault_path = note_path.parent.parent
        workflow_manager = WorkflowManager(str(vault_path))

    result = workflow_manager.process_inbox_note(str(note_path), dry_run=False)

    triage_rec = None
    recommendations = result.get("recommendations", [])
    if recommendations:
        triage_rec = recommendations[0].get("action")

    return {
        "success": "error" not in result,
        "note": note_path.name,
        "path": str(note_path),
        "triage_recommendation": triage_rec,
        "details": result,
    }


def batch_process_unprocessed_inbox(
    inbox_dir: Path,
    dry_run: bool = False,
    workflow_manager: Optional[Any] = None,
    show_progress: bool = True,
) -> Dict:
    """
    Process all unprocessed notes in the inbox.

    Args:
        inbox_dir: Path to the Inbox directory
        dry_run: If True, don't modify files - just report what would be done
        workflow_manager: Optional WorkflowManager instance
        show_progress: If True, print progress to stderr

    Returns:
        Dict with processed, skipped, errors, error_details, summary, dry_run
    """
    all_notes = list(inbox_dir.glob("*.md")) if inbox_dir.exists() else []
    eligible_notes = scan_eligible_notes(inbox_dir)
    skipped_count = len(all_notes) - len(eligible_notes)

    result = {
        "processed": 0,
        "skipped": skipped_count,
        "errors": 0,
        "error_details": [],
        "summary": {"by_recommendation": {}},
        "dry_run": dry_run,
    }

    if dry_run:
        result["would_process"] = len(eligible_notes)
        result["eligible_notes"] = [str(p) for p in eligible_notes]
        return result

    total = len(eligible_notes)
    for idx, note_path in enumerate(eligible_notes, 1):
        if show_progress:
            pct = int((idx / total) * 100) if total > 0 else 100
            sys.stderr.write(f"\r[{idx}/{total}] {pct}% - {note_path.name[:40]}...")
            sys.stderr.flush()

        try:
            proc_result = process_single_note(note_path, workflow_manager)

            if proc_result.get("success"):
                result["processed"] += 1
                rec = proc_result.get("triage_recommendation")
                if rec:
                    by_rec = result["summary"]["by_recommendation"]
                    by_rec[rec] = by_rec.get(rec, 0) + 1
            else:
                result["errors"] += 1
                result["error_details"].append(
                    {
                        "note": note_path.name,
                        "path": str(note_path),
                        "error": "Processing returned failure",
                    }
                )

        except Exception as e:
            result["errors"] += 1
            result["error_details"].append(
                {
                    "note": note_path.name,
                    "path": str(note_path),
                    "error": str(e),
                }
            )
            logger.exception(f"Error processing {note_path.name}")

    if show_progress and total > 0:
        sys.stderr.write("\r" + " " * 60 + "\r")
        sys.stderr.flush()

    return result
