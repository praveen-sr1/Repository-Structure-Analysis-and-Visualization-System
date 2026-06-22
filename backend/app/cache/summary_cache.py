"""Persistent cache for AI-generated summaries.

Summaries are stored in the database keyed by ``(file_path, content_hash)``.
Because the key includes the SHA-256 of the file's contents, any change to the
file produces a different key and therefore triggers regeneration — stale
summaries are never served.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.summary import Summary


class SummaryCache:
    """Read/write access to cached file summaries."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, file_path: str, content_hash: str) -> Summary | None:
        """Return the cached summary for this exact content, or ``None``."""
        stmt = select(Summary).where(
            Summary.file_path == file_path,
            Summary.content_hash == content_hash,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def set(
        self,
        *,
        file_path: str,
        content_hash: str,
        summary: str,
        provider: str,
        model: str,
    ) -> Summary:
        """Insert (or return existing) cached summary for this content.

        Concurrent generation could race on the unique constraint; if a row
        already exists we simply return it rather than failing.
        """
        existing = self.get(file_path, content_hash)
        if existing is not None:
            return existing

        record = Summary(
            file_path=file_path,
            content_hash=content_hash,
            summary=summary,
            provider=provider,
            model=model,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def invalidate(self, file_path: str) -> int:
        """Delete all cached summaries for ``file_path``. Returns rows removed."""
        rows = (
            self._db.execute(
                select(Summary).where(Summary.file_path == file_path)
            )
            .scalars()
            .all()
        )
        for row in rows:
            self._db.delete(row)
        self._db.commit()
        return len(rows)
