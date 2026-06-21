"""Graph builder.

Combines the scanner output, language parsers, metric calculators, and the
import resolver into a set of analysed files (nodes) and resolved dependencies
(edges). This is the heart of the analysis pipeline and remains free of any
database or framework concerns so it can be unit-tested in isolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.metrics import count_lines_of_code, estimate_complexity
from app.parsers import registry
from app.services.scanner import ScanResult
from app.graph.resolver import ImportResolver


@dataclass(slots=True)
class AnalyzedFile:
    """A fully analysed file: identity, language, metrics, and raw imports."""

    path: str
    name: str
    extension: str
    language: str
    content_hash: str
    lines_of_code: int = 0
    num_imports: int = 0
    num_classes: int = 0
    num_functions: int = 0
    cyclomatic_complexity: int = 0
    imports: list[str] = field(default_factory=list)
    class_names: list[str] = field(default_factory=list)
    function_names: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Edge:
    """A resolved dependency edge between two repo-relative paths."""

    source: str
    target: str
    raw_import: str


@dataclass(slots=True)
class GraphBuildResult:
    """The complete analysis result for a repository."""

    files: list[AnalyzedFile] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    @property
    def total_lines(self) -> int:
        return sum(f.lines_of_code for f in self.files)


class GraphBuilder:
    """Builds an in-memory dependency graph from a :class:`ScanResult`."""

    def build(self, scan: ScanResult) -> GraphBuildResult:
        analysed: list[AnalyzedFile] = []

        # ---- Pass 1: parse + measure each file ----
        for scanned in scan.files:
            parsed = registry.parse(scanned.language, scanned.content)
            analysed.append(
                AnalyzedFile(
                    path=scanned.relative_path,
                    name=scanned.name,
                    extension=scanned.extension,
                    language=scanned.language,
                    content_hash=scanned.content_hash,
                    lines_of_code=count_lines_of_code(
                        scanned.content, scanned.language
                    ),
                    num_imports=parsed.num_imports,
                    num_classes=parsed.num_classes,
                    num_functions=parsed.num_functions,
                    cyclomatic_complexity=estimate_complexity(
                        scanned.content, scanned.language
                    ),
                    imports=list(parsed.imports),
                    class_names=list(parsed.classes),
                    function_names=list(parsed.functions),
                )
            )

        # ---- Pass 2: resolve imports into edges ----
        resolver = ImportResolver([f.path for f in analysed])
        edges: list[Edge] = []
        seen: set[tuple[str, str]] = set()

        for file in analysed:
            for token in file.imports:
                target = resolver.resolve(file.path, token)
                if target is None or target == file.path:
                    # Unresolved (external) import or self-import — skip edge.
                    continue
                key = (file.path, target)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(Edge(source=file.path, target=target, raw_import=token))

        return GraphBuildResult(files=analysed, edges=edges)
