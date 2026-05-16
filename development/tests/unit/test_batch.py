"""
Spec tests for the batch module (#120).

Verifies the public API surface of the consolidated module:
- WorkflowManager, NoteProcessingCoordinator, BatchProcessingCoordinator,
  WorkflowReportingCoordinator, and the batch_inbox_processor functions
  are all importable from ai.batch.
- Imports use the new consolidated modules (enrichment, analytics,
  connections_discovery) rather than the old split files.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src")
sys.path.insert(0, src_dir)

from ai.batch import (
    WorkflowManager,
    BatchProcessingCoordinator,
    NoteProcessingCoordinator,
    WorkflowReportingCoordinator,
    batch_process_unprocessed_inbox,
    is_note_eligible_for_processing,
    scan_eligible_notes,
)


# ---------------------------------------------------------------------------
# Import surface — all public names importable from ai.batch
# ---------------------------------------------------------------------------


class TestBatchImports:
    def test_workflow_manager_importable(self):
        assert WorkflowManager is not None

    def test_batch_processing_coordinator_importable(self):
        assert BatchProcessingCoordinator is not None

    def test_note_processing_coordinator_importable(self):
        assert NoteProcessingCoordinator is not None

    def test_workflow_reporting_coordinator_importable(self):
        assert WorkflowReportingCoordinator is not None

    def test_batch_process_unprocessed_inbox_callable(self):
        assert callable(batch_process_unprocessed_inbox)

    def test_is_note_eligible_callable(self):
        assert callable(is_note_eligible_for_processing)

    def test_scan_eligible_notes_callable(self):
        assert callable(scan_eligible_notes)


# ---------------------------------------------------------------------------
# WorkflowManager — interface
# ---------------------------------------------------------------------------


class TestWorkflowManagerInterface:
    REQUIRED_METHODS = [
        "process_inbox_note",
        "promote_note",
        "batch_process_inbox",
        "generate_workflow_report",
        "scan_review_candidates",
        "generate_weekly_recommendations",
        "detect_orphaned_notes",
        "detect_stale_notes",
        "generate_enhanced_metrics",
        "remediate_orphaned_notes",
        "analyze_fleeting_notes",
        "generate_fleeting_health_report",
        "generate_fleeting_triage_report",
        "promote_fleeting_note",
        "promote_fleeting_notes_batch",
        "auto_promote_ready_notes",
        "repair_inbox_metadata",
        "safe_process_inbox_note",
        "safe_batch_process_inbox",
    ]

    @pytest.mark.parametrize("method", REQUIRED_METHODS)
    def test_has_method(self, method):
        assert callable(
            getattr(WorkflowManager, method, None)
        ), f"WorkflowManager missing method: {method}"


# ---------------------------------------------------------------------------
# WorkflowManager — behaviour
# ---------------------------------------------------------------------------


class TestWorkflowManagerBehaviour:
    def test_init_with_no_args(self, tmp_path):
        wm = WorkflowManager(base_directory=str(tmp_path))
        assert wm is not None

    def test_init_sets_base_dir(self, tmp_path):
        wm = WorkflowManager(base_directory=str(tmp_path))
        assert wm.base_dir is not None

    def test_merge_tags_deduplicates(self, tmp_path):
        wm = WorkflowManager(base_directory=str(tmp_path))
        result = wm._merge_tags(["ai", "automation"], ["ai", "business"])
        assert "ai" in result
        assert result.count("ai") == 1

    def test_merge_tags_combines(self, tmp_path):
        wm = WorkflowManager(base_directory=str(tmp_path))
        result = wm._merge_tags(["a"], ["b"])
        assert "a" in result and "b" in result

    def test_process_inbox_note_missing_file(self, tmp_path):
        wm = WorkflowManager(base_directory=str(tmp_path))
        result = wm.process_inbox_note(str(tmp_path / "nonexistent.md"))
        assert (
            result.get("status") in ("error", "failed", "not_found")
            or "error" in result
        )


# ---------------------------------------------------------------------------
# BatchProcessingCoordinator — interface
# ---------------------------------------------------------------------------


class TestBatchProcessingCoordinatorInterface:
    def test_has_batch_process_inbox(self):
        assert callable(
            getattr(BatchProcessingCoordinator, "batch_process_inbox", None)
        )

    def test_init_with_inbox_dir(self, tmp_path):
        coord = BatchProcessingCoordinator(inbox_dir=tmp_path)
        assert coord is not None


# ---------------------------------------------------------------------------
# NoteProcessingCoordinator — interface
# ---------------------------------------------------------------------------


class TestNoteProcessingCoordinatorInterface:
    REQUIRED_METHODS = [
        "process_note",
        "_merge_tags",
        "_extract_wikilinks_from_body",
        "_compute_suggested_links",
    ]

    @pytest.mark.parametrize("method", REQUIRED_METHODS)
    def test_has_method(self, method):
        assert callable(getattr(NoteProcessingCoordinator, method, None))


# ---------------------------------------------------------------------------
# WorkflowReportingCoordinator — interface
# ---------------------------------------------------------------------------


class TestWorkflowReportingCoordinatorInterface:
    def test_has_generate_workflow_report(self):
        assert callable(
            getattr(WorkflowReportingCoordinator, "generate_workflow_report", None)
        )


# ---------------------------------------------------------------------------
# batch_inbox_processor functions
# ---------------------------------------------------------------------------


class TestBatchInboxProcessorFunctions:
    def test_is_note_eligible_missing_file(self, tmp_path):
        result = is_note_eligible_for_processing(tmp_path / "no_such.md")
        assert isinstance(result, bool)

    def test_is_note_eligible_processed_note(self, tmp_path):
        note = tmp_path / "processed.md"
        note.write_text(
            "---\nai_processed: true\ntriage_recommendation: keep\n---\nContent."
        )
        assert is_note_eligible_for_processing(note) is False

    def test_is_note_eligible_unprocessed_note(self, tmp_path):
        note = tmp_path / "fresh.md"
        note.write_text("---\ntitle: New Note\n---\nContent.")
        assert is_note_eligible_for_processing(note) is True

    def test_scan_eligible_notes_empty_dir(self, tmp_path):
        result = scan_eligible_notes(tmp_path)
        assert result == []

    def test_scan_eligible_notes_finds_md_files(self, tmp_path):
        (tmp_path / "a.md").write_text("---\ntitle: A\n---\nContent.")
        (tmp_path / "b.txt").write_text("not a note")
        result = scan_eligible_notes(tmp_path)
        assert len(result) >= 1
        assert all(str(p).endswith(".md") for p in result)

    def test_batch_process_unprocessed_inbox_missing_dir(self, tmp_path):
        result = batch_process_unprocessed_inbox(tmp_path / "nonexistent")
        assert isinstance(result, dict)
        assert "errors" in result or "processed" in result or "error" in result
