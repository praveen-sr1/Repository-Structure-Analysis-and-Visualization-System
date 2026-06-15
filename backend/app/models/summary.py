"""Summary model — cached AI explanation for a file at a specific content hash."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Summary(Base):
    """A cached AI-generated explanation, keyed by file path + content hash.

    The (path, content_hash) pair is unique: when a file changes, its hash
    changes, so a new row is generated instead of serving a stale summary.
    """

    __tablename__ = "summaries"
    __table_args__ = (
        UniqueConstraint("file_path", "content_hash", name="uq_summary_path_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    provider: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    model: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Summary path={self.file_path!r} hash={self.content_hash[:8]}>"
