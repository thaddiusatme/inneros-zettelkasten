"""
YouTubeNoteEnhancer - TDD Iteration 1
Enhances Templater-created YouTube notes with AI-extracted quotes

REFACTOR PHASE: Modular architecture with extracted utilities
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil
import time

from src.utils.frontmatter import parse_frontmatter
from src.ai.youtube_note_enhancer_utils import (
    NoteStructure,
    NoteParser,
    FrontmatterUpdater,
    SectionInserter,
)


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
        
        Delegates to NoteParser utility class for modular parsing logic.
        
        Args:
            content: Full note content as string
            
        Returns:
            NoteStructure with parsed information
        """
        return NoteParser.parse_structure(content)

    def identify_insertion_point(self, content: str) -> int:
        """
        Find line number where quotes section should be inserted
        
        Delegates to NoteParser utility for consistent logic.
        
        Args:
            content: Full note content
            
        Returns:
            Line number for insertion (0-indexed)
        """
        return NoteParser.identify_insertion_point(content)

    def insert_quotes_section(
        self,
        content: str,
        quotes_markdown: str,
        insertion_line: int
    ) -> str:
        """
        Insert quotes section at specified line
        
        Delegates to SectionInserter utility for consistent formatting.
        
        Args:
            content: Original note content
            quotes_markdown: Formatted quotes section to insert
            insertion_line: Line number for insertion
            
        Returns:
            Updated content with quotes inserted
        """
        return SectionInserter.insert_section(content, quotes_markdown, insertion_line)

    def update_frontmatter(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Update YAML frontmatter with processing metadata
        
        Delegates to FrontmatterUpdater utility for consistent YAML handling.
        
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
        return FrontmatterUpdater.update(content, metadata)

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
        
        Delegates to SectionInserter utility for consistent formatting.
        
        Args:
            quotes_data: Quotes organized by category
            
        Returns:
            Formatted markdown string
        """
        return SectionInserter.format_quotes_section(quotes_data)

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
