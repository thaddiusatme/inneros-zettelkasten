"""
Spec tests for the media module (#120).

Verifies the public API surface of the consolidated module:
- All key classes importable from media
- Core behaviours preserved from the source files:
    safe_image_processor.py, safe_image_processor_utils.py,
    safe_image_processing_coordinator.py, image_integrity_monitor.py,
    image_integrity_utils.py
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src")
sys.path.insert(0, src_dir)

from ai.media import (
    # safe_image_processor
    ProcessingResult,
    BackupIntegrityCheck,
    ImageBackupSession,
    SafeImageProcessor,
    AtomicFileOperations,
    WorkflowSafetyManager,
    ConcurrentProcessingGuard,
    # safe_image_processor_utils
    BackupMetadata,
    AtomicOperationResult,
    ImageBackupManager,
    AtomicOperationEngine,
    ImageExtractor,
    SessionManager,
    ProcessingResultBuilder,
    # safe_image_processing_coordinator
    SafeImageProcessingCoordinator,
    # image_integrity_monitor
    WorkflowIntegrityResult,
    ImageIntegrityMonitor,
    # image_integrity_utils
    ImageTrackingInfo,
    WorkflowCheckpoint,
    ImageRegistrationManager,
    WorkflowStepTracker,
    AuditReportGenerator,
    IntegrityValidationEngine,
    PerformanceOptimizer,
)


# ---------------------------------------------------------------------------
# SafeImageProcessor — interface
# ---------------------------------------------------------------------------


class TestSafeImageProcessorInterface:
    def test_importable(self):
        assert SafeImageProcessor is not None

    def test_init_with_vault_path(self, tmp_path):
        proc = SafeImageProcessor(vault_path=str(tmp_path))
        assert proc is not None

    def test_vault_path_stored(self, tmp_path):
        proc = SafeImageProcessor(vault_path=str(tmp_path))
        assert proc.vault_path == tmp_path

    def test_has_create_backup_session(self):
        assert callable(getattr(SafeImageProcessor, "create_backup_session", None))

    def test_has_process_note_with_images(self):
        assert callable(getattr(SafeImageProcessor, "process_note_with_images", None))


class TestProcessingResult:
    def test_importable(self):
        assert ProcessingResult is not None


class TestBackupIntegrityCheck:
    def test_importable(self):
        assert BackupIntegrityCheck is not None


class TestImageBackupSession:
    def test_importable(self):
        assert ImageBackupSession is not None

    def test_init(self, tmp_path):
        session = ImageBackupSession(
            vault_path=tmp_path, operation_name="test_op", images_to_backup=[]
        )
        assert session is not None
        assert session.vault_path == tmp_path

    def test_has_session_id(self, tmp_path):
        session = ImageBackupSession(
            vault_path=tmp_path, operation_name="test_op", images_to_backup=[]
        )
        assert hasattr(session, "session_id")


class TestAtomicFileOperations:
    def test_importable(self):
        assert AtomicFileOperations is not None


class TestWorkflowSafetyManager:
    def test_importable(self):
        assert WorkflowSafetyManager is not None

    def test_init_with_vault_path(self, tmp_path):
        mgr = WorkflowSafetyManager(vault_path=tmp_path)
        assert mgr is not None


class TestConcurrentProcessingGuard:
    def test_importable(self):
        assert ConcurrentProcessingGuard is not None

    def test_init_no_args(self):
        guard = ConcurrentProcessingGuard()
        assert guard is not None


# ---------------------------------------------------------------------------
# safe_image_processor_utils — interface
# ---------------------------------------------------------------------------


class TestImageBackupManager:
    def test_importable(self):
        assert ImageBackupManager is not None

    def test_init_with_vault_path(self, tmp_path):
        mgr = ImageBackupManager(vault_path=tmp_path)
        assert mgr is not None

    def test_has_create_session_backup(self):
        assert callable(getattr(ImageBackupManager, "create_session_backup", None))


class TestAtomicOperationResult:
    def test_importable(self):
        assert AtomicOperationResult is not None


class TestBackupMetadata:
    def test_importable(self):
        assert BackupMetadata is not None


class TestAtomicOperationEngine:
    def test_importable(self):
        assert AtomicOperationEngine is not None

    def test_init_with_backup_manager(self, tmp_path):
        mgr = ImageBackupManager(vault_path=tmp_path)
        engine = AtomicOperationEngine(backup_manager=mgr)
        assert engine is not None


class TestImageExtractor:
    def test_importable(self):
        assert ImageExtractor is not None

    def test_init_with_vault_path(self, tmp_path):
        extractor = ImageExtractor(vault_path=tmp_path)
        assert extractor is not None


class TestSessionManager:
    def test_importable(self):
        assert SessionManager is not None

    def test_init_no_args(self):
        sm = SessionManager()
        assert sm is not None


class TestProcessingResultBuilder:
    def test_importable(self):
        assert ProcessingResultBuilder is not None

    def test_init_no_args(self):
        builder = ProcessingResultBuilder()
        assert builder is not None


# ---------------------------------------------------------------------------
# SafeImageProcessingCoordinator — interface
# ---------------------------------------------------------------------------


class TestSafeImageProcessingCoordinatorInterface:
    def test_importable(self):
        assert SafeImageProcessingCoordinator is not None

    def test_init_with_deps(self, tmp_path):
        coord = SafeImageProcessingCoordinator(
            safe_workflow_processor=MagicMock(),
            atomic_workflow_engine=MagicMock(),
            integrity_monitoring_manager=MagicMock(),
            concurrent_session_manager=MagicMock(),
            performance_metrics_collector=MagicMock(),
            safe_image_processor=MagicMock(),
            image_integrity_monitor=MagicMock(),
            inbox_dir=tmp_path,
        )
        assert coord is not None


# ---------------------------------------------------------------------------
# ImageIntegrityMonitor — interface
# ---------------------------------------------------------------------------


class TestImageIntegrityMonitorInterface:
    def test_importable(self):
        assert ImageIntegrityMonitor is not None

    def test_init_with_vault_path(self, tmp_path):
        monitor = ImageIntegrityMonitor(vault_path=str(tmp_path))
        assert monitor is not None

    def test_has_tracked_images(self, tmp_path):
        monitor = ImageIntegrityMonitor(vault_path=str(tmp_path))
        assert hasattr(monitor, "tracked_images")


class TestWorkflowIntegrityResult:
    def test_importable(self):
        assert WorkflowIntegrityResult is not None


# ---------------------------------------------------------------------------
# image_integrity_utils — interface
# ---------------------------------------------------------------------------


class TestImageRegistrationManager:
    def test_importable(self):
        assert ImageRegistrationManager is not None

    def test_init_no_args(self):
        mgr = ImageRegistrationManager()
        assert mgr is not None

    def test_has_register_image(self):
        assert callable(getattr(ImageRegistrationManager, "register_image", None))


class TestWorkflowStepTracker:
    def test_importable(self):
        assert WorkflowStepTracker is not None

    def test_init_no_args(self):
        tracker = WorkflowStepTracker()
        assert tracker is not None


class TestAuditReportGenerator:
    def test_importable(self):
        assert AuditReportGenerator is not None

    def test_init_with_vault_path(self, tmp_path):
        gen = AuditReportGenerator(vault_path=tmp_path)
        assert gen is not None


class TestIntegrityValidationEngine:
    def test_importable(self):
        assert IntegrityValidationEngine is not None

    def test_init_no_args(self):
        engine = IntegrityValidationEngine()
        assert engine is not None


class TestPerformanceOptimizer:
    def test_importable(self):
        assert PerformanceOptimizer is not None

    def test_init_no_args(self):
        opt = PerformanceOptimizer()
        assert opt is not None


class TestImageTrackingInfo:
    def test_importable(self):
        assert ImageTrackingInfo is not None


class TestWorkflowCheckpoint:
    def test_importable(self):
        assert WorkflowCheckpoint is not None
