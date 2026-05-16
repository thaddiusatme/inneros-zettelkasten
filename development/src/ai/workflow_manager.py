# Compatibility shim — WorkflowManager now lives in batch.py
from .batch import WorkflowManager, SafeWorkflowManager

__all__ = ["WorkflowManager", "SafeWorkflowManager"]
