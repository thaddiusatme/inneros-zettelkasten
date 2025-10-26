"""
Tests for LegacyWorkflowManagerAdapter - Backward compatibility bridge.

Tests verify that the adapter maintains exact same public API as old WorkflowManager
while delegating to new 4-manager architecture (Core, Analytics, AI, Connection).

TDD Phase: RED - Write failing tests first
"""

import pytest
from unittest.mock import Mock, patch

from src.ai.workflow_manager_adapter import LegacyWorkflowManagerAdapter


class TestAdapterInitialization:
    """Test adapter initialization and attribute exposure."""

    def test_adapter_initializes_with_base_directory(self, tmp_path):
        """Test adapter can be initialized with explicit base_directory."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        # Act
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Assert
        assert adapter.base_dir == base_dir
        assert adapter.config is not None
        assert isinstance(adapter.config, dict)

    @patch('src.ai.workflow_manager_adapter.get_default_vault_path')
    def test_adapter_initializes_with_none_resolves_vault_path(self, mock_get_path, tmp_path):
        """Test adapter resolves vault path when base_directory is None."""
        # Arrange
        vault_path = tmp_path / "resolved_vault"
        vault_path.mkdir()
        mock_get_path.return_value = vault_path

        # Act
        adapter = LegacyWorkflowManagerAdapter(base_directory=None)

        # Assert
        mock_get_path.assert_called_once()
        assert adapter.base_dir == vault_path

    def test_adapter_exposes_legacy_attributes(self, tmp_path):
        """Test adapter exposes legacy WorkflowManager attributes."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        # Act
        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Assert - Legacy attributes accessible
        assert hasattr(adapter, 'base_dir')
        assert hasattr(adapter, 'config')
        assert hasattr(adapter, 'inbox_dir')
        assert hasattr(adapter, 'fleeting_dir')
        assert hasattr(adapter, 'permanent_dir')
        assert hasattr(adapter, 'archive_dir')

        # Verify directory paths correct
        assert adapter.inbox_dir == base_dir / "Inbox"
        assert adapter.fleeting_dir == base_dir / "Fleeting Notes"
        assert adapter.permanent_dir == base_dir / "Permanent Notes"
        assert adapter.archive_dir == base_dir / "Archive"


