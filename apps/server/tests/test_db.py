from app.db import _normalize_database_url


def test_postgres_url_is_normalized_for_psycopg3() -> None:
    assert _normalize_database_url("postgresql://user:pass@example.com:5432/app") == (
        "postgresql+psycopg://user:pass@example.com:5432/app"
    )


def test_existing_sqlalchemy_driver_prefix_is_preserved() -> None:
    assert _normalize_database_url("postgresql+psycopg://user:pass@example.com:5432/app") == (
        "postgresql+psycopg://user:pass@example.com:5432/app"
    )
