# Re-export shim — OllamaClient now lives in llm_client.py
from .llm_client import OllamaClient

__all__ = ["OllamaClient"]
