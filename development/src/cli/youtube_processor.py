"""
YouTube Video Processor - TDD Iteration 4: CLI Integration

Orchestrates the complete YouTube processing pipeline:
1. URL validation and video ID extraction
2. Transcript fetching (YouTubeTranscriptFetcher)
3. Quote extraction with AI (ContextAwareQuoteExtractor)
4. Markdown formatting (YouTubeTemplateFormatter)
5. File creation in knowledge/Inbox/

This is the "glue code" that connects all three existing components
into a seamless URL-to-Note workflow.

Usage:
    processor = YouTubeProcessor()
    result = processor.process_video(
        url="https://youtube.com/watch?v=FLpS7OfD5-s",
        user_context="I'm interested in AI and productivity"
    )
    print(f"Note created: {result['file_path']}")
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
from src.ai.youtube_quote_extractor import ContextAwareQuoteExtractor
from src.ai.youtube_template_formatter import YouTubeTemplateFormatter

logger = logging.getLogger(__name__)


class YouTubeProcessor:
    """
    Orchestrates end-to-end YouTube video processing.
    
    Connects transcript fetching, AI quote extraction, and markdown
    formatting into a single workflow that produces Obsidian-ready
    notes in the knowledge/Inbox/ directory.
    
    Attributes:
        knowledge_dir: Path to knowledge base root directory
        fetcher: YouTubeTranscriptFetcher instance
        extractor: ContextAwareQuoteExtractor instance
        formatter: YouTubeTemplateFormatter instance
    
    Example:
        >>> processor = YouTubeProcessor()
        >>> result = processor.process_video("https://youtube.com/watch?v=FLpS7OfD5-s")
        >>> print(f"Created: {result['file_path']}")
    """
    
    def __init__(self, knowledge_dir: Optional[Path] = None):
        """
        Initialize YouTube processor with optional knowledge directory.
        
        Args:
            knowledge_dir: Path to knowledge base root (defaults to ./knowledge)
        """
        self.knowledge_dir = knowledge_dir or Path("knowledge")
        self.fetcher = YouTubeTranscriptFetcher()
        self.extractor = ContextAwareQuoteExtractor()
        self.formatter = YouTubeTemplateFormatter()
        logger.info(f"YouTubeProcessor initialized with knowledge_dir: {self.knowledge_dir}")
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Supports multiple URL formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - URLs with additional parameters (&t=120s, etc.)
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID string (e.g., "FLpS7OfD5-s")
            
        Raises:
            ValueError: If URL format is invalid or video ID cannot be extracted
            
        Example:
            >>> processor = YouTubeProcessor()
            >>> video_id = processor.extract_video_id("https://youtube.com/watch?v=FLpS7OfD5-s")
            >>> print(video_id)
            FLpS7OfD5-s
        """
        # Try standard format: youtube.com/watch?v=VIDEO_ID
        match = re.search(r'[?&]v=([^&]+)', url)
        if match:
            return match.group(1)
        
        # Try short format: youtu.be/VIDEO_ID
        match = re.search(r'youtu\.be/([^?]+)', url)
        if match:
            return match.group(1)
        
        raise ValueError(f"Invalid YouTube URL: {url}")
    
    def validate_url(self, url: str) -> bool:
        """
        Validate YouTube URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
            
        Example:
            >>> processor = YouTubeProcessor()
            >>> processor.validate_url("https://youtube.com/watch?v=FLpS7OfD5-s")
            True
            >>> processor.validate_url("https://vimeo.com/12345")
            False
        """
        if not url:
            return False
        
        # Check for YouTube domains
        youtube_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtu\.be/'
        ]
        
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def process_video(
        self,
        url: str,
        user_context: Optional[str] = None,
        max_quotes: int = 7,
        min_quality: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process YouTube video through complete pipeline.
        
        Pipeline stages:
        1. Extract and validate video ID from URL
        2. Fetch transcript using YouTubeTranscriptFetcher
        3. Extract quotes using ContextAwareQuoteExtractor (with user context)
        4. Format markdown using YouTubeTemplateFormatter
        5. Write note file to knowledge/Inbox/
        6. Return processing results and file path
        
        Args:
            url: YouTube video URL
            user_context: Optional context to guide quote selection
                Example: "I'm interested in AI automation and productivity"
            max_quotes: Maximum quotes to extract (default: 7)
            min_quality: Minimum quality threshold for quotes (default: 0.7)
            
        Returns:
            Dict containing:
                - success: bool - Whether processing succeeded
                - video_id: str - Extracted video ID
                - file_path: str - Path to created note file
                - quotes_extracted: int - Number of quotes extracted
                - metadata: dict - Note frontmatter metadata
                - timing: dict - Processing time for each stage
                - error: str - Error message if success=False
                
        Raises:
            ValueError: If URL is invalid
            
        Example:
            >>> processor = YouTubeProcessor()
            >>> result = processor.process_video(
            ...     url="https://youtube.com/watch?v=FLpS7OfD5-s",
            ...     user_context="I'm learning about AI and creativity"
            ... )
            >>> print(f"Success: {result['success']}")
            >>> print(f"File: {result['file_path']}")
            >>> print(f"Quotes: {result['quotes_extracted']}")
        """
        import time
        
        timing: Dict[str, float] = {
            "total": 0.0,
            "fetch": 0.0,
            "extraction": 0.0,
            "formatting": 0.0
        }
        start_time = time.time()
        
        try:
            # Step 1: Extract video ID
            video_id = self.extract_video_id(url)
            logger.info(f"Processing video: {video_id}")
            
            # Step 2: Fetch transcript
            fetch_start = time.time()
            transcript_result = self.fetcher.fetch_transcript(video_id)
            timing["fetch"] = time.time() - fetch_start
            logger.info(f"Transcript fetched: {len(transcript_result['transcript'])} segments in {timing['fetch']:.2f}s")
            
            # Format transcript for LLM
            llm_transcript = self.fetcher.format_for_llm(transcript_result["transcript"])
            
            # Step 3: Extract quotes with AI
            extract_start = time.time()
            quotes_result = self.extractor.extract_quotes(
                transcript=llm_transcript,
                user_context=user_context,
                max_quotes=max_quotes,
                min_quality=min_quality
            )
            timing["extraction"] = time.time() - extract_start
            logger.info(f"Quotes extracted: {len(quotes_result['quotes'])} quotes in {timing['extraction']:.2f}s")
            
            # Step 4: Format markdown
            format_start = time.time()
            format_result = self.formatter.format_template(
                quotes_data=quotes_result,
                video_id=video_id
            )
            timing["formatting"] = time.time() - format_start
            logger.info(f"Markdown formatted in {timing['formatting']:.2f}s")
            
            # Step 5: Build metadata
            metadata = self._build_metadata(video_id, transcript_result, quotes_result)
            
            # Step 6: Create note file
            file_path = self._create_note_file(video_id, format_result["markdown"], metadata)
            
            timing["total"] = time.time() - start_time
            logger.info(f"Processing complete: {file_path} in {timing['total']:.2f}s")
            
            return {
                "success": True,
                "video_id": video_id,
                "file_path": str(file_path),
                "quotes_extracted": len(quotes_result["quotes"]),
                "metadata": metadata,
                "timing": timing
            }
            
        except Exception as e:
            timing["total"] = time.time() - start_time
            error_msg = str(e).lower()
            
            # Categorize error for user-friendly messages (order matters!)
            if "llm" in error_msg or "service unavailable" in error_msg:
                error_type = "LLM service unavailable"
            elif "transcript" in error_msg and "not available" in error_msg:
                error_type = "Transcript not available for this video"
            elif "connection" in error_msg or "unavailable" in error_msg:
                error_type = "Service unavailable"
            else:
                error_type = str(e)
            
            logger.error(f"Processing failed: {error_type}")
            
            return {
                "success": False,
                "error": error_type,
                "timing": timing
            }
    
    def _create_note_file(
        self,
        video_id: str,
        formatted_content: str,
        metadata: Dict[str, Any]
    ) -> Path:
        """
        Create note file in knowledge/Inbox/ directory.
        
        File naming format: youtube-YYYYMMDD-HHmm-{video_id}.md
        Example: youtube-20251005-0830-FLpS7OfD5-s.md
        
        Args:
            video_id: YouTube video ID
            formatted_content: Formatted markdown content
            metadata: Frontmatter metadata dict
            
        Returns:
            Path to created file
        """
        # Create Inbox directory if it doesn't exist
        inbox_dir = self.knowledge_dir / "Inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename: youtube-YYYYMMDD-HHmm-{video_id}.md
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M")
        filename = f"youtube-{timestamp}-{video_id}.md"
        file_path = inbox_dir / filename
        
        # Build complete content with frontmatter
        frontmatter_lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, list):
                # Format lists properly
                frontmatter_lines.append(f"{key}:")
                for item in value:
                    frontmatter_lines.append(f"  - {item}")
            else:
                frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.append("---")
        
        full_content = "\n".join(frontmatter_lines) + "\n\n" + formatted_content
        
        # Write file
        file_path.write_text(full_content, encoding="utf-8")
        logger.info(f"Note created: {file_path}")
        
        return file_path
    
    def _build_metadata(
        self,
        video_id: str,
        transcript_metadata: Dict[str, Any],
        quotes_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build frontmatter metadata for note.
        
        Args:
            video_id: YouTube video ID
            transcript_metadata: Metadata from transcript fetcher
            quotes_data: Quote extraction results
            
        Returns:
            Dict with frontmatter fields (type, status, created, etc.)
        """
        now = datetime.now()
        
        metadata = {
            "type": "literature",
            "status": "inbox",
            "created": now.strftime("%Y-%m-%d %H:%M"),
            "video_id": video_id,
            "source": f"https://youtube.com/watch?v={video_id}",
            "tags": quotes_data.get("key_themes", [])
        }
        
        # Add video title if available
        if "title" in transcript_metadata.get("metadata", {}):
            metadata["title"] = transcript_metadata["metadata"]["title"]
        
        return metadata
