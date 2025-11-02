"""
Tests for YouTube Integration in LegacyWorkflowManagerAdapter.

TDD Iteration 1: scan_youtube_notes() method implementation
- RED: Tests expecting AttributeError (method doesn't exist yet)
- GREEN: Minimal implementation returning YouTube notes from Inbox
- REFACTOR: Extract helpers, improve error handling
"""

import pytest
from pathlib import Path
from src.ai.workflow_manager_adapter import LegacyWorkflowManagerAdapter


class TestYouTubeAdapterIntegration:
    """Test YouTube-specific methods in LegacyWorkflowManagerAdapter."""

    def test_scan_youtube_notes_method_exists(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() method exists on adapter.
        
        Expected to FAIL with AttributeError until GREEN phase.
        """
        # Arrange
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        
        # Act & Assert
        assert hasattr(adapter, 'scan_youtube_notes'), \
            "LegacyWorkflowManagerAdapter should have scan_youtube_notes() method"

    def test_scan_youtube_notes_returns_empty_list_when_no_notes(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() returns empty list when Inbox is empty.
        
        Expected to FAIL until GREEN phase implementation.
        """
        # Arrange
        inbox_dir = tmp_path / "Inbox"
        inbox_dir.mkdir()
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        
        # Act
        result = adapter.scan_youtube_notes()
        
        # Assert
        assert isinstance(result, list), "Should return a list"
        assert len(result) == 0, "Should return empty list when no YouTube notes"

    def test_scan_youtube_notes_finds_youtube_note_with_correct_frontmatter(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() finds notes with 'source: youtube' frontmatter.
        
        Expected to FAIL until GREEN phase implementation.
        """
        # Arrange
        inbox_dir = tmp_path / "Inbox"
        inbox_dir.mkdir()
        
        youtube_note = inbox_dir / "test-youtube.md"
        youtube_note.write_text("""---
type: literature
source: youtube
video_id: test123
url: https://www.youtube.com/watch?v=test123
---

# Test YouTube Note
""")
        
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        
        # Act
        result = adapter.scan_youtube_notes()
        
        # Assert
        assert len(result) == 1, "Should find 1 YouTube note"
        note_path, metadata = result[0]
        assert note_path.name == "test-youtube.md"
        assert metadata.get('source') == 'youtube'
        assert metadata.get('video_id') == 'test123'

    def test_scan_youtube_notes_ignores_non_youtube_notes(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() ignores notes without YouTube source.
        
        Expected to FAIL until GREEN phase implementation.
        """
        # Arrange
        inbox_dir = tmp_path / "Inbox"
        inbox_dir.mkdir()
        
        # Create regular note
        regular_note = inbox_dir / "regular.md"
        regular_note.write_text("""---
type: fleeting
---

# Regular Note
""")
        
        # Create YouTube note
        youtube_note = inbox_dir / "youtube.md"
        youtube_note.write_text("""---
type: literature
source: youtube
video_id: abc123
---

# YouTube Note
""")
        
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        
        # Act
        result = adapter.scan_youtube_notes()
        
        # Assert
        assert len(result) == 1, "Should find only YouTube note, not regular note"
        note_path, _ = result[0]
        assert note_path.name == "youtube.md"

    def test_scan_youtube_notes_handles_malformed_frontmatter(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() handles notes with malformed YAML.
        
        Expected to FAIL until GREEN phase implementation.
        """
        # Arrange
        inbox_dir = tmp_path / "Inbox"
        inbox_dir.mkdir()
        
        malformed_note = inbox_dir / "malformed.md"
        malformed_note.write_text("""---
type: literature
source: youtube
invalid: yaml: structure: here
---

# Malformed Note
""")
        
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        
        # Act
        result = adapter.scan_youtube_notes()
        
        # Assert
        # Should gracefully skip malformed notes instead of crashing
        assert isinstance(result, list), "Should return list even with malformed notes"

    def test_scan_youtube_notes_excludes_backup_files(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() excludes backup files.
        
        Matches workflow_demo.py behavior:
        youtube_notes = [(path, meta) for path, meta in all_youtube_notes 
                        if "_backup_" not in path.name]
        
        Expected to FAIL until GREEN phase implementation.
        """
        # Arrange
        inbox_dir = tmp_path / "Inbox"
        inbox_dir.mkdir()
        
        # Create normal YouTube note
        youtube_note = inbox_dir / "youtube-note.md"
        youtube_note.write_text("""---
source: youtube
video_id: test123
---

# YouTube Note
""")
        
        # Create backup YouTube note
        backup_note = inbox_dir / "youtube-note_backup_20251101.md"
        backup_note.write_text("""---
source: youtube
video_id: test123
---

# Backup Note
""")
        
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        
        # Act
        result = adapter.scan_youtube_notes()
        
        # Assert
        assert len(result) == 1, "Should exclude backup files"
        note_path, _ = result[0]
        assert "_backup_" not in note_path.name

    def test_scan_youtube_notes_handles_missing_inbox(self, tmp_path):
        """
        RED: Test that scan_youtube_notes() handles missing Inbox directory gracefully.
        
        Expected to FAIL until GREEN phase implementation.
        """
        # Arrange
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(tmp_path))
        # Note: No Inbox directory created
        
        # Act
        result = adapter.scan_youtube_notes()
        
        # Assert
        assert isinstance(result, list), "Should return empty list when Inbox missing"
        assert len(result) == 0, "Should return empty list when Inbox missing"
