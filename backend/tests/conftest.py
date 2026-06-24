"""Shared pytest fixtures.

Provides an isolated in-memory SQLite database and a FastAPI ``TestClient`` with
the database dependency overridden, plus a helper to materialise sample
repositories on disk in a temp directory.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def _disable_ai(monkeypatch) -> None:
    """Keep tests hermetic: never use a real AI provider or make network calls.

    Without this, a developer's local ``backend/.env`` (with a real API key)
    would leak into the test run and cause live provider calls.
    """
    monkeypatch.setattr(settings, "ai_provider", "none")
    monkeypatch.setattr(settings, "openai_api_key", "")
    monkeypatch.setattr(settings, "gemini_api_key", "")


@pytest.fixture
def db_session() -> Iterator:
    """An isolated in-memory database session per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session) -> Iterator[TestClient]:
    """A TestClient whose DB dependency is bound to the in-memory session."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """Create a small multi-language repository on disk for scanning tests."""
    repo = tmp_path / "sample_repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "node_modules").mkdir()  # should be ignored

    # Python files with an internal dependency.
    (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pkg" / "utils.py").write_text(
        "def add(a, b):\n    return a + b\n\n\nclass Helper:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "main.py").write_text(
        "from pkg.utils import add\n\n\n"
        "def main():\n"
        "    if add(1, 2) > 0:\n"
        "        return True\n"
        "    return False\n",
        encoding="utf-8",
    )

    # A JS file importing a sibling.
    (repo / "app.js").write_text(
        "import { add } from './pkg/utils';\n"
        "export function run() { return add(1, 2); }\n",
        encoding="utf-8",
    )

    # Ignored dir content should never be scanned.
    (repo / "node_modules" / "lib.js").write_text(
        "export const x = 1;\n", encoding="utf-8"
    )
    return repo
