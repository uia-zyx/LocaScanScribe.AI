from app.core.settings import Settings


def test_cors_origin_list_accepts_wildcard() -> None:
    settings = Settings(cors_origins="*")

    assert settings.cors_origin_list == ["*"]


def test_cors_origin_list_accepts_json_list() -> None:
    settings = Settings(
        cors_origins='["http://localhost:3000", "http://127.0.0.1:3000"]'
    )

    assert settings.cors_origin_list == ["http://localhost:3000", "http://127.0.0.1:3000"]
