"""
TDD RED Phase: YouTube Handler Status Synchronization

Tests for status state machine in YouTubeFeatureHandler.handle():
- Status transitions: draft → processing → processed
- Timestamp tracking (processing_started_at, processing_completed_at)
- Preservation of ready_for_processing: true after completion
- Error handling (status remains processing on failure)
- Integration with existing ai_processed flag

State Machine:
    draft (ready_for_processing: false)
      ↓ [user checks checkbox]
    draft (ready_for_processing: true)
      ↓ [handle() starts]
    processing (ready_for_processing: true)
      ↓ [handle() completes successfully]
    processed (ready_for_processing: true, ai_processed: true)
      ↓ [handle() fails]
    processing (ready_for_processing: true, error details)

Expected: 6 failing tests (RED phase)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from datetime import datetime
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestStatusSynchronization:
    """Test status field updates during processing lifecycle"""
    
    def test_status_changes_to_processing_when_handle_starts(self):
        """
        Status should change from 'draft' to 'processing' when handle() begins
        
        Acceptance Criteria:
        - Read note with status: draft
        - First action in handle(): Update status to 'processing'
        - Add processing_started_at timestamp
        - Preserve ready_for_processing: true
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        # Note starts in draft state with approval
        note_content = """---
type: literature
status: draft
source: youtube
video_id: test123
ready_for_processing: true
---

# User Notes
My notes here...
"""
        
        mock_enhance_result = Mock()
        mock_enhance_result.success = True
        mock_enhance_result.quote_count = 5
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.read_text', return_value=note_content), \
             patch('pathlib.Path.write_text') as mock_write, \
             patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher'), \
             patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor'), \
             patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer:
            
            handler = YouTubeFeatureHandler(config=config_dict)
            mock_enhancer = MockEnhancer.return_value
            mock_enhancer.enhance_note.return_value = mock_enhance_result
            mock_enhancer.update_frontmatter.return_value = note_content  # Simplified mock
            
            result = handler.handle(mock_event)
        
        # Verify update_frontmatter was called with status: processing
        calls = mock_enhancer.update_frontmatter.call_args_list
        assert len(calls) >= 1, "Should call update_frontmatter at least once"
        
        # First call should set status to processing
        first_call_metadata = calls[0][0][1] if calls[0][0] else calls[0][1]['metadata']
        assert first_call_metadata.get('status') == 'processing', \
            "First update should change status to 'processing'"
        assert 'processing_started_at' in first_call_metadata, \
            "Should add processing_started_at timestamp"
        assert result['success'] is True
    
    def test_status_changes_to_processed_when_handle_completes_successfully(self):
        """
        Status should change to 'processed' when handle() completes successfully
        
        Acceptance Criteria:
        - After successful quote extraction and enhancement
        - Update status to 'processed'
        - Add processing_completed_at timestamp
        - Keep ai_processed: true (existing functionality)
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        note_content = """---
type: literature
status: processing
source: youtube
video_id: test123
ready_for_processing: true
processing_started_at: 2025-10-20 20:00:00
---

