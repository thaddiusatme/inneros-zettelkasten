import logging
import hashlib
from pathlib import Path
from typing import List, Optional, Generator

from .embedding_service import EmbeddingService
from .vector_store import VectorStore


class VaultIndexer:
    """
    Handles indexing of markdown files in the vault.
    Scans files, detects changes, generates embeddings, and updates the vector store.
    """

    def __init__(
        self,
        vault_path: str,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(__name__)

        # Initialize services if not provided
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService()

    def index_vault(self, incremental: bool = True) -> dict:
        """
        Scan and index the vault.

        Args:
            incremental: If True, only processes files that have changed.

        Returns:
            Dict with stats: {'processed': int, 'skipped': int, 'errors': int}
        """
        self.logger.info(f"Starting vault indexing (incremental={incremental})...")

        stats = {"processed": 0, "skipped": 0, "errors": 0}

        # Iterate over all markdown files
        for file_path in self._get_markdown_files():
            try:
                self._process_file(file_path, stats, incremental)
            except Exception as e:
                self.logger.error(f"Error processing {file_path.name}: {e}")
                stats["errors"] += 1

        self.logger.info(f"Indexing complete. Stats: {stats}")
        return stats

    def _get_markdown_files(self) -> Generator[Path, None, None]:
        """Yields all markdown files in the vault, excluding hidden/ignored ones."""
        # Simple recursive glob
        for p in self.vault_path.rglob("*.md"):
            # Skip hidden folders (e.g. .obsidian, .git)
            if any(part.startswith(".") for part in p.parts):
                continue
            yield p

    def _process_file(self, file_path: Path, stats: dict, incremental: bool):
        """Process a single file."""
        # Calculate content hash
        content = file_path.read_text(encoding="utf-8")
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

        rel_path = str(file_path.relative_to(self.vault_path))

        if incremental:
            # Check if existing hash matches
            stored_hash = self.vector_store.get_document_hash(rel_path)
            if stored_hash == content_hash:
                stats["skipped"] += 1
                return

        # Generate embedding
        # TODO: Smart chunking? For now, truncate/use full text (all-MiniLM truncates to 256/512 tokens usually)
        # For Zettelkasten, notes are usually atomic, so full text is often okay.
        embedding = self.embedding_service.generate(content)

        # Update store
        self.vector_store.add_document(rel_path, embedding, content_hash)
        stats["processed"] += 1
        self.logger.debug(f"Indexed: {rel_path}")

    def remove_deleted_files(self) -> int:
        """
        Check for files in the DB that no longer exist on disk and remove them.
        Returns count of removed files.
        """
        # This is harder with the current VectorStore API (it doesn't list all paths).
        # We might need to add a `list_documents` method to VectorStore.
        # For now, skipping cleanup.
        return 0
