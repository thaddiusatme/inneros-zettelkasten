# Compatibility shim — safe_image_processor_utils classes now live in media.py
from .media import (
    BackupMetadata,
    AtomicOperationResult,
    ImageBackupManager,
    AtomicOperationEngine,
    ImageExtractor,
    SessionManager,
    ProcessingResultBuilder,
)

__all__ = [
    "BackupMetadata",
    "AtomicOperationResult",
    "ImageBackupManager",
    "AtomicOperationEngine",
    "ImageExtractor",
    "SessionManager",
    "ProcessingResultBuilder",
]
