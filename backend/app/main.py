"""FastAPI application entrypoint.

Wires configuration, database initialisation, CORS, exception handling, and all
API routers under the ``/api`` prefix.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.config import settings
from app.database import init_db
from app.routers import graph, health, metrics, repositories, summaries

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialise the database schema on startup."""
    logger.info("Starting %s v%s", settings.app_name, __version__)
    init_db()
    logger.info("Database initialised at %s", settings.database_url)
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Static analysis & dependency visualisation for local repositories. "
        "Scan a repo, explore its dependency graph, inspect file metrics, and "
        "get AI explanations of individual files."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Convert unexpected errors into a clean JSON 500 response."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


# ---- Routers (all under /api) ----
API_PREFIX = "/api"
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(repositories.router, prefix=API_PREFIX)
app.include_router(graph.router, prefix=API_PREFIX)
app.include_router(metrics.router, prefix=API_PREFIX)
app.include_router(summaries.router, prefix=API_PREFIX)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Root endpoint with basic service metadata."""
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
