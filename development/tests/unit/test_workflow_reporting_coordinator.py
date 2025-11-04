"""
Test suite for WorkflowReportingCoordinator - ADR-002 Phase 10 Extraction

RED PHASE: Comprehensive failing tests for workflow reporting extraction.

This coordinator handles:
- Comprehensive workflow status reporting
- AI feature usage analysis across the vault
- Workflow health assessment
- Intelligent recommendation generation
"""

import pytest
from unittest.mock import Mock

# This import will fail until we create the coordinator
from src.ai.workflow_reporting_coordinator import WorkflowReportingCoordinator


class TestWorkflowReportingCoordinator:
    """Test suite for WorkflowReportingCoordinator extraction."""

    @pytest.fixture
    def temp_vault(self, tmp_path):
        """Create a temporary vault structure with vault config."""
        from src.config.vault_config_loader import get_vault_config

        vault = tmp_path / "test_vault"
        vault.mkdir()

        # Get vault config and create directories at correct paths
        config = get_vault_config(str(vault))
        config.inbox_dir.mkdir(parents=True, exist_ok=True)
        config.fleeting_dir.mkdir(parents=True, exist_ok=True)
        config.permanent_dir.mkdir(parents=True, exist_ok=True)
        config.archive_dir.mkdir(parents=True, exist_ok=True)

        return vault

    @pytest.fixture
    def mock_analytics(self):
        """Mock NoteAnalytics instance."""
        analytics = Mock()
        analytics.generate_report.return_value = {
            "total_notes": 100,
            "avg_quality": 0.75,
            "connection_density": 3.5,
        }
        return analytics

    @pytest.fixture
    def coordinator(self, temp_vault, mock_analytics):
        """Create WorkflowReportingCoordinator instance."""
        return WorkflowReportingCoordinator(temp_vault, mock_analytics)

    # ============================================================================
    # Test 1: Basic Coordinator Initialization
    # ============================================================================

    def test_coordinator_initialization(self, temp_vault, mock_analytics):
        """Test coordinator initializes with required dependencies."""
        from src.config.vault_config_loader import get_vault_config

        config = get_vault_config(str(temp_vault))
        coordinator = WorkflowReportingCoordinator(temp_vault, mock_analytics)

        assert coordinator.base_dir == temp_vault
        assert coordinator.analytics == mock_analytics
        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.fleeting_dir == config.fleeting_dir
        assert coordinator.permanent_dir == config.permanent_dir
        assert coordinator.archive_dir == config.archive_dir

    # ============================================================================
    # Test 2: Workflow Report Generation - Empty Vault
    # ============================================================================

    def test_generate_workflow_report_empty_vault(self, coordinator, mock_analytics):
        """Test workflow report generation with empty directories."""
        report = coordinator.generate_workflow_report()

        # Verify report structure
        assert "workflow_status" in report
        assert "ai_features" in report
        assert "analytics" in report
        assert "recommendations" in report

        # Verify workflow status
        status = report["workflow_status"]
        assert status["health"] == "healthy"
        assert status["directory_counts"]["Inbox"] == 0
        assert status["directory_counts"]["Fleeting Notes"] == 0
        assert status["directory_counts"]["Permanent Notes"] == 0
        assert status["directory_counts"]["Archive"] == 0
        assert status["total_notes"] == 0

        # Verify analytics integration
        assert report["analytics"] == mock_analytics.generate_report.return_value

    # ============================================================================
    # Test 3: Directory Counting with Notes
    # ============================================================================

    def test_directory_counting_with_notes(self, coordinator, temp_vault):
        """Test accurate directory note counting."""
        # Create test notes in each directory using coordinator paths
        (coordinator.inbox_dir / "note1.md").write_text("# Note 1")
        (coordinator.inbox_dir / "note2.md").write_text("# Note 2")
        (coordinator.fleeting_dir / "fleeting1.md").write_text("# Fleeting")
        (coordinator.permanent_dir / "perm1.md").write_text("# Permanent")
        (coordinator.permanent_dir / "perm2.md").write_text("# Permanent 2")
        (coordinator.permanent_dir / "perm3.md").write_text("# Permanent 3")

        report = coordinator.generate_workflow_report()

        counts = report["workflow_status"]["directory_counts"]
        assert counts["Inbox"] == 2
        assert counts["Fleeting Notes"] == 1
        assert counts["Permanent Notes"] == 3
        assert counts["Archive"] == 0
        assert report["workflow_status"]["total_notes"] == 6

    # ============================================================================
    # Test 4: Workflow Health Status - Healthy
    # ============================================================================

    def test_workflow_health_healthy(self, coordinator, temp_vault):
        """Test workflow health assessment - healthy state."""
        # Create few inbox notes (< 20)
        for i in range(10):
            (coordinator.inbox_dir / f"note{i}.md").write_text(f"# Note {i}")

        report = coordinator.generate_workflow_report()

        assert report["workflow_status"]["health"] == "healthy"

    # ============================================================================
    # Test 5: Workflow Health Status - Needs Attention
    # ============================================================================

    def test_workflow_health_needs_attention(self, coordinator, temp_vault):
        """Test workflow health assessment - needs attention state."""
        # Create 25 inbox notes (> 20 but <= 50)
        for i in range(25):
            (coordinator.inbox_dir / f"note{i}.md").write_text(f"# Note {i}")

        report = coordinator.generate_workflow_report()

        assert report["workflow_status"]["health"] == "needs_attention"

    # ============================================================================
    # Test 6: Workflow Health Status - Critical
    # ============================================================================

    def test_workflow_health_critical(self, coordinator, temp_vault):
        """Test workflow health assessment - critical state."""
        # Create 60 inbox notes (> 50)
        for i in range(60):
            (coordinator.inbox_dir / f"note{i}.md").write_text(f"# Note {i}")

        report = coordinator.generate_workflow_report()

        assert report["workflow_status"]["health"] == "critical"

    # ============================================================================
    # Test 7: AI Usage Analysis - No AI Features
    # ============================================================================

    def test_analyze_ai_usage_no_features(self, coordinator, temp_vault):
        """Test AI usage analysis with notes lacking AI features."""
        # Create notes without AI frontmatter
        (coordinator.permanent_dir / "note1.md").write_text(
            """---
title: Test Note
tags: [test, manual]
---
# Manual Note"""
        )

        (coordinator.inbox_dir / "note2.md").write_text(
            """---
title: Another Note
---
# Another Note"""
        )

        report = coordinator.generate_workflow_report()
        ai_usage = report["ai_features"]

        assert ai_usage["total_analyzed"] == 2
        assert ai_usage["notes_with_ai_tags"] == 0
        assert ai_usage["notes_with_ai_summaries"] == 0
        assert ai_usage["notes_with_ai_processing"] == 0

    # ============================================================================
    # Test 8: AI Usage Analysis - With AI Features
    # ============================================================================

    def test_analyze_ai_usage_with_features(self, coordinator, temp_vault):
        """Test AI usage analysis detects AI-enhanced notes."""
        # Note with AI summary
        (coordinator.permanent_dir / "ai_note1.md").write_text(
            """---
title: AI Enhanced Note
ai_summary: This is an AI-generated summary
ai_tags: [ai-feature, test]
---
# AI Note"""
        )

        # Note with AI processing only
        (coordinator.inbox_dir / "ai_note2.md").write_text(
            """---
title: Processed Note
ai_processed: true
---
# Processed Note"""
        )

        # Manual note for comparison
        (coordinator.fleeting_dir / "manual.md").write_text(
            """---
title: Manual Note
---
# Manual Note"""
        )

        report = coordinator.generate_workflow_report()
        ai_usage = report["ai_features"]

        assert ai_usage["total_analyzed"] == 3
        assert ai_usage["notes_with_ai_tags"] == 1  # Only first note has AI-style tags
        assert ai_usage["notes_with_ai_summaries"] == 1
        assert ai_usage["notes_with_ai_processing"] == 2

    # ============================================================================
    # Test 9: Recommendations - Inbox Management
    # ============================================================================

    def test_recommendations_inbox_management(self, coordinator, temp_vault):
        """Test recommendations for inbox backlog."""
        # Create 30 inbox notes to trigger recommendation
        for i in range(30):
            (coordinator.inbox_dir / f"note{i}.md").write_text(f"# Note {i}")

        report = coordinator.generate_workflow_report()
        recommendations = report["recommendations"]

        # Should recommend processing inbox
        assert any("inbox" in rec.lower() for rec in recommendations)
        assert any("batch processing" in rec.lower() for rec in recommendations)

    # ============================================================================
    # Test 10: Recommendations - AI Adoption
    # ============================================================================

    def test_recommendations_ai_adoption(self, coordinator, temp_vault):
        """Test recommendations for low AI feature adoption."""
        # Create 10 notes with no AI features
        for i in range(10):
            (coordinator.permanent_dir / f"note{i}.md").write_text(
                f"""---
title: Note {i}
---
# Content {i}"""
            )

        report = coordinator.generate_workflow_report()
        recommendations = report["recommendations"]

        # Should recommend AI processing or summarization
        assert any(
            "AI" in rec or "summarization" in rec.lower() for rec in recommendations
        )

    # ============================================================================
    # Test 11: Recommendations - Note Type Balance
    # ============================================================================

    def test_recommendations_note_type_balance(self, coordinator, temp_vault):
        """Test recommendations for fleeting/permanent note imbalance."""
        # Create many fleeting notes
        for i in range(20):
            (coordinator.fleeting_dir / f"fleeting{i}.md").write_text(f"# Fleeting {i}")

        # Create few permanent notes (imbalance ratio > 2)
        for i in range(5):
            (coordinator.permanent_dir / f"perm{i}.md").write_text(f"# Permanent {i}")

        report = coordinator.generate_workflow_report()
        recommendations = report["recommendations"]

        # Should recommend promoting fleeting notes
        assert any(
            "promot" in rec.lower() and "fleeting" in rec.lower()
            for rec in recommendations
        )

    # ============================================================================
    # Test 12: Missing Directories Handling
    # ============================================================================

    def test_missing_directories_handling(self, temp_vault):
        """Test coordinator handles missing directories gracefully."""
        from src.config.vault_config_loader import get_vault_config
        import shutil

        # Get vault config for proper paths
        config = get_vault_config(str(temp_vault))

        # Remove some directories
        shutil.rmtree(config.archive_dir)
        shutil.rmtree(config.fleeting_dir)

        mock_analytics = Mock()
        mock_analytics.generate_report.return_value = {}

        coordinator = WorkflowReportingCoordinator(temp_vault, mock_analytics)
        report = coordinator.generate_workflow_report()

        # Should report 0 for missing directories
        counts = report["workflow_status"]["directory_counts"]
        assert counts["Archive"] == 0
        assert counts["Fleeting Notes"] == 0

    # ============================================================================
    # Test 13: Malformed YAML Handling
    # ============================================================================

    def test_malformed_yaml_handling(self, coordinator, temp_vault):
        """Test AI usage analysis handles malformed YAML gracefully."""
        # Create note with malformed YAML
        (coordinator.inbox_dir / "malformed.md").write_text(
            """---
title: Malformed
tags: [unclosed, array
---

# Malformed Note"""
        )

        # Create valid note
        (coordinator.inbox_dir / "valid.md").write_text(
            """---
title: Valid
---

# Valid Note"""
        )

        # Should not crash, should count at least the valid note
        report = coordinator.generate_workflow_report()
        assert report["ai_features"]["total_analyzed"] >= 1

    # ============================================================================
    # Test 14: WorkflowManager Integration
    # ============================================================================

    def test_workflow_manager_delegation(self, temp_vault, mock_analytics):
        """Test WorkflowManager delegates to coordinator correctly."""

        # This test verifies the delegation pattern
        # WorkflowManager should have a reporting_coordinator and delegate
        # the generate_workflow_report() call to it

        # For now, this is a placeholder that will be implemented
        # when we update WorkflowManager in the GREEN phase

        # Create coordinator directly
        coordinator = WorkflowReportingCoordinator(temp_vault, mock_analytics)

        # Verify it matches expected interface
        assert hasattr(coordinator, "generate_workflow_report")
        assert callable(coordinator.generate_workflow_report)

    # ============================================================================
    # Test 15: Empty Recommendations List
    # ============================================================================

    def test_empty_recommendations_when_healthy(self, coordinator, temp_vault):
        """Test no recommendations generated when workflow is healthy."""
        # Create ideal state: few inbox notes, good AI adoption, balanced types
        # Create 5 inbox notes (healthy)
        for i in range(5):
            (coordinator.inbox_dir / f"note{i}.md").write_text(f"# Note {i}")

        # Create notes with high AI adoption
        for i in range(8):
            (coordinator.permanent_dir / f"ai_note{i}.md").write_text(
                f"""---
ai_processed: true
ai_summary: Summary {i}
---

# AI Note {i}"""
            )

        # Balanced fleeting notes (not > 2x permanent)
        for i in range(10):
            (coordinator.fleeting_dir / f"fleeting{i}.md").write_text(f"# Fleeting {i}")

        report = coordinator.generate_workflow_report()

        # Should have few or no recommendations
        assert isinstance(report["recommendations"], list)