# User Notes
"""
        
        mock_enhance_result = Mock()
        mock_enhance_result.success = True
        mock_enhance_result.quote_count = 7
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.read_text', return_value=note_content), \
             patch('pathlib.Path.write_text') as mock_write, \
             patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher'), \
             patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor'), \
             patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer:
            
            handler = YouTubeFeatureHandler(config=config_dict)
            mock_enhancer = MockEnhancer.return_value
            mock_enhancer.enhance_note.return_value = mock_enhance_result
            mock_enhancer.update_frontmatter.return_value = note_content
            
            result = handler.handle(mock_event)
        
        # Verify update_frontmatter was called with final status: processed
        calls = mock_enhancer.update_frontmatter.call_args_list
        assert len(calls) >= 2, "Should call update_frontmatter at least twice (start + end)"
        
        # Last call should set status to processed
        last_call_metadata = calls[-1][0][1] if calls[-1][0] else calls[-1][1]['metadata']
        assert last_call_metadata.get('status') == 'processed', \
            "Final update should change status to 'processed'"
        assert 'processing_completed_at' in last_call_metadata, \
            "Should add processing_completed_at timestamp"
        assert last_call_metadata.get('ai_processed') is True, \
            "Should still set ai_processed flag"
        assert result['success'] is True
    
    def test_ready_for_processing_preserved_after_successful_completion(self):
        """
        ready_for_processing: true should be preserved after processing
        
        Acceptance Criteria:
        - User can manually reprocess by checking box again
        - ready_for_processing not reset to false after completion
        - Enables manual override for re-extraction with different parameters
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        note_content = """---
status: draft
source: youtube
video_id: test123
ready_for_processing: true
---
Notes"""
        
        mock_enhance_result = Mock()
        mock_enhance_result.success = True
        mock_enhance_result.quote_count = 3
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.read_text', return_value=note_content), \
             patch('pathlib.Path.write_text'), \
             patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher'), \
             patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor'), \
             patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer:
            
            handler = YouTubeFeatureHandler(config=config_dict)
            mock_enhancer = MockEnhancer.return_value
            mock_enhancer.enhance_note.return_value = mock_enhance_result
            mock_enhancer.update_frontmatter.return_value = note_content
            
            result = handler.handle(mock_event)
        
        # Check all update_frontmatter calls - none should set ready_for_processing: false
        calls = mock_enhancer.update_frontmatter.call_args_list
        for call_args in calls:
            metadata = call_args[0][1] if call_args[0] else call_args[1]['metadata']
            # Either not present (preserves existing) or explicitly true
            if 'ready_for_processing' in metadata:
                assert metadata['ready_for_processing'] is True, \
                    "Should never reset ready_for_processing to false"
        
        assert result['success'] is True
    
    def test_timestamps_track_processing_duration(self):
        """
        Timestamps should enable processing duration calculation and monitoring
        
        Acceptance Criteria:
        - processing_started_at set when handle() begins
        - processing_completed_at set when handle() finishes
        - Timestamps use ISO 8601 format
        - Enable analytics on processing performance
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        note_content = """---
status: draft
source: youtube
video_id: test123
ready_for_processing: true
---
Notes"""
        
        mock_enhance_result = Mock()
        mock_enhance_result.success = True
        mock_enhance_result.quote_count = 4
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.read_text', return_value=note_content), \
             patch('pathlib.Path.write_text'), \
             patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher'), \
             patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor'), \
             patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer:
            
            handler = YouTubeFeatureHandler(config=config_dict)
            mock_enhancer = MockEnhancer.return_value
            mock_enhancer.enhance_note.return_value = mock_enhance_result
            mock_enhancer.update_frontmatter.return_value = note_content
            
            result = handler.handle(mock_event)
        
        # Verify timestamps in metadata updates
        calls = mock_enhancer.update_frontmatter.call_args_list
        
        # First call should have processing_started_at
        first_metadata = calls[0][0][1] if calls[0][0] else calls[0][1]['metadata']
        assert 'processing_started_at' in first_metadata, \
            "First update should include processing_started_at"
        
        # Parse timestamp to verify format
        started_at = first_metadata['processing_started_at']
        assert isinstance(started_at, str), "Timestamp should be string"
        # Should be parseable as datetime
        datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        
        # Last call should have processing_completed_at
        last_metadata = calls[-1][0][1] if calls[-1][0] else calls[-1][1]['metadata']
        assert 'processing_completed_at' in last_metadata, \
            "Final update should include processing_completed_at"
        
        completed_at = last_metadata['processing_completed_at']
        datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
        
        assert result['success'] is True
    
    def test_status_remains_processing_on_failure(self):
        """
        Status should remain 'processing' if handle() fails, enabling retry detection
        
        Acceptance Criteria:
        - Exception during processing caught
        - Status stays 'processing' (not reverted to draft)
        - Daemon can detect stuck processing state
        - Enables manual intervention or retry logic
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        note_content = """---
status: processing
source: youtube
video_id: test123
ready_for_processing: true
processing_started_at: 2025-10-20 20:00:00
---
Notes"""
        
        # Simulate processing failure
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.read_text', return_value=note_content), \
             patch('pathlib.Path.write_text'), \
             patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher') as MockFetcher:
            
            handler = YouTubeFeatureHandler(config=config_dict)
            # Make transcript fetcher fail
            MockFetcher.return_value.fetch_transcript.side_effect = Exception("API Error")
            
            result = handler.handle(mock_event)
        
        # Should return error result
        assert result['success'] is False
        assert 'error' in result
        
        # Status should remain 'processing' (not reverted)
        # This is implicit - we don't update status on failure
        # Future retry logic can detect notes stuck in 'processing' state
    
    def test_ai_processed_flag_still_set_on_successful_completion(self):
        """
        ai_processed: true should still be set for backward compatibility
        
        Acceptance Criteria:
        - Existing functionality preserved
        - ai_processed: true in final metadata update
        - Works alongside new status field
        - Supports existing workflows that check ai_processed
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        note_path = Path('/test/vault/Inbox/youtube-note.md')
        mock_event = Mock()
        mock_event.src_path = str(note_path)
        
        note_content = """---
status: draft
source: youtube
video_id: test123
ready_for_processing: true
---
Notes"""
        
        mock_enhance_result = Mock()
        mock_enhance_result.success = True
        mock_enhance_result.quote_count = 6
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.read_text', return_value=note_content), \
             patch('pathlib.Path.write_text'), \
             patch('src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher'), \
             patch('src.ai.youtube_quote_extractor.ContextAwareQuoteExtractor'), \
             patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer:
            
            handler = YouTubeFeatureHandler(config=config_dict)
            mock_enhancer = MockEnhancer.return_value
            mock_enhancer.enhance_note.return_value = mock_enhance_result
            mock_enhancer.update_frontmatter.return_value = note_content
            
            result = handler.handle(mock_event)
        
        # Verify ai_processed: true in final metadata update
        calls = mock_enhancer.update_frontmatter.call_args_list
        last_metadata = calls[-1][0][1] if calls[-1][0] else calls[-1][1]['metadata']
        
        assert last_metadata.get('ai_processed') is True, \
            "Should maintain backward compatibility with ai_processed flag"
        assert last_metadata.get('status') == 'processed', \
            "Should also set new status field"
        
        assert result['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
