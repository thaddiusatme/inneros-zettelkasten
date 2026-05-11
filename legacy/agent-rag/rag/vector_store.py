import sqlite3
import logging
import json
import struct
from typing import List, Dict, Any, Optional
from pathlib import Path

# Try to import sqlite_vec for extension loading if available
try:
    import sqlite_vec
except ImportError:
    sqlite_vec = None


class VectorStore:
    """
    Vector storage using SQLite (with optional sqlite-vec extension).
    Falls back to pure Python cosine similarity if extension is missing/fails.
    """

    def __init__(self, db_path: str = ".automation/vectors.db", dimension: int = 384):
        self.db_path = Path(db_path)
        self.dimension = dimension
        self.logger = logging.getLogger(__name__)

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _load_extension(self, conn: sqlite3.Connection):
        """Load sqlite-vec extension if available."""
        if sqlite_vec:
            try:
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                conn.enable_load_extension(False)
                return True
            except Exception as e:
                self.logger.warning(
                    f"Failed to load sqlite-vec extension: {e}. using fallback."
                )
        return False

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Main table for metadata and raw embeddings (as binary)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    path TEXT PRIMARY KEY,
                    content_hash TEXT,
                    embedding BLOB,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index on path for fast lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_path ON documents(path)")

    def add_document(self, path: str, embedding: List[float], content_hash: str):
        """Add or update document embedding."""
        # Pack floats into binary for storage
        embedding_blob = struct.pack(f"{len(embedding)}f", *embedding)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO documents (path, content_hash, embedding, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (path, content_hash, embedding_blob),
            )

    def get_document_hash(self, path: str) -> Optional[str]:
        """Get current hash for a document to check if update needed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT content_hash FROM documents WHERE path = ?", (path,)
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def search(
        self, query_embedding: List[float], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        Currently implements in-memory cosine similarity for simplicity and portability.
        TODO: Switch to sqlite-vec vector search when properly configured.
        """
        import numpy as np

        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)

        if query_norm == 0:
            return []

        results = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT path, embedding FROM documents")
            for path, blob in cursor:
                # Unpack binary embedding
                vec = np.array(struct.unpack(f"{self.dimension}f", blob))

                # Cosine similarity
                vec_norm = np.linalg.norm(vec)
                if vec_norm == 0:
                    continue

                similarity = np.dot(query_vec, vec) / (query_norm * vec_norm)

                results.append({"path": path, "score": float(similarity)})

        # Sort by score descending and take top K
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def delete_document(self, path: str):
        """Remove document from store."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM documents WHERE path = ?", (path,))
