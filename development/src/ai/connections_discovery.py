"""
connections_discovery — semantic connection finding for Zettelkasten notes.

Consolidates connections.py + connection_coordinator.py (issue #120).
Pure compute: no filesystem writes. Takes a note corpus, returns ranked
similarity candidates. Filesystem mutations live in connections_insertion.py.

Import boundary: imports from llm_client only. Does NOT import from enrichment.
"""

import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .llm_client import OllamaClient, EmbeddingCache


class AIConnections:
    """Discovers semantic connections between notes using AI embeddings."""

    def __init__(
        self,
        similarity_threshold: float = 0.7,
        max_suggestions: int = 5,
        config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ):
        self.ollama_client = OllamaClient(config=config)
        self.similarity_threshold = similarity_threshold
        self.max_suggestions = max_suggestions
        self.use_cache = use_cache
        self.embedding_cache = EmbeddingCache() if use_cache else None

    def find_similar_notes(
        self, target_note: str, note_corpus: Dict[str, str]
    ) -> List[Tuple[str, float]]:
        """Return (filename, score) pairs above threshold, sorted descending."""
        if not note_corpus:
            return []

        target_content = self._extract_content(target_note)
        if not target_content.strip():
            return []

        similarities = []
        for filename, content in note_corpus.items():
            note_content = self._extract_content(content)
            if not note_content.strip():
                continue
            try:
                score = self._calculate_semantic_similarity(
                    target_content, note_content
                )
            except Exception:
                score = self._simple_text_similarity(target_content, note_content)
            if score >= self.similarity_threshold:
                similarities.append((filename, score))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[: self.max_suggestions]

    def suggest_links(
        self, target_note: str, note_corpus: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Return link suggestions with similarity metadata."""
        return [
            {
                "filename": f,
                "similarity": s,
                "reason": f"High semantic similarity ({s:.0%})",
            }
            for f, s in self.find_similar_notes(target_note, note_corpus)
        ]

    def build_connection_map(
        self, note_corpus: Dict[str, str]
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Return full pairwise connection map for all notes in corpus."""
        return {
            filename: self.find_similar_notes(
                content,
                {f: c for f, c in note_corpus.items() if f != filename},
            )
            for filename, content in note_corpus.items()
        }

    def _extract_content(self, note_content: str) -> str:
        content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", note_content, flags=re.DOTALL)
        content = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", content)
        content = re.sub(r"\[\[([^\]]+)\]\]", r"\1", content)
        content = re.sub(r"!\[\[[^\]]+\]\]", "", content)
        return content.strip()

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        try:
            e1 = self._generate_ollama_embedding(text1)
            e2 = self._generate_ollama_embedding(text2)
            return max(0.0, min(1.0, self._cosine_similarity(e1, e2)))
        except Exception:
            return self._simple_text_similarity(text1, text2)

    def _generate_ollama_embedding(self, text: str) -> List[float]:
        if self.embedding_cache:
            try:
                return self.embedding_cache.get_or_generate_embedding(text)
            except Exception as e:
                raise Exception(f"Failed to generate embedding: {e}")
        if not self.ollama_client.health_check():
            raise Exception("Ollama service is not available")
        try:
            return self.ollama_client.generate_embedding(text)
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {e}")

    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        w1 = set(self._normalize_text(text1).split())
        w2 = set(self._normalize_text(text2).split())
        if not w1 or not w2:
            return 0.0
        return len(w1 & w2) / len(w1 | w2)

    def _cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        if not vector1 or not vector2 or len(vector1) != len(vector2):
            return 0.0
        dot = sum(a * b for a, b in zip(vector1, vector2))
        mag1 = math.sqrt(sum(a * a for a in vector1))
        mag2 = math.sqrt(sum(b * b for b in vector2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)


class ConnectionCoordinator:
    """Coordinates connection discovery across a note corpus directory."""

    def __init__(
        self, base_directory: str, min_similarity: float = 0.7, max_suggestions: int = 5
    ):
        self.base_directory = base_directory
        self.base_dir = Path(base_directory)
        self.min_similarity = min_similarity
        self.max_suggestions = max_suggestions
        self.connections = AIConnections(
            similarity_threshold=min_similarity, max_suggestions=max_suggestions
        )
        self._corpus_cache: Dict[str, Dict[str, str]] = {}
        self._total_discoveries = 0
        self._total_similarity_sum = 0.0

    def load_corpus(self, directory: Path) -> Dict[str, str]:
        """Load all .md files from directory into a filename→content dict."""
        if not directory.exists():
            return {}
        corpus = {}
        for md_file in directory.glob("*.md"):
            try:
                corpus[md_file.name] = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
        self._corpus_cache[str(directory)] = corpus
        return corpus

    def discover_connections(
        self, target_content: str, corpus_dir: Optional[Path] = None
    ) -> List[Dict]:
        """Discover semantically similar notes for target_content."""
        if not target_content:
            return []
        if corpus_dir is None:
            corpus_dir = self.base_dir / "Permanent Notes"
        corpus = self.load_corpus(corpus_dir)
        if not corpus:
            return []
        try:
            similar = self.connections.find_similar_notes(target_content, corpus)
            results = []
            for filename, similarity in similar:
                results.append({"filename": filename, "similarity": similarity})
                self._total_discoveries += 1
                self._total_similarity_sum += similarity
            return results
        except Exception:
            return []

    def validate_connections(self, connections: List[Dict]) -> List[Dict]:
        """Deduplicate by filename, keep highest similarity, filter below threshold."""
        if not connections:
            return []
        seen: Dict[str, float] = {}
        validated = []
        for conn in connections:
            filename = conn.get("filename")
            similarity = conn.get("similarity", 0.0)
            if not filename:
                continue
            if similarity < self.min_similarity:
                continue
            if filename not in seen or similarity > seen[filename]:
                seen[filename] = similarity
                validated = [c for c in validated if c["filename"] != filename]
                validated.append(conn)
        validated.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)
        return validated

    def get_connection_statistics(self) -> Dict:
        """Return total discoveries and average similarity."""
        avg = (
            self._total_similarity_sum / self._total_discoveries
            if self._total_discoveries
            else 0.0
        )
        return {"total_discoveries": self._total_discoveries, "average_similarity": avg}

    def clear_cache(self):
        """Clear the loaded corpus cache."""
        self._corpus_cache.clear()
