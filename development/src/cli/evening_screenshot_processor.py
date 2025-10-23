from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional

import logging
from .screenshot_utils import OneDriveScreenshotDetector, ScreenshotOCRProcessor, DailyNoteGenerator, SmartLinkIntegrator, SafeScreenshotManager

logger = logging.getLogger(__name__)

class EveningScreenshotProcessor:
    def __init__(self, onedrive_path: Optional[str], knowledge_path: str):
        self.knowledge_path = Path(knowledge_path)
        self.onedrive_path = Path(onedrive_path) if onedrive_path else None
        self.screenshot_detector = OneDriveScreenshotDetector(str(self.onedrive_path)) if self.onedrive_path else None
        self.ocr_processor = ScreenshotOCRProcessor()
        self.note_generator = DailyNoteGenerator(knowledge_path)
        self.link_integrator = SmartLinkIntegrator(knowledge_path)
        self.safe_manager = SafeScreenshotManager(knowledge_path)

    def scan_todays_screenshots(self, limit: Optional[int] = None) -> List[Path]:
        if not self.screenshot_detector:
            return []
        return self.screenshot_detector.scan_todays_screenshots(limit=limit)

    def process_evening_batch(self, limit: Optional[int] = None) -> Dict[str, Any]:
        start = datetime.now()
        backup_path = self.safe_manager.create_evening_backup()
        screenshots = self.scan_todays_screenshots(limit=limit)
        ocr_results_map = self.ocr_processor.process_batch(screenshots)
        date_str = date.today().strftime("%Y-%m-%d")
        daily_note_path = self.note_generator.generate_daily_note(
            ocr_results=list(ocr_results_map.values()),
            screenshot_paths=[str(p) for p in screenshots],
            date_str=date_str,
        )
        processing_time = (datetime.now() - start).total_seconds()
        result = {
            "processed_count": len(screenshots),
            "daily_note_path": daily_note_path,
            "processing_time": processing_time,
            "backup_path": backup_path,
            "ocr_results": len(ocr_results_map),
        }
        return result