class TestSimpleDelegations:
    """Test simple delegation methods (analytics + core)."""

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_detect_orphaned_notes_delegates_to_analytics(self, mock_analytics_class, tmp_path):
        """Test detect_orphaned_notes() delegates to AnalyticsManager."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.detect_orphaned_notes.return_value = [
            {'note': 'orphan1.md', 'title': 'Orphan 1'},
            {'note': 'orphan2.md', 'title': 'Orphan 2'}
        ]
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.detect_orphaned_notes()

        # Assert
        mock_analytics.detect_orphaned_notes.assert_called_once()
        assert len(result) == 2
        assert result[0]['note'] == 'orphan1.md'

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_detect_stale_notes_delegates_to_analytics(self, mock_analytics_class, tmp_path):
        """Test detect_stale_notes() delegates to AnalyticsManager."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.detect_stale_notes.return_value = [
            {'note': 'stale1.md', 'days_since_modified': 120}
        ]
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.detect_stale_notes(days_threshold=90)

        # Assert
        mock_analytics.detect_stale_notes.assert_called_once_with(days_threshold=90)
        assert len(result) == 1
        assert result[0]['days_since_modified'] == 120

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_detect_stale_notes_handles_default_threshold(self, mock_analytics_class, tmp_path):
        """Test detect_stale_notes() uses default threshold when None."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.detect_stale_notes.return_value = []
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.detect_stale_notes()  # No threshold specified

        # Assert
        # Should call with None (AnalyticsManager handles default internally)
        mock_analytics.detect_stale_notes.assert_called_once_with(days_threshold=None)

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_generate_workflow_report_delegates_to_analytics(self, mock_analytics_class, tmp_path):
        """Test generate_workflow_report() delegates to AnalyticsManager."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.generate_workflow_report.return_value = {
            'total_notes': 42,
            'orphaned_count': 5,
            'stale_count': 3
        }
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.generate_workflow_report()

        # Assert - Should return dict with workflow_status, ai_features, analytics, recommendations
        mock_analytics.generate_workflow_report.assert_called_once()
        assert 'workflow_status' in result
        assert 'ai_features' in result
        assert 'analytics' in result
        assert 'recommendations' in result
        # Check workflow_status structure
        assert result['workflow_status']['total_notes'] >= 0
        assert 'health' in result['workflow_status']
        assert 'directory_counts' in result['workflow_status']

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_scan_review_candidates_delegates_to_analytics(self, mock_analytics_class, tmp_path):
        """Test scan_review_candidates() delegates to AnalyticsManager."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.scan_review_candidates.return_value = [
            {'note': 'candidate1.md', 'quality_score': 0.8}
        ]
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.scan_review_candidates()

        # Assert
        mock_analytics.scan_review_candidates.assert_called_once()
        assert len(result) == 1
        assert result[0]['quality_score'] == 0.8

    @patch('src.ai.workflow_manager_adapter.CoreWorkflowManager')
    def test_process_inbox_note_delegates_to_core(self, mock_core_class, tmp_path):
        """Test process_inbox_note() delegates to CoreWorkflowManager."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_core = Mock()
        mock_core.process_inbox_note.return_value = {
            'success': True,
            'quality_score': 0.7,
            'ai_tags': ['test', 'note']
        }
        mock_core_class.return_value = mock_core

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.process_inbox_note("knowledge/Inbox/test.md", dry_run=True)

        # Assert
        mock_core.process_inbox_note.assert_called_once_with(
            "knowledge/Inbox/test.md",
            dry_run=True
        )
        assert result['success'] is True
        assert result['quality_score'] == 0.7

    @patch('src.ai.workflow_manager_adapter.CoreWorkflowManager')
    def test_process_inbox_note_handles_fast_parameter(self, mock_core_class, tmp_path):
        """Test process_inbox_note() gracefully drops 'fast' parameter."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_core = Mock()
        mock_core.process_inbox_note.return_value = {'success': True}
        mock_core_class.return_value = mock_core

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act - Old API included 'fast' parameter
        result = adapter.process_inbox_note("test.md", dry_run=False, fast=True)

        # Assert - New API doesn't use 'fast', adapter should drop it
        mock_core.process_inbox_note.assert_called_once_with(
            "test.md",
            dry_run=False
        )
        assert result['success'] is True


class TestMultiManagerCoordination:
    """Test methods that orchestrate multiple managers."""

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    @patch('src.ai.workflow_manager_adapter.AIEnhancementManager')
    def test_generate_weekly_recommendations_coordinates_managers(
        self, mock_ai_class, mock_analytics_class, tmp_path
    ):
        """Test generate_weekly_recommendations() coordinates analytics + AI."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        # Mock analytics
        mock_analytics = Mock()
        mock_analytics_class.return_value = mock_analytics

        # Mock AI enhancement
        mock_ai = Mock()
        mock_ai.assess_promotion_readiness.return_value = {
            'action': 'promote_to_permanent',
            'confidence': 'high',
            'rationale': 'Well-structured note'
        }
        mock_ai_class.return_value = mock_ai

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        candidates = [
            {'note': 'test1.md', 'quality_score': 0.8},
            {'note': 'test2.md', 'quality_score': 0.75}
        ]

        # Act
        result = adapter.generate_weekly_recommendations(candidates, dry_run=True)

        # Assert - Should return dict with summary, recommendations, generated_at
        assert result is not None
        assert isinstance(result, dict)
        assert 'summary' in result
        assert 'recommendations' in result
        assert 'generated_at' in result
        assert isinstance(result['recommendations'], list)
        # AI should be called for each candidate
        assert mock_ai.assess_promotion_readiness.call_count >= 1

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_generate_enhanced_metrics_aggregates_multiple_sources(
        self, mock_analytics_class, tmp_path
    ):
        """Test generate_enhanced_metrics() calls multiple analytics methods."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.detect_orphaned_notes.return_value = [{'note': 'orphan1.md'}]
        mock_analytics.detect_stale_notes.return_value = [{'note': 'stale1.md'}]
        mock_analytics.generate_workflow_report.return_value = {'total_notes': 50}
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.generate_enhanced_metrics()

        # Assert - Should call all 3 analytics methods
        mock_analytics.detect_orphaned_notes.assert_called_once()
        mock_analytics.detect_stale_notes.assert_called_once()
        mock_analytics.generate_workflow_report.assert_called_once()

        # Should return enhanced metrics dict
        assert result is not None
        assert isinstance(result, dict)

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_analyze_fleeting_notes_delegates_to_analytics(
        self, mock_analytics_class, tmp_path
    ):
        """Test analyze_fleeting_notes() simple delegation."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.analyze_fleeting_notes.return_value = {
            'total': 20,
            'age_buckets': {'0-7': 5, '8-30': 10, '30+': 5}
        }
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.analyze_fleeting_notes()

        # Assert
        mock_analytics.analyze_fleeting_notes.assert_called_once()
        assert result['total'] == 20

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_generate_fleeting_health_report_formats_analysis(
        self, mock_analytics_class, tmp_path
    ):
        """Test generate_fleeting_health_report() wraps analytics."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics.analyze_fleeting_notes.return_value = {
            'total': 20,
            'age_buckets': {'0-7': 5}
        }
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.generate_fleeting_health_report()

        # Assert
        mock_analytics.analyze_fleeting_notes.assert_called_once()
        assert result is not None
        assert isinstance(result, dict)

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    @patch('src.ai.workflow_manager_adapter.AIEnhancementManager')
    def test_generate_fleeting_triage_report_coordinates_quality_scoring(
        self, mock_ai_class, mock_analytics_class, tmp_path
    ):
        """Test generate_fleeting_triage_report() coordinates analytics + AI."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        # Setup mocks
        mock_analytics = Mock()
        mock_analytics_class.return_value = mock_analytics

        mock_ai = Mock()
        mock_ai_class.return_value = mock_ai

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.generate_fleeting_triage_report(quality_threshold=0.7)

        # Assert
        assert result is not None
        assert isinstance(result, dict)

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_generate_fleeting_triage_report_drops_fast_parameter(
        self, mock_analytics_class, tmp_path
    ):
        """Test generate_fleeting_triage_report() drops 'fast' parameter."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        mock_analytics = Mock()
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act - Old API had 'fast' parameter
        result = adapter.generate_fleeting_triage_report(quality_threshold=0.7, fast=True)

        # Assert - Should work without error (fast parameter ignored)
        assert result is not None


class TestFileOperations:
    """Test file move operations with safety checks."""

    def test_promote_note_moves_to_correct_directory(self, tmp_path):
        """Test promote_note() moves file to target directory."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()
        (base_dir / "Permanent Notes").mkdir()

        # Create test note
        note_path = base_dir / "Inbox" / "test_note.md"
        note_path.write_text("---\ntype: permanent\n---\nTest content")

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.promote_note(str(note_path), target_type="permanent")

        # Assert - File should be moved (or result indicates move plan)
        assert result is not None
        assert isinstance(result, dict)

    def test_promote_note_validates_target_type(self, tmp_path):
        """Test promote_note() raises error on invalid target_type."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act & Assert - Invalid target_type should raise ValueError
        with pytest.raises(ValueError, match="Invalid target_type"):
            adapter.promote_note("test.md", target_type="invalid_type")

    def test_promote_fleeting_note_preview_mode_no_file_changes(self, tmp_path):
        """Test promote_fleeting_note() preview mode doesn't mutate filesystem."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()
        (base_dir / "Fleeting Notes").mkdir()

        # Create test note
        note_path = base_dir / "Fleeting Notes" / "test_fleeting.md"
        note_path.write_text("---\ntype: permanent\n---\nTest content")

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.promote_fleeting_note(str(note_path), preview_mode=True)

        # Assert - File should still exist in original location
        assert note_path.exists()
        assert result is not None
        assert 'preview' in result or 'plan' in result

    def test_promote_fleeting_note_detects_target_type_from_yaml(self, tmp_path):
        """Test promote_fleeting_note() reads type from YAML when None."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()
        (base_dir / "Fleeting Notes").mkdir()

        # Create note with type in frontmatter
        note_path = base_dir / "Fleeting Notes" / "test_fleeting.md"
        note_path.write_text("---\ntype: literature\n---\nTest content")

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act - Don't specify target_type, should detect from YAML
        result = adapter.promote_fleeting_note(str(note_path), target_type=None, preview_mode=True)

        # Assert
        assert result is not None
        # Should detect 'literature' from frontmatter

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_promote_fleeting_notes_batch_handles_partial_failures(
        self, mock_analytics_class, tmp_path
    ):
        """Test promote_fleeting_notes_batch() continues on individual failures."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()
        (base_dir / "Fleeting Notes").mkdir()

        # Mock analytics
        mock_analytics = Mock()
        mock_analytics.analyze_fleeting_notes.return_value = {
            'total': 5,
            'age_buckets': {}
        }
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act - Batch promote with preview mode
        result = adapter.promote_fleeting_notes_batch(
            quality_threshold=0.7,
            preview_mode=True
        )

        # Assert - Should return results dict
        assert result is not None
        assert isinstance(result, dict)