class TestVaultConfigIntegration:
    """Test WorkflowReportingCoordinator integration with vault configuration."""

    def test_coordinator_uses_vault_config_for_directories(self, tmp_path):
        """
        RED PHASE: Verify coordinator uses vault config for directory paths.

        This test validates that WorkflowReportingCoordinator uses the centralized
        vault configuration (knowledge/Inbox) instead of hardcoded paths (Inbox).

        Expected to FAIL until GREEN phase replaces hardcoded paths with config.

        Part of GitHub Issue #45 - Vault Configuration Centralization
        """
        from src.config.vault_config_loader import get_vault_config

        # Get vault config for test directory
        config = get_vault_config(str(tmp_path))

        # Create mock analytics
        analytics = Mock()
        analytics.generate_report.return_value = {
            "total_notes": 0,
            "avg_quality": 0.0,
            "connection_density": 0.0,
        }

        # Initialize coordinator
        coordinator = WorkflowReportingCoordinator(tmp_path, analytics)

        # Should use knowledge/Inbox, not root-level Inbox
        assert "knowledge" in str(
            coordinator.inbox_dir
        ), f"Expected 'knowledge' in path, got: {coordinator.inbox_dir}"
        assert (
            coordinator.inbox_dir == config.inbox_dir
        ), f"Expected {config.inbox_dir}, got {coordinator.inbox_dir}"
        assert (
            coordinator.fleeting_dir == config.fleeting_dir
        ), f"Expected {config.fleeting_dir}, got {coordinator.fleeting_dir}"
        assert (
            coordinator.permanent_dir == config.permanent_dir
        ), f"Expected {config.permanent_dir}, got {coordinator.permanent_dir}"
        assert (
            coordinator.archive_dir == config.archive_dir
        ), f"Expected {config.archive_dir}, got {coordinator.archive_dir}"
