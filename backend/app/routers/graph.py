"""Graph and statistics routers."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.routers.dependencies import get_graph_service, get_repository_or_404
from app.models import Repository
from app.schemas.graph import GraphResponse
from app.schemas.repository import RepositoryStats
from app.services.graph_service import GraphService

router = APIRouter(prefix="/repositories/{repository_id}", tags=["graph"])


@router.get(
    "/graph",
    response_model=GraphResponse,
    summary="Get the dependency graph (nodes + edges)",
)
def get_graph(
    repository: Repository = Depends(get_repository_or_404),
    graph_service: GraphService = Depends(get_graph_service),
) -> GraphResponse:
    return graph_service.get_graph(repository)


@router.get(
    "/stats",
    response_model=RepositoryStats,
    summary="Get aggregate statistics for a repository",
)
def get_stats(
    repository: Repository = Depends(get_repository_or_404),
    graph_service: GraphService = Depends(get_graph_service),
) -> RepositoryStats:
    return graph_service.get_stats(repository)
