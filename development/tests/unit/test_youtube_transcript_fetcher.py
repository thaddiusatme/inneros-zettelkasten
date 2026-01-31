#!/usr/bin/env python3
"""
TDD Iteration 1 RED Phase: YouTube Transcript Fetcher Tests

Tests for YouTubeTranscriptFetcher class that fetches and formats
YouTube video transcripts for knowledge capture workflow.

Following TDD methodology proven across 10 successful iterations.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.youtube_transcript_fetcher import (
    YouTubeTranscriptFetcher,
    TranscriptNotAvailableError,
    InvalidVideoIdError,
    RateLimitError,
    TranscriptParseError,
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

        # Mock a video that exists but has no transcripts
        video_id = "NO_TRANSCRIPT"

        from youtube_transcript_api._errors import TranscriptsDisabled

        with patch.object(fetcher.api, "list") as mock_list:
            mock_list.side_effect = TranscriptsDisabled(video_id)

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
        with patch.object(fetcher.api, "list") as mock_list:
            # Setup mock to have both manual and auto-generated
            mock_transcript_list = Mock()
            mock_manual = Mock()
            mock_manual.is_generated = False
            mock_manual.language_code = "en"
            # Create mock transcript snippet objects
            mock_entry = Mock()
            mock_entry.text = "Manual transcript"
            mock_entry.start = 0.0
            mock_entry.duration = 2.0
            mock_manual.fetch.return_value = [mock_entry]

            mock_auto = Mock()
            mock_auto.is_generated = True
            mock_auto.language_code = "en"
            mock_auto_entry = Mock()
            mock_auto_entry.text = "Auto-generated transcript"
            mock_auto_entry.start = 0.0
            mock_auto_entry.duration = 2.0
            mock_auto.fetch.return_value = [mock_auto_entry]

            mock_transcript_list.__iter__ = Mock(
                return_value=iter([mock_manual, mock_auto])
            )
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
            assert (
                formatted == expected
            ), f"Expected {expected}, got {formatted} for {seconds}s"

    def test_format_transcript_for_llm_processing(self):
        """
        RED Phase Test 5: Format transcript for LLM consumption

        Should create clean text format suitable for AI processing
        """
        fetcher = YouTubeTranscriptFetcher()

        sample_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0},
            {"text": "This is a test", "start": 2.0, "duration": 3.0},
            {"text": "End of transcript", "start": 5.0, "duration": 2.0},
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
        from youtube_transcript_api._errors import RequestBlocked

        with patch.object(fetcher.api, "list") as mock_list:
            mock_list.side_effect = RequestBlocked("Too many requests")

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
        with patch.object(fetcher.api, "list") as mock_list:
            mock_list.side_effect = ConnectionError("Network unreachable")

            with pytest.raises(Exception) as exc_info:
                fetcher.fetch_transcript(video_id)

            # Should indicate network issue
            assert (
                "network" in str(exc_info.value).lower()
                or "connection" in str(exc_info.value).lower()
            )


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

        sample_transcript = [{"text": "Test content", "start": 0.0, "duration": 2.0}]

        formatted = fetcher.format_for_llm(sample_transcript)

        # Should be string format for LLM consumption
        assert isinstance(formatted, str)
        assert len(formatted) > 0

        # Should be under reasonable token limit (rough estimate: 4 chars per token)
        # Target: <4000 tokens for most videos
        estimated_tokens = len(formatted) / 4
        assert estimated_tokens < 8000, f"Output too long: ~{estimated_tokens} tokens"


class TestYouTubeTranscriptFetcherParseErrorHandling:
    """Test ParseError handling with retry logic (GitHub Issue #81)"""

    def test_parse_error_raises_transcript_parse_error_after_retries(self):
        """
        Test that XMLParseError raises TranscriptParseError after retry exhaustion.

        GitHub Issue #81: ParseError when fetching transcripts for certain videos.
        The system should retry with exponential backoff, then raise a clear error.
        """
        from xml.etree.ElementTree import ParseError as XMLParseError

        fetcher = YouTubeTranscriptFetcher(max_retries=2, retry_delay=0.01)

        video_id = "PARSE_ERROR_TEST"

        # Mock transcript object that always raises ParseError
        mock_transcript = Mock()
        mock_transcript.is_generated = False
        mock_transcript.language_code = "en"
        mock_transcript.fetch.side_effect = XMLParseError(
            "no element found: line 1, column 0"
        )

        # Mock transcript list
        mock_transcript_list = Mock()
        mock_transcript_list.__iter__ = Mock(return_value=iter([mock_transcript]))

        with patch.object(fetcher.api, "list") as mock_list:
            mock_list.return_value = mock_transcript_list

            with pytest.raises(TranscriptParseError) as exc_info:
                fetcher.fetch_transcript(video_id)

            # Should have helpful error message
            assert "parse" in str(exc_info.value).lower()
            assert video_id in str(exc_info.value)
            assert "3 attempts" in str(exc_info.value)  # max_retries + 1

    def test_parse_error_retry_succeeds_on_second_attempt(self):
        """
        Test that transient ParseError succeeds on retry.

        ParseError can be transient - the system should retry and succeed
        if the error resolves.
        """
        from xml.etree.ElementTree import ParseError as XMLParseError

        fetcher = YouTubeTranscriptFetcher(max_retries=2, retry_delay=0.01)

        video_id = "TRANSIENT_ERROR_TEST"

        # Create mock transcript entry
        mock_entry = Mock()
        mock_entry.text = "Transcript text after retry"
        mock_entry.start = 0.0
        mock_entry.duration = 2.0

        # Mock transcript object that fails once, then succeeds
        mock_transcript = Mock()
        mock_transcript.is_generated = False
        mock_transcript.language_code = "en"
        mock_transcript.fetch.side_effect = [
            XMLParseError("no element found: line 1, column 0"),  # First call fails
            [mock_entry],  # Second call succeeds
        ]

        # Mock transcript list
        mock_transcript_list = Mock()
        mock_transcript_list.__iter__ = Mock(return_value=iter([mock_transcript]))

        with patch.object(fetcher.api, "list") as mock_list:
            mock_list.return_value = mock_transcript_list

            result = fetcher.fetch_transcript(video_id)

            # Should succeed after retry
            assert result is not None
            assert result["video_id"] == video_id
            assert len(result["transcript"]) == 1
            assert result["transcript"][0]["text"] == "Transcript text after retry"

    def test_parse_error_configurable_retry_settings(self):
        """
        Test that retry settings are configurable.

        Users should be able to configure max_retries, retry_delay, and retry_backoff.
        """
        # Test custom configuration
        fetcher = YouTubeTranscriptFetcher(
            max_retries=5,
            retry_delay=0.5,
            retry_backoff=3.0,
        )

        assert fetcher.max_retries == 5
        assert fetcher.retry_delay == 0.5
        assert fetcher.retry_backoff == 3.0

        # Test default configuration
        default_fetcher = YouTubeTranscriptFetcher()

        assert default_fetcher.max_retries == 3
        assert default_fetcher.retry_delay == 1.0
        assert default_fetcher.retry_backoff == 2.0


# RED Phase Summary
"""
TDD Iteration 1 RED Phase Complete: 10 Failing Tests + 3 ParseError Tests

Test Coverage:
- P0 Core Functionality: 3 tests (fetch, error handling, preference logic)
- P0 Formatting: 2 tests (timestamps, LLM format)
- P0 Error Handling: 3 tests (invalid ID, rate limits, network)
- P0 Performance: 1 test (<30s requirement)
- P1 Integration: 1 test (Ollama LLM compatibility)
- P1 ParseError Handling: 3 tests (GitHub Issue #81 fix)

All tests should FAIL until GREEN Phase implementation.

Next: GREEN Phase implementation in src/ai/youtube_transcript_fetcher.py
"""
