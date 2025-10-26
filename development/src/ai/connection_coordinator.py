"""
ConnectionCoordinator - Extracted from WorkflowManager god class (ADR-002 Phase 2).

Responsibilities:
- Load and cache note corpus from directories
- Discover semantic connections using AIConnections
- Format connection results for workflow integration
- Provide connection statistics and metrics

Single Responsibility: Connection discovery coordination
Target: ~200-300 LOC, <15 methods
"""

from pathlib import Path
from typing import Dict, List, Optional
from .connections import AIConnections


class ConnectionCoordinator:
    """
    Coordinates connection discovery between notes.
    
    Extracted from WorkflowManager to reduce god class complexity.
    Uses AIConnections for semantic similarity analysis.
    """

    def __init__(
        self,
        base_directory: str,
        min_similarity: float = 0.7,
        max_suggestions: int = 5
    ):
        """
        Initialize connection coordinator.
        
        Args:
            base_directory: Base directory of the Zettelkasten
            min_similarity: Minimum similarity threshold (0.0-1.0)
            max_suggestions: Maximum number of suggestions to return
        """
        self.base_dir = Path(base_directory)
        self.min_similarity = min_similarity
        self.max_suggestions = max_suggestions

        # Initialize AIConnections for semantic analysis
        self.connections = AIConnections(
            similarity_threshold=min_similarity,
            max_suggestions=max_suggestions
        )

        # Cache for loaded corpora
        self._corpus_cache: Dict[str, Dict[str, str]] = {}

        # Statistics tracking
        self._total_discoveries = 0
        self._total_similarity_sum = 0.0

    def load_corpus(self, directory: Path) -> Dict[str, str]:
        """
        Load all notes from a directory into a corpus.
        
        Extracted from WorkflowManager._load_notes_corpus()
        
        Args:
            directory: Directory containing markdown notes
            
        Returns:
            Dictionary mapping filenames to note content
        """
        corpus = {}

        if not directory.exists():
            return corpus

        for md_file in directory.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    corpus[md_file.name] = f.read()
            except Exception:
                # Skip files that can't be read
                continue

        # Cache the corpus
        cache_key = str(directory)
        self._corpus_cache[cache_key] = corpus

        return corpus

    def discover_connections(
        self,
        target_content: str,
        corpus_dir: Optional[Path] = None
    ) -> List[Dict]:
        """
        Discover semantic connections for target content.
        
        Uses AIConnections to find notes with semantic similarity above
        the configured threshold. Results are ranked by similarity score.
        
        Args:
            target_content: Content of the note to find connections for
            corpus_dir: Directory to search for connections (defaults to Permanent Notes/)
            
        Returns:
            List of connection dictionaries with filename and similarity:
            [{"filename": "note.md", "similarity": 0.85}, ...]
            
        Examples:
            >>> coordinator = ConnectionCoordinator("/path/to/vault")
            >>> content = "Machine learning is a subset of AI"
            >>> connections = coordinator.discover_connections(content)
            >>> print(f"Found {len(connections)} related notes")
        """
        if not target_content:
            return []

        # Default to Permanent Notes if no directory specified
        if corpus_dir is None:
            corpus_dir = self.base_dir / "Permanent Notes"

        # Load the corpus from directory
        corpus = self.load_corpus(corpus_dir)
        if not corpus:
            return []

        # Find similar notes using AIConnections semantic analysis
        try:
            similar_notes = self.connections.find_similar_notes(
                target_content,
                corpus
            )

            # Format results and update statistics
            connections = []
            for filename, similarity in similar_notes:
                connections.append({
                    "filename": filename,
                    "similarity": similarity
                })

                # Track discovery statistics
                self._total_discoveries += 1
                self._total_similarity_sum += similarity

            return connections

        except Exception:
            # Graceful fallback - return empty list on any errors
            # Prevents connection discovery failures from blocking workflows
            return []

    def validate_connections(
        self,
        connections: List[Dict]
    ) -> List[Dict]:
        """
        Validate and deduplicate connections.
        
        Args:
            connections: List of connection dictionaries
            
        Returns:
            Validated and deduplicated connections
        """
        if not connections:
            return []

        # Track seen filenames with best similarity
        seen: Dict[str, float] = {}
        validated = []

        for conn in connections:
            filename = conn.get("filename")
            similarity = conn.get("similarity", 0.0)

            if filename:
                # Keep highest similarity for duplicates
                if filename not in seen or similarity > seen[filename]:
                    seen[filename] = similarity

                    # Remove old entry if exists
                    validated = [c for c in validated if c["filename"] != filename]
                    validated.append(conn)

        # Sort by similarity descending
        validated.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)

        return validated

    def get_connection_statistics(self) -> Dict:
        """
        Get statistics about connection discoveries.
        
        Returns:
            Dictionary with total_discoveries and average_similarity
        """
        avg_similarity = 0.0
        if self._total_discoveries > 0:
            avg_similarity = self._total_similarity_sum / self._total_discoveries

        return {
            "total_discoveries": self._total_discoveries,
            "average_similarity": avg_similarity
        }

    def clear_cache(self):
        """Clear the corpus cache."""
        self._corpus_cache.clear()
