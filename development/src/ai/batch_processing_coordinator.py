"""
Batch Processing Coordinator (ADR-002 Phase 11).

Extracts batch processing logic from WorkflowManager to reduce god class size.
"""

from pathlib import Path
from typing import Dict, Callable, Optional
import sys


class BatchProcessingCoordinator:
    """Coordinates batch processing of inbox notes with progress tracking."""

    def __init__(
        self, inbox_dir: Path, process_callback: Optional[Callable[[str], Dict]] = None
    ):
        """Initialize the batch processing coordinator.

        Args:
            inbox_dir: Path to inbox directory
            process_callback: Optional callback for processing notes (can be set later)
        """
        if not isinstance(inbox_dir, Path):
            inbox_dir = Path(inbox_dir)

        if not inbox_dir.exists():
            raise ValueError(f"Inbox directory does not exist: {inbox_dir}")

        # Callback can be None initially and set later by WorkflowManager
        if process_callback is not None and not callable(process_callback):
            raise TypeError("process_callback must be a callable function")

        self.inbox_dir = inbox_dir
        self.process_callback = process_callback

    def batch_process_inbox(self, show_progress: bool = True) -> Dict:
        """Process all notes in the inbox with progress tracking."""
        inbox_files = list(self.inbox_dir.glob("*.md"))
        total = len(inbox_files)

        results = {
            "total_files": total,
            "processed": 0,
            "failed": 0,
            "results": [],
            "summary": {
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0,
            },
        }

        for idx, note_file in enumerate(inbox_files, 1):
            if show_progress:
                filename = note_file.name
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                progress_pct = int((idx / total) * 100)
                sys.stderr.write(f"\r[{idx}/{total}] {progress_pct}% - {filename}...")
                sys.stderr.flush()

            try:
                result = self.process_callback(str(note_file))

                if "error" not in result:
                    results["processed"] += 1

                    for rec in result.get("recommendations", []):
                        action = rec.get("action", "")
                        if action == "promote_to_permanent":
                            results["summary"]["promote_to_permanent"] += 1
                        elif action == "move_to_fleeting":
                            results["summary"]["move_to_fleeting"] += 1
                        elif action == "improve_or_archive":
                            results["summary"]["needs_improvement"] += 1
                else:
                    results["failed"] += 1

                results["results"].append(result)

            except Exception as e:
                results["failed"] += 1
                results["results"].append(
                    {"original_file": str(note_file), "error": str(e)}
                )

        if show_progress and total > 0:
            sys.stderr.write("\r" + " " * 80 + "\r")
            sys.stderr.flush()

        return results
