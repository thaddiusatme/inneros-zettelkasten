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


class YouTubeFeatureHandler:
    """
    Handles automatic quote extraction for YouTube video notes.
    
    Monitors for YouTube notes (source: youtube) and triggers AI-powered
    quote extraction using YouTubeNoteEnhancer while preserving user content.
    
    Size: ~150 LOC (ADR-001 compliant)
    """

    # Regex pattern for extracting video_id from body content
    VIDEO_ID_BODY_PATTERN = r'Video ID[*:\s]+`?([a-zA-Z0-9_-]+)`?'

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize YouTube handler.
        
        Args:
            config: Configuration dictionary
                Required keys: vault_path
                Optional keys: max_quotes, min_quality, processing_timeout, cooldown_seconds
        
        Raises:
            ValueError: If vault_path is missing
        """
        if not config:
            raise ValueError("Configuration dictionary is required")

        if 'vault_path' not in config:
            raise ValueError("vault_path is required in configuration")

        self.vault_path = Path(config['vault_path'])
        self.max_quotes = config.get('max_quotes', 7)
        self.min_quality = config.get('min_quality', 0.7)
        self.processing_timeout = config.get('processing_timeout', 300)

        # CATASTROPHIC INCIDENT FIX: Cooldown to prevent file watching loops
        self.cooldown_seconds = config.get('cooldown_seconds', 60)  # Default: 60 seconds
        self._last_processed = {}  # Track last processing time per file
        self._processing_files = set()  # Track currently processing files

        self._setup_logging()
        self.logger.info(f"Initialized YouTubeFeatureHandler: {self.vault_path}")
        self.logger.info(f"Cooldown enabled: {self.cooldown_seconds}s (prevents file watching loops)")

        # CATASTROPHIC INCIDENT FIX: Transcript caching to prevent redundant API calls
        from src.automation.transcript_cache import TranscriptCache
        cache_dir = Path.cwd() / '.automation' / 'cache'

        # Get TTL from config (default: 7 days for safety in distribution)
        # Personal use: Set to 36500 (100 years) in daemon_config.yaml
        ttl_days = config.get('transcript_cache', {}).get('ttl_days', 7)
        self.transcript_cache = TranscriptCache(cache_dir=cache_dir, ttl_days=ttl_days)
        cache_stats = self.transcript_cache.get_stats()
        self.logger.info(
            f"Transcript cache initialized: {cache_stats['entries']} cached transcripts "
            f"(TTL: {ttl_days} days)"
        )

        # Initialize metrics tracker
        self.metrics_tracker = ProcessingMetricsTracker()

        # Initialize rate limit handler if configured
        if 'rate_limit' in config:
            from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
            self.rate_limit_handler = YouTubeRateLimitHandler(config['rate_limit'])
            self.logger.info("Rate limit handler initialized with exponential backoff")
        else:
            self.rate_limit_handler = None

        # Phase 2: Initialize transcript saver for automatic archival
        from src.ai.youtube_transcript_saver import YouTubeTranscriptSaver
        self.transcript_saver = YouTubeTranscriptSaver(self.vault_path)
        self.logger.info("Transcript saver initialized for automatic archival")

    def _is_ready_for_processing(self, frontmatter: dict) -> tuple[bool, str]:
        """
        Check if note has user approval for processing.
        
        Handles various edge cases for user-friendly template compatibility:
        - Boolean true: ready_for_processing: true ✅
        - String "true": ready_for_processing: "true" ✅
        - String "yes": ready_for_processing: "yes" ✅
        - Numeric 1: ready_for_processing: 1 ✅
        - Boolean false: ready_for_processing: false ❌
        - Missing field: (no ready_for_processing) ❌
        - Any other value: ready_for_processing: "pending" ❌
        
        Args:
            frontmatter: Parsed YAML frontmatter dictionary
        
        Returns:
            Tuple of (is_ready: bool, reason: str) for diagnostic logging
            
        Examples:
            >>> self._is_ready_for_processing({'ready_for_processing': True})
            (True, 'approved')
            
            >>> self._is_ready_for_processing({'ready_for_processing': 'true'})
            (True, 'approved (string value)')
            
            >>> self._is_ready_for_processing({'ready_for_processing': False})
            (False, 'explicitly set to false')
            
            >>> self._is_ready_for_processing({'source': 'youtube'})
            (False, 'field missing')
        """
        if 'ready_for_processing' not in frontmatter:
            return (False, 'field missing')

        value = frontmatter['ready_for_processing']

        # Handle boolean True
        if value is True:
            return (True, 'approved')

        # Handle string representations of true (case-insensitive)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ('true', 'yes', 'y', '1'):
                return (True, 'approved (string value)')
            return (False, f'unsupported string value: "{value}"')

        # Handle numeric 1
        if isinstance(value, (int, float)) and value == 1:
            return (True, 'approved (numeric value)')

        # Handle explicit false
        if value is False:
            return (False, 'explicitly set to false')

        # All other cases
        return (False, f'unsupported value type: {type(value).__name__} = {value}')

    def can_handle(self, event) -> bool:
        """
        Check if this handler can process the given event.
        
        Criteria:
        - File must have 'source: youtube' in frontmatter
        - File must have 'ready_for_processing: true' (user approval)
        - File must NOT have 'ai_processed: true'
        - Frontmatter must be valid YAML
        
        Args:
            event: File system event with src_path attribute
        
        Returns:
            True if handler should process this event, False otherwise
        """
        try:
            file_path = Path(event.src_path)

            # Only process markdown files
            if not str(file_path).endswith('.md'):
                return False

            # Check if file exists
            if not file_path.exists():
                return False

            # Read and parse frontmatter
            content = file_path.read_text(encoding='utf-8')

            # Import parse_frontmatter for YAML parsing
            from src.utils.frontmatter import parse_frontmatter

            try:
                frontmatter, _ = parse_frontmatter(content)
            except Exception as e:
                self.logger.debug(f"Failed to parse frontmatter for {file_path.name}: {e}")
                return False

            # Check for source: youtube
            if frontmatter.get('source') != 'youtube':
                return False

            # OPTIMIZATION: Check approval BEFORE ai_processed (fail fast for drafts)
            # Most notes will be drafts, so check this first to avoid unnecessary processing
            is_ready, reason = self._is_ready_for_processing(frontmatter)
            if not is_ready:
                self.logger.debug(
                    f"Skipping note awaiting approval: {file_path.name} "
                    f"(ready_for_processing: {reason})"
                )
                return False

            # Check if already processed (only after confirming user approval)
            if frontmatter.get('ai_processed') is True:
                self.logger.debug(f"Skipping already processed note: {file_path.name}")
                return False

            # All checks passed - ready for processing
            self.logger.debug(
                f"YouTube note approved for processing: {file_path.name} "
                f"(approval: {reason})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error in can_handle for {event.src_path}: {e}")
            return False

    def handle(self, event) -> Dict[str, Any]:
        """
        Process YouTube note with AI quote extraction and status synchronization.
        
        State Machine (PBI-003):
            draft (ready_for_processing: false)
              ↓ [user checks checkbox]
            draft (ready_for_processing: true)
              ↓ [handle() starts]
            processing (ready_for_processing: true, processing_started_at)
              ↓ [handle() completes successfully]
            processed (ready_for_processing: true, processing_completed_at, ai_processed: true)
              ↓ [handle() fails]
            processing (ready_for_processing: true) [remains for retry detection]
        
        Workflow:
        1. Update status to 'processing' with timestamp
        2. Read video_id from frontmatter
        3. Fetch transcript using YouTubeTranscriptFetcher
        4. Extract quotes using ContextAwareQuoteExtractor
        5. Use YouTubeNoteEnhancer to insert quotes (preserving user content)
        6. Update status to 'processed' with completion timestamp and ai_processed flag
        
        Args:
            event: File system event
        
        Returns:
            Dict with processing results:
                - success: bool
                - quotes_added: int (if successful)
                - processing_time: float
                - error: str (if failed)
        """
        file_path = Path(event.src_path)
        self.logger.info(f"Processing YouTube note: {file_path.name}")

        start_time = time.time()

        try:
            # Read note to get video_id
            content = file_path.read_text(encoding='utf-8')
            from src.utils.frontmatter import parse_frontmatter
            frontmatter, _ = parse_frontmatter(content)

            # PBI-003: Update status to 'processing' at start
            from datetime import datetime
            from src.ai.youtube_note_enhancer import YouTubeNoteEnhancer
            enhancer = YouTubeNoteEnhancer()

            content = self._update_processing_state(
                file_path=file_path,
                content=content,
                enhancer=enhancer,
                state='processing',
                metadata={'processing_started_at': datetime.now().isoformat()}
            )

            # Re-parse after status update
            frontmatter, _ = parse_frontmatter(content)

            video_id = frontmatter.get('video_id')
            if not video_id or video_id.strip() == '':
                # Fallback: Extract from body content
                video_id = self._extract_video_id_from_body(content)
                if video_id:
                    self.logger.info(f"Extracted video_id from body content: {video_id}")
                else:
                    raise ValueError("video_id not found in frontmatter or body")

            # 1. Fetch transcript
            transcript_result = self._fetch_transcript(video_id)

            # REFACTOR: Save transcript to archive BEFORE quote extraction
            transcript_file, transcript_wikilink = self._save_transcript_with_metadata(
                video_id=video_id,
                transcript_result=transcript_result,
                frontmatter=frontmatter,
                file_path=file_path
            )

            # Format for LLM
            from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
            fetcher = YouTubeTranscriptFetcher()
            llm_transcript = fetcher.format_for_llm(transcript_result["transcript"])

            # 2. Extract quotes with AI
            from src.ai.youtube_quote_extractor import ContextAwareQuoteExtractor
            extractor = ContextAwareQuoteExtractor()
            quotes_result = extractor.extract_quotes(
                transcript=llm_transcript,
                user_context=None,  # No user context for daemon processing
                max_quotes=self.max_quotes,
                min_quality=self.min_quality
            )

            # 3. Convert to QuotesData format (map 'text' -> 'quote' field)
            from src.ai.youtube_note_enhancer import QuotesData

            # Transform quote structure from extractor format to enhancer format
            transformed_quotes = [
                {
                    'quote': q.get('text', ''),
                    'timestamp': q.get('timestamp', '00:00'),
                    'context': q.get('context', ''),
                    'relevance': q.get('relevance_score', 0.0)
                }
                for q in quotes_result.get('quotes', [])
            ]

            quotes_data = QuotesData(
                key_insights=transformed_quotes,
                actionable=[],
                notable=[],
                definitions=[]
            )

            # 4. Use YouTubeNoteEnhancer to insert quotes
            # Note: enhancer already instantiated at start for status update
            result = enhancer.enhance_note(
                note_path=file_path,
                quotes_data=quotes_data,
                force=False
            )

            processing_time = time.time() - start_time

            if result.success:
                # PBI-003: Update status to 'processed' on success
                # Re-read to get latest content (after enhance_note modified it)
                final_content = file_path.read_text(encoding='utf-8')

                self._update_processing_state(
                    file_path=file_path,
                    content=final_content,
                    enhancer=enhancer,
                    state='processed',
                    metadata={
                        'processing_completed_at': datetime.now().isoformat(),
                        'ai_processed': True
                    }
                )

                # Record success metrics
                self.metrics_tracker.record_success(
                    filename=file_path.name,
                    handler_type='youtube',
                    quotes_added=result.quote_count
                )
                self.metrics_tracker.record_processing_time(processing_time, threshold=self.processing_timeout)

                self.logger.info(f"Successfully processed {file_path.name}: {result.quote_count} quotes added in {processing_time:.2f}s")

                # Phase 3: Add bidirectional transcript links to parent note
                transcript_link_added = False
                if transcript_wikilink:
                    transcript_link_added = self._add_transcript_links_to_note(
                        file_path=file_path,
                        transcript_wikilink=transcript_wikilink
                    )

                # Include transcript info and linking status in results
                return {
                    'success': True,
                    'quotes_added': result.quote_count,
                    'processing_time': processing_time,
                    'transcript_file': transcript_file,
                    'transcript_wikilink': transcript_wikilink,
                    'transcript_link_added': transcript_link_added
                }
            else:
                # Record failure
                self.metrics_tracker.record_failure()
                self.metrics_tracker.record_processing_time(processing_time, threshold=self.processing_timeout)

                error_msg = result.error_message or "Unknown error"
                self.logger.error(f"Failed to process {file_path.name}: {error_msg}")

                # Include transcript info even on failure for debugging
                return {
                    'success': False,
                    'error': error_msg,
                    'processing_time': processing_time,
                    'transcript_file': transcript_file,
                    'transcript_wikilink': transcript_wikilink
                }

        except Exception as e:
            processing_time = time.time() - start_time

            # Record failure
            self.metrics_tracker.record_failure()
            self.metrics_tracker.record_processing_time(processing_time, threshold=self.processing_timeout)

            error_msg = str(e)
            self.logger.error(f"Exception processing {file_path.name}: {error_msg}")

            # Even on exception, try to indicate if transcript was saved
            return {
                'success': False,
                'error': error_msg,
                'processing_time': processing_time,
                'transcript_file': None,
                'transcript_wikilink': None
            }

    def _update_processing_state(
        self,
        file_path: Path,
        content: str,
        enhancer: 'YouTubeNoteEnhancer',
        state: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Update note processing state with status transition tracking.
        
        PBI-003: Status Synchronization Helper
        
        This method centralizes status updates during YouTube note processing,
        ensuring consistent state transitions and comprehensive error handling.
        
        State transitions:
        - 'processing': Set at start with processing_started_at timestamp
        - 'processed': Set at completion with processing_completed_at and ai_processed
        
        Note: ready_for_processing field is NOT modified (preserved for manual reprocessing)
        
        Args:
            file_path: Path to the note file
            content: Current note content
            enhancer: YouTubeNoteEnhancer instance for frontmatter updates
            state: Target state ('processing' or 'processed')
            metadata: Additional metadata fields to update (timestamps, flags)
        
        Returns:
            Updated note content string
        
        Raises:
            IOError: If file write fails
            ValueError: If frontmatter update fails
        
        Example:
            >>> content = self._update_processing_state(
            ...     file_path=note_path,
            ...     content=current_content,
            ...     enhancer=enhancer,
            ...     state='processing',
            ...     metadata={'processing_started_at': datetime.now().isoformat()}
            ... )
        """
        try:
            # Prepare complete metadata with status
            full_metadata = {'status': state, **metadata}

            # Update frontmatter
            updated_content = enhancer.update_frontmatter(content, full_metadata)

            # Write to file
            file_path.write_text(updated_content, encoding='utf-8')

            # Log state transition
            self.logger.info(
                f"Status transition: {file_path.name} → {state} "
                f"(metadata: {', '.join(metadata.keys())})"
            )

            return updated_content

        except IOError as e:
            self.logger.error(
                f"Failed to write status update ({state}) to {file_path.name}: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to update frontmatter for {file_path.name}: {e}"
            )
            raise ValueError(f"Frontmatter update failed: {e}")

    def _save_transcript_with_metadata(
        self,
        video_id: str,
        transcript_result: Dict[str, Any],
        frontmatter: Dict[str, Any],
        file_path: Path
    ) -> tuple[Optional[Path], Optional[str]]:
        """
        REFACTOR: Helper method to save transcript with metadata preparation.
        
        Extracts metadata from frontmatter and transcript result, then saves
        transcript file. Gracefully handles failures to avoid blocking quote
        extraction workflow.
        
        Args:
            video_id: YouTube video ID
            transcript_result: Result dict from _fetch_transcript()
            frontmatter: Note frontmatter dict
            file_path: Path to parent note file
            
        Returns:
            Tuple of (transcript_file_path, transcript_wikilink) or (None, None) on failure
        """
        try:
            # Prepare metadata for transcript saver
            video_url = frontmatter.get('video_url', f"https://youtube.com/watch?v={video_id}")
            video_title = frontmatter.get('video_title', file_path.stem)
            duration = transcript_result.get('duration', 0.0)
            language = transcript_result.get('language', 'en')

            metadata = {
                'video_id': video_id,
                'video_url': video_url,
                'video_title': video_title,
                'duration': duration,
                'language': language
            }

            # Save transcript with parent note name for bidirectional linking
            parent_note_name = file_path.stem
            transcript_file = self.transcript_saver.save_transcript(
                video_id=video_id,
                transcript_data=transcript_result["transcript"],
                metadata=metadata,
                parent_note_name=parent_note_name
            )

            # Generate wikilink for result dict
            from datetime import datetime
            date_str = datetime.now().strftime("%Y-%m-%d")
            transcript_wikilink = f"[[youtube-{video_id}-{date_str}]]"

            self.logger.info(f"Transcript saved: {transcript_file}")
            return transcript_file, transcript_wikilink

        except Exception as e:
            # Log error but continue processing - transcript save shouldn't block quote extraction
            self.logger.warning(f"Failed to save transcript for {video_id}: {e}")
            return None, None

    def _add_transcript_links_to_note(
        self,
        file_path: Path,
        transcript_wikilink: str
    ) -> bool:
        """
        Add transcript links to parent note (Phase 3: Note Linking Integration).
        
        Updates both frontmatter and body with bidirectional transcript links:
        1. Adds transcript_file field to frontmatter
        2. Inserts transcript link in body after title
        
        This enables seamless bidirectional navigation between notes and transcripts
        in the knowledge graph.
        
        Args:
            file_path: Path to parent note file
            transcript_wikilink: Wikilink to transcript (e.g., [[youtube-{id}-{date}]])
            
        Returns:
            True if linking succeeded, False if it failed (non-blocking)
        """
        try:
            # Read note content
            content = file_path.read_text(encoding='utf-8')

            # Update frontmatter
            updated_content = self._update_note_frontmatter(
                content=content,
                transcript_wikilink=transcript_wikilink
            )

            # Insert body link
            updated_content = self._insert_transcript_link_in_body(
                content=updated_content,
                transcript_wikilink=transcript_wikilink
            )

            # Write updated content
            file_path.write_text(updated_content, encoding='utf-8')

            self.logger.info(f"Added transcript links to {file_path.name}")
            return True

        except Exception as e:
            # Log error but don't crash - quote insertion already succeeded
            self.logger.warning(f"Failed to add transcript links to {file_path.name}: {e}")
            return False

    def _update_note_frontmatter(
        self,
        content: str,
        transcript_wikilink: str
    ) -> str:
        """
        Update note frontmatter with transcript field.
        
        Adds transcript_file: [[youtube-{id}-{date}]] to frontmatter while
        preserving all existing fields and ordering. Uses centralized
        frontmatter utilities for YAML safety.
        
        Args:
            content: Original note content
            transcript_wikilink: Wikilink to transcript
            
        Returns:
            Updated content with modified frontmatter
        """
        from src.utils.frontmatter import parse_frontmatter, build_frontmatter

        # Parse existing frontmatter
        metadata, body = parse_frontmatter(content)

        # Add transcript field
        metadata['transcript_file'] = transcript_wikilink

        # Rebuild content
        return build_frontmatter(metadata, body)

    def _insert_transcript_link_in_body(
        self,
        content: str,
        transcript_wikilink: str
    ) -> str:
        """
        Insert transcript link in note body.
        
        Inserts "**Full Transcript**: [[youtube-{id}-{date}]]" after the first
        H1 heading (or at start of body if no heading found). This provides
        immediate visual access to the full transcript from the note.
        
        Args:
            content: Note content (with updated frontmatter)
            transcript_wikilink: Wikilink to transcript
            
        Returns:
            Updated content with transcript link in body
        """
        from src.utils.frontmatter import parse_frontmatter, build_frontmatter

        # Parse to separate frontmatter from body
        metadata, body = parse_frontmatter(content)

        # Create transcript link line
        transcript_line = f"\n**Full Transcript**: {transcript_wikilink}\n"

        # Find first heading
        lines = body.split('\n')
        insert_index = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                # Found heading - insert after it
                insert_index = i + 1
                break

        # Insert transcript link
        if insert_index == 0:
            # No heading found - insert at start
            updated_body = transcript_line + body
        else:
            # Insert after heading
            lines.insert(insert_index, transcript_line)
            updated_body = '\n'.join(lines)

        # Rebuild with frontmatter
        return build_frontmatter(metadata, updated_body)

    def _setup_logging(self) -> None:
        """Setup logging for YouTube handler."""
        log_dir = Path('.automation/logs')
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'youtube_handler_{time.strftime("%Y-%m-%d")}.log'

        self.logger = logging.getLogger(f"{__name__}.YouTubeFeatureHandler")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)

    def _extract_video_id_from_body(self, content: str) -> Optional[str]:
        """
        Extract video_id from note body content using regex pattern.
        
        Looks for patterns like:
        - **Video ID**: `IeVxir50Q2Q`
        - Video ID: IeVxir50Q2Q
        - **Video ID**: IeVxir50Q2Q
        
        Args:
            content: Full note content including frontmatter and body
        
        Returns:
            Extracted video_id or None if not found
        """
        import re
        match = re.search(self.VIDEO_ID_BODY_PATTERN, content)
        if match:
            return match.group(1)
        return None

    def _fetch_transcript(self, video_id: str) -> Dict[str, Any]:
        """
        Fetch transcript with caching to prevent redundant API calls.
        
        CATASTROPHIC INCIDENT FIX: Checks cache first, only fetches from API if needed.
        This prevents the 2,165 redundant requests that caused the rate limit ban.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Transcript result (from cache or fetcher)
        
        Raises:
            RateLimitError: If API rate limit exceeded
            TranscriptNotAvailableError: If video has no captions
        """
        # CACHE CHECK: Return cached transcript if available
        cached = self.transcript_cache.get(video_id)
        if cached:
            self.logger.info(f"Cache HIT: {video_id} - no API call needed!")
            return cached

        # CACHE MISS: Fetch from API
        self.logger.info(f"Cache MISS: {video_id} - fetching from YouTube API")

        from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
        fetcher = YouTubeTranscriptFetcher()

        if self.rate_limit_handler:
            # Use rate limit handler with exponential backoff retry
            result = self.rate_limit_handler.fetch_with_retry(
                video_id,
                lambda vid: fetcher.fetch_transcript(vid)
            )
        else:
            # Direct fetch without retry logic
            result = fetcher.fetch_transcript(video_id)

        # CACHE RESULT: Store for future use
        self.transcript_cache.set(video_id, result)
        self.logger.info(f"Transcript cached: {video_id} (valid for 7 days)")

        return result

    def get_metrics(self) -> dict:
        """
        Get handler metrics for monitoring.
        
        Returns:
            Dictionary with YouTube processing metrics
        """
        return self.metrics_tracker.get_metrics()

    def get_health(self) -> dict:
        """
        Get handler health status for daemon monitoring.
        
        Returns:
            Dictionary with health status information
        """
        metrics = self.metrics_tracker.get_metrics()
        error_rate = self.metrics_tracker.get_error_rate()

        # Calculate success rate
        total = metrics['events_processed'] + metrics['events_failed']
        success_rate = metrics['events_processed'] / total if total > 0 else 0

        # Determine health status based on success rate
        if total == 0:
            status = 'healthy'
        elif success_rate > 0.9:
            status = 'healthy'
        elif success_rate > 0.7:
            status = 'degraded'
        else:
            status = 'unhealthy'

        return {
            'status': status,
            'success_rate': success_rate,
            'last_processed': metrics['last_processed'],
            'error_rate': error_rate
        }

    def export_metrics(self) -> str:
        """
        Export handler metrics in JSON format.
        
        Returns:
            JSON string with metrics data
        """
        import json
        metrics = self.get_metrics()
        return json.dumps(metrics, indent=2)

    def process(self, file_path: Path, event_type: str) -> None:
        """
        Process file events with cooldown to prevent file watching loops.
        
        CATASTROPHIC INCIDENT FIX: Implements 60-second cooldown between processing
        the same file. This prevents the infinite loop that caused 2,165 processing
        events and resulted in YouTube IP ban.
        
        Args:
            file_path: Path to file that changed
            event_type: Event type ('created', 'modified', 'deleted')
        """
        # Only process markdown files
        if not str(file_path).endswith('.md'):
            return

        # Only process creation and modification events
        if event_type not in ['created', 'modified']:
            return

        # COOLDOWN CHECK: Prevent processing same file too frequently
        if file_path in self._last_processed:
            elapsed = time.time() - self._last_processed[file_path]
            if elapsed < self.cooldown_seconds:
                self.logger.debug(
                    f"COOLDOWN: Skipping {file_path.name} - processed {int(elapsed)}s ago "
                    f"(cooldown: {self.cooldown_seconds}s)"
                )
                return

        # CONCURRENT PROCESSING CHECK: Prevent multiple simultaneous processing
        if file_path in self._processing_files:
            self.logger.debug(f"CONCURRENT: Skipping {file_path.name} - already processing")
            return

        # Mark as processing
        self._processing_files.add(file_path)

        try:
            # Create mock event object for internal methods
            class FileEvent:
                def __init__(self, path):
                    self.src_path = path

            event = FileEvent(file_path)

            # Check if handler should process this file
            if not self.can_handle(event):
                return

            # Process the file
            self.handle(event)

            # Record processing time (success)
            self._last_processed[file_path] = time.time()

        finally:
            # Always remove from processing set
            self._processing_files.discard(file_path)
