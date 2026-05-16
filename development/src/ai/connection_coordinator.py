# Compatibility shim — ConnectionCoordinator now lives in connections_discovery.py
from .connections_discovery import ConnectionCoordinator

__all__ = ["ConnectionCoordinator"]
