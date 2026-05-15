"""
Spec tests for the connections_insertion module (#120).

Verifies the public API surface of the consolidated module:
- All key classes importable from connections_insertion
- Core behaviours preserved from the source files:
    link_insertion_engine.py, link_insertion_utils.py,
    real_connection_integration_engine.py, connection_integration_utils.py,
    orphan_remediation_coordinator.py
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src")
sys.path.insert(0, src_dir)

from ai.connections_insertion import (
    # link_insertion_engine
    LinkInsertionEngine,
    UndoManager,
    # link_insertion_utils
    InsertionResult,
    SafetyBackupManager,
    SmartInsertionProcessor,
    ContentValidator,
    BatchInsertionOrchestrator,
    LocationDetectionEnhancer,
    # real_connection_integration_engine
    RealConnectionIntegrationEngine,
    CLIIntegrationOrchestrator,
    ProductionOptimizedProcessor,
    # connection_integration_utils
    ConnectionObject,
    SimilarityResultConverter,
    RealNoteLoader,
    PerformanceMonitor,
    ConnectionQualityAnalyzer,
    RealConnectionProcessor,
    # orphan_remediation_coordinator
    OrphanRemediationCoordinator,
)


# ---------------------------------------------------------------------------
# LinkInsertionEngine — interface
# ---------------------------------------------------------------------------


class TestLinkInsertionEngineInterface:
    def test_importable(self):
        assert LinkInsertionEngine is not None

    def test_init_with_vault_path(self, tmp_path):
        engine = LinkInsertionEngine(vault_path=str(tmp_path))
        assert engine is not None

    def test_vault_path_stored(self, tmp_path):
        engine = LinkInsertionEngine(vault_path=str(tmp_path))
        assert str(tmp_path) in engine.vault_path

    def test_backup_enabled_default(self, tmp_path):
        engine = LinkInsertionEngine(vault_path=str(tmp_path))
        assert engine.backup_enabled is True

    def test_backup_enabled_can_disable(self, tmp_path):
        engine = LinkInsertionEngine(vault_path=str(tmp_path), backup_enabled=False)
        assert engine.backup_enabled is False

    def test_has_insert_suggestions_into_note(self):
        assert callable(
            getattr(LinkInsertionEngine, "insert_suggestions_into_note", None)
        )

    def test_has_insert_multiple_suggestions(self):
        assert callable(
            getattr(LinkInsertionEngine, "insert_multiple_suggestions", None)
        )

    def test_has_preview_changes(self):
        assert callable(getattr(LinkInsertionEngine, "preview_changes", None))


# ---------------------------------------------------------------------------
# UndoManager — interface
# ---------------------------------------------------------------------------


class TestUndoManagerInterface:
    def test_importable(self):
        assert UndoManager is not None

    def test_init_default(self):
        mgr = UndoManager()
        assert mgr is not None

    def test_init_custom_history(self):
        mgr = UndoManager(max_history=10)
        assert mgr._max_history == 10

    def test_history_empty_on_init(self):
        mgr = UndoManager()
        assert mgr.history_size() == 0

    def test_can_undo_false_when_empty(self):
        mgr = UndoManager()
        assert mgr.can_undo() is False

    def test_record_insertion_increases_history(self):
        mgr = UndoManager()
        mgr.record_insertion({"note": "test.md", "backup": "/tmp/backup"})
        assert mgr.history_size() == 1
        assert mgr.can_undo() is True


# ---------------------------------------------------------------------------
# link_insertion_utils — interface
# ---------------------------------------------------------------------------


class TestInsertionResult:
    def test_importable(self):
        assert InsertionResult is not None

    def test_instantiates(self):
        result = InsertionResult(success=True, insertions_made=1)
        assert result.success is True
        assert result.insertions_made == 1


class TestSafetyBackupManager:
    def test_importable(self):
        assert SafetyBackupManager is not None

    def test_init_with_vault_path(self, tmp_path):
        mgr = SafetyBackupManager(tmp_path)
        assert mgr is not None


class TestSmartInsertionProcessor:
    def test_importable(self):
        assert SmartInsertionProcessor is not None

    def test_init_no_args(self):
        proc = SmartInsertionProcessor()
        assert proc is not None


class TestContentValidator:
    def test_importable(self):
        assert ContentValidator is not None

    def test_init_with_vault_path(self, tmp_path):
        v = ContentValidator(tmp_path)
        assert v is not None


class TestBatchInsertionOrchestrator:
    def test_importable(self):
        assert BatchInsertionOrchestrator is not None

    def test_init_no_args(self):
        orch = BatchInsertionOrchestrator()
        assert orch is not None


class TestLocationDetectionEnhancer:
    def test_importable(self):
        assert LocationDetectionEnhancer is not None

    def test_init_no_args(self):
        enh = LocationDetectionEnhancer()
        assert enh is not None


# ---------------------------------------------------------------------------
# RealConnectionIntegrationEngine — interface
# ---------------------------------------------------------------------------


class TestRealConnectionIntegrationEngineInterface:
    def test_importable(self):
        assert RealConnectionIntegrationEngine is not None

    def test_init_with_vault_path(self, tmp_path):
        engine = RealConnectionIntegrationEngine(vault_path=str(tmp_path))
        assert engine is not None

    def test_init_defaults(self, tmp_path):
        engine = RealConnectionIntegrationEngine(vault_path=str(tmp_path))
        assert engine.similarity_threshold == 0.6
        assert engine.quality_threshold == 0.5
        assert engine.max_suggestions == 10

    def test_init_custom(self, tmp_path):
        engine = RealConnectionIntegrationEngine(
            vault_path=str(tmp_path),
            similarity_threshold=0.8,
            max_suggestions=5,
        )
        assert engine.similarity_threshold == 0.8
        assert engine.max_suggestions == 5


class TestCLIIntegrationOrchestrator:
    def test_importable(self):
        assert CLIIntegrationOrchestrator is not None


class TestProductionOptimizedProcessor:
    def test_importable(self):
        assert ProductionOptimizedProcessor is not None


# ---------------------------------------------------------------------------
# connection_integration_utils — interface
# ---------------------------------------------------------------------------


class TestConnectionObject:
    def test_importable(self):
        assert ConnectionObject is not None


class TestSimilarityResultConverter:
    def test_importable(self):
        assert SimilarityResultConverter is not None

    def test_init_no_args(self):
        c = SimilarityResultConverter()
        assert c is not None


class TestRealNoteLoader:
    def test_importable(self):
        assert RealNoteLoader is not None

    def test_init_with_vault_path(self, tmp_path):
        loader = RealNoteLoader(str(tmp_path))
        assert loader is not None


class TestPerformanceMonitor:
    def test_importable(self):
        assert PerformanceMonitor is not None

    def test_init_no_args(self):
        mon = PerformanceMonitor()
        assert mon is not None


class TestConnectionQualityAnalyzer:
    def test_importable(self):
        assert ConnectionQualityAnalyzer is not None

    def test_init_no_args(self):
        a = ConnectionQualityAnalyzer()
        assert a is not None


class TestRealConnectionProcessor:
    def test_importable(self):
        assert RealConnectionProcessor is not None


# ---------------------------------------------------------------------------
# OrphanRemediationCoordinator — interface
# ---------------------------------------------------------------------------


class TestOrphanRemediationCoordinatorInterface:
    def test_importable(self):
        assert OrphanRemediationCoordinator is not None

    def test_init_with_deps(self, tmp_path):
        mock_analytics = MagicMock()
        coord = OrphanRemediationCoordinator(
            base_dir=str(tmp_path), analytics_coordinator=mock_analytics
        )
        assert coord is not None

    def test_has_remediate_orphaned_notes(self):
        assert callable(
            getattr(OrphanRemediationCoordinator, "remediate_orphaned_notes", None)
        )

    def test_has_list_orphans_by_scope(self):
        assert callable(
            getattr(OrphanRemediationCoordinator, "list_orphans_by_scope", None)
        )

    def test_has_insert_bidirectional_links(self):
        assert callable(
            getattr(OrphanRemediationCoordinator, "insert_bidirectional_links", None)
        )


# ---------------------------------------------------------------------------
# Module boundary — no circular imports
# ---------------------------------------------------------------------------


class TestModuleBoundary:
    def test_no_llm_attribute_on_link_insertion_engine(self, tmp_path):
        """connections_insertion must not hold a top-level LLM client."""
        engine = LinkInsertionEngine(vault_path=str(tmp_path))
        assert not hasattr(engine, "ollama_client")
        assert not hasattr(engine, "llm_client")
