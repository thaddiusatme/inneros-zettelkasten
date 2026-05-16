# Compatibility shim — LinkSuggestion, LinkSuggestionEngine, and QualityScore now live in connections_insertion.py
from .connections_insertion import LinkSuggestion, LinkSuggestionEngine, QualityScore

__all__ = ["LinkSuggestion", "LinkSuggestionEngine", "QualityScore"]
