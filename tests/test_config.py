import pytest
from pydantic import ValidationError

from platform_api.config import Settings


def test_production_rejects_sqlite():
    with pytest.raises(ValidationError, match="PostgreSQL"):
        Settings(environment="production", database_url="sqlite:///bad.db", auth_mode="oidc", oidc_issuer="x", oidc_audience="y", oidc_public_key="z", auto_create_schema=False)


def test_production_rejects_disabled_auth():
    with pytest.raises(ValidationError, match="OIDC"):
        Settings(environment="production", database_url="postgresql+psycopg://db/platform", auth_mode="disabled")


def test_production_rejects_automatic_schema_mutation():
    with pytest.raises(ValidationError, match="explicit migration"):
        Settings(environment="production", database_url="postgresql+psycopg://db/platform", auth_mode="oidc", oidc_issuer="x", oidc_audience="y", oidc_public_key="z", auto_create_schema=True)
