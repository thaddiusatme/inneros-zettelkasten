"""
TDD RED Phase: YouTube Rate Limit Handler Tests

Test suite driving implementation of exponential backoff retry logic
for YouTube transcript fetching with rate limit mitigation.

Expected to FAIL until GREEN phase implementation complete.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, call
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable


class RateLimitError(Exception):
    """Mock rate limit error for testing."""
    pass


class TestYouTubeRateLimitHandlerBasicRetry:
    """Test basic retry functionality."""

    def test_successful_fetch_on_first_attempt_no_retries(self):
        """Test that successful fetch on first attempt requires no retries."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 60,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        # Mock fetch function that succeeds immediately
        mock_fetch = Mock(return_value="transcript_data")
        
        with patch('time.sleep') as mock_sleep:
            result = handler.fetch_with_retry('video123', mock_fetch)
        
        assert result == "transcript_data"
        assert mock_fetch.call_count == 1
        assert mock_sleep.call_count == 0  # No retries needed
        assert handler.metrics['total_attempts'] == 1
        assert handler.metrics['succeeded'] == 1
        assert handler.metrics['rate_limited'] == 0

    def test_retry_with_exponential_backoff_success_on_third_attempt(self):
        """Test retry with exponential backoff, succeeding on 3rd attempt."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 60,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        # Mock fetch function: fail twice, succeed on third
        mock_fetch = Mock(side_effect=[
            RateLimitError("429 Too Many Requests"),
            RateLimitError("429 Too Many Requests"),
            "transcript_data"
        ])
        
        with patch('time.sleep') as mock_sleep:
            result = handler.fetch_with_retry('video123', mock_fetch)
        
        assert result == "transcript_data"
        assert mock_fetch.call_count == 3
        
        # Verify exponential backoff delays: 5s, 10s
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(5)  # First retry delay
        mock_sleep.assert_any_call(10)  # Second retry delay
        
        assert handler.metrics['total_attempts'] == 3
        assert handler.metrics['succeeded'] == 1
        assert handler.metrics['rate_limited'] == 2

    def test_max_retries_exhausted_all_attempts_fail(self):
        """Test that max retries limit is respected when all attempts fail."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 60,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        # Mock fetch function that always fails with rate limit
        mock_fetch = Mock(side_effect=RateLimitError("429 Too Many Requests"))
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(RateLimitError):
                handler.fetch_with_retry('video123', mock_fetch)
        
        # Should attempt max_retries + 1 times (initial + 3 retries)
        assert mock_fetch.call_count == 4
        
        # Should sleep 3 times (between attempts)
        assert mock_sleep.call_count == 3
        mock_sleep.assert_any_call(5)   # 1st retry
        mock_sleep.assert_any_call(10)  # 2nd retry  
        mock_sleep.assert_any_call(20)  # 3rd retry
        
        assert handler.metrics['total_attempts'] == 4
        assert handler.metrics['succeeded'] == 0
        assert handler.metrics['rate_limited'] == 4


