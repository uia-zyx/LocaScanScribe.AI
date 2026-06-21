from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"


class ProcessingStrategy(StrEnum):
    parser = "parser"
    scanner_ocr = "scanner_ocr"
    ocr_model = "ocr_model"


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    original_filename: str
    mime_type: str
    original_content: bytes = b""
    content_hash: str
    storage_key: str | None = None
    status: DocumentStatus = DocumentStatus.uploaded
    processing_strategy: ProcessingStrategy
    markdown: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chunk_index: int
    text: str
    page_number: int | None = None
    heading_path: list[str] = Field(default_factory=list)


class SearchSnippet(BaseModel):
    chunk_id: UUID
    phrase: str
    page_number: int | None = None
    heading_path: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    document_id: UUID
    title: str
    url: str
    score: float
    snippets: list[SearchSnippet]

