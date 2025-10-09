#!/usr/bin/env python3
"""
TDD RED Phase: YouTube Official API Fetcher Tests

Comprehensive test suite for YouTubeOfficialAPIFetcher class.
This replaces unofficial youtube-transcript-api with official YouTube Data API v3.

Test Coverage:
- P0-1: Basic transcript fetching via YouTube Data API v3
- P0-2: API integration with captions.list and captions.download
- P0-3: SRT parsing and format normalization
- P0-4: Error handling for YouTube API-specific errors
- P0-5: Interface compatibility with existing YouTubeTranscriptFetcher
- P0-6: Quota tracking (250 units per video)
- P0-7: API key validation and secure configuration
- P0-8: Preference for manual transcripts over auto-generated
- P0-9: Graceful handling of quota exceeded scenarios
- P0-10: Integration with YouTubeFeatureHandler

Author: InnerOS Zettelkasten Team
Version: 1.0.0 (TDD Iteration 1 RED Phase)
"""
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from googleapiclient.errors import HttpError
from googleapiclient.http import HttpRequest

# Import will fail until we create the module (expected in RED phase)
try:
    from development.src.ai.youtube_official_api_fetcher import (
        YouTubeOfficialAPIFetcher,
        QuotaExceededError,
        TranscriptNotAvailableError,
        InvalidVideoIdError
    )
except ImportError:
    # Expected to fail in RED phase - tests should fail appropriately
    YouTubeOfficialAPIFetcher = None
    QuotaExceededError = Exception
    TranscriptNotAvailableError = Exception
    InvalidVideoIdError = Exception


class TestYouTubeOfficialAPIFetcherInitialization:
    """Test suite for YouTubeOfficialAPIFetcher initialization and API key validation"""
    
    def test_initialization_with_valid_api_key(self):
        """Test successful initialization with valid API key"""
        # RED: This test should fail because YouTubeOfficialAPIFetcher doesn't exist yet
        assert YouTubeOfficialAPIFetcher is not None, "YouTubeOfficialAPIFetcher class not implemented"
        
        fetcher = YouTubeOfficialAPIFetcher(api_key="test_api_key_12345")
        
        assert fetcher is not None
        assert hasattr(fetcher, 'api_key')
        assert hasattr(fetcher, 'quota_used')
        assert fetcher.quota_used == 0
    
    def test_initialization_without_api_key_raises_error(self):
        """Test that missing API key raises clear error"""
        # RED: Should fail - class doesn't exist
        assert YouTubeOfficialAPIFetcher is not None
        
        with pytest.raises(ValueError) as exc_info:
            YouTubeOfficialAPIFetcher(api_key=None)
        
        assert "api key" in str(exc_info.value).lower()
        assert "youtube_api_key" in str(exc_info.value).lower()
    
    def test_initialization_with_empty_api_key_raises_error(self):
        """Test that empty API key raises clear error"""
        # RED: Should fail - class doesn't exist
        assert YouTubeOfficialAPIFetcher is not None
        
        with pytest.raises(ValueError) as exc_info:
            YouTubeOfficialAPIFetcher(api_key="")
        
        assert "api key" in str(exc_info.value).lower()


class TestYouTubeOfficialAPIFetcherBasicFetching:
    """Test suite for basic transcript fetching functionality"""
    
    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance for testing"""
        if YouTubeOfficialAPIFetcher is None:
            pytest.skip("YouTubeOfficialAPIFetcher not implemented yet")
        return YouTubeOfficialAPIFetcher(api_key="test_api_key_12345")
    
    @pytest.fixture
    def mock_youtube_service(self):
        """Create mock YouTube API service"""
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        return service, captions
    
    def test_fetch_transcript_success(self, fetcher, mock_youtube_service):
        """Test successful transcript fetch via YouTube Data API v3"""
        # RED: Should fail - fetch_transcript method doesn't exist
        service, captions = mock_youtube_service
        
        # Mock captions.list() response (50 units)
        list_request = MagicMock()
        list_request.execute.return_value = {
            'items': [
                {
                    'id': 'caption_track_123',
                    'snippet': {
                        'language': 'en',
                        'trackKind': 'standard',  # manual transcript
                        'name': 'English'
                    }
                }
            ]
        }
        captions.list.return_value = list_request
        
        # Mock captions.download() response (200 units)
        download_request = MagicMock()
        download_request.execute.return_value = b"""1
