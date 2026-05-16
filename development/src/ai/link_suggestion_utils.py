# Compatibility shim — link_suggestion_utils classes now live in connections_insertion.py
from .connections_insertion import (
    QualityScore,
    LinkTextGenerator,
    LinkQualityAssessor,
    InsertionContextDetector,
    SuggestionBatchProcessor,
)

__all__ = [
    "QualityScore",
    "LinkTextGenerator",
    "LinkQualityAssessor",
    "InsertionContextDetector",
    "SuggestionBatchProcessor",
]
