"""
YouTubeNoteEnhancer Utilities - TDD Iteration 1 REFACTOR Phase
Extracted utility classes for modular architecture

Following proven patterns from Smart Link Management and Advanced Tag Enhancement.
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from src.utils.frontmatter import parse_frontmatter, build_frontmatter


@dataclass
class NoteStructure:
    """Parsed structure of a YouTube note"""
    has_frontmatter: bool = False
    has_why_section: bool = False
    has_parse_errors: bool = False
    error_message: Optional[str] = None
    title: Optional[str] = None
    frontmatter_data: Dict[str, Any] = field(default_factory=dict)
    why_section_content: Optional[str] = None
    insertion_point: Optional[int] = None


class NoteParser:
    """
    Utility class for parsing note structure and content
    
    Responsibilities:
    - Extract YAML frontmatter
    - Identify note sections
    - Detect malformed YAML
    - Find title and key content
    """
    
    @staticmethod
    def parse_structure(content: str) -> NoteStructure:
        """
        Parse note to identify structure and sections
        
        Args:
            content: Full note content as string
            
        Returns:
            NoteStructure with parsed information
        """
        result = NoteStructure()
        
        # Parse frontmatter
        try:
            frontmatter_data, body = parse_frontmatter(content)
            result.has_frontmatter = bool(frontmatter_data)
            result.frontmatter_data = frontmatter_data
            
            # Check for malformed YAML indicators
            if content.startswith('---'):
                yaml_section = content.split('---', 2)[1] if content.count('---') >= 2 else ''
                # Check for template placeholders or unclosed brackets
                if '{{' in yaml_section or '[' in yaml_section and ']' not in yaml_section.split('[')[-1]:
                    result.has_parse_errors = True
                    result.error_message = "Malformed YAML: template placeholders or unclosed brackets detected"
                    return result
                    
        except Exception as e:
            result.has_parse_errors = True
            result.error_message = f"YAML parse error: {str(e)}"
            return result
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            result.title = title_match.group(1).strip()
        
        # Check for "Why I'm Saving This" section
        why_match = re.search(r'##\s+Why I\'?m Saving This\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if why_match:
            result.has_why_section = True
            result.why_section_content = why_match.group(1).strip()
            
            # Find insertion point (after why section content)
            result.insertion_point = content.find(why_match.group(0)) + len(why_match.group(0))
        else:
            # No why section - insert after title or frontmatter
            result.insertion_point = len(content) // 2
        
        return result
    
    @staticmethod
    def identify_insertion_point(content: str) -> int:
        """
        Find line number where quotes section should be inserted
        
        Args:
            content: Full note content
            
        Returns:
            Line number for insertion (0-indexed)
        """
        lines = content.split('\n')
        
        # Find "Why I'm Saving This" section
        why_line = None
        for i, line in enumerate(lines):
            if "Why I'm Saving This" in line or "Why Im Saving This" in line:
                why_line = i
                break
        
        if why_line is None:
            # No why section, insert after frontmatter/title
            return len(lines) // 2
        
        # Find the next section after "Why I'm Saving This"
        # We want to insert BEFORE that section
        for i in range(why_line + 1, len(lines)):
            if lines[i].strip().startswith('##'):
                # Insert before this section (one line up if there's whitespace)
                insert_at = i
                # Back up one line if previous line is empty (better formatting)
                if i > 0 and lines[i-1].strip() == '':
                    insert_at = i - 1
                return insert_at
        
        return len(lines)


class FrontmatterUpdater:
    """
    Utility class for YAML frontmatter manipulation
    
    Responsibilities:
    - Update existing frontmatter
    - Preserve existing fields
    - Add processing metadata
    """
    
    @staticmethod
    def update(content: str, metadata: Dict[str, Any]) -> str:
        """
        Update YAML frontmatter with new metadata
        
        Args:
            content: Note content with frontmatter
            metadata: Fields to add/update
            
        Returns:
            Content with updated frontmatter
        """
        # Parse existing frontmatter
        existing_frontmatter, body = parse_frontmatter(content)
        
        # Merge with new metadata
        updated_frontmatter = {**existing_frontmatter, **metadata}
        
        # Rebuild content with updated frontmatter
        return build_frontmatter(updated_frontmatter, body)


class SectionInserter:
    """
    Utility class for markdown section manipulation
    
    Responsibilities:
    - Insert sections at specific lines
    - Preserve document structure
    - Format quotes with categories
    """
    
    @staticmethod
    def insert_section(content: str, section_markdown: str, insertion_line: int) -> str:
        """
        Insert section at specified line
        
        Args:
            content: Original note content
            section_markdown: Formatted section to insert
            insertion_line: Line number for insertion
            
        Returns:
            Updated content with section inserted
        """
        lines = content.split('\n')
        
        # Insert section with proper spacing
        lines.insert(insertion_line, '\n' + section_markdown.rstrip() + '\n')
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_quotes_section(quotes_data) -> str:
        """
        Format QuotesData into markdown section
        
        Args:
            quotes_data: Quotes organized by category (QuotesData object)
            
        Returns:
            Formatted markdown string
        """
        sections = ["## Extracted Quotes\n"]
        
        # Key Insights
        if quotes_data.key_insights:
            sections.append("### 🎯 Key Insights\n")
            for quote in quotes_data.key_insights:
                sections.append(f"> [{quote['timestamp']}] \"{quote['quote']}\"")
                sections.append(f"> - **Context**: {quote['context']}")
                if 'relevance' in quote:
                    sections.append(f"> - **Relevance**: {quote['relevance']}")
                sections.append("")
        
        # Actionable Insights
        if quotes_data.actionable:
            sections.append("### 💡 Actionable Insights\n")
            for quote in quotes_data.actionable:
                sections.append(f"> [{quote['timestamp']}] \"{quote['quote']}\"")
                sections.append(f"> - **Context**: {quote['context']}")
                sections.append("")
        
        # Notable Quotes
        if quotes_data.notable:
            sections.append("### 📝 Notable Quotes\n")
            for quote in quotes_data.notable:
                sections.append(f"> [{quote['timestamp']}] \"{quote['quote']}\"")
                sections.append(f"> - **Context**: {quote['context']}")
                sections.append("")
        
        # Definitions
        if quotes_data.definitions:
            sections.append("### 📖 Definitions\n")
            for quote in quotes_data.definitions:
                sections.append(f"> [{quote['timestamp']}] \"{quote['quote']}\"")
                sections.append(f"> - **Context**: {quote['context']}")
                sections.append("")
        
        return '\n'.join(sections)
