"""
Image Attachment Manager - Centralized Image Storage

Manages centralized image storage in attachments/YYYY-MM/ structure.
Part of TDD Iteration 10: Image Linking System (GREEN Phase)
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImageAttachmentManager:
    """
    Manages centralized image storage in attachments/YYYY-MM/ structure.

    Features:
    - Auto-creates date-based folders (attachments/YYYY-MM/)
    - Device-aware filename prefixes (samsung-, ipad-)
    - Preserves original filenames when possible
    """

    def __init__(self, base_path: Path):
        """
        Initialize manager with knowledge base path.

        Args:
            base_path: Path to knowledge base (e.g., Path("knowledge/"))
        """
        self.base_path = Path(base_path)
        self.attachments_root = self.base_path / "attachments"

    def save_to_attachments(self, image_path: Path) -> Path:
        """
        Save image to centralized attachments/YYYY-MM/ structure.

        Automatically detects:
        - Capture date from filename (Samsung/iPad) or file metadata
        - Device type from filename patterns

        Args:
            image_path: Current path to image file

        Returns:
            Path to saved image in attachments/

        Raises:
            FileNotFoundError: If source image doesn't exist
            ValueError: If image_path is not a file
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Source image not found: {image_path}")

        if not image_path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")

        # Auto-detect capture date and device
        capture_date = self._extract_capture_date(image_path)
        device_prefix = self._detect_device_from_filename(image_path.name)

        # Create destination folder
        dest_folder = self.create_month_folder(capture_date.year, capture_date.month)

        # Generate destination filename
        dest_filename = self._generate_filename(image_path, capture_date, device_prefix)
        dest_path = dest_folder / dest_filename

        # Copy image to attachments (preserve original)
        shutil.copy2(image_path, dest_path)
        logger.info(
            f"Saved image to attachments: {dest_path} (captured: {capture_date.strftime('%Y-%m-%d %H:%M:%S')})"
        )

        return dest_path

    def get_attachment_path(
        self,
        image_filename: str,
        capture_date: datetime,
        device_prefix: Optional[str] = None,
    ) -> Path:
        """
        Calculate destination path for image without moving it.

        Args:
            image_filename: Original image filename
            capture_date: Date when image was captured
            device_prefix: Optional device prefix

        Returns:
            Path where image would be saved
        """
        dest_folder = self.get_month_folder(capture_date.year, capture_date.month)

        if device_prefix:
            # Use device prefix with timestamp
            stem = Path(image_filename).stem
            suffix = Path(image_filename).suffix
            timestamp = capture_date.strftime("%Y%m%d-%H%M%S")
            dest_filename = f"{device_prefix}-{timestamp}{suffix}"
        else:
            dest_filename = image_filename

        return dest_folder / dest_filename

    def create_month_folder(self, year: int, month: int) -> Path:
        """
        Create attachments/YYYY-MM/ folder if it doesn't exist.

        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)

        Returns:
            Path to created/existing folder
        """
        folder_name = f"{year:04d}-{month:02d}"
        folder_path = self.attachments_root / folder_name

        # Create folder and parents if needed
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured folder exists: {folder_path}")

        return folder_path

    def get_month_folder(self, year: int, month: int) -> Path:
        """
        Get path to month folder without creating it.

        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)

        Returns:
            Path to folder (may not exist yet)
        """
        folder_name = f"{year:04d}-{month:02d}"
        return self.attachments_root / folder_name

    def _generate_filename(
        self,
        image_path: Path,
        capture_date: datetime,
        device_prefix: Optional[str] = None,
    ) -> str:
        """
        Generate destination filename with optional device prefix.

        Args:
            image_path: Original image path
            capture_date: Capture date for timestamp
            device_prefix: Optional device prefix (samsung, ipad)

        Returns:
            Filename for attachments folder
        """
        if device_prefix:
            # Format: device-YYYYMMDD-HHMMSS.ext
            timestamp = capture_date.strftime("%Y%m%d-%H%M%S")
            suffix = image_path.suffix
            return f"{device_prefix}-{timestamp}{suffix}"
        else:
            # Use original filename
            return image_path.name

    def _extract_capture_date(self, image_path: Path) -> datetime:
        """
        Extract capture date from filename or file metadata.

        Priority:
        1. Samsung filename: Screenshot_YYYYMMDD_HHMMSS_*.jpg
        2. iPad filename: YYYYMMDD_HHMMSS000_iOS.png
        3. File modification date (fallback)

        Args:
            image_path: Path to image file

        Returns:
            Capture datetime
        """
        filename = image_path.name

        # Try Samsung pattern: Screenshot_20251002_083000_Chrome.jpg
        if filename.startswith("Screenshot_"):
            parts = filename.split("_")
            if len(parts) >= 3:
                try:
                    date_str = parts[1]  # 20251002
                    time_str = parts[2]  # 083000
                    capture_date = datetime.strptime(
                        f"{date_str}{time_str}", "%Y%m%d%H%M%S"
                    )
                    logger.debug(f"Extracted Samsung capture date: {capture_date}")
                    return capture_date
                except (ValueError, IndexError):
                    logger.debug(f"Could not parse Samsung date from: {filename}")

        # Try iPad pattern: 20241002_083000000_iOS.png
        if "_iOS" in filename or "_ios" in filename:
            parts = filename.split("_")
            if len(parts) >= 2:
                try:
                    date_str = parts[0]  # 20241002
                    time_str = parts[1][:6]  # 083000 (first 6 digits)
                    capture_date = datetime.strptime(
                        f"{date_str}{time_str}", "%Y%m%d%H%M%S"
                    )
                    logger.debug(f"Extracted iPad capture date: {capture_date}")
                    return capture_date
                except (ValueError, IndexError):
                    logger.debug(f"Could not parse iPad date from: {filename}")

        # Fallback: Use file modification date
        stat = image_path.stat()
        capture_date = datetime.fromtimestamp(stat.st_mtime)
        logger.debug(f"Using file modification date: {capture_date}")
        return capture_date

    def _detect_device_from_filename(self, filename: str) -> Optional[str]:
        """
        Detect device type from screenshot filename patterns.

        Args:
            filename: Image filename

        Returns:
            Device prefix (samsung, ipad) or None
        """
        filename_lower = filename.lower()

        # Samsung patterns: Screenshot_YYYYMMDD_HHMMSS_*.jpg
        if filename_lower.startswith("screenshot_") and "_" in filename:
            return "samsung"

        # iPad patterns: YYYYMMDD_HHMMSS000_iOS.png
        if "_ios" in filename_lower:
            return "ipad"

        return None
