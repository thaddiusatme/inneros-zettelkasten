# Re-export shim — all type aliases now live in llm_client.py
from .llm_client import (
    AnalyticsResult,
    AIEnhancementResult,
    ConnectionResult,
    WorkflowResult,
    ConfigDict,
    QualityMetrics,
    LinkSuggestion,
    LinkFeedback,
    NoteMetadata,
    NoteInfo,
    WorkflowReport,
    EnhancedMetrics,
    PromotionCandidate,
    ReviewCandidate,
)

__all__ = [
    "AnalyticsResult",
    "AIEnhancementResult",
    "ConnectionResult",
    "WorkflowResult",
    "ConfigDict",
    "QualityMetrics",
    "LinkSuggestion",
    "LinkFeedback",
    "NoteMetadata",
    "NoteInfo",
    "WorkflowReport",
    "EnhancedMetrics",
    "PromotionCandidate",
    "ReviewCandidate",
]
