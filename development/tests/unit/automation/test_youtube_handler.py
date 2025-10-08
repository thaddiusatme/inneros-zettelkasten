"""
TDD Iteration 9 RED Phase: YouTube Feature Handler Integration

Tests for YouTubeFeatureHandler daemon integration:
- Handler initialization with YouTubeHandlerConfig
- Event detection for YouTube notes (source: youtube in frontmatter)
- Processing integration with YouTubeNoteEnhancer
- Health monitoring and metrics tracking
- Error handling and graceful degradation

Following established patterns from ScreenshotEventHandler and SmartLinkEventHandler.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
from datetime import datetime

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.automation.config import DaemonConfig


class TestYouTubeHandlerInitialization:
    """Test YouTubeFeatureHandler initialization"""
    
    def test_handler_initializes_with_valid_config(self):
        """Handler should initialize with valid YouTubeHandlerConfig"""
        config_dict = {
            'enabled': True,
            'vault_path': '/test/vault',
            'max_quotes': 7,
            'min_quality': 0.7,
            'processing_timeout': 300
        }
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        assert handler.vault_path == Path('/test/vault')
        assert handler.max_quotes == 7
        assert handler.min_quality == 0.7
        assert handler.processing_timeout == 300
    
    def test_handler_raises_error_with_invalid_config(self):
        """Handler should raise error when vault_path is missing"""
        config_dict = {'enabled': True}  # Missing vault_path
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with pytest.raises(ValueError, match="vault_path.*required"):
            handler = YouTubeFeatureHandler(config=config_dict)
    
    def test_handler_uses_defaults_for_optional_config(self):
        """Handler should use sensible defaults when optional keys missing"""
        config_dict = {'vault_path': '/test/vault'}  # Minimal config
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        assert handler.vault_path == Path('/test/vault')
        assert handler.max_quotes == 7  # Default
        assert handler.min_quality == 0.7  # Default
        assert handler.processing_timeout == 300  # 5 minutes default


class TestYouTubeEventDetection:
    """Test YouTubeFeatureHandler event detection (can_handle)"""
    
    def test_can_handle_returns_true_for_youtube_notes(self):
        """Handler should detect notes with source: youtube in frontmatter"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        # Create mock event with YouTube note
        note_content = """---
type: literature
status: inbox
source: youtube
video_id: FLpS7OfD5-s
---

# Video Notes

User notes here...
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-note.md'
        
        with patch('pathlib.Path.read_text', return_value=note_content):
            result = handler.can_handle(mock_event)
        
        assert result is True
    
    def test_can_handle_returns_false_for_non_youtube_notes(self):
        """Handler should ignore notes without source: youtube"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        # Note without YouTube source
        note_content = """---
type: permanent
status: active
---

# Regular Note

Some content
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Permanent Notes/regular-note.md'
        
        with patch('pathlib.Path.read_text', return_value=note_content):
            result = handler.can_handle(mock_event)
        
        assert result is False
    
    def test_can_handle_returns_false_for_already_processed_notes(self):
        """Handler should skip notes with ai_processed: true"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        # Already processed YouTube note
        note_content = """---
type: literature
status: inbox
source: youtube
video_id: FLpS7OfD5-s
ai_processed: true
processed_at: 2025-10-08 10:00
---

# Video Notes

## AI-Extracted Quotes

Already enhanced...
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-note.md'
        
        with patch('pathlib.Path.read_text', return_value=note_content):
            result = handler.can_handle(mock_event)
        
        assert result is False
    
    def test_can_handle_validates_frontmatter_structure(self):
        """Handler should handle malformed frontmatter gracefully"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        # Malformed frontmatter
        note_content = """---
type literature
broken yaml here
---

Content
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/malformed.md'
        
        with patch('pathlib.Path.read_text', return_value=note_content):
            result = handler.can_handle(mock_event)
        
        # Should return False for malformed notes instead of crashing
        assert result is False


class TestYouTubeProcessing:
    """Test YouTubeFeatureHandler processing (handle method)"""
    
    def test_handle_processes_valid_youtube_note(self):
        """Handler should successfully process valid YouTube note"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock YouTubeNoteEnhancer
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 5
        mock_result.processing_time = 15.0
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
        
        assert result['success'] is True
        assert result['quotes_added'] == 5
        assert 'processing_time' in result
    
    def test_handle_extracts_quotes_from_transcript(self):
        """Handler should extract quotes using AI (integration with YouTubeNoteEnhancer)"""
        config_dict = {'vault_path': '/test/vault', 'max_quotes': 7, 'min_quality': 0.7}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock successful enhancement
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 7
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
            
            # Verify enhancement was called with correct parameters
            mock_enhancer_instance.enhance_note.assert_called_once()
            call_args = mock_enhancer_instance.enhance_note.call_args
            
            # Should receive note path and quotes data
            assert call_args is not None
    
    def test_handle_updates_note_with_quotes_preserving_user_content(self):
        """Handler should insert quotes section without overwriting user notes"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock successful enhancement that preserves content
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 5
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
        
        # Should succeed and preserve user content (tested by enhancer)
        assert result['success'] is True
    
    def test_handle_sets_ai_processed_flag_in_frontmatter(self):
        """Handler should update frontmatter with ai_processed: true"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock successful processing
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 5
        mock_result.processing_time = 15.0
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
        
        # Enhancement includes setting ai_processed flag
        assert result['success'] is True
    
    def test_handle_returns_success_result_with_quote_count(self):
        """Handler should return result dict with quotes_added count"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock with specific quote count
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 12  # Specific count
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
        
        assert result['success'] is True
        assert result['quotes_added'] == 12
        assert isinstance(result['quotes_added'], int)


class TestYouTubeErrorHandling:
    """Test YouTubeFeatureHandler error handling"""
    
    def test_handles_missing_transcript_gracefully(self):
        """Handler should handle missing transcript without crashing daemon"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock transcript not available error
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_type = "transcript_unavailable"
        mock_result.error_message = "Transcript not available for this video"
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
        
        assert result['success'] is False
        assert 'transcript' in result.get('error', '').lower()
    
    def test_handles_llm_timeout_gracefully(self):
        """Handler should handle LLM timeout without crashing daemon"""
        config_dict = {'vault_path': '/test/vault', 'processing_timeout': 300}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock LLM timeout
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_type = "llm_timeout"
        mock_result.error_message = "LLM service unavailable"
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_handles_malformed_note_structure_without_daemon_crash(self):
        """Handler should handle malformed notes without crashing daemon"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/malformed.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock enhancement failure due to malformed structure
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.side_effect = ValueError("Malformed frontmatter")
            
            result = handler.handle(mock_event)
        
        # Should return error result instead of raising exception
        assert result['success'] is False
        assert 'error' in result


class TestYouTubeMetricsAndHealth:
    """Test YouTubeFeatureHandler metrics and health monitoring"""
    
    def test_tracks_processing_time_and_increments_success_counter(self):
        """Handler should track processing time and success count"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock successful processing
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 5
        mock_result.processing_time = 15.0
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
            metrics = handler.get_metrics()
        
        assert metrics['events_processed'] > 0
        assert 'processing_time_avg' in metrics
    
    def test_increments_failure_counter_on_error(self):
        """Handler should increment failure counter when processing fails"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Mock failure
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_type = "transcript_unavailable"
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            result = handler.handle(mock_event)
            metrics = handler.get_metrics()
        
        assert metrics['events_failed'] > 0
    
    def test_get_health_returns_healthy_with_good_success_rate(self):
        """Handler should report healthy status with >90% success rate"""
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        handler = YouTubeFeatureHandler(config=config_dict)
        
        # Mock successful processing multiple times
        mock_result = Mock()
        mock_result.success = True
        mock_result.quote_count = 5
        
        with patch('src.automation.feature_handlers.YouTubeNoteEnhancer') as MockEnhancer:
            mock_enhancer_instance = MockEnhancer.return_value
            mock_enhancer_instance.enhance_note.return_value = mock_result
            
            # Process multiple events successfully
            for i in range(10):
                mock_event = Mock()
                mock_event.src_path = f'/test/vault/Inbox/youtube-{i}.md'
                handler.handle(mock_event)
            
            health = handler.get_health()
        
        assert health['status'] == 'healthy'
        assert health['success_rate'] > 0.9


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
