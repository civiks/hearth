import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend import models  # noqa: F401 — ensure all models register


@pytest.fixture(scope="session")
def db_url() -> Generator[str]:
    """Per-session SQLite file."""
    fd, path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    url = f"sqlite:///{path}"
    os.environ["DATABASE_URL"] = url
    yield url
    os.unlink(path)


@pytest.fixture(scope="session")
def engine(db_url: str):
    eng = create_engine(db_url)
    models.Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine) -> Generator[Session]:
    """Per-test session wrapped in a rolled-back transaction."""
    connection = engine.connect()
    trans = connection.begin()
    Local = sessionmaker(bind=connection, expire_on_commit=False)
    s = Local()
    try:
        yield s
    finally:
        s.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def client(session: Session) -> Generator[TestClient]:
    from backend.api.main import app
    from backend.core.db import get_session

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
