"""
RED phase — consolidated analytics module (#120).

Verifies that AnalyticsManager and AnalyticsCoordinator are importable
directly from src.ai.analytics after the three source files are merged.
All tests here will fail until the Green phase is complete.
"""

import pytest


# These imports define the contract — they FAIL until analytics.py is consolidated.
from src.ai.analytics import (
    AnalyticsManager,
    AnalyticsCoordinator,
    NoteAnalytics,
    NoteStats,
)


class TestConsolidatedImports:
    """Verify all public classes are importable from src.ai.analytics."""

    def test_analytics_manager_importable_from_analytics(self):
        assert AnalyticsManager is not None

    def test_analytics_coordinator_importable_from_analytics(self):
        assert AnalyticsCoordinator is not None

    def test_note_analytics_importable_from_analytics(self):
        assert NoteAnalytics is not None

    def test_note_stats_importable_from_analytics(self):
        assert NoteStats is not None


class TestAnalyticsManagerNoPureAIDeps:
    """AnalyticsManager must remain free of AI instantiation."""

    def test_analytics_manager_has_no_ai_attributes(self, tmp_path):
        mgr = AnalyticsManager(tmp_path, {})
        assert not hasattr(mgr, "ai_tagger")
        assert not hasattr(mgr, "ai_summarizer")
        assert not hasattr(mgr, "ai_connections")


class TestNoteAnalyticsNoPureAIDeps:
    """NoteAnalytics dead AI deps should be removed during consolidation."""

    def test_note_analytics_has_no_dead_ai_attributes(self, tmp_path):
        na = NoteAnalytics(str(tmp_path))
        assert not hasattr(na, "ai_tagger")
        assert not hasattr(na, "ai_summarizer")
        assert not hasattr(na, "ai_connections")


class TestAnalyticsCoordinatorSmoke:
    """Basic smoke tests for AnalyticsCoordinator via consolidated import."""

    def test_coordinator_initializes(self, tmp_path):
        coord = AnalyticsCoordinator(tmp_path)
        assert coord.base_dir == tmp_path

    def test_coordinator_empty_vault_returns_empty_lists(self, tmp_path):
        (tmp_path / "Permanent Notes").mkdir()
        coord = AnalyticsCoordinator(tmp_path)
        assert coord.detect_orphaned_notes() == []
        assert coord.detect_stale_notes() == []

    def test_coordinator_enhanced_metrics_keys(self, tmp_path):
        (tmp_path / "Permanent Notes").mkdir()
        coord = AnalyticsCoordinator(tmp_path)
        metrics = coord.generate_enhanced_metrics()
        for key in ("orphaned_notes", "stale_notes", "link_density", "summary"):
            assert key in metrics


class TestAnalyticsManagerSmoke:
    """Basic smoke tests for AnalyticsManager via consolidated import."""

    @pytest.fixture
    def vault(self, tmp_path):
        (tmp_path / "Fleeting Notes").mkdir()
        note = tmp_path / "Fleeting Notes" / "sample.md"
        note.write_text(
            "---\ntype: fleeting\nstatus: inbox\ntags: [a, b, c]\n---\n\n"
            + "word " * 200
            + "[[link-one]] [[link-two]]"
        )
        return tmp_path

    def test_assess_quality_returns_score(self, vault):
        mgr = AnalyticsManager(vault, {})
        result = mgr.assess_quality("Fleeting Notes/sample.md")
        assert result["success"] is True
        assert 0.0 <= result["quality_score"] <= 1.0

    def test_generate_workflow_report_has_required_keys(self, vault):
        mgr = AnalyticsManager(vault, {})
        report = mgr.generate_workflow_report()
        assert "total_notes" in report
        assert "notes_by_type" in report
        assert report["total_notes"] >= 1
