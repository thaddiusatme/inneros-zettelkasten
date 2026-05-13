# Re-export shim — EmbeddingCache now lives in llm_client.py
from .llm_client import EmbeddingCache

__all__ = ["EmbeddingCache"]
