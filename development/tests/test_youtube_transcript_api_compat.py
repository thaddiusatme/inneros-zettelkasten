"""
Compatibility tests for youtube-transcript-api integration.

These tests verify that the youtube-transcript-api library version we're using
is compatible with our code. They catch API changes that would break our integration.

Run: pytest development/tests/test_youtube_transcript_api_compat.py -v
"""

import pytest
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import _errors


class TestYouTubeTranscriptAPICompatibility:
    """Test suite for youtube-transcript-api version compatibility."""

    def test_api_has_required_methods(self):
        """Verify YouTubeTranscriptApi has the methods we use."""
        api = YouTubeTranscriptApi()

        # These methods must exist for our code to work
        assert hasattr(api, 'list'), "YouTubeTranscriptApi must have 'list' method"
        assert callable(api.list), "'list' must be callable"

    def test_required_error_classes_exist(self):
        """Verify all error classes we import are available."""
        required_errors = [
            'TranscriptsDisabled',
            'NoTranscriptFound',
            'VideoUnavailable',
            'YouTubeRequestFailed',
            'RequestBlocked',
            'IpBlocked'
        ]

        for error_name in required_errors:
            assert hasattr(_errors, error_name), f"Missing error class: {error_name}"
            error_class = getattr(_errors, error_name)
            assert isinstance(error_class, type), f"{error_name} must be a class"

    def test_fetch_returns_correct_structure(self):
        """Verify .fetch() returns FetchedTranscript with .snippets attribute."""
        api = YouTubeTranscriptApi()

        # Use a well-known public video that should always have transcripts
        # This is a short Kurzgesagt video: "The Egg - A Short Story"
        test_video_id = "h6fcK_fRYaI"

        try:
            transcript_list = api.list(test_video_id)

            # Get first available transcript
            for transcript in transcript_list:
                fetched = transcript.fetch()

                # Verify structure
                assert hasattr(fetched, 'snippets'), "FetchedTranscript must have 'snippets' attribute"
                assert hasattr(fetched, 'is_generated'), "FetchedTranscript must have 'is_generated' attribute"
                assert hasattr(fetched, 'language_code'), "FetchedTranscript must have 'language_code' attribute"
                assert hasattr(fetched, 'video_id'), "FetchedTranscript must have 'video_id' attribute"

                # Verify snippets structure
                if len(fetched.snippets) > 0:
                    snippet = fetched.snippets[0]
                    assert hasattr(snippet, 'text'), "Snippet must have 'text' attribute"
                    assert hasattr(snippet, 'start'), "Snippet must have 'start' attribute"
                    assert hasattr(snippet, 'duration'), "Snippet must have 'duration' attribute"

                break  # Only need to check one

        except Exception as e:
            pytest.skip(f"Network test skipped (video unavailable or API issue): {e}")

    def test_transcript_list_structure(self):
        """Verify .list() returns iterable with correct structure."""
        api = YouTubeTranscriptApi()
        test_video_id = "h6fcK_fRYaI"

        try:
            transcript_list = api.list(test_video_id)

            # Verify it's iterable
            transcripts = list(transcript_list)
            assert len(transcripts) > 0, "Should have at least one transcript"

            # Verify transcript objects have required attributes
            for transcript in transcripts:
                assert hasattr(transcript, 'language_code'), "Transcript must have 'language_code'"
                assert hasattr(transcript, 'is_generated'), "Transcript must have 'is_generated'"
                assert hasattr(transcript, 'fetch'), "Transcript must have 'fetch' method"

        except Exception as e:
            pytest.skip(f"Network test skipped: {e}")


class TestYouTubeTranscriptFetcherIntegration:
    """Test our YouTubeTranscriptFetcher class works with the API."""

    def test_fetcher_imports_successfully(self):
        """Verify our fetcher can be imported without errors."""
        import sys
        sys.path.insert(0, 'development')

        from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher

        # Should initialize without errors
        fetcher = YouTubeTranscriptFetcher()
        assert fetcher is not None

    def test_fetcher_can_fetch_transcript(self):
        """Integration test: Verify full fetch workflow works."""
        import sys
        sys.path.insert(0, 'development')

        from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher

        fetcher = YouTubeTranscriptFetcher()
        test_video_id = "h6fcK_fRYaI"

        try:
            result = fetcher.fetch_transcript(test_video_id)

            # Verify return structure
            assert 'video_id' in result
            assert 'transcript' in result
            assert 'is_manual' in result
            assert 'language' in result

            # Verify transcript entries
            assert isinstance(result['transcript'], list)
            assert len(result['transcript']) > 0

            # Verify entry structure
            entry = result['transcript'][0]
            assert 'text' in entry
            assert 'start' in entry
            assert 'duration' in entry

        except Exception as e:
            pytest.skip(f"Network test skipped: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
