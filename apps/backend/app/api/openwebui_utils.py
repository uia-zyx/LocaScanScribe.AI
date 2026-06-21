from uuid import UUID

from fastapi import HTTPException, Request, status

from app.core.settings import Settings


def validate_openwebui_key(
    settings: Settings,
    authorization: str | None,
    x_api_key: str | None,
) -> None:
    expected_key = settings.openwebui_web_search_api_key
    if not expected_key:
        return

    bearer_prefix = "Bearer "
    bearer_key = ""
    if authorization and authorization.startswith(bearer_prefix):
        bearer_key = authorization.removeprefix(bearer_prefix).strip()

    if bearer_key == expected_key or x_api_key == expected_key:
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Open WebUI web search API key",
    )


def request_base_url(request: Request) -> str:
    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_proto and forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}".rstrip("/")

    base_url = str(request.base_url).rstrip("/")
    if base_url:
        return base_url

    origin = request.headers.get("origin")
    if origin:
        return origin.rstrip("/")

    return ""


def document_frontend_url(base_url: str, document_id: UUID) -> str:
    return f"{base_url.rstrip('/')}/documents/{document_id}"


def document_id_from_url(url: str) -> UUID | None:
    marker = "/documents/"
    if marker not in url:
        return None

    raw_document_id = url.rsplit(marker, maxsplit=1)[-1].split("?", maxsplit=1)[0].strip("/")
    try:
        return UUID(raw_document_id)
    except ValueError:
        return None
