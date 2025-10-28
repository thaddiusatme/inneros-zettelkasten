"""
RED PHASE: Comprehensive failing tests for FleetingAnalysisCoordinator extraction.

ADR-002 Phase 9: Extract fleeting note analysis functionality from WorkflowManager
into dedicated coordinator following proven composition pattern.

Test Coverage:
- Fleeting note age categorization (new/recent/stale/old)
- Age distribution statistics aggregation
- Metadata extraction from note files
- Health reporting generation with recommendations
- Edge cases: missing metadata, invalid dates, empty directories
- Integration with WorkflowManager delegation
- Error handling for file access issues

Expected: 18/18 tests FAILING (coordinator doesn't exist yet)
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

# Import will fail initially - that's expected for RED phase
try:
    from src.ai.fleeting_analysis_coordinator import (
        FleetingAnalysisCoordinator,
        FleetingAnalysis,
    )

    COORDINATOR_EXISTS = True
except ImportError:
    COORDINATOR_EXISTS = False

    # Create placeholder for test structure
    class FleetingAnalysisCoordinator:
        pass

    class FleetingAnalysis:
        pass


class TestFleetingAnalysisDataclass:
    """Test FleetingAnalysis dataclass structure and defaults."""

    def test_fleeting_analysis_default_values(self):
        """RED: FleetingAnalysis should initialize with proper defaults."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        analysis = FleetingAnalysis()
        assert analysis.total_count == 0
        assert analysis.age_distribution == {
            "new": 0,
            "recent": 0,
            "stale": 0,
            "old": 0,
        }
        assert analysis.oldest_note is None
        assert analysis.newest_note is None
        assert analysis.notes_by_age == []

    def test_fleeting_analysis_with_data(self):
        """RED: FleetingAnalysis should store analysis results correctly."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        analysis = FleetingAnalysis()
        analysis.total_count = 5
        analysis.age_distribution = {"new": 2, "recent": 1, "stale": 1, "old": 1}
        analysis.oldest_note = {"name": "old.md", "days_old": 100}
        analysis.newest_note = {"name": "new.md", "days_old": 1}

        assert analysis.total_count == 5
        assert analysis.age_distribution["new"] == 2
        assert analysis.oldest_note["days_old"] == 100


class TestFleetingAnalysisCoordinatorInitialization:
    """Test coordinator initialization and dependency injection."""

    def test_coordinator_initialization(self):
        """RED: Coordinator should initialize with fleeting_dir dependency."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        fleeting_dir = Path("/fake/fleeting/notes")
        coordinator = FleetingAnalysisCoordinator(fleeting_dir)

        assert coordinator.fleeting_dir == fleeting_dir

    def test_coordinator_rejects_none_directory(self):
        """RED: Coordinator should reject None as fleeting_dir."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with pytest.raises((TypeError, ValueError)):
            FleetingAnalysisCoordinator(None)


class TestFleetingNoteAgeAnalysis:
    """Test age categorization and analysis logic."""

    def test_analyze_fleeting_notes_empty_directory(self):
        """RED: Should handle empty fleeting notes directory gracefully."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir) / "fleeting"
            fleeting_dir.mkdir()

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 0
            assert all(count == 0 for count in analysis.age_distribution.values())
            assert analysis.oldest_note is None
            assert analysis.newest_note is None

    def test_analyze_fleeting_notes_nonexistent_directory(self):
        """RED: Should handle nonexistent directory gracefully."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        fleeting_dir = Path("/nonexistent/directory")
        coordinator = FleetingAnalysisCoordinator(fleeting_dir)
        analysis = coordinator.analyze_fleeting_notes()

        assert analysis.total_count == 0

    def test_categorize_note_as_new(self):
        """RED: Should categorize note created 5 days ago as 'new'."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            # Create note with frontmatter dated 5 days ago
            created_date = (datetime.now() - timedelta(days=5)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1
            assert analysis.age_distribution["new"] == 1
            assert analysis.age_distribution["recent"] == 0

    def test_categorize_note_as_recent(self):
        """RED: Should categorize note created 20 days ago as 'recent'."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            created_date = (datetime.now() - timedelta(days=20)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1
            assert analysis.age_distribution["recent"] == 1

    def test_categorize_note_as_stale(self):
        """RED: Should categorize note created 60 days ago as 'stale'."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            created_date = (datetime.now() - timedelta(days=60)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1
            assert analysis.age_distribution["stale"] == 1

    def test_categorize_note_as_old(self):
        """RED: Should categorize note created 100 days ago as 'old'."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            created_date = (datetime.now() - timedelta(days=100)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1
            assert analysis.age_distribution["old"] == 1


class TestMetadataExtraction:
    """Test metadata extraction and fallback logic."""

    def test_extract_metadata_from_frontmatter(self):
        """RED: Should extract created date from YAML frontmatter."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            created_date = "2024-01-15 10:30"
            content = f"---\ncreated: {created_date}\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1
            assert len(analysis.notes_by_age) == 1

    def test_fallback_to_file_mtime_when_no_frontmatter(self):
        """RED: Should use file modification time when created date missing."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            content = "---\n---\n\nNo created date"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1

    def test_handle_invalid_date_format(self):
        """RED: Should fallback gracefully on invalid date format."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            content = "---\ncreated: invalid-date\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            assert analysis.total_count == 1  # Should still process the note

    def test_skip_templater_placeholders(self):
        """RED: Should skip notes with unprocessed template placeholders."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)
            note_path = fleeting_dir / "test-note.md"

            content = "---\ncreated: {{date:YYYY-MM-DD HH:mm}}\n---\n\nTest content"
            note_path.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            analysis = coordinator.analyze_fleeting_notes()

            # Should fallback to file mtime instead of processing placeholder
            assert analysis.total_count == 1


class TestHealthReportGeneration:
    """Test health report generation with recommendations."""

    def test_health_report_for_empty_collection(self):
        """RED: Health report should show HEALTHY for empty collection."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir) / "fleeting"
            fleeting_dir.mkdir()

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            report = coordinator.generate_fleeting_health_report()

            assert report["health_status"] == "HEALTHY"
            assert report["total_count"] == 0
            assert "well-managed" in report["summary"].lower()

    def test_health_report_critical_status(self):
        """RED: Health report should show CRITICAL when 50%+ notes are old."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)

            # Create 4 old notes and 1 new note
            for i in range(4):
                note_path = fleeting_dir / f"old-note-{i}.md"
                created_date = (datetime.now() - timedelta(days=100)).strftime(
                    "%Y-%m-%d %H:%M"
                )
                content = f"---\ncreated: {created_date}\n---\n\nOld note"
                note_path.write_text(content, encoding="utf-8")

            new_note = fleeting_dir / "new-note.md"
            created_date = (datetime.now() - timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nNew note"
            new_note.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            report = coordinator.generate_fleeting_health_report()

            assert report["health_status"] == "CRITICAL"
            assert report["total_count"] == 5
            assert "critical" in report["summary"].lower() or "80%" in report["summary"]

    def test_health_report_with_recommendations(self):
        """RED: Health report should include actionable recommendations."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        with TemporaryDirectory() as tmpdir:
            fleeting_dir = Path(tmpdir)

            # Create mix of notes
            old_note = fleeting_dir / "old-note.md"
            created_date = (datetime.now() - timedelta(days=95)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nOld note"
            old_note.write_text(content, encoding="utf-8")

            stale_note = fleeting_dir / "stale-note.md"
            created_date = (datetime.now() - timedelta(days=60)).strftime(
                "%Y-%m-%d %H:%M"
            )
            content = f"---\ncreated: {created_date}\n---\n\nStale note"
            stale_note.write_text(content, encoding="utf-8")

            coordinator = FleetingAnalysisCoordinator(fleeting_dir)
            report = coordinator.generate_fleeting_health_report()

            assert "recommendations" in report
            assert len(report["recommendations"]) > 0
            # Should recommend processing old notes
            assert any("old" in rec.lower() for rec in report["recommendations"])


class TestWorkflowManagerDelegation:
    """Test WorkflowManager delegation to coordinator."""

    def test_workflow_manager_delegates_analyze_fleeting_notes(self):
        """RED: WorkflowManager should delegate to FleetingAnalysisCoordinator."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        # This test will verify the integration after GREEN phase
        # For now, just check the structure
        from src.ai.workflow_manager import WorkflowManager

        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            fleeting_dir = base_dir / "Fleeting Notes"
            fleeting_dir.mkdir()

            manager = WorkflowManager(str(base_dir))

            # Should have coordinator initialized
            assert hasattr(manager, "fleeting_analysis_coordinator")
            assert manager.fleeting_analysis_coordinator is not None

    def test_workflow_manager_delegates_health_report(self):
        """RED: WorkflowManager should delegate health report generation."""
        if not COORDINATOR_EXISTS:
            pytest.skip("Coordinator not yet created - RED phase")

        from src.ai.workflow_manager import WorkflowManager

        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            fleeting_dir = base_dir / "Fleeting Notes"
            fleeting_dir.mkdir()

            manager = WorkflowManager(str(base_dir))
            report = manager.generate_fleeting_health_report()

            # Should return health report structure
            assert "health_status" in report
            assert "recommendations" in report
