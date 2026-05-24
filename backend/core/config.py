from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Load .env from both the repo root and backend/ so either convention
    # works regardless of which cwd the process is started from. Later
    # entries take precedence.
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", _REPO_ROOT / "backend" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

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

    # GenAI — Gemini
    # `gemini_api_key` is the server-wide fallback used when the caller has
    # no per-user key stored. Empty by default so CI runs without a secret
    # (tests mock at the `backend/agent/gemini.py` boundary).
    gemini_api_key: str = ""
    # Default to Flash — cheaper and fast enough for the agent loop.
    gemini_default_model: str = "gemini-2.5-flash"
    # Upper bound on the agent's tool-execution loop. Prevents runaway
    # function-calling chains if the model keeps requesting tools.
    gemini_max_tool_iterations: int = 6
    # Fernet key used to encrypt per-user Gemini API keys at rest. Generate
    # one with:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # When empty, the BYOK endpoints 503 but the agent still works using
    # `gemini_api_key` as a global fallback (useful for local dev).
    gemini_key_encryption_key: str = ""

    # CORS — `NoDecode` tells pydantic-settings to skip its JSON parse so
    # the validator below can accept a plain comma-separated string in .env.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",
            "http://localhost:5000",
        ]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_csv_origins(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

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
