#!/usr/bin/env python3
"""
YouTube Transcript Fetcher - TDD Iteration 1 REFACTOR Phase

Fetches and formats YouTube video transcripts for knowledge capture workflow.
Part of YouTube Transcript AI Processing System (4-iteration roadmap).

Features:
- Fetches transcripts using youtube-transcript-api (no API key required)
- Prefers manual transcripts over auto-generated for quality
- Formats timestamps in MM:SS markdown format
- Generates LLM-ready text with preserved timestamps
- Comprehensive error handling for production use

Usage:
    from ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher

    fetcher = YouTubeTranscriptFetcher()
    result = fetcher.fetch_transcript("dQw4w9WgXcQ")

    # Format for LLM processing
    llm_text = fetcher.format_for_llm(result["transcript"])

Author: InnerOS Zettelkasten Team
Version: 1.0.0 (TDD Iteration 1 REFACTOR Phase)
"""
import re
import logging
import time
from typing import Dict, List, Any, Optional
from xml.etree.ElementTree import ParseError as XMLParseError
from youtube_transcript_api import YouTubeTranscriptApi

# Import available exceptions, with fallbacks for older versions
try:
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        YouTubeRequestFailed,
        RequestBlocked,
        IpBlocked,
    )
except ImportError:
    # Older versions don't have RequestBlocked and IpBlocked
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        YouTubeRequestFailed,
    )

    # Create placeholder exceptions for compatibility
    class RequestBlocked(Exception):
        """Placeholder for RequestBlocked exception in older youtube-transcript-api versions."""

        pass

    class IpBlocked(Exception):
        """Placeholder for IpBlocked exception in older youtube-transcript-api versions."""

        pass


logger = logging.getLogger(__name__)


class TranscriptNotAvailableError(Exception):
    """Raised when video has no transcript available"""

    pass


