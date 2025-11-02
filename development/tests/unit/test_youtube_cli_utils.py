"""
TDD Iteration 3 RED Phase: YouTube CLI Utilities Tests
Comprehensive failing tests for 5 utility classes

Following proven TDD patterns from:
- Smart Link Management TDD iterations (utility testing)
- Advanced Tag Enhancement (CLI testing)
- Safe Workflow CLI Utils (orchestrator testing)

Test Structure:
- YouTubeCLIProcessor: 5 tests (orchestration, workflows, integration)
- BatchProgressReporter: 3 tests (progress, formatting, statistics)
- YouTubeNoteValidator: 3 tests (validation, error handling, edge cases)
- CLIOutputFormatter: 2 tests (formatting, quiet mode)
- CLIExportManager: 2 tests (markdown, JSON export)

Total: 15+ comprehensive tests
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add development directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.youtube_cli_utils import (
    YouTubeCLIProcessor,
    BatchProgressReporter,
    YouTubeNoteValidator,
    CLIOutputFormatter,
    CLIExportManager,
    ProcessingResult,
    BatchStatistics,
)


# ============================================================================
# YouTubeCLIProcessor Tests (5 tests)
# ============================================================================


class TestYouTubeCLIProcessor:
    """Test main orchestrator class"""

    def test_cli_processor_single_note_success(self, tmp_path):
        """Test successful single note processing workflow"""
        # RED Phase: This test will fail because processor not implemented

        # Setup: Create test note with YouTube metadata
        note_path = tmp_path / "test-youtube-note.md"
        note_path.write_text(
            """---
type: literature
source: youtube
url: https://www.youtube.com/watch?v=test123
created: 2025-10-06 19:00
ai_processed: false
---

# Test Video

