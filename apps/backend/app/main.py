from importlib import import_module
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.routes import documents, health, mcp, openwebui, search
from app.core.settings import get_settings
from app.db.session import init_database

MCP_OPERATION_IDS = [
    "get_health_status",
    "list_documents",
    "get_document",
    "update_document_title",
    "delete_document",
    "retry_document_processing",
    "get_document_markdown",
    "reindex_document_vectors",
    "mcp_search_documents",
]


def mount_mcp_server(app: FastAPI) -> None:
    fastapi_mcp: Any = import_module("fastapi_mcp")
    mcp = fastapi_mcp.FastApiMCP(
        app,
        name="OpenLocalSearchParser MCP Server",
        description=(
            "Tools for checking health, listing documents, reading recognized Markdown, "
            "reindexing vectors, and searching local documents."
        ),
        include_operations=MCP_OPERATION_IDS,
        describe_all_responses=True,
        describe_full_response_schema=True,
    )
    mcp.mount_http(mount_path="/mcp")


def create_app() -> FastAPI:
    settings = get_settings()
    cors_origins = settings.cors_origin_list
    app = FastAPI(
        title=settings.app_name,
        summary="Local OCR, Markdown, embedding, and document search API.",
        description=(
            "OpenLocalSearchParser exposes an API for uploading documents, "
            "running OCR/parsing, storing recognized Markdown, indexing chunks in Qdrant, "
            "searching through embeddings, and integrating with Open WebUI external search."
        ),
        version="0.1.0",
        openapi_tags=[
            {"name": "health", "description": "Readiness and health-check endpoints."},
            {"name": "documents", "description": "Document ingestion, CRUD, downloads, and indexing."},
            {"name": "search", "description": "Embedding-first search over local indexed documents."},
            {
                "name": "openwebui",
                "description": "External web search and loader contract for Open WebUI.",
            },
            {
                "name": "mcp",
                "description": "Model Context Protocol server exposed over Streamable HTTP.",
            },
        ],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        init_database()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials="*" not in cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(openwebui.router, prefix="/api")
    app.include_router(mcp.router, prefix="/api")

    mount_mcp_server(app)

    @app.get("/api/reference", include_in_schema=False)
    def scalar_reference() -> HTMLResponse:
        return HTMLResponse(
            """
            <!doctype html>
            <html>
              <head>
                <title>OpenLocalSearchParser API Reference</title>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
              </head>
              <body>
                <script
                  id="api-reference"
                  data-url="/openapi.json"
                  data-theme="alternate"
                ></script>
                <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
              </body>
            </html>
            """
        )

    return app


app = create_app()

