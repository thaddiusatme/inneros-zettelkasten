"""
Tests for AnalyticsCoordinator extraction from WorkflowManager.

This test suite follows the TDD RED phase for ADR-002 Phase 3:
Extract analytics and metrics logic into a dedicated coordinator.

Target methods to extract:
- detect_orphaned_notes()
- detect_orphaned_notes_comprehensive()
- detect_stale_notes(days_threshold)
- generate_enhanced_metrics()
- _build_link_graph()
- _calculate_link_density()
- _calculate_note_age_distribution()
- _calculate_productivity_metrics()
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import os
from unittest.mock import Mock

from src.ai.analytics_coordinator import AnalyticsCoordinator
from src.config.vault_config_loader import get_vault_config


@pytest.fixture
def vault_with_config(tmp_path):
    """
    Fixture providing vault structure with vault configuration.
    
    Creates knowledge/ subdirectory structure as per vault_config.yaml.
    Used for vault config integration tests (GitHub Issue #45 Phase 2 Priority 3).
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


class TestAnalyticsCoordinatorVaultConfigIntegration:
    """
    Test AnalyticsCoordinator uses vault configuration for directory paths.
    
    RED Phase: This test will fail because current AnalyticsCoordinator constructor
    does not accept workflow_manager parameter (GitHub Issue #45 Phase 2 Priority 3).
    """

    def test_analytics_coordinator_uses_vault_config_for_directories(self, vault_with_config):
        """
        Test that AnalyticsCoordinator loads directory paths from vault config.
        
        Expected RED failure: TypeError about unexpected keyword argument 'workflow_manager'
        because current constructor signature is: __init__(self, base_dir: Path)
        
        Target GREEN signature: __init__(self, base_dir: Path, workflow_manager)
        """
        vault = vault_with_config["vault"]
        config = vault_with_config["config"]
        
        # Create coordinator with vault config pattern (will fail in RED phase)
        coordinator = AnalyticsCoordinator(
            base_dir=vault,
            workflow_manager=Mock()
        )
        
        # Verify coordinator uses vault config paths
        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.fleeting_dir == config.fleeting_dir
        assert coordinator.permanent_dir == config.permanent_dir


class TestAnalyticsCoordinatorCore:
    """Test core analytics functionality."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create directories
            (vault_path / "Inbox").mkdir()
            (vault_path / "Fleeting Notes").mkdir()
            (vault_path / "Permanent Notes").mkdir()

            # Create sample notes with links
            (vault_path / "Permanent Notes" / "note1.md").write_text(
                "# Note 1\n\nThis links to [[note2]] and [[note3]]."
            )
            (vault_path / "Permanent Notes" / "note2.md").write_text(
                "# Note 2\n\nThis links to [[note1]]."
            )
            (vault_path / "Permanent Notes" / "note3.md").write_text(
                "# Note 3\n\nThis has no links."
            )
            (vault_path / "Permanent Notes" / "orphan.md").write_text(
                "# Orphan Note\n\nThis note has no links and is not linked to."
            )

            # Create stale note (modify timestamp)
            stale_note = vault_path / "Permanent Notes" / "stale.md"
            stale_note.write_text("# Stale Note")
            # Set modification time to 100 days ago
            old_time = (datetime.now() - timedelta(days=100)).timestamp()
            os.utime(stale_note, (old_time, old_time))

            yield vault_path

    @pytest.fixture
    def coordinator(self, temp_vault):
        """Create AnalyticsCoordinator instance."""
        return AnalyticsCoordinator(temp_vault)

    def test_coordinator_initialization(self, coordinator):
        """Test AnalyticsCoordinator initializes with vault path."""
        assert coordinator is not None
        assert coordinator.base_dir is not None

    def test_detect_orphaned_notes_finds_isolated_notes(self, coordinator):
        """Test that detect_orphaned_notes identifies notes with no links."""
        orphaned = coordinator.detect_orphaned_notes()

        assert isinstance(orphaned, list)
        assert len(orphaned) > 0

        # Check that orphan.md is detected
        orphan_paths = [note["path"] for note in orphaned]
        assert any("orphan.md" in path for path in orphan_paths)

        # Verify structure of returned data
        for note in orphaned:
            assert "path" in note
            assert "title" in note
            assert "last_modified" in note
            assert "directory" in note

    def test_detect_orphaned_notes_excludes_inbox(self, coordinator, temp_vault):
        """Test that inbox notes are not flagged as orphaned."""
        # Create inbox note with no links
        (temp_vault / "Inbox" / "inbox_note.md").write_text(
            "# Inbox Note\n\nNo links here."
        )

        orphaned = coordinator.detect_orphaned_notes()
        orphan_paths = [note["path"] for note in orphaned]

        # Inbox notes should not be flagged as orphaned
        assert not any("Inbox" in path for path in orphan_paths)

    def test_detect_orphaned_notes_comprehensive_scans_all_files(
        self, coordinator, temp_vault
    ):
        """Test comprehensive scan includes all markdown files in repo."""
        # Create note outside standard directories
        (temp_vault / "Projects").mkdir()
        (temp_vault / "Projects" / "project_note.md").write_text(
            "# Project Note\n\nIsolated project note."
        )

        orphaned = coordinator.detect_orphaned_notes_comprehensive()

        assert isinstance(orphaned, list)
        # Should find more notes than standard scan
        standard_orphaned = coordinator.detect_orphaned_notes()
        assert len(orphaned) >= len(standard_orphaned)

    def test_detect_stale_notes_with_default_threshold(self, coordinator):
        """Test stale note detection with default 90-day threshold."""
        stale = coordinator.detect_stale_notes()

        assert isinstance(stale, list)
        assert len(stale) > 0

        # Verify structure
        for note in stale:
            assert "path" in note
            assert "title" in note
            assert "last_modified" in note
            assert "days_since_modified" in note
            assert note["days_since_modified"] >= 90

        # Verify sorted by staleness (most stale first)
        if len(stale) > 1:
            assert stale[0]["days_since_modified"] >= stale[-1]["days_since_modified"]

    def test_detect_stale_notes_with_custom_threshold(self, coordinator, temp_vault):
        """Test stale note detection with custom threshold."""
        # Create note that's 50 days old
        medium_stale = temp_vault / "Permanent Notes" / "medium_stale.md"
        medium_stale.write_text("# Medium Stale")
        old_time = (datetime.now() - timedelta(days=50)).timestamp()
        os.utime(medium_stale, (old_time, old_time))

        # Should find with 30-day threshold
        stale_30 = coordinator.detect_stale_notes(days_threshold=30)
        assert len(stale_30) > 0

        # Should not find with 60-day threshold
        stale_60 = coordinator.detect_stale_notes(days_threshold=60)
        paths_60 = [note["path"] for note in stale_60]
        assert not any("medium_stale.md" in path for path in paths_60)

    def test_generate_enhanced_metrics_returns_complete_data(self, coordinator):
        """Test generate_enhanced_metrics returns all required metrics."""
        metrics = coordinator.generate_enhanced_metrics()

        assert isinstance(metrics, dict)

        # Verify required top-level keys
        assert "generated_at" in metrics
        assert "orphaned_notes" in metrics
        assert "stale_notes" in metrics
        assert "link_density" in metrics
        assert "note_age_distribution" in metrics
        assert "productivity_metrics" in metrics
        assert "summary" in metrics

        # Verify summary statistics
        summary = metrics["summary"]
        assert "total_orphaned" in summary
        assert "total_stale" in summary
        assert "avg_links_per_note" in summary
        assert "total_notes" in summary


class TestAnalyticsCoordinatorGraphConstruction:
    """Test link graph construction logic."""

    @pytest.fixture
    def temp_vault(self):
        """Create vault with specific link patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "Permanent Notes").mkdir(parents=True)

            # Create notes with various link patterns
            (vault_path / "Permanent Notes" / "hub.md").write_text(
                "# Hub\n\nLinks: [[spoke1]], [[spoke2]], [[spoke3]]"
            )
            (vault_path / "Permanent Notes" / "spoke1.md").write_text(
                "# Spoke 1\n\nBack to [[hub]]"
            )
            (vault_path / "Permanent Notes" / "spoke2.md").write_text(
                "# Spoke 2\n\nLinks: [[hub]] and [[spoke1]]"
            )

            yield vault_path

    @pytest.fixture
    def coordinator(self, temp_vault):
        """Create coordinator."""
        if AnalyticsCoordinator is None:
            pytest.skip("AnalyticsCoordinator not yet implemented (RED phase)")
        return AnalyticsCoordinator(temp_vault)

    def test_build_link_graph_creates_correct_structure(self, coordinator):
        """Test that link graph correctly represents note connections."""
        # Access internal method for testing
        all_notes = list(Path(coordinator.base_dir).rglob("*.md"))
        link_graph = coordinator._build_link_graph(all_notes)

        assert isinstance(link_graph, dict)

        # Verify hub note has outgoing links
        assert "hub" in link_graph
        assert len(link_graph["hub"]) == 3
        assert "spoke1" in link_graph["hub"]
        assert "spoke2" in link_graph["hub"]
        assert "spoke3" in link_graph["hub"]

    def test_calculate_link_density_returns_average(self, coordinator):
        """Test link density calculation."""
        density = coordinator._calculate_link_density()

        assert isinstance(density, float)
        assert density >= 0.0
        # With our test data: hub (3 links), spoke1 (1 link), spoke2 (2 links), spoke3 (0 links)
        # Average should be around 1.5 links per note
        assert density > 0.0


