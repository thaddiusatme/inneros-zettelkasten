#!/usr/bin/env python3
"""
YouTube Transcript Fetcher - TDD Iteration 1 GREEN Phase

Fetches and formats YouTube video transcripts for knowledge capture workflow.
Part of YouTube Transcript AI Processing System (4-iteration roadmap).

GREEN Phase: Minimal implementation to pass all 10 tests.
"""
import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    YouTubeRequestFailed,
    RequestBlocked
)

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


class YouTubeTranscriptFetcher:
    """
    Fetches YouTube video transcripts using youtube-transcript-api.
    
    GREEN Phase: Minimal implementation to pass all tests.
    """
    
    def __init__(self):
        """Initialize transcript fetcher"""
        # Create API instance
        self.api = YouTubeTranscriptApi()
        logger.debug("YouTubeTranscriptFetcher initialized")
    
    def fetch_transcript(self, video_id: str, prefer_manual: bool = True) -> dict:
        """
        Fetch transcript for YouTube video.
        
        Args:
            video_id: YouTube video ID (11 characters)
            prefer_manual: Prefer manual transcripts over auto-generated
            
        Returns:
            dict with transcript data and metadata
            
        Raises:
            InvalidVideoIdError: Video ID is invalid
            TranscriptNotAvailableError: No transcript available
            RateLimitError: API rate limit exceeded
        """
        # Validate video ID
        if not video_id or not isinstance(video_id, str):
            raise InvalidVideoIdError(f"Invalid video ID: {video_id}")
        
        video_id = video_id.strip()
        
        if not video_id or not re.match(r'^[\w-]+$', video_id):
            raise InvalidVideoIdError(f"Invalid video ID format: {video_id}")
        
        try:
            # Fetch transcript using youtube-transcript-api
            transcript_list = self.api.list(video_id)
            
            if prefer_manual:
                # Try to get manual transcript first
                for transcript in transcript_list:
                    if not transcript.is_generated:
                        transcript_data = transcript.fetch()
                        # Convert transcript objects to dict format
                        transcript_entries = [
                            {
                                "text": entry.text,
                                "start": entry.start,
                                "duration": entry.duration
                            }
                            for entry in transcript_data
                        ]
                        return {
                            "video_id": video_id,
                            "transcript": transcript_entries,
                            "is_manual": True,
                            "language": transcript.language_code
                        }
                
                # If no manual found, use auto-generated
                for transcript in transcript_list:
                    if transcript.is_generated:
                        transcript_data = transcript.fetch()
                        # Convert transcript objects to dict format
                        transcript_entries = [
                            {
                                "text": entry.text,
                                "start": entry.start,
                                "duration": entry.duration
                            }
                            for entry in transcript_data
                        ]
                        return {
                            "video_id": video_id,
                            "transcript": transcript_entries,
                            "is_manual": False,
                            "language": transcript.language_code
                        }
            else:
                # Simple fetch (first available transcript)
                for transcript in transcript_list:
                    transcript_data = transcript.fetch()
                    # Convert transcript objects to dict format
                    transcript_entries = [
                        {
                            "text": entry.text,
                            "start": entry.start,
                            "duration": entry.duration
                        }
                        for entry in transcript_data
                    ]
                    return {
                        "video_id": video_id,
                        "transcript": transcript_entries,
                        "is_manual": not transcript.is_generated,
                        "language": transcript.language_code
                    }
                
        except (YouTubeRequestFailed, RequestBlocked) as e:
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
            raise Exception(
                f"Network connection error: {str(e)}"
            )
        except Exception as e:
            # Check if it's a rate limit error in disguise
            if "too many requests" in str(e).lower():
                raise RateLimitError(
                    f"Rate limit exceeded. Please retry later. Details: {str(e)}"
                )
            # Re-raise other exceptions
            raise
    
    def format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp in MM:SS format for markdown.
        
        Args:
            seconds: Timestamp in seconds
            
        Returns:
            Formatted timestamp string (MM:SS)
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def format_for_llm(self, transcript: list) -> str:
        """
        Format transcript for LLM consumption.
        
        Args:
            transcript: List of transcript entries
            
        Returns:
            Clean formatted text with timestamps
        """
        if not transcript:
            return ""
        
        # Format each entry with timestamp
        formatted_lines = []
        for entry in transcript:
            timestamp = self.format_timestamp(entry['start'])
            text = entry['text'].strip()
            formatted_lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(formatted_lines)
