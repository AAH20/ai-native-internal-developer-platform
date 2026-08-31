from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LAUNCHRAIL_", env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "sqlite:///./launchrail.db"
    auth_mode: str = "disabled"
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_public_key: str | None = None
    allowed_roles: str = "platform-admin,platform-engineer,developer"
    log_level: str = "INFO"
    auto_create_schema: bool = True

    @model_validator(mode="after")
    def production_invariants(self) -> "Settings":
        if self.environment == "production":
            if self.database_url.startswith("sqlite"):
                raise ValueError("production requires PostgreSQL; SQLite is development-only")
            if self.auth_mode != "oidc":
                raise ValueError("production requires OIDC authentication")
            if self.auto_create_schema:
                raise ValueError("production schema changes must run as an explicit migration")
            if not all((self.oidc_issuer, self.oidc_audience, self.oidc_public_key)):
                raise ValueError("production OIDC issuer, audience and public key are required")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
