"""Core configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "CirclePortal API"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://circleportal:circleportal@localhost:5432/circleportal"

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Keycloak (OAuth2/OIDC)
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "CirclePortal-dev"
    keycloak_client_id: str = "circle-portal-backend"
    keycloak_client_secret: str = "dev-client-secret"
    keycloak_integration_test: bool = False
    
    # Keycloak Test User (for integration tests)
    # None の場合、統合テストはスキップされます
    keycloak_test_username: str | None = None
    keycloak_test_password: str | None = None

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Static files
    static_dir: str = "./static"
    images_dir: str = "./static/images"


settings = Settings()