## Why I'm Saving This
Interesting AI content
"""
        )

        # Mock YouTube components since test uses fake video ID
        with patch(
            "src.cli.youtube_processor.YouTubeProcessor"
        ) as MockProcessor, patch(
            "src.ai.youtube_note_enhancer.YouTubeNoteEnhancer"
        ) as MockEnhancer:

            # Setup mocks - fetch_transcript returns dict with 'transcript' key
            mock_processor_instance = MockProcessor.return_value
            mock_processor_instance.extract_video_id.return_value = "test123"
            mock_processor_instance.fetcher.fetch_transcript.return_value = {
                "transcript": [
                    {"text": "Test segment 1", "start": 0.0, "duration": 2.0},
                    {"text": "Test segment 2", "start": 2.0, "duration": 2.0},
                ]
            }
            mock_processor_instance.fetcher.format_for_llm.return_value = "Test transcript formatted for LLM"
            mock_processor_instance.extractor.extract_quotes.return_value = {
                "quotes": [
                    {"text": "Test quote", "timestamp": "0:00", "context": "Test", "category": "key-insight", "relevance_score": 0.9}
                ]
            }

            mock_enhance_result = Mock(
                success=True, backup_path=tmp_path / "backup.md", error_message=None
            )
            MockEnhancer.return_value.enhance_note.return_value = mock_enhance_result

            # Execute: Process note
            processor = YouTubeCLIProcessor(str(tmp_path))
            result = processor.process_single_note(note_path)

            # Assert: Success with valid result
            assert result.success is True
            assert result.note_path == note_path
            assert result.quotes_inserted > 0
            assert result.backup_path is not None
            assert result.error_message is None
            assert result.processing_time >= 0

    def test_cli_processor_file_not_found(self, tmp_path):
        """Test error handling when note file doesn't exist"""
        # RED Phase: This test will fail because processor not implemented

        # Setup: Non-existent note path
        note_path = tmp_path / "nonexistent-note.md"

        # Execute: Try to process
        processor = YouTubeCLIProcessor(str(tmp_path))
        result = processor.process_single_note(note_path)

        # Assert: Failure with clear error message
        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
        assert result.quotes_inserted == 0

    def test_cli_processor_not_youtube_note(self, tmp_path):
        """Test error handling when note is not a YouTube note"""
        # RED Phase: This test will fail because processor not implemented

        # Setup: Create note without YouTube source
        note_path = tmp_path / "regular-note.md"
        note_path.write_text(
            """---
type: fleeting
source: article
created: 2025-10-06 19:00
---

# Regular Note
This is not a YouTube note
"""
        )

        # Execute: Try to process
        processor = YouTubeCLIProcessor(str(tmp_path))
        result = processor.process_single_note(note_path)

        # Assert: Failure with informative message
        assert result.success is False
        assert result.error_message is not None
        assert "youtube" in result.error_message.lower()

    def test_cli_processor_batch_empty(self, tmp_path):
        """Test batch processing with no YouTube notes"""
        # RED Phase: This test will fail because processor not implemented

        # Setup: Empty Inbox directory
        inbox = tmp_path / "Inbox"
        inbox.mkdir()

        # Execute: Batch process
        processor = YouTubeCLIProcessor(str(tmp_path))
        stats = processor.process_batch()

        # Assert: Zero notes processed
        assert stats.total_notes == 0
        assert stats.successful == 0
        assert stats.failed == 0
        assert stats.skipped == 0

    def test_cli_processor_integration(self, tmp_path):
        """Test complete workflow: validation -> fetch -> extract -> enhance"""
        # RED Phase: This test will fail because processor not implemented

        # Setup: Create test vault structure and note
        inbox_dir = tmp_path / "Inbox"
        inbox_dir.mkdir()
        note_path = inbox_dir / "youtube-note.md"
        note_path.write_text(
            """---
type: literature
source: youtube
url: https://www.youtube.com/watch?v=test123
video_id: test123
---

# Test YouTube Note

User content here.
"""
        )

        # Mock YouTube components
        with patch(
            "src.cli.youtube_processor.YouTubeProcessor"
        ) as MockProcessor, patch(
            "src.ai.youtube_note_enhancer.YouTubeNoteEnhancer"
        ) as MockEnhancer:

            # Setup mocks - match expected data structures
            mock_processor_instance = MockProcessor.return_value
            mock_processor_instance.extract_video_id.return_value = "test123"
            mock_processor_instance.fetcher.fetch_transcript.return_value = {
                "transcript": [
                    {"text": "Test segment 1", "start": 0.0, "duration": 2.0},
                    {"text": "Test segment 2", "start": 2.0, "duration": 2.0},
                ]
            }
            mock_processor_instance.fetcher.format_for_llm.return_value = "Test transcript formatted for LLM"
            mock_processor_instance.extractor.extract_quotes.return_value = {
                "quotes": [
                    {"text": "Test quote", "timestamp": "0:00", "context": "Test", "category": "key-insight", "relevance_score": 0.9}
                ]
            }
            mock_enhancer_return_value = Mock(
                success=True, backup_path=tmp_path / "backup.md", error_message=None
            )
            MockEnhancer.return_value.enhance_note.return_value = mock_enhancer_return_value

            # Execute: Process with integration
            processor = YouTubeCLIProcessor(str(tmp_path))
            result = processor.process_single_note(note_path)

            # Assert: Integration working
            assert result.success is True
            MockProcessor.return_value.fetcher.fetch_transcript.assert_called_once()
            MockEnhancer.return_value.enhance_note.assert_called_once()


# ============================================================================
# BatchProgressReporter Tests (3 tests)
# ============================================================================


