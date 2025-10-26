"""
TDD Iteration - ADR-002 Phase 5: Review/Triage Coordinator Tests

RED Phase: Comprehensive failing tests for ReviewTriageCoordinator extraction.
This coordinator handles weekly review and fleeting note triage functionality.

Expected: 0/18 tests passing initially (all tests should FAIL)
Target: 18/18 tests passing after GREEN phase implementation
"""

from pathlib import Path
from datetime import datetime
from unittest.mock import Mock
import tempfile


class TestReviewTriageCoordinatorInitialization:
    """Test ReviewTriageCoordinator initialization and configuration."""

    def test_coordinator_initialization_with_required_dependencies(self):
        """Test coordinator initializes with base_dir and workflow_manager."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        base_dir = Path("/tmp/test_vault")
        workflow_manager = Mock()

        coordinator = ReviewTriageCoordinator(base_dir, workflow_manager)

        assert coordinator.base_dir == base_dir
        assert coordinator.workflow_manager == workflow_manager
        assert coordinator.inbox_dir == base_dir / "Inbox"
        assert coordinator.fleeting_dir == base_dir / "Fleeting Notes"

    def test_coordinator_validates_base_directory_exists(self):
        """Test coordinator validates base directory exists."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir) / "vault"
            base_dir.mkdir()

            workflow_manager = Mock()
            coordinator = ReviewTriageCoordinator(base_dir, workflow_manager)

            assert coordinator.base_dir.exists()


