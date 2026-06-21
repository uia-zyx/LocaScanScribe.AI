from app.api.schemas import SearchRequest
from app.domain.models import SearchResult, SearchSnippet
from app.ingestion.repository import DocumentRepository
from app.search.chunking import chunk_markdown
from app.search.vector_store import VectorStore


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
        results: list[SearchResult] = []

        for document in self.repository.list():
            if request.filters and request.filters.mime_types:
                if document.mime_type not in request.filters.mime_types:
                    continue

            markdown = document.markdown or ""
            chunks = chunk_markdown(document.id, markdown)
            snippets: list[SearchSnippet] = []

            for chunk in chunks:
                if query in chunk.text.casefold():
                    snippets.append(
                        SearchSnippet(
                            chunk_id=chunk.id,
                            phrase=_snippet(chunk.text, request.query),
                            page_number=chunk.page_number,
                            heading_path=chunk.heading_path,
                        )
                    )

            if snippets:
                results.append(
                    SearchResult(
                        document_id=document.id,
                        title=document.title,
                        url=f"/documents/{document.id}",
                        score=1.0,
                        snippets=snippets[:3],
                    )
                )

        return results[: request.limit]


def _snippet(text: str, query: str, radius: int = 120) -> str:
    position = text.casefold().find(query.casefold())
    if position < 0:
        return text[: radius * 2].strip()

    start = max(position - radius, 0)
    end = min(position + len(query) + radius, len(text))
    return text[start:end].strip()

