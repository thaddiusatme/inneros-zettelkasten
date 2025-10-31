"""
TDD RED Phase: YouTube Global Rate Limiting (Issue #29)

Tests for 60-second global cooldown between ANY YouTube API requests
to prevent rate limiting and file watching loop bugs.

CRITICAL: This is GLOBAL rate limiting (all requests), not per-note cooldown.

Expected to FAIL until implementation complete.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestYouTubeGlobalRateLimiting:
    """Test global 60-second rate limiting across all YouTube API requests."""

    def test_first_request_proceeds_immediately(self, tmp_path):
        """First API request should proceed without waiting."""
        from automation.youtube_api import create_youtube_blueprint
        from automation.feature_handlers import YouTubeFeatureHandler
        from flask import Flask

        # Setup
        config = {
            "vault_path": str(tmp_path),
            "max_quotes": 7,
            "min_quality": 0.7,
        }
        handler = YouTubeFeatureHandler(config)

        # Create test note
        note_path = tmp_path / "test.md"
        note_path.write_text(
            """---
video_id: test123
---
Test content"""
        )

        # Mock the handler's processing
        with patch.object(handler, "handle", return_value={"success": True}):
            # First request should not wait
            start_time = time.time()
            blueprint = create_youtube_blueprint(handler)

            app = Flask(__name__)
            app.register_blueprint(blueprint, url_prefix="/api/youtube")

            with app.test_client() as client:
                response = client.post(
                    "/api/youtube/process", json={"note_path": str(note_path)}
                )

            elapsed = time.time() - start_time

        assert response.status_code == 202
        assert elapsed < 1.0  # Should be instant

    def test_second_request_within_60s_rejected(self, tmp_path):
        """Second API request within 60 seconds should be rejected with 429."""
        from automation.youtube_api import create_youtube_blueprint
        from automation.feature_handlers import YouTubeFeatureHandler
        from flask import Flask

        # Use unique cache directory for this test to avoid interference
        test_vault = tmp_path / "test_vault"
        test_vault.mkdir()

        config = {
            "vault_path": str(test_vault),
            "max_quotes": 7,
            "min_quality": 0.7,
        }
        handler = YouTubeFeatureHandler(config)

        # Create test notes
        note1 = test_vault / "test1.md"
        note2 = test_vault / "test2.md"
        note1.write_text("---\nvideo_id: test1\n---\nContent")
        note2.write_text("---\nvideo_id: test2\n---\nContent")

        # Clear any existing rate limit state
        cache_dir = tmp_path / ".automation" / "cache"
        if cache_dir.exists():
            import shutil

            shutil.rmtree(cache_dir)

        blueprint = create_youtube_blueprint(handler)
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix="/api/youtube")

        with patch.object(handler, "handle", return_value={"success": True}):
            with app.test_client() as client:
                # First request
                resp1 = client.post(
                    "/api/youtube/process", json={"note_path": str(note1)}
                )

                # Second request immediately after
                resp2 = client.post(
                    "/api/youtube/process", json={"note_path": str(note2)}
                )

        assert resp1.status_code == 202
        assert resp2.status_code == 429
        assert "rate_limit" in resp2.get_json()["error"]

    def test_rate_limit_tracking_file_created(self, tmp_path):
        """Rate limit tracking should create persistent file."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # Record a request
        rate_limiter.record_request()

        # Check tracking file exists
        tracking_file = cache_dir / "youtube_last_request.txt"
        assert tracking_file.exists()

        # Verify timestamp format
        timestamp = int(tracking_file.read_text())
        assert timestamp > 0
        assert timestamp <= int(time.time())

    def test_can_proceed_respects_60_second_cooldown(self, tmp_path):
        """can_proceed should return False within 60 seconds."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # First request
        assert rate_limiter.can_proceed() is True
        rate_limiter.record_request()

        # Immediate second request
        assert rate_limiter.can_proceed() is False

        # Check time remaining
        remaining = rate_limiter.seconds_until_next_allowed()
        assert 55 < remaining <= 60

    def test_can_proceed_allows_after_60_seconds(self, tmp_path):
        """can_proceed should return True after 60 seconds."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # Simulate old request (61 seconds ago)
        tracking_file = cache_dir / "youtube_last_request.txt"
        cache_dir.mkdir(parents=True, exist_ok=True)
        old_timestamp = int(time.time()) - 61
        tracking_file.write_text(str(old_timestamp))

        # Should allow new request
        assert rate_limiter.can_proceed() is True

    def test_handle_429_error_implements_exponential_backoff(self, tmp_path):
        """429 errors should trigger exponential backoff (60s → 120s → 240s)."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # Test that 429 error updates tracking file
        rate_limiter.handle_429_error(attempt=1)

        # Should block next request
        assert rate_limiter.can_proceed() is False

        # Verify tracking file exists
        assert rate_limiter.tracking_file.exists()

        # Verify remaining time is reasonable (test records current time, so ~60s)
        remaining = rate_limiter.seconds_until_next_allowed()
        assert 55 <= remaining <= 60

    def test_rate_limit_events_logged(self, tmp_path, caplog):
        """Rate limit events should be logged with timestamps."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter
        import logging

        # Set log level to capture INFO logs
        caplog.set_level(logging.INFO, logger="automation.youtube_global_rate_limiter")

        cache_dir = tmp_path / ".automation" / "cache"
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # Record request
        rate_limiter.record_request()

        # Try to proceed again (should fail and log)
        can_proceed = rate_limiter.can_proceed()

        assert can_proceed is False
        # Should have logged rate limit event (check for "Rate limit active" message)
        assert any("rate limit" in record.message.lower() for record in caplog.records)

    def test_integration_with_youtube_api_blueprint(self, tmp_path):
        """YouTube API blueprint should use global rate limiter."""
        from automation.youtube_api import create_youtube_blueprint
        from automation.feature_handlers import YouTubeFeatureHandler

        config = {
            "vault_path": str(tmp_path),
            "max_quotes": 7,
            "min_quality": 0.7,
        }
        handler = YouTubeFeatureHandler(config)
        blueprint = create_youtube_blueprint(handler)

        # Blueprint should have rate_limiter attached
        assert hasattr(blueprint, "rate_limiter")

        # Rate limiter should be configured
        assert blueprint.rate_limiter.cooldown_seconds == 60

    def test_multiple_rapid_requests_all_blocked(self, tmp_path):
        """Multiple rapid requests should all be blocked after first."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # First request succeeds
        assert rate_limiter.can_proceed() is True
        rate_limiter.record_request()

        # Next 5 requests all blocked
        for i in range(5):
            assert rate_limiter.can_proceed() is False

    def test_rate_limiter_survives_process_restart(self, tmp_path):
        """Rate limiter state should persist across process restarts."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"

        # First process: make request
        limiter1 = YouTubeGlobalRateLimiter(cache_dir)
        limiter1.record_request()
        del limiter1

        # Second process: check rate limit still active
        limiter2 = YouTubeGlobalRateLimiter(cache_dir)
        assert limiter2.can_proceed() is False

    def test_error_handling_missing_cache_directory(self, tmp_path):
        """Missing cache directory should be created automatically."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache_nonexistent"

        # Should not raise error
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)

        # Should create directory
        assert cache_dir.exists()

        # Should work normally
        assert rate_limiter.can_proceed() is True
        rate_limiter.record_request()

    def test_malformed_tracking_file_handled_gracefully(self, tmp_path):
        """Malformed tracking file should be handled without crashing."""
        from automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter

        cache_dir = tmp_path / ".automation" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create malformed tracking file
        tracking_file = cache_dir / "youtube_last_request.txt"
        tracking_file.write_text("not_a_number")

        # Should handle gracefully
        rate_limiter = YouTubeGlobalRateLimiter(cache_dir)
        assert rate_limiter.can_proceed() is True  # Treat as no previous request
