import logging
import random
from typing import List, Union

try:
    import numpy as np
except ImportError:
    np = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class EmbeddingService:
    """
    Service for generating text embeddings using local models.
    Default model: all-MiniLM-L6-v2 (384 dimensions)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.logger = logging.getLogger(__name__)
        self._model_name = model_name
        self._model = None

        if SentenceTransformer is None:
            self.logger.warning(
                "sentence-transformers not installed. Using DUMMY mode (random embeddings)."
            )

    @property
    def model(self):
        if self._model is None:
            if SentenceTransformer is None:
                return None  # Dummy mode indicator

            self.logger.info(f"Loading embedding model: {self._model_name}...")
            self._model = SentenceTransformer(self._model_name)
            self.logger.info("Model loaded successfully.")
        return self._model

    def generate(self, text: str) -> List[float]:
        """Generate embedding for a single string."""
        if self.model is None:
            # Dummy embedding (384 dimensions for compatibility with default model)
            if np:
                rng = np.random.default_rng(len(text))
                return rng.random(384).tolist()
            else:
                # Pure python fallback
                return [random.random() for _ in range(384)]

        try:
            # model.encode returns numpy array
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of strings."""
        if self.model is None:
            if np:
                rng = np.random.default_rng(42)
                return [rng.random(384).tolist() for _ in texts]
            else:
                return [[random.random() for _ in range(384)] for _ in texts]

        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            self.logger.error(f"Error generating batch embeddings: {e}")
            raise
