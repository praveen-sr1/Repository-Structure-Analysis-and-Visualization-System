"""FileNode model — one row per analysed source file."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FileNode(Base):
    """A single file within a repository, with its computed metrics.

    Metrics are stored denormalised on the node so the graph endpoint can return
    everything the frontend needs without recomputing on each request.
    """

    __tablename__ = "file_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Path relative to the repository root (stable identifier within a repo).
    path: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    language: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)

    # Content hash for AI-summary cache invalidation.
    content_hash: Mapped[str] = mapped_column(String(64), default="", nullable=False)

    # ---- Metrics ----
    lines_of_code: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    num_imports: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    num_classes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    num_functions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Names of the declared classes/functions (stored as JSON arrays). SQLAlchemy
    # serialises these to TEXT for SQLite and returns them as Python lists.
    class_names: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    function_names: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    repository: Mapped["Repository"] = relationship(back_populates="files")

    # Edges where this file is the source ("imports from").
    outgoing: Mapped[list["Dependency"]] = relationship(
        back_populates="source",
        foreign_keys="Dependency.source_id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<FileNode id={self.id} path={self.path!r} loc={self.lines_of_code}>"
