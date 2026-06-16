"""Schemas for AI summary responses."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """An AI-generated (or cached) explanation of a file."""

    file_path: str
    content_hash: str
    summary: str
    provider: str = ""
    model: str = ""
    cached: bool = Field(False, description="True if served from the local cache.")
    available: bool = Field(
        True, description="False when no AI provider is configured."
    )
