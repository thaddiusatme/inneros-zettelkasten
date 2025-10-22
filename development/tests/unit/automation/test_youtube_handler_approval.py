"""
TDD RED Phase: YouTube Handler Approval Detection (PBI-002)

Tests for YouTubeFeatureHandler approval gate functionality:
- Handler respects ready_for_processing: true for approved notes
- Handler skips ready_for_processing: false for draft notes
- Handler handles missing ready_for_processing field gracefully
- Handler preserves existing ai_processed logic
- Handler handles string values gracefully

Following TDD methodology from updated-development-workflow.md:
RED → GREEN → REFACTOR → COMMIT → LESSONS LEARNED
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestYouTubeHandlerApprovalDetection:
    """Test YouTubeFeatureHandler approval gate (ready_for_processing field)"""
    
    def test_can_handle_returns_true_for_approved_note(self):
        """
        Handler should process notes with ready_for_processing: true
        
        Acceptance Criteria:
        - Note has source: youtube
        - Note has ready_for_processing: true
        - Note does NOT have ai_processed: true
        - Expected: can_handle() returns True
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Approved YouTube note ready for processing
        note_content = """---
type: literature
status: inbox
source: youtube
video_id: FLpS7OfD5-s
ready_for_processing: true
---

# My YouTube Notes

User has checked the approval checkbox.
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-approved.md'
        
        # Mock YouTubeTranscriptSaver to avoid directory creation
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.read_text', return_value=note_content):
            handler = YouTubeFeatureHandler(config=config_dict)
            result = handler.can_handle(mock_event)
        
        assert result is True, "Should process approved YouTube notes"
    
    def test_can_handle_returns_false_for_draft_note(self):
        """
        Handler should skip notes with ready_for_processing: false
        
        Acceptance Criteria:
        - Note has source: youtube
        - Note has ready_for_processing: false
        - Expected: can_handle() returns False
        - Expected: Debug log message about skipping draft
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Draft YouTube note not ready for processing
        note_content = """---
type: literature
status: draft
source: youtube
video_id: FLpS7OfD5-s
ready_for_processing: false
---

# My YouTube Notes

User is still taking notes, not ready for AI processing yet.
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-draft.md'
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.read_text', return_value=note_content):
            handler = YouTubeFeatureHandler(config=config_dict)
            result = handler.can_handle(mock_event)
        
        assert result is False, "Should skip draft YouTube notes (ready_for_processing: false)"
    
    def test_can_handle_returns_false_for_missing_approval_field(self):
        """
        Handler should skip notes without ready_for_processing field
        
        Acceptance Criteria:
        - Note has source: youtube
        - Note does NOT have ready_for_processing field
        - Expected: can_handle() returns False (safe default)
        - Expected: Debug log message about missing approval
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Legacy YouTube note without approval field
        note_content = """---
type: literature
status: inbox
source: youtube
video_id: FLpS7OfD5-s
---

# My YouTube Notes

Old note created before approval feature was added.
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-legacy.md'
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.read_text', return_value=note_content):
            handler = YouTubeFeatureHandler(config=config_dict)
            result = handler.can_handle(mock_event)
        
        assert result is False, "Should skip notes without ready_for_processing field (safe default)"
    
    def test_can_handle_preserves_ai_processed_logic(self):
        """
        Handler should respect ai_processed: true even if ready_for_processing: true
        
        Acceptance Criteria:
        - Note has source: youtube
        - Note has ready_for_processing: true
        - Note has ai_processed: true
        - Expected: can_handle() returns False (already processed takes priority)
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Already processed note (should not reprocess even if approved)
        note_content = """---
type: literature
status: inbox
source: youtube
video_id: FLpS7OfD5-s
ready_for_processing: true
ai_processed: true
processed_at: 2025-10-20 19:00
---

# My YouTube Notes

## AI-Extracted Quotes

Already processed, should not process again.
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-already-processed.md'
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.read_text', return_value=note_content):
            handler = YouTubeFeatureHandler(config=config_dict)
            result = handler.can_handle(mock_event)
        
        assert result is False, "Should skip already processed notes (ai_processed check takes priority)"
    
    def test_can_handle_handles_string_values_gracefully(self):
        """
        Handler should handle ready_for_processing: "true" (string) gracefully
        
        Acceptance Criteria:
        - Note has source: youtube
        - Note has ready_for_processing: "true" (string, not boolean)
        - Expected: can_handle() handles gracefully (implementation choice: accept or reject)
        - Expected: No exceptions or crashes
        """
        config_dict = {'vault_path': '/test/vault'}
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Edge case: string value instead of boolean
        note_content = """---
