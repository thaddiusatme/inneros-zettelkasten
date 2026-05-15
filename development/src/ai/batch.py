"""
batch — user-invoked orchestration for multi-note workflows.

Consolidates workflow_manager, batch_processing_coordinator,
batch_inbox_processor, note_processing_coordinator,
workflow_integration_utils, and workflow_reporting_coordinator (issue #120).

Single import point for all batch/orchestration concerns. Does not own the
event loop — daemon/file-watching concerns are handled separately.

Import boundary: imports from enrichment, analytics, connections_discovery,
llm_client, and lifecycle modules. Does NOT import from the old split files
(tagger, summarizer, enhancer, connections, connection_coordinator).
"""

# ---------------------------------------------------------------------------
# Core orchestrator
# ---------------------------------------------------------------------------
from .workflow_manager import WorkflowManager, SafeWorkflowManager

# ---------------------------------------------------------------------------
# Coordinators
# ---------------------------------------------------------------------------
from .batch_processing_coordinator import BatchProcessingCoordinator
from .note_processing_coordinator import NoteProcessingCoordinator
from .workflow_reporting_coordinator import WorkflowReportingCoordinator

# ---------------------------------------------------------------------------
# Infrastructure utilities
# ---------------------------------------------------------------------------
from .workflow_integration_utils import (
    WorkflowProcessingResult,
    BatchProcessingStats,
    SafeWorkflowProcessor,
    AtomicWorkflowEngine,
    IntegrityMonitoringManager,
    ConcurrentSessionManager,
    PerformanceMetricsCollector,
)

# ---------------------------------------------------------------------------
# Batch inbox processor functions (called directly from Makefile)
# ---------------------------------------------------------------------------
from .batch_inbox_processor import (
    batch_process_unprocessed_inbox,
    is_note_eligible_for_processing,
    scan_eligible_notes,
    process_single_note,
)

__all__ = [
    # Core
    "WorkflowManager",
    "SafeWorkflowManager",
    # Coordinators
    "BatchProcessingCoordinator",
    "NoteProcessingCoordinator",
    "WorkflowReportingCoordinator",
    # Utilities
    "WorkflowProcessingResult",
    "BatchProcessingStats",
    "SafeWorkflowProcessor",
    "AtomicWorkflowEngine",
    "IntegrityMonitoringManager",
    "ConcurrentSessionManager",
    "PerformanceMetricsCollector",
    # Functions
    "batch_process_unprocessed_inbox",
    "is_note_eligible_for_processing",
    "scan_eligible_notes",
    "process_single_note",
]
