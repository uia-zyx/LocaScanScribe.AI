import re

from app.api.schemas import SearchRequest
from app.domain.models import SearchResult, SearchSnippet
from app.ingestion.repository import DocumentRepository
from app.search.chunking import chunk_markdown
from app.search.vector_store import VectorStore

MIN_QUERY_TOKEN_LENGTH = 3
QUERY_STOP_WORDS = {
    "как",
    "для",
    "или",
    "при",
    "что",
    "это",
    "без",
    "над",
    "под",
    "the",
    "and",
    "for",
    "with",
    "how",
}


class SearchService:
    def __init__(self, repository: DocumentRepository, vector_store: VectorStore) -> None:
        self.repository = repository
        self.vector_store = vector_store

    async def search(self, request: SearchRequest) -> list[SearchResult]:
        try:
            vector_results = await self._vector_search(request)
        except Exception:
            vector_results = []

        if vector_results:
            return vector_results

        return self._keyword_search(request)

    async def _vector_search(self, request: SearchRequest) -> list[SearchResult]:
        matches = await self.vector_store.search(request.query, limit=request.limit * 5)
        grouped: dict[str, SearchResult] = {}

        for document_id, score, snippet in matches:
            document = self.repository.get(document_id, include_content=False)
            if document is None:
                continue
            if request.filters and request.filters.mime_types:
                if document.mime_type not in request.filters.mime_types:
                    continue

            key = str(document.id)
            if key not in grouped:
                grouped[key] = SearchResult(
                    document_id=document.id,
                    title=document.title,
                    url=f"/documents/{document.id}",
                    score=score,
                    snippets=[],
                )

            if len(grouped[key].snippets) < 3:
                grouped[key].snippets.append(snippet)

        return list(grouped.values())[: request.limit]

    def _keyword_search(self, request: SearchRequest) -> list[SearchResult]:
        query = request.query.casefold()
        query_tokens = _query_tokens(query)
        results: list[tuple[float, SearchResult]] = []

        for document in self.repository.list():
            if request.filters and request.filters.mime_types:
                if document.mime_type not in request.filters.mime_types:
                    continue

            markdown = document.markdown or ""
            chunks = chunk_markdown(document.id, markdown)
            snippets: list[SearchSnippet] = []
            score = _match_score(
                f"{document.title}\n{document.original_filename}\n{markdown}".casefold(),
                query,
                query_tokens,
            )
            if score <= 0:
                continue

            for chunk in chunks:
                chunk_score = _match_score(chunk.text.casefold(), query, query_tokens)
                if chunk_score > 0:
                    snippets.append(
                        SearchSnippet(
                            chunk_id=chunk.id,
                            phrase=_snippet(chunk.text, request.query, query_tokens),
                            page_number=chunk.page_number,
                            heading_path=chunk.heading_path,
                        )
                    )
                if len(snippets) >= 3:
                    break

            if snippets:
                results.append(
                    (
                        score,
                        SearchResult(
                            document_id=document.id,
                            title=document.title,
                            url=f"/documents/{document.id}",
                            score=score,
                            snippets=snippets[:3],
                        ),
                    )
                )

        results.sort(key=lambda item: item[0], reverse=True)
        return [result for _, result in results[: request.limit]]


def _snippet(
    text: str,
    query: str,
    query_tokens: list[str] | None = None,
    radius: int = 120,
) -> str:
    position = text.casefold().find(query.casefold())
    if position < 0 and query_tokens:
        position = min(
            (
                token_position
                for token in query_tokens
                if (token_position := text.casefold().find(token)) >= 0
            ),
            default=-1,
        )
    if position < 0:
        return text[: radius * 2].strip()

    start = max(position - radius, 0)
    end = min(position + len(query) + radius, len(text))
    return text[start:end].strip()


def _query_tokens(query: str) -> list[str]:
    tokens = re.findall(r"[\wА-Яа-яЁё]+", query.casefold())
    return [
        token
        for token in tokens
        if len(token) >= MIN_QUERY_TOKEN_LENGTH and token not in QUERY_STOP_WORDS
    ]


def _match_score(text: str, query: str, query_tokens: list[str]) -> float:
    if query in text:
        return 1000.0 + len(query_tokens)

    matching_tokens = [token for token in query_tokens if token in text]
    if not matching_tokens:
        return 0.0

    coverage = len(matching_tokens) / max(len(query_tokens), 1)
    return float(len(matching_tokens)) + coverage

