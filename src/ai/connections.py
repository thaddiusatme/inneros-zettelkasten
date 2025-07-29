"""
AI-powered connection discovery and semantic similarity for notes.
Finds related notes and suggests links based on content analysis.
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from .ollama_client import OllamaClient
from .embedding_cache import EmbeddingCache


class AIConnections:
    """Discovers semantic connections between notes using AI analysis."""
    
    def __init__(self, similarity_threshold: float = 0.7, max_suggestions: int = 5, config: Optional[Dict[str, Any]] = None, use_cache: bool = True):
        """
        Initialize AI connections with configuration.
        
        Args:
            similarity_threshold: Minimum similarity score for suggestions
            max_suggestions: Maximum number of suggestions to return
            config: Optional configuration for Ollama client
            use_cache: Whether to use embedding cache for performance
        """
        self.ollama_client = OllamaClient(config=config)
        self.similarity_threshold = similarity_threshold
        self.max_suggestions = max_suggestions
        self.use_cache = use_cache
        
        # Initialize embedding cache if enabled
        if use_cache:
            self.embedding_cache = EmbeddingCache()
        else:
            self.embedding_cache = None
    
    def find_similar_notes(self, target_note: str, note_corpus: Dict[str, str]) -> List[Tuple[str, float]]:
        """
        Find notes similar to the target note.
        
        Args:
            target_note: Content of the note to find similarities for
            note_corpus: Dictionary mapping filenames to note content
            
        Returns:
            List of tuples (filename, similarity_score) sorted by similarity
        """
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
                similarity = self._calculate_semantic_similarity(target_content, note_content)
                if similarity >= self.similarity_threshold:
                    similarities.append((filename, similarity))
            except Exception:
                # Fall back to simple similarity if semantic analysis fails
                similarity = self._simple_text_similarity(target_content, note_content)
                if similarity >= self.similarity_threshold:
                    similarities.append((filename, similarity))
        
        # Sort by similarity score (descending) and limit results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:self.max_suggestions]
    
    def suggest_links(self, target_note: str, note_corpus: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Suggest links to related notes with explanations.
        
        Args:
            target_note: Content of the note to suggest links for
            note_corpus: Dictionary mapping filenames to note content
            
        Returns:
            List of link suggestions with metadata
        """
        similar_notes = self.find_similar_notes(target_note, note_corpus)
        
        suggestions = []
        for filename, similarity in similar_notes:
            suggestion = {
                "filename": filename,
                "similarity": similarity,
                "reason": f"High semantic similarity ({similarity:.0%})"
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def build_connection_map(self, note_corpus: Dict[str, str]) -> Dict[str, List[Tuple[str, float]]]:
        """
        Build a complete connection map for all notes in the corpus.
        
        Args:
            note_corpus: Dictionary mapping filenames to note content
            
        Returns:
            Dictionary mapping each filename to its similar notes
        """
        connection_map = {}
        
        for filename, content in note_corpus.items():
            # Create a corpus excluding the current note
            other_notes = {f: c for f, c in note_corpus.items() if f != filename}
            similar_notes = self.find_similar_notes(content, other_notes)
            connection_map[filename] = similar_notes
        
        return connection_map
    
    def _extract_content(self, note_content: str) -> str:
        """
        Extract main content from note, removing YAML frontmatter.
        
        Args:
            note_content: Raw note content
            
        Returns:
            Cleaned content without metadata
        """
        # Remove YAML frontmatter
        yaml_pattern = r'^---\s*\n.*?\n---\s*\n'
        content = re.sub(yaml_pattern, '', note_content, flags=re.DOTALL)
        return content.strip()
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity using AI embeddings.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            Similarity score between 0 and 1
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Generate embeddings for both texts
            embedding1 = self._generate_ollama_embedding(text1)
            embedding2 = self._generate_ollama_embedding(text2)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(embedding1, embedding2)
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
        
        except Exception as e:
            # Fall back to simple text similarity
            return self._simple_text_similarity(text1, text2)
    
    def _generate_ollama_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Ollama API with optional caching.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector
            
        Raises:
            Exception: If Ollama service is unavailable or API call fails
        """
        # Use cache if available
        if self.embedding_cache:
            try:
                return self.embedding_cache.get_or_generate_embedding(text)
            except Exception as e:
                raise Exception(f"Failed to generate embedding: {str(e)}")
        
        # Fallback to direct API call
        if not self.ollama_client.health_check():
            raise Exception("Ollama service is not available")
        
        try:
            embedding = self.ollama_client.generate_embedding(text)
            return embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity using word overlap.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            Similarity score between 0 and 1
        """
        # Normalize texts
        norm_text1 = self._normalize_text(text1)
        norm_text2 = self._normalize_text(text2)
        
        if not norm_text1 or not norm_text2:
            return 0.0
        
        # Get word sets
        words1 = set(norm_text1.split())
        words2 = set(norm_text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vector1: First vector
            vector2: Second vector
            
        Returns:
            Cosine similarity score
        """
        if not vector1 or not vector2 or len(vector1) != len(vector2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(b * b for b in vector2))
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
