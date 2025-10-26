"""
Feature Handler Utilities - REFACTOR Phase

Extracted utility classes for feature handler processing:
- ScreenshotProcessorIntegrator: Manages ScreenshotProcessor integration
- SmartLinkEngineIntegrator: Manages LinkSuggestionEngine + AIConnections integration
- ProcessingMetricsTracker: Enhanced metrics tracking for real processing
- ErrorHandlingStrategy: Graceful degradation and fallback strategies

Following ADR-001: Keep utilities modular and focused (each <200 LOC)
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import deque
import logging

try:
    from src.cli.screenshot_processor import ScreenshotProcessor
except ImportError:
    ScreenshotProcessor = None

try:
    from src.ai.link_suggestion_engine import LinkSuggestionEngine
    from src.ai.connections import AIConnections
except ImportError:
    LinkSuggestionEngine = None
    AIConnections = None


class ScreenshotProcessorIntegrator:
    """
    Manages integration between ScreenshotEventHandler and ScreenshotProcessor.
    
    Responsibilities:
    - Initialize ScreenshotProcessor with correct paths
    - Process screenshots with OCR
    - Handle OCR service unavailability gracefully
    - Track processing metrics
    
    Size: ~60 LOC (ADR-001 compliant)
    """

    def __init__(self, onedrive_path: Path, logger: logging.Logger,
                 ocr_enabled: bool = True, processing_timeout: int = 600):
        """
        Initialize screenshot processor integrator.
        
        Args:
            onedrive_path: Path to OneDrive screenshot directory
            logger: Logger instance for processing events
            ocr_enabled: Whether OCR processing is enabled
            processing_timeout: Maximum processing time in seconds
        """
        self.onedrive_path = onedrive_path
        self.logger = logger
        self.ocr_enabled = ocr_enabled
        self.processing_timeout = processing_timeout
        self.processor = None

    def process_screenshot(self, file_path: Path) -> Dict[str, Any]:
        """
        Process screenshot with OCR integration.
        
        Args:
            file_path: Path to screenshot file
            
        Returns:
            Dictionary with processing results:
            - success: bool
            - ocr_results: dict (if available)
            - error: str (if failed)
        """
        if not ScreenshotProcessor:
            self.logger.warning("ScreenshotProcessor not available - graceful fallback")
            return {
                'success': False,
                'error': 'ScreenshotProcessor not available',
                'fallback': True
            }

        try:
            # Initialize processor (lazy initialization for performance)
            if not self.processor:
                knowledge_path = self.onedrive_path.parent if self.onedrive_path.parent else Path.cwd()
                self.processor = ScreenshotProcessor(
                    onedrive_path=str(self.onedrive_path),
                    knowledge_path=str(knowledge_path)
                )

            # Process with OCR
            ocr_results = self.processor.process_screenshots_with_ocr([file_path])

            if ocr_results:
                self.logger.info(f"Screenshot processed with OCR: {file_path.name}")
                return {
                    'success': True,
                    'ocr_results': ocr_results,
                    'screenshot_count': len(ocr_results)
                }
            else:
                self.logger.warning(f"Screenshot processed but no OCR results: {file_path.name}")
                return {
                    'success': True,
                    'ocr_results': {},
                    'screenshot_count': 0
                }

        except Exception as e:
            self.logger.error(f"OCR processing failed for {file_path.name}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


class SmartLinkEngineIntegrator:
    """
    Manages integration between SmartLinkEventHandler and AI link engines.
    
    Responsibilities:
    - Initialize AIConnections for semantic analysis
    - Find similar notes and generate suggestions
    - Handle AI service unavailability gracefully
    - Track suggestion metrics
    
    Size: ~80 LOC (ADR-001 compliant)
    """

    def __init__(self, vault_path: Path, logger: logging.Logger,
                 similarity_threshold: float = 0.75, max_suggestions: int = 5):
        """
        Initialize smart link engine integrator.
        
        Args:
            vault_path: Path to knowledge vault root
            logger: Logger instance for processing events
            similarity_threshold: Minimum similarity score for suggestions
            max_suggestions: Maximum number of suggestions to return
        """
        self.vault_path = vault_path
        self.logger = logger
        self.similarity_threshold = similarity_threshold
        self.max_suggestions = max_suggestions
        self.ai_connections = None

    def process_note_for_links(self, file_path: Path) -> Dict[str, Any]:
        """
        Process note file for smart link suggestions.
        
        Args:
            file_path: Path to note file
            
        Returns:
            Dictionary with processing results:
            - success: bool
            - suggestions_count: int
            - similar_notes: list (if available)
            - error: str (if failed)
        """
        if not AIConnections:
            self.logger.warning("AIConnections not available - graceful fallback")
            return {
                'success': False,
                'error': 'AIConnections not available',
                'fallback': True,
                'suggestions_count': 0
            }

        if not file_path.exists():
            self.logger.error(f"Note file does not exist: {file_path}")
            return {
                'success': False,
                'error': 'File does not exist',
                'suggestions_count': 0
            }

        try:
            # Initialize AI connections (lazy initialization)
            if not self.ai_connections:
                self.ai_connections = AIConnections(
                    similarity_threshold=self.similarity_threshold,
                    max_suggestions=self.max_suggestions
                )

            # Read note content
            note_content = file_path.read_text(encoding='utf-8')

            # Find similar notes
            # Note: In GREEN phase, we use empty corpus for minimal implementation
            # P1 enhancement: Build full vault corpus for real similarity analysis
            similar_notes = self.ai_connections.find_similar_notes(
                target_note=note_content,
                note_corpus={}  # Empty corpus for minimal GREEN implementation
            )

            suggestions_count = len(similar_notes)

            self.logger.info(f"Smart link analysis complete: {file_path.name} ({suggestions_count} suggestions)")
            return {
                'success': True,
                'suggestions_count': suggestions_count,
                'similar_notes': similar_notes
            }

        except Exception as e:
            self.logger.error(f"Smart link processing failed for {file_path.name}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'suggestions_count': 0
            }


class ProcessingMetricsTracker:
    """
    Enhanced metrics tracking for real processing integration.
    
    Tracks:
    - Processing success/failure rates
    - OCR-specific metrics (for screenshot handler)
    - Link suggestion metrics (for smart link handler)
    - Performance timing (P1 enhancement)
    
    Size: ~40 LOC (ADR-001 compliant)
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize metrics tracker.
        
        Args:
            window_size: Number of recent processing times to retain (rolling window)
        """
        self.window_size = window_size
        self.processing_times_deque = deque(maxlen=window_size)

        self.metrics = {
            'events_processed': 0,
            'events_failed': 0,
            'last_processed': None,
            # Handler-specific metrics
            'ocr_success': 0,
            'ocr_failed': 0,
            'links_suggested': 0,
            'links_inserted': 0,
            # Performance timing metrics
            'processing_times': [],  # Kept for backward compatibility
            'total_processing_time': 0.0,
            'slow_processing_events': 0
        }

    def record_success(self, filename: str, handler_type: str = 'generic', **kwargs):
        """
        Record successful processing event.
        
        Args:
            filename: Name of processed file
            handler_type: Type of handler ('screenshot', 'smart_link')
            **kwargs: Additional metrics to record
        """
        self.metrics['events_processed'] += 1
        self.metrics['last_processed'] = filename

        # Handler-specific tracking
        if handler_type == 'screenshot' and kwargs.get('ocr_success'):
            self.metrics['ocr_success'] += 1
        elif handler_type == 'smart_link' and 'suggestions_count' in kwargs:
            self.metrics['links_suggested'] += kwargs['suggestions_count']

    def record_failure(self):
        """Record failed processing event."""
        self.metrics['events_failed'] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()

    def get_error_rate(self) -> float:
        """Calculate error rate."""
        total = self.metrics['events_processed'] + self.metrics['events_failed']
        return self.metrics['events_failed'] / total if total > 0 else 0.0

    def record_processing_time(self, duration: float, threshold: Optional[float] = None) -> None:
        """
        Record processing time for performance monitoring.
        
        Args:
            duration: Processing duration in seconds
            threshold: Optional performance threshold for slow event detection
        """
        self.processing_times_deque.append(duration)
        self.metrics['processing_times'] = list(self.processing_times_deque)
        self.metrics['total_processing_time'] += duration

        # Track slow processing events if threshold provided
        if threshold and duration > threshold:
            self.metrics['slow_processing_events'] += 1

    def get_average_processing_time(self) -> float:
        """
        Calculate average processing time.
        
        Returns:
            Average processing time in seconds (0.0 if no data)
        """
        if not self.processing_times_deque:
            return 0.0
        return sum(self.processing_times_deque) / len(self.processing_times_deque)

    def get_max_processing_time(self) -> float:
        """
        Get maximum processing time from rolling window.
        
        Returns:
            Maximum processing time in seconds (0.0 if no data)
        """
        if not self.processing_times_deque:
            return 0.0
        return max(self.processing_times_deque)

    def get_processing_times(self) -> List[float]:
        """
        Get list of processing times in rolling window.
        
        Returns:
            List of processing times (oldest to newest)
        """
        return list(self.processing_times_deque)

    def export_metrics_json(self) -> str:
        """
        Export metrics as JSON string for reporting.
        
        Returns:
            JSON string representation of metrics
        """
        import json
        export_data = self.metrics.copy()

        # Use 'avg_processing_time' key for consistency with other metrics systems
        export_data['avg_processing_time'] = self.get_average_processing_time()
        export_data['max_processing_time'] = self.get_max_processing_time()
        export_data['total_events'] = self.metrics['events_processed'] + self.metrics['events_failed']

        # Calculate success rate
        total = export_data['total_events']
        export_data['success_rate'] = (self.metrics['events_processed'] / total) if total > 0 else 0.0

        return json.dumps(export_data, indent=2)

    def export_prometheus_format(self) -> str:
        """
        Export metrics in Prometheus-compatible format.
        
        Returns:
            String in Prometheus exposition format
        """
        lines = []

        # Processing time metrics
        avg_time = self.get_average_processing_time()
        max_time = self.get_max_processing_time()

        lines.append("# HELP inneros_handler_processing_seconds Average processing time in seconds")
        lines.append("# TYPE inneros_handler_processing_seconds gauge")
        lines.append(f"inneros_handler_processing_seconds {avg_time:.4f}")
        lines.append("")

        lines.append("# HELP inneros_handler_processing_seconds_max Maximum processing time in seconds")
        lines.append("# TYPE inneros_handler_processing_seconds_max gauge")
        lines.append(f"inneros_handler_processing_seconds_max {max_time:.4f}")
        lines.append("")

        # Event counters
        total_events = self.metrics['events_processed'] + self.metrics['events_failed']
        lines.append("# HELP inneros_handler_events_total Total number of events processed")
        lines.append("# TYPE inneros_handler_events_total counter")
        lines.append(f"inneros_handler_events_total {total_events}")
        lines.append("")

        # Success rate
        success_rate = (self.metrics['events_processed'] / total_events) if total_events > 0 else 0.0
        lines.append("# HELP inneros_handler_success_rate Ratio of successful events")
        lines.append("# TYPE inneros_handler_success_rate gauge")
        lines.append(f"inneros_handler_success_rate {success_rate:.4f}")

        return "\n".join(lines)


class ErrorHandlingStrategy:
    """
    Graceful degradation and fallback strategies for handler errors.
    
    Strategies:
    - Service unavailable: Log warning, continue without processing
    - Processing error: Log error, increment failure metrics
    - Configuration error: Provide user-friendly guidance
    
    Size: ~30 LOC (ADR-001 compliant)
    """

    @staticmethod
    def handle_service_unavailable(logger: logging.Logger, service_name: str, filename: str) -> None:
        """
        Handle service unavailability gracefully.
        
        Args:
            logger: Logger instance
            service_name: Name of unavailable service
            filename: File being processed
        """
        logger.warning(
            f"{service_name} unavailable for {filename} - continuing without processing. "
            f"Ensure {service_name} is installed and configured."
        )

    @staticmethod
    def handle_processing_error(logger: logging.Logger, error: Exception, filename: str) -> None:
        """
        Handle processing errors with detailed logging.
        
        Args:
            logger: Logger instance
            error: Exception that occurred
            filename: File being processed
        """
        logger.error(
            f"Processing failed for {filename}: {error}",
            exc_info=True,
            extra={
                'target_file': filename,
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        )
