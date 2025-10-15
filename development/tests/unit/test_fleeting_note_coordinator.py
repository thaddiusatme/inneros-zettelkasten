"""
Tests for FleetingNoteCoordinator (ADR-002 Phase 12b)

RED Phase: Comprehensive failing tests for fleeting note management extraction.
Target: Extract ~250-300 LOC from WorkflowManager (fleeting note triage and promotion).
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Target class (doesn't exist yet - RED phase)
from src.ai.fleeting_note_coordinator import FleetingNoteCoordinator


class TestFleetingNoteCoordinatorInitialization:
    """Test FleetingNoteCoordinator initialization and dependency management."""
    
    def test_initialization_with_required_dependencies(self, tmp_path):
        """Test coordinator initialization with all required dependencies."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        (vault_path / "Fleeting Notes").mkdir()
        (vault_path / "Inbox").mkdir()
        (vault_path / "Permanent Notes").mkdir()
        
        # Mock process callback
        mock_process_callback = Mock(return_value={'quality_score': 0.8})
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=mock_process_callback
        )
        
        assert coordinator.fleeting_dir == vault_path / "Fleeting Notes"
        assert coordinator.inbox_dir == vault_path / "Inbox"
        assert coordinator.permanent_dir == vault_path / "Permanent Notes"
        assert coordinator.process_callback is mock_process_callback
    
    def test_initialization_validates_directory_paths(self, tmp_path):
        """Test coordinator validates that directory paths exist or can be created."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        # Create coordinator with non-existent directories (should create them)
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        # Directories should exist after initialization
        assert coordinator.fleeting_dir.exists()
        assert coordinator.inbox_dir.exists()
    
    def test_initialization_accepts_quality_threshold_config(self, tmp_path):
        """Test coordinator accepts quality threshold configuration."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock(),
            default_quality_threshold=0.75
        )
        
        assert coordinator.default_quality_threshold == 0.75


