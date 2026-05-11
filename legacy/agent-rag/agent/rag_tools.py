from typing import Optional
from ...rag.embedding_service import EmbeddingService
from ...rag.vector_store import VectorStore

# Singleton instances (lazy loaded)
_embedding_service: Optional[EmbeddingService] = None
_vector_store: Optional[VectorStore] = None


def _get_services():
    global _embedding_service, _vector_store
    if not _embedding_service:
        _embedding_service = EmbeddingService()
    if not _vector_store:
        _vector_store = VectorStore()
    return _embedding_service, _vector_store


def search_vault(query: str, limit: int = 5) -> str:
    """
    Search the Zettelkasten vault for relevant notes using semantic search.

    Args:
        query: The search query (e.g., "history of autonomous agents")
        limit: Number of results to return (default: 5)

    Returns:
        A formatted string containing the filenames and similarity scores of relevant notes.
    """
    try:
        embedder, store = _get_services()

        # Generate embedding for query
        query_vec = embedder.generate(query)

        # Search
        results = store.search(query_vec, limit=limit)

        if not results:
            return "No relevant notes found."

        # Format output
        output = ["Found relevant notes:"]
        for res in results:
            score = res.get("score", 0.0)
            output.append(f"- {res['path']} (Similarity: {score:.2f})")

        return "\n".join(output)
    except Exception as e:
        return f"Error searching vault: {str(e)}"
