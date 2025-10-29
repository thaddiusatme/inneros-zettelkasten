"""
Tests for BatchProcessingCoordinator (ADR-002 Phase 11).

This module extracts batch processing logic from WorkflowManager
to reduce its size toward the <500 LOC target.

RED Phase: All tests should fail initially until GREEN phase implementation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil


# Import will fail until GREEN phase creates the module
try:
    from src.ai.batch_processing_coordinator import BatchProcessingCoordinator
except ImportError:
    BatchProcessingCoordinator = None


@pytest.fixture
def temp_inbox():
    """Create a temporary inbox directory with test notes."""
    temp_dir = tempfile.mkdtemp()
    inbox_dir = Path(temp_dir) / "Inbox"
    inbox_dir.mkdir()

    # Create test notes
    (inbox_dir / "note1.md").write_text("# Note 1\nContent")
    (inbox_dir / "note2.md").write_text("# Note 2\nContent")
    (inbox_dir / "note3.md").write_text("# Note 3\nContent")

    yield inbox_dir

    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_process_callback():
    """Create a mock process_inbox_note callback."""
    mock = Mock()
    mock.return_value = {
        "original_file": "test.md",
        "quality_score": 0.8,
        "recommendations": [
            {"action": "promote_to_permanent", "reason": "High quality"}
        ],
    }
    return mock


class TestBatchProcessingCoordinatorInitialization:
    """Test coordinator initialization and dependency injection."""

    def test_coordinator_initialization_with_required_dependencies(
        self, temp_inbox, mock_process_callback
    ):
        """Test that coordinator initializes with inbox_dir and process_callback."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        assert coordinator.inbox_dir == temp_inbox
        assert coordinator.process_callback == mock_process_callback

    def test_coordinator_initialization_validates_inbox_dir_exists(
        self, mock_process_callback
    ):
        """Test that coordinator validates inbox directory exists."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        nonexistent_dir = Path("/nonexistent/inbox")

        with pytest.raises((ValueError, FileNotFoundError)):
            BatchProcessingCoordinator(
                inbox_dir=nonexistent_dir, process_callback=mock_process_callback
            )

    def test_coordinator_initialization_requires_callable_process_callback(
        self, temp_inbox
    ):
        """Test that coordinator validates process_callback is callable."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        with pytest.raises((ValueError, TypeError)):
            BatchProcessingCoordinator(
                inbox_dir=temp_inbox, process_callback="not_a_function"
            )


class TestBatchProcessingCore:
    """Test core batch processing functionality."""

    def test_batch_process_inbox_processes_all_markdown_files(
        self, temp_inbox, mock_process_callback
    ):
        """Test that batch_process_inbox processes all .md files in inbox."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["total_files"] == 3
        assert mock_process_callback.call_count == 3

    def test_batch_process_inbox_returns_complete_results_structure(
        self, temp_inbox, mock_process_callback
    ):
        """Test that result contains all expected keys and structure."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        # Verify top-level structure
        assert "total_files" in result
        assert "processed" in result
        assert "failed" in result
        assert "results" in result
        assert "summary" in result

        # Verify summary structure
        assert "promote_to_permanent" in result["summary"]
        assert "move_to_fleeting" in result["summary"]
        assert "needs_improvement" in result["summary"]

    def test_batch_process_inbox_counts_successful_processing(
        self, temp_inbox, mock_process_callback
    ):
        """Test that successful processing increments processed count."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        mock_process_callback.return_value = {
            "original_file": "test.md",
            "quality_score": 0.8,
            "recommendations": [],
        }

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["processed"] == 3
        assert result["failed"] == 0

    def test_batch_process_inbox_handles_processing_errors(self, temp_inbox):
        """Test that processing errors increment failed count."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        mock_callback = Mock(side_effect=Exception("Processing failed"))

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["failed"] == 3
        assert result["processed"] == 0


