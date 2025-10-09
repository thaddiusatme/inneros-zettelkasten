#!/usr/bin/env python3
"""
YouTube Official API Fetcher - TDD Iteration 1 REFACTOR Phase

Fetches YouTube video transcripts using official YouTube Data API v3.
Replaces unofficial youtube-transcript-api with quota-based official API.

Features:
- Official YouTube Data API v3 integration (requires API key)
- Quota tracking with QuotaTracker utility (250 units per video)
- SRT format parsing via SRTParser utility
- Interface compatibility with existing YouTubeTranscriptFetcher
- Comprehensive error handling with YouTubeAPIErrorHandler

Usage:
    from ai.youtube_official_api_fetcher import YouTubeOfficialAPIFetcher
    
    fetcher = YouTubeOfficialAPIFetcher(api_key=os.getenv('YOUTUBE_API_KEY'))
    result = fetcher.fetch_transcript("dQw4w9WgXcQ")
    
    # Format for LLM processing
    llm_text = fetcher.format_for_llm(result["transcript"])
    
    # Check quota usage
    print(f"Videos remaining today: {fetcher.quota_tracker.videos_remaining()}")

Author: InnerOS Zettelkasten Team
Version: 1.0.0 (TDD Iteration 1 REFACTOR Phase)
"""
import re
import logging
from typing import Dict, List, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from development.src.ai.youtube_api_utils import QuotaTracker, SRTParser, YouTubeAPIErrorHandler

logger = logging.getLogger(__name__)


class TranscriptNotAvailableError(Exception):
    """Raised when video has no transcript available"""
    pass


class InvalidVideoIdError(Exception):
    """Raised when video ID is invalid or malformed"""
    pass


class QuotaExceededError(Exception):
    """Raised when YouTube API quota is exceeded"""
    pass


