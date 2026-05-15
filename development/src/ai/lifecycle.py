"""
lifecycle — note state transitions and import management for Zettelkasten.

Consolidates note_lifecycle_manager.py, promotion_engine.py,
fleeting_note_coordinator.py, fleeting_analysis_coordinator.py,
review_triage_coordinator.py, import_manager.py, import_schema.py (issue #120).

Manages the full note lifecycle: fleeting → permanent → archive transitions,
promotion decisions, import ingestion, and review triage.

Import boundary: may import from llm_client and connections_discovery.
Does NOT import from enrichment, connections_insertion, or batch.
"""

from .note_lifecycle_manager import StatusTransition, NoteLifecycleManager
from .promotion_engine import PromotionEngine
from .fleeting_note_coordinator import FleetingNoteCoordinator
from .fleeting_analysis_coordinator import FleetingAnalysis, FleetingAnalysisCoordinator
from .review_triage_coordinator import ReviewTriageCoordinator
from .import_manager import CSVImportAdapter, JSONImportAdapter, NoteWriter
from .import_schema import ImportItem, validate_item

__all__ = [
    # note lifecycle
    "StatusTransition",
    "NoteLifecycleManager",
    # promotion
    "PromotionEngine",
    # fleeting coordination
    "FleetingNoteCoordinator",
    # fleeting analysis
    "FleetingAnalysis",
    "FleetingAnalysisCoordinator",
    # review triage
    "ReviewTriageCoordinator",
    # import
    "CSVImportAdapter",
    "JSONImportAdapter",
    "NoteWriter",
    # import schema
    "ImportItem",
    "validate_item",
]
