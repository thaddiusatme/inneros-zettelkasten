# Compatibility shim — classes now live in connections_insertion.py
from .connections_insertion import (
    RealConnectionIntegrationEngine,
    CLIIntegrationOrchestrator,
    ProductionOptimizedProcessor,
)

__all__ = [
    "RealConnectionIntegrationEngine",
    "CLIIntegrationOrchestrator",
    "ProductionOptimizedProcessor",
]
