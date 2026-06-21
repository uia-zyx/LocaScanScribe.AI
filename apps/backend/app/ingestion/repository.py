from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import DocumentRecord
from app.domain.models import Document, DocumentStatus, ProcessingStrategy
from app.storage.object_store import ObjectStore


class DocumentRepository:
    def __init__(self, session_factory: sessionmaker[Session], object_store: ObjectStore) -> None:
        self.session_factory = session_factory
        self.object_store = object_store

    def save(self, document: Document) -> Document:
        with self.session_factory() as session:
            record = session.get(DocumentRecord, str(document.id))
            if record is None:
                record = DocumentRecord(id=str(document.id))
                session.add(record)

            record.title = document.title
            record.original_filename = document.original_filename
            record.mime_type = document.mime_type
            record.content_hash = document.content_hash
            record.storage_key = document.storage_key or ""
            record.status = document.status.value
            record.processing_strategy = document.processing_strategy.value
            record.markdown = document.markdown
            record.created_at = document.created_at
            session.commit()

        return document

    def list(self) -> list[Document]:
        with self.session_factory() as session:
            records = session.scalars(
                select(DocumentRecord).order_by(DocumentRecord.created_at.desc())
            ).all()
            return [self._to_document(record, include_content=False) for record in records]

    def get(self, document_id: UUID, *, include_content: bool = True) -> Document | None:
        with self.session_factory() as session:
            record = session.get(DocumentRecord, str(document_id))
            if record is None:
                return None
            return self._to_document(record, include_content=include_content)

    def find_by_content_hash(self, content_hash: str) -> Document | None:
        with self.session_factory() as session:
            record = session.scalar(
                select(DocumentRecord).where(DocumentRecord.content_hash == content_hash)
            )
            if record is None:
                return None
            return self._to_document(record, include_content=False)

    def delete(self, document_id: UUID) -> bool:
        document = self.get(document_id, include_content=False)
        if document is None:
            return False

        self.object_store.delete_document(document.storage_key)
        with self.session_factory() as session:
            session.execute(delete(DocumentRecord).where(DocumentRecord.id == str(document_id)))
            session.commit()
        return True

    def _to_document(self, record: DocumentRecord, *, include_content: bool) -> Document:
        content = b""
        if include_content and record.storage_key:
            content = self.object_store.get_document(record.storage_key)

        return Document(
            id=UUID(record.id),
            title=record.title,
            original_filename=record.original_filename,
            mime_type=record.mime_type,
            original_content=content,
            content_hash=record.content_hash,
            storage_key=record.storage_key,
            status=DocumentStatus(record.status),
            processing_strategy=ProcessingStrategy(record.processing_strategy),
            markdown=record.markdown,
            created_at=record.created_at,
        )
