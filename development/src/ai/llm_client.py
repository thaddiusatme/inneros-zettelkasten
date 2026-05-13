"""
llm_client — base LLM I/O layer for InnerOS.

Consolidates three former modules:
  - ollama_client.py  → OllamaClient
  - embedding_cache.py → EmbeddingCache
  - types.py          → shared type aliases

Nothing in this module imports from any other src.ai module.
All other modules that need LLM access import from here.
"""

import hashlib
import json
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Shared type aliases
# ---------------------------------------------------------------------------

AnalyticsResult = Dict[str, Any]
AIEnhancementResult = Dict[str, Any]
ConnectionResult = List[Dict[str, Any]]
WorkflowResult = Dict[str, Any]
ConfigDict = Dict[str, Any]
QualityMetrics = Dict[str, float]
LinkSuggestion = Dict[str, Any]
LinkFeedback = Dict[str, Any]
NoteMetadata = Dict[str, Any]
NoteInfo = Dict[str, Any]
WorkflowReport = Dict[str, Any]
EnhancedMetrics = Dict[str, Any]
PromotionCandidate = Dict[str, Any]
ReviewCandidate = List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# OllamaClient
# ---------------------------------------------------------------------------


class OllamaClient:
    """Client for interacting with the Ollama local AI service."""

    def __init__(self, config: Optional[ConfigDict] = None):
        if config is None:
            config = {}
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.timeout = config.get("timeout", 30)
        self.model = config.get("model", "gemma4:latest")

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def is_model_available(self, model_name: str) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m.get("name") == model_name for m in models)
            return False
        except (requests.ConnectionError, requests.Timeout):
            return False

    def generate_completion(
        self, prompt: str, system_prompt: str = "", max_tokens: int = -1
    ) -> str:
        """Generate text via Ollama. max_tokens=-1 omits num_predict (required for thinking models)."""
        try:
            options: Dict[str, Any] = {"temperature": 0.3}
            if max_tokens != -1:
                options["num_predict"] = max_tokens

            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": options,
            }
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            raise Exception(f"API error: {response.status_code} - {response.text}")
        except requests.ConnectionError:
            raise Exception("Failed to connect to Ollama service")
        except requests.Timeout:
            raise Exception("Request to Ollama service timed out")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

    def generate(
        self, prompt: str, system_prompt: str = "", max_tokens: int = -1
    ) -> str:
        """Alias for generate_completion."""
        return self.generate_completion(prompt, system_prompt, max_tokens)

    def generate_embedding(self, text: str) -> List[float]:
        try:
            payload = {"model": self.model, "prompt": text}
            response = requests.post(
                f"{self.base_url}/api/embeddings", json=payload, timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
            raise Exception(
                f"Embedding API error: {response.status_code} - {response.text}"
            )
        except requests.ConnectionError:
            raise Exception("Failed to connect to Ollama service")
        except requests.Timeout:
            raise Exception("Request to Ollama service timed out")
        except Exception as e:
            known = ("Embedding API error", "Failed to connect", "timed out")
            if any(k in str(e) for k in known):
                raise
            raise Exception(f"Unexpected error generating embedding: {e}")


# ---------------------------------------------------------------------------
# EmbeddingCache
# ---------------------------------------------------------------------------


class EmbeddingCache:
    """Disk-backed LRU cache for text embeddings."""

    def __init__(self, cache_dir: str = ".embedding_cache", max_cache_size: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_cache_size = max_cache_size
        self.client = OllamaClient()
        self.index_file = self.cache_dir / "index.json"
        self.cache_index = self._load_index()

    def _load_index(self) -> Dict:
        if self.index_file.exists():
            try:
                with open(self.index_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"entries": {}, "access_order": []}

    def _save_index(self):
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception:
            pass

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _cache_file(self, text_hash: str) -> Path:
        return self.cache_dir / f"{text_hash}.json"

    def _evict(self):
        entries = self.cache_index["entries"]
        order = self.cache_index["access_order"]
        while len(entries) > self.max_cache_size:
            oldest = order.pop(0)
            if oldest in entries:
                self._cache_file(oldest).unlink(missing_ok=True)
                del entries[oldest]

    def _remove(self, text_hash: str):
        entries = self.cache_index["entries"]
        if text_hash in entries:
            self._cache_file(text_hash).unlink(missing_ok=True)
            del entries[text_hash]
        order = self.cache_index["access_order"]
        if text_hash in order:
            order.remove(text_hash)

    def get_embedding(self, text: str) -> Optional[List[float]]:
        h = self._hash(text)
        if h not in self.cache_index["entries"]:
            return None
        f = self._cache_file(h)
        if not f.exists():
            return None
        try:
            with open(f) as fp:
                data = json.load(fp)
            order = self.cache_index["access_order"]
            if h in order:
                order.remove(h)
            order.append(h)
            return data["embedding"]
        except Exception:
            self._remove(h)
            return None

    def store_embedding(self, text: str, embedding: List[float]):
        h = self._hash(text)
        f = self._cache_file(h)
        try:
            with open(f, "w") as fp:
                json.dump(
                    {"text_hash": h, "text_length": len(text), "embedding": embedding},
                    fp,
                )
            self.cache_index["entries"][h] = {"file": f.name, "text_length": len(text)}
            order = self.cache_index["access_order"]
            if h in order:
                order.remove(h)
            order.append(h)
            self._evict()
            self._save_index()
        except Exception:
            pass

    def get_or_generate_embedding(self, text: str) -> List[float]:
        cached = self.get_embedding(text)
        if cached is not None:
            return cached
        if not self.client.health_check():
            raise Exception("Ollama service is not available")
        embedding = self.client.generate_embedding(text)
        self.store_embedding(text, embedding)
        return embedding

    def clear_cache(self):
        for f in self.cache_dir.glob("*.json"):
            if f.name != "index.json":
                f.unlink()
        self.cache_index = {"entries": {}, "access_order": []}
        self._save_index()

    def get_cache_stats(self) -> Dict:
        return {
            "total_entries": len(self.cache_index["entries"]),
            "max_size": self.max_cache_size,
            "cache_dir": str(self.cache_dir),
            "disk_usage_mb": sum(
                f.stat().st_size for f in self.cache_dir.glob("*.json")
            )
            / (1024 * 1024),
        }
