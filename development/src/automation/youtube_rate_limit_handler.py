"""
YouTube Rate Limit Handler - Exponential Backoff Retry Logic

Implements intelligent retry logic with exponential backoff for YouTube
transcript fetching to mitigate rate limiting issues on certain networks.

TDD REFACTOR Phase: Enhanced production-ready implementation.

Usage:
    config = {
        'max_retries': 3,
        'base_delay': 5,
        'max_delay': 60,
        'backoff_multiplier': 2
    }
    handler = YouTubeRateLimitHandler(config)
    result = handler.fetch_with_retry(video_id, fetch_func)

Size: ~230 LOC (ADR-001 compliant: <500 LOC)
"""

import logging
import time
import threading
from typing import Callable, Any, Dict
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    VideoUnavailable,
    NoTranscriptFound
)


class YouTubeRateLimitHandler:
    """
    Handles rate limit mitigation with exponential backoff retry logic.
    
    Provides intelligent retry mechanism for transient failures (rate limits,
    network timeouts) while immediately failing on permanent errors (video
    unavailable, transcripts disabled).
    
    Thread-safe for concurrent request handling.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize rate limit handler with configuration.
        
        Args:
            config: Configuration dictionary with keys:
                - max_retries: Maximum retry attempts (default: 3, range: 0-10)
                - base_delay: Initial delay in seconds (default: 5, range: 1-30)
                - max_delay: Maximum delay cap in seconds (default: 60, range: 10-300)
                - backoff_multiplier: Exponential multiplier (default: 2, range: 1.5-5)
        
        Raises:
            ValueError: If configuration values are out of valid ranges
        """
        # Validate and set configuration with defaults
        self.max_retries = int(self._validate_config(
            config.get('max_retries', 3), 'max_retries', 0, 10
        ))
        self.base_delay = self._validate_config(
            config.get('base_delay', 5), 'base_delay', 1, 30
        )
        self.max_delay = self._validate_config(
            config.get('max_delay', 60), 'max_delay', 10, 300
        )
        self.backoff_multiplier = self._validate_config(
            config.get('backoff_multiplier', 2), 'backoff_multiplier', 1.5, 5
        )

        # Thread-safe metrics tracking with enhanced statistics
        self._metrics_lock = threading.Lock()
        self._metrics = {
            'total_attempts': 0,
            'rate_limited': 0,
            'succeeded': 0,
            'failed': 0,
            'permanent_failures': 0
        }

        # Setup structured logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @property
    def metrics(self) -> Dict[str, int]:
        """
        Get current metrics (thread-safe).
        
        Returns:
            Dictionary with total_attempts, rate_limited, succeeded counts
        """
        with self._metrics_lock:
            return self._metrics.copy()

    def fetch_with_retry(self, video_id: str, fetch_func: Callable[[str], Any]) -> Any:
        """
        Fetch transcript with exponential backoff retry logic.
        
        Args:
            video_id: YouTube video ID
            fetch_func: Function to call for fetching (receives video_id)
        
        Returns:
            Result from successful fetch_func call
        
        Raises:
            Exception: Permanent errors or exhausted retries
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # Increment total attempts (thread-safe)
                with self._metrics_lock:
                    self._metrics['total_attempts'] += 1

                # Attempt fetch
                result = fetch_func(video_id)

                # Success - increment succeeded counter
                with self._metrics_lock:
                    self._metrics['succeeded'] += 1

                return result

            except Exception as e:
                last_exception = e

                # Classify error - permanent errors fail immediately
                is_transient = self._classify_error(e)

                if not is_transient:
                    # Permanent error - fail immediately without retry
                    with self._metrics_lock:
                        self._metrics['permanent_failures'] += 1
                        self._metrics['failed'] += 1

                    self.logger.info(
                        f"Permanent error [video_id={video_id}] "
                        f"error_type={type(e).__name__}, no retry attempted"
                    )
                    raise

                # Transient error - check if we can retry
                if attempt >= self.max_retries:
                    # Exhausted retries - increment counters and log warning
                    with self._metrics_lock:
                        self._metrics['rate_limited'] += 1
                        self._metrics['failed'] += 1

                    self.logger.warning(
                        f"Rate limit exhausted [video_id={video_id}] "
                        f"after {self.max_retries + 1} attempts. "
                        f"Consider increasing max_delay or max_retries. "
                        f"Final error: {type(e).__name__}"
                    )
                    raise

                # We will retry - increment rate_limited counter
                with self._metrics_lock:
                    self._metrics['rate_limited'] += 1

                # Calculate delay and log retry attempt with structured context
                delay = self._calculate_delay(attempt)
                self.logger.info(
                    f"Rate limit retry [video_id={video_id}] "
                    f"attempt={attempt + 1}/{self.max_retries + 1}, "
                    f"delay={delay}s, error_type={type(e).__name__}, "
                    f"error_msg={str(e)[:100]}"
                )

                # Sleep before retry
                time.sleep(delay)

        # Should never reach here, but raise last exception if we do
        if last_exception:
            raise last_exception

    def _validate_config(self, value: Any, name: str, min_val: float, max_val: float) -> float:
        """Validate configuration parameter is within acceptable range.
        
        Args:
            value: Configuration value to validate
            name: Parameter name for error messages
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value
        
        Returns:
            Validated value
        
        Raises:
            ValueError: If value is out of range
        """
        try:
            num_value = float(value)
            if not (min_val <= num_value <= max_val):
                raise ValueError(
                    f"{name} must be between {min_val} and {max_val}, got {value}"
                )
            return num_value
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"Invalid {name} value: {value}. Must be numeric between {min_val}-{max_val}"
            ) from e

    def _classify_error(self, exception: Exception) -> bool:
        """Classify error as transient (retryable) or permanent.
        
        Permanent errors indicate issues that won't resolve with retry:
        - VideoUnavailable: Video deleted or private
        - TranscriptsDisabled: Transcripts not available for video
        - NoTranscriptFound: No transcript in requested language
        
        Transient errors may resolve with retry:
        - 429 Too Many Requests: Rate limiting
        - Network timeouts: Temporary connectivity issues
        - Generic exceptions: Conservative retry approach
        
        Args:
            exception: Exception to classify
        
        Returns:
            True if transient (retry), False if permanent (fail immediately)
        """
        # Permanent errors - fail immediately
        if isinstance(exception, (VideoUnavailable, TranscriptsDisabled, NoTranscriptFound)):
            return False

        # Transient errors - retry with backoff
        error_message = str(exception)
        if "429" in error_message or "Too Many Requests" in error_message:
            return True

        # Generic exceptions - treat as transient for now (conservative retry)
        return True

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with max cap.
        
        Uses formula: delay = base_delay * (multiplier ^ attempt)
        
        Examples:
            base_delay=5, multiplier=2, attempt=0 → 5s
            base_delay=5, multiplier=2, attempt=1 → 10s
            base_delay=5, multiplier=2, attempt=2 → 20s
            base_delay=5, multiplier=3, attempt=2 → 45s
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Delay in seconds (capped at max_delay)
        """
        # Exponential backoff: base_delay * (multiplier ^ attempt)
        delay = self.base_delay * (self.backoff_multiplier ** attempt)

        # Cap at max_delay to prevent excessive waits
        return min(delay, self.max_delay)

    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get detailed retry statistics for monitoring.
        
        Returns:
            Dictionary with:
                - retry_rate: Percentage of requests that required retry
                - success_rate: Percentage of successful requests
                - failure_rate: Percentage of failed requests
                - avg_attempts: Average attempts per request
        """
        with self._metrics_lock:
            total = self._metrics['total_attempts']
            if total == 0:
                return {
                    'retry_rate': 0.0,
                    'success_rate': 0.0,
                    'failure_rate': 0.0,
                    'avg_attempts': 0.0
                }

            return {
                'retry_rate': self._metrics['rate_limited'] / total,
                'success_rate': self._metrics['succeeded'] / total,
                'failure_rate': self._metrics['failed'] / total,
                'avg_attempts': total / max(self._metrics['succeeded'] + self._metrics['failed'], 1)
            }
