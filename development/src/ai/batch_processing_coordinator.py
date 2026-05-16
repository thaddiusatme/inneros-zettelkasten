# Compatibility shim — BatchProcessingCoordinator now lives in batch.py
from .batch import BatchProcessingCoordinator

__all__ = ["BatchProcessingCoordinator"]
