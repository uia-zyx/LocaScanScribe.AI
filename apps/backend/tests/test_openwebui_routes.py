from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.openwebui_utils import (
    document_frontend_url,
    document_id_from_url,
    request_base_url,
    validate_openwebui_key,
)
from app.core.settings import Settings


def test_document_id_from_frontend_url() -> None:
    document_id = uuid4()

    parsed_id = document_id_from_url(f"http://localhost:3000/documents/{document_id}?tab=preview")

    assert parsed_id == document_id


def test_request_base_url_prefers_origin_header() -> None:
    request = SimpleNamespace(
        headers={"origin": "http://192.168.1.10:3000"},
        base_url="http://localhost:8000/",
    )

    assert request_base_url(request) == "http://192.168.1.10:3000"


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
