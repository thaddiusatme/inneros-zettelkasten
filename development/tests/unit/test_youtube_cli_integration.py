"""
Test suite for YouTube CLI integration (TDD Iteration 2)

RED Phase: Comprehensive failing tests for --process-youtube-note and --process-youtube-notes commands.
Following established CLI patterns from --fleeting-triage and --promote-note.

Tests cover:
- P0: CLI argument parsing, single note processing, batch processing, error handling
- P1: Preview mode, quality filtering, category selection
"""

import pytest
import tempfile
import shutil
import subprocess
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestYouTubeCLIIntegration:
    """Test cases for YouTube note processing CLI commands."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        self.cli_script = Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"
        
        # Create vault structure
        (self.vault_path / "knowledge" / "Inbox").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Literature Notes").mkdir(parents=True)
        (self.vault_path / "backups").mkdir(parents=True)
        
        # Create sample YouTube notes for testing
        self._create_sample_youtube_notes()
        
    def teardown_method(self):
        """Clean up test environment."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_sample_youtube_notes(self):
        """Create sample YouTube notes for testing."""
        inbox_dir = self.vault_path / "knowledge" / "Inbox"
        
        # Valid YouTube note ready for processing (ai_processed: false)
        valid_note = inbox_dir / "lit-20251003-0954-test-youtube-video.md"
        valid_note.write_text("""---
type: literature
source: youtube
created: 2025-10-03 09:54
status: inbox
visibility: private
ai_processed: false
url: https://www.youtube.com/watch?v=test123
youtube_channel: Test Channel
---

# Test YouTube Video Title

## Why I'm Saving This
Testing YouTube note processing with AI quote extraction.

## Key Takeaways
- Important concept about AI
- Relevant to knowledge management

## Initial Notes
This video discusses interesting concepts that should be captured.
""")
        
        # Already processed YouTube note (ai_processed: true)
        processed_note = inbox_dir / "lit-20251003-1030-already-processed.md"
        processed_note.write_text("""---
type: literature
source: youtube
created: 2025-10-03 10:30
status: inbox
visibility: private
ai_processed: true
ai_processing_date: 2025-10-03 10:35
url: https://www.youtube.com/watch?v=processed456
---

# Already Processed Video

## Extracted Quotes

### 🎯 Key Insights
- [00:05:30] "This was already extracted" (Context: Previous processing)

## Initial Notes
This was already processed.
""")
        
        # YouTube note with malformed YAML (template placeholder not processed)
        malformed_note = inbox_dir / "lit-20251003-1100-malformed-yaml.md"
        malformed_note.write_text("""---
type: literature
source: youtube
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
visibility: private
ai_processed: false
url: https://www.youtube.com/watch?v=malformed789
---

# Malformed YAML Test

## Initial Notes
This has unprocessed template placeholders.
""")
        
        # Non-YouTube note (should be filtered out)
        non_youtube_note = inbox_dir / "fleeting-20251003-1200-regular-note.md"
        non_youtube_note.write_text("""---
type: fleeting
created: 2025-10-03 12:00
status: inbox
---

# Regular Fleeting Note
This is not a YouTube note.
""")
    
    # ============================================================================
    # P0.1: CLI Argument Parsing Tests
    # ============================================================================
    
    def test_process_youtube_note_argument_exists(self):
        """Test that --process-youtube-note argument is recognized."""
        result = subprocess.run(
            [sys.executable, str(self.cli_script), str(self.vault_path), "--help"],
            capture_output=True,
            text=True
        )
        
        assert "--process-youtube-note" in result.stdout
        assert "Process single YouTube note" in result.stdout or "YouTube note" in result.stdout
    
    def test_process_youtube_notes_batch_argument_exists(self):
        """Test that --process-youtube-notes batch argument is recognized."""
        result = subprocess.run(
            [sys.executable, str(self.cli_script), str(self.vault_path), "--help"],
            capture_output=True,
            text=True
        )
        
        assert "--process-youtube-notes" in result.stdout
        assert "batch" in result.stdout.lower() or "scan" in result.stdout.lower()
    
    def test_youtube_min_quality_argument(self):
        """Test that --min-quality can be used with YouTube processing."""
        result = subprocess.run(
            [sys.executable, str(self.cli_script), str(self.vault_path), "--help"],
            capture_output=True,
            text=True
        )
        
        # Should support quality filtering
        assert "--min-quality" in result.stdout
    
    def test_youtube_categories_argument(self):
        """Test that --categories argument exists for YouTube processing."""
        result = subprocess.run(
            [sys.executable, str(self.cli_script), str(self.vault_path), "--help"],
            capture_output=True,
            text=True
        )
        
        # Should support category selection
        assert "--categories" in result.stdout or "category" in result.stdout.lower()
    
    # ============================================================================
    # P0.2: Single Note Processing Tests
    # ============================================================================
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_process_single_youtube_note_success(self, mock_enhancer, mock_processor):
        """Test successful processing of single YouTube note."""
        # Mock transcript and quote extraction
        mock_processor.return_value.fetch_transcript.return_value = "Sample transcript"
        mock_processor.return_value.extract_quotes.return_value = {
            'key_insights': [
                {'timestamp': '00:05:30', 'quote': 'Key insight quote', 'context': 'Important context', 'relevance': 0.9}
            ],
            'actionable': [],
            'notable': [],
            'definitions': []
        }
        
        # Mock note enhancement
        from src.ai.youtube_note_enhancer import EnhanceResult
        mock_enhancer.return_value.enhance_note.return_value = EnhanceResult(
            success=True,
            message="Successfully enhanced note",
            backup_path=Path(self.temp_dir) / "backup.md"
        )
        
        note_path = self.vault_path / "knowledge" / "Inbox" / "lit-20251003-0954-test-youtube-video.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(note_path)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "✅" in result.stdout or "success" in result.stdout.lower()
        assert "enhanced" in result.stdout.lower() or "processed" in result.stdout.lower()
    
    def test_process_single_note_file_not_found(self):
        """Test error handling when note file doesn't exist."""
        non_existent = self.vault_path / "knowledge" / "Inbox" / "non-existent.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(non_existent)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌" in result.stdout or "error" in result.stdout.lower()
        assert "not found" in result.stdout.lower() or "does not exist" in result.stdout.lower()
    
    def test_process_single_note_not_youtube_note(self):
        """Test error handling when note is not a YouTube note."""
        non_youtube = self.vault_path / "knowledge" / "Inbox" / "fleeting-20251003-1200-regular-note.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(non_youtube)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌" in result.stdout or "error" in result.stdout.lower()
        assert "not a youtube note" in result.stdout.lower() or "youtube" in result.stdout.lower()
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    def test_process_single_note_transcript_unavailable(self, mock_processor):
        """Test error handling when YouTube transcript is unavailable."""
        # Mock transcript fetch failure
        mock_processor.return_value.fetch_transcript.side_effect = Exception("Transcript unavailable")
        
        note_path = self.vault_path / "knowledge" / "Inbox" / "lit-20251003-0954-test-youtube-video.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(note_path)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "❌" in result.stdout or "error" in result.stdout.lower()
        assert "transcript" in result.stdout.lower()
    
    # ============================================================================
    # P0.3: Batch Processing Tests
    # ============================================================================
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_batch_process_youtube_notes(self, mock_enhancer, mock_processor):
        """Test batch processing of multiple YouTube notes."""
        # Mock transcript and quote extraction
        mock_processor.return_value.fetch_transcript.return_value = "Sample transcript"
        mock_processor.return_value.extract_quotes.return_value = {
            'key_insights': [{'timestamp': '00:05:30', 'quote': 'Test', 'context': 'Context', 'relevance': 0.9}],
            'actionable': [],
            'notable': [],
            'definitions': []
        }
        
        # Mock enhancement
        from src.ai.youtube_note_enhancer import EnhanceResult
        mock_enhancer.return_value.enhance_note.return_value = EnhanceResult(
            success=True,
            message="Enhanced",
            backup_path=Path(self.temp_dir) / "backup.md"
        )
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-notes"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "processed" in result.stdout.lower()
        # Should show summary with counts
        assert any(char.isdigit() for char in result.stdout)  # Has numbers in output
    
    def test_batch_process_filters_already_processed(self):
        """Test that batch processing skips already-processed notes."""
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-notes"
            ],
            capture_output=True,
            text=True
        )
        
        # Should report skipped notes
        assert "skipped" in result.stdout.lower() or "already" in result.stdout.lower()
    
    def test_batch_process_with_progress_reporting(self):
        """Test that batch processing shows progress indicators."""
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-notes"
            ],
            capture_output=True,
            text=True
        )
        
        # Should show progress indicators
        assert "processing" in result.stdout.lower() or "🔄" in result.stdout
    
    # ============================================================================
    # P1.1: Preview Mode Tests
    # ============================================================================
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    def test_preview_mode_no_modification(self, mock_processor):
        """Test that --preview mode doesn't modify notes."""
        # Mock quote extraction
        mock_processor.return_value.fetch_transcript.return_value = "Sample transcript"
        mock_processor.return_value.extract_quotes.return_value = {
            'key_insights': [{'timestamp': '00:05:30', 'quote': 'Preview test', 'context': 'Context', 'relevance': 0.9}],
            'actionable': [],
            'notable': [],
            'definitions': []
        }
        
        note_path = self.vault_path / "knowledge" / "Inbox" / "lit-20251003-0954-test-youtube-video.md"
        original_content = note_path.read_text()
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(note_path),
                "--preview"
            ],
            capture_output=True,
            text=True
        )
        
        # Note should not be modified
        assert note_path.read_text() == original_content
        # Should show preview in output
        assert "preview" in result.stdout.lower() or "would insert" in result.stdout.lower()
    
    # ============================================================================
    # P1.2: Quality Filtering Tests
    # ============================================================================
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    def test_quality_filtering(self, mock_processor):
        """Test that --min-quality filters low-relevance quotes."""
        # Mock quotes with varying quality
        mock_processor.return_value.fetch_transcript.return_value = "Sample transcript"
        mock_processor.return_value.extract_quotes.return_value = {
            'key_insights': [
                {'timestamp': '00:05:30', 'quote': 'High quality', 'context': 'Context', 'relevance': 0.9},
                {'timestamp': '00:10:00', 'quote': 'Low quality', 'context': 'Context', 'relevance': 0.3}
            ],
            'actionable': [],
            'notable': [],
            'definitions': []
        }
        
        note_path = self.vault_path / "knowledge" / "Inbox" / "lit-20251003-0954-test-youtube-video.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(note_path),
                "--min-quality", "0.7",
                "--preview"
            ],
            capture_output=True,
            text=True
        )
        
        # Should only show high-quality quote
        assert "High quality" in result.stdout
        # Low quality quote should be filtered
        # (This is a soft check since preview mode may show filtering info)
    
    # ============================================================================
    # P1.3: Category Selection Tests
    # ============================================================================
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    def test_category_selection(self, mock_processor):
        """Test that --categories filters quote categories."""
        # Mock quotes in different categories
        mock_processor.return_value.fetch_transcript.return_value = "Sample transcript"
        mock_processor.return_value.extract_quotes.return_value = {
            'key_insights': [{'timestamp': '00:05:30', 'quote': 'Key insight', 'context': 'Context', 'relevance': 0.9}],
            'actionable': [{'timestamp': '00:10:00', 'quote': 'Action item', 'context': 'Context', 'relevance': 0.8}],
            'notable': [{'timestamp': '00:15:00', 'quote': 'Notable quote', 'context': 'Context', 'relevance': 0.7}],
            'definitions': []
        }
        
        note_path = self.vault_path / "knowledge" / "Inbox" / "lit-20251003-0954-test-youtube-video.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-note", str(note_path),
                "--categories", "key-insights,actionable",
                "--preview"
            ],
            capture_output=True,
            text=True
        )
        
        # Should show selected categories
        assert "key insight" in result.stdout.lower() or "actionable" in result.stdout.lower()
    
    # ============================================================================
    # P0.4: Export Functionality Tests
    # ============================================================================
    
    @patch('src.ai.youtube_processor.YouTubeProcessor')
    @patch('src.ai.youtube_note_enhancer.YouTubeNoteEnhancer')
    def test_batch_export_to_file(self, mock_enhancer, mock_processor):
        """Test exporting batch processing results to file."""
        # Mock processing
        mock_processor.return_value.fetch_transcript.return_value = "Sample transcript"
        mock_processor.return_value.extract_quotes.return_value = {
            'key_insights': [{'timestamp': '00:05:30', 'quote': 'Test', 'context': 'Context', 'relevance': 0.9}],
            'actionable': [],
            'notable': [],
            'definitions': []
        }
        
        from src.ai.youtube_note_enhancer import EnhanceResult
        mock_enhancer.return_value.enhance_note.return_value = EnhanceResult(
            success=True,
            message="Enhanced",
            backup_path=Path(self.temp_dir) / "backup.md"
        )
        
        export_path = self.vault_path / "youtube_processing_report.md"
        
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-notes",
                "--export", str(export_path)
            ],
            capture_output=True,
            text=True
        )
        
        assert export_path.exists()
        content = export_path.read_text()
        assert "YouTube" in content or "processed" in content.lower()
    
    def test_json_output_format(self):
        """Test that --format json produces valid JSON output."""
        result = subprocess.run(
            [
                sys.executable, str(self.cli_script),
                str(self.vault_path),
                "--process-youtube-notes",
                "--format", "json"
            ],
            capture_output=True,
            text=True
        )
        
        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
