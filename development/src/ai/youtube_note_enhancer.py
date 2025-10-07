"""
YouTubeNoteEnhancer - TDD Iteration 1
Enhances Templater-created YouTube notes with AI-extracted quotes

GREEN PHASE: Minimal working implementation
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import shutil
import time

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


@dataclass
class QuoteItem:
    """Single quote item"""
    timestamp: str
    quote: str
    context: str
    relevance: float = 0.0


@dataclass
class QuotesData:
    """AI-extracted quotes organized by category"""
    key_insights: List[Dict[str, Any]] = field(default_factory=list)
    actionable: List[Dict[str, Any]] = field(default_factory=list)
    notable: List[Dict[str, Any]] = field(default_factory=list)
    definitions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EnhanceResult:
    """Result of note enhancement operation"""
    success: bool = False
    skipped: bool = False
    message: str = ""
    backup_path: Optional[Path] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    quote_count: int = 0
    processing_time: float = 0.0


class YouTubeNoteEnhancer:
    """
    Enhances Templater-created YouTube notes with AI quotes
    
    Core responsibilities:
    1. Parse note structure (frontmatter, sections, content)
    2. Identify insertion point for quotes section
    3. Insert AI-extracted quotes while preserving content
    4. Update frontmatter with processing metadata
    5. Create backups and support rollback
    """
    
    def __init__(self):
        """Initialize enhancer"""
        # Minimal GREEN phase implementation
        pass
    
    def parse_note_structure(self, content: str) -> NoteStructure:
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
    
    def identify_insertion_point(self, content: str) -> int:
        """
        Find line number where quotes section should be inserted
        
        Insertion point is after "Why I'm Saving This" section content
        but before "Key Takeaways" section.
        
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
    
    def insert_quotes_section(
        self, 
        content: str, 
        quotes_markdown: str, 
        insertion_line: int
    ) -> str:
        """
        Insert quotes section at specified line
        
        Args:
            content: Original note content
            quotes_markdown: Formatted quotes section to insert
            insertion_line: Line number for insertion
            
        Returns:
            Updated content with quotes inserted
        """
        lines = content.split('\n')
        
        # Insert quotes with proper spacing
        lines.insert(insertion_line, '\n' + quotes_markdown.rstrip() + '\n')
        
        return '\n'.join(lines)
    
    def update_frontmatter(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Update YAML frontmatter with processing metadata
        
        Adds fields:
        - ai_processed: true
        - processed_at: timestamp
        - quote_count: number
        - processing_time_seconds: float
        
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
    
    def enhance_note(
        self, 
        note_path: Path, 
        quotes_data: QuotesData,
        force: bool = False
    ) -> EnhanceResult:
        """
        Complete enhancement workflow for a single note
        
        Workflow:
        1. Validate note exists
        2. Check if already processed (unless force=True)
        3. Create backup
        4. Generate quotes markdown from QuotesData
        5. Insert quotes section
        6. Update frontmatter
        7. Write enhanced note
        8. Rollback on any failure
        
        Args:
            note_path: Path to note file
            quotes_data: AI-extracted quotes to insert
            force: Reprocess even if ai_processed=true
            
        Returns:
            EnhanceResult with operation details
        """
        start_time = time.time()
        result = EnhanceResult()
        
        # Validate quotes_data
        if quotes_data is None:
            raise ValueError("quotes_data cannot be None")
        
        # 1. Validate note exists
        if not note_path.exists():
            result.success = False
            result.error_type = "FileNotFoundError"
            result.error_message = f"Note not found: {note_path}"
            return result
        
        try:
            # Read original content
            original_content = note_path.read_text(encoding='utf-8')
            
            # 2. Check if already processed
            frontmatter, _ = parse_frontmatter(original_content)
            if frontmatter.get('ai_processed') and not force:
                result.success = False
                result.skipped = True
                result.message = "Note already processed (use force=True to reprocess)"
                return result
            
            # 3. Create backup
            backup_path = self._create_backup(note_path)
            result.backup_path = backup_path
            
            # 4. Generate quotes markdown
            quotes_markdown = self._format_quotes_markdown(quotes_data)
            
            # 5. Insert quotes section
            insertion_point = self.identify_insertion_point(original_content)
            enhanced_content = self.insert_quotes_section(
                original_content, 
                quotes_markdown, 
                insertion_point
            )
            
            # 6. Update frontmatter
            processing_time = time.time() - start_time
            quote_count = (
                len(quotes_data.key_insights) + 
                len(quotes_data.actionable) + 
                len(quotes_data.notable) + 
                len(quotes_data.definitions)
            )
            
            metadata = {
                'ai_processed': True,
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'quote_count': quote_count,
                'processing_time_seconds': round(processing_time, 2)
            }
            
            enhanced_content = self.update_frontmatter(enhanced_content, metadata)
            
            # 7. Write enhanced note
            note_path.write_text(enhanced_content, encoding='utf-8')
            
            result.success = True
            result.message = f"Successfully enhanced note with {quote_count} quotes"
            result.quote_count = quote_count
            result.processing_time = processing_time
            
        except Exception as e:
            # 8. Rollback on failure
            result.success = False
            result.error_type = type(e).__name__
            result.error_message = str(e)
            
            if result.backup_path and result.backup_path.exists():
                self._rollback(note_path, result.backup_path)
        
        return result
    
    def _format_quotes_markdown(self, quotes_data: QuotesData) -> str:
        """
        Format QuotesData into markdown section
        
        Args:
            quotes_data: Quotes organized by category
            
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
    
    def _create_backup(self, note_path: Path) -> Path:
        """
        Create backup before modification
        
        Args:
            note_path: Path to note file
            
        Returns:
            Path to backup file
        """
        # Create backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = note_path.parent / f"{note_path.stem}_backup_{timestamp}{note_path.suffix}"
        
        # Copy file to backup location
        shutil.copy2(note_path, backup_path)
        
        return backup_path
    
    def _rollback(self, note_path: Path, backup_path: Path) -> bool:
        """
        Restore from backup on failure
        
        Args:
            note_path: Original note path
            backup_path: Backup file path
            
        Returns:
            True if rollback successful
        """
        try:
            # Restore from backup
            shutil.copy2(backup_path, note_path)
            return True
        except Exception:
            return False
