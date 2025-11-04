"""
Tests for FleetingNoteCoordinator (ADR-002 Phase 12b)

RED Phase: Comprehensive failing tests for fleeting note management extraction.
Target: Extract ~250-300 LOC from WorkflowManager (fleeting note triage and promotion).

Vault Config Integration (GitHub Issue #45 Phase 2 Priority 3):
Updated to use vault configuration for directory paths.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Target class (doesn't exist yet - RED phase)
from src.ai.fleeting_note_coordinator import FleetingNoteCoordinator
from src.config.vault_config_loader import get_vault_config


@pytest.fixture
def vault_with_config(tmp_path):
    """
    Fixture providing vault structure with vault configuration.
    
    Creates knowledge/ subdirectory structure as per vault_config.yaml.
    Used for vault config integration tests.
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
    
    # Create legacy directories for WorkflowManager compatibility
    # TODO: Remove after WorkflowManager migrates to vault config
    (vault / "Fleeting Notes").mkdir(parents=True, exist_ok=True)
    (vault / "Inbox").mkdir(parents=True, exist_ok=True)
    (vault / "Permanent Notes").mkdir(parents=True, exist_ok=True)
    (vault / "Literature Notes").mkdir(parents=True, exist_ok=True)
    
    return {
        "vault": vault,
        "config": config,
        "fleeting_dir": config.fleeting_dir,
        "inbox_dir": config.inbox_dir,
        "permanent_dir": config.permanent_dir,
        "literature_dir": config.literature_dir,
    }


class TestFleetingNoteCoordinatorInitialization:
    """Test FleetingNoteCoordinator initialization and dependency management."""

    def test_initialization_with_required_dependencies(self, vault_with_config):
        """Test coordinator initialization with all required dependencies."""
        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        # Mock workflow_manager
        mock_workflow_manager = Mock()
        mock_process_callback = Mock(return_value={"quality_score": 0.8})

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=mock_workflow_manager,
            process_callback=mock_process_callback,
        )

        # Should use vault config paths
        assert coordinator.fleeting_dir == config.fleeting_dir
        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.permanent_dir == config.permanent_dir
        assert coordinator.process_callback is mock_process_callback

    def test_initialization_validates_directory_paths(self, vault_with_config):
        """Test coordinator validates that directory paths exist or can be created."""
        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        # Create coordinator (should create directories if they don't exist)
        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
        )

        # Directories should exist after initialization
        assert coordinator.fleeting_dir.exists()
        assert coordinator.inbox_dir.exists()
        assert coordinator.fleeting_dir == config.fleeting_dir

    def test_initialization_accepts_quality_threshold_config(self, vault_with_config):
        """Test coordinator accepts quality threshold configuration."""
        vault = vault_with_config["vault"]

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            default_quality_threshold=0.75,
        )

        assert coordinator.default_quality_threshold == 0.75