00:00:00,000 --> 00:00:02,500
Hello world

2
00:00:02,500 --> 00:00:05,000
This is a test transcript
"""
        captions.download.return_value = download_request
        
        # Patch the YouTube API service
        with patch.object(fetcher, 'service', service):
            result = fetcher.fetch_transcript("dQw4w9WgXcQ")
        
        # Verify API calls
        captions.list.assert_called_once_with(
            part='snippet',
            videoId='dQw4w9WgXcQ'
        )
        captions.download.assert_called_once_with(
            id='caption_track_123',
            tfmt='srt'
        )
        
        # Verify result format matches existing fetcher
        assert result['video_id'] == 'dQw4w9WgXcQ'
        assert 'transcript' in result
        assert isinstance(result['transcript'], list)
        assert len(result['transcript']) == 2
        assert result['transcript'][0]['text'] == 'Hello world'
        assert result['transcript'][0]['start'] == 0.0
        assert 'duration' in result['transcript'][0]
        assert result['is_manual'] is True
        assert result['language'] == 'en'
    
    def test_fetch_transcript_prefers_manual_over_autogenerated(self, fetcher, mock_youtube_service):
        """Test that manual transcripts are preferred over auto-generated"""
        # RED: Should fail - preference logic doesn't exist
        service, captions = mock_youtube_service
        
        # Mock captions.list() with both manual and auto-generated
        list_request = MagicMock()
        list_request.execute.return_value = {
            'items': [
                {
                    'id': 'auto_caption_123',
                    'snippet': {
                        'language': 'en',
                        'trackKind': 'asr',  # auto-generated
                        'name': 'English (auto-generated)'
                    }
                },
                {
                    'id': 'manual_caption_456',
                    'snippet': {
                        'language': 'en',
                        'trackKind': 'standard',  # manual
                        'name': 'English'
                    }
                }
            ]
        }
        captions.list.return_value = list_request
        
        download_request = MagicMock()
        download_request.execute.return_value = b"""1
00:00:00,000 --> 00:00:02,500
Manual transcript content
"""
        captions.download.return_value = download_request
        
        with patch.object(fetcher, 'service', service):
            result = fetcher.fetch_transcript("dQw4w9WgXcQ", prefer_manual=True)
        
        # Should choose manual_caption_456, not auto_caption_123
        captions.download.assert_called_once_with(
            id='manual_caption_456',
            tfmt='srt'
        )
        assert result['is_manual'] is True


class TestYouTubeOfficialAPIFetcherQuotaTracking:
    """Test suite for API quota tracking"""
    
    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance for testing"""
        if YouTubeOfficialAPIFetcher is None:
            pytest.skip("YouTubeOfficialAPIFetcher not implemented yet")
        return YouTubeOfficialAPIFetcher(api_key="test_api_key_12345")
    
    @pytest.fixture
    def mock_youtube_service(self):
        """Create mock YouTube API service"""
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        return service, captions
    
    def test_quota_tracking_single_video(self, fetcher, mock_youtube_service):
        """Verify 250 units charged per video (50 list + 200 download)"""
        # RED: Should fail - quota tracking doesn't exist
        service, captions = mock_youtube_service
        
        # Setup mocks
        list_request = MagicMock()
        list_request.execute.return_value = {
            'items': [{'id': 'caption_123', 'snippet': {'language': 'en', 'trackKind': 'standard'}}]
        }
        captions.list.return_value = list_request
        
        download_request = MagicMock()
        download_request.execute.return_value = b"1\n00:00:00,000 --> 00:00:02,500\nTest"
        captions.download.return_value = download_request
        
        initial_quota = fetcher.quota_used
        
        with patch.object(fetcher, 'service', service):
            fetcher.fetch_transcript("test_video_id")
        
        # Verify quota increment: 50 (list) + 200 (download) = 250 units
        assert fetcher.quota_used == initial_quota + 250
    
    def test_quota_tracking_multiple_videos(self, fetcher, mock_youtube_service):
        """Verify quota accumulates correctly across multiple fetches"""
        # RED: Should fail - quota tracking doesn't exist
        service, captions = mock_youtube_service
        
        # Setup mocks
        list_request = MagicMock()
        list_request.execute.return_value = {
            'items': [{'id': 'caption_123', 'snippet': {'language': 'en', 'trackKind': 'standard'}}]
        }
        captions.list.return_value = list_request
        
        download_request = MagicMock()
        download_request.execute.return_value = b"1\n00:00:00,000 --> 00:00:02,500\nTest"
        captions.download.return_value = download_request
        
        with patch.object(fetcher, 'service', service):
            fetcher.fetch_transcript("video_1")
            fetcher.fetch_transcript("video_2")
            fetcher.fetch_transcript("video_3")
        
        # 3 videos × 250 units = 750 units total
        assert fetcher.quota_used == 750


