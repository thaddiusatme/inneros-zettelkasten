# Compatibility shim — connection_integration_utils classes now live in connections_insertion.py
from .connections_insertion import (
    ConnectionObject,
    SimilarityResultConverter,
    RealNoteLoader,
    PerformanceMonitor,
    ConnectionQualityAnalyzer,
    RealConnectionProcessor,
)

__all__ = [
    "ConnectionObject",
    "SimilarityResultConverter",
    "RealNoteLoader",
    "PerformanceMonitor",
    "ConnectionQualityAnalyzer",
    "RealConnectionProcessor",
]
