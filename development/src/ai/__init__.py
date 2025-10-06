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
    'tagger',
    'summarizer',
    'connections',
    'enhancer',
    'ollama_client',
    'analytics',
    'workflow_manager',
    'embedding_cache',
    'auto_processor',
    'core_workflow_manager',
    'analytics_manager',
    'ai_enhancement_manager',
    'connection_manager',
]
