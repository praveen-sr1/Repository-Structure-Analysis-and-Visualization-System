"""File metrics router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.routers.dependencies import get_graph_service, get_repository_or_404
from app.models import Repository
from app.schemas.metrics import FileMetrics
from app.services.graph_service import GraphService

router = APIRouter(prefix="/repositories/{repository_id}", tags=["metrics"])


@router.get(
    "/files/metrics",
    response_model=FileMetrics,
    summary="Get metrics for a single file",
)
def get_file_metrics(
    path: str = Query(..., description="Repository-relative file path."),
    repository: Repository = Depends(get_repository_or_404),
    graph_service: GraphService = Depends(get_graph_service),
) -> FileMetrics:
    metrics = graph_service.get_file_metrics(repository.id, path)
    if metrics is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"File not found in repository: {path}",
        )
    return metrics