class TestFleetingNoteDiscovery:
    """Test fleeting note discovery and scanning functionality."""
    
    def test_find_fleeting_notes_in_fleeting_directory(self, tmp_path):
        """Test finding notes in Fleeting Notes directory."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        # Create test fleeting notes
        note1 = fleeting_dir / "fleeting1.md"
        note1.write_text("---\ntype: fleeting\n---\nContent")
        note2 = fleeting_dir / "fleeting2.md"
        note2.write_text("---\ntype: fleeting\n---\nContent")
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        notes = coordinator.find_fleeting_notes()
        
        assert len(notes) == 2
        assert note1 in notes
        assert note2 in notes
    
    def test_find_fleeting_notes_in_inbox_with_fleeting_type(self, tmp_path):
        """Test finding fleeting-type notes in Inbox directory."""
        vault_path = tmp_path / "vault"
        inbox_dir = vault_path / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        # Create inbox notes with fleeting type
        fleeting_in_inbox = inbox_dir / "inbox_fleeting.md"
        fleeting_in_inbox.write_text("---\ntype: fleeting\n---\nContent")
        
        permanent_in_inbox = inbox_dir / "inbox_permanent.md"
        permanent_in_inbox.write_text("---\ntype: permanent\n---\nContent")
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=inbox_dir,
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        notes = coordinator.find_fleeting_notes()
        
        assert len(notes) == 1
        assert fleeting_in_inbox in notes
        assert permanent_in_inbox not in notes
    
    def test_find_fleeting_notes_handles_missing_directories(self, tmp_path):
        """Test finding fleeting notes when directories don't exist."""
        vault_path = tmp_path / "vault"
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        notes = coordinator.find_fleeting_notes()
        
        assert len(notes) == 0
    
    def test_find_fleeting_notes_handles_unparseable_files(self, tmp_path):
        """Test finding fleeting notes skips files that can't be parsed."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        # Create valid and invalid notes
        valid_note = fleeting_dir / "valid.md"
        valid_note.write_text("---\ntype: fleeting\n---\nContent")
        
        invalid_note = fleeting_dir / "invalid.md"
        invalid_note.write_text("Invalid YAML\n---\nBroken")
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        notes = coordinator.find_fleeting_notes()
        
        # Should find at least the valid note (invalid might be skipped)
        assert valid_note in notes


class TestTriageReportGeneration:
    """Test fleeting note triage report generation."""
    
    def test_generate_triage_report_with_quality_distribution(self, tmp_path):
        """Test generating triage report with quality score distribution."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        # Create test notes
        (fleeting_dir / "high_quality.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "medium_quality.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "low_quality.md").write_text("---\ntype: fleeting\n---\nContent")
        
        # Mock process callback with varying quality scores
        def mock_process(note_path, fast=False):
            if "high" in str(note_path):
                return {'quality_score': 0.85, 'ai_tags': ['tag1'], 'metadata': {'created': '2024-01-01'}}
            elif "medium" in str(note_path):
                return {'quality_score': 0.55, 'ai_tags': ['tag2'], 'metadata': {'created': '2024-01-02'}}
            else:
                return {'quality_score': 0.25, 'ai_tags': ['tag3'], 'metadata': {'created': '2024-01-03'}}
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=mock_process
        )
        
        report = coordinator.generate_triage_report()
        
        assert report['total_notes_processed'] == 3
        assert report['quality_distribution']['high'] == 1
        assert report['quality_distribution']['medium'] == 1
        assert report['quality_distribution']['low'] == 1
        assert len(report['recommendations']) == 3
    
    def test_generate_triage_report_filters_by_quality_threshold(self, tmp_path):
        """Test triage report filters recommendations by quality threshold."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        (fleeting_dir / "high.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "low.md").write_text("---\ntype: fleeting\n---\nContent")
        
        def mock_process(note_path, fast=False):
            if "high" in str(note_path):
                return {'quality_score': 0.85, 'ai_tags': [], 'metadata': {}}
            else:
                return {'quality_score': 0.25, 'ai_tags': [], 'metadata': {}}
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=mock_process
        )
        
        report = coordinator.generate_triage_report(quality_threshold=0.7)
        
        assert report['total_notes_processed'] == 2
        assert len(report['recommendations']) == 1  # Only high quality note
        assert report['filtered_count'] == 1
    
    def test_generate_triage_report_handles_empty_directory(self, tmp_path):
        """Test triage report handles empty fleeting notes directory."""
        vault_path = tmp_path / "vault"
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        report = coordinator.generate_triage_report()
        
        assert report['total_notes_processed'] == 0
        assert report['quality_distribution'] == {'high': 0, 'medium': 0, 'low': 0}
        assert len(report['recommendations']) == 0
    
    def test_generate_triage_report_tracks_processing_time(self, tmp_path):
        """Test triage report tracks and reports processing time."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        (fleeting_dir / "note.md").write_text("---\ntype: fleeting\n---\nContent")
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock(return_value={'quality_score': 0.5, 'ai_tags': [], 'metadata': {}})
        )
        
        report = coordinator.generate_triage_report()
        
        assert 'processing_time' in report
        assert isinstance(report['processing_time'], (int, float))
        assert report['processing_time'] >= 0
    
    def test_generate_triage_report_sorts_by_quality_score(self, tmp_path):
        """Test triage report sorts recommendations by quality score (highest first)."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        (fleeting_dir / "low.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "high.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "medium.md").write_text("---\ntype: fleeting\n---\nContent")
        
        def mock_process(note_path, fast=False):
            if "low" in str(note_path):
                return {'quality_score': 0.2, 'ai_tags': [], 'metadata': {}}
            elif "high" in str(note_path):
                return {'quality_score': 0.9, 'ai_tags': [], 'metadata': {}}
            else:
                return {'quality_score': 0.5, 'ai_tags': [], 'metadata': {}}
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=mock_process
        )
        
        report = coordinator.generate_triage_report()
        
        # Recommendations should be sorted by quality score descending
        scores = [rec['quality_score'] for rec in report['recommendations']]
        assert scores == sorted(scores, reverse=True)
        assert scores[0] == 0.9
        assert scores[-1] == 0.2


class TestSingleNotePromotion:
    """Test single fleeting note promotion functionality."""
    
    @patch('src.utils.directory_organizer.DirectoryOrganizer')
    def test_promote_fleeting_note_to_permanent(self, mock_organizer, tmp_path):
        """Test promoting single fleeting note to permanent notes."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        note = fleeting_dir / "test_note.md"
        note.write_text("---\ntype: fleeting\n---\nContent")
        
        # Mock DirectoryOrganizer
        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock(return_value={'quality_score': 0.8, 'ai_tags': [], 'metadata': {}})
        )
        
        result = coordinator.promote_fleeting_note(str(note), target_type='permanent', base_dir=vault_path)
        
        assert result['success'] is True
        assert result['promoted_notes'][0]['target_type'] == 'permanent'
        assert result['backup_created'] is True
        mock_organizer.assert_called_once()
    
    @patch('src.utils.directory_organizer.DirectoryOrganizer')
    def test_promote_fleeting_note_with_preview_mode(self, mock_organizer, tmp_path):
        """Test promoting note in preview mode (no actual changes)."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        note = fleeting_dir / "test_note.md"
        note.write_text("---\ntype: fleeting\n---\nContent")
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        result = coordinator.promote_fleeting_note(str(note), preview_mode=True)
        
        assert result['preview'] is True
        assert note.exists()  # Note should still exist
        # DirectoryOrganizer should not be called in preview mode
        mock_organizer.assert_not_called()
    
    def test_promote_fleeting_note_handles_invalid_path(self, tmp_path):
        """Test promotion handles invalid note paths gracefully."""
        vault_path = tmp_path / "vault"
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        result = coordinator.promote_fleeting_note("/nonexistent/note.md")
        
        assert 'error' in result or result['success'] is False
    
    @patch('src.utils.directory_organizer.DirectoryOrganizer')
    def test_promote_fleeting_note_updates_metadata(self, mock_organizer, tmp_path):
        """Test promotion updates note metadata correctly."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        permanent_dir = vault_path / "Permanent Notes"
        fleeting_dir.mkdir(parents=True)
        permanent_dir.mkdir(parents=True)
        
        note = fleeting_dir / "test_note.md"
        note.write_text("---\ntype: fleeting\ncreated: 2024-01-01\n---\nContent")
        
        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=permanent_dir,
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        result = coordinator.promote_fleeting_note(str(note), target_type='permanent')
        
        # Verify metadata update expectations
        assert result['success'] is True
        assert 'promoted_date' in result or 'metadata_updated' in result


