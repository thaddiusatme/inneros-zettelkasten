"""
AI package for InnerOS Zettelkasten.

Lightweight initialization to avoid eager imports that can break various
test environments (e.g., when tests add only the `src/` directory to sys.path).

Import submodules/classes directly where needed, e.g.:
    from ai.connections import AIConnections
    from ai.analytics import NoteAnalytics
"""

# Expose submodule names for convenience without importing them eagerly
__all__ = [
    # Primary consolidated modules (issue #120)
    "llm_client",
    "analytics",
    "enrichment",
    "connections_discovery",
    "connections_insertion",
    "lifecycle",
    "batch",
    "media",
    # Compatibility shims (re-export to old names)
    "ollama_client",
    "embedding_cache",
    "analytics_manager",
    "analytics_coordinator",
    "tagger",
    "summarizer",
    "enhancer",
    "ai_enhancement_manager",
    "connections",
    "connection_coordinator",
    "link_suggestion_utils",
    "link_suggestion_engine",
    "link_insertion_engine",
    "link_insertion_utils",
    "orphan_remediation_coordinator",
    "real_connection_integration_engine",
    "connection_integration_utils",
    "note_lifecycle_manager",
    "promotion_engine",
    "fleeting_note_coordinator",
    "fleeting_analysis_coordinator",
    "review_triage_coordinator",
    "workflow_manager",
    "batch_processing_coordinator",
    "note_processing_coordinator",
    "workflow_reporting_coordinator",
    "workflow_integration_utils",
    "batch_inbox_processor",
    "safe_image_processor",
    "safe_image_processor_utils",
    "safe_image_processing_coordinator",
    "image_integrity_utils",
    "image_integrity_monitor",
    # Always-shims
    "types",
    "metadata_repair_engine",
]