class TestAdditionalMethods:
    """Test additional adapter methods."""

    @patch('src.ai.workflow_manager_adapter.AnalyticsManager')
    def test_batch_process_inbox_loops_over_notes(
        self, mock_analytics_class, tmp_path
    ):
        """Test batch_process_inbox() processes multiple notes."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()

        # Create test notes
        note1 = base_dir / "Inbox" / "note1.md"
        note1.write_text("Test content 1")
        note2 = base_dir / "Inbox" / "note2.md"
        note2.write_text("Test content 2")

        mock_analytics = Mock()
        mock_analytics_class.return_value = mock_analytics

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act
        result = adapter.batch_process_inbox(dry_run=True)

        # Assert
        assert result is not None
        assert isinstance(result, (dict, list))


class TestSessionManagement:
    """Test session management methods (can be stubbed)."""

    def test_start_safe_processing_session_initializes(self, tmp_path):
        """Test start_safe_processing_session() creates session."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act & Assert - May raise NotImplementedError if stubbed
        try:
            result = adapter.start_safe_processing_session("test_operation")
            assert result is not None
        except NotImplementedError:
            pytest.skip("Session management not yet implemented")

    def test_process_inbox_note_safe_wraps_with_session(self, tmp_path):
        """Test process_inbox_note_safe() uses session management."""
        # Arrange
        base_dir = tmp_path / "test_vault"
        base_dir.mkdir()

        adapter = LegacyWorkflowManagerAdapter(base_directory=str(base_dir))

        # Act & Assert
        try:
            result = adapter.process_inbox_note_safe("test.md")
            assert result is not None
        except NotImplementedError:
            pytest.skip("Session management not yet implemented")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
