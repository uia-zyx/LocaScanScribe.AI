from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from app.core.settings import get_settings
from app.domain.models import Document, DocumentChunk, SearchSnippet
from app.search.embeddings import EmbeddingClient


class VectorStore:
    def __init__(self, embedding_client: EmbeddingClient) -> None:
        self.settings = get_settings()
        self.embedding_client = embedding_client
        self.client = QdrantClient(url=self.settings.qdrant_url)

    async def upsert_document_chunks(self, document: Document, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        self._ensure_collection()
        points: list[qdrant_models.PointStruct] = []
        for chunk in chunks:
            vector = await self.embedding_client.embed(chunk.text)
            points.append(
                qdrant_models.PointStruct(
                    id=str(chunk.id),
                    vector=vector,
                    payload={
                        "document_id": str(document.id),
                        "title": document.title,
                        "url": f"/documents/{document.id}",
                        "text": chunk.text,
                        "page_number": chunk.page_number,
                        "heading_path": chunk.heading_path,
                        "chunk_id": str(chunk.id),
                    },
                )
            )

        self.client.upsert(collection_name=self.settings.qdrant_collection, points=points)

    def delete_document(self, document_id: UUID) -> None:
        self._ensure_collection()
        self.client.delete(
            collection_name=self.settings.qdrant_collection,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="document_id",
                            match=qdrant_models.MatchValue(value=str(document_id)),
                        )
                    ]
                )
            ),
        )

    async def search(self, query: str, limit: int) -> list[tuple[UUID, float, SearchSnippet]]:
        self._ensure_collection()
        vector = await self.embedding_client.embed(query)
        results = self.client.search(
            collection_name=self.settings.qdrant_collection,
            query_vector=vector,
            limit=limit,
            with_payload=True,
        )

        matches: list[tuple[UUID, float, SearchSnippet]] = []
        for point in results:
            payload = point.payload or {}
            document_id = payload.get("document_id")
            chunk_id = payload.get("chunk_id")
            text = payload.get("text")
            if not document_id or not chunk_id or not text:
                continue

            matches.append(
                (
                    UUID(str(document_id)),
                    float(point.score),
                    SearchSnippet(
                        chunk_id=UUID(str(chunk_id)),
                        phrase=str(text),
                        page_number=payload.get("page_number"),
                        heading_path=list(payload.get("heading_path") or []),
                    ),
                )
            )
        return matches

    def _ensure_collection(self) -> None:
        existing = {collection.name for collection in self.client.get_collections().collections}
        if self.settings.qdrant_collection in existing:
            return

        self.client.create_collection(
            collection_name=self.settings.qdrant_collection,
            vectors_config=qdrant_models.VectorParams(
                size=self.settings.embedding_dimensions,
                distance=qdrant_models.Distance.COSINE,
            ),
        )
