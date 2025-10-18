#!/usr/bin/env python3
"""
TDD Iteration 1 RED Phase: YouTube Transcript Saver Tests

Tests for YouTubeTranscriptSaver class that saves complete video transcripts
as separate markdown files with bidirectional links.

Part of YouTube Transcript Archival System - Phase 1: Core Transcript Saver.

Following TDD methodology proven across 10+ successful iterations.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.youtube_transcript_saver import YouTubeTranscriptSaver


class TestYouTubeTranscriptSaverBasicFunctionality:
    """Test P0: Core transcript saving functionality"""
    
    def test_save_transcript_creates_file(self, tmp_path):
        """
        RED Phase Test 1: Save transcript creates markdown file
        
        Success case: Should create transcript file in Media/Transcripts/ directory
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        # Sample transcript data
        transcript_data = [
            {"text": "Hello world", "start": 0.0, "duration": 2.5},
            {"text": "This is a test", "start": 2.5, "duration": 3.0}
        ]
        
        metadata = {
            "video_id": "dQw4w9WgXcQ",
            "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "video_title": "Test Video",
            "duration": 5.5,
            "language": "en"
        }
        
        # Save transcript
        result_path = saver.save_transcript(
            video_id="dQw4w9WgXcQ",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="fleeting-youtube-test"
        )
        
        # Verify file was created
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert "dQw4w9WgXcQ" in result_path.name
        
        # Verify it's in correct directory
        assert result_path.parent.name == "Transcripts"
        assert result_path.parent.parent.name == "Media"
    
    def test_transcript_filename_format(self, tmp_path):
        """
        RED Phase Test 2: Verify transcript filename follows youtube-{id}-{date}.md pattern
        
        File naming convention: youtube-dQw4w9WgXcQ-2025-10-17.md
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        transcript_data = [{"text": "Test", "start": 0.0, "duration": 1.0}]
        metadata = {
            "video_id": "abc123XYZ",
            "video_url": "https://youtube.com/watch?v=abc123XYZ",
            "video_title": "Test",
            "duration": 1.0,
            "language": "en"
        }
        
        result_path = saver.save_transcript(
            video_id="abc123XYZ",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="test-note"
        )
        
        # Verify filename format: youtube-{video_id}-{YYYY-MM-DD}.md
        filename = result_path.name
        assert filename.startswith("youtube-abc123XYZ-")
        assert filename.endswith(".md")
        
        # Verify date format (YYYY-MM-DD)
        date_part = filename.replace("youtube-abc123XYZ-", "").replace(".md", "")
        assert len(date_part) == 10  # YYYY-MM-DD is 10 characters
        assert date_part.count("-") == 2  # Two dashes in date
    
    def test_transcript_frontmatter_structure(self, tmp_path):
        """
        RED Phase Test 3: Verify transcript frontmatter includes all required fields
        
        Required fields:
        - type: transcript
        - source: youtube
        - video_id
        - video_url
        - video_title
        - duration
        - transcript_length
        - fetched (timestamp)
        - parent_note (bidirectional link)
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        transcript_data = [
            {"text": "First line", "start": 0.0, "duration": 2.0},
            {"text": "Second line", "start": 2.0, "duration": 3.0}
        ]
        
        metadata = {
            "video_id": "testID123",
            "video_url": "https://youtube.com/watch?v=testID123",
            "video_title": "Amazing Test Video",
            "duration": 180.5,  # 3 minutes 0.5 seconds
            "language": "en"
        }
        
        result_path = saver.save_transcript(
            video_id="testID123",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="fleeting-youtube-amazing-video"
        )
        
        # Read and verify frontmatter
        content = result_path.read_text()
        
        # Check for required frontmatter fields
        assert "type: transcript" in content
        assert "source: youtube" in content
        assert "video_id: testID123" in content
        assert "video_url: https://youtube.com/watch?v=testID123" in content
        assert "video_title: Amazing Test Video" in content
        assert "duration:" in content  # Duration should be formatted
        assert "transcript_length: 2" in content  # 2 entries
        assert "fetched:" in content  # Should have timestamp
        assert "parent_note: fleeting-youtube-amazing-video" in content
    
    def test_format_timestamp_seconds_to_mmss(self, tmp_path):
        """
        RED Phase Test 4: Convert seconds to MM:SS timestamp format
        
        Examples:
        - 0.0 → "00:00"
        - 90.0 → "01:30"
        - 125.5 → "02:05"
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        # Test various timestamp conversions
        assert saver._format_timestamp(0.0) == "00:00"
        assert saver._format_timestamp(90.0) == "01:30"
        assert saver._format_timestamp(125.5) == "02:05"
        assert saver._format_timestamp(59.9) == "00:59"
        assert saver._format_timestamp(3600.0) == "60:00"  # 1 hour = 60 minutes
    
    def test_format_duration_with_hours(self, tmp_path):
        """
        RED Phase Test 5: Format duration as HH:MM:SS or MM:SS
        
        Examples:
        - 90 seconds → "1:30" (MM:SS)
        - 3661 seconds → "1:01:01" (HH:MM:SS)
        - 45 seconds → "0:45" (MM:SS)
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        # Test duration formatting
        assert saver._format_duration(90) == "1:30"
        assert saver._format_duration(3661) == "1:01:01"
        assert saver._format_duration(45) == "0:45"
        assert saver._format_duration(7200) == "2:00:00"
        assert saver._format_duration(125) == "2:05"
    
    def test_get_transcript_link(self, tmp_path):
        """
        RED Phase Test 6: Generate wikilink for transcript file
        
        Format: [[youtube-{video_id}-{date}]]
        Example: [[youtube-dQw4w9WgXcQ-2025-10-17]]
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        # Test link generation
        link = saver.get_transcript_link("dQw4w9WgXcQ", "2025-10-17")
        assert link == "[[youtube-dQw4w9WgXcQ-2025-10-17]]"
        
        # Test with different video ID
        link2 = saver.get_transcript_link("abc123XYZ", "2025-12-25")
        assert link2 == "[[youtube-abc123XYZ-2025-12-25]]"
    
    def test_idempotent_save(self, tmp_path):
        """
        RED Phase Test 7: Don't recreate transcript file if already exists
        
        If transcript file already exists for video_id + date, should return
        existing path without overwriting.
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        transcript_data = [{"text": "Test", "start": 0.0, "duration": 1.0}]
        metadata = {
            "video_id": "testID123",
            "video_url": "https://youtube.com/watch?v=testID123",
            "video_title": "Test Video",
            "duration": 1.0,
            "language": "en"
        }
        
        # Save once
        path1 = saver.save_transcript(
            video_id="testID123",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="test-note"
        )
        
        original_content = path1.read_text()
        original_mtime = path1.stat().st_mtime
        
        # Save again with same video_id (should not overwrite)
        path2 = saver.save_transcript(
            video_id="testID123",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="test-note"
        )
        
        # Verify same path returned
        assert path1 == path2
        
        # Verify file not modified
        assert path2.stat().st_mtime == original_mtime
        assert path2.read_text() == original_content
    
    def test_bidirectional_parent_note_link(self, tmp_path):
        """
        RED Phase Test 8: Transcript frontmatter includes parent_note link
        
        The saved transcript should include parent_note field in frontmatter
        to create bidirectional link back to the note that triggered processing.
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        transcript_data = [{"text": "Test content", "start": 0.0, "duration": 1.0}]
        metadata = {
            "video_id": "xyz789",
            "video_url": "https://youtube.com/watch?v=xyz789",
            "video_title": "Parent Link Test",
            "duration": 1.0,
            "language": "en"
        }
        
        result_path = saver.save_transcript(
            video_id="xyz789",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="fleeting-youtube-my-note"
        )
        
        content = result_path.read_text()
        
        # Verify parent_note in frontmatter
        assert "parent_note: fleeting-youtube-my-note" in content
        
        # Verify it's in the frontmatter section (before first ---)
        frontmatter_end = content.find("---", 3)  # Find second ---
        frontmatter = content[:frontmatter_end]
        assert "parent_note: fleeting-youtube-my-note" in frontmatter
    
    def test_transcript_body_with_timestamps(self, tmp_path):
        """
        RED Phase Test 9: Transcript body includes timestamps in MM:SS format
        
        Body should contain timestamped transcript entries:
        [00:00] First line of transcript
        [00:05] Second line of transcript
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        transcript_data = [
            {"text": "Welcome to the video", "start": 0.0, "duration": 3.0},
            {"text": "Let's get started", "start": 3.0, "duration": 2.5},
            {"text": "First topic here", "start": 5.5, "duration": 4.0}
        ]
        
        metadata = {
            "video_id": "timestamp123",
            "video_url": "https://youtube.com/watch?v=timestamp123",
            "video_title": "Timestamp Test",
            "duration": 10.0,
            "language": "en"
        }
        
        result_path = saver.save_transcript(
            video_id="timestamp123",
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="test-note"
        )
        
        content = result_path.read_text()
        
        # Verify timestamped entries in body (after frontmatter)
        assert "[00:00] Welcome to the video" in content
        assert "[00:03] Let's get started" in content
        assert "[00:05] First topic here" in content


class TestYouTubeTranscriptSaverHelperMethods:
    """Test helper methods for transcript formatting"""
    
    def test_build_transcript_content_structure(self, tmp_path):
        """
        RED Phase Test 10: Verify _build_transcript_content() assembles complete file
        
        Should assemble: frontmatter + header + timestamped transcript body
        """
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        saver = YouTubeTranscriptSaver(vault_path)
        
        transcript_data = [
            {"text": "Line 1", "start": 0.0, "duration": 1.0},
            {"text": "Line 2", "start": 1.0, "duration": 1.0}
        ]
        
        metadata = {
            "video_id": "build123",
            "video_url": "https://youtube.com/watch?v=build123",
            "video_title": "Build Test",
            "duration": 2.0,
            "language": "en"
        }
        
        content = saver._build_transcript_content(
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name="test-parent",
            date_str="2025-10-17"
        )
        
        # Verify structure: frontmatter (---...---) + header + body
        assert content.startswith("---")
        assert content.count("---") >= 2  # Opening and closing frontmatter
        
        # Verify header
        assert "# Transcript: Build Test" in content
        
        # Verify body has timestamps
        assert "[00:00] Line 1" in content
        assert "[00:01] Line 2" in content
