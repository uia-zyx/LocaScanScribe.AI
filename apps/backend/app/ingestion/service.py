import hashlib
import logging
from uuid import UUID, uuid4

from app.domain.models import Document, DocumentStatus, ProcessingStrategy
from app.ingestion.repository import DocumentRepository
from app.parsers.base import StoredFile
from app.parsers.registry import ParserRegistry
from app.search.chunking import chunk_markdown
from app.search.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        repository: DocumentRepository,
        parser_registry: ParserRegistry,
        vector_store: VectorStore,
    ) -> None:
        self.repository = repository
        self.parser_registry = parser_registry
        self.vector_store = vector_store

    async def ingest(
        self,
        filename: str,
        mime_type: str,
        content: bytes,
        strategy: ProcessingStrategy,
    ) -> tuple[Document, UUID, bool]:
        content_hash = hashlib.sha256(content).hexdigest()
        existing_document = self.repository.find_by_content_hash(content_hash)
        if existing_document is not None:
            return existing_document, uuid4(), True

        document = Document(
            title=filename,
            original_filename=filename,
            mime_type=mime_type,
            original_content=content,
            content_hash=content_hash,
            status=DocumentStatus.processing,
            processing_strategy=strategy,
        )
        document.storage_key = self.repository.object_store.put_document(
            document_id=document.id,
            filename=filename,
            content=content,
            mime_type=mime_type,
        )
        self.repository.save(document)
        return document, uuid4(), False

    async def process_document(self, document_id: UUID) -> None:
        document = self.repository.get(document_id)
        if document is None:
            return

        file = StoredFile(
            filename=document.original_filename,
            mime_type=document.mime_type,
            content=document.original_content,
        )

        try:
            parsed = await self.parser_registry.parse(file, document.processing_strategy)
            document.title = parsed.title
            document.status = DocumentStatus.indexed
            document.processing_strategy = parsed.strategy
            document.markdown = parsed.markdown
            self.repository.save(document)

            chunks = chunk_markdown(document.id, parsed.markdown)
            try:
                await self.vector_store.upsert_document_chunks(document, chunks)
            except Exception:
                logger.exception("Vector indexing failed for %s", document.id)
        except Exception:
            logger.exception("Document processing failed for %s", document.id)
            document.status = DocumentStatus.failed
            document.markdown = (
                f"# {document.original_filename}\n\n"
                "_Document processing failed. Check backend and OCR service logs._"
            )
            self.repository.save(document)

    async def reindex_document_vectors(self, document_id: UUID) -> bool:
        document = self.repository.get(document_id, include_content=False)
        if document is None or not document.markdown:
            return False

        chunks = chunk_markdown(document.id, document.markdown)
        self.vector_store.delete_document(document.id)
        await self.vector_store.upsert_document_chunks(document, chunks)
        return True

    async def reindex_all_vectors(self) -> int:
        indexed_count = 0
        for document in self.repository.list():
            if document.status != DocumentStatus.indexed or not document.markdown:
                continue

            if await self.reindex_document_vectors(document.id):
                indexed_count += 1

        return indexed_count

