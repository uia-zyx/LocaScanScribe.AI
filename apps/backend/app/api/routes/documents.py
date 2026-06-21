from pathlib import Path
from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import Response

from app.api.deps import (
    get_document_job_queue,
    get_document_repository,
    get_ingestion_service,
    get_vector_store,
)
from app.api.schemas import DocumentListItem, DocumentUpdateRequest, DocumentUploadResponse
from app.domain.models import Document, DocumentStatus, ProcessingStrategy
from app.ingestion.repository import DocumentRepository
from app.ingestion.service import IngestionService
from app.jobs.queue import DocumentJobQueue
from app.search.vector_store import VectorStore

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    strategy: Annotated[ProcessingStrategy, Form(...)],
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
    job_queue: Annotated[DocumentJobQueue, Depends(get_document_job_queue)],
) -> DocumentUploadResponse:
    content = await file.read()
    document, job_id, deduplicated = await service.ingest(
        filename=file.filename or "document",
        mime_type=file.content_type or "application/octet-stream",
        content=content,
        strategy=strategy,
    )
    if not deduplicated:
        try:
            job_queue.enqueue_processing(document.id)
        except Exception:
            background_tasks.add_task(service.process_document, document.id)

    return DocumentUploadResponse(
        document_id=document.id,
        job_id=job_id,
        status=document.status,
        deduplicated=deduplicated,
    )


@router.get("", response_model=list[DocumentListItem])
async def list_documents(
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> list[DocumentListItem]:
    return [
        DocumentListItem(
            id=document.id,
            title=document.title,
            original_filename=document.original_filename,
            mime_type=document.mime_type,
            status=document.status,
            processing_strategy=document.processing_strategy,
        )
        for document in repository.list()
    ]


@router.get("/{document_id}", response_model=DocumentListItem)
async def get_document(
    document_id: UUID,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentListItem:
    document = repository.get(document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return DocumentListItem(
        id=document.id,
        title=document.title,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        status=document.status,
        processing_strategy=document.processing_strategy,
    )


@router.put("/{document_id}", response_model=DocumentListItem)
async def update_document(
    document_id: UUID,
    request: DocumentUpdateRequest,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentListItem:
    document = repository.get(document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    document.title = request.title
    repository.save(document)

    return DocumentListItem(
        id=document.id,
        title=document.title,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        status=document.status,
        processing_strategy=document.processing_strategy,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> Response:
    try:
        vector_store.delete_document(document_id)
    except Exception:
        pass

    if not repository.delete(document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{document_id}/retry",
    response_model=DocumentListItem,
    status_code=status.HTTP_202_ACCEPTED,
)
async def retry_document_processing(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
    job_queue: Annotated[DocumentJobQueue, Depends(get_document_job_queue)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> DocumentListItem:
    document = repository.get(document_id, include_content=False)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    try:
        vector_store.delete_document(document.id)
    except Exception:
        pass

    document.status = DocumentStatus.processing
    document.markdown = None
    repository.save(document)

    try:
        job_queue.enqueue_processing(document.id)
    except Exception:
        background_tasks.add_task(service.process_document, document.id)

    return _document_list_item(document)


@router.get("/{document_id}/markdown", response_model=str)
async def get_document_markdown(
    document_id: UUID,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> str:
    document = repository.get(document_id, include_content=False)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return document.markdown or _pending_markdown(document.original_filename, document.status)


@router.get("/{document_id}/recognized")
async def get_recognized_document(
    document_id: UUID,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> Response:
    document = repository.get(document_id, include_content=False)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    filename = _recognized_filename(document.original_filename)
    content = document.markdown or _pending_markdown(document.original_filename, document.status)
    return Response(
        content=content.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": _content_disposition(filename),
        },
    )


@router.get("/{document_id}/original")
async def get_original_document(
    document_id: UUID,
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> Response:
    document = repository.get(document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return Response(
        content=document.original_content,
        media_type=document.mime_type,
        headers={
            "Content-Disposition": _content_disposition(document.original_filename),
        },
    )


def _content_disposition(filename: str) -> str:
    ascii_filename = filename.encode("ascii", errors="ignore").decode("ascii").strip()
    if not ascii_filename or ascii_filename == Path(filename).suffix:
        ascii_filename = f"document{Path(filename).suffix}"

    utf8_filename = quote(filename)
    return f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{utf8_filename}'


def _recognized_filename(filename: str) -> str:
    path = Path(filename)
    stem = path.stem or "document"
    return f"{stem}.recognized.md"


def _pending_markdown(filename: str, status: str) -> str:
    return f"# {filename}\n\n_Document OCR status: {status}._"


def _document_list_item(document: Document) -> DocumentListItem:
    return DocumentListItem(
        id=document.id,
        title=document.title,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        status=document.status,
        processing_strategy=document.processing_strategy,
    )

