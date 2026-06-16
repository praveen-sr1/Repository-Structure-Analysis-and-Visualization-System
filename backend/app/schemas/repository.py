"""Schemas for repository scanning, listing, and statistics."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanRequest(BaseModel):
    """Request body for scanning (or rescanning) a local repository."""

    path: str = Field(..., min_length=1, description="Absolute path to a local repo.")
    name: str | None = Field(
        None, description="Optional display name; defaults to the folder name."
    )

    @field_validator("path")
    @classmethod
    def _strip_path(cls, value: str) -> str:
        return value.strip()


class RepositorySummary(BaseModel):
    """Lightweight repository record used in list responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: str
    total_files: int = 0
    total_lines: int = 0
    total_dependencies: int = 0
    created_at: datetime | None = None
    last_scanned_at: datetime | None = None


class ScanResponse(BaseModel):
    """Result of a scan operation."""

    repository: RepositorySummary
    nodes_created: int = 0
    edges_created: int = 0
    message: str = "Scan completed successfully."


class LanguageBreakdown(BaseModel):
    """File and line counts grouped by language."""

    language: str
    files: int = 0
    lines: int = 0


class RepositoryStats(BaseModel):
    """Aggregate statistics for a repository."""

    repository_id: int
    total_files: int = 0
    total_lines: int = 0
    total_dependencies: int = 0
    total_classes: int = 0
    total_functions: int = 0
    average_complexity: float = 0.0
    languages: list[LanguageBreakdown] = Field(default_factory=list)
