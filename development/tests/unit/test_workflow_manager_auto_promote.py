#!/usr/bin/env python3
"""
TDD RED Phase - WorkflowManager Auto-Promotion Delegation

Test Suite: PBI-002 WorkflowManager Auto-Promotion Integration
Feature: WorkflowManager delegates to PromotionEngine.auto_promote_ready_notes()

Following ADR-002 Phase 11 delegation pattern established for:
- promote_note() → promotion_engine.promote_note()
- promote_fleeting_notes_batch() → promotion_engine.promote_fleeting_notes_batch()

This test validates that WorkflowManager properly delegates auto-promotion
to PromotionEngine, maintaining the composition pattern established in ADR-002.

Expected Test Results (RED Phase):
- test_workflow_manager_has_auto_promote_method: FAIL (method doesn't exist)
- test_auto_promote_delegates_to_promotion_engine: FAIL (no delegation)
- test_auto_promote_passes_parameters_correctly: FAIL (no implementation)
- test_auto_promote_dry_run_delegation: FAIL (no dry-run support)
- test_auto_promote_quality_threshold_delegation: FAIL (no threshold support)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.workflow_manager import WorkflowManager
from src.ai.promotion_engine import PromotionEngine


class TestWorkflowManagerAutoPromotionDelegation:
    """
    RED Phase tests for WorkflowManager.auto_promote_ready_notes() delegation.
    
    All tests expected to FAIL until GREEN phase implementation.
    """
    
    def test_workflow_manager_has_auto_promote_method(self, tmp_path):
        """
        RED-1: Verify WorkflowManager has auto_promote_ready_notes method.
        
        Expected: FAIL - AttributeError (method doesn't exist yet)
        
        Success criteria:
        - WorkflowManager instance has auto_promote_ready_notes method
        - Method signature matches PromotionEngine.auto_promote_ready_notes()
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()  # Required by WorkflowManager
        workflow_manager = WorkflowManager(base_dir)
        
        # Act & Assert
        assert hasattr(workflow_manager, 'auto_promote_ready_notes'), \
            "WorkflowManager should have auto_promote_ready_notes method"
        
        # Verify method is callable
        assert callable(workflow_manager.auto_promote_ready_notes), \
            "auto_promote_ready_notes should be a callable method"
    
    def test_auto_promote_delegates_to_promotion_engine(self, tmp_path):
        """
        RED-2: Verify auto_promote_ready_notes delegates to PromotionEngine.
        
        Expected: FAIL - AttributeError (method doesn't exist)
        
        Success criteria:
        - WorkflowManager.auto_promote_ready_notes() calls PromotionEngine.auto_promote_ready_notes()
        - Delegation follows ADR-002 composition pattern
        - Return value is passed through correctly
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()  # Required by WorkflowManager
        workflow_manager = WorkflowManager(base_dir)
        
        # Mock PromotionEngine response
        expected_result = {
            "total_candidates": 5,
            "promoted_count": 3,
            "skipped_count": 2,
            "error_count": 0,
            "promoted": [],
            "skipped_notes": [],
            "errors": [],
            "dry_run": False
        }
        
        # Replace promotion_engine with mock
        workflow_manager.promotion_engine = Mock(spec=PromotionEngine)
        workflow_manager.promotion_engine.auto_promote_ready_notes.return_value = expected_result
        
        # Act
        result = workflow_manager.auto_promote_ready_notes()
        
        # Assert
        workflow_manager.promotion_engine.auto_promote_ready_notes.assert_called_once()
        assert result == expected_result, \
            "WorkflowManager should return PromotionEngine result unchanged"
    
    def test_auto_promote_passes_parameters_correctly(self, tmp_path):
        """
        RED-3: Verify parameters are passed through to PromotionEngine.
        
        Expected: FAIL - AttributeError (method doesn't exist)
        
        Success criteria:
        - dry_run parameter passed correctly
        - quality_threshold parameter passed correctly
        - All optional parameters supported
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()  # Required by WorkflowManager
        workflow_manager = WorkflowManager(base_dir)
        
        # Mock PromotionEngine
        workflow_manager.promotion_engine = Mock(spec=PromotionEngine)
        workflow_manager.promotion_engine.auto_promote_ready_notes.return_value = {
            "dry_run": True,
            "total_candidates": 0
        }
        
        # Act
        workflow_manager.auto_promote_ready_notes(
            dry_run=True,
            quality_threshold=0.8
        )
        
        # Assert
        workflow_manager.promotion_engine.auto_promote_ready_notes.assert_called_once_with(
            dry_run=True,
            quality_threshold=0.8
        )
    
    def test_auto_promote_dry_run_delegation(self, tmp_path):
        """
        RED-4: Verify dry-run mode delegation works correctly.
        
        Expected: FAIL - AttributeError (method doesn't exist)
        
        Success criteria:
        - dry_run=True parameter passed to PromotionEngine
        - No actual file modifications occur
        - Preview results returned correctly
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        # Create test note
        test_note = inbox_dir / "test.md"
        test_note.write_text("""---
type: permanent
status: inbox
quality_score: 0.85
---

# Test Note
""")
        
        workflow_manager = WorkflowManager(base_dir)
        
        # Act
        result = workflow_manager.auto_promote_ready_notes(dry_run=True)
        
        # Assert
        assert result["dry_run"] is True, "Result should indicate dry-run mode"
        assert test_note.exists(), "Note should not be moved in dry-run mode"
        assert "would_promote_count" in result, "Should include preview count"
    
    def test_auto_promote_quality_threshold_delegation(self, tmp_path):
        """
        RED-5: Verify custom quality threshold delegation.
        
        Expected: FAIL - AttributeError (method doesn't exist)
        
        Success criteria:
        - quality_threshold parameter accepted (default: 0.7)
        - Custom threshold (e.g., 0.8) passed to PromotionEngine
        - Only notes above threshold are promoted
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        # Create notes with different quality scores
        high_quality = inbox_dir / "high.md"
        high_quality.write_text("""---
type: permanent
status: inbox
quality_score: 0.85
---
# High
""")
        
        medium_quality = inbox_dir / "medium.md"
        medium_quality.write_text("""---
type: permanent
status: inbox
quality_score: 0.75
---
# Medium
""")
        
        workflow_manager = WorkflowManager(base_dir)
        
        # Act - Use higher threshold
        result = workflow_manager.auto_promote_ready_notes(quality_threshold=0.8)
        
        # Assert
        # Should only promote note with quality >= 0.8
        assert result["promoted_count"] == 1, \
            "Should only promote notes meeting custom threshold (0.8)"


class TestAutoPromoteIntegrationPattern:
    """
    RED Phase tests verifying ADR-002 composition pattern consistency.
    
    Validates that auto_promote follows the same delegation pattern as
    existing promotion methods in WorkflowManager.
    """
    
    def test_auto_promote_follows_adr002_delegation_pattern(self, tmp_path):
        """
        RED-6: Verify auto_promote follows ADR-002 Phase 11 pattern.
        
        Expected: FAIL - AttributeError (method doesn't exist)
        
        Success criteria:
        - Delegation method in WorkflowManager
        - Calls self.promotion_engine.auto_promote_ready_notes()
        - Returns result unchanged (simple passthrough)
        - Matches pattern of promote_note() and promote_fleeting_notes_batch()
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()  # Required by WorkflowManager
        workflow_manager = WorkflowManager(base_dir)
        
        # Verify PromotionEngine is initialized
        assert hasattr(workflow_manager, 'promotion_engine'), \
            "WorkflowManager should have promotion_engine attribute (ADR-002 Phase 4)"
        assert isinstance(workflow_manager.promotion_engine, PromotionEngine), \
            "promotion_engine should be PromotionEngine instance"
        
        # Mock PromotionEngine method
        mock_result = {"promoted_count": 5}
        workflow_manager.promotion_engine.auto_promote_ready_notes = Mock(return_value=mock_result)
        
        # Act
        result = workflow_manager.auto_promote_ready_notes(dry_run=False, quality_threshold=0.7)
        
        # Assert - Follows ADR-002 delegation pattern
        workflow_manager.promotion_engine.auto_promote_ready_notes.assert_called_once_with(
            dry_run=False,
            quality_threshold=0.7
        )
        assert result == mock_result, \
            "Should return PromotionEngine result unchanged (simple delegation)"
    
    def test_auto_promote_consistency_with_existing_delegations(self, tmp_path):
        """
        RED-7: Verify consistency with promote_note() and promote_fleeting_notes_batch().
        
        Expected: FAIL - AttributeError (method doesn't exist)
        
        Success criteria:
        - Same delegation pattern as existing methods
        - Simple passthrough (no business logic in WorkflowManager)
        - Returns PromotionEngine result directly
        """
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        (base_dir / "Inbox").mkdir()  # Required by WorkflowManager
        workflow_manager = WorkflowManager(base_dir)
        
        # Verify existing delegation methods exist (ADR-002 Phase 11)
        assert hasattr(workflow_manager, 'promote_note'), \
            "promote_note delegation should exist"
        assert hasattr(workflow_manager, 'promote_fleeting_notes_batch'), \
            "promote_fleeting_notes_batch delegation should exist"
        
        # Verify auto_promote follows same pattern
        assert hasattr(workflow_manager, 'auto_promote_ready_notes'), \
            "auto_promote_ready_notes should follow same delegation pattern"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