class TestResultCategorization:
    """Test recommendation categorization and summary generation."""

    def test_batch_process_categorizes_promote_to_permanent(self, temp_inbox):
        """Test that promote_to_permanent recommendations are counted."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        mock_callback = Mock(
            return_value={
                "original_file": "test.md",
                "recommendations": [
                    {"action": "promote_to_permanent", "reason": "High quality"}
                ],
            }
        )

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["promote_to_permanent"] == 3

    def test_batch_process_categorizes_move_to_fleeting(self, temp_inbox):
        """Test that move_to_fleeting recommendations are counted."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        mock_callback = Mock(
            return_value={
                "original_file": "test.md",
                "recommendations": [
                    {"action": "move_to_fleeting", "reason": "Medium quality"}
                ],
            }
        )

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["move_to_fleeting"] == 3

    def test_batch_process_categorizes_needs_improvement(self, temp_inbox):
        """Test that improve_or_archive recommendations are counted."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        mock_callback = Mock(
            return_value={
                "original_file": "test.md",
                "recommendations": [
                    {"action": "improve_or_archive", "reason": "Low quality"}
                ],
            }
        )

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["needs_improvement"] == 3

    def test_batch_process_handles_multiple_recommendations(self, temp_inbox):
        """Test that multiple recommendations are all counted."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        # Mock callback returns different recommendations for each note
        call_count = [0]

        def callback_with_variations(note_path):
            call_count[0] += 1
            if call_count[0] == 1:
                return {
                    "original_file": note_path,
                    "recommendations": [
                        {"action": "promote_to_permanent", "reason": "High"}
                    ],
                }
            elif call_count[0] == 2:
                return {
                    "original_file": note_path,
                    "recommendations": [
                        {"action": "move_to_fleeting", "reason": "Medium"}
                    ],
                }
            else:
                return {
                    "original_file": note_path,
                    "recommendations": [
                        {"action": "improve_or_archive", "reason": "Low"}
                    ],
                }

        mock_callback = Mock(side_effect=callback_with_variations)

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["promote_to_permanent"] == 1
        assert result["summary"]["move_to_fleeting"] == 1
        assert result["summary"]["needs_improvement"] == 1


class TestProgressReporting:
    """Test progress reporting functionality."""

    @patch("sys.stderr")
    def test_batch_process_shows_progress_when_enabled(
        self, mock_stderr, temp_inbox, mock_process_callback
    ):
        """Test that progress is written to stderr when show_progress=True."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        result = coordinator.batch_process_inbox(show_progress=True)

        # Should have written progress updates
        assert mock_stderr.write.called
        assert mock_stderr.flush.called

    def test_batch_process_suppresses_progress_when_disabled(
        self, temp_inbox, mock_process_callback
    ):
        """Test that no progress is shown when show_progress=False."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        with patch("sys.stderr") as mock_stderr:
            result = coordinator.batch_process_inbox(show_progress=False)

            # Should not have written any progress
            assert not mock_stderr.write.called

    @patch("sys.stderr")
    def test_batch_process_clears_progress_line_after_completion(
        self, mock_stderr, temp_inbox, mock_process_callback
    ):
        """Test that progress line is cleared after processing completes."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        result = coordinator.batch_process_inbox(show_progress=True)

        # Should have cleared progress line
        write_calls = [call[0][0] for call in mock_stderr.write.call_args_list]
        assert any(
            " " * 80 in call for call in write_calls
        ), "Progress line not cleared"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_batch_process_handles_empty_inbox(self, mock_process_callback):
        """Test that empty inbox returns correct zero results."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        temp_dir = tempfile.mkdtemp()
        empty_inbox = Path(temp_dir) / "Inbox"
        empty_inbox.mkdir()

        try:
            coordinator = BatchProcessingCoordinator(
                inbox_dir=empty_inbox, process_callback=mock_process_callback
            )

            result = coordinator.batch_process_inbox(show_progress=False)

            assert result["total_files"] == 0
            assert result["processed"] == 0
            assert result["failed"] == 0
            assert len(result["results"]) == 0
        finally:
            shutil.rmtree(temp_dir)

    def test_batch_process_handles_error_results_with_error_key(self, temp_inbox):
        """Test that results containing 'error' key increment failed count."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        mock_callback = Mock(
            return_value={"original_file": "test.md", "error": "Processing failed"}
        )

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["failed"] == 3
        assert result["processed"] == 0

    def test_batch_process_includes_all_individual_results(
        self, temp_inbox, mock_process_callback
    ):
        """Test that all individual note results are included in results list."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            inbox_dir=temp_inbox, process_callback=mock_process_callback
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert len(result["results"]) == 3
        for note_result in result["results"]:
            assert "original_file" in note_result
