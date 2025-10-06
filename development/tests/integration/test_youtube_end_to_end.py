"""
TDD Iteration 4 - RED Phase: YouTube End-to-End CLI Integration Tests

Tests the complete YouTube processing pipeline:
URL → Transcript → Quotes → Formatted Markdown → File Creation

This integration test file drives the implementation of YouTubeProcessor,
which orchestrates all three existing components:
1. YouTubeTranscriptFetcher (TDD Iteration 1 ✅)
2. ContextAwareQuoteExtractor (TDD Iteration 2 ✅)
3. YouTubeTemplateFormatter (TDD Iteration 3 ✅)
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.youtube_processor import YouTubeProcessor


class TestYouTubeProcessorURLValidation:
    """Test YouTube URL validation and video ID extraction."""
    
    def test_extract_video_id_from_standard_url(self):
        """Should extract video ID from standard youtube.com URLs"""
        processor = YouTubeProcessor()
        
        # Standard format
        video_id = processor.extract_video_id("https://www.youtube.com/watch?v=FLpS7OfD5-s")
        assert video_id == "FLpS7OfD5-s"
        
        # Without www
        video_id = processor.extract_video_id("https://youtube.com/watch?v=FLpS7OfD5-s")
        assert video_id == "FLpS7OfD5-s"
        
        # With additional parameters
        video_id = processor.extract_video_id("https://www.youtube.com/watch?v=FLpS7OfD5-s&t=120s")
        assert video_id == "FLpS7OfD5-s"
    
    def test_extract_video_id_from_short_url(self):
        """Should extract video ID from youtu.be short URLs"""
        processor = YouTubeProcessor()
        
        # Short format
        video_id = processor.extract_video_id("https://youtu.be/FLpS7OfD5-s")
        assert video_id == "FLpS7OfD5-s"
        
        # With timestamp
        video_id = processor.extract_video_id("https://youtu.be/FLpS7OfD5-s?t=120")
        assert video_id == "FLpS7OfD5-s"
    
    def test_validate_url_format(self):
        """Should validate YouTube URL format"""
        processor = YouTubeProcessor()
        
        # Valid URLs
        assert processor.validate_url("https://www.youtube.com/watch?v=FLpS7OfD5-s") is True
        assert processor.validate_url("https://youtu.be/FLpS7OfD5-s") is True
        
        # Invalid URLs
        assert processor.validate_url("https://vimeo.com/12345") is False
        assert processor.validate_url("not a url") is False
        assert processor.validate_url("") is False
    
    def test_handle_invalid_video_id(self):
        """Should raise clear error for invalid video IDs"""
        processor = YouTubeProcessor()
        
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            processor.extract_video_id("https://example.com/video")


class TestYouTubeProcessorEndToEnd:
    """Test complete end-to-end processing pipeline."""
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    @patch('src.cli.youtube_processor.ContextAwareQuoteExtractor')
    @patch('src.cli.youtube_processor.YouTubeTemplateFormatter')
    def test_process_youtube_url_complete_pipeline(
        self, 
        mock_formatter_class,
        mock_extractor_class,
        mock_fetcher_class
    ):
        """Should process YouTube URL through complete pipeline"""
        # Setup mocks
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = {
            "video_id": "FLpS7OfD5-s",
            "transcript": [{"text": "AI is transforming", "start": 15.0, "duration": 2.5}],
            "metadata": {"title": "AI Video"}
        }
        mock_fetcher.format_for_llm.return_value = "[00:15] AI is transforming"
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {
            "quotes": [{
                "text": "AI is transforming",
                "timestamp": "00:15",
                "relevance_score": 0.85,
                "context": "Key insight",
                "category": "key-insight"
            }],
            "summary": "Video about AI",
            "key_themes": ["ai", "transformation"],
            "processing_time": 5.2
        }
        mock_extractor_class.return_value = mock_extractor
        
        mock_formatter = Mock()
        mock_formatter.format_template.return_value = {
            "markdown": "# Formatted Note\n\nContent here",
            "metadata": {"quote_count": 1}
        }
        mock_formatter_class.return_value = mock_formatter
        
        # Process video
        processor = YouTubeProcessor()
        result = processor.process_video("https://youtube.com/watch?v=FLpS7OfD5-s")
        
        # Verify pipeline executed
        assert result["success"] is True
        assert result["video_id"] == "FLpS7OfD5-s"
        assert "file_path" in result
        assert result["quotes_extracted"] == 1
        
        # Verify components called correctly
        mock_fetcher.fetch_transcript.assert_called_once_with("FLpS7OfD5-s")
        mock_extractor.extract_quotes.assert_called_once()
        mock_formatter.format_template.assert_called_once()
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    def test_process_with_user_context(self, mock_fetcher_class):
        """Should pass user context to quote extractor"""
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = {
            "video_id": "test123",
            "transcript": [{"text": "Content", "start": 0, "duration": 1}],
            "metadata": {"title": "Test"}
        }
        mock_fetcher.format_for_llm.return_value = "[00:00] Content"
        mock_fetcher_class.return_value = mock_fetcher
        
        with patch('src.cli.youtube_processor.ContextAwareQuoteExtractor') as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor.extract_quotes.return_value = {
                "quotes": [],
                "summary": "Summary",
                "key_themes": [],
                "processing_time": 1.0
            }
            mock_extractor_class.return_value = mock_extractor
            
            with patch('src.cli.youtube_processor.YouTubeTemplateFormatter'):
                processor = YouTubeProcessor()
                processor.process_video(
                    "https://youtube.com/watch?v=test123",
                    user_context="I'm interested in AI automation"
                )
                
                # Verify context passed to extractor
                call_args = mock_extractor.extract_quotes.call_args
                assert call_args[1]["user_context"] == "I'm interested in AI automation"


class TestYouTubeProcessorFileCreation:
    """Test file creation and metadata population."""
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    @patch('src.cli.youtube_processor.ContextAwareQuoteExtractor')
    @patch('src.cli.youtube_processor.YouTubeTemplateFormatter')
    def test_create_note_file_in_inbox(
        self,
        mock_formatter_class,
        mock_extractor_class,
        mock_fetcher_class
    ):
        """Should create note file in knowledge/Inbox/ with correct naming"""
        # Setup minimal mocks
        self._setup_mocks(mock_fetcher_class, mock_extractor_class, mock_formatter_class)
        
        processor = YouTubeProcessor(knowledge_dir=Path("/tmp/test_knowledge"))
        result = processor.process_video("https://youtube.com/watch?v=FLpS7OfD5-s")
        
        # Verify file path structure
        file_path = Path(result["file_path"])
        assert "Inbox" in str(file_path)
        assert file_path.name.startswith("youtube-")
        assert "FLpS7OfD5-s" in file_path.name
        assert file_path.suffix == ".md"
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    @patch('src.cli.youtube_processor.ContextAwareQuoteExtractor')
    @patch('src.cli.youtube_processor.YouTubeTemplateFormatter')
    def test_populate_frontmatter_metadata(
        self,
        mock_formatter_class,
        mock_extractor_class,
        mock_fetcher_class
    ):
        """Should populate YAML frontmatter with video metadata"""
        self._setup_mocks(mock_fetcher_class, mock_extractor_class, mock_formatter_class)
        
        processor = YouTubeProcessor(knowledge_dir=Path("/tmp/test_knowledge"))
        result = processor.process_video("https://youtube.com/watch?v=FLpS7OfD5-s")
        
        # Verify metadata populated
        assert result["metadata"]["video_id"] == "FLpS7OfD5-s"
        assert result["metadata"]["type"] == "literature"
        assert result["metadata"]["status"] == "inbox"
        assert "created" in result["metadata"]
    
    def _setup_mocks(self, mock_fetcher_class, mock_extractor_class, mock_formatter_class):
        """Helper to setup standard mocks"""
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = {
            "video_id": "FLpS7OfD5-s",
            "transcript": [{"text": "Content", "start": 0, "duration": 1}],
            "metadata": {"title": "Test Video"}
        }
        mock_fetcher.format_for_llm.return_value = "[00:00] Content"
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {
            "quotes": [],
            "summary": "Summary",
            "key_themes": ["test", "demo"],
            "processing_time": 1.0
        }
        mock_extractor_class.return_value = mock_extractor
        
        mock_formatter = Mock()
        mock_formatter.format_template.return_value = {
            "markdown": "# Test\n\nFormatted content",
            "metadata": {"quote_count": 0}
        }
        mock_formatter_class.return_value = mock_formatter


class TestYouTubeProcessorErrorHandling:
    """Test error handling for common failure scenarios."""
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    def test_handle_transcript_unavailable(self, mock_fetcher_class):
        """Should handle videos with no transcript gracefully"""
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.side_effect = Exception("Transcript not available")
        mock_fetcher_class.return_value = mock_fetcher
        
        processor = YouTubeProcessor()
        result = processor.process_video("https://youtube.com/watch?v=invalid123")
        
        assert result["success"] is False
        assert "error" in result
        assert "transcript" in result["error"].lower()
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    @patch('src.cli.youtube_processor.ContextAwareQuoteExtractor')
    def test_handle_llm_service_unavailable(self, mock_extractor_class, mock_fetcher_class):
        """Should handle LLM service unavailable error"""
        # Fetcher succeeds
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = {
            "video_id": "test123",
            "transcript": [{"text": "Content", "start": 0, "duration": 1}],
            "metadata": {"title": "Test"}
        }
        mock_fetcher.format_for_llm.return_value = "[00:00] Content"
        mock_fetcher_class.return_value = mock_fetcher
        
        # Extractor fails
        mock_extractor = Mock()
        mock_extractor.extract_quotes.side_effect = Exception("LLM service unavailable")
        mock_extractor_class.return_value = mock_extractor
        
        processor = YouTubeProcessor()
        result = processor.process_video("https://youtube.com/watch?v=test123")
        
        assert result["success"] is False
        assert "error" in result
        assert "llm" in result["error"].lower() or "service" in result["error"].lower()


class TestYouTubeProcessorPerformance:
    """Test performance characteristics of the pipeline."""
    
    @patch('src.cli.youtube_processor.YouTubeTranscriptFetcher')
    @patch('src.cli.youtube_processor.ContextAwareQuoteExtractor')
    @patch('src.cli.youtube_processor.YouTubeTemplateFormatter')
    def test_processing_time_tracking(
        self,
        mock_formatter_class,
        mock_extractor_class,
        mock_fetcher_class
    ):
        """Should track processing time for each component"""
        # Setup mocks with timing
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = {
            "video_id": "test123",
            "transcript": [{"text": "Content", "start": 0, "duration": 1}],
            "metadata": {"title": "Test"},
            "fetch_time": 2.4
        }
        mock_fetcher.format_for_llm.return_value = "[00:00] Content"
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {
            "quotes": [],
            "summary": "Summary",
            "key_themes": [],
            "processing_time": 8.2
        }
        mock_extractor_class.return_value = mock_extractor
        
        mock_formatter = Mock()
        mock_formatter.format_youtube_note.return_value = "Content"
        mock_formatter_class.return_value = mock_formatter
        
        processor = YouTubeProcessor()
        result = processor.process_video("https://youtube.com/watch?v=test123")
        
        # Verify timing data collected
        assert "timing" in result
        assert result["timing"]["total"] > 0
        assert "fetch" in result["timing"]
        assert "extraction" in result["timing"]
        assert "formatting" in result["timing"]
