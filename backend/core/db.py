from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import get_settings

_engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, autoflush=False)


def get_engine():
    return _engine


def get_session() -> Generator[Session]:
    """FastAPI dependency that yields a request-scoped session."""
    with SessionLocal() as session:
        yield session


def session_scope() -> Session:
    """For use outside request scope (e.g. Celery tasks, seed CLI)."""
    return SessionLocal()
