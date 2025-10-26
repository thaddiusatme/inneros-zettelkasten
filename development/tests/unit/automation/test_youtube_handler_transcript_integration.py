#!/usr/bin/env python3
"""
YouTube Handler Transcript Integration Tests - TDD Phase 2 RED Phase

Tests for integrating YouTubeTranscriptSaver into YouTubeFeatureHandler.
These tests will initially FAIL as the integration hasn't been implemented yet.

This is the RED phase of TDD - we write failing tests first to drive implementation.

Test Coverage:
1. Handler initializes transcript saver correctly
2. Handler saves transcript after successful fetch
3. Handler returns transcript file path in results
4. Handler generates proper transcript wikilink
5. Handler handles transcript save failures gracefully

Author: InnerOS Zettelkasten Team
Date: 2025-10-17
TDD Phase: RED (Expected to FAIL - drives implementation)
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import tempfile
import shutil

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.automation.feature_handlers import YouTubeFeatureHandler
from src.ai.youtube_transcript_saver import YouTubeTranscriptSaver


class TestYouTubeHandlerTranscriptIntegration:
    """
    TDD RED Phase: Tests for transcript saver integration.
    
    These tests define the expected behavior before implementation.
    All tests should FAIL initially - this is intentional and correct.
    """

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault directory for testing."""
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir) / "knowledge"
        vault_path.mkdir(parents=True, exist_ok=True)

        # Create Media/Transcripts directory
        transcripts_dir = vault_path / "Media" / "Transcripts"
        transcripts_dir.mkdir(parents=True, exist_ok=True)

        yield vault_path

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def handler_config(self, temp_vault):
        """Create handler configuration with vault path."""
        return {
            'vault_path': str(temp_vault),
            'max_quotes': 5,
            'processing_timeout': 300,
            'cooldown_seconds': 60
        }

    @pytest.fixture
    def mock_transcript_result(self):
        """Mock transcript fetch result."""
        return {
            "transcript": [
                {"text": "Hello world", "start": 0.0, "duration": 2.0},
                {"text": "This is a test", "start": 2.5, "duration": 3.0}
            ],
            "video_id": "dQw4w9WgXcQ",
            "language": "en",
            "duration": 120.0
        }

    # ==========================================
    # TEST 1: Handler Initializes Transcript Saver
    # ==========================================
    def test_handler_initializes_transcript_saver(self, handler_config):
        """
        TEST 1 (RED): Handler should initialize YouTubeTranscriptSaver in __init__
        
        Expected Behavior:
        - Handler creates self.transcript_saver attribute
        - Saver is instance of YouTubeTranscriptSaver
        - Saver is initialized with correct vault_path
        
        Current Status: EXPECTED TO FAIL - feature not yet implemented
        """
        # Act
        handler = YouTubeFeatureHandler(config=handler_config)

        # Assert
        assert hasattr(handler, 'transcript_saver'), \
            "Handler should have transcript_saver attribute"

        assert isinstance(handler.transcript_saver, YouTubeTranscriptSaver), \
            "transcript_saver should be instance of YouTubeTranscriptSaver"

        # Verify vault path is correct
        expected_vault = Path(handler_config['vault_path'])
        assert handler.transcript_saver.vault_path == expected_vault, \
            f"Saver vault_path should be {expected_vault}"

    # ==========================================
    # TEST 2: Handler Saves Transcript After Fetch
    # ==========================================
    @patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher')
    @patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_handler_saves_transcript_after_fetch(
        self,
        mock_enhancer_class,
        mock_extractor_class,
        mock_fetcher_class,
        handler_config,
        temp_vault,
        mock_transcript_result
    ):
        """
        TEST 2 (RED): Handler should call save_transcript() after successful fetch
        
        Expected Behavior:
        - After fetching transcript, handler calls transcript_saver.save_transcript()
        - save_transcript() is called with correct video_id, transcript_data, metadata
        - save_transcript() is called BEFORE quote extraction
        
        Current Status: EXPECTED TO FAIL - feature not yet implemented
        """
        # Setup mocks
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = mock_transcript_result
        mock_fetcher.format_for_llm.return_value = "formatted transcript"
        mock_fetcher_class.return_value = mock_fetcher

        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {'quotes': []}
        mock_extractor_class.return_value = mock_extractor

        mock_enhancer = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 0
        mock_enhancer.enhance_note.return_value = mock_result
        mock_enhancer_class.return_value = mock_enhancer

        # Create test note
        note_path = temp_vault / "test-youtube-note.md"
        note_content = """---
type: literature
source: youtube
video_id: dQw4w9WgXcQ
created: 2025-10-17
---

# Test Video Note
"""
        note_path.write_text(note_content, encoding='utf-8')

        # Create mock event
        class MockEvent:
            def __init__(self, path):
                self.src_path = path

        event = MockEvent(note_path)

        # Act
        handler = YouTubeFeatureHandler(config=handler_config)

        # Patch transcript_saver.save_transcript to verify it's called
        with patch.object(handler.transcript_saver, 'save_transcript') as mock_save:
            expected_transcript_path = temp_vault / "Media" / "Transcripts" / "youtube-dQw4w9WgXcQ-2025-10-17.md"
            mock_save.return_value = expected_transcript_path

            result = handler.handle(event)

            # Assert save_transcript was called
            assert mock_save.called, "save_transcript() should be called"

            # Verify call arguments
            call_args = mock_save.call_args
            assert call_args is not None, "save_transcript() should have been called with arguments"

            # Check video_id
            assert call_args[1]['video_id'] == 'dQw4w9WgXcQ', \
                "save_transcript() should be called with correct video_id"

            # Check transcript_data
            assert 'transcript_data' in call_args[1], \
                "save_transcript() should be called with transcript_data"

            # Check metadata
            assert 'metadata' in call_args[1], \
                "save_transcript() should be called with metadata"

            # Check parent_note_name
            assert 'parent_note_name' in call_args[1], \
                "save_transcript() should be called with parent_note_name"

    # ==========================================
    # TEST 3: Handler Returns Transcript Path in Results
    # ==========================================
    @patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher')
    @patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_handler_returns_transcript_path(
        self,
        mock_enhancer_class,
        mock_extractor_class,
        mock_fetcher_class,
        handler_config,
        temp_vault,
        mock_transcript_result
    ):
        """
        TEST 3 (RED): Handler should return transcript_file path in results dict
        
        Expected Behavior:
        - Result dict includes 'transcript_file' key
        - transcript_file contains Path to saved transcript
        - All existing result keys are preserved (backward compatibility)
        
        Current Status: EXPECTED TO FAIL - feature not yet implemented
        """
        # Setup mocks (same as test 2)
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = mock_transcript_result
        mock_fetcher.format_for_llm.return_value = "formatted transcript"
        mock_fetcher_class.return_value = mock_fetcher

        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {'quotes': []}
        mock_extractor_class.return_value = mock_extractor

        mock_enhancer = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 3
        mock_enhancer.enhance_note.return_value = mock_result
        mock_enhancer_class.return_value = mock_enhancer

        # Create test note
        note_path = temp_vault / "test-youtube-note.md"
        note_content = """---
type: literature
source: youtube
video_id: abc123xyz
created: 2025-10-17
---

# Test Video Note
"""
        note_path.write_text(note_content, encoding='utf-8')

        class MockEvent:
            def __init__(self, path):
                self.src_path = path

        event = MockEvent(note_path)

        # Act
        handler = YouTubeFeatureHandler(config=handler_config)
        result = handler.handle(event)

        # Assert
        assert result is not None, "Handler should return result dict"
        assert 'transcript_file' in result, "Result should include 'transcript_file' key"

        # Verify transcript_file is a Path
        assert isinstance(result['transcript_file'], Path), \
            "transcript_file should be a Path object"

        # Verify transcript file exists
        assert result['transcript_file'].exists(), \
            "Transcript file should exist after processing"

        # Verify backward compatibility - existing keys should still be present
        assert 'success' in result, "Result should include 'success' key (backward compatibility)"
        assert 'quotes_added' in result, "Result should include 'quotes_added' key"
        assert 'processing_time' in result, "Result should include 'processing_time' key"

    # ==========================================
    # TEST 4: Handler Generates Transcript Wikilink
    # ==========================================
    @patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher')
    @patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_handler_generates_transcript_wikilink(
        self,
        mock_enhancer_class,
        mock_extractor_class,
        mock_fetcher_class,
        handler_config,
        temp_vault,
        mock_transcript_result
    ):
        """
        TEST 4 (RED): Handler should generate proper wikilink for transcript file
        
        Expected Behavior:
        - Result dict includes 'transcript_wikilink' key
        - Wikilink follows format: [[youtube-{video_id}-{date}]]
        - Wikilink is ready for note enhancer integration
        
        Current Status: EXPECTED TO FAIL - feature not yet implemented
        """
        # Setup mocks
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = mock_transcript_result
        mock_fetcher.format_for_llm.return_value = "formatted transcript"
        mock_fetcher_class.return_value = mock_fetcher

        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {'quotes': []}
        mock_extractor_class.return_value = mock_extractor

        mock_enhancer = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 0
        mock_enhancer.enhance_note.return_value = mock_result
        mock_enhancer_class.return_value = mock_enhancer

        # Create test note
        note_path = temp_vault / "test-youtube-note.md"
        note_content = """---
type: literature
source: youtube
video_id: test123
created: 2025-10-17
---

# Test Video
"""
        note_path.write_text(note_content, encoding='utf-8')

        class MockEvent:
            def __init__(self, path):
                self.src_path = path

        event = MockEvent(note_path)

        # Act
        handler = YouTubeFeatureHandler(config=handler_config)
        result = handler.handle(event)

        # Assert
        assert 'transcript_wikilink' in result, \
            "Result should include 'transcript_wikilink' key"

        # Verify wikilink format
        wikilink = result['transcript_wikilink']
        assert wikilink.startswith('[['), "Wikilink should start with '[[')"
        assert wikilink.endswith(']]'), "Wikilink should end with ']]'"
        assert 'youtube-test123-' in wikilink, \
            "Wikilink should contain video_id in format 'youtube-{id}-'"
        assert '2025-10-17' in wikilink, "Wikilink should contain date"

    # ==========================================
    # TEST 5: Handler Handles Save Failures Gracefully
    # ==========================================
    @patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher')
    @patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_handler_handles_transcript_save_failure(
        self,
        mock_enhancer_class,
        mock_extractor_class,
        mock_fetcher_class,
        handler_config,
        temp_vault,
        mock_transcript_result
    ):
        """
        TEST 5 (RED): Handler should handle transcript save failures gracefully
        
        Expected Behavior:
        - If save_transcript() raises exception, handler continues processing
        - Quote extraction still happens (transcript save failure doesn't block workflow)
        - Error is logged but doesn't crash handler
        - Result indicates transcript save failed but processing succeeded
        
        Current Status: EXPECTED TO FAIL - feature not yet implemented
        """
        # Setup mocks
        mock_fetcher = Mock()
        mock_fetcher.fetch_transcript.return_value = mock_transcript_result
        mock_fetcher.format_for_llm.return_value = "formatted transcript"
        mock_fetcher_class.return_value = mock_fetcher

        mock_extractor = Mock()
        mock_extractor.extract_quotes.return_value = {'quotes': [
            {'text': 'Test quote', 'timestamp': '00:00', 'context': 'test', 'relevance_score': 0.8}
        ]}
        mock_extractor_class.return_value = mock_extractor

        mock_enhancer = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 1
        mock_enhancer.enhance_note.return_value = mock_result
        mock_enhancer_class.return_value = mock_enhancer

        # Create test note
        note_path = temp_vault / "test-youtube-note.md"
        note_content = """---
type: literature
source: youtube
video_id: failtest
created: 2025-10-17
---

# Test Failure Handling
"""
        note_path.write_text(note_content, encoding='utf-8')

        class MockEvent:
            def __init__(self, path):
                self.src_path = path

        event = MockEvent(note_path)

        # Act
        handler = YouTubeFeatureHandler(config=handler_config)

        # Make save_transcript raise an exception
        with patch.object(handler.transcript_saver, 'save_transcript', side_effect=Exception("Disk full")):
            result = handler.handle(event)

        # Assert - Processing should still succeed
        assert result is not None, "Handler should return result even if transcript save fails"
        assert result['success'] is True, \
            "Handler should succeed even if transcript save fails (graceful degradation)"

        # Quotes should still be extracted
        assert result['quotes_added'] == 1, \
            "Quote extraction should succeed even if transcript save fails"

        # Transcript failure should be indicated
        assert 'transcript_error' in result or result.get('transcript_file') is None, \
            "Result should indicate transcript save failure"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
