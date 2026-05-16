# Compatibility shim — link_insertion_utils classes now live in connections_insertion.py
from .connections_insertion import (
    InsertionResult,
    SafetyBackupManager,
    SmartInsertionProcessor,
    ContentValidator,
    BatchInsertionOrchestrator,
    LocationDetectionEnhancer,
)

__all__ = [
    "InsertionResult",
    "SafetyBackupManager",
    "SmartInsertionProcessor",
    "ContentValidator",
    "BatchInsertionOrchestrator",
    "LocationDetectionEnhancer",
]
