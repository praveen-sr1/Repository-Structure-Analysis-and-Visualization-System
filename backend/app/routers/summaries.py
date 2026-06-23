"""AI summary router.

On request it reads the file's *current* contents from disk, hashes them, and
checks the local cache. A cache hit returns instantly; a miss calls the
configured AI provider, stores the result keyed by the content hash, and returns
it. Because the cache key is the SHA-256 of the contents, edits automatically
invalidate stale summaries.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.cache.summary_cache import SummaryCache
from app.database import get_db
from app.routers.dependencies import get_graph_service, get_repository_or_404
from app.models import Repository
from app.schemas.summary import SummaryResponse
from app.services.ai_service import AIService, AIServiceError
from app.services.graph_service import GraphService
from app.utils.file_utils import detect_language, read_text_safe
from app.utils.hashing import hash_text

router = APIRouter(prefix="/repositories/{repository_id}", tags=["summaries"])


def _safe_resolve(repo_root: str, relative_path: str) -> Path:
    """Resolve ``relative_path`` under ``repo_root``, blocking path traversal."""
    root = Path(repo_root).resolve()
    target = (root / relative_path).resolve()
    if root != target and root not in target.parents:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Resolved path escapes the repository root."
        )
    return target


@router.get(
    "/files/summary",
    response_model=SummaryResponse,
    summary="Get (or generate) an AI explanation for a file",
)
def get_file_summary(
    path: str = Query(..., description="Repository-relative file path."),
    repository: Repository = Depends(get_repository_or_404),
    graph_service: GraphService = Depends(get_graph_service),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    # The file must be part of the analysed repository.
    node = graph_service.get_file(repository.id, path)
    if node is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"File not found in repository: {path}"
        )

    absolute = _safe_resolve(repository.path, path)
    content = read_text_safe(absolute)
    if content is None:
        raise HTTPException(
            status.HTTP_410_GONE,
            "File is no longer readable on disk; try rescanning the repository.",
        )

    content_hash = hash_text(content)
    cache = SummaryCache(db)

    # 1) Cache lookup keyed by current content hash.
    cached = cache.get(path, content_hash)
    if cached is not None:
        return SummaryResponse(
            file_path=path,
            content_hash=content_hash,
            summary=cached.summary,
            provider=cached.provider,
            model=cached.model,
            cached=True,
            available=True,
        )

    # 2) Generate via AI provider (or report unavailable).
    ai = AIService()
    language = node.language or detect_language(path)
    try:
        result = ai.explain_file(
            file_path=path, language=language, content=content
        )
    except AIServiceError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, f"AI provider error: {exc}"
        ) from exc

    # Only persist real summaries (don't cache the "not configured" notice).
    if result.available:
        cache.set(
            file_path=path,
            content_hash=content_hash,
            summary=result.summary,
            provider=result.provider,
            model=result.model,
        )

    return SummaryResponse(
        file_path=path,
        content_hash=content_hash,
        summary=result.summary,
        provider=result.provider,
        model=result.model,
        cached=False,
        available=result.available,
    )
