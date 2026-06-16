"""Schemas for per-file metrics responses."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FileMetrics(BaseModel):
    """Detailed metrics for a single file."""

    model_config = ConfigDict(from_attributes=True)

    path: str
    name: str
    language: str = "unknown"
    lines_of_code: int = Field(0, ge=0)
    num_imports: int = Field(0, ge=0)
    num_classes: int = Field(0, ge=0)
    num_functions: int = Field(0, ge=0)
    cyclomatic_complexity: int = Field(0, ge=0)
    class_names: list[str] = Field(default_factory=list)
    function_names: list[str] = Field(default_factory=list)
