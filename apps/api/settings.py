from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("apps/api/.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "postgresql://user:password@localhost:5432/flowtab"
    # Required for admin operations like POST /v1/prompts.
    # Render blueprint generates this automatically; local dev should set it in apps/api/.env.
    admin_key: str | None = None

    # Auth settings
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Change in production!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OAuth settings (set these in apps/api/.env for production)
    google_client_id: str | None = None
    google_client_secret: str | None = None

    github_client_id: str | None = None
    github_client_secret: str | None = None

    facebook_client_id: str | None = None
    facebook_client_secret: str | None = None

    # Stripe settings
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    # Exact-match allowlist of redirect URIs we will accept in OAuth flows.
    # Comma-separated list.
    # NOTE: exact-match allowlist. Include dev callback routes here.
    # Our frontend uses a single callback route and passes provider as a query param.
    oauth_redirect_allowlist: str = "http://localhost/callback,http://localhost:3000/auth/callback?provider=google,http://localhost:3000/auth/callback?provider=github,http://localhost:3000/auth/callback?provider=facebook,https://flowtab.pro/auth/callback?provider=google,https://flowtab.pro/auth/callback?provider=github,https://flowtab.pro/auth/callback?provider=facebook,https://www.flowtab.pro/auth/callback?provider=google,https://www.flowtab.pro/auth/callback?provider=github,https://www.flowtab.pro/auth/callback?provider=facebook"

    @property
    def oauth_redirect_allowlist_list(self) -> List[str]:
        return [
            uri.strip()
            for uri in self.oauth_redirect_allowlist.split(",")
            if uri.strip()
        ]

    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list of origins."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


settings = Settings()
