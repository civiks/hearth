from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    env: str = "local"
    debug: bool = True

    # Database
    database_url: str = "postgresql+psycopg://household:household@localhost:5432/household"

    # Redis (Celery broker + result + slowapi storage)
    redis_url: str = "redis://localhost:6379"

    # When true, Celery runs tasks in-process (no broker) and slowapi uses
    # in-memory storage. Used by the bundled Docker image to drop the Redis
    # dependency.
    celery_eager: bool = False

    # Auth
    secret_key: str = "dev-secret-do-not-use-in-prod"
    jwt_secret: str = "dev-jwt-secret-do-not-use-in-prod"
    jwt_lifetime_seconds: int = 3600

    # SMTP (MailHog locally)
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_from: str = "noreply@hearth.local"

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",
            "http://localhost:5000",
        ]
    )

    @property
    def celery_broker_url(self) -> str:
        return "memory://" if self.celery_eager else f"{self.redis_url}/0"

    @property
    def celery_result_backend(self) -> str:
        return "cache+memory://" if self.celery_eager else f"{self.redis_url}/1"

    @property
    def slowapi_storage_uri(self) -> str:
        return "memory://" if self.celery_eager else f"{self.redis_url}/2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
