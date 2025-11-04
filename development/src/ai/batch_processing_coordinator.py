"""
Batch Processing Coordinator (ADR-002 Phase 11).

Extracts batch processing logic from WorkflowManager to reduce god class size.

GitHub Issue #45 Phase 2 Priority 3 (P1-VAULT-10):
- Migrated to use centralized vault configuration
- Constructor now accepts base_dir and workflow_manager
- Loads inbox_dir from vault config internally
"""

from pathlib import Path
from typing import Dict, Callable, Optional
import sys
import logging

from src.config.vault_config_loader import get_vault_config

logger = logging.getLogger(__name__)


class BatchProcessingCoordinator:
    """Coordinates batch processing of inbox notes with progress tracking."""

    def __init__(
        self,
        base_dir: Path,
        workflow_manager,
        process_callback: Optional[Callable[[str], Dict]] = None,
    ):
        """Initialize the batch processing coordinator.

        Args:
            base_dir: Path to vault root directory
            workflow_manager: WorkflowManager instance for delegation pattern
            process_callback: Optional callback for processing notes (can be set later)
        """
        # Store base directory and workflow manager
        self.base_dir = Path(base_dir)
        self.workflow_manager = workflow_manager

        # Load vault configuration for directory paths
        vault_config = get_vault_config(str(self.base_dir))
        self.inbox_dir = vault_config.inbox_dir

        # Ensure inbox directory exists (create if needed for test environments)
        created = not self.inbox_dir.exists()
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        if created:
            logger.info(
                f"Created inbox directory for test environment: {self.inbox_dir}"
            )
        else:
            logger.debug(f"Using existing inbox directory: {self.inbox_dir}")

        # Callback can be None initially and set later by WorkflowManager
        if process_callback is not None and not callable(process_callback):
            logger.error(f"Invalid process_callback type: {type(process_callback)}")
            raise TypeError("process_callback must be a callable function")

        self.process_callback = process_callback

        logger.info(
            f"BatchProcessingCoordinator initialized: base_dir={self.base_dir}, "
            f"inbox_dir={self.inbox_dir}, has_callback={process_callback is not None}"
        )

    def batch_process_inbox(self, show_progress: bool = True) -> Dict:
        """Process all notes in the inbox with progress tracking."""
        inbox_files = list(self.inbox_dir.glob("*.md"))
        total = len(inbox_files)

        logger.info(
            f"Starting batch processing: {total} files in {self.inbox_dir}, "
            f"show_progress={show_progress}"
        )

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

            logger.debug(f"Processing note [{idx}/{total}]: {note_file.name}")

            try:
                result = self.process_callback(str(note_file))

                if "error" not in result:
                    results["processed"] += 1
                    logger.debug(f"Successfully processed: {note_file.name}")

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
                    logger.warning(
                        f"Processing failed for {note_file.name}: {result.get('error', 'Unknown error')}"
                    )

                results["results"].append(result)

            except Exception as e:
                results["failed"] += 1
                logger.error(
                    f"Exception processing {note_file.name}: {type(e).__name__}: {e}",
                    exc_info=True,
                )
                results["results"].append(
                    {"original_file": str(note_file), "error": str(e)}
                )

        if show_progress and total > 0:
            sys.stderr.write("\r" + " " * 80 + "\r")
            sys.stderr.flush()

        logger.info(
            f"Batch processing complete: {results['processed']}/{total} successful, "
            f"{results['failed']} failed | "
            f"Summary: {results['summary']['promote_to_permanent']} promote, "
            f"{results['summary']['move_to_fleeting']} fleeting, "
            f"{results['summary']['needs_improvement']} needs improvement"
        )

        return results
