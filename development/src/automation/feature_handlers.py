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
from typing import Optional, Dict, Any
import sys

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import utility classes for REFACTOR phase
from .feature_handler_utils import (
    ScreenshotProcessorIntegrator,
    SmartLinkEngineIntegrator,
    ProcessingMetricsTracker,
    ErrorHandlingStrategy
)


class ScreenshotEventHandler:
    """
    Handles OneDrive screenshot events for evening workflow processing.
    
    Monitors for Samsung Galaxy S23 screenshots synced via OneDrive and
    triggers OCR processing and daily note generation.
    
    Size: ~80 LOC (ADR-001 compliant)
    """
    
    def __init__(self, onedrive_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize screenshot handler.
        
        Args:
            onedrive_path: Path to OneDrive screenshot directory (backward compatibility)
            config: Configuration dictionary (priority: config > positional > defaults)
                Keys: onedrive_path, knowledge_path, ocr_enabled, processing_timeout
        """
        # Configuration priority: config dict > positional arg > defaults
        if config:
            # Validate required config key
            if 'onedrive_path' not in config:
                raise ValueError("onedrive_path is required in configuration")
            
            self.onedrive_path = Path(config['onedrive_path'])
            self.knowledge_path = Path(config.get('knowledge_path', Path.cwd() / 'knowledge'))
            self.ocr_enabled = config.get('ocr_enabled', True)
            self.processing_timeout = config.get('processing_timeout', 600)
        elif onedrive_path:
            # Backward compatibility: positional argument
            self.onedrive_path = Path(onedrive_path)
            self.knowledge_path = Path.cwd() / 'knowledge'
            self.ocr_enabled = True
            self.processing_timeout = 600
        else:
            raise ValueError("Must provide either onedrive_path or config dictionary")
        
        self._setup_logging()
        self.logger.info(f"Initialized ScreenshotEventHandler: {self.onedrive_path}")
        
        # Initialize REFACTOR: Use utility classes
        self.processor_integrator = ScreenshotProcessorIntegrator(
            self.onedrive_path, 
            self.logger,
            ocr_enabled=self.ocr_enabled,
            processing_timeout=self.processing_timeout
        )
        self.metrics_tracker = ProcessingMetricsTracker()
    
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
        
        # Track processing time
        start_time = time.time()
        
        try:
            # REFACTOR: Use ScreenshotProcessorIntegrator utility
            result = self.processor_integrator.process_screenshot(file_path)
            
            if result['success']:
                self.metrics_tracker.record_success(
                    filename=file_path.name,
                    handler_type='screenshot',
                    ocr_success=bool(result.get('ocr_results'))
                )
            elif result.get('fallback'):
                # Service unavailable - graceful degradation
                ErrorHandlingStrategy.handle_service_unavailable(
                    self.logger, 'ScreenshotProcessor', file_path.name
                )
                self.metrics_tracker.record_success(file_path.name, 'screenshot')
            else:
                # Processing error
                error_msg = result.get('error', 'Unknown error')
                ErrorHandlingStrategy.handle_processing_error(
                    self.logger, Exception(error_msg), file_path.name
                )
                self.metrics_tracker.record_failure()
            
        except Exception as e:
            ErrorHandlingStrategy.handle_processing_error(self.logger, e, file_path.name)
            self.metrics_tracker.record_failure()
        finally:
            # Record processing time regardless of success/failure
            duration = time.time() - start_time
            self.metrics_tracker.record_processing_time(duration, threshold=self.processing_timeout)
            
            # Log warning if processing exceeded threshold
            if duration > self.processing_timeout:
                self.logger.warning(
                    f"Processing time {duration:.1f}s exceeded threshold {self.processing_timeout}s for {file_path.name}"
                )
    
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
        # REFACTOR: Use ProcessingMetricsTracker
        return self.metrics_tracker.get_metrics()
    
    def get_health(self) -> dict:
        """
        Get handler health status for daemon monitoring.
        
        Returns:
            Dictionary with health status information
        """
        # REFACTOR: Use ProcessingMetricsTracker for error rate calculation
        metrics = self.metrics_tracker.get_metrics()
        error_rate = self.metrics_tracker.get_error_rate()
        
        # Determine health status based on error rate
        if metrics['events_processed'] + metrics['events_failed'] == 0:
            status = 'healthy'
        elif error_rate > 0.5:
            status = 'unhealthy'
        elif error_rate > 0.2:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_processed': metrics['last_processed'],
            'error_rate': error_rate
        }
    
    def export_metrics(self) -> str:
        """
        Export handler metrics in JSON format.
        
        Returns:
            JSON string with handler metrics including performance data
        """
        import json
        metrics = self.metrics_tracker.export_metrics_json()
        metrics_dict = json.loads(metrics)
        
        # Add handler-specific context
        metrics_dict['handler_type'] = 'screenshot'
        metrics_dict['performance_threshold'] = self.processing_timeout
        metrics_dict['threshold_violations'] = metrics_dict.get('slow_processing_events', 0)
        metrics_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return json.dumps(metrics_dict, indent=2)
    
    def get_health_status(self) -> dict:
        """
        Get comprehensive health status including performance metrics.
        
        Returns:
            Dictionary with health status and performance information
        """
        metrics = self.metrics_tracker.get_metrics()
        error_rate = self.metrics_tracker.get_error_rate()
        avg_time = self.metrics_tracker.get_average_processing_time()
        
        # Check for performance degradation
        performance_degraded = (
            metrics.get('slow_processing_events', 0) > 0 or
            avg_time > self.processing_timeout
        )
        
        # Determine overall status
        if metrics['events_processed'] + metrics['events_failed'] == 0:
            status = 'healthy'
        elif error_rate > 0.5 or performance_degraded:
            status = 'degraded'
        elif error_rate > 0.2:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_processed': metrics['last_processed'],
            'error_rate': error_rate,
            'avg_processing_time': avg_time,
            'performance_degraded': performance_degraded
        }


class SmartLinkEventHandler:
    """
    Handles automatic link suggestion and insertion for notes.
    
    Monitors note changes and triggers smart link discovery and insertion
    based on semantic similarity and connection strength.
    
    Size: ~80 LOC (ADR-001 compliant)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize smart link handler.
        
        Args:
            vault_path: Path to Zettelkasten vault root (backward compatibility)
            config: Configuration dictionary (priority: config > positional > defaults)
                Keys: vault_path, similarity_threshold, max_suggestions, auto_insert
        """
        # Configuration priority: config dict > positional arg > defaults
        if config:
            self.vault_path = Path(config.get('vault_path', Path.cwd()))
            self.similarity_threshold = config.get('similarity_threshold', 0.75)
            self.max_suggestions = config.get('max_suggestions', 5)
            self.auto_insert = config.get('auto_insert', False)
            
            # Validate similarity_threshold range
            if not (0.0 <= self.similarity_threshold <= 1.0):
                raise ValueError(f"similarity_threshold must be between 0.0 and 1.0, got {self.similarity_threshold}")
        elif vault_path:
            # Backward compatibility: positional argument
            self.vault_path = Path(vault_path)
            self.similarity_threshold = 0.75
            self.max_suggestions = 5
            self.auto_insert = False
        else:
            # Default to current working directory
            self.vault_path = Path.cwd()
            self.similarity_threshold = 0.75
            self.max_suggestions = 5
            self.auto_insert = False
        
        self._setup_logging()
        self.logger.info(f"Initialized SmartLinkEventHandler: {self.vault_path}")
        
        # Initialize REFACTOR: Use utility classes
        self.link_integrator = SmartLinkEngineIntegrator(self.vault_path, self.logger)
        self.metrics_tracker = ProcessingMetricsTracker()
    
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
        
        # Track processing time
        start_time = time.time()
        
        try:
            # REFACTOR: Use SmartLinkEngineIntegrator utility
            result = self.link_integrator.process_note_for_links(file_path)
            
            if result['success']:
                self.metrics_tracker.record_success(
                    filename=file_path.name,
                    handler_type='smart_link',
                    suggestions_count=result['suggestions_count']
                )
            elif result.get('fallback'):
                # Service unavailable - graceful degradation
                ErrorHandlingStrategy.handle_service_unavailable(
                    self.logger, 'AIConnections', file_path.name
                )
                self.metrics_tracker.record_success(file_path.name, 'smart_link', suggestions_count=0)
            else:
                # Processing error
                error_msg = result.get('error', 'Unknown error')
                ErrorHandlingStrategy.handle_processing_error(
                    self.logger, Exception(error_msg), file_path.name
                )
                self.metrics_tracker.record_failure()
            
        except Exception as e:
            ErrorHandlingStrategy.handle_processing_error(self.logger, e, file_path.name)
            self.metrics_tracker.record_failure()
        finally:
            # Record processing time regardless of success/failure
            duration = time.time() - start_time
            threshold = 5.0  # 5 second threshold for link suggestions
            self.metrics_tracker.record_processing_time(duration, threshold=threshold)
            
            # Log warning if processing exceeded threshold
            if duration > threshold:
                self.logger.warning(
                    f"Processing time {duration:.1f}s exceeded threshold {threshold}s for {file_path.name}"
                )
    
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
        # REFACTOR: Use ProcessingMetricsTracker
        return self.metrics_tracker.get_metrics()
    
    def get_health(self) -> dict:
        """
        Get handler health status for daemon monitoring.
        
        Returns:
            Dictionary with health status information
        """
        # REFACTOR: Use ProcessingMetricsTracker for error rate calculation
        metrics = self.metrics_tracker.get_metrics()
        error_rate = self.metrics_tracker.get_error_rate()
        
        # Determine health status based on error rate
        if metrics['events_processed'] + metrics['events_failed'] == 0:
            status = 'healthy'
        elif error_rate > 0.5:
            status = 'unhealthy'
        elif error_rate > 0.2:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_processed': metrics['last_processed'],
            'error_rate': error_rate
        }
    
    def export_metrics(self) -> str:
        """
        Export handler metrics in JSON format.
        
        Returns:
            JSON string with handler metrics including performance data
        """
        import json
        metrics = self.metrics_tracker.export_metrics_json()
        metrics_dict = json.loads(metrics)
        
        # Add handler-specific context
        metrics_dict['handler_type'] = 'smart_link'
        metrics_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return json.dumps(metrics_dict, indent=2)
