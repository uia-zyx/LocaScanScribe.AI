from uuid import uuid4

from app.search.chunking import chunk_markdown


def test_chunk_markdown_groups_paragraphs_without_losing_text() -> None:
    document_id = uuid4()
    markdown = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."

    chunks = chunk_markdown(document_id, markdown, target_size=32)

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert "\n\n".join(chunk.text for chunk in chunks) == markdown
    assert all(chunk.document_id == document_id for chunk in chunks)