class TestYouTubeOfficialAPIFetcherErrorHandling:
    """Test suite for YouTube API error handling"""
    
    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance for testing"""
        if YouTubeOfficialAPIFetcher is None:
            pytest.skip("YouTubeOfficialAPIFetcher not implemented yet")
        return YouTubeOfficialAPIFetcher(api_key="test_api_key_12345")
    
    def test_handle_video_not_found(self, fetcher):
        """Test handling of 404 video not found error"""
        # RED: Should fail - error handling doesn't exist
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        
        # Mock HttpError 404
        list_request = MagicMock()
        resp = Mock()
        resp.status = 404
        resp.reason = 'Not Found'
        list_request.execute.side_effect = HttpError(resp=resp, content=b'Video not found')
        captions.list.return_value = list_request
        
        with patch.object(fetcher, 'service', service):
            with pytest.raises(InvalidVideoIdError) as exc_info:
                fetcher.fetch_transcript("invalid_video_id")
            
            assert "not found" in str(exc_info.value).lower()
    
    def test_handle_captions_disabled(self, fetcher):
        """Test handling of videos with captions disabled"""
        # RED: Should fail - error handling doesn't exist
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        
        # Mock empty captions list
        list_request = MagicMock()
        list_request.execute.return_value = {'items': []}
        captions.list.return_value = list_request
        
        with patch.object(fetcher, 'service', service):
            with pytest.raises(TranscriptNotAvailableError) as exc_info:
                fetcher.fetch_transcript("no_captions_video")
            
            assert "no transcript" in str(exc_info.value).lower() or "captions" in str(exc_info.value).lower()
    
    def test_handle_quota_exceeded(self, fetcher):
        """Test handling of quota exceeded (403) error"""
        # RED: Should fail - quota error handling doesn't exist
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        
        # Mock HttpError 403 (quota exceeded)
        list_request = MagicMock()
        resp = Mock()
        resp.status = 403
        resp.reason = 'Forbidden'
        list_request.execute.side_effect = HttpError(
            resp=resp, 
            content=b'{"error": {"code": 403, "message": "The request cannot be completed because you have exceeded your quota."}}'
        )
        captions.list.return_value = list_request
        
        with patch.object(fetcher, 'service', service):
            with pytest.raises(QuotaExceededError) as exc_info:
                fetcher.fetch_transcript("test_video_id")
            
            assert "quota" in str(exc_info.value).lower()
    
    def test_handle_invalid_api_key(self, fetcher):
        """Test handling of invalid API key (403) error"""
        # RED: Should fail - API key error handling doesn't exist
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        
        # Mock HttpError 403 (invalid key)
        list_request = MagicMock()
        resp = Mock()
        resp.status = 403
        resp.reason = 'Forbidden'
        list_request.execute.side_effect = HttpError(
            resp=resp,
            content=b'{"error": {"code": 403, "message": "API key not valid."}}'
        )
        captions.list.return_value = list_request
        
        with patch.object(fetcher, 'service', service):
            with pytest.raises(Exception) as exc_info:
                fetcher.fetch_transcript("test_video_id")
            
            assert "api key" in str(exc_info.value).lower()


class TestYouTubeOfficialAPIFetcherFormatCompatibility:
    """Test suite for format compatibility with existing YouTubeTranscriptFetcher"""
    
    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance for testing"""
        if YouTubeOfficialAPIFetcher is None:
            pytest.skip("YouTubeOfficialAPIFetcher not implemented yet")
        return YouTubeOfficialAPIFetcher(api_key="test_api_key_12345")
    
    def test_format_for_llm_compatibility(self, fetcher):
        """Test that format_for_llm produces same output as existing fetcher"""
        # RED: Should fail - format_for_llm doesn't exist
        transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 2.5},
            {"text": "This is a test", "start": 2.5, "duration": 3.0},
            {"text": "Final segment", "start": 5.5, "duration": 2.0}
        ]
        
        result = fetcher.format_for_llm(transcript)
        
        # Should match existing format: [MM:SS] text
        expected = "[00:00] Hello world\n[00:02] This is a test\n[00:05] Final segment"
        assert result == expected
    
    def test_format_timestamp_compatibility(self, fetcher):
        """Test that timestamp formatting matches existing fetcher"""
        # RED: Should fail - format_timestamp doesn't exist
        assert fetcher.format_timestamp(0.0) == "00:00"
        assert fetcher.format_timestamp(90.5) == "01:30"
        assert fetcher.format_timestamp(3661.0) == "61:01"
    
    def test_fetch_result_structure_matches_existing(self, fetcher):
        """Test that fetch_transcript returns same structure as existing fetcher"""
        # RED: Should fail - return structure doesn't match
        service = MagicMock()
        captions = MagicMock()
        service.captions.return_value = captions
        
        list_request = MagicMock()
        list_request.execute.return_value = {
            'items': [{'id': 'caption_123', 'snippet': {'language': 'en', 'trackKind': 'standard'}}]
        }
        captions.list.return_value = list_request
        
        download_request = MagicMock()
        download_request.execute.return_value = b"1\n00:00:00,000 --> 00:00:02,500\nTest content"
        captions.download.return_value = download_request
        
        with patch.object(fetcher, 'service', service):
            result = fetcher.fetch_transcript("test_video_id")
        
        # Must have exact same keys as existing fetcher
        required_keys = {'video_id', 'transcript', 'is_manual', 'language'}
        assert set(result.keys()) == required_keys
        
        # Transcript entries must have same structure
        assert all(
            set(entry.keys()) == {'text', 'start', 'duration'}
            for entry in result['transcript']
        )


