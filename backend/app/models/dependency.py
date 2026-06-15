"""Dependency model — a directed edge between two files (source imports target)."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Dependency(Base):
    """A resolved import relationship between two files in the same repository.

    Only edges whose import could be resolved to an actual file in the scanned
    set are persisted; the raw import string is kept for display/debugging.
    """

    __tablename__ = "dependencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("file_nodes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("file_nodes.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # The original import statement token (e.g. "./utils" or "os.path").
    raw_import: Mapped[str] = mapped_column(String(512), default="", nullable=False)

    source: Mapped["FileNode"] = relationship(
        back_populates="outgoing", foreign_keys=[source_id]
    )
    target: Mapped["FileNode"] = relationship(foreign_keys=[target_id])

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Dependency {self.source_id} -> {self.target_id} ({self.raw_import!r})>"