class TestAnalyticsCoordinatorAgeAnalysis:
    """Test note age and productivity analysis."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator with temp vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "Permanent Notes").mkdir(parents=True)

            # Create notes with different ages
            # Note: Age distribution uses ctime (creation time) which can't be set on many filesystems
            # We create 4 notes to test the categorization logic exists
            new_note = vault_path / "Permanent Notes" / "new.md"
            new_note.write_text("# New")

            recent_note = vault_path / "Permanent Notes" / "recent.md"
            recent_note.write_text("# Recent")

            mature_note = vault_path / "Permanent Notes" / "mature.md"
            mature_note.write_text("# Mature")

            old_note = vault_path / "Permanent Notes" / "old.md"
            old_note.write_text("# Old")

            if AnalyticsCoordinator is None:
                pytest.skip("AnalyticsCoordinator not yet implemented (RED phase)")

            yield AnalyticsCoordinator(vault_path)

    def test_calculate_note_age_distribution_categorizes_correctly(self, coordinator):
        """Test age distribution categorization."""
        distribution = coordinator._calculate_note_age_distribution()

        assert isinstance(distribution, dict)
        assert "new" in distribution  # < 7 days
        assert "recent" in distribution  # 7-30 days
        assert "mature" in distribution  # 30-90 days
        assert "old" in distribution  # > 90 days

        # Verify we have 4 notes total distributed across buckets
        total_notes = sum(distribution.values())
        assert total_notes == 4

        # All newly created notes will be in "new" bucket (ctime is current)
        assert distribution["new"] == 4

    def test_calculate_productivity_metrics_returns_weekly_stats(self, coordinator):
        """Test productivity metrics calculation."""
        metrics = coordinator._calculate_productivity_metrics()

        assert isinstance(metrics, dict)
        assert "avg_notes_created_per_week" in metrics
        assert "avg_notes_modified_per_week" in metrics
        assert "total_weeks_active" in metrics

        # Verify reasonable values
        assert metrics["avg_notes_created_per_week"] >= 0
        assert metrics["avg_notes_modified_per_week"] >= 0
        assert metrics["total_weeks_active"] >= 0


class TestAnalyticsCoordinatorIntegration:
    """Integration tests with WorkflowManager."""

    @pytest.fixture
    def temp_vault(self):
        """Create minimal vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "Inbox").mkdir()
            (vault_path / "Fleeting Notes").mkdir()
            (vault_path / "Permanent Notes").mkdir()

            # Create one note
            (vault_path / "Permanent Notes" / "test.md").write_text(
                "# Test Note\n\nSome content."
            )

            yield vault_path

    def test_coordinator_integrates_with_workflow_manager(self, temp_vault):
        """Test that WorkflowManager can delegate to AnalyticsCoordinator."""
        from development.src.ai.workflow_manager import WorkflowManager

        # WorkflowManager should still work (backward compatibility)
        workflow = WorkflowManager(temp_vault)

        # These methods should now delegate to AnalyticsCoordinator
        orphaned = workflow.detect_orphaned_notes()
        assert isinstance(orphaned, list)

        stale = workflow.detect_stale_notes()
        assert isinstance(stale, list)

        metrics = workflow.generate_enhanced_metrics()
        assert isinstance(metrics, dict)

    def test_coordinator_handles_empty_vault_gracefully(self):
        """Test coordinator with empty vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "Permanent Notes").mkdir(parents=True)

            if AnalyticsCoordinator is None:
                pytest.skip("AnalyticsCoordinator not yet implemented (RED phase)")

            coordinator = AnalyticsCoordinator(vault_path)

            # Should return empty results, not crash
            orphaned = coordinator.detect_orphaned_notes()
            assert orphaned == []

            stale = coordinator.detect_stale_notes()
            assert stale == []

            metrics = coordinator.generate_enhanced_metrics()
            assert metrics["summary"]["total_notes"] == 0


class TestAnalyticsCoordinatorEdgeCases:
    """Test edge cases and error handling."""

    def test_coordinator_handles_malformed_markdown(self):
        """Test handling of files with encoding issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "Permanent Notes").mkdir(parents=True)

            # Create file with potential encoding issues
            normal_note = vault_path / "Permanent Notes" / "normal.md"
            normal_note.write_text("# Normal\n\nLinks: [[other]]", encoding="utf-8")

            if AnalyticsCoordinator is None:
                pytest.skip("AnalyticsCoordinator not yet implemented (RED phase)")

            coordinator = AnalyticsCoordinator(vault_path)

            # Should handle gracefully
            orphaned = coordinator.detect_orphaned_notes()
            assert isinstance(orphaned, list)

    def test_coordinator_handles_missing_directories(self):
        """Test handling when expected directories don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            # Don't create subdirectories

            if AnalyticsCoordinator is None:
                pytest.skip("AnalyticsCoordinator not yet implemented (RED phase)")

            coordinator = AnalyticsCoordinator(vault_path)

            # Should not crash, should return empty results
            orphaned = coordinator.detect_orphaned_notes()
            assert isinstance(orphaned, list)
            assert len(orphaned) == 0

    def test_extract_note_title_fallback_to_filename(self):
        """Test title extraction falls back to filename when no heading found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            (vault_path / "Permanent Notes").mkdir(parents=True)

            # Create note without markdown heading
            no_heading = vault_path / "Permanent Notes" / "no-heading.md"
            no_heading.write_text("Just some content without a heading.")

            if AnalyticsCoordinator is None:
                pytest.skip("AnalyticsCoordinator not yet implemented (RED phase)")

            coordinator = AnalyticsCoordinator(vault_path)

            # Should use filename as title
            title = coordinator._extract_note_title(no_heading)
            assert title == "no-heading"
