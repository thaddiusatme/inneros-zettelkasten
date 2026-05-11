"""
Integration tests for RAG (Retrieval Augmented Generation) system.
Tests the complete pipeline: indexing → embedding → search.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from development.src.rag.embedding_service import EmbeddingService
from development.src.rag.vector_store import VectorStore
from development.src.rag.indexer import VaultIndexer


class TestRAGIntegration(unittest.TestCase):
    """Integration tests for the complete RAG pipeline."""

    def setUp(self):
        """Create temporary vault with test notes."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir) / "vault"
        self.vault_path.mkdir()
        self.db_path = Path(self.test_dir) / "vectors.db"

        # Create test notes with distinct topics
        self._create_test_note(
            "ai-agents.md",
            "# AI Agents\nAutonomous AI agents use LLMs for reasoning and tool use.",
        )
        self._create_test_note(
            "cooking-pasta.md",
            "# Cooking Pasta\nBoil water, add salt, cook pasta for 8-10 minutes.",
        )
        self._create_test_note(
            "machine-learning.md",
            "# Machine Learning\nNeural networks learn patterns from training data.",
        )
        self._create_test_note(
            "gardening.md",
            "# Gardening Tips\nPlant tomatoes in spring with full sun exposure.",
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def _create_test_note(self, filename: str, content: str):
        """Helper to create a test note."""
        (self.vault_path / filename).write_text(content, encoding="utf-8")

    def test_indexer_processes_all_files(self):
        """Test that indexer processes all markdown files."""
        store = VectorStore(db_path=str(self.db_path))
        embedder = EmbeddingService()
        indexer = VaultIndexer(
            vault_path=str(self.vault_path),
            vector_store=store,
            embedding_service=embedder,
        )

        stats = indexer.index_vault(incremental=False)

        self.assertEqual(stats["processed"], 4)
        self.assertEqual(stats["skipped"], 0)
        self.assertEqual(stats["errors"], 0)

    def test_incremental_indexing_skips_unchanged(self):
        """Test that incremental indexing skips unchanged files."""
        store = VectorStore(db_path=str(self.db_path))
        embedder = EmbeddingService()
        indexer = VaultIndexer(
            vault_path=str(self.vault_path),
            vector_store=store,
            embedding_service=embedder,
        )

        # First index
        stats1 = indexer.index_vault(incremental=True)
        self.assertEqual(stats1["processed"], 4)

        # Second index - should skip all
        stats2 = indexer.index_vault(incremental=True)
        self.assertEqual(stats2["processed"], 0)
        self.assertEqual(stats2["skipped"], 4)

    def test_search_returns_relevant_results(self):
        """Test that semantic search returns relevant notes."""
        store = VectorStore(db_path=str(self.db_path))
        embedder = EmbeddingService()
        indexer = VaultIndexer(
            vault_path=str(self.vault_path),
            vector_store=store,
            embedding_service=embedder,
        )

        # Index vault
        indexer.index_vault(incremental=False)

        # Search for AI-related content
        query_vec = embedder.generate("artificial intelligence and neural networks")
        results = store.search(query_vec, limit=2)

        # Should return AI and ML notes as most relevant
        self.assertEqual(len(results), 2)
        result_paths = [r["path"] for r in results]

        # AI-related notes should be in top results
        ai_notes = {"ai-agents.md", "machine-learning.md"}
        self.assertTrue(
            any(path in ai_notes for path in result_paths),
            f"Expected AI-related notes in results, got: {result_paths}",
        )

    def test_search_with_different_topics(self):
        """Test that search distinguishes between topics."""
        store = VectorStore(db_path=str(self.db_path))
        embedder = EmbeddingService()
        indexer = VaultIndexer(
            vault_path=str(self.vault_path),
            vector_store=store,
            embedding_service=embedder,
        )

        indexer.index_vault(incremental=False)

        # Search for cooking
        cooking_vec = embedder.generate("how to cook food in the kitchen")
        cooking_results = store.search(cooking_vec, limit=1)

        # Search for plants
        garden_vec = embedder.generate("growing vegetables and plants")
        garden_results = store.search(garden_vec, limit=1)

        # Results should be different
        self.assertNotEqual(
            cooking_results[0]["path"],
            garden_results[0]["path"],
            "Different queries should return different top results",
        )

    def test_vector_store_persistence(self):
        """Test that vector store persists data across instances."""
        # First instance: index vault
        store1 = VectorStore(db_path=str(self.db_path))
        embedder = EmbeddingService()
        indexer = VaultIndexer(
            vault_path=str(self.vault_path),
            vector_store=store1,
            embedding_service=embedder,
        )
        indexer.index_vault(incremental=False)

        # Second instance: search without re-indexing
        store2 = VectorStore(db_path=str(self.db_path))
        query_vec = embedder.generate("AI agents")
        results = store2.search(query_vec, limit=4)

        # Should find all indexed documents
        self.assertEqual(len(results), 4)


if __name__ == "__main__":
    unittest.main()