class TestBatchProgressReporter:
    """Test progress tracking and reporting"""

    def test_progress_reporting_format(self, capsys):
        """Test progress message formatting"""
        # RED Phase: This test will fail because reporter not implemented

        # Setup: Reporter for 10 notes
        reporter = BatchProgressReporter(total_notes=10)

        # Execute: Report progress
        reporter.report_progress(current=3, note_name="test-note.md")
        captured = capsys.readouterr()

        # Assert: Formatted progress message with emoji
        assert "3/10" in captured.out or "3 of 10" in captured.out
        assert "test-note.md" in captured.out
        assert "🔄" in captured.out or "⏳" in captured.out

    def test_summary_statistics(self):
        """Test summary generation with statistics"""
        # RED Phase: This test will fail because reporter not implemented

        # Setup: Reporter and statistics
        reporter = BatchProgressReporter(total_notes=10)
        stats = BatchStatistics(
            total_notes=10,
            successful=7,
            failed=2,
            skipped=1,
            total_quotes=35,
            total_time=120.5,
            notes_per_second=0.058,
        )

        # Execute: Generate summary
        summary = reporter.generate_summary(stats)

        # Assert: Summary contains key metrics with emojis
        assert "7" in summary  # Successful count
        assert "2" in summary  # Failed count
        assert "35" in summary  # Total quotes
        assert "✅" in summary  # Success emoji
        assert "❌" in summary  # Failed emoji

    def test_emoji_indicators(self, capsys):
        """Test emoji usage in status messages"""
        # RED Phase: This test will fail because reporter not implemented

        # Setup: Reporter
        reporter = BatchProgressReporter(total_notes=5)

        # Execute: Report different statuses
        reporter.report_success("note1.md", quotes_count=5)
        reporter.report_failure("note2.md", error="Transcript unavailable")
        reporter.report_skip("note3.md", reason="Already processed")
        captured = capsys.readouterr()

        # Assert: Appropriate emojis used
        assert "✅" in captured.out  # Success emoji
        assert "❌" in captured.out  # Failure emoji
        assert "⚠️" in captured.out  # Skip emoji


# ============================================================================
# YouTubeNoteValidator Tests (3 tests)
# ============================================================================


class TestYouTubeNoteValidator:
    """Test validation logic"""

    def test_validate_youtube_note_success(self, tmp_path):
        """Test validation of valid YouTube note"""
        # RED Phase: This test will fail because validator not implemented

        # Setup: Create valid YouTube note
        note_path = tmp_path / "youtube-note.md"
        note_path.write_text(
            """---
type: literature
source: youtube
url: https://www.youtube.com/watch?v=test123
created: 2025-10-06 19:00
ai_processed: false
---

# Test Video
"""
        )

        # Execute: Validate
        is_valid, error_msg, metadata = YouTubeNoteValidator.validate_youtube_note(
            note_path
        )

        # Assert: Valid with metadata
        assert is_valid is True
        assert error_msg is None
        assert metadata["source"] == "youtube"
        assert metadata["url"] == "https://www.youtube.com/watch?v=test123"

    def test_validate_missing_source(self, tmp_path):
        """Test validation when source field missing"""
        # RED Phase: This test will fail because validator not implemented

        # Setup: Note without source field
        note_path = tmp_path / "note-no-source.md"
        note_path.write_text(
            """---
type: literature
created: 2025-10-06 19:00
---

# Note Without Source
"""
        )

        # Execute: Validate
        is_valid, error_msg, metadata = YouTubeNoteValidator.validate_youtube_note(
            note_path
        )

        # Assert: Invalid with helpful error
        assert is_valid is False
        assert error_msg is not None
        assert "source" in error_msg.lower()

    def test_validate_already_processed(self, tmp_path):
        """Test detection of already processed notes"""
        # RED Phase: This test will fail because validator not implemented

        # Setup: Note with ai_processed: true
        note_path = tmp_path / "processed-note.md"
        note_path.write_text(
            """---
type: literature
source: youtube
url: https://www.youtube.com/watch?v=test123
created: 2025-10-06 19:00
ai_processed: true
---

# Already Processed Video
"""
        )

        # Execute: Parse and check
        _, _, metadata = YouTubeNoteValidator.validate_youtube_note(note_path)
        is_processed = YouTubeNoteValidator.is_already_processed(metadata)

        # Assert: Detected as processed
        assert is_processed is True


# ============================================================================
# CLIOutputFormatter Tests (2 tests)
# ============================================================================


