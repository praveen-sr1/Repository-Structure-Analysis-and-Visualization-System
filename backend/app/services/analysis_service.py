"""Analysis service — orchestrates scanning, graph building, and persistence.

This is the application-layer coordinator the routers call. It ties together the
scanner, graph builder, and ORM models, and owns the transactional logic for
creating or refreshing a repository's analysis.
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.graph.builder import GraphBuilder, GraphBuildResult
from app.models import Dependency, FileNode, Repository
from app.services.scanner import RepositoryScanner


class AnalysisService:
    """Coordinates a full repository analysis and persists the result."""

    def __init__(
        self,
        db: Session,
        *,
        scanner: RepositoryScanner | None = None,
        builder: GraphBuilder | None = None,
    ) -> None:
        self._db = db
        self._scanner = scanner or RepositoryScanner()
        self._builder = builder or GraphBuilder()

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    def get_repository(self, repository_id: int) -> Repository | None:
        return self._db.get(Repository, repository_id)

    def get_repository_by_path(self, path: str) -> Repository | None:
        resolved = str(Path(path).expanduser().resolve())
        stmt = select(Repository).where(Repository.path == resolved)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_repositories(self) -> list[Repository]:
        stmt = select(Repository).order_by(Repository.last_scanned_at.desc())
        return list(self._db.execute(stmt).scalars().all())

    # ------------------------------------------------------------------ #
    # Commands
    # ------------------------------------------------------------------ #
    def scan_repository(self, path: str, name: str | None = None) -> tuple[Repository, GraphBuildResult]:
        """Scan ``path`` and persist its analysis.

        If a repository with the same resolved path already exists, it is
        refreshed in place (its files and dependencies are replaced). Returns the
        persisted repository and the in-memory build result.

        Raises:
            FileNotFoundError / NotADirectoryError: for invalid paths.
        """
        scan = self._scanner.scan(path)
        build = self._builder.build(scan)
        resolved_path = str(scan.root)

        repository = self.get_repository_by_path(resolved_path)
        if repository is None:
            repository = Repository(name=name or scan.name, path=resolved_path)
            self._db.add(repository)
            self._db.flush()  # assign repository.id
        else:
            # Refresh: clear previous analysis for a clean rebuild.
            if name:
                repository.name = name
            self._clear_repository_data(repository)

        path_to_node = self._persist_nodes(repository, build)
        self._persist_edges(repository, build, path_to_node)

        # Update aggregate stats.
        repository.total_files = len(build.files)
        repository.total_lines = build.total_lines
        repository.total_dependencies = len(build.edges)

        self._db.commit()
        self._db.refresh(repository)
        return repository, build

    def rescan_repository(self, repository_id: int) -> tuple[Repository, GraphBuildResult]:
        """Re-run analysis for an existing repository using its stored path."""
        repository = self.get_repository(repository_id)
        if repository is None:
            raise LookupError(f"Repository {repository_id} not found.")
        return self.scan_repository(repository.path, repository.name)

    def delete_repository(self, repository_id: int) -> bool:
        repository = self.get_repository(repository_id)
        if repository is None:
            return False
        self._db.delete(repository)
        self._db.commit()
        return True

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _clear_repository_data(self, repository: Repository) -> None:
        """Remove all file nodes and dependencies for a repository."""
        for dependency in list(
            self._db.execute(
                select(Dependency).where(
                    Dependency.repository_id == repository.id
                )
            ).scalars()
        ):
            self._db.delete(dependency)
        for node in list(
            self._db.execute(
                select(FileNode).where(FileNode.repository_id == repository.id)
            ).scalars()
        ):
            self._db.delete(node)
        self._db.flush()

    def _persist_nodes(
        self, repository: Repository, build: GraphBuildResult
    ) -> dict[str, int]:
        """Persist file nodes and return a path -> node id map."""
        path_to_node: dict[str, int] = {}
        for f in build.files:
            node = FileNode(
                repository_id=repository.id,
                path=f.path,
                name=f.name,
                extension=f.extension,
                language=f.language,
                content_hash=f.content_hash,
                lines_of_code=f.lines_of_code,
                num_imports=f.num_imports,
                num_classes=f.num_classes,
                num_functions=f.num_functions,
                cyclomatic_complexity=f.cyclomatic_complexity,
                class_names=f.class_names,
                function_names=f.function_names,
            )
            self._db.add(node)
            self._db.flush()  # assign node.id
            path_to_node[f.path] = node.id
        return path_to_node

    def _persist_edges(
        self,
        repository: Repository,
        build: GraphBuildResult,
        path_to_node: dict[str, int],
    ) -> None:
        """Persist dependency edges using the path -> node id map."""
        for edge in build.edges:
            source_id = path_to_node.get(edge.source)
            target_id = path_to_node.get(edge.target)
            if source_id is None or target_id is None:
                continue
            self._db.add(
                Dependency(
                    repository_id=repository.id,
                    source_id=source_id,
                    target_id=target_id,
                    raw_import=edge.raw_import,
                )
            )