class TestYouTubeOfficialAPIFetcherSRTParsing:
    """Test suite for SRT format parsing"""
    
    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance for testing"""
        if YouTubeOfficialAPIFetcher is None:
            pytest.skip("YouTubeOfficialAPIFetcher not implemented yet")
        return YouTubeOfficialAPIFetcher(api_key="test_api_key_12345")
    
    def test_parse_srt_format(self, fetcher):
        """Test parsing of SRT subtitle format"""
        # RED: Should fail - SRT parsing doesn't exist
        srt_content = b"""1
00:00:00,000 --> 00:00:02,500
First subtitle line

2
00:00:02,500 --> 00:00:05,000
Second subtitle line
With multiple lines

3
00:00:05,000 --> 00:00:08,500
Third subtitle
"""
        
        # This method doesn't exist yet but will be needed
        transcript = fetcher._parse_srt(srt_content)
        
        assert len(transcript) == 3
        assert transcript[0]['text'] == 'First subtitle line'
        assert transcript[0]['start'] == 0.0
        assert transcript[0]['duration'] == 2.5
        
        assert transcript[1]['text'] == 'Second subtitle line\nWith multiple lines'
        assert transcript[1]['start'] == 2.5
        assert transcript[1]['duration'] == 2.5
    
    def test_parse_srt_handles_hours(self, fetcher):
        """Test SRT parsing with hour timestamps"""
        # RED: Should fail - hour handling doesn't exist
        srt_content = b"""1
01:30:00,000 --> 01:30:05,500
Content after 90 minutes
"""
        
        transcript = fetcher._parse_srt(srt_content)
        
        # 1 hour 30 minutes = 5400 seconds
        assert transcript[0]['start'] == 5400.0
        assert transcript[0]['duration'] == 5.5


# Additional integration test placeholder
class TestYouTubeOfficialAPIFetcherIntegration:
    """Integration tests with YouTubeFeatureHandler"""
    
    def test_integration_with_feature_handler_placeholder(self):
        """Placeholder for integration testing with feature handler"""
        # RED: This will be implemented after basic functionality works
        # For now, just ensure we have the placeholder
        pytest.skip("Integration test - implement after GREEN phase")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
