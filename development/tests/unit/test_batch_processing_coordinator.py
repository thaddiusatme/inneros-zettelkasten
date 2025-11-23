"""
Tests for BatchProcessingCoordinator (ADR-002 Phase 11).

This module extracts batch processing logic from WorkflowManager
to reduce its size toward the <500 LOC target.

RED Phase: All tests should fail initially until GREEN phase implementation.

GitHub Issue #45 Phase 2 Priority 3 (P1-VAULT-10):
- Vault config integration tests added
- Tests updated to use vault_with_config fixture
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from src.config.vault_config_loader import get_vault_config


# Import will fail until GREEN phase creates the module
try:
    from src.ai.batch_processing_coordinator import BatchProcessingCoordinator
except ImportError:
    BatchProcessingCoordinator = None


@pytest.fixture
def vault_with_config(tmp_path):
    """
    Fixture providing vault structure with vault configuration.

    Creates knowledge/ subdirectory structure as per vault_config.yaml.
    Used for vault config integration tests (GitHub Issue #45 Phase 2 Priority 3).

    Copied pattern from test_safe_image_processing_coordinator.py for consistency.
    """
    vault = tmp_path / "vault"
    vault.mkdir()

    # Get vault config (creates knowledge/ subdirectory structure)
    config = get_vault_config(str(vault))

    # Ensure vault config directories exist
    config.fleeting_dir.mkdir(parents=True, exist_ok=True)
    config.inbox_dir.mkdir(parents=True, exist_ok=True)
    config.permanent_dir.mkdir(parents=True, exist_ok=True)
    config.literature_dir.mkdir(parents=True, exist_ok=True)

    return {
        "vault": vault,
        "config": config,
        "fleeting_dir": config.fleeting_dir,
        "inbox_dir": config.inbox_dir,
        "permanent_dir": config.permanent_dir,
        "literature_dir": config.literature_dir,
    }


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


class TestBatchProcessingCoordinatorVaultConfigIntegration:
    """Test vault configuration integration (GitHub Issue #45 P1-VAULT-10)."""

    def test_coordinator_uses_vault_config_for_inbox_directory(self, vault_with_config):
        """
        Test that BatchProcessingCoordinator loads inbox path from vault config.

        Expected RED failure: TypeError about unexpected keyword arguments 'base_dir'
        and 'workflow_manager' because current constructor expects inbox_dir parameter.

        Target GREEN signature includes:
        - base_dir parameter for vault root
        - workflow_manager parameter for delegation pattern
        - Internal vault config loading for inbox_dir
        """
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented")

        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        # Create coordinator with vault config pattern (will fail in RED phase)
        coordinator = BatchProcessingCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(),
        )

        # Verify coordinator uses vault config path for inbox
        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.base_dir == vault


class TestBatchProcessingCoordinatorInitialization:
    """Test coordinator initialization and dependency injection."""

    def test_coordinator_initialization_with_required_dependencies(
        self, vault_with_config, mock_process_callback
    ):
        """Test that coordinator initializes with base_dir, workflow_manager, and process_callback."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        coordinator = BatchProcessingCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.process_callback == mock_process_callback
        assert coordinator.base_dir == vault

    def test_coordinator_initialization_validates_inbox_dir_exists(
        self, vault_with_config, mock_process_callback
    ):
        """Test that coordinator creates inbox directory if it doesn't exist."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        # Coordinator should use vault config inbox path
        coordinator = BatchProcessingCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        # Verify coordinator uses vault config inbox directory
        assert coordinator.inbox_dir.exists()
        assert coordinator.inbox_dir == config.inbox_dir

    def test_coordinator_initialization_requires_callable_process_callback(
        self, vault_with_config
    ):
        """Test that coordinator validates process_callback is callable."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        vault = vault_with_config["vault"]

        with pytest.raises((ValueError, TypeError)):
            BatchProcessingCoordinator(
                base_dir=vault,
                workflow_manager=Mock(),
                process_callback="not_a_function",
            )


class TestBatchProcessingCore:
    """Test core batch processing functionality."""

    @pytest.fixture
    def coordinator_with_notes(self, vault_with_config, mock_process_callback):
        """Create coordinator with test notes in vault inbox."""
        inbox_dir = vault_with_config["inbox_dir"]

        # Create test notes
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")

        return BatchProcessingCoordinator(
            base_dir=vault_with_config["vault"],
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

    def test_batch_process_inbox_processes_all_markdown_files(
        self, coordinator_with_notes, mock_process_callback
    ):
        """Test that batch_process_inbox processes all .md files in inbox."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = coordinator_with_notes

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["total_files"] == 3
        assert mock_process_callback.call_count == 3

    def test_batch_process_inbox_returns_complete_results_structure(
        self, coordinator_with_notes
    ):
        """Test that result contains all expected keys and structure."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = coordinator_with_notes

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

    def test_batch_process_inbox_counts_successful_processing(self, vault_with_config):
        """Test that successful processing increments processed count."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        inbox_dir = vault_with_config["inbox_dir"]
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")

        mock_callback = Mock()
        mock_callback.return_value = {
            "original_file": "test.md",
            "quality_score": 0.8,
            "recommendations": [],
        }

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_config["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["processed"] == 3
        assert result["failed"] == 0

    def test_batch_process_inbox_handles_processing_errors(self, vault_with_config):
        """Test that processing errors increment failed count."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        inbox_dir = vault_with_config["inbox_dir"]
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")

        mock_callback = Mock(side_effect=Exception("Processing failed"))

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_config["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["failed"] == 3
        assert result["processed"] == 0


class TestResultCategorization:
    """Test recommendation categorization and summary generation."""

    @pytest.fixture
    def setup_vault_with_notes(self, vault_with_config):
        """Setup vault with test notes."""
        inbox_dir = vault_with_config["inbox_dir"]
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")
        return vault_with_config

    def test_batch_process_categorizes_promote_to_permanent(
        self, setup_vault_with_notes
    ):
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
            base_dir=setup_vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["promote_to_permanent"] == 3

    def test_batch_process_categorizes_move_to_fleeting(self, setup_vault_with_notes):
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
            base_dir=setup_vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["move_to_fleeting"] == 3

    def test_batch_process_categorizes_needs_improvement(self, setup_vault_with_notes):
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
            base_dir=setup_vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["needs_improvement"] == 3

    def test_batch_process_handles_multiple_recommendations(
        self, setup_vault_with_notes
    ):
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
            base_dir=setup_vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["summary"]["promote_to_permanent"] == 1
        assert result["summary"]["move_to_fleeting"] == 1
        assert result["summary"]["needs_improvement"] == 1


class TestProgressReporting:
    """Test progress reporting functionality."""

    @pytest.fixture
    def vault_with_notes(self, vault_with_config, mock_process_callback):
        """Create vault with test notes."""
        inbox_dir = vault_with_config["inbox_dir"]
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")
        return vault_with_config

    @patch("sys.stderr")
    def test_batch_process_shows_progress_when_enabled(
        self, mock_stderr, vault_with_notes, mock_process_callback
    ):
        """Test that progress is written to stderr when show_progress=True."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=True)

        # Should have written progress updates
        assert mock_stderr.write.called
        assert mock_stderr.flush.called

    def test_batch_process_suppresses_progress_when_disabled(
        self, vault_with_notes, mock_process_callback
    ):
        """Test that no progress is shown when show_progress=False."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        with patch("sys.stderr") as mock_stderr:
            result = coordinator.batch_process_inbox(show_progress=False)

            # Should not have written any progress
            assert not mock_stderr.write.called

    @patch("sys.stderr")
    def test_batch_process_clears_progress_line_after_completion(
        self, mock_stderr, vault_with_notes, mock_process_callback
    ):
        """Test that progress line is cleared after processing completes."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_notes["vault"],
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=True)

        # Should have cleared progress line
        write_calls = [call[0][0] for call in mock_stderr.write.call_args_list]
        assert any(
            " " * 80 in call for call in write_calls
        ), "Progress line not cleared"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_batch_process_handles_empty_inbox(
        self, vault_with_config, mock_process_callback
    ):
        """Test that empty inbox returns correct zero results."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        # Vault inbox already exists but is empty
        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_config["vault"],
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["total_files"] == 0
        assert result["processed"] == 0
        assert result["failed"] == 0
        assert len(result["results"]) == 0

    def test_batch_process_handles_error_results_with_error_key(
        self, vault_with_config
    ):
        """Test that results containing 'error' key increment failed count."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        inbox_dir = vault_with_config["inbox_dir"]
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")

        mock_callback = Mock(
            return_value={"original_file": "test.md", "error": "Processing failed"}
        )

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_config["vault"],
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert result["failed"] == 3
        assert result["processed"] == 0

    def test_batch_process_includes_all_individual_results(
        self, vault_with_config, mock_process_callback
    ):
        """Test that all individual note results are included in results list."""
        if BatchProcessingCoordinator is None:
            pytest.skip("BatchProcessingCoordinator not yet implemented (RED phase)")

        inbox_dir = vault_with_config["inbox_dir"]
        (inbox_dir / "note1.md").write_text("# Note 1\nContent")
        (inbox_dir / "note2.md").write_text("# Note 2\nContent")
        (inbox_dir / "note3.md").write_text("# Note 3\nContent")

        coordinator = BatchProcessingCoordinator(
            base_dir=vault_with_config["vault"],
            workflow_manager=Mock(),
            process_callback=mock_process_callback,
        )

        result = coordinator.batch_process_inbox(show_progress=False)

        assert len(result["results"]) == 3
        for note_result in result["results"]:
            assert "original_file" in note_result
