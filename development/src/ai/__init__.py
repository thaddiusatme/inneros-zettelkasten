"""
AI module for InnerOS Zettelkasten.
Provides intelligent tagging, summarization, connections, enhancement, analytics, and workflow management.
"""

from .tagger import AITagger
from .summarizer import AISummarizer
from .connections import AIConnections
from .enhancer import AIEnhancer
from .ollama_client import OllamaClient
from .analytics import NoteAnalytics
from .workflow_manager import WorkflowManager
from .embedding_cache import EmbeddingCache
from .auto_processor import AutoProcessor, NoteProcessor, NoteWatcher

__all__ = [
    'AITagger',
    'AISummarizer', 
    'AIConnections',
    'AIEnhancer',
    'OllamaClient',
    'NoteAnalytics',
    'WorkflowManager',
    'EmbeddingCache',
    'AutoProcessor',
    'NoteProcessor',
    'NoteWatcher'
]