class TestYouTubeRateLimitHandlerErrorClassification:
    """Test error classification and handling."""

    def test_immediate_failure_on_permanent_errors_no_retry(self):
        """Test that permanent errors fail immediately without retry."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 60,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        # Mock fetch function that raises permanent error
        mock_fetch = Mock(side_effect=VideoUnavailable("video_id"))
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(VideoUnavailable):
                handler.fetch_with_retry('video123', mock_fetch)
        
        # Should only attempt once (no retries for permanent errors)
        assert mock_fetch.call_count == 1
        assert mock_sleep.call_count == 0  # No retries
        
        assert handler.metrics['total_attempts'] == 1
        assert handler.metrics['succeeded'] == 0
        # Permanent errors don't increment rate_limited counter


class TestYouTubeRateLimitHandlerConfiguration:
    """Test configuration handling."""

    def test_configurable_retry_parameters(self):
        """Test that retry parameters can be customized via config."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        # Custom configuration with higher limits
        config = {
            'max_retries': 5,
            'base_delay': 10,
            'max_delay': 120,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        mock_fetch = Mock(side_effect=RateLimitError("429 Too Many Requests"))
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(RateLimitError):
                handler.fetch_with_retry('video123', mock_fetch)
        
        # Should attempt max_retries + 1 times (initial + 5 retries)
        assert mock_fetch.call_count == 6
        
        # First retry should use base_delay of 10
        assert mock_sleep.call_args_list[0] == call(10)

    def test_backoff_multiplier_customization(self):
        """Test that backoff multiplier affects delay progression."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 200,
            'backoff_multiplier': 3  # Higher multiplier
        }
        handler = YouTubeRateLimitHandler(config)
        
        mock_fetch = Mock(side_effect=RateLimitError("429 Too Many Requests"))
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(RateLimitError):
                handler.fetch_with_retry('video123', mock_fetch)
        
        # Verify multiplier=3 progression: 5s, 15s, 45s
        assert mock_sleep.call_args_list[0] == call(5)   # base * 3^0
        assert mock_sleep.call_args_list[1] == call(15)  # base * 3^1
        assert mock_sleep.call_args_list[2] == call(45)  # base * 3^2

    def test_max_delay_cap_enforcement(self):
        """Test that delays are capped at max_delay."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 5,
            'base_delay': 10,
            'max_delay': 30,  # Cap delays at 30s
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        mock_fetch = Mock(side_effect=RateLimitError("429 Too Many Requests"))
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(RateLimitError):
                handler.fetch_with_retry('video123', mock_fetch)
        
        # Verify delays respect max_delay cap
        # Expected: 10, 20, 30, 30, 30 (capped at 30)
        assert mock_sleep.call_args_list[0] == call(10)
        assert mock_sleep.call_args_list[1] == call(20)
        assert mock_sleep.call_args_list[2] == call(30)  # Would be 40, capped to 30
        assert mock_sleep.call_args_list[3] == call(30)  # Would be 80, capped to 30
        assert mock_sleep.call_args_list[4] == call(30)  # Would be 160, capped to 30


class TestYouTubeRateLimitHandlerMetrics:
    """Test metrics tracking."""

    def test_request_metrics_tracking_accurate(self):
        """Test that metrics accurately track attempts and outcomes."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 60,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        # 2 failures, then success
        mock_fetch = Mock(side_effect=[
            RateLimitError("429"),
            RateLimitError("429"),
            "transcript_data"
        ])
        
        with patch('time.sleep'):
            result = handler.fetch_with_retry('video123', mock_fetch)
        
        assert result == "transcript_data"
        assert handler.metrics['total_attempts'] == 3
        assert handler.metrics['rate_limited'] == 2
        assert handler.metrics['succeeded'] == 1
        
        # Calculate retry rate: 2/3 = 66.67%
        retry_rate = handler.metrics['rate_limited'] / handler.metrics['total_attempts']
        assert retry_rate == pytest.approx(0.6667, rel=0.01)


class TestYouTubeRateLimitHandlerThreadSafety:
    """Test thread safety of retry handler."""

    def test_thread_safe_retry_handling(self):
        """Test that concurrent requests don't interfere with each other."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        import threading
        
        config = {
            'max_retries': 3,
            'base_delay': 1,  # Short delays for test speed
            'max_delay': 10,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        results = []
        errors = []
        
        def fetch_video(video_id):
            try:
                mock_fetch = Mock(return_value=f"transcript_{video_id}")
                with patch('time.sleep'):
                    result = handler.fetch_with_retry(video_id, mock_fetch)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Launch 5 concurrent requests
        threads = [threading.Thread(target=fetch_video, args=(f"video{i}",)) 
                   for i in range(5)]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 5
        assert len(errors) == 0
        
        # Metrics should reflect all attempts
        assert handler.metrics['total_attempts'] == 5
        assert handler.metrics['succeeded'] == 5


class TestYouTubeRateLimitHandlerLogging:
    """Test logging behavior."""

    def test_logging_at_each_retry_attempt(self):
        """Test that each retry attempt is logged appropriately."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'max_delay': 60,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        mock_fetch = Mock(side_effect=[
            RateLimitError("429"),
            RateLimitError("429"),
            "transcript_data"
        ])
        
        with patch('time.sleep'), \
             patch('logging.Logger.info') as mock_info, \
             patch('logging.Logger.warning') as mock_warning:
            
            result = handler.fetch_with_retry('video123', mock_fetch)
        
        # Should log INFO for each retry
        assert mock_info.call_count >= 2  # At least 2 retry logs
        
        # Should not log WARNING on success
        assert mock_warning.call_count == 0
        
        # Verify log messages contain video_id and attempt number
        log_calls = [str(call) for call in mock_info.call_args_list]
        assert any('video123' in log for log in log_calls)


class TestYouTubeRateLimitHandlerIntegration:
    """Test integration with YouTubeFeatureHandler."""

    def test_integration_with_youtube_feature_handler(self):
        """Test that rate limit handler integrates with YouTubeFeatureHandler."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        from automation.feature_handlers import YouTubeFeatureHandler
        
        # Mock config matching YouTubeFeatureHandler.__init__() signature
        config = {
            'vault_path': '/tmp/test_vault',
            'max_quotes': 7,
            'min_quality': 0.7,
            'rate_limit': {
                'max_retries': 3,
                'base_delay': 5,
                'max_delay': 60,
                'backoff_multiplier': 2
            }
        }
        
        handler = YouTubeFeatureHandler(config)
        
        # Verify rate_limit_handler is instantiated
        assert hasattr(handler, 'rate_limit_handler')
        assert isinstance(handler.rate_limit_handler, YouTubeRateLimitHandler)
        
        # Test that transcript fetching uses rate limit handler
        with patch.object(handler.rate_limit_handler, 'fetch_with_retry') as mock_retry:
            mock_retry.return_value = [{'text': 'transcript'}]
            
            result = handler._fetch_transcript('video123')
            
            mock_retry.assert_called_once()
            assert result == [{'text': 'transcript'}]

    def test_graceful_degradation_on_total_failure(self):
        """Test that daemon remains stable when all retries fail."""
        from automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
        
        config = {
            'max_retries': 2,
            'base_delay': 1,
            'max_delay': 10,
            'backoff_multiplier': 2
        }
        handler = YouTubeRateLimitHandler(config)
        
        mock_fetch = Mock(side_effect=RateLimitError("429 Too Many Requests"))
        
        # Should raise exception but not crash
        with patch('time.sleep'):
            with pytest.raises(RateLimitError) as exc_info:
                handler.fetch_with_retry('video123', mock_fetch)
        
        # Exception message should be informative
        assert "429" in str(exc_info.value)
        
        # Handler should remain functional for next request
        mock_fetch_success = Mock(return_value="transcript_data")
        with patch('time.sleep'):
            result = handler.fetch_with_retry('video456', mock_fetch_success)
        
        assert result == "transcript_data"
