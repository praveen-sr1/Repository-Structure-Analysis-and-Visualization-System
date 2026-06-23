"""Graph service — reads persisted analysis and shapes it into API responses."""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Dependency, FileNode, Repository
from app.schemas.graph import GraphEdge, GraphNode, GraphResponse, NodeMetrics
from app.schemas.metrics import FileMetrics
from app.schemas.repository import LanguageBreakdown, RepositoryStats


class GraphService:
    """Builds graph, stats, and metrics responses from stored data."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _files(self, repository_id: int) -> list[FileNode]:
        stmt = (
            select(FileNode)
            .where(FileNode.repository_id == repository_id)
            .order_by(FileNode.path)
        )
        return list(self._db.execute(stmt).scalars().all())

    def _dependencies(self, repository_id: int) -> list[Dependency]:
        stmt = select(Dependency).where(Dependency.repository_id == repository_id)
        return list(self._db.execute(stmt).scalars().all())

    def get_graph(self, repository: Repository) -> GraphResponse:
        """Return nodes + edges for a repository, keyed by repo-relative path."""
        files = self._files(repository.id)
        id_to_path = {f.id: f.path for f in files}

        nodes = [
            GraphNode(
                id=f.path,
                label=f.name,
                path=f.path,
                language=f.language,
                metrics=NodeMetrics(
                    lines_of_code=f.lines_of_code,
                    num_imports=f.num_imports,
                    num_classes=f.num_classes,
                    num_functions=f.num_functions,
                    cyclomatic_complexity=f.cyclomatic_complexity,
                ),
            )
            for f in files
        ]

        edges: list[GraphEdge] = []
        for dep in self._dependencies(repository.id):
            source = id_to_path.get(dep.source_id)
            target = id_to_path.get(dep.target_id)
            if source is None or target is None:
                continue
            edges.append(
                GraphEdge(
                    id=f"{dep.source_id}-{dep.target_id}",
                    source=source,
                    target=target,
                    raw_import=dep.raw_import,
                )
            )

        return GraphResponse(
            repository_id=repository.id, nodes=nodes, edges=edges
        )

    def get_stats(self, repository: Repository) -> RepositoryStats:
        """Compute aggregate statistics and a per-language breakdown."""
        files = self._files(repository.id)

        by_language_files: dict[str, int] = defaultdict(int)
        by_language_lines: dict[str, int] = defaultdict(int)
        total_classes = total_functions = total_complexity = 0

        for f in files:
            by_language_files[f.language] += 1
            by_language_lines[f.language] += f.lines_of_code
            total_classes += f.num_classes
            total_functions += f.num_functions
            total_complexity += f.cyclomatic_complexity

        avg_complexity = total_complexity / len(files) if files else 0.0
        languages = [
            LanguageBreakdown(
                language=lang,
                files=by_language_files[lang],
                lines=by_language_lines[lang],
            )
            for lang in sorted(by_language_files)
        ]

        return RepositoryStats(
            repository_id=repository.id,
            total_files=len(files),
            total_lines=sum(f.lines_of_code for f in files),
            total_dependencies=repository.total_dependencies,
            total_classes=total_classes,
            total_functions=total_functions,
            average_complexity=round(avg_complexity, 2),
            languages=languages,
        )

    def get_file(self, repository_id: int, file_path: str) -> FileNode | None:
        stmt = select(FileNode).where(
            FileNode.repository_id == repository_id,
            FileNode.path == file_path,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def get_file_metrics(
        self, repository_id: int, file_path: str
    ) -> FileMetrics | None:
        node = self.get_file(repository_id, file_path)
        if node is None:
            return None
        return FileMetrics.model_validate(node)