class TestReviewCandidateScanning:
    """Test review candidate scanning functionality."""

    def test_scan_review_candidates_finds_inbox_notes(self):
        """Test scanning finds all .md files in Inbox/ directory."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            # Create test notes
            (inbox / "note1.md").write_text("---\ntitle: Note 1\n---\nContent")
            (inbox / "note2.md").write_text("---\ntitle: Note 2\n---\nContent")

            workflow_manager = Mock()
            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            candidates = coordinator.scan_review_candidates()

            assert len(candidates) == 2
            assert all(c["source"] == "inbox" for c in candidates)

    def test_scan_review_candidates_finds_fleeting_notes_with_inbox_status(self):
        """Test scanning finds fleeting notes with status: inbox."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            fleeting = vault / "Fleeting Notes"
            fleeting.mkdir()

            # Note with status: inbox should be included
            (fleeting / "fleeting1.md").write_text(
                "---\ntitle: Fleeting 1\nstatus: inbox\n---\nContent"
            )
            # Note without status: inbox should be excluded
            (fleeting / "fleeting2.md").write_text(
                "---\ntitle: Fleeting 2\n---\nContent"
            )

            workflow_manager = Mock()
            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            candidates = coordinator.scan_review_candidates()

            assert len(candidates) == 1
            assert candidates[0]["source"] == "fleeting"
            assert candidates[0]["metadata"]["status"] == "inbox"

    def test_scan_handles_malformed_frontmatter_gracefully(self):
        """Test scanning handles notes with malformed YAML frontmatter."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            # Malformed YAML
            (inbox / "broken.md").write_text("---\ninvalid yaml: {{\n---\nContent")
            # Valid note
            (inbox / "valid.md").write_text("---\ntitle: Valid\n---\nContent")

            workflow_manager = Mock()
            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            candidates = coordinator.scan_review_candidates()

            # Should still find both, but broken one has empty metadata or error
            assert len(candidates) == 2


class TestWeeklyRecommendations:
    """Test weekly review recommendations generation."""

    def test_generate_weekly_recommendations_processes_all_candidates(self):
        """Test generates recommendations for all candidates."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            (inbox / "note1.md").write_text("---\ntitle: Note 1\n---\nContent")
            (inbox / "note2.md").write_text("---\ntitle: Note 2\n---\nContent")

            # Mock workflow_manager.process_inbox_note
            workflow_manager = Mock()
            workflow_manager.process_inbox_note.return_value = {
                "quality_score": 0.8,
                "recommendations": [{
                    "action": "promote_to_permanent",
                    "reason": "High quality",
                    "confidence": 0.9
                }],
                "processing": {"ai_tags": ["tag1", "tag2"]}
            }

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)
            candidates = coordinator.scan_review_candidates()

            result = coordinator.generate_weekly_recommendations(candidates)

            assert len(result["recommendations"]) == 2
            assert result["summary"]["total_notes"] == 2
            assert result["summary"]["promote_to_permanent"] == 2

    def test_generate_recommendations_respects_dry_run_mode(self):
        """Test dry_run mode passes fast=True to avoid AI calls."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            (inbox / "note.md").write_text("---\ntitle: Note\n---\nContent")

            workflow_manager = Mock()
            workflow_manager.process_inbox_note.return_value = {
                "quality_score": 0.7,
                "recommendations": [{"action": "promote_to_permanent", "reason": "Good", "confidence": 0.8}],
                "processing": {"ai_tags": []}
            }

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)
            candidates = coordinator.scan_review_candidates()

            coordinator.generate_weekly_recommendations(candidates, dry_run=True)

            # Verify process_inbox_note was called with fast=True
            workflow_manager.process_inbox_note.assert_called_once()
            call_kwargs = workflow_manager.process_inbox_note.call_args[1]
            assert call_kwargs.get("fast") is True

    def test_generate_recommendations_handles_processing_errors(self):
        """Test gracefully handles errors during note processing."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            (inbox / "note.md").write_text("---\ntitle: Note\n---\nContent")

            workflow_manager = Mock()
            workflow_manager.process_inbox_note.side_effect = Exception("AI service down")

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)
            candidates = coordinator.scan_review_candidates()

            result = coordinator.generate_weekly_recommendations(candidates)

            assert len(result["recommendations"]) == 1
            assert result["recommendations"][0]["action"] == "manual_review"
            assert result["summary"]["processing_errors"] == 1

    def test_generate_recommendations_includes_timestamp(self):
        """Test result includes ISO timestamp of generation."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            workflow_manager = Mock()

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            result = coordinator.generate_weekly_recommendations([])

            assert "generated_at" in result
            # Should be valid ISO format
            datetime.fromisoformat(result["generated_at"])


class TestFleetingTriageReport:
    """Test fleeting note triage report generation."""

    def test_generate_fleeting_triage_report_finds_fleeting_notes(self):
        """Test triage report scans for fleeting notes in appropriate directories."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            fleeting = vault / "Fleeting Notes"
            fleeting.mkdir()

            (fleeting / "fleeting1.md").write_text(
                "---\ntitle: Fleeting 1\ntype: fleeting\n---\nContent"
            )

            workflow_manager = Mock()
            workflow_manager.process_inbox_note.return_value = {
                "quality_score": 0.6,
                "ai_tags": ["tag1"],
                "metadata": {"created": "2025-10-14"}
            }

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            report = coordinator.generate_fleeting_triage_report()

            assert report["total_notes_processed"] == 1
            assert len(report["recommendations"]) == 1

    def test_triage_report_categorizes_by_quality_score(self):
        """Test triage report categorizes notes by quality thresholds."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            fleeting = vault / "Fleeting Notes"
            fleeting.mkdir()

            # High quality note
            (fleeting / "high.md").write_text(
                "---\ntitle: High\ntype: fleeting\n---\nContent"
            )
            # Medium quality note
            (fleeting / "med.md").write_text(
                "---\ntitle: Med\ntype: fleeting\n---\nContent"
            )
            # Low quality note
            (fleeting / "low.md").write_text(
                "---\ntitle: Low\ntype: fleeting\n---\nContent"
            )

            workflow_manager = Mock()
            # Return different quality scores for each note
            workflow_manager.process_inbox_note.side_effect = [
                {"quality_score": 0.8, "ai_tags": [], "metadata": {}},  # High
                {"quality_score": 0.5, "ai_tags": [], "metadata": {}},  # Medium
                {"quality_score": 0.2, "ai_tags": [], "metadata": {}},  # Low
            ]

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            report = coordinator.generate_fleeting_triage_report()

            assert report["quality_distribution"]["high"] == 1
            assert report["quality_distribution"]["medium"] == 1
            assert report["quality_distribution"]["low"] == 1

    def test_triage_report_filters_by_quality_threshold(self):
        """Test triage report can filter notes by minimum quality threshold."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            fleeting = vault / "Fleeting Notes"
            fleeting.mkdir()

            (fleeting / "high.md").write_text(
                "---\ntitle: High\ntype: fleeting\n---\nContent"
            )
            (fleeting / "low.md").write_text(
                "---\ntitle: Low\ntype: fleeting\n---\nContent"
            )

            workflow_manager = Mock()
            workflow_manager.process_inbox_note.side_effect = [
                {"quality_score": 0.8, "ai_tags": [], "metadata": {}},
                {"quality_score": 0.3, "ai_tags": [], "metadata": {}},
            ]

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            report = coordinator.generate_fleeting_triage_report(quality_threshold=0.7)

            # Only high quality note should be in recommendations
            assert len(report["recommendations"]) == 1
            assert report["filtered_count"] == 1

    def test_triage_report_respects_fast_mode(self):
        """Test fast mode skips external AI calls for speed."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            fleeting = vault / "Fleeting Notes"
            fleeting.mkdir()

            (fleeting / "note.md").write_text(
                "---\ntitle: Note\ntype: fleeting\n---\nContent"
            )

            workflow_manager = Mock()
            workflow_manager.process_inbox_note.return_value = {
                "quality_score": 0.7,
                "ai_tags": [],
                "metadata": {}
            }

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            coordinator.generate_fleeting_triage_report(fast=True)

            # Verify process_inbox_note was called with fast=True
            workflow_manager.process_inbox_note.assert_called()
            call_kwargs = workflow_manager.process_inbox_note.call_args[1]
            assert call_kwargs.get("fast") is True

    def test_triage_report_includes_processing_time(self):
        """Test triage report includes total processing time."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            workflow_manager = Mock()

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            report = coordinator.generate_fleeting_triage_report()

            assert "processing_time" in report
            assert isinstance(report["processing_time"], (int, float))
            assert report["processing_time"] >= 0


