"""
Spec tests for the lifecycle module (#120).

Verifies the public API surface of the consolidated module:
- All key classes importable from lifecycle
- Core behaviours preserved from the source files:
    note_lifecycle_manager.py, promotion_engine.py,
    fleeting_note_coordinator.py, fleeting_analysis_coordinator.py,
    review_triage_coordinator.py, import_manager.py, import_schema.py
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src")
sys.path.insert(0, src_dir)

from ai.lifecycle import (
    # note_lifecycle_manager
    StatusTransition,
    NoteLifecycleManager,
    # promotion_engine
    PromotionEngine,
    # fleeting_note_coordinator
    FleetingNoteCoordinator,
    # fleeting_analysis_coordinator
    FleetingAnalysis,
    FleetingAnalysisCoordinator,
    # review_triage_coordinator
    ReviewTriageCoordinator,
    # import_manager
    CSVImportAdapter,
    JSONImportAdapter,
    NoteWriter,
    # import_schema
    ImportItem,
    validate_item,
)


# ---------------------------------------------------------------------------
# NoteLifecycleManager — interface
# ---------------------------------------------------------------------------


class TestNoteLifecycleManagerInterface:
    def test_importable(self):
        assert NoteLifecycleManager is not None

    def test_init_no_args(self):
        mgr = NoteLifecycleManager()
        assert mgr is not None

    def test_init_with_base_dir(self, tmp_path):
        mgr = NoteLifecycleManager(base_dir=tmp_path)
        assert mgr is not None

    def test_has_update_status(self):
        assert callable(getattr(NoteLifecycleManager, "update_status", None))

    def test_has_validate_transition(self):
        assert callable(getattr(NoteLifecycleManager, "validate_transition", None))


class TestStatusTransition:
    def test_importable(self):
        assert StatusTransition is not None


# ---------------------------------------------------------------------------
# PromotionEngine — interface
# ---------------------------------------------------------------------------


class TestPromotionEngineInterface:
    def test_importable(self):
        assert PromotionEngine is not None

    def test_init_with_deps(self, tmp_path):
        mgr = NoteLifecycleManager(base_dir=tmp_path)
        engine = PromotionEngine(base_dir=tmp_path, lifecycle_manager=mgr)
        assert engine is not None

    def test_base_dir_stored(self, tmp_path):
        mgr = NoteLifecycleManager(base_dir=tmp_path)
        engine = PromotionEngine(base_dir=tmp_path, lifecycle_manager=mgr)
        assert engine.base_dir == tmp_path

    def test_has_promote_note(self):
        assert callable(getattr(PromotionEngine, "promote_note", None))


# ---------------------------------------------------------------------------
# FleetingNoteCoordinator — interface
# ---------------------------------------------------------------------------


class TestFleetingNoteCoordinatorInterface:
    def test_importable(self):
        assert FleetingNoteCoordinator is not None

    def test_init_with_dirs(self, tmp_path):
        coord = FleetingNoteCoordinator(
            fleeting_dir=tmp_path / "Fleeting",
            inbox_dir=tmp_path / "Inbox",
            permanent_dir=tmp_path / "Permanent",
            literature_dir=tmp_path / "Literature",
        )
        assert coord is not None

    def test_quality_threshold_default(self, tmp_path):
        coord = FleetingNoteCoordinator(
            fleeting_dir=tmp_path / "Fleeting",
            inbox_dir=tmp_path / "Inbox",
            permanent_dir=tmp_path / "Permanent",
            literature_dir=tmp_path / "Literature",
        )
        assert coord.default_quality_threshold == 0.7

    def test_quality_threshold_custom(self, tmp_path):
        coord = FleetingNoteCoordinator(
            fleeting_dir=tmp_path / "Fleeting",
            inbox_dir=tmp_path / "Inbox",
            permanent_dir=tmp_path / "Permanent",
            literature_dir=tmp_path / "Literature",
            default_quality_threshold=0.5,
        )
        assert coord.default_quality_threshold == 0.5


# ---------------------------------------------------------------------------
# FleetingAnalysisCoordinator — interface
# ---------------------------------------------------------------------------


class TestFleetingAnalysisCoordinatorInterface:
    def test_importable(self):
        assert FleetingAnalysisCoordinator is not None

    def test_init_with_fleeting_dir(self, tmp_path):
        coord = FleetingAnalysisCoordinator(fleeting_dir=tmp_path)
        assert coord is not None

    def test_has_analyze_fleeting_notes(self):
        assert callable(
            getattr(FleetingAnalysisCoordinator, "analyze_fleeting_notes", None)
        )


class TestFleetingAnalysis:
    def test_importable(self):
        assert FleetingAnalysis is not None


# ---------------------------------------------------------------------------
# ReviewTriageCoordinator — interface
# ---------------------------------------------------------------------------


class TestReviewTriageCoordinatorInterface:
    def test_importable(self):
        assert ReviewTriageCoordinator is not None

    def test_init_with_deps(self, tmp_path):
        mock_wm = MagicMock()
        coord = ReviewTriageCoordinator(base_dir=tmp_path, workflow_manager=mock_wm)
        assert coord is not None

    def test_has_scan_review_candidates(self):
        assert callable(
            getattr(ReviewTriageCoordinator, "scan_review_candidates", None)
        )


# ---------------------------------------------------------------------------
# import_manager — interface
# ---------------------------------------------------------------------------


class TestCSVImportAdapter:
    def test_importable(self):
        assert CSVImportAdapter is not None

    def test_has_load_method(self):
        assert callable(getattr(CSVImportAdapter, "load", None))

    def test_load_empty_csv(self, tmp_path):
        csv_file = tmp_path / "items.csv"
        csv_file.write_text("title,content\n")
        result = CSVImportAdapter.load(csv_file)
        assert isinstance(result, list)


class TestJSONImportAdapter:
    def test_importable(self):
        assert JSONImportAdapter is not None

    def test_has_load_method(self):
        assert callable(getattr(JSONImportAdapter, "load", None))


class TestNoteWriter:
    def test_importable(self):
        assert NoteWriter is not None

    def test_init_with_base_dir(self, tmp_path):
        writer = NoteWriter(base_dir=tmp_path)
        assert writer is not None


# ---------------------------------------------------------------------------
# import_schema — interface
# ---------------------------------------------------------------------------


class TestImportItem:
    def test_importable(self):
        assert ImportItem is not None


class TestValidateItem:
    def test_importable(self):
        assert validate_item is not None

    def test_callable(self):
        assert callable(validate_item)
