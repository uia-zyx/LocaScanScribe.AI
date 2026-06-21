from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.routes.openwebui import (
    _to_openwebui_search_results,
    _truncate_loader_content,
)
from app.api.openwebui_utils import (
    document_frontend_url,
    document_id_from_url,
    request_base_url,
    validate_openwebui_key,
)
from app.core.settings import Settings
from app.domain.models import SearchResult, SearchSnippet


def test_document_id_from_frontend_url() -> None:
    document_id = uuid4()

    parsed_id = document_id_from_url(f"http://localhost:3000/documents/{document_id}?tab=preview")

    assert parsed_id == document_id


def test_request_base_url_uses_request_host_before_origin_header() -> None:
    request = SimpleNamespace(
        headers={"origin": "http://192.168.1.10:3000"},
        base_url="http://host.docker.internal:8000/",
    )

    assert request_base_url(request) == "http://host.docker.internal:8000"


def test_request_base_url_uses_forwarded_host() -> None:
    request = SimpleNamespace(
        headers={"x-forwarded-proto": "https", "x-forwarded-host": "docs.example.com"},
        base_url="http://localhost:8000/",
    )

    assert request_base_url(request) == "https://docs.example.com"


def test_document_frontend_url_uses_request_base_url() -> None:
    document_id = uuid4()

    assert (
        document_frontend_url("https://docs.example.com", document_id)
        == f"https://docs.example.com/documents/{document_id}"
    )


def test_openwebui_auth_accepts_bearer_key() -> None:
    settings = Settings(openwebui_web_search_api_key="secret")

    validate_openwebui_key(settings, "Bearer secret", None)


def test_openwebui_auth_rejects_wrong_key() -> None:
    settings = Settings(openwebui_web_search_api_key="secret")

    with pytest.raises(HTTPException):
        validate_openwebui_key(settings, "Bearer wrong", None)


def test_openwebui_search_results_adapt_local_search_response() -> None:
    document_id = uuid4()
    source_base_url = "http://host.docker.internal:8000"
    results = _to_openwebui_search_results(
        [
            SearchResult(
                document_id=document_id,
                title="Equations",
                url=f"/documents/{document_id}",
                score=1.0,
                snippets=[
                    SearchSnippet(
                        chunk_id="chunk-1",
                        phrase="корни уравнения на отрезке",
                    ),
                    SearchSnippet(
                        chunk_id="chunk-2",
                        phrase="оставьте только решения внутри интервала",
                    ),
                ],
            )
        ],
        source_base_url,
    )

    assert len(results) == 1
    assert results[0].title == "Equations"
    assert results[0].link == f"http://host.docker.internal:8000/documents/{document_id}"
    assert "корни уравнения" in results[0].snippet
    assert "внутри интервала" in results[0].snippet


def test_truncate_loader_content_limits_large_documents() -> None:
    content = _truncate_loader_content("A" * 50, 10)

    assert content.startswith("AAAAAAAAAA")
    assert "longer" in content
