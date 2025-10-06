"""
YouTube Template Formatter

Formats extracted YouTube quotes and metadata into markdown template format
for integration with Obsidian Zettelkasten workflow.

Author: InnerOS Development Team
Date: 2025-10-04
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class YouTubeTemplateFormatter:
    """
    Formats YouTube video quotes and metadata into markdown template.
    
    Takes the output from ContextAwareQuoteExtractor and transforms it into
    a formatted markdown string suitable for the youtube-video.md template.
    
    Features:
    - Category-based quote grouping (key-insight, actionable, quote, definition)
    - Clickable YouTube timestamp links
    - Summary and theme sections
    - Metadata preservation (scores, context)
    - Graceful handling of missing data
    
    Example:
        >>> formatter = YouTubeTemplateFormatter()
        >>> quotes_data = {
        ...     "summary": "Video about AI trends",
        ...     "quotes": [{
        ...         "text": "AI will transform everything",
        ...         "timestamp": "01:15",
        ...         "relevance_score": 0.88,
        ...         "context": "Discusses AI impact",
        ...         "category": "key-insight"
        ...     }],
        ...     "key_themes": ["AI", "Technology"]
        ... }
        >>> result = formatter.format_template(
        ...     quotes_data=quotes_data,
        ...     video_id="dQw4w9WgXcQ"
        ... )
        >>> print(result["markdown"])
        # Video Summary
        Video about AI trends
        ...
    """
    
    # Category display names with emojis (class constant)
    CATEGORY_DISPLAY = {
        "key-insight": "🎯 Key Insights",
        "actionable": "💡 Actionable Insights",
        "quote": "📝 Notable Quotes",
        "definition": "📖 Definitions"
    }
    
    # Category processing order
    CATEGORY_ORDER = ["key-insight", "actionable", "quote", "definition"]
    
    # YouTube URL template
    YOUTUBE_URL_TEMPLATE = "https://youtu.be/{video_id}?t={seconds}"
    
    def __init__(self):
        """Initialize the template formatter."""
        logger.info("YouTubeTemplateFormatter initialized")
        self._current_video_id = None  # Track video ID for timestamp links
    
    def format_template(
        self,
        quotes_data: Dict[str, Any],
        video_id: str,
        video_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format complete template with all sections.
        
        Args:
            quotes_data: Output from ContextAwareQuoteExtractor containing:
                - quotes: List of quote objects
                - summary: Video summary string
                - key_themes: List of theme strings
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            video_title: Optional video title for metadata
            
        Returns:
            Dict with:
                - markdown: Complete formatted markdown string
                - metadata: Template metadata including:
                  - quote_count: Number of quotes
                  - categories: List of quote categories present
                  - average_score: Mean relevance score
                  - video_id: YouTube video ID
                  - has_summary: Whether summary exists
                  - theme_count: Number of themes
                
        Raises:
            ValueError: If quotes_data is None or video_id is empty
            
        Example:
            >>> result = formatter.format_template(
            ...     quotes_data={"summary": "...", "quotes": [...], "key_themes": [...]},
            ...     video_id="abc123"
            ... )
            >>> print(result["metadata"]["quote_count"])
            5
        """
        # Input validation
        if quotes_data is None:
            raise ValueError("quotes_data cannot be None")
        if not video_id or not video_id.strip():
            raise ValueError("video_id cannot be empty")
        
        logger.info(f"Formatting template for video: {video_id}")
        
        # Store video_id for use in timestamp links
        self._current_video_id = video_id
        
        # Extract data from quotes_data with defaults
        quotes = quotes_data.get("quotes", [])
        summary = quotes_data.get("summary", "")
        themes = quotes_data.get("key_themes", [])
        
        logger.debug(
            f"Processing {len(quotes)} quotes, "
            f"summary length: {len(summary)} chars, "
            f"{len(themes)} themes"
        )
        
        # Build markdown sections
        sections = []
        
        # Summary section
        summary_section = self.format_summary_section(summary, themes)
        sections.append(summary_section)
        
        # Quotes section
        if quotes:
            sections.append("\n---\n\n## Extracted Quotes\n")
            quotes_section = self.format_quotes_section(quotes)
            sections.append(quotes_section)
        else:
            sections.append("\n---\n\n## Extracted Quotes\n\n*No high-quality quotes found for this video.*\n")
        
        markdown = "".join(sections)
        
        # Calculate metadata
        categories = list(self.group_quotes_by_category(quotes).keys())
        avg_score = sum(q.get("relevance_score", 0) for q in quotes) / len(quotes) if quotes else 0.0
        
        metadata = {
            "quote_count": len(quotes),
            "categories": categories,
            "average_score": avg_score,
            "video_id": video_id,
            "has_summary": bool(summary),
            "theme_count": len(themes)
        }
        
        logger.info(f"Template formatted: {len(quotes)} quotes, {len(categories)} categories, avg score: {avg_score:.2f}")
        
        return {
            "markdown": markdown,
            "metadata": metadata
        }
    
    def format_quotes_section(self, quotes: List[Dict[str, Any]]) -> str:
        """
        Format quotes with category grouping and markdown bullets.
        
        Args:
            quotes: List of quote objects from extraction
            
        Returns:
            Formatted markdown string with categorized quotes
        """
        if not quotes:
            return "*No quotes available.*\n"
        
        logger.debug(f"Grouping {len(quotes)} quotes by category")
        grouped = self.group_quotes_by_category(quotes)
        logger.debug(f"Found {len(grouped)} categories: {list(grouped.keys())}")
        
        sections = []
        
        # Format each category in defined order
        for category in self.CATEGORY_ORDER:
            if category in grouped and grouped[category]:
                cat_quotes = grouped[category]
                display_name = self.CATEGORY_DISPLAY.get(category, category.title())
                logger.debug(f"Formatting {len(cat_quotes)} quotes for category: {category}")
                
                sections.append(f"\n### {display_name}\n")
                
                for quote in cat_quotes:
                    text = quote.get("text", "")
                    timestamp = quote.get("timestamp", "XX:XX")
                    context = quote.get("context", "")
                    score = quote.get("relevance_score", 0.0)
                    
                    # Create clickable timestamp link if video_id available
                    if self._current_video_id:
                        timestamp_display = self.create_timestamp_link(timestamp, self._current_video_id)
                    else:
                        timestamp_display = timestamp
                    
                    sections.append(f'\n> {timestamp_display} "{text}"\n')
                    sections.append(f"> - **Context**: {context}\n")
                    sections.append(f"> - **Relevance**: {score:.2f}\n")
        
        return "".join(sections)
    
    def group_quotes_by_category(
        self, 
        quotes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group quotes by their category field.
        
        Args:
            quotes: List of quote objects with 'category' field
            
        Returns:
            Dict mapping category names to lists of quotes
            
        Example:
            >>> quotes = [
            ...     {"text": "Q1", "category": "key-insight"},
            ...     {"text": "Q2", "category": "actionable"},
            ...     {"text": "Q3", "category": "key-insight"}
            ... ]
            >>> grouped = formatter.group_quotes_by_category(quotes)
            >>> len(grouped["key-insight"])
            2
        """
        grouped = {}
        
        for quote in quotes:
            category = quote.get("category", "quote")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(quote)
        
        logger.debug(f"Grouped {len(quotes)} quotes into {len(grouped)} categories")
        return grouped
    
    def format_summary_section(
        self,
        summary: str,
        themes: List[str]
    ) -> str:
        """
        Format summary and themes section.
        
        Args:
            summary: Video summary text
            themes: List of key theme strings
            
        Returns:
            Formatted markdown string with summary and themes
            
        Example:
            >>> markdown = formatter.format_summary_section(
            ...     summary="Great video about AI",
            ...     themes=["AI", "Technology"]
            ... )
            >>> "# Video Summary" in markdown
            True
        """
        logger.debug(f"Formatting summary section: {len(themes)} themes")
        sections = []
        
        # Summary header and content
        sections.append(self._create_markdown_header("Video Summary", level=1))
        sections.append(f"{summary}\n")
        
        # Themes section
        if themes:
            sections.append(self._create_markdown_header("Key Themes", level=2))
            for theme in themes:
                sections.append(f"- {theme}\n")
            logger.debug(f"Added {len(themes)} themes to summary section")
        
        return "".join(sections)
    
    def create_timestamp_link(
        self,
        timestamp: str,
        video_id: str
    ) -> str:
        """
        Create clickable YouTube timestamp link.
        
        Args:
            timestamp: Timestamp in MM:SS or HH:MM:SS format
            video_id: YouTube video ID
            
        Returns:
            Markdown link: [MM:SS](https://youtu.be/ID?t=seconds)
            
        Example:
            >>> link = formatter.create_timestamp_link("01:15", "abc123")
            >>> link
            '[01:15](https://youtu.be/abc123?t=75)'
        """
        seconds = self._timestamp_to_seconds(timestamp)
        url = self.YOUTUBE_URL_TEMPLATE.format(video_id=video_id, seconds=seconds)
        return f"[{timestamp}]({url})"
    
    def _timestamp_to_seconds(self, timestamp: str) -> int:
        """
        Convert timestamp string to total seconds.
        
        Args:
            timestamp: Timestamp in MM:SS or HH:MM:SS format
            
        Returns:
            Total seconds as integer (0 if invalid format)
            
        Example:
            >>> formatter._timestamp_to_seconds("01:15")
            75
            >>> formatter._timestamp_to_seconds("01:05:30")
            3930
        """
        try:
            parts = timestamp.split(":")
            
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                logger.warning(f"Invalid timestamp format: {timestamp}")
                return 0
        except (ValueError, AttributeError) as e:
            logger.error(f"Failed to parse timestamp '{timestamp}': {e}")
            return 0
    
    def _create_markdown_header(self, text: str, level: int = 1) -> str:
        """
        Create markdown header with proper formatting.
        
        Args:
            text: Header text
            level: Header level (1-6)
            
        Returns:
            Formatted markdown header with newlines
            
        Example:
            >>> formatter._create_markdown_header("Summary", level=2)
            '\\n## Summary\\n\\n'
        """
        prefix = "#" * min(max(level, 1), 6)
        return f"\n{prefix} {text}\n\n" if level > 1 else f"{prefix} {text}\n\n"
