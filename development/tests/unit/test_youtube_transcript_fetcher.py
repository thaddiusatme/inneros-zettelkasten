#!/usr/bin/env python3
"""
TDD Iteration 1 RED Phase: YouTube Transcript Fetcher Tests

Tests for YouTubeTranscriptFetcher class that fetches and formats
YouTube video transcripts for knowledge capture workflow.

Following TDD methodology proven across 10 successful iterations.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.youtube_transcript_fetcher import (
    YouTubeTranscriptFetcher,
    TranscriptNotAvailableError,
    InvalidVideoIdError,
    RateLimitError
)


class TestYouTubeTranscriptFetcherBasicFunctionality:
    """Test P0: Core transcript fetching functionality"""
    
    def test_fetch_valid_video_transcript(self):
        """
        RED Phase Test 1: Fetch transcript for valid YouTube video
        
        Success case: Should return formatted transcript with timestamps
        """
        fetcher = YouTubeTranscriptFetcher()
        
        # Use a real video ID that has transcripts (example)
        video_id = "dQw4w9WgXcQ"  # Famous video with transcripts
        
        result = fetcher.fetch_transcript(video_id)
        
        # Verify result structure
        assert result is not None
        assert "transcript" in result
        assert "video_id" in result
        assert result["video_id"] == video_id
        
        # Verify transcript format
        transcript = result["transcript"]
        assert isinstance(transcript, list)
        assert len(transcript) > 0
        
        # Each entry should have text and timestamp
        for entry in transcript:
            assert "text" in entry
            assert "start" in entry
            assert "duration" in entry
    
    def test_fetch_video_without_transcript(self):
        """
        RED Phase Test 2: Handle videos without transcripts gracefully
        
        Error case: Should raise TranscriptNotAvailableError with clear message
        """
        fetcher = YouTubeTranscriptFetcher()
        
        # Video ID without transcripts (mock scenario)
        video_id = "NO_TRANSCRIPT"
        
        with pytest.raises(TranscriptNotAvailableError) as exc_info:
            fetcher.fetch_transcript(video_id)
        
        # Error message should be helpful
        assert "transcript" in str(exc_info.value).lower()
        assert video_id in str(exc_info.value)
    
    def test_fetch_manual_vs_auto_transcript_preference(self):
        """
        RED Phase Test 3: Prefer manual transcripts over auto-generated
        
        When both available, should return manual transcript (higher quality)
        """
        fetcher = YouTubeTranscriptFetcher()
        
        # Mock scenario where both transcript types available
        video_id = "BOTH_TYPES"
        
        # Mock the transcript API to return both types
        with patch('youtube_transcript_api.YouTubeTranscriptApi.list_transcripts') as mock_list:
            # Setup mock to have both manual and auto-generated
            mock_transcript_list = Mock()
            mock_manual = Mock()
            mock_manual.is_generated = False
            mock_manual.language_code = "en"
            mock_manual.fetch.return_value = [
                {"text": "Manual transcript", "start": 0.0, "duration": 2.0}
            ]
            
            mock_auto = Mock()
            mock_auto.is_generated = True
            mock_auto.language_code = "en"
            mock_auto.fetch.return_value = [
                {"text": "Auto-generated transcript", "start": 0.0, "duration": 2.0}
            ]
            
            mock_transcript_list.__iter__ = Mock(return_value=iter([mock_manual, mock_auto]))
            mock_list.return_value = mock_transcript_list
            
            result = fetcher.fetch_transcript(video_id, prefer_manual=True)
            
            # Should use manual transcript
            assert result["transcript"][0]["text"] == "Manual transcript"
            assert result["is_manual"] == True


class TestYouTubeTranscriptFetcherFormatting:
    """Test P0: Transcript formatting for markdown display"""
    
    def test_format_timestamps_for_markdown(self):
        """
        RED Phase Test 4: Format timestamps in MM:SS format for markdown
        
        Should convert float timestamps to human-readable format
        """
        fetcher = YouTubeTranscriptFetcher()
        
        # Test various timestamp scenarios
        test_cases = [
            (0.0, "00:00"),
            (45.5, "00:45"),
            (90.0, "01:30"),
            (3661.0, "61:01"),  # Over 1 hour
        ]
        
        for seconds, expected in test_cases:
            formatted = fetcher.format_timestamp(seconds)
            assert formatted == expected, f"Expected {expected}, got {formatted} for {seconds}s"
    
    def test_format_transcript_for_llm_processing(self):
        """
        RED Phase Test 5: Format transcript for LLM consumption
        
        Should create clean text format suitable for AI processing
        """
        fetcher = YouTubeTranscriptFetcher()
        
        sample_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0},
            {"text": "This is a test", "start": 2.0, "duration": 3.0},
            {"text": "End of transcript", "start": 5.0, "duration": 2.0}
        ]
        
        formatted = fetcher.format_for_llm(sample_transcript)
        
        # Should be clean text with timestamps
        assert isinstance(formatted, str)
        assert "Hello world" in formatted
        assert "This is a test" in formatted
        assert "End of transcript" in formatted
        
        # Should include timestamps for reference
        assert "00:00" in formatted
        assert "00:02" in formatted
        assert "00:05" in formatted


class TestYouTubeTranscriptFetcherErrorHandling:
    """Test P0: Comprehensive error handling"""
    
    def test_handle_invalid_video_id(self):
        """
        RED Phase Test 6: Handle invalid video IDs gracefully
        
        Should raise InvalidVideoIdError for malformed IDs
        """
        fetcher = YouTubeTranscriptFetcher()
        
        invalid_ids = [
            "",  # Empty
            "   ",  # Whitespace only
            "not-a-valid-id!@#",  # Invalid characters
            None,  # None value
        ]
        
        for invalid_id in invalid_ids:
            with pytest.raises(InvalidVideoIdError) as exc_info:
                fetcher.fetch_transcript(invalid_id)
            
            assert "invalid" in str(exc_info.value).lower()
    
    def test_handle_rate_limit_errors(self):
        """
        RED Phase Test 7: Handle API rate limiting gracefully
        
        Should raise RateLimitError with retry guidance
        """
        fetcher = YouTubeTranscriptFetcher()
        
        video_id = "RATE_LIMIT_TEST"
        
        # Mock rate limit scenario
        with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
            mock_get.side_effect = Exception("Too many requests")
            
            with pytest.raises(RateLimitError) as exc_info:
                fetcher.fetch_transcript(video_id)
            
            # Should provide helpful guidance
            assert "rate limit" in str(exc_info.value).lower()
            assert "retry" in str(exc_info.value).lower()
    
    def test_handle_network_errors(self):
        """
        RED Phase Test 8: Handle network connectivity issues
        
        Should raise appropriate error with recovery suggestions
        """
        fetcher = YouTubeTranscriptFetcher()
        
        video_id = "NETWORK_ERROR_TEST"
        
        # Mock network error
        with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get:
            mock_get.side_effect = ConnectionError("Network unreachable")
            
            with pytest.raises(Exception) as exc_info:
                fetcher.fetch_transcript(video_id)
            
            # Should indicate network issue
            assert "network" in str(exc_info.value).lower() or "connection" in str(exc_info.value).lower()


class TestYouTubeTranscriptFetcherPerformance:
    """Test P0: Performance requirements"""
    
    def test_fetch_completes_within_30_seconds(self):
        """
        RED Phase Test 9: Ensure transcript fetch completes in <30s
        
        Performance target: <30 seconds per video
        """
        import time
        
        fetcher = YouTubeTranscriptFetcher()
        video_id = "dQw4w9WgXcQ"
        
        start_time = time.time()
        
        try:
            result = fetcher.fetch_transcript(video_id)
            duration = time.time() - start_time
            
            assert duration < 30.0, f"Fetch took {duration}s, expected <30s"
        except Exception:
            # Even failures should be fast
            duration = time.time() - start_time
            assert duration < 30.0, f"Error handling took {duration}s, expected <30s"


class TestYouTubeTranscriptFetcherIntegration:
    """Test P1: Integration with existing systems"""
    
    def test_transcript_output_compatible_with_ollama_llm(self):
        """
        RED Phase Test 10: Ensure output format works with Ollama LLM
        
        Output should be compatible with existing LLM infrastructure
        """
        fetcher = YouTubeTranscriptFetcher()
        
        sample_transcript = [
            {"text": "Test content", "start": 0.0, "duration": 2.0}
        ]
        
        formatted = fetcher.format_for_llm(sample_transcript)
        
        # Should be string format for LLM consumption
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        
        # Should be under reasonable token limit (rough estimate: 4 chars per token)
        # Target: <4000 tokens for most videos
        estimated_tokens = len(formatted) / 4
        assert estimated_tokens < 8000, f"Output too long: ~{estimated_tokens} tokens"


# RED Phase Summary
"""
TDD Iteration 1 RED Phase Complete: 10 Failing Tests

Test Coverage:
- P0 Core Functionality: 3 tests (fetch, error handling, preference logic)
- P0 Formatting: 2 tests (timestamps, LLM format)
- P0 Error Handling: 3 tests (invalid ID, rate limits, network)
- P0 Performance: 1 test (<30s requirement)
- P1 Integration: 1 test (Ollama LLM compatibility)

All tests should FAIL until GREEN Phase implementation.

Next: GREEN Phase implementation in src/ai/youtube_transcript_fetcher.py
"""
