import json
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LocaScanScribe.AI"
    app_env: str = "local"
    cors_origins: str = "*"
    openwebui_web_search_api_key: str = ""
    openwebui_loader_max_chars: int = 20000

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "locascan"
    postgres_user: str = "locascan"
    postgres_password: str = "locascan"

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "document_chunks"

    redis_url: str = "redis://redis:6379/0"

    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "minio"
    s3_secret_key: str = "minio12345"
    s3_bucket_documents: str = "documents"

    llama_ocr_base_url: str = "http://llama-ocr:8080/v1"
    llama_ocr_model: str = "glm-ocr"
    pdf_ocr_render_scale: float = 1.25
    pdf_ocr_jpeg_quality: int = 85
    pdf_ocr_concurrency: int = 2

    llama_embedding_base_url: str = "http://llama-embedding:8080/v1"
    llama_embedding_model: str = "qwen3-embedding"
    embedding_dimensions: int = 1024

    default_image_strategy: str = "ocr_model"
    default_pdf_strategy: str = "scanner_ocr"
    max_upload_size_mb: int = 200

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        value = self.cors_origins.strip()
        if value == "*":
            return ["*"]

        if value.startswith("["):
            parsed = json.loads(value)
            return [str(origin) for origin in parsed]

        return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

