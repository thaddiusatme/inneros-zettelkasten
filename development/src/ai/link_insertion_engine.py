# Compatibility shim — LinkInsertionEngine and UndoManager now live in connections_insertion.py
from .connections_insertion import LinkInsertionEngine, UndoManager

__all__ = ["LinkInsertionEngine", "UndoManager"]
