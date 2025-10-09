#!/usr/bin/env python3
"""
YouTube API Utilities - TDD Iteration 1 REFACTOR Phase

Utility classes for YouTube Official API integration.
Extracted during REFACTOR phase for modularity and reusability.

Author: InnerOS Zettelkasten Team
Version: 1.0.0 (TDD Iteration 1 REFACTOR Phase)
"""
import re
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QuotaTracker:
    """
    Track YouTube API quota usage across sessions.
    
    YouTube Data API v3 has daily quota limits (10,000 units for free tier).
    Each video transcript fetch costs 250 units (50 list + 200 download).
    This tracker helps monitor usage and predict capacity.
    
    Attributes:
        quota_used: Units consumed in current session
        daily_limit: Daily quota limit (default 10,000)
        reset_time: When quota resets (midnight Pacific Time)
    
    Example:
        >>> tracker = QuotaTracker(daily_limit=10000)
        >>> tracker.consume(250)
        >>> print(f"Remaining: {tracker.remaining_quota()}")
        >>> print(f"Can fetch: {tracker.videos_remaining()} videos")
    """
    
    QUOTA_PER_VIDEO = 250  # 50 (list) + 200 (download)
    
    def __init__(self, daily_limit: int = 10000, quota_used: int = 0):
        """
        Initialize quota tracker.
        
        Args:
            daily_limit: Daily quota limit (default 10,000 for free tier)
            quota_used: Initial quota used (default 0)
        """
        self.daily_limit = daily_limit
        self.quota_used = quota_used
        self.reset_time = self._calculate_reset_time()
        logger.info(f"QuotaTracker initialized: {quota_used}/{daily_limit} used")
    
    def _calculate_reset_time(self) -> datetime:
        """Calculate when quota resets (midnight Pacific Time)"""
        # Simplified: next midnight UTC (YouTube actually resets at midnight PT)
        now = datetime.utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return tomorrow
    
    def consume(self, units: int) -> None:
        """
        Consume quota units.
        
        Args:
            units: Number of units to consume
        """
        self.quota_used += units
        logger.debug(f"Quota consumed: {units} units, total: {self.quota_used}/{self.daily_limit}")
        
        # Warn if approaching limit
        if self.quota_used >= self.daily_limit * 0.8:
            logger.warning(
                f"Approaching daily quota limit: {self.quota_used}/{self.daily_limit} "
                f"({(self.quota_used/self.daily_limit)*100:.1f}%)"
            )
    
    def remaining_quota(self) -> int:
        """Get remaining quota units"""
        return max(0, self.daily_limit - self.quota_used)
    
    def videos_remaining(self) -> int:
        """Calculate how many videos can still be fetched today"""
        return self.remaining_quota() // self.QUOTA_PER_VIDEO
    
    def usage_percentage(self) -> float:
        """Get quota usage as percentage"""
        return (self.quota_used / self.daily_limit) * 100
    
    def is_quota_exceeded(self) -> bool:
        """Check if quota limit is exceeded"""
        return self.quota_used >= self.daily_limit
    
    def get_reset_info(self) -> Dict[str, Any]:
        """Get information about quota reset"""
        now = datetime.utcnow()
        time_until_reset = self.reset_time - now
        hours_remaining = time_until_reset.total_seconds() / 3600
        
        return {
            'reset_time': self.reset_time.isoformat(),
            'hours_until_reset': round(hours_remaining, 2),
            'current_usage': self.quota_used,
            'daily_limit': self.daily_limit,
            'remaining': self.remaining_quota(),
            'videos_remaining': self.videos_remaining()
        }