class YouTubeOfficialAPIFetcher:
    """
    Fetches YouTube video transcripts using official YouTube Data API v3.
    
    This class provides a production-ready interface for fetching YouTube
    transcripts with comprehensive error handling, quota tracking, and
    format compatibility with existing YouTubeTranscriptFetcher.
    
    Attributes:
        api_key: YouTube Data API v3 key
        service: YouTube API service instance
        quota_used: Units consumed in current session (250 per video)
    
    Example:
        >>> fetcher = YouTubeOfficialAPIFetcher(api_key="your_api_key")
        >>> result = fetcher.fetch_transcript("dQw4w9WgXcQ")
        >>> print(f"Fetched {len(result['transcript'])} entries")
    """
    
    # Quota costs per API operation
    QUOTA_COST_LIST = 50      # captions.list() cost
    QUOTA_COST_DOWNLOAD = 200  # captions.download() cost
    QUOTA_COST_PER_VIDEO = QUOTA_COST_LIST + QUOTA_COST_DOWNLOAD  # 250 total
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube Official API fetcher.
        
        Args:
            api_key: YouTube Data API v3 key (required)
            
        Raises:
            ValueError: If API key is missing or empty
        """
        if not api_key:
            raise ValueError(
                "YouTube API key is required. Set YOUTUBE_API_KEY environment variable.\n"
                "Get your key at: https://console.cloud.google.com/apis/credentials"
            )
        
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError(
                "YouTube API key must be a non-empty string.\n"
                "Set YOUTUBE_API_KEY environment variable with your API key."
            )
        
        self.api_key = api_key.strip()
        self.quota_used = 0
        self.quota_tracker = QuotaTracker()  # Initialize quota tracker utility
        
        # Build YouTube API service
        try:
            self.service = build('youtube', 'v3', developerKey=self.api_key)
            logger.info("YouTubeOfficialAPIFetcher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to build YouTube API service: {str(e)}")
            raise
    
    def _parse_srt(self, srt_content: bytes) -> List[Dict[str, Any]]:
        """
        Parse SRT subtitle format to transcript entries.
        
        Delegates to SRTParser utility for parsing logic.
        
        Args:
            srt_content: Raw SRT content from YouTube API
            
        Returns:
            List of transcript entries with text/start/duration
        """
        return SRTParser.parse(srt_content)
    
    def fetch_transcript(self, video_id: str, prefer_manual: bool = True) -> Dict[str, Any]:
        """
        Fetch transcript for YouTube video using official API.
        
        Fetches transcript using YouTube Data API v3 captions endpoint.
        Tracks quota usage (250 units per video).
        
        Args:
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            prefer_manual: If True, prefer manual transcripts over auto-generated
            
        Returns:
            Dictionary containing:
                - video_id (str): The video ID requested
                - transcript (list): List of transcript entries with text/start/duration
                - is_manual (bool): Whether transcript is manually created
                - language (str): Language code (e.g., 'en')
            
        Raises:
            InvalidVideoIdError: Video ID is invalid or video not found
            TranscriptNotAvailableError: No transcript available for video
            QuotaExceededError: API quota exceeded
            
        Example:
            >>> result = fetcher.fetch_transcript("dQw4w9WgXcQ")
            >>> print(f"Language: {result['language']}")
            >>> print(f"Entries: {len(result['transcript'])}")
        """
        logger.info(f"Fetching transcript for video: {video_id} (official API)")
        
        # Validate video ID format
        if not video_id or not isinstance(video_id, str):
            error_msg = f"Invalid video ID: {video_id} (must be non-empty string)"
            logger.error(error_msg)
            raise InvalidVideoIdError(error_msg)
        
        video_id = video_id.strip()
        
        if not video_id or not re.match(r'^[\w-]+$', video_id):
            error_msg = f"Invalid video ID format: {video_id} (contains invalid characters)"
            logger.error(error_msg)
            raise InvalidVideoIdError(error_msg)
        
        try:
            # Step 1: List available captions (50 quota units)
            logger.debug(f"Calling captions.list() for video: {video_id}")
            captions_list = self.service.captions().list(
                part='snippet',
                videoId=video_id
            ).execute()
            
            # Track quota usage for list operation
            self.quota_used += self.QUOTA_COST_LIST
            self.quota_tracker.consume(self.QUOTA_COST_LIST)
            logger.debug(f"Quota used: {self.quota_used} (+{self.QUOTA_COST_LIST} for list)")
            
            # Check if captions are available
            caption_tracks = captions_list.get('items', [])
            if not caption_tracks:
                error_msg = f"No captions available for video: {video_id}"
                logger.warning(error_msg)
                raise TranscriptNotAvailableError(error_msg)
            
            # Step 2: Choose best caption track
            selected_caption = None
            is_manual = False
            
            if prefer_manual:
                # Try to find manual transcript first
                for caption in caption_tracks:
                    track_kind = caption['snippet'].get('trackKind', '')
                    if track_kind == 'standard':  # Manual transcript
                        selected_caption = caption
                        is_manual = True
                        logger.debug(f"Selected manual caption: {caption['id']}")
                        break
                
                # If no manual found, use auto-generated
                if not selected_caption:
                    for caption in caption_tracks:
                        track_kind = caption['snippet'].get('trackKind', '')
                        if track_kind == 'asr':  # Auto-generated
                            selected_caption = caption
                            is_manual = False
                            logger.debug(f"Selected auto-generated caption: {caption['id']}")
                            break
            
            # Fallback: use first available caption
            if not selected_caption:
                selected_caption = caption_tracks[0]
                is_manual = selected_caption['snippet'].get('trackKind', '') == 'standard'
            
            caption_id = selected_caption['id']
            language = selected_caption['snippet'].get('language', 'unknown')
            
            # Step 3: Download caption track (200 quota units)
            logger.debug(f"Calling captions.download() for caption: {caption_id}")
            srt_content = self.service.captions().download(
                id=caption_id,
                tfmt='srt'
            ).execute()
            
            # Track quota usage for download operation
            self.quota_used += self.QUOTA_COST_DOWNLOAD
            self.quota_tracker.consume(self.QUOTA_COST_DOWNLOAD)
            logger.debug(f"Quota used: {self.quota_used} (+{self.QUOTA_COST_DOWNLOAD} for download)")
            
            # Step 4: Parse SRT format
            transcript = self._parse_srt(srt_content)
            
            logger.info(
                f"Successfully fetched transcript: {len(transcript)} entries, "
                f"manual: {is_manual}, language: {language}, "
                f"quota used: {self.quota_used}"
            )
            
            return {
                'video_id': video_id,
                'transcript': transcript,
                'is_manual': is_manual,
                'language': language
            }
            
        except HttpError as e:
            # Use YouTubeAPIErrorHandler for semantic error mapping
            semantic_error = YouTubeAPIErrorHandler.handle_http_error(e, video_id, self.quota_used)
            logger.error(f"YouTube API error for video {video_id}: {str(semantic_error)}")
            raise semantic_error
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript: {str(e)}")
            raise
    
    def format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp in MM:SS format for markdown.
        
        Converts float seconds into human-readable MM:SS format.
        Compatible with existing YouTubeTranscriptFetcher format.
        
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
        Compatible with existing YouTubeTranscriptFetcher format.
        
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
            timestamp = self.format_timestamp(entry['start'])
            text = entry['text'].strip()
            formatted_lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(formatted_lines)
