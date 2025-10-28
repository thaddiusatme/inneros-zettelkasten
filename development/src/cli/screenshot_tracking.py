"""
Processed Screenshot Tracking System

Tracks which screenshots have been processed to prevent reprocessing and API waste.
Part of TDD Iteration 7 for Samsung Screenshot Evening Workflow.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Optional filelock for concurrent safety
try:
    from filelock import FileLock

    FILELOCK_AVAILABLE = True
except ImportError:
    FILELOCK_AVAILABLE = False

    # Simple no-op context manager
    class FileLock:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass


logger = logging.getLogger(__name__)


class ProcessedScreenshotTracker:
    """
    Track processed screenshots to prevent reprocessing

    Stores history in JSON file with screenshot filenames, processing timestamps,
    and file hashes for integrity verification.
    """

    def __init__(self, history_file: Path):
        """
        Initialize tracker with history file

        Args:
            history_file: Path to JSON history file
        """
        self.history_file = Path(history_file)
        self.lock_file = Path(str(history_file) + ".lock")

        # Ensure history file exists with correct structure
        if not self.history_file.exists():
            self._create_empty_history()

        logger.info(f"Initialized ProcessedScreenshotTracker: {self.history_file}")

    def _create_empty_history(self):
        """Create empty history file with correct structure"""
        empty_history = {"version": "1.0", "processed_screenshots": {}}

        # Ensure parent directory exists
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.history_file, "w") as f:
            json.dump(empty_history, f, indent=2)

        logger.info(f"Created empty history file: {self.history_file}")

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file for integrity checking

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string, or "unavailable" if file doesn't exist
        """
        if not file_path.exists():
            return "unavailable"

        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return f"sha256:{sha256_hash.hexdigest()}"
        except Exception as e:
            logger.warning(f"Could not compute hash for {file_path}: {e}")
            return "error"

    def mark_processed(self, screenshot_path: Path, daily_note: str):
        """
        Mark screenshot as processed

        Args:
            screenshot_path: Path to screenshot file
            daily_note: Name of generated note (daily note or individual note path)
        """
        with FileLock(self.lock_file):
            history = self._load_history()

            # Add entry with both keys for backward compatibility
            history["processed_screenshots"][screenshot_path.name] = {
                "processed_at": datetime.now().isoformat(),
                "note_path": daily_note,  # New key (TDD Iteration 8)
                "daily_note": daily_note,  # Legacy key (backward compatibility)
                "file_hash": self._compute_file_hash(screenshot_path),
            }

            # Save
            self._save_history(history)

        logger.info(f"Marked as processed: {screenshot_path.name}")

    def is_processed(self, screenshot_path: Path) -> bool:
        """
        Check if screenshot has been processed

        Args:
            screenshot_path: Path to screenshot file

        Returns:
            True if processed, False otherwise
        """
        history = self._load_history()
        return screenshot_path.name in history["processed_screenshots"]

    def filter_unprocessed(
        self, screenshots: List[Path], force: bool = False
    ) -> List[Path]:
        """
        Filter list to unprocessed screenshots only

        Args:
            screenshots: List of screenshot paths
            force: If True, return all screenshots regardless of history

        Returns:
            List of unprocessed screenshot paths
        """
        if force:
            return screenshots

        history = self._load_history()
        processed_names = set(history["processed_screenshots"].keys())

        unprocessed = [
            screenshot
            for screenshot in screenshots
            if screenshot.name not in processed_names
        ]

        logger.info(
            f"Filtered {len(screenshots)} screenshots -> {len(unprocessed)} unprocessed"
        )
        return unprocessed

    def get_statistics(self, screenshots: List[Path]) -> Dict[str, Any]:
        """
        Get statistics on new vs already-processed screenshots

        Args:
            screenshots: List of screenshot paths to analyze

        Returns:
            Dictionary with statistics
        """
        history = self._load_history()
        processed_names = set(history["processed_screenshots"].keys())

        processed_in_list = [s.name for s in screenshots if s.name in processed_names]
        new_in_list = [s.name for s in screenshots if s.name not in processed_names]

        return {
            "total": len(screenshots),
            "already_processed": len(processed_in_list),
            "new_screenshots": len(new_in_list),
            "processed_files": processed_in_list,
            "new_files": new_in_list,
        }

    def get_history(self) -> Dict[str, Any]:
        """
        Get full processing history

        Returns:
            History dictionary
        """
        return self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        """Load history from JSON file"""
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load history: {e}, creating new")
            self._create_empty_history()
            return {"version": "1.0", "processed_screenshots": {}}

    def _save_history(self, history: Dict[str, Any]):
        """Save history to JSON file"""
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)
