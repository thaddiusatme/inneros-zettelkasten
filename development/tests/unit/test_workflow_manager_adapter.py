"""
Tests for LegacyWorkflowManagerAdapter - Backward compatibility bridge.

Tests verify that the adapter maintains exact same public API as old WorkflowManager
while delegating to new 4-manager architecture (Core, Analytics, AI, Connection).

TDD Phase: RED - Write failing tests first
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

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
        
        # Assert
        mock_analytics.generate_workflow_report.assert_called_once()
        assert result['total_notes'] == 42
        assert result['orphaned_count'] == 5
    
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
