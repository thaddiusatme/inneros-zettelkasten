# Compatibility shim — NoteProcessingCoordinator now lives in batch.py
from .batch import NoteProcessingCoordinator

__all__ = ["NoteProcessingCoordinator"]
