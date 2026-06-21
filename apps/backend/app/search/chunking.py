from uuid import UUID

from app.domain.models import DocumentChunk


def chunk_markdown(
    document_id: UUID,
    markdown: str,
    target_size: int = 1200,
) -> list[DocumentChunk]:
    paragraphs = [part.strip() for part in markdown.split("\n\n") if part.strip()]
    chunks: list[DocumentChunk] = []
    buffer: list[str] = []
    buffer_size = 0

    for paragraph in paragraphs:
        if buffer and buffer_size + len(paragraph) > target_size:
            chunks.append(_make_chunk(document_id, len(chunks), buffer))
            buffer = []
            buffer_size = 0

        buffer.append(paragraph)
        buffer_size += len(paragraph)

    if buffer:
        chunks.append(_make_chunk(document_id, len(chunks), buffer))

    return chunks


def _make_chunk(document_id: UUID, index: int, parts: list[str]) -> DocumentChunk:
    return DocumentChunk(document_id=document_id, chunk_index=index, text="\n\n".join(parts))

