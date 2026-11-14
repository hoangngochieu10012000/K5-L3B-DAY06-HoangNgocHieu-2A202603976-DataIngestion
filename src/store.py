"""Persistent vector store implementation using Qdrant Local with cosine similarity."""
import logging
from pathlib import Path
from typing import Any
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)
from .models import Chunk

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Persistent local vector store backed by Qdrant Embedded."""

    def __init__(self, db_path: str = "starter/results/qdrant_db", dimensions: int = 768) -> None:
        self.db_path = str(db_path)
        self.dimensions = dimensions
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=self.db_path)
        logger.info(f"Initialized QdrantVectorStore at '{self.db_path}' (dim={self.dimensions})")

    def _collection_name(self, strategy: str) -> str:
        return f"chunks_strategy_{strategy.lower()}"

    def create_schema(self, strategy: str) -> None:
        """Create or recreate collection for a given strategy."""
        coll = self._collection_name(strategy)
        if not self.client.collection_exists(coll):
            self.client.create_collection(
                collection_name=coll,
                vectors_config=VectorParams(size=self.dimensions, distance=Distance.COSINE),
            )
            logger.info(f"Created collection '{coll}' with cosine metric.")
        else:
            logger.info(f"Collection '{coll}' already exists.")

    def reset_collection(self, strategy: str) -> None:
        """Delete and recreate collection for clean re-ingestion."""
        coll = self._collection_name(strategy)
        if self.client.collection_exists(coll):
            self.client.delete_collection(coll)
        self.client.create_collection(
            collection_name=coll,
            vectors_config=VectorParams(size=self.dimensions, distance=Distance.COSINE),
        )
        logger.info(f"Reset collection '{coll}'.")

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]], batch_size: int = 64) -> None:
        """Validate lengths/dimensions and write stable IDs without duplicates.

        Idempotent: Uses deterministic UUID5 so re-inserting identical chunks updates rather than duplicates.
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"Mismatch between chunks ({len(chunks)}) and vectors ({len(vectors)})")

        coll = self._collection_name(strategy)
        self.create_schema(strategy)

        points: list[PointStruct] = []
        for chunk, vector in zip(chunks, vectors):
            if len(vector) != self.dimensions:
                raise ValueError(f"Vector dim {len(vector)} != expected {self.dimensions}")

            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{strategy}_{chunk.chunk_id}"))
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "source": chunk.source,
                "page": chunk.page,
                "text": chunk.text,
                "section": chunk.metadata.get("section", "general"),
                "strategy": strategy,
                "metadata": chunk.metadata,
            }
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=coll, points=batch)

        logger.info(f"Successfully upserted {len(points)} points into '{coll}'. Total count: {self.count(strategy)}")

    def count(self, strategy: str) -> int:
        coll = self._collection_name(strategy)
        if not self.client.collection_exists(coll):
            return 0
        return self.client.count(collection_name=coll).count

    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search top-k most similar chunks using cosine similarity, with optional metadata filtering."""
        coll = self._collection_name(strategy)
        if not self.client.collection_exists(coll):
            raise RuntimeError(f"Collection '{coll}' does not exist. Please run ingestion first.")

        query_filter = None
        if filters:
            conditions = []
            for key, val in filters.items():
                if val is not None:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=val)))
            if conditions:
                query_filter = Filter(must=conditions)

        response = self.client.query_points(
            collection_name=coll,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        results = []
        for p in response.points:
            payload = p.payload or {}
            results.append({
                "chunk_id": payload.get("chunk_id"),
                "document_id": payload.get("document_id"),
                "source": payload.get("source"),
                "page": payload.get("page"),
                "text": payload.get("text", ""),
                "score": float(p.score) if p.score is not None else 0.0,
                "section": payload.get("section"),
                "metadata": payload.get("metadata", {}),
            })

        return results

    def close(self) -> None:
        self.client.close()


# Alias for compatibility with starter template
PgVectorStore = QdrantVectorStore
