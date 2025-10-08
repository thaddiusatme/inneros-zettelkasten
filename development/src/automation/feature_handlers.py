"""
Feature-Specific Event Handlers - Screenshot and Smart Link processing

Provides specialized event handlers for feature-specific automation:
- ScreenshotEventHandler: OneDrive screenshot processing
- SmartLinkEventHandler: Automatic link suggestion and insertion

These handlers integrate with FileWatcher callbacks and can be registered
with the AutomationDaemon for event-driven feature automation.

Size: ~180 LOC (ADR-001 compliant: <500 LOC)
"""

import logging
import time
from pathlib import Path


class ScreenshotEventHandler:
    """
    Handles OneDrive screenshot events for evening workflow processing.
    
    Monitors for Samsung Galaxy S23 screenshots synced via OneDrive and
    triggers OCR processing and daily note generation.
    
    Size: ~80 LOC (ADR-001 compliant)
    """
    
    def __init__(self, onedrive_path: str):
        """
        Initialize screenshot handler.
        
        Args:
            onedrive_path: Path to OneDrive screenshot directory
        """
        self.onedrive_path = Path(onedrive_path)
        self._setup_logging()
        self.logger.info(f"Initialized ScreenshotEventHandler: {onedrive_path}")
        
        # Initialize metrics tracking
        self._events_processed = 0
        self._events_failed = 0
        self._last_processed = None
    
    def process(self, file_path: Path, event_type: str) -> None:
        """
        Process screenshot file events.
        
        FileWatcher callback signature: (file_path: Path, event_type: str) -> None
        
        Args:
            file_path: Path to screenshot file
            event_type: Event type ('created', 'modified', 'deleted')
        """
        # Filter for screenshot files only
        if not self._is_screenshot(file_path):
            return
        
        # Only process creation events
        if event_type != 'created':
            return
        
        self.logger.info(f"Processing screenshot: {file_path.name}")
        
        try:
            # TODO: Integrate with EveningScreenshotProcessor
            # For now, just log the event
            self.logger.info(f"Screenshot processed: {file_path.name}")
            self._events_processed += 1
            self._last_processed = file_path.name
            
        except Exception as e:
            self._events_failed += 1
            self.logger.error(f"Failed to process screenshot {file_path.name}: {e}", exc_info=True)
    
    def _is_screenshot(self, file_path: Path) -> bool:
        """
        Check if file is a Samsung screenshot.
        
        Samsung Galaxy S23 screenshot naming pattern:
        - Screenshot_YYYYMMDD-HHmmss_*.jpg
        - Screenshot_YYYYMMDD_HHmmss.png
        """
        name = file_path.name
        return (
            name.startswith('Screenshot_') and
            file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']
        )
    
    def _setup_logging(self) -> None:
        """Setup logging for screenshot handler."""
        log_dir = Path('.automation/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'screenshot_handler_{time.strftime("%Y-%m-%d")}.log'
        
        self.logger = logging.getLogger(f"{__name__}.ScreenshotEventHandler")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
    
    def get_metrics(self) -> dict:
        """
        Get handler metrics for monitoring.
        
        Returns:
            Dictionary with processing metrics
        """
        return {
            'events_processed': self._events_processed,
            'events_failed': self._events_failed,
            'last_processed': self._last_processed
        }
    
    def get_health(self) -> dict:
        """
        Get handler health status for daemon monitoring.
        
        Returns:
            Dictionary with health status information
        """
        # Determine health status based on error rate
        total_events = self._events_processed + self._events_failed
        if total_events == 0:
            status = 'healthy'
        elif self._events_failed / total_events > 0.5:
            status = 'unhealthy'
        elif self._events_failed / total_events > 0.2:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_processed': self._last_processed,
            'error_rate': self._events_failed / total_events if total_events > 0 else 0.0
        }


class SmartLinkEventHandler:
    """
    Handles automatic link suggestion and insertion for notes.
    
    Monitors note changes and triggers smart link discovery and insertion
    based on semantic similarity and connection strength.
    
    Size: ~80 LOC (ADR-001 compliant)
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize smart link handler.
        
        Args:
            vault_path: Path to Zettelkasten vault root
        """
        self.vault_path = Path(vault_path)
        self._setup_logging()
        self.logger.info(f"Initialized SmartLinkEventHandler: {vault_path}")
        
        # Initialize metrics tracking
        self._events_processed = 0
        self._events_failed = 0
        self._links_suggested = 0
        self._links_inserted = 0
        self._last_processed = None
    
    def process(self, file_path: Path, event_type: str) -> None:
        """
        Process note file events for smart linking.
        
        FileWatcher callback signature: (file_path: Path, event_type: str) -> None
        
        Args:
            file_path: Path to note file
            event_type: Event type ('created', 'modified', 'deleted')
        """
        # Only process markdown files
        if not str(file_path).endswith('.md'):
            return
        
        # Skip deleted events
        if event_type == 'deleted':
            return
        
        self.logger.info(f"Processing smart links for: {file_path.name}")
        
        try:
            # TODO: Integrate with LinkSuggestionEngine and LinkInsertionEngine
            # For now, just log the event
            self.logger.info(f"Smart link analysis complete: {file_path.name}")
            self._events_processed += 1
            self._last_processed = file_path.name
            
        except Exception as e:
            self._events_failed += 1
            self.logger.error(f"Failed smart link processing for {file_path.name}: {e}", exc_info=True)
    
    def _setup_logging(self) -> None:
        """Setup logging for smart link handler."""
        log_dir = Path('.automation/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'smart_link_handler_{time.strftime("%Y-%m-%d")}.log'
        
        self.logger = logging.getLogger(f"{__name__}.SmartLinkEventHandler")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
    
    def get_metrics(self) -> dict:
        """
        Get handler metrics for monitoring.
        
        Returns:
            Dictionary with link processing metrics
        """
        return {
            'events_processed': self._events_processed,
            'events_failed': self._events_failed,
            'links_suggested': self._links_suggested,
            'links_inserted': self._links_inserted,
            'last_processed': self._last_processed
        }
    
    def get_health(self) -> dict:
        """
        Get handler health status for daemon monitoring.
        
        Returns:
            Dictionary with health status information
        """
        # Determine health status based on error rate
        total_events = self._events_processed + self._events_failed
        if total_events == 0:
            status = 'healthy'
        elif self._events_failed / total_events > 0.5:
            status = 'unhealthy'
        elif self._events_failed / total_events > 0.2:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_processed': self._last_processed,
            'error_rate': self._events_failed / total_events if total_events > 0 else 0.0
        }
