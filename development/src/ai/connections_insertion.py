"""
connections_insertion — filesystem link mutations for Zettelkasten notes.

Consolidates link_insertion_engine.py, link_insertion_utils.py,
real_connection_integration_engine.py, connection_integration_utils.py,
orphan_remediation_coordinator.py (issue #120).

Filesystem I/O with rollback. Takes suggestions from connections_discovery
and writes wiki-links into note files. Pure compute lives in
connections_discovery.py; mutations live here.

Import boundary: may import from connections_discovery and llm_client.
Does NOT import from enrichment, lifecycle, or batch.
"""

from .link_insertion_engine import LinkInsertionEngine, UndoManager
from .link_insertion_utils import (
    InsertionResult,
    SafetyBackupManager,
    SmartInsertionProcessor,
    ContentValidator,
    BatchInsertionOrchestrator,
    LocationDetectionEnhancer,
)
from .real_connection_integration_engine import (
    RealConnectionIntegrationEngine,
    CLIIntegrationOrchestrator,
    ProductionOptimizedProcessor,
)
from .connection_integration_utils import (
    ConnectionObject,
    SimilarityResultConverter,
    RealNoteLoader,
    PerformanceMonitor,
    ConnectionQualityAnalyzer,
    RealConnectionProcessor,
)
from .orphan_remediation_coordinator import OrphanRemediationCoordinator

__all__ = [
    # link insertion
    "LinkInsertionEngine",
    "UndoManager",
    "InsertionResult",
    "SafetyBackupManager",
    "SmartInsertionProcessor",
    "ContentValidator",
    "BatchInsertionOrchestrator",
    "LocationDetectionEnhancer",
    # real connection integration
    "RealConnectionIntegrationEngine",
    "CLIIntegrationOrchestrator",
    "ProductionOptimizedProcessor",
    # connection integration utilities
    "ConnectionObject",
    "SimilarityResultConverter",
    "RealNoteLoader",
    "PerformanceMonitor",
    "ConnectionQualityAnalyzer",
    "RealConnectionProcessor",
    # orphan remediation
    "OrphanRemediationCoordinator",
]
