#!/usr/bin/env python3
"""
TDD RED Phase: YouTube Handler Note Linking Integration Tests

Tests for Phase 3: Note Linking Integration
- Adds transcript references to note frontmatter
- Inserts transcript links in note body
- Preserves existing content and structure
- Handles errors gracefully

Author: InnerOS Zettelkasten Team
Phase: 3 (Note Linking Integration)
TDD Cycle: RED Phase - All tests should FAIL initially
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from datetime import datetime
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.automation.feature_handlers import YouTubeFeatureHandler
from src.ai.youtube_transcript_saver import YouTubeTranscriptSaver
from src.utils.frontmatter import parse_frontmatter, build_frontmatter


class TestYouTubeHandlerNoteLinking(unittest.TestCase):
    """
    RED Phase: Tests for transcript link integration in parent notes.
    
    These tests verify that after successful quote insertion, the handler
    adds bidirectional links between the note and transcript file.
    """
    
    def setUp(self):
        """Set up test environment with temporary vault."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        self.inbox_path = self.vault_path / "Inbox"
        self.inbox_path.mkdir(parents=True)
        self.transcripts_dir = self.vault_path / "Media" / "Transcripts"
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_handler_adds_transcript_to_frontmatter(self):
        """
        RED: Test that handler adds transcript_file field to note frontmatter.
        
        After successful quote insertion, the handler should:
        1. Read the note file
        2. Parse existing frontmatter
        3. Add transcript_file: [[youtube-{id}-{date}]] field
        4. Preserve all existing frontmatter fields
        5. Write updated content back
        """
        # Create test note with frontmatter
        note_path = self.inbox_path / "test-youtube-note.md"
        original_content = """---
created: 2025-10-18 00:00
type: fleeting
status: inbox
tags: [youtube, test]
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

# Test YouTube Note

Original content here.
"""
        note_path.write_text(original_content)
        
        # Mock dependencies
        with patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer, \
             patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver') as MockSaver:
            
            # Setup mocks
            mock_enhancer = MockEnhancer.return_value
            mock_result = Mock()
            mock_result.success = True
            mock_result.quote_count = 3
            mock_enhancer.enhance_note.return_value = mock_result
            
            mock_saver = MockSaver.return_value
            transcript_path = self.transcripts_dir / "youtube-dQw4w9WgXcQ-2025-10-18.md"
            mock_saver.save_transcript.return_value = transcript_path
            
            # Create handler and process
            from src.automation.feature_handlers import YouTubeFeatureHandler
            handler = YouTubeFeatureHandler(
                vault_path=self.vault_path,
                processing_timeout=30,
                metrics_tracker=Mock()
            )
            
            result = handler.handle(note_path)
            
            # Verify success
            self.assertTrue(result['success'])
            
            # RED: This should FAIL - frontmatter update not implemented yet
            updated_content = note_path.read_text()
            self.assertIn('transcript_file:', updated_content)
            self.assertIn('[[youtube-dQw4w9WgXcQ-2025-10-18]]', updated_content)
            
            # Verify original fields preserved
            self.assertIn('created: 2025-10-18 00:00', updated_content)
            self.assertIn('type: fleeting', updated_content)
            self.assertIn('tags: [youtube, test]', updated_content)
    
    def test_handler_inserts_transcript_link_in_body(self):
        """
        RED: Test that handler inserts transcript link in note body after title.
        
        Should insert: **Full Transcript**: [[youtube-{id}-{date}]]
        Position: After the first heading, before other content
        """
        # Create test note
        note_path = self.inbox_path / "test-youtube-note.md"
        original_content = """---
created: 2025-10-18 00:00
type: fleeting
status: inbox
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

# Amazing Video Title

This is the original content.

## Section 1

More content here.
"""
        note_path.write_text(original_content)
        
        # Mock dependencies
        with patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer, \
             patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver') as MockSaver:
            
            # Setup mocks
            mock_enhancer = MockEnhancer.return_value
            mock_result = Mock()
            mock_result.success = True
            mock_result.quote_count = 2
            mock_enhancer.enhance_note.return_value = mock_result
            
            mock_saver = MockSaver.return_value
            transcript_path = self.transcripts_dir / "youtube-dQw4w9WgXcQ-2025-10-18.md"
            mock_saver.save_transcript.return_value = transcript_path
            
            # Create handler and process
            from src.automation.feature_handlers import YouTubeFeatureHandler
            handler = YouTubeFeatureHandler(
                vault_path=self.vault_path,
                processing_timeout=30,
                metrics_tracker=Mock()
            )
            
            result = handler.handle(note_path)
            
            # Verify success
            self.assertTrue(result['success'])
            
            # RED: This should FAIL - body link insertion not implemented yet
            updated_content = note_path.read_text()
            self.assertIn('**Full Transcript**:', updated_content)
            self.assertIn('[[youtube-dQw4w9WgXcQ-2025-10-18]]', updated_content)
            
            # Verify link is after title but before original content
            lines = updated_content.split('\n')
            title_idx = next(i for i, line in enumerate(lines) if line.startswith('# Amazing Video Title'))
            transcript_link_idx = next(i for i, line in enumerate(lines) if '**Full Transcript**:' in line)
            content_idx = next(i for i, line in enumerate(lines) if 'This is the original content' in line)
            
            self.assertGreater(transcript_link_idx, title_idx)
            self.assertLess(transcript_link_idx, content_idx)
    
    def test_handler_preserves_existing_content(self):
        """
        RED: Test that handler preserves all existing note content.
        
        Must preserve:
        - All original text
        - Quote sections added by enhancer
        - Existing headings and structure
        - Spacing and formatting
        """
        # Create test note
        note_path = self.inbox_path / "test-youtube-note.md"
        original_content = """---
created: 2025-10-18 00:00
type: fleeting
status: inbox
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

# Test Video

Important user notes here.

## My Thoughts

These are my reflections.

## References

- Link 1
- Link 2
"""
        note_path.write_text(original_content)
        
        # Mock dependencies
        with patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer, \
             patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver') as MockSaver:
            
            # Setup mocks
            mock_enhancer = MockEnhancer.return_value
            mock_result = Mock()
            mock_result.success = True
            mock_result.quote_count = 1
            mock_enhancer.enhance_note.return_value = mock_result
            
            mock_saver = MockSaver.return_value
            transcript_path = self.transcripts_dir / "youtube-dQw4w9WgXcQ-2025-10-18.md"
            mock_saver.save_transcript.return_value = transcript_path
            
            # Create handler and process
            from src.automation.feature_handlers import YouTubeFeatureHandler
            handler = YouTubeFeatureHandler(
                vault_path=self.vault_path,
                processing_timeout=30,
                metrics_tracker=Mock()
            )
            
            result = handler.handle(note_path)
            
            # Verify success
            self.assertTrue(result['success'])
            
            # RED: Verify content preservation
            updated_content = note_path.read_text()
            self.assertIn('Important user notes here.', updated_content)
            self.assertIn('## My Thoughts', updated_content)
            self.assertIn('These are my reflections.', updated_content)
            self.assertIn('## References', updated_content)
            self.assertIn('- Link 1', updated_content)
            self.assertIn('- Link 2', updated_content)
    
    def test_handler_handles_linking_failure_gracefully(self):
        """
        RED: Test that linking failures don't crash the handler.
        
        If frontmatter/body update fails:
        - Handler should continue (quotes already inserted)
        - Should log warning
        - Should return success=True (main operation succeeded)
        - Should include linking_failed indicator in result
        """
        # Create test note
        note_path = self.inbox_path / "test-youtube-note.md"
        original_content = """---
created: 2025-10-18 00:00
type: fleeting
status: inbox
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

# Test Video

Content here.
"""
        note_path.write_text(original_content)
        
        # Mock dependencies - simulate error during frontmatter update
        with patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer, \
             patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver') as MockSaver, \
             patch('src.utils.frontmatter.parse_frontmatter', side_effect=Exception("Simulated parse error")):
            
            # Setup mocks
            mock_enhancer = MockEnhancer.return_value
            mock_result = Mock()
            mock_result.success = True
            mock_result.quote_count = 2
            mock_enhancer.enhance_note.return_value = mock_result
            
            mock_saver = MockSaver.return_value
            transcript_path = self.transcripts_dir / "youtube-dQw4w9WgXcQ-2025-10-18.md"
            mock_saver.save_transcript.return_value = transcript_path
            
            # Create handler and process
            handler = YouTubeFeatureHandler(
                vault_path=self.vault_path,
                processing_timeout=30,
                metrics_tracker=Mock()
            )
            
            # Should not raise exception
            result = handler.handle(note_path)
            
            # RED: Handler should still report success (quotes were added)
            self.assertTrue(result['success'])
            
            # RED: Should indicate linking had issues
            self.assertIn('transcript_link_added', result)
            self.assertFalse(result['transcript_link_added'])
    
    def test_bidirectional_navigation_works(self):
        """
        RED: Test end-to-end bidirectional linking.
        
        Verifies:
        1. Transcript file contains: parent_note: [[note-name]]
        2. Note file contains: transcript_file: [[youtube-{id}-{date}]]
        3. Note body contains: **Full Transcript**: [[youtube-{id}-{date}]]
        """
        # Create test note
        note_path = self.inbox_path / "test-youtube-note.md"
        original_content = """---
created: 2025-10-18 00:00
type: fleeting
status: inbox
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

# Test Video

Content here.
"""
        note_path.write_text(original_content)
        
        # Create actual transcript file (not mocked)
        transcript_content = """---
created: 2025-10-18 00:00
type: literature
status: published
video_id: dQw4w9WgXcQ
parent_note: [[test-youtube-note]]
---

# YouTube Transcript: Test Video

Transcript content here.
"""
        transcript_path = self.transcripts_dir / "youtube-dQw4w9WgXcQ-2025-10-18.md"
        transcript_path.write_text(transcript_content)
        
        # Mock dependencies
        with patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer, \
             patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver') as MockSaver:
            
            # Setup mocks
            mock_enhancer = MockEnhancer.return_value
            mock_result = Mock()
            mock_result.success = True
            mock_result.quote_count = 1
            mock_enhancer.enhance_note.return_value = mock_result
            
            mock_saver = MockSaver.return_value
            mock_saver.save_transcript.return_value = transcript_path
            
            # Create handler and process
            from src.automation.feature_handlers import YouTubeFeatureHandler
            handler = YouTubeFeatureHandler(
                vault_path=self.vault_path,
                processing_timeout=30,
                metrics_tracker=Mock()
            )
            
            result = handler.handle(note_path)
            
            # Verify success
            self.assertTrue(result['success'])
            
            # RED: Verify bidirectional linking
            # 1. Transcript → Note (already done by Phase 1)
            transcript_text = transcript_path.read_text()
            self.assertIn('parent_note: [[test-youtube-note]]', transcript_text)
            
            # 2. Note → Transcript (frontmatter)
            note_text = note_path.read_text()
            self.assertIn('transcript_file: [[youtube-dQw4w9WgXcQ-2025-10-18]]', note_text)
            
            # 3. Note → Transcript (body)
            self.assertIn('**Full Transcript**: [[youtube-dQw4w9WgXcQ-2025-10-18]]', note_text)
    
    def test_linking_with_various_note_structures(self):
        """
        RED: Test linking works with different note structures.
        
        Edge cases:
        - Notes without titles
        - Notes with multiple H1 headings
        - Notes with existing sections
        - Minimal notes
        """
        # Test case 1: Note without title
        note_path = self.inbox_path / "no-title-note.md"
        original_content = """---
created: 2025-10-18 00:00
type: fleeting
status: inbox
video_url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
---

Just some content without a title heading.
"""
        note_path.write_text(original_content)
        
        # Mock dependencies
        with patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer') as MockEnhancer, \
             patch('src.ai.youtube_transcript_saver.YouTubeTranscriptSaver') as MockSaver:
            
            # Setup mocks
            mock_enhancer = MockEnhancer.return_value
            mock_result = Mock()
            mock_result.success = True
            mock_result.quote_count = 1
            mock_enhancer.enhance_note.return_value = mock_result
            
            mock_saver = MockSaver.return_value
            transcript_path = self.transcripts_dir / "youtube-dQw4w9WgXcQ-2025-10-18.md"
            mock_saver.save_transcript.return_value = transcript_path
            
            # Create handler and process
            from src.automation.feature_handlers import YouTubeFeatureHandler
            handler = YouTubeFeatureHandler(
                vault_path=self.vault_path,
                processing_timeout=30,
                metrics_tracker=Mock()
            )
            
            result = handler.handle(note_path)
            
            # Verify success
            self.assertTrue(result['success'])
            
            # RED: Should still add transcript link (at start of body if no title)
            updated_content = note_path.read_text()
            self.assertIn('**Full Transcript**: [[youtube-dQw4w9WgXcQ-2025-10-18]]', updated_content)
            
            # Should preserve original content
            self.assertIn('Just some content without a title heading.', updated_content)


if __name__ == '__main__':
    unittest.main()
