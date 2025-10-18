#!/usr/bin/env python3
"""
YouTube Transcript Saver - TDD Iteration 1 GREEN Phase

Saves complete video transcripts as separate markdown files with bidirectional links.
Part of YouTube Transcript Archival System.

Features:
- Creates transcript files in Media/Transcripts/ directory
- Generates filename: youtube-{video_id}-{YYYY-MM-DD}.md
- Includes comprehensive frontmatter with metadata
- Formats timestamps in MM:SS format
- Creates bidirectional links with parent notes
- Idempotent saves (doesn't recreate existing files)

Usage:
    from ai.youtube_transcript_saver import YouTubeTranscriptSaver
    
    saver = YouTubeTranscriptSaver(vault_path)
    
    transcript_file = saver.save_transcript(
        video_id="dQw4w9WgXcQ",
        transcript_data=transcript_entries,
        metadata=video_metadata,
        parent_note_name="fleeting-youtube-note"
    )

Author: InnerOS Zettelkasten Team
Version: 1.0.0 (TDD Iteration 1 GREEN Phase)
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class YouTubeTranscriptSaver:
    """
    Saves YouTube video transcripts as separate markdown files.
    
    This class provides archival functionality for YouTube transcripts,
    creating searchable markdown files with bidirectional links to parent notes.
    
    Attributes:
        vault_path: Path to the Zettelkasten vault root
        transcripts_dir: Path to Media/Transcripts/ directory
    
    Example:
        >>> saver = YouTubeTranscriptSaver(Path("/path/to/vault"))
        >>> path = saver.save_transcript(
        ...     video_id="dQw4w9WgXcQ",
        ...     transcript_data=[...],
        ...     metadata={...},
        ...     parent_note_name="fleeting-note"
        ... )
    """
    
    def __init__(self, vault_path: Path):
        """
        Initialize transcript saver.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = Path(vault_path)
        self.transcripts_dir = self.vault_path / "Media" / "Transcripts"
        
        # Create transcripts directory if it doesn't exist
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"YouTubeTranscriptSaver initialized with vault: {vault_path}")
    
    def save_transcript(
        self,
        video_id: str,
        transcript_data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        parent_note_name: str
    ) -> Path:
        """
        Save transcript to markdown file.
        
        Creates a transcript file with frontmatter, header, and timestamped body.
        If file already exists for this video_id + date, returns existing path
        without overwriting (idempotent).
        
        Args:
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            transcript_data: List of transcript entries with text/start/duration
            metadata: Video metadata dict with video_url, video_title, duration, language
            parent_note_name: Name of parent note for bidirectional linking
            
        Returns:
            Path to created (or existing) transcript file
            
        Example:
            >>> path = saver.save_transcript(
            ...     video_id="dQw4w9WgXcQ",
            ...     transcript_data=[
            ...         {"text": "Hello", "start": 0.0, "duration": 2.0}
            ...     ],
            ...     metadata={
            ...         "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            ...         "video_title": "Test Video",
            ...         "duration": 120.0,
            ...         "language": "en"
            ...     },
            ...     parent_note_name="fleeting-youtube-note"
            ... )
        """
        # Generate filename with current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"youtube-{video_id}-{date_str}.md"
        file_path = self.transcripts_dir / filename
        
        # Check if file already exists (idempotent)
        if file_path.exists():
            logger.info(f"Transcript file already exists: {file_path}")
            return file_path
        
        # Build complete transcript content
        content = self._build_transcript_content(
            transcript_data=transcript_data,
            metadata=metadata,
            parent_note_name=parent_note_name,
            date_str=date_str
        )
        
        # Write to file
        file_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Saved transcript to: {file_path}")
        return file_path
    
    def _build_transcript_content(
        self,
        transcript_data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        parent_note_name: str,
        date_str: str
    ) -> str:
        """
        Build complete transcript markdown content.
        
        Assembles frontmatter, header, and timestamped transcript body.
        
        Args:
            transcript_data: List of transcript entries
            metadata: Video metadata
            parent_note_name: Parent note for bidirectional link
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            Complete markdown content string
        """
        # Extract metadata
        video_id = metadata["video_id"]
        video_url = metadata["video_url"]
        video_title = metadata["video_title"]
        duration = metadata["duration"]
        language = metadata.get("language", "en")
        
        # Build content sections
        frontmatter = self._build_frontmatter(
            video_id=video_id,
            video_url=video_url,
            video_title=video_title,
            duration=duration,
            language=language,
            transcript_length=len(transcript_data),
            parent_note_name=parent_note_name
        )
        
        header = self._build_header(
            video_title=video_title,
            video_url=video_url,
            duration=duration,
            language=language,
            parent_note_name=parent_note_name
        )
        
        body = self._build_timestamped_body(transcript_data)
        
        return frontmatter + header + body
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp in MM:SS format.
        
        Converts float seconds into MM:SS format for transcript entries.
        Handles videos over 1 hour (e.g., 61:01 for 1h 1m 1s).
        
        Args:
            seconds: Timestamp in seconds (float)
            
        Returns:
            Formatted timestamp string in MM:SS format
            
        Example:
            >>> saver._format_timestamp(0.0)
            '00:00'
            >>> saver._format_timestamp(90.5)
            '01:30'
            >>> saver._format_timestamp(3600.0)
            '60:00'
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration as HH:MM:SS or MM:SS.
        
        Formats video duration in human-readable format.
        Uses HH:MM:SS for videos >= 1 hour, MM:SS for shorter videos.
        
        Args:
            seconds: Duration in seconds (float)
            
        Returns:
            Formatted duration string
            
        Example:
            >>> saver._format_duration(90)
            '1:30'
            >>> saver._format_duration(3661)
            '1:01:01'
            >>> saver._format_duration(45)
            '0:45'
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _build_frontmatter(
        self,
        video_id: str,
        video_url: str,
        video_title: str,
        duration: float,
        language: str,
        transcript_length: int,
        parent_note_name: str
    ) -> str:
        """
        Build YAML frontmatter section.
        
        Args:
            video_id: YouTube video ID
            video_url: Full video URL
            video_title: Video title
            duration: Video duration in seconds
            language: Language code
            transcript_length: Number of transcript entries
            parent_note_name: Parent note for bidirectional link
            
        Returns:
            YAML frontmatter string with --- delimiters
        """
        duration_str = self._format_duration(duration)
        fetched_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""---