class SRTParser:
    """
    Parse SRT subtitle format to normalized transcript entries.
    
    SRT (SubRip Text) is the format returned by YouTube API captions.download().
    This parser converts SRT to the standard transcript format used by InnerOS.
    
    Example:
        >>> parser = SRTParser()
        >>> srt = b"1\\n00:00:00,000 --> 00:00:02,500\\nHello world"
        >>> transcript = parser.parse(srt)
        >>> print(transcript[0]['text'])  # "Hello world"
    """
    
    @staticmethod
    def parse_timestamp(timestamp: str) -> float:
        """
        Parse SRT timestamp to seconds.
        
        Args:
            timestamp: SRT timestamp (HH:MM:SS,mmm format)
            
        Returns:
            Timestamp in seconds (float)
            
        Example:
            >>> SRTParser.parse_timestamp("00:01:30,500")
            90.5
            >>> SRTParser.parse_timestamp("01:00:00,000")
            3600.0
        """
        # Replace comma with dot for milliseconds
        parts = timestamp.replace(',', '.').strip()
        time_parts = parts.split(':')
        
        if len(time_parts) == 3:
            # HH:MM:SS.mmm format
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = float(time_parts[2])
            return hours * 3600 + minutes * 60 + seconds
        elif len(time_parts) == 2:
            # MM:SS.mmm format
            minutes = int(time_parts[0])
            seconds = float(time_parts[1])
            return minutes * 60 + seconds
        else:
            # Just seconds
            return float(parts)
    
    @staticmethod
    def parse(srt_content: bytes) -> List[Dict[str, Any]]:
        """
        Parse SRT subtitle format to transcript entries.
        
        Args:
            srt_content: Raw SRT content from YouTube API
            
        Returns:
            List of transcript entries with text/start/duration
            
        Example:
            >>> srt = b"1\\n00:00:00,000 --> 00:00:02,500\\nFirst line\\n\\n2\\n00:00:02,500 --> 00:00:05,000\\nSecond line"
            >>> transcript = SRTParser.parse(srt)
            >>> len(transcript)
            2
            >>> transcript[0]['text']
            'First line'
        """
        transcript = []
        
        # Decode bytes to string
        srt_text = srt_content.decode('utf-8', errors='ignore')
        
        # Split into subtitle blocks (separated by blank lines)
        blocks = re.split(r'\n\s*\n', srt_text.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            # Line 1: sequence number (ignore)
            # Line 2: timestamp line (00:00:00,000 --> 00:00:02,500)
            # Line 3+: subtitle text
            
            try:
                timestamp_line = lines[1]
                match = re.match(r'(\S+)\s+-->\s+(\S+)', timestamp_line)
                if not match:
                    continue
                
                start_str, end_str = match.groups()
                start = SRTParser.parse_timestamp(start_str)
                end = SRTParser.parse_timestamp(end_str)
                duration = end - start
                
                # Join remaining lines as text
                text = '\n'.join(lines[2:]).strip()
                
                transcript.append({
                    'text': text,
                    'start': start,
                    'duration': duration
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse SRT block: {str(e)}")
                continue
        
        logger.debug(f"Parsed {len(transcript)} transcript entries from SRT")
        return transcript


class YouTubeAPIErrorHandler:
    """
    Handle YouTube API errors and map to semantic exceptions.
    
    Provides clear, actionable error messages for common YouTube API errors
    with troubleshooting guidance for users.
    """
    
    @staticmethod
    def handle_http_error(error: Exception, video_id: str, quota_used: int = 0) -> Exception:
        """
        Convert HttpError to semantic exception with helpful message.
        
        Args:
            error: HttpError from YouTube API
            video_id: Video ID that caused the error
            quota_used: Current quota usage for context
            
        Returns:
            Semantic exception (InvalidVideoIdError, QuotaExceededError, etc.)
        """
        from googleapiclient.errors import HttpError
        
        if not isinstance(error, HttpError):
            return error
        
        error_content = error.content.decode('utf-8') if error.content else ''
        status = error.resp.status
        
        if status == 404:
            from development.src.ai.youtube_official_api_fetcher import InvalidVideoIdError
            return InvalidVideoIdError(
                f"Video not found: {video_id}\n"
                f"Possible reasons:\n"
                f"  - Video is private or deleted\n"
                f"  - Invalid video ID format\n"
                f"  - Video doesn't exist on YouTube"
            )
        elif status == 403:
            # Check if it's quota or API key issue
            if 'quota' in error_content.lower():
                from development.src.ai.youtube_official_api_fetcher import QuotaExceededError
                return QuotaExceededError(
                    f"YouTube API quota exceeded!\n"
                    f"Session used: {quota_used} units\n"
                    f"Daily limit: 10,000 units (~40 videos)\n"
                    f"Quota resets at midnight Pacific Time\n"
                    f"\n"
                    f"Solutions:\n"
                    f"  - Wait for quota reset (midnight PT)\n"
                    f"  - Request quota increase: https://console.cloud.google.com/\n"
                    f"  - Use multiple API keys with rotation"
                )
            else:
                return ValueError(
                    f"API key error: {error_content}\n"
                    f"\n"
                    f"Troubleshooting steps:\n"
                    f"  1. Verify YOUTUBE_API_KEY is set correctly\n"
                    f"  2. Check API key is enabled for YouTube Data API v3\n"
                    f"  3. Verify API key restrictions allow your IP/domain\n"
                    f"  4. Generate new key at: https://console.cloud.google.com/apis/credentials"
                )
        elif status == 400:
            from development.src.ai.youtube_official_api_fetcher import InvalidVideoIdError
            return InvalidVideoIdError(
                f"Invalid request: {error_content}\n"
                f"Video ID: {video_id}\n"
                f"Check video ID format (should be 11 characters)"
            )
        else:
            return Exception(f"YouTube API error ({status}): {error_content}")
