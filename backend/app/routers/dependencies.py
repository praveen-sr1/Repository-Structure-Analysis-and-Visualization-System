"""Shared FastAPI dependencies and helpers for routers."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Repository
from app.services.analysis_service import AnalysisService
from app.services.graph_service import GraphService


def get_analysis_service(db: Session = Depends(get_db)) -> AnalysisService:
    return AnalysisService(db)


def get_graph_service(db: Session = Depends(get_db)) -> GraphService:
    return GraphService(db)


def get_repository_or_404(
    repository_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> Repository:
    """Resolve a repository by id or raise 404."""
    repository = service.get_repository(repository_id)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository {repository_id} not found.",
        )
    return repository
