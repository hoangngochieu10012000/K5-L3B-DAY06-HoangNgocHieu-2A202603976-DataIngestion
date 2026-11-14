"""Real embedding provider adapter using google/embeddinggemma-2."""
import logging
import os
from typing import Protocol

# Avoid OpenMP collision on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class EmbeddingGemmaEmbedder:
    """Embedder using Google EmbeddingGemma-2 (768 dimensions)."""

    def __init__(self, model_name: str = "google/embeddinggemma-2", device: str | None = None) -> None:
        self.model_name = model_name
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Loading embedding model '{self.model_name}' on {self.device}...")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        self.dimensions = int(self.model.get_embedding_dimension())
        logger.info(f"Model loaded: {self.model_name}, dimensions: {self.dimensions}")

    def embed_documents(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Embed document chunks using Google EmbeddingGemma document instruction format."""
        if not texts:
            return []

        formatted_texts = [f"title: none | text: {t}" for t in texts]
        embeddings = self.model.encode(
            formatted_texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, question: str) -> list[float]:
        """Embed user question using Google EmbeddingGemma QA query instruction format."""
        formatted_query = f"task: question answering | query: {question}"
        embedding = self.model.encode(
            [formatted_query],
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )[0]
        return embedding.tolist()


# Alias for compatibility with starter template
MyEmbedder = EmbeddingGemmaEmbedder