type: transcript
source: youtube
video_id: {video_id}
video_url: {video_url}
video_title: {video_title}
duration: {duration_str}
transcript_length: {transcript_length}
language: {language}
fetched: {fetched_timestamp}
parent_note: {parent_note_name}
---

"""
    
    def _build_header(
        self,
        video_title: str,
        video_url: str,
        duration: float,
        language: str,
        parent_note_name: str
    ) -> str:
        """
        Build markdown header section.
        
        Args:
            video_title: Video title
            video_url: Full video URL
            duration: Video duration in seconds
            language: Language code
            parent_note_name: Parent note for bidirectional link
            
        Returns:
            Markdown header with title and metadata
        """
        duration_str = self._format_duration(duration)
        
        header = f"# Transcript: {video_title}\n\n"
        header += f"**Video**: [{video_title}]({video_url})\n"
        header += f"**Duration**: {duration_str}\n"
        header += f"**Language**: {language}\n"
        header += f"**Parent Note**: [[{parent_note_name}]]\n\n"
        header += "## Transcript\n\n"
        
        return header
    
    def _build_timestamped_body(self, transcript_data: List[Dict[str, Any]]) -> str:
        """
        Build timestamped transcript body.
        
        Args:
            transcript_data: List of transcript entries with text/start/duration
            
        Returns:
            Timestamped transcript text with one entry per line
        """
        transcript_lines = []
        for entry in transcript_data:
            timestamp = self._format_timestamp(entry["start"])
            text = entry["text"].strip()
            transcript_lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(transcript_lines)
    
    def get_transcript_link(self, video_id: str, date_str: str) -> str:
        """
        Generate wikilink for transcript file.
        
        Creates a wikilink in [[...]] format for referencing the transcript.
        
        Args:
            video_id: YouTube video ID
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            Wikilink string in format [[youtube-{video_id}-{date}]]
            
        Example:
            >>> saver.get_transcript_link("dQw4w9WgXcQ", "2025-10-17")
            '[[youtube-dQw4w9WgXcQ-2025-10-17]]'
        """
        return f"[[youtube-{video_id}-{date_str}]]"
