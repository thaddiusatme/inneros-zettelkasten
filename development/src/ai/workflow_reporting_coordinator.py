# Compatibility shim — WorkflowReportingCoordinator now lives in batch.py
from .batch import WorkflowReportingCoordinator

__all__ = ["WorkflowReportingCoordinator"]
