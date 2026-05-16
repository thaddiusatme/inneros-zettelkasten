# Compatibility shim — OrphanRemediationCoordinator now lives in connections_insertion.py
from .connections_insertion import OrphanRemediationCoordinator

__all__ = ["OrphanRemediationCoordinator"]