class TestCoordinatorIntegration:
    """Test ReviewTriageCoordinator integration with WorkflowManager."""

    def test_coordinator_integrates_with_workflow_manager_delegation(self):
        """Test WorkflowManager correctly delegates to coordinator."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            (inbox / "note.md").write_text("---\ntitle: Note\n---\nContent")

            # Mock workflow manager that will be injected
            workflow_manager = Mock()
            workflow_manager.base_dir = vault
            workflow_manager.process_inbox_note.return_value = {
                "quality_score": 0.7,
                "recommendations": [{"action": "promote", "reason": "Good", "confidence": 0.8}],
                "processing": {"ai_tags": []}
            }

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)

            # Test that coordinator can use workflow_manager.process_inbox_note
            candidates = coordinator.scan_review_candidates()
            result = coordinator.generate_weekly_recommendations(candidates)

            assert workflow_manager.process_inbox_note.called
            assert len(result["recommendations"]) > 0

    def test_coordinator_sanitizes_tags_in_recommendations(self):
        """Test coordinator sanitizes metadata tags for clean display."""
        from src.ai.review_triage_coordinator import ReviewTriageCoordinator

        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            inbox = vault / "Inbox"
            inbox.mkdir()

            # Note with problematic tags
            (inbox / "note.md").write_text(
                "---\ntitle: Note\ntags: [valid-tag, '!!!', '', '123']\n---\nContent"
            )

            workflow_manager = Mock()
            workflow_manager.process_inbox_note.return_value = {
                "quality_score": 0.7,
                "recommendations": [{"action": "promote", "reason": "Good", "confidence": 0.8}],
                "processing": {"ai_tags": []}
            }

            coordinator = ReviewTriageCoordinator(vault, workflow_manager)
            candidates = coordinator.scan_review_candidates()
            result = coordinator.generate_weekly_recommendations(candidates)

            # Tags should be sanitized (punctuation-only and empty removed)
            rec_metadata = result["recommendations"][0]["metadata"]
            if "tags" in rec_metadata:
                # Should not contain empty or punctuation-only tags
                assert "!!!" not in rec_metadata["tags"]
                assert "" not in rec_metadata["tags"]


# RED Phase Expected Results:
# - All 18 tests should FAIL (ReviewTriageCoordinator doesn't exist yet)
# - Tests define the complete API contract for the coordinator
# - Tests cover: initialization, scanning, recommendations, triage, integration, edge cases
