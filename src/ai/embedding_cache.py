"""
Embedding cache for improved performance in connection discovery.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from .ollama_client import OllamaClient


class EmbeddingCache:
    """Cache for text embeddings to improve performance."""
    
    def __init__(self, cache_dir: str = ".embedding_cache", max_cache_size: int = 1000):
        """
        Initialize embedding cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_cache_size: Maximum number of cached embeddings
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_cache_size = max_cache_size
        self.client = OllamaClient()
        
        # Load cache index
        self.index_file = self.cache_dir / "index.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict:
        """Load cache index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"entries": {}, "access_order": []}
    
    def _save_cache_index(self):
        """Save cache index to disk."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception:
            pass
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    def _get_cache_file(self, text_hash: str) -> Path:
        """Get cache file path for text hash."""
        return self.cache_dir / f"{text_hash}.json"
    
    def _cleanup_cache(self):
        """Remove oldest cache entries if over limit."""
        entries = self.cache_index["entries"]
        access_order = self.cache_index["access_order"]
        
        while len(entries) > self.max_cache_size:
            # Remove oldest entry
            oldest_hash = access_order.pop(0)
            if oldest_hash in entries:
                cache_file = self._get_cache_file(oldest_hash)
                cache_file.unlink(missing_ok=True)
                del entries[oldest_hash]
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for text, using cache if available.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Embedding vector or None if not cached
        """
        text_hash = self._get_text_hash(text)
        
        # Check if in cache
        if text_hash in self.cache_index["entries"]:
            cache_file = self._get_cache_file(text_hash)
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    # Update access order
                    access_order = self.cache_index["access_order"]
                    if text_hash in access_order:
                        access_order.remove(text_hash)
                    access_order.append(text_hash)
                    
                    return data["embedding"]
                except Exception:
                    # Remove corrupted cache entry
                    self._remove_cache_entry(text_hash)
        
        return None
    
    def store_embedding(self, text: str, embedding: List[float]):
        """
        Store embedding in cache.
        
        Args:
            text: Original text
            embedding: Embedding vector
        """
        text_hash = self._get_text_hash(text)
        cache_file = self._get_cache_file(text_hash)
        
        try:
            # Store embedding
            cache_data = {
                "text_hash": text_hash,
                "text_length": len(text),
                "embedding": embedding
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            # Update index
            self.cache_index["entries"][text_hash] = {
                "file": cache_file.name,
                "text_length": len(text)
            }
            
            # Update access order
            access_order = self.cache_index["access_order"]
            if text_hash in access_order:
                access_order.remove(text_hash)
            access_order.append(text_hash)
            
            # Cleanup if needed
            self._cleanup_cache()
            
            # Save index
            self._save_cache_index()
            
        except Exception:
            pass
    
    def _remove_cache_entry(self, text_hash: str):
        """Remove cache entry."""
        if text_hash in self.cache_index["entries"]:
            cache_file = self._get_cache_file(text_hash)
            cache_file.unlink(missing_ok=True)
            del self.cache_index["entries"][text_hash]
            
            access_order = self.cache_index["access_order"]
            if text_hash in access_order:
                access_order.remove(text_hash)
    
    def get_or_generate_embedding(self, text: str) -> List[float]:
        """
        Get embedding from cache or generate new one.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        # Try cache first
        cached_embedding = self.get_embedding(text)
        if cached_embedding is not None:
            return cached_embedding
        
        # Generate new embedding
        if not self.client.health_check():
            raise Exception("Ollama service is not available")
        
        embedding = self.client.generate_embedding(text)
        
        # Store in cache
        self.store_embedding(text, embedding)
        
        return embedding
    
    def clear_cache(self):
        """Clear all cached embeddings."""
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != "index.json":
                cache_file.unlink()
        
        self.cache_index = {"entries": {}, "access_order": []}
        self._save_cache_index()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache_index["entries"]),
            "max_size": self.max_cache_size,
            "cache_dir": str(self.cache_dir),
            "disk_usage_mb": sum(
                f.stat().st_size for f in self.cache_dir.glob("*.json")
            ) / (1024 * 1024)
        }
