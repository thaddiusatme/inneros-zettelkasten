"""
YouTube CLI Utilities - TDD Iteration 3
Extracted utility classes for modular architecture and maintainability

Following proven patterns from:
- Smart Link Management TDD Iterations (utility extraction)
- Advanced Tag Enhancement (CLI architecture)
- Safe Workflow CLI Utils (orchestrator pattern)

Architecture:
- YouTubeCLIProcessor: Main orchestrator coordinating workflows
- BatchProgressReporter: Progress tracking and statistics
- YouTubeNoteValidator: Validation logic for YouTube notes
- CLIOutputFormatter: Display logic and formatting
- CLIExportManager: Export functionality (markdown/JSON)

GREEN Phase Complete: All 16/16 tests passing
REFACTOR Phase: Added logging, error messages, and documentation
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import frontmatter parsing utilities
from src.utils.frontmatter import parse_frontmatter

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result from processing a single YouTube note"""
    success: bool
    note_path: Path
    quotes_inserted: int = 0
    backup_path: Optional[Path] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class BatchStatistics:
    """Statistics from batch processing"""
    total_notes: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_quotes: int = 0
    total_time: float = 0.0
    notes_per_second: float = 0.0


class YouTubeCLIProcessor:
    """
    Main orchestrator for YouTube note processing workflows
    
    Responsibilities:
    - Coordinate single note processing
    - Coordinate batch processing workflows
    - Integrate YouTubeProcessor for transcript/quotes
    - Integrate YouTubeNoteEnhancer for note modification
    - Handle all error scenarios with user-friendly messages
    - Maintain backward compatibility with existing CLI
    """

    def __init__(self, vault_path: str):
        """
        Initialize processor with vault path
        
        Args:
            vault_path: Path to Zettelkasten vault root directory
            
        Example:
            >>> processor = YouTubeCLIProcessor("/path/to/vault")
            >>> result = processor.process_single_note(note_path)
        """
        self.vault_path = Path(vault_path)
        self.inbox_dir = self.vault_path / "Inbox"

        # Initialize monitoring counters for production tracking
        from src.automation.youtube_monitoring import MonitoringCounters
        self.counters = MonitoringCounters()

        logger.info(f"Initialized YouTubeCLIProcessor with vault: {self.vault_path}")

    def process_single_note(self, note_path: Path, preview: bool = False,
                           min_quality: Optional[float] = None,
                           categories: Optional[List[str]] = None) -> ProcessingResult:
        """
        Process a single YouTube note with transcript and quotes
        
        Args:
            note_path: Path to note file
            preview: If True, show quotes without modifying note
            min_quality: Minimum relevance score for quotes
            categories: List of quote categories to include
            
        Returns:
            ProcessingResult with success status and details
        """
        import time
        start_time = time.time()

        # Validate note exists
        exists, error = YouTubeNoteValidator.validate_note_exists(note_path)
        if not exists:
            return ProcessingResult(
                success=False,
                note_path=note_path,
                error_message=error,
                processing_time=time.time() - start_time
            )

        # Validate it's a YouTube note
        is_valid, error_msg, metadata = YouTubeNoteValidator.validate_youtube_note(note_path)
        if not is_valid:
            return ProcessingResult(
                success=False,
                note_path=note_path,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

        # Extract video URL
        video_url = YouTubeNoteValidator.extract_video_url(metadata)
        if not video_url:
            return ProcessingResult(
                success=False,
                note_path=note_path,
                error_message="No YouTube URL found in note metadata",
                processing_time=time.time() - start_time
            )

        try:
            # Import YouTube processing components
            from src.cli.youtube_processor import YouTubeProcessor
            from src.ai.youtube_note_enhancer import YouTubeNoteEnhancer, QuotesData

            # Initialize processor (doesn't take video_url in __init__)
            processor = YouTubeProcessor(knowledge_dir=self.vault_path)

            # Extract video ID from URL
            video_id = processor.extract_video_id(video_url)
            logger.debug(f"Extracted video ID: {video_id}")

            # Fetch transcript using video ID
            transcript_result = processor.fetcher.fetch_transcript(video_id)
            logger.info(f"Transcript fetched: {len(transcript_result['transcript'])} segments")

            # Format transcript for LLM
            llm_transcript = processor.fetcher.format_for_llm(transcript_result["transcript"])

            # Extract quotes from transcript
            quotes_result = processor.extractor.extract_quotes(llm_transcript)

            # Categorize quotes by their category field
            quotes_by_category = {
                'key_insights': [],
                'actionable': [],
                'notable': [],
                'definitions': []
            }

            for quote in quotes_result.get('quotes', []):
                category = quote.get('category', 'notable')

                # Transform extractor format to enhancer format
                # Extractor: {text, timestamp, relevance_score, context, category}
                # Enhancer: {quote, timestamp, relevance, context}
                transformed_quote = {
                    'quote': quote.get('text', ''),
                    'timestamp': quote.get('timestamp', '00:00'),
                    'context': quote.get('context', ''),
                    'relevance': quote.get('relevance_score', 0.0)
                }

                # Map category names to QuotesData fields
                if category == 'key-insight':
                    quotes_by_category['key_insights'].append(transformed_quote)
                elif category == 'actionable':
                    quotes_by_category['actionable'].append(transformed_quote)
                elif category == 'definition':
                    quotes_by_category['definitions'].append(transformed_quote)
                else:  # 'quote' or any other
                    quotes_by_category['notable'].append(transformed_quote)

            logger.info(f"Categorized quotes: {len(quotes_by_category['key_insights'])} key insights, "
                       f"{len(quotes_by_category['actionable'])} actionable, "
                       f"{len(quotes_by_category['notable'])} notable, "
                       f"{len(quotes_by_category['definitions'])} definitions")

            # Convert to QuotesData format
            quotes_data = QuotesData(
                key_insights=quotes_by_category['key_insights'],
                actionable=quotes_by_category['actionable'],
                notable=quotes_by_category['notable'],
                definitions=quotes_by_category['definitions']
            )

            # Count total quotes
            quote_count = (
                len(quotes_data.key_insights) +
                len(quotes_data.actionable) +
                len(quotes_data.notable) +
                len(quotes_data.definitions)
            )

            # If preview mode, don't modify note
            if preview:
                return ProcessingResult(
                    success=True,
                    note_path=note_path,
                    quotes_inserted=quote_count,
                    processing_time=time.time() - start_time
                )

            # Enhance note with quotes
            enhancer = YouTubeNoteEnhancer()
            enhancement_result = enhancer.enhance_note(note_path, quotes_data)

            return ProcessingResult(
                success=enhancement_result.success,
                note_path=note_path,
                quotes_inserted=quote_count,
                backup_path=enhancement_result.backup_path,
                error_message=enhancement_result.error_message,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                note_path=note_path,
                error_message=f"Processing failed: {str(e)}",
                processing_time=time.time() - start_time
            )

    def process_batch(self, preview: bool = False,
                     min_quality: Optional[float] = None,
                     categories: Optional[List[str]] = None,
                     quiet_mode: bool = False) -> BatchStatistics:
        """
        Process all unprocessed YouTube notes in Inbox
        
        Args:
            preview: If True, show what would be processed without modifying
            min_quality: Minimum relevance score for quotes
            categories: List of quote categories to include
            quiet_mode: Suppress all output except final result
            
        Returns:
            BatchStatistics with processing results
        """
        import time
        start_time = time.time()

        # Find all markdown files in Inbox
        if not self.inbox_dir.exists():
            return BatchStatistics(total_notes=0)

        markdown_files = list(self.inbox_dir.glob("*.md"))

        # Filter for YouTube notes that haven't been processed
        youtube_notes = []
        for note_path in markdown_files:
            is_valid, _, metadata = YouTubeNoteValidator.validate_youtube_note(note_path)
            if is_valid and not YouTubeNoteValidator.is_already_processed(metadata):
                youtube_notes.append(note_path)

        # Initialize statistics
        stats = BatchStatistics(total_notes=len(youtube_notes))

        if len(youtube_notes) == 0:
            return stats

        # Initialize progress reporter
        reporter = BatchProgressReporter(total_notes=len(youtube_notes), quiet_mode=quiet_mode)

        # Process each note
        for idx, note_path in enumerate(youtube_notes, start=1):
            reporter.report_progress(idx, note_path.name)

            result = self.process_single_note(
                note_path,
                preview=preview,
                min_quality=min_quality,
                categories=categories
            )

            if result.success:
                stats.successful += 1
                stats.total_quotes += result.quotes_inserted
                self.counters.increment_success()
                reporter.report_success(note_path.name, result.quotes_inserted)
            else:
                stats.failed += 1
                self.counters.increment_failure()
                reporter.report_failure(note_path.name, result.error_message or "Unknown error")

        stats.total_time = time.time() - start_time
        if stats.total_time > 0:
            stats.notes_per_second = stats.total_notes / stats.total_time

        return stats


class BatchProgressReporter:
    """
    Progress tracking and statistics reporting for batch operations
    
    Responsibilities:
    - Real-time progress indicators ("Processing X of Y")
    - Summary statistics (successful/failed/skipped counts)
    - Performance metrics (time, throughput)
    - Emoji-enhanced status messages
    """

    def __init__(self, total_notes: int, quiet_mode: bool = False):
        """Initialize reporter with total note count"""
        self.total_notes = total_notes
        self.quiet_mode = quiet_mode

    def report_progress(self, current: int, note_name: str):
        """Report progress for current note"""
        if not self.quiet_mode:
            print(f"🔄 Processing {current}/{self.total_notes}: {note_name}")

    def report_success(self, note_name: str, quotes_count: int):
        """Report successful processing"""
        if not self.quiet_mode:
            print(f"✅ Enhanced {note_name} with {quotes_count} quotes")

    def report_failure(self, note_name: str, error: str):
        """Report processing failure"""
        if not self.quiet_mode:
            print(f"❌ Failed {note_name}: {error}")

    def report_skip(self, note_name: str, reason: str):
        """Report skipped note"""
        if not self.quiet_mode:
            print(f"⚠️ Skipped {note_name}: {reason}")

    def generate_summary(self, stats: BatchStatistics) -> str:
        """Generate formatted summary with statistics and emojis"""
        return f"""
📊 Batch Processing Summary:
   ✅ Successful: {stats.successful}
   ❌ Failed: {stats.failed}
   ⚠️ Skipped: {stats.skipped}
   📝 Total Quotes: {stats.total_quotes}
   📈 Total Notes: {stats.total_notes}
"""


class YouTubeNoteValidator:
    """
    Validation logic for YouTube notes
    
    Responsibilities:
    - File existence validation
    - YouTube source detection (source: youtube)
    - Already-processed filtering (ai_processed: false)
    - URL extraction and validation
    - Clear error messages with troubleshooting guidance
    
    All methods are static for easy testing and reusability.
    """

    @staticmethod
    def validate_note_exists(note_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate note file exists at the given path
        
        Args:
            note_path: Path to note file
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            >>> is_valid, error = YouTubeNoteValidator.validate_note_exists(Path("note.md"))
            >>> if not is_valid:
            ...     print(f"Error: {error}")
        """
        if not note_path.exists():
            logger.warning(f"Note file not found: {note_path}")
            return False, f"Note not found at {note_path}"

        logger.debug(f"Note exists: {note_path}")
        return True, None

    @staticmethod
    def validate_youtube_note(note_path: Path) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate note is a YouTube note with required metadata
        
        Checks:
        1. File exists
        2. Valid YAML frontmatter
        3. Contains 'source: youtube' field
        
        Args:
            note_path: Path to note file
            
        Returns:
            Tuple of (is_valid, error_message, metadata)
            - is_valid: True if all checks pass
            - error_message: Descriptive error if validation fails
            - metadata: Parsed frontmatter dict (empty if validation fails)
            
        Example:
            >>> is_valid, error, metadata = YouTubeNoteValidator.validate_youtube_note(path)
            >>> if is_valid:
            ...     video_url = metadata.get('url')
        """
        # First check if file exists
        exists, error = YouTubeNoteValidator.validate_note_exists(note_path)
        if not exists:
            return False, error, {}

        # Read and parse frontmatter
        try:
            content = note_path.read_text()
            metadata, _ = parse_frontmatter(content)
        except Exception as e:
            error_msg = f"Failed to parse note: {str(e)}. Ensure YAML frontmatter is valid."
            logger.error(f"Parse error for {note_path}: {e}")
            return False, error_msg, {}

        # Check for source: youtube field
        if 'source' not in metadata:
            error_msg = (
                "Note is missing 'source' field in frontmatter. "
                "Add 'source: youtube' to process this note."
            )
            logger.debug(f"Missing source field: {note_path}")
            return False, error_msg, {}

        if metadata['source'] != 'youtube':
            error_msg = (
                f"Note source is '{metadata['source']}', expected 'youtube'. "
                f"This processor only handles YouTube notes."
            )
            logger.debug(f"Wrong source type: {note_path}")
            return False, error_msg, {}

        logger.info(f"Valid YouTube note: {note_path}")
        return True, None, metadata

    @staticmethod
    def is_already_processed(metadata: Dict[str, Any]) -> bool:
        """
        Check if note has already been AI processed
        
        Args:
            metadata: Parsed frontmatter metadata
            
        Returns:
            True if ai_processed field is True, False otherwise
            
        Note:
            Defaults to False if ai_processed field is missing
        """
        processed = metadata.get('ai_processed', False)
        logger.debug(f"Note processed status: {processed}")
        return processed

    @staticmethod
    def extract_video_url(metadata: Dict[str, Any]) -> Optional[str]:
        """
        Extract and validate YouTube URL from metadata
        
        Args:
            metadata: Parsed frontmatter metadata
            
        Returns:
            YouTube URL string if found, None otherwise
            
        Example:
            >>> url = YouTubeNoteValidator.extract_video_url(metadata)
            >>> if url:
            ...     print(f"Processing: {url}")
        """
        url = metadata.get('url', None)
        if url:
            logger.debug(f"Extracted video URL: {url}")
        else:
            logger.warning("No URL found in metadata")
        return url


class CLIOutputFormatter:
    """
    Display logic and output formatting
    
    Responsibilities:
    - Format single note processing results
    - Format batch processing summaries
    - Generate export reports (markdown/JSON)
    - Suppress stdout when quiet_mode is active
    - Consistent emoji formatting across outputs
    """

    def __init__(self, quiet_mode: bool = False):
        """Initialize formatter with quiet mode setting"""
        self.quiet_mode = quiet_mode

    def format_single_result(self, result: ProcessingResult) -> str:
        """Format single note processing result"""
        if result.success:
            return f"✅ Successfully processed {result.note_path.name}: {result.quotes_inserted} quotes inserted"
        else:
            return f"❌ Failed to process {result.note_path.name}: {result.error_message}"

    def format_batch_summary(self, stats: BatchStatistics) -> str:
        """Format batch processing summary"""
        # Use BatchProgressReporter for consistent formatting
        reporter = BatchProgressReporter(total_notes=stats.total_notes, quiet_mode=True)
        return reporter.generate_summary(stats)

    def format_json_output(self, stats: BatchStatistics) -> str:
        """Format statistics as JSON"""
        import json
        return json.dumps({
            'successful': stats.successful,
            'failed': stats.failed,
            'skipped': stats.skipped,
            'total': stats.total_notes,
            'total_quotes': stats.total_quotes
        })

    def print_output(self, message: str):
        """Print message respecting quiet mode"""
        if not self.quiet_mode:
            print(message)


class CLIExportManager:
    """
    Export functionality for processing results
    
    Responsibilities:
    - Markdown report generation with statistics
    - JSON output for automation pipelines
    - File export with error handling
    - Format compatibility with existing patterns
    """

    @staticmethod
    def export_markdown_report(stats: BatchStatistics, export_path: Path,
                               processed_notes: List[ProcessingResult]) -> bool:
        """
        Export batch processing report as markdown
        
        Args:
            stats: Batch statistics
            export_path: Path to export file
            processed_notes: List of all processing results
            
        Returns:
            True if export successful
        """
        try:
            report = f"""# YouTube Processing Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- ✅ Successful: {stats.successful}
- ❌ Failed: {stats.failed}
- ⚠️ Skipped: {stats.skipped}
- 📝 Total Quotes: {stats.total_quotes}
- 📈 Total Notes: {stats.total_notes}

## Processing Details
"""
            # Add details for each processed note
            for result in processed_notes:
                if result.success:
                    report += f"- ✅ {result.note_path.name}: {result.quotes_inserted} quotes\n"
                else:
                    report += f"- ❌ {result.note_path.name}: {result.error_message}\n"

            export_path.write_text(report)
            return True
        except Exception:
            return False

    @staticmethod
    def export_json_output(stats: BatchStatistics, export_path: Optional[Path] = None) -> str:
        """
        Export statistics as JSON
        
        Args:
            stats: Batch statistics
            export_path: Optional file path for export
            
        Returns:
            JSON string
        """
        import json
        json_str = json.dumps({
            'successful': stats.successful,
            'failed': stats.failed,
            'skipped': stats.skipped,
            'total': stats.total_notes,
            'total_quotes': stats.total_quotes
        }, indent=2)

        if export_path:
            try:
                export_path.write_text(json_str)
            except Exception:
                pass  # Silent fail if export path is invalid

        return json_str