type: literature
status: inbox
source: youtube
video_id: FLpS7OfD5-s
ready_for_processing: "true"
---

# My YouTube Notes

Edge case: YAML parsed as string instead of boolean.
"""
        mock_event = Mock()
        mock_event.src_path = '/test/vault/Inbox/youtube-string-value.md'
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.read_text', return_value=note_content):
            handler = YouTubeFeatureHandler(config=config_dict)
            # Should not raise exception
            result = handler.can_handle(mock_event)
        
        # Implementation note: can return True or False, but must not crash
        assert isinstance(result, bool), "Should return boolean without crashing on string values"


class TestYouTubeHandlerApprovalHelperMethod:
    """Test _is_ready_for_processing() helper method"""
    
    def test_helper_returns_true_for_approved_frontmatter(self):
        """Helper should return (True, reason) when ready_for_processing: true"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        frontmatter = {
            'source': 'youtube',
            'ready_for_processing': True
        }
        
        is_ready, reason = handler._is_ready_for_processing(frontmatter)
        assert is_ready is True
        assert reason == 'approved'
    
    def test_helper_returns_false_for_draft_frontmatter(self):
        """Helper should return (False, reason) when ready_for_processing: false"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        frontmatter = {
            'source': 'youtube',
            'ready_for_processing': False
        }
        
        is_ready, reason = handler._is_ready_for_processing(frontmatter)
        assert is_ready is False
        assert reason == 'explicitly set to false'
    
    def test_helper_returns_false_for_missing_field(self):
        """Helper should return (False, reason) when ready_for_processing field missing"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        frontmatter = {
            'source': 'youtube'
            # No ready_for_processing field
        }
        
        is_ready, reason = handler._is_ready_for_processing(frontmatter)
        assert is_ready is False
        assert reason == 'field missing'
    
    def test_helper_handles_string_true_value(self):
        """Helper should handle ready_for_processing: 'true' (string) gracefully"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        frontmatter = {
            'source': 'youtube',
            'ready_for_processing': 'true'  # String instead of boolean
        }
        
        # Enhanced: Now handles string values and returns approval
        is_ready, reason = handler._is_ready_for_processing(frontmatter)
        assert is_ready is True
        assert reason == 'approved (string value)'
    
    def test_helper_handles_yes_string_value(self):
        """Helper should handle ready_for_processing: 'yes' (enhanced edge case)"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        # Test various "yes" formats
        for value in ['yes', 'Yes', 'YES', 'y', 'Y']:
            frontmatter = {'ready_for_processing': value}
            is_ready, reason = handler._is_ready_for_processing(frontmatter)
            assert is_ready is True, f"Failed for value: {value}"
            assert reason == 'approved (string value)'
    
    def test_helper_handles_numeric_one_value(self):
        """Helper should handle ready_for_processing: 1 (numeric edge case)"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        frontmatter = {'ready_for_processing': 1}
        is_ready, reason = handler._is_ready_for_processing(frontmatter)
        assert is_ready is True
        assert reason == 'approved (numeric value)'
    
    def test_helper_rejects_invalid_string_values(self):
        """Helper should reject invalid string values with descriptive reason"""
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        with patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver'):
            handler = YouTubeFeatureHandler(config={'vault_path': '/test/vault'})
        
        # Test invalid string values
        for value in ['pending', 'maybe', 'not yet', 'false']:
            frontmatter = {'ready_for_processing': value}
            is_ready, reason = handler._is_ready_for_processing(frontmatter)
            assert is_ready is False
            assert 'unsupported string value' in reason
            assert value in reason  # Should include the actual value in error