class TestFleetingNoteDiscovery:
    """Test fleeting note discovery and scanning functionality."""

    def test_find_fleeting_notes_in_fleeting_directory(self, vault_with_config):
        """Test finding notes in Fleeting Notes directory."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        # Create test fleeting notes
        note1 = fleeting_dir / "fleeting1.md"
        note1.write_text("---\ntype: fleeting\n---\nContent")
        note2 = fleeting_dir / "fleeting2.md"
        note2.write_text("---\ntype: fleeting\n---\nContent")

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
        )

        notes = coordinator.find_fleeting_notes()

        assert len(notes) == 2
        assert note1 in notes
        assert note2 in notes

    def test_find_fleeting_notes_in_inbox_with_fleeting_type(self, vault_with_config):
        """Test finding fleeting-type notes in Inbox directory."""
        vault = vault_with_config["vault"]
        inbox_dir = vault_with_config["inbox_dir"]

        # Create inbox notes with fleeting type
        fleeting_in_inbox = inbox_dir / "inbox_fleeting.md"
        fleeting_in_inbox.write_text("---\ntype: fleeting\n---\nContent")

        permanent_in_inbox = inbox_dir / "inbox_permanent.md"
        permanent_in_inbox.write_text("---\ntype: permanent\n---\nContent")

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
        )

        notes = coordinator.find_fleeting_notes()

        assert len(notes) == 1
        assert fleeting_in_inbox in notes
        assert permanent_in_inbox not in notes

    def test_find_fleeting_notes_handles_missing_directories(self, vault_with_config):
        """Test finding fleeting notes when directories don't exist."""
        vault = vault_with_config["vault"]

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
        )

        notes = coordinator.find_fleeting_notes()

        # Should return empty list, not error
        assert isinstance(notes, list)

    def test_find_fleeting_notes_handles_unparseable_files(self, vault_with_config):
        """Test finding fleeting notes skips files that can't be parsed."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        # Create valid and invalid notes
        valid_note = fleeting_dir / "valid.md"
        valid_note.write_text("---\ntype: fleeting\n---\nContent")

        invalid_note = fleeting_dir / "invalid.md"
        invalid_note.write_text("Invalid YAML\n---\nBroken")

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
        )

        notes = coordinator.find_fleeting_notes()

        # Should find at least the valid note (invalid might be skipped)
        assert valid_note in notes


class TestTriageReportGeneration:
    """Test fleeting note triage report generation."""

    def test_generate_triage_report_with_quality_distribution(self, vault_with_config):
        """Test generating triage report with quality score distribution."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        # Create test notes
        (fleeting_dir / "high_quality.md").write_text(
            "---\ntype: fleeting\n---\nContent"
        )
        (fleeting_dir / "medium_quality.md").write_text(
            "---\ntype: fleeting\n---\nContent"
        )
        (fleeting_dir / "low_quality.md").write_text(
            "---\ntype: fleeting\n---\nContent"
        )

        # Mock process callback with varying quality scores
        def mock_process(note_path, fast=False):
            if "high" in str(note_path):
                return {
                    "quality_score": 0.85,
                    "ai_tags": ["tag1"],
                    "metadata": {"created": "2024-01-01"},
                }
            elif "medium" in str(note_path):
                return {
                    "quality_score": 0.55,
                    "ai_tags": ["tag2"],
                    "metadata": {"created": "2024-01-02"},
                }
            else:
                return {
                    "quality_score": 0.25,
                    "ai_tags": ["tag3"],
                    "metadata": {"created": "2024-01-03"},
                }

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_process,
        )

        report = coordinator.generate_triage_report()

        assert report["total_notes_processed"] == 3
        assert report["quality_distribution"]["high"] == 1
        assert report["quality_distribution"]["medium"] == 1
        assert report["quality_distribution"]["low"] == 1
        assert len(report["recommendations"]) == 3

    def test_generate_triage_report_filters_by_quality_threshold(self, vault_with_config):
        """Test triage report filters recommendations by quality threshold."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        (fleeting_dir / "high.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "low.md").write_text("---\ntype: fleeting\n---\nContent")

        def mock_process(note_path, fast=False):
            if "high" in str(note_path):
                return {"quality_score": 0.85, "ai_tags": [], "metadata": {}}
            else:
                return {"quality_score": 0.25, "ai_tags": [], "metadata": {}}

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_process,
        )

        report = coordinator.generate_triage_report(quality_threshold=0.7)

        assert report["total_notes_processed"] == 2
        assert len(report["recommendations"]) == 1  # Only high quality note
        assert report["filtered_count"] == 1

    def test_generate_triage_report_handles_empty_directory(self, vault_with_config):
        """Test triage report handles empty fleeting notes directory."""
        vault = vault_with_config["vault"]

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(),
        )

        report = coordinator.generate_triage_report()

        assert report["total_notes_processed"] == 0
        assert report["quality_distribution"] == {"high": 0, "medium": 0, "low": 0}
        assert len(report["recommendations"]) == 0

    def test_generate_triage_report_tracks_processing_time(self, vault_with_config):
        """Test triage report tracks and reports processing time."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        (fleeting_dir / "note.md").write_text("---\ntype: fleeting\n---\nContent")

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(
                return_value={"quality_score": 0.5, "ai_tags": [], "metadata": {}}
            ),
        )

        report = coordinator.generate_triage_report()

        assert "processing_time" in report
        assert isinstance(report["processing_time"], (int, float))
        assert report["processing_time"] >= 0

    def test_generate_triage_report_sorts_by_quality_score(self, vault_with_config):
        """Test triage report sorts recommendations by quality score (highest first)."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        (fleeting_dir / "low.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "high.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "medium.md").write_text("---\ntype: fleeting\n---\nContent")

        def mock_process(note_path, fast=False):
            if "low" in str(note_path):
                return {"quality_score": 0.2, "ai_tags": [], "metadata": {}}
            elif "high" in str(note_path):
                return {"quality_score": 0.9, "ai_tags": [], "metadata": {}}
            else:
                return {"quality_score": 0.5, "ai_tags": [], "metadata": {}}

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_process,
        )

        report = coordinator.generate_triage_report()

        # Recommendations should be sorted by quality score descending
        scores = [rec["quality_score"] for rec in report["recommendations"]]
        assert scores == sorted(scores, reverse=True)
        assert scores[0] == 0.9
        assert scores[-1] == 0.2


class TestSingleNotePromotion:
    """Test single fleeting note promotion functionality."""

    @patch("src.utils.directory_organizer.DirectoryOrganizer")
    def test_promote_fleeting_note_to_permanent(self, mock_organizer, vault_with_config):
        """Test promoting single fleeting note to permanent notes."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        note = fleeting_dir / "test_note.md"
        note.write_text("---\ntype: fleeting\n---\nContent")

        # Mock DirectoryOrganizer
        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(
                return_value={"quality_score": 0.8, "ai_tags": [], "metadata": {}}
            ),
        )

        result = coordinator.promote_fleeting_note(
            str(note), target_type="permanent", base_dir=vault
        )

        assert result["success"] is True
        assert result["promoted_notes"][0]["target_type"] == "permanent"
        assert result["backup_created"] is True
        mock_organizer.assert_called_once()

    @patch("src.utils.directory_organizer.DirectoryOrganizer")
    def test_promote_fleeting_note_with_preview_mode(self, mock_organizer, vault_with_config):
        """Test promoting note in preview mode (no actual changes)."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        note = fleeting_dir / "test_note.md"
        note.write_text("---\ntype: fleeting\n---\nContent")

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(),
        )

        result = coordinator.promote_fleeting_note(str(note), preview_mode=True)

        assert result["preview"] is True
        assert note.exists()  # Note should still exist
        # DirectoryOrganizer should not be called in preview mode
        mock_organizer.assert_not_called()

    def test_promote_fleeting_note_handles_invalid_path(self, vault_with_config):
        """Test promotion handles invalid note paths gracefully."""
        vault = vault_with_config["vault"]

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(),
        )

        result = coordinator.promote_fleeting_note("/nonexistent/note.md")

        assert "error" in result or result["success"] is False

    @patch("src.utils.directory_organizer.DirectoryOrganizer")
    def test_promote_fleeting_note_updates_metadata(self, mock_organizer, vault_with_config):
        """Test promotion updates note metadata correctly."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]
        permanent_dir = vault_with_config["permanent_dir"]

        note = fleeting_dir / "test_note.md"
        note.write_text("---\ntype: fleeting\ncreated: 2024-01-01\n---\nContent")

        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(),
        )

        result = coordinator.promote_fleeting_note(str(note), target_type="permanent")

        # Verify metadata update expectations
        assert result["success"] is True
        assert "promoted_date" in result or "metadata_updated" in result