class InvalidVideoIdError(Exception):
    """Raised when video ID is invalid or malformed"""

    pass


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded"""

    pass


class TranscriptParseError(Exception):
    """Raised when transcript XML parsing fails (transient API issue)"""

    pass


class YouTubeTranscriptFetcher:
    """
    Fetches YouTube video transcripts using youtube-transcript-api.

    This class provides a production-ready interface for fetching YouTube
    transcripts with comprehensive error handling and formatting options.

    Attributes:
        api: YouTubeTranscriptApi instance for fetching transcripts

    Example:
        >>> fetcher = YouTubeTranscriptFetcher()
        >>> result = fetcher.fetch_transcript("dQw4w9WgXcQ")
        >>> print(f"Fetched {len(result['transcript'])} entries")
    """

    # Default retry configuration for transient errors
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0  # seconds
    DEFAULT_RETRY_BACKOFF = 2.0  # exponential backoff multiplier

    def __init__(
        self,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
    ):
        """
        Initialize transcript fetcher.

        Creates a YouTubeTranscriptApi instance for transcript fetching.
        No external dependencies or API keys required.

        Args:
            max_retries: Maximum retry attempts for transient errors (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 1.0)
            retry_backoff: Exponential backoff multiplier (default: 2.0)
        """
        self.api = YouTubeTranscriptApi()  # Create instance for v1.2.3+ API
        self.max_retries = (
            max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES
        )
        self.retry_delay = (
            retry_delay if retry_delay is not None else self.DEFAULT_RETRY_DELAY
        )
        self.retry_backoff = (
            retry_backoff if retry_backoff is not None else self.DEFAULT_RETRY_BACKOFF
        )
        logger.info("YouTubeTranscriptFetcher initialized successfully")

    def _convert_transcript_to_dict(
        self, transcript_data: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert API transcript objects to dict format.

        Helper method to convert FetchedTranscriptSnippet objects returned
        by the API into clean dictionary format for consistent handling.

        Args:
            transcript_data: List of FetchedTranscriptSnippet objects

        Returns:
            List of dicts with 'text', 'start', 'duration' keys
        """
        return [
            {"text": entry.text, "start": entry.start, "duration": entry.duration}
            for entry in transcript_data
        ]

    def _fetch_transcript_with_retry(
        self,
        transcript,
        video_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetch transcript data with retry logic for transient XML parse errors.

        Some YouTube videos have malformed caption XML that causes ParseError.
        This is often a transient issue that resolves on retry. This method
        implements exponential backoff retry for such errors.

        Args:
            transcript: Transcript object from list_transcripts()
            video_id: Video ID for logging purposes

        Returns:
            List of transcript entry dicts with 'text', 'start', 'duration' keys

        Raises:
            TranscriptParseError: If all retries fail due to XML parsing issues
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                transcript_data = transcript.fetch()
                return self._convert_transcript_to_dict(transcript_data)

            except XMLParseError as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (self.retry_backoff**attempt)
                    logger.warning(
                        f"XML ParseError fetching transcript for {video_id} "
                        f"(attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed for {video_id} "
                        f"due to XML ParseError: {e}"
                    )

        # All retries exhausted
        raise TranscriptParseError(
            f"Failed to parse transcript XML for video {video_id} after "
            f"{self.max_retries + 1} attempts. This may be a video-specific issue "
            f"with malformed captions. Error: {last_error}"
        )

    def fetch_transcript(
        self,
        video_id: str,
        prefer_manual: bool = True,
        preferred_languages: list = None,
    ) -> Dict[str, Any]:
        """
        Fetch transcript for YouTube video.

        Fetches transcript using youtube-transcript-api and converts to
        clean dictionary format. Prefers manual transcripts for quality
        and prioritizes English language by default.

        Args:
            video_id: YouTube video ID (typically 11 characters, e.g., "dQw4w9WgXcQ")
            prefer_manual: If True, prefer manual transcripts over auto-generated
            preferred_languages: List of language codes to prefer (default: ['en'])

        Returns:
            Dictionary containing:
                - video_id (str): The video ID requested
                - transcript (list): List of transcript entries with text/start/duration
                - is_manual (bool): Whether transcript is manually created
                - language (str): Language code (e.g., 'en')

        Raises:
            InvalidVideoIdError: Video ID is invalid or malformed
            TranscriptNotAvailableError: No transcript available for video
            RateLimitError: API rate limit exceeded, retry later

        Example:
            >>> result = fetcher.fetch_transcript("dQw4w9WgXcQ")
            >>> print(f"Language: {result['language']}")
            >>> print(f"Entries: {len(result['transcript'])}")
        """
        if preferred_languages is None:
            preferred_languages = ["en"]

        logger.info(
            f"Fetching transcript for video: {video_id} (preferred languages: {preferred_languages})"
        )

        # Validate video ID format
        if not video_id or not isinstance(video_id, str):
            error_msg = f"Invalid video ID: {video_id} (must be non-empty string)"
            logger.error(error_msg)
            raise InvalidVideoIdError(error_msg)

        video_id = video_id.strip()

        if not video_id or not re.match(r"^[\w-]+$", video_id):
            error_msg = (
                f"Invalid video ID format: {video_id} (contains invalid characters)"
            )
            logger.error(error_msg)
            raise InvalidVideoIdError(error_msg)

        try:
            # Fetch transcript using youtube-transcript-api (v1.2.3+ uses list())
            transcript_list = self.api.list(video_id)

            if prefer_manual:
                # Try to get manual transcript in preferred language first (higher quality)
                logger.debug(
                    f"Looking for manual transcript in preferred languages: {preferred_languages}"
                )
                for lang in preferred_languages:
                    for transcript in transcript_list:
                        if (
                            not transcript.is_generated
                            and transcript.language_code.startswith(lang)
                        ):
                            transcript_entries = self._fetch_transcript_with_retry(
                                transcript, video_id
                            )
                            logger.info(
                                f"Found manual transcript: {len(transcript_entries)} entries, language: {transcript.language_code}"
                            )
                            return {
                                "video_id": video_id,
                                "transcript": transcript_entries,
                                "is_manual": True,
                                "language": transcript.language_code,
                            }

                # If no preferred manual found, try any manual
                logger.debug(
                    "No manual transcript in preferred languages, trying any manual"
                )
                for transcript in transcript_list:
                    if not transcript.is_generated:
                        transcript_entries = self._fetch_transcript_with_retry(
                            transcript, video_id
                        )
                        logger.info(
                            f"Found manual transcript: {len(transcript_entries)} entries, language: {transcript.language_code}"
                        )
                        return {
                            "video_id": video_id,
                            "transcript": transcript_entries,
                            "is_manual": True,
                            "language": transcript.language_code,
                        }

                # If no manual found, use auto-generated in preferred language
                logger.debug(
                    "No manual transcript found, looking for auto-generated in preferred languages"
                )
                for lang in preferred_languages:
                    for transcript in transcript_list:
                        if (
                            transcript.is_generated
                            and transcript.language_code.startswith(lang)
                        ):
                            transcript_entries = self._fetch_transcript_with_retry(
                                transcript, video_id
                            )
                            logger.info(
                                f"Using auto-generated transcript: {len(transcript_entries)} entries, language: {transcript.language_code}"
                            )
                            return {
                                "video_id": video_id,
                                "transcript": transcript_entries,
                                "is_manual": False,
                                "language": transcript.language_code,
                            }

                # Last resort: any auto-generated
                logger.debug("Using any available auto-generated transcript")
                for transcript in transcript_list:
                    if transcript.is_generated:
                        transcript_entries = self._fetch_transcript_with_retry(
                            transcript, video_id
                        )
                        logger.info(
                            f"Using auto-generated transcript: {len(transcript_entries)} entries, language: {transcript.language_code}"
                        )
                        return {
                            "video_id": video_id,
                            "transcript": transcript_entries,
                            "is_manual": False,
                            "language": transcript.language_code,
                        }
            else:
                # Simple fetch (first available transcript)
                logger.debug(
                    f"Fetching first available transcript for video: {video_id}"
                )
                for transcript in transcript_list:
                    transcript_entries = self._fetch_transcript_with_retry(
                        transcript, video_id
                    )
                    is_manual = not transcript.is_generated
                    logger.info(
                        f"Fetched transcript: {len(transcript_entries)} entries, manual: {is_manual}, language: {transcript.language_code}"
                    )
                    return {
                        "video_id": video_id,
                        "transcript": transcript_entries,
                        "is_manual": is_manual,
                        "language": transcript.language_code,
                    }

        except (YouTubeRequestFailed, RequestBlocked, IpBlocked) as e:
            raise RateLimitError(
                f"Rate limit exceeded. Please retry later. Details: {str(e)}"
            )
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise TranscriptNotAvailableError(
                f"No transcript available for video: {video_id}. Details: {str(e)}"
            )
        except VideoUnavailable as e:
            raise InvalidVideoIdError(
                f"Video not found or unavailable: {video_id}. Details: {str(e)}"
            )
        except ConnectionError as e:
            raise Exception(f"Network connection error: {str(e)}")
        except TranscriptParseError:
            # Re-raise TranscriptParseError as-is (already has detailed message)
            raise
        except Exception as e:
            # Check if it's a rate limit error in disguise
            if "too many requests" in str(e).lower():
                raise RateLimitError(
                    f"Rate limit exceeded. Please retry later. Details: {str(e)}"
                )
            # Check if it's an XML parse error not caught by retry logic
            if "no element found" in str(e).lower() or "parseerror" in str(e).lower():
                raise TranscriptParseError(
                    f"XML parsing failed for video {video_id}: {str(e)}. "
                    "This may be a video-specific issue with malformed captions."
                )
            # Re-raise other exceptions
            raise

    def format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp in MM:SS format for markdown.

        Converts float seconds into human-readable MM:SS format.
        Handles videos over 1 hour (e.g., 61:01 for 1 hour 1 minute 1 second).

        Args:
            seconds: Timestamp in seconds (float or int)

        Returns:
            Formatted timestamp string in MM:SS format

        Example:
            >>> fetcher.format_timestamp(0.0)
            '00:00'
            >>> fetcher.format_timestamp(90.5)
            '01:30'
            >>> fetcher.format_timestamp(3661.0)
            '61:01'
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def format_for_llm(self, transcript: List[Dict[str, Any]]) -> str:
        """
        Format transcript for LLM consumption.

        Converts transcript entries into clean timestamped text format
        suitable for AI processing and quote extraction.

        Args:
            transcript: List of transcript entry dicts with 'text' and 'start' keys

        Returns:
            Formatted text with timestamps (one entry per line)
            Example: "[00:00] transcript text here\\n[00:05] more text..."

        Example:
            >>> transcript = [
            ...     {"text": "Hello world", "start": 0.0, "duration": 2.0},
            ...     {"text": "This is a test", "start": 2.0, "duration": 3.0}
            ... ]
            >>> text = fetcher.format_for_llm(transcript)
            >>> print(text)
            [00:00] Hello world
            [00:02] This is a test
        """
        if not transcript:
            logger.warning("Empty transcript provided to format_for_llm()")
            return ""

        logger.debug(f"Formatting {len(transcript)} transcript entries for LLM")

        # Format each entry with timestamp
        formatted_lines = []
        for entry in transcript:
            timestamp = self.format_timestamp(entry["start"])
            text = entry["text"].strip()
            formatted_lines.append(f"[{timestamp}] {text}")

        return "\n".join(formatted_lines)