class TestCLIOutputFormatter:
    """Test output formatting"""

    def test_format_batch_summary(self):
        """Test batch summary formatting"""
        # RED Phase: This test will fail because formatter not implemented

        # Setup: Formatter and statistics
        formatter = CLIOutputFormatter()
        stats = BatchStatistics(
            total_notes=10,
            successful=8,
            failed=1,
            skipped=1,
            total_quotes=40,
            total_time=150.0,
        )

        # Execute: Format summary
        summary = formatter.format_batch_summary(stats)

        # Assert: Well-formatted summary with emojis and statistics
        assert "8" in summary  # Successful
        assert "1" in summary  # Failed
        assert "40" in summary  # Quotes
        assert "✅" in summary
        assert "📊" in summary or "📈" in summary

    def test_json_only_mode(self, capsys):
        """Test quiet mode suppresses stdout except JSON"""
        # RED Phase: This test will fail because formatter not implemented

        # Setup: Formatter in quiet mode
        formatter = CLIOutputFormatter(quiet_mode=True)
        stats = BatchStatistics(total_notes=5, successful=5, failed=0, skipped=0)

        # Execute: Try to print messages and JSON
        formatter.print_output("This should be suppressed")
        json_output = formatter.format_json_output(stats)
        print(json_output)  # This should appear
        captured = capsys.readouterr()

        # Assert: Only JSON in output
        assert "This should be suppressed" not in captured.out
        assert "successful" in captured.out
        # Verify it's valid JSON
        parsed = json.loads(json_output)
        assert parsed["successful"] == 5


# ============================================================================
# CLIExportManager Tests (2 tests)
# ============================================================================


class TestCLIExportManager:
    """Test export functionality"""

    def test_export_markdown_report(self, tmp_path):
        """Test markdown report generation"""
        # RED Phase: This test will fail because export manager not implemented

        # Setup: Statistics and results
        stats = BatchStatistics(
            total_notes=10, successful=8, failed=2, skipped=0, total_quotes=40
        )
        results = [
            ProcessingResult(
                success=True, note_path=Path("note1.md"), quotes_inserted=5
            ),
            ProcessingResult(
                success=False,
                note_path=Path("note2.md"),
                error_message="Transcript unavailable",
            ),
        ]
        export_path = tmp_path / "report.md"

        # Execute: Export
        success = CLIExportManager.export_markdown_report(stats, export_path, results)

        # Assert: File created with content
        assert success is True
        assert export_path.exists()
        content = export_path.read_text()
        assert "YouTube Processing Report" in content or "Summary" in content
        assert "8" in content  # Successful count
        assert "2" in content  # Failed count

    def test_export_json_output(self, tmp_path):
        """Test JSON export"""
        # RED Phase: This test will fail because export manager not implemented

        # Setup: Statistics
        stats = BatchStatistics(
            total_notes=5, successful=4, failed=1, skipped=0, total_quotes=20
        )
        export_path = tmp_path / "stats.json"

        # Execute: Export JSON
        json_str = CLIExportManager.export_json_output(stats, export_path)

        # Assert: Valid JSON with correct data
        parsed = json.loads(json_str)
        assert parsed["successful"] == 4
        assert parsed["failed"] == 1
        assert parsed["total"] == 5 or parsed["total_notes"] == 5

        # Assert: File created if path provided
        if export_path:
            assert export_path.exists()
            file_content = json.loads(export_path.read_text())
            assert file_content["successful"] == 4


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Test utility classes working together"""

    def test_complete_workflow_integration(self, tmp_path):
        """Test all utilities working together in complete workflow"""
        # RED Phase: This test will fail because utilities not implemented

        # Setup: Create test environment
        inbox = tmp_path / "Inbox"
        inbox.mkdir()

        # Create 3 YouTube notes
        for i in range(3):
            note = inbox / f"youtube-note-{i}.md"
            note.write_text(
                f"""---
type: literature
source: youtube
url: https://www.youtube.com/watch?v=test{i}
created: 2025-10-06 19:00
ai_processed: false
---

# Test Video {i}

## Why I'm Saving This
Test content {i}
"""
            )

        # Execute: Process batch with all utilities
        processor = YouTubeCLIProcessor(str(tmp_path))
        formatter = CLIOutputFormatter()

        with patch("src.cli.youtube_processor.YouTubeProcessor"), patch(
            "src.ai.youtube_note_enhancer.YouTubeNoteEnhancer"
        ):
            stats = processor.process_batch()
            summary = formatter.format_batch_summary(stats)

        # Assert: Complete workflow executed
        assert stats.total_notes == 3
        assert summary is not None
        assert "3" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
