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
        formatter = YouTubeTemplateFormatter()
        result = formatter.format_template(
            quotes_data=extraction_result,
            video_id="dQw4w9WgXcQ",
            video_title="Example Video"
        )
        print(result["markdown"])
    """
    
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
            video_id: YouTube video ID
            video_title: Optional video title
            
        Returns:
            Dict with:
                - markdown: Formatted markdown string
                - metadata: Template metadata (quote_count, categories, etc)
                
        Raises:
            ValueError: If required data is missing
        """
        logger.info(f"Formatting template for video: {video_id}")
        
        # Store video_id for use in timestamp links
        self._current_video_id = video_id
        
        # Extract data from quotes_data
        quotes = quotes_data.get("quotes", [])
        summary = quotes_data.get("summary", "")
        themes = quotes_data.get("key_themes", [])
        
        logger.debug(f"Processing {len(quotes)} quotes, summary length: {len(summary)}, {len(themes)} themes")
        
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
        
        # Group quotes by category
        grouped = self.group_quotes_by_category(quotes)
        
        # Category display names and emojis
        category_display = {
            "key-insight": "🎯 Key Insights",
            "actionable": "💡 Actionable Insights",
            "quote": "📝 Notable Quotes",
            "definition": "📖 Definitions"
        }
        
        sections = []
        
        # Format each category
        for category in ["key-insight", "actionable", "quote", "definition"]:
            if category in grouped and grouped[category]:
                cat_quotes = grouped[category]
                display_name = category_display.get(category, category.title())
                
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
            quotes: List of quote objects
            
        Returns:
            Dict mapping category names to lists of quotes
        """
        grouped = {}
        
        for quote in quotes:
            category = quote.get("category", "quote")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(quote)
        
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
            Formatted markdown string
        """
        sections = []
        
        # Summary
        sections.append("# Video Summary\n\n")
        sections.append(f"{summary}\n")
        
        # Themes
        if themes:
            sections.append("\n## Key Themes\n\n")
            for theme in themes:
                sections.append(f"- {theme}\n")
        
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
        """
        seconds = self._timestamp_to_seconds(timestamp)
        return f"[{timestamp}](https://youtu.be/{video_id}?t={seconds})"
    
    def _timestamp_to_seconds(self, timestamp: str) -> int:
        """
        Convert timestamp string to total seconds.
        
        Args:
            timestamp: Timestamp in MM:SS or HH:MM:SS format
            
        Returns:
            Total seconds as integer
        """
        parts = timestamp.split(":")
        
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            return 0
