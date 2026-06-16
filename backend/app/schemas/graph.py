"""Schemas describing the dependency graph returned to the frontend."""
from __future__ import annotations

from pydantic import BaseModel, Field


class NodeMetrics(BaseModel):
    """Per-file metrics embedded in a graph node."""

    lines_of_code: int = Field(0, ge=0)
    num_imports: int = Field(0, ge=0)
    num_classes: int = Field(0, ge=0)
    num_functions: int = Field(0, ge=0)
    cyclomatic_complexity: int = Field(0, ge=0)


class GraphNode(BaseModel):
    """A single node in the dependency graph (one source file)."""

    id: str = Field(..., description="Stable node id (the repo-relative path).")
    label: str = Field(..., description="Display name (file name).")
    path: str = Field(..., description="Repository-relative path.")
    language: str = Field("unknown")
    metrics: NodeMetrics = Field(default_factory=NodeMetrics)


class GraphEdge(BaseModel):
    """A directed edge: ``source`` imports ``target``."""

    id: str = Field(..., description="Stable edge id.")
    source: str = Field(..., description="Source node id.")
    target: str = Field(..., description="Target node id.")
    raw_import: str = Field("", description="Original import token.")


class GraphResponse(BaseModel):
    """The full graph payload: nodes + edges for a repository."""

    repository_id: int
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