class TestBatchPromotion:
    """Test batch fleeting note promotion functionality."""

    @patch("src.utils.directory_organizer.DirectoryOrganizer")
    def test_promote_fleeting_notes_batch_by_quality_threshold(
        self, mock_organizer, vault_with_config
    ):
        """Test batch promotion based on quality threshold."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        (fleeting_dir / "high1.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "high2.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "low.md").write_text("---\ntype: fleeting\n---\nContent")

        def mock_process(note_path, fast=False):
            if "high" in str(note_path):
                return {"quality_score": 0.85, "ai_tags": [], "metadata": {}}
            else:
                return {"quality_score": 0.35, "ai_tags": [], "metadata": {}}

        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_process,
        )

        result = coordinator.promote_fleeting_notes_batch(quality_threshold=0.7)

        assert result["total_promoted"] == 2
        assert result["total_skipped"] == 1

    @patch("src.utils.directory_organizer.DirectoryOrganizer")
    def test_promote_fleeting_notes_batch_tracks_statistics(
        self, mock_organizer, vault_with_config
    ):
        """Test batch promotion tracks detailed statistics."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        (fleeting_dir / "note1.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "note2.md").write_text("---\ntype: fleeting\n---\nContent")

        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(
                return_value={"quality_score": 0.8, "ai_tags": [], "metadata": {}}
            ),
        )

        result = coordinator.promote_fleeting_notes_batch(quality_threshold=0.7)

        assert "total_promoted" in result
        assert "total_skipped" in result
        assert "processing_time" in result
        assert "promoted_notes" in result

    @patch("src.utils.directory_organizer.DirectoryOrganizer")
    def test_promote_fleeting_notes_batch_preview_mode(self, mock_organizer, vault_with_config):
        """Test batch promotion in preview mode."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        note = fleeting_dir / "note.md"
        note.write_text("---\ntype: fleeting\n---\nContent")

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(
                return_value={"quality_score": 0.8, "ai_tags": [], "metadata": {}}
            ),
        )

        result = coordinator.promote_fleeting_notes_batch(
            quality_threshold=0.7, preview_mode=True
        )

        assert result["preview"] is True
        assert note.exists()  # Note should still exist
        # No actual promotions should occur
        mock_organizer.assert_not_called()


class TestFleetingNoteCoordinatorIntegration:
    """Test integration with WorkflowManager."""

    def test_coordinator_provides_all_fleeting_note_methods(self, vault_with_config):
        """Test coordinator provides all required fleeting note methods."""
        vault = vault_with_config["vault"]

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=Mock(),
        )

        # Verify all required methods exist
        assert hasattr(coordinator, "find_fleeting_notes")
        assert hasattr(coordinator, "generate_triage_report")
        assert hasattr(coordinator, "promote_fleeting_note")
        assert hasattr(coordinator, "promote_fleeting_notes_batch")

        # Verify methods are callable
        assert callable(coordinator.find_fleeting_notes)
        assert callable(coordinator.generate_triage_report)
        assert callable(coordinator.promote_fleeting_note)
        assert callable(coordinator.promote_fleeting_notes_batch)

    def test_coordinator_uses_process_callback_for_quality_assessment(self, vault_with_config):
        """Test coordinator uses process_callback for note quality assessment."""
        vault = vault_with_config["vault"]
        fleeting_dir = vault_with_config["fleeting_dir"]

        note = fleeting_dir / "test.md"
        note.write_text("---\ntype: fleeting\n---\nContent")

        mock_callback = Mock(
            return_value={"quality_score": 0.75, "ai_tags": [], "metadata": {}}
        )

        coordinator = FleetingNoteCoordinator(
            base_dir=vault,
            workflow_manager=Mock(),
            process_callback=mock_callback,
        )

        coordinator.generate_triage_report()

        # Verify callback was called for quality assessment
        assert mock_callback.called
        assert mock_callback.call_count >= 1


class TestVaultConfigIntegration:
    """Test FleetingNoteCoordinator integration with vault configuration."""

    def test_coordinator_uses_vault_config_for_directories(self, tmp_path):
        """
        RED PHASE: Verify coordinator uses vault config for directory paths.
        
        This test validates that FleetingNoteCoordinator uses centralized vault
        configuration instead of hardcoded paths. Expected to FAIL until GREEN
        phase replaces hardcoded directory initialization with config properties.
        
        Part of GitHub Issue #45 Phase 2 Priority 3 (P0-VAULT-6).
        """
        from src.config.vault_config_loader import get_vault_config
        
        # Get vault config (creates knowledge/ subdirectory structure)
        config = get_vault_config(str(tmp_path))
        
        # Mock workflow_manager (required for process_callback)
        workflow_manager = Mock()
        
        # Create coordinator with root path (config adds knowledge/)
        coordinator = FleetingNoteCoordinator(
            base_dir=tmp_path,
            workflow_manager=workflow_manager
        )
        
        # Should use knowledge/Fleeting Notes, knowledge/Inbox, etc. from config
        assert "knowledge" in str(coordinator.fleeting_dir), \
            f"Expected fleeting_dir to use knowledge/ subdirectory, got: {coordinator.fleeting_dir}"
        assert coordinator.fleeting_dir == config.fleeting_dir, \
            f"Expected fleeting_dir to match config, got: {coordinator.fleeting_dir} vs {config.fleeting_dir}"
        assert coordinator.inbox_dir == config.inbox_dir, \
            f"Expected inbox_dir to match config, got: {coordinator.inbox_dir} vs {config.inbox_dir}"
        assert coordinator.permanent_dir == config.permanent_dir, \
            "Expected permanent_dir to match config"
        assert coordinator.literature_dir == config.literature_dir, \
            "Expected literature_dir to match config"
