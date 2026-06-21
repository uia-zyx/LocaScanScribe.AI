from app.api.schemas import SearchRequest
from app.domain.models import Document, ProcessingStrategy
from app.search.service import SearchService, _query_tokens


class StubRepository:
    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents

    def list(self) -> list[Document]:
        return self.documents


class StubVectorStore:
    pass


def test_keyword_search_matches_long_question_by_tokens() -> None:
    document = Document(
        title="Equations",
        original_filename="equations.pdf",
        mime_type="application/pdf",
        content_hash="hash",
        processing_strategy=ProcessingStrategy.scanner_ocr,
        markdown=(
            "# Equations\n\n"
            "Чтобы найти корни уравнения на отрезке, сначала решите уравнение, "
            "а затем оставьте только корни, принадлежащие заданному интервалу."
        ),
    )
    service = SearchService(StubRepository([document]), StubVectorStore())

    results = service._keyword_search(
        SearchRequest(
            query="как найти корни уравнения принадлежащие отрезку пошаговый алгоритм",
            limit=5,
        )
    )

    assert len(results) == 1
    assert results[0].document_id == document.id
    assert "корни уравнения" in results[0].snippets[0].phrase


def test_keyword_search_ranks_more_matching_tokens_first() -> None:
    weak_match = Document(
        title="Single term",
        original_filename="single.pdf",
        mime_type="application/pdf",
        content_hash="weak",
        processing_strategy=ProcessingStrategy.scanner_ocr,
        markdown="Уравнение описывает равенство.",
    )
    strong_match = Document(
        title="Full method",
        original_filename="full.pdf",
        mime_type="application/pdf",
        content_hash="strong",
        processing_strategy=ProcessingStrategy.scanner_ocr,
        markdown="Решение уравнения помогает найти корни на заданном отрезке.",
    )
    service = SearchService(StubRepository([weak_match, strong_match]), StubVectorStore())

    results = service._keyword_search(SearchRequest(query="найти корни уравнения", limit=5))

    assert [result.document_id for result in results] == [strong_match.id, weak_match.id]


def test_query_tokens_remove_common_short_words() -> None:
    assert _query_tokens("как найти корни уравнения") == ["найти", "корни", "уравнения"]
