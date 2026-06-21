import asyncio

from app.domain.models import Document, DocumentStatus, ProcessingStrategy
from app.ingestion.service import IngestionService
from app.parsers.base import ParsedDocument, StoredFile


class StubRepository:
    def __init__(self, document: Document) -> None:
        self.document = document
        self.saved_statuses: list[DocumentStatus] = []

    def get(self, document_id, include_content: bool = True) -> Document | None:
        if document_id == self.document.id:
            return self.document
        return None

    def save(self, document: Document) -> None:
        self.document = document
        self.saved_statuses.append(document.status)


class StubParserRegistry:
    async def parse(self, file: StoredFile, strategy: ProcessingStrategy) -> ParsedDocument:
        return ParsedDocument(
            title="Recognized document",
            markdown="# Recognized document\n\nVector indexed content.",
            strategy=strategy,
        )


class StubVectorStore:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.upserted_chunks = 0

    async def upsert_document_chunks(self, document: Document, chunks) -> None:
        if self.should_fail:
            raise RuntimeError("vector store unavailable")
        self.upserted_chunks = len(chunks)


def test_process_document_marks_indexed_after_vector_upsert() -> None:
    document = Document(
        title="source.pdf",
        original_filename="source.pdf",
        mime_type="application/pdf",
        original_content=b"pdf",
        content_hash="hash",
        processing_strategy=ProcessingStrategy.ocr_model,
        status=DocumentStatus.processing,
    )
    repository = StubRepository(document)
    vector_store = StubVectorStore()
    service = IngestionService(repository, StubParserRegistry(), vector_store)

    asyncio.run(service.process_document(document.id))

    assert repository.document.status == DocumentStatus.indexed
    assert repository.document.markdown == "# Recognized document\n\nVector indexed content."
    assert vector_store.upserted_chunks == 1
    assert repository.saved_statuses == [DocumentStatus.processing, DocumentStatus.indexed]


def test_process_document_fails_when_vector_upsert_fails() -> None:
    document = Document(
        title="source.pdf",
        original_filename="source.pdf",
        mime_type="application/pdf",
        original_content=b"pdf",
        content_hash="hash",
        processing_strategy=ProcessingStrategy.ocr_model,
        status=DocumentStatus.processing,
    )
    repository = StubRepository(document)
    vector_store = StubVectorStore(should_fail=True)
    service = IngestionService(repository, StubParserRegistry(), vector_store)

    asyncio.run(service.process_document(document.id))

    assert repository.document.status == DocumentStatus.failed
    assert repository.document.markdown == "# Recognized document\n\nVector indexed content."
    assert repository.saved_statuses == [DocumentStatus.processing, DocumentStatus.failed]