class TestBatchPromotion:
    """Test batch fleeting note promotion functionality."""
    
    @patch('src.utils.directory_organizer.DirectoryOrganizer')
    def test_promote_fleeting_notes_batch_by_quality_threshold(self, mock_organizer, tmp_path):
        """Test batch promotion based on quality threshold."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        (fleeting_dir / "high1.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "high2.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "low.md").write_text("---\ntype: fleeting\n---\nContent")
        
        def mock_process(note_path, fast=False):
            if "high" in str(note_path):
                return {'quality_score': 0.85, 'ai_tags': [], 'metadata': {}}
            else:
                return {'quality_score': 0.35, 'ai_tags': [], 'metadata': {}}
        
        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=mock_process
        )
        
        result = coordinator.promote_fleeting_notes_batch(quality_threshold=0.7)
        
        assert result['total_promoted'] == 2
        assert result['total_skipped'] == 1
    
    @patch('src.utils.directory_organizer.DirectoryOrganizer')
    def test_promote_fleeting_notes_batch_tracks_statistics(self, mock_organizer, tmp_path):
        """Test batch promotion tracks detailed statistics."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        (fleeting_dir / "note1.md").write_text("---\ntype: fleeting\n---\nContent")
        (fleeting_dir / "note2.md").write_text("---\ntype: fleeting\n---\nContent")
        
        mock_org_instance = Mock()
        mock_org_instance.create_backup.return_value = "/backup/path"
        mock_organizer.return_value = mock_org_instance
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock(return_value={'quality_score': 0.8, 'ai_tags': [], 'metadata': {}})
        )
        
        result = coordinator.promote_fleeting_notes_batch(quality_threshold=0.7)
        
        assert 'total_promoted' in result
        assert 'total_skipped' in result
        assert 'processing_time' in result
        assert 'promoted_notes' in result
    
    @patch('src.utils.directory_organizer.DirectoryOrganizer')
    def test_promote_fleeting_notes_batch_preview_mode(self, mock_organizer, tmp_path):
        """Test batch promotion in preview mode."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        note = fleeting_dir / "note.md"
        note.write_text("---\ntype: fleeting\n---\nContent")
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock(return_value={'quality_score': 0.8, 'ai_tags': [], 'metadata': {}})
        )
        
        result = coordinator.promote_fleeting_notes_batch(quality_threshold=0.7, preview_mode=True)
        
        assert result['preview'] is True
        assert note.exists()  # Note should still exist
        # No actual promotions should occur
        mock_organizer.assert_not_called()


class TestFleetingNoteCoordinatorIntegration:
    """Test integration with WorkflowManager."""
    
    def test_coordinator_provides_all_fleeting_note_methods(self, tmp_path):
        """Test coordinator provides all required fleeting note methods."""
        vault_path = tmp_path / "vault"
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=vault_path / "Fleeting Notes",
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=Mock()
        )
        
        # Verify all required methods exist
        assert hasattr(coordinator, 'find_fleeting_notes')
        assert hasattr(coordinator, 'generate_triage_report')
        assert hasattr(coordinator, 'promote_fleeting_note')
        assert hasattr(coordinator, 'promote_fleeting_notes_batch')
        
        # Verify methods are callable
        assert callable(coordinator.find_fleeting_notes)
        assert callable(coordinator.generate_triage_report)
        assert callable(coordinator.promote_fleeting_note)
        assert callable(coordinator.promote_fleeting_notes_batch)
    
    def test_coordinator_uses_process_callback_for_quality_assessment(self, tmp_path):
        """Test coordinator uses process_callback for note quality assessment."""
        vault_path = tmp_path / "vault"
        fleeting_dir = vault_path / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        note = fleeting_dir / "test.md"
        note.write_text("---\ntype: fleeting\n---\nContent")
        
        mock_callback = Mock(return_value={'quality_score': 0.75, 'ai_tags': [], 'metadata': {}})
        
        coordinator = FleetingNoteCoordinator(
            fleeting_dir=fleeting_dir,
            inbox_dir=vault_path / "Inbox",
            permanent_dir=vault_path / "Permanent Notes",
            literature_dir=vault_path / "Literature Notes",
            process_callback=mock_callback
        )
        
        coordinator.generate_triage_report()
        
        # Verify callback was called for quality assessment
        assert mock_callback.called
        assert mock_callback.call_count >= 1
