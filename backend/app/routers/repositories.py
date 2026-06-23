"""Repository routers: scan, list, get, rescan, delete."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.dependencies import (
    get_analysis_service,
    get_repository_or_404,
)
from app.models import Repository
from app.schemas.repository import (
    RepositorySummary,
    ScanRequest,
    ScanResponse,
)
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/repositories", tags=["repositories"])


def _to_summary(repo: Repository) -> RepositorySummary:
    return RepositorySummary.model_validate(repo)


@router.post(
    "/scan",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Scan (or refresh) a local repository",
)
def scan_repository(
    payload: ScanRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> ScanResponse:
    """Scan a local directory and persist its dependency analysis."""
    try:
        repository, build = service.scan_repository(payload.path, payload.name)
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    return ScanResponse(
        repository=_to_summary(repository),
        nodes_created=len(build.files),
        edges_created=len(build.edges),
    )


@router.get(
    "",
    response_model=list[RepositorySummary],
    summary="List analysed repositories",
)
def list_repositories(
    service: AnalysisService = Depends(get_analysis_service),
) -> list[RepositorySummary]:
    return [_to_summary(r) for r in service.list_repositories()]


@router.get(
    "/{repository_id}",
    response_model=RepositorySummary,
    summary="Get a repository by id",
)
def get_repository(
    repository: Repository = Depends(get_repository_or_404),
) -> RepositorySummary:
    return _to_summary(repository)


@router.post(
    "/{repository_id}/rescan",
    response_model=ScanResponse,
    summary="Re-run analysis for an existing repository",
)
def rescan_repository(
    repository_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> ScanResponse:
    try:
        repository, build = service.rescan_repository(repository_id)
    except LookupError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except FileNotFoundError as exc:
        # The stored path no longer exists on disk.
        raise HTTPException(
            status.HTTP_410_GONE,
            f"Repository path is no longer available: {exc}",
        ) from exc

    return ScanResponse(
        repository=_to_summary(repository),
        nodes_created=len(build.files),
        edges_created=len(build.edges),
        message="Repository rescanned successfully.",
    )


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a repository and its analysis",
)
def delete_repository(
    repository_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> None:
    if not service.delete_repository(repository_id):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Repository {repository_id} not found."
        )
