"""
media — atomic image processing and integrity monitoring for Zettelkasten.

Consolidates safe_image_processor.py, safe_image_processor_utils.py,
safe_image_processing_coordinator.py, image_integrity_monitor.py,
image_integrity_utils.py (issue #120).

Atomic image operations with guaranteed rollback. Fully isolated from the
note AI pipeline. Monitors image integrity through workflow steps.

Import boundary: no imports from enrichment, lifecycle, connections, or batch.
"""

from .safe_image_processor import (
    ProcessingResult,
    BackupIntegrityCheck,
    ImageBackupSession,
    SafeImageProcessor,
    AtomicFileOperations,
    WorkflowSafetyManager,
    ConcurrentProcessingGuard,
)
from .safe_image_processor_utils import (
    BackupMetadata,
    AtomicOperationResult,
    ImageBackupManager,
    AtomicOperationEngine,
    ImageExtractor,
    SessionManager,
    ProcessingResultBuilder,
)
from .safe_image_processing_coordinator import SafeImageProcessingCoordinator
from .image_integrity_monitor import WorkflowIntegrityResult, ImageIntegrityMonitor
from .image_integrity_utils import (
    ImageTrackingInfo,
    WorkflowCheckpoint,
    ImageRegistrationManager,
    WorkflowStepTracker,
    AuditReportGenerator,
    IntegrityValidationEngine,
    PerformanceOptimizer,
)

__all__ = [
    # safe_image_processor
    "ProcessingResult",
    "BackupIntegrityCheck",
    "ImageBackupSession",
    "SafeImageProcessor",
    "AtomicFileOperations",
    "WorkflowSafetyManager",
    "ConcurrentProcessingGuard",
    # safe_image_processor_utils
    "BackupMetadata",
    "AtomicOperationResult",
    "ImageBackupManager",
    "AtomicOperationEngine",
    "ImageExtractor",
    "SessionManager",
    "ProcessingResultBuilder",
    # safe_image_processing_coordinator
    "SafeImageProcessingCoordinator",
    # image_integrity_monitor
    "WorkflowIntegrityResult",
    "ImageIntegrityMonitor",
    # image_integrity_utils
    "ImageTrackingInfo",
    "WorkflowCheckpoint",
    "ImageRegistrationManager",
    "WorkflowStepTracker",
    "AuditReportGenerator",
    "IntegrityValidationEngine",
    "PerformanceOptimizer",
]
