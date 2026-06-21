import hashlib
import logging
from uuid import UUID, uuid4

from app.domain.models import Document, DocumentStatus, ProcessingStrategy
from app.parsers.base import StoredFile
from app.parsers.registry import ParserRegistry
from app.search.chunking import chunk_markdown

logger = logging.getLogger(__name__)


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self.documents: dict[UUID, Document] = {}

    def save(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    def list(self) -> list[Document]:
        return sorted(self.documents.values(), key=lambda item: item.created_at, reverse=True)

    def get(self, document_id: UUID) -> Document | None:
        return self.documents.get(document_id)

    def find_by_content_hash(self, content_hash: str) -> Document | None:
        return next(
            (document for document in self.documents.values() if document.content_hash == content_hash),
            None,
        )

    def delete(self, document_id: UUID) -> bool:
        return self.documents.pop(document_id, None) is not None


class IngestionService:
    def __init__(
        self,
        repository: InMemoryDocumentRepository,
        parser_registry: ParserRegistry,
    ) -> None:
        self.repository = repository
        self.parser_registry = parser_registry

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

            # The chunking call is intentionally kept here so API contracts already match ingestion.
            chunk_markdown(document.id, parsed.markdown)
        except Exception:
            logger.exception("Document processing failed for %s", document.id)
            document.status = DocumentStatus.failed
            document.markdown = (
                f"# {document.original_filename}\n\n"
                "_Document processing failed. Check backend and OCR service logs._"
            )
            self.repository.save(document)

