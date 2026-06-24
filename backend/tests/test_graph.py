"""Tests for the import resolver and graph builder."""
from __future__ import annotations

from app.graph.builder import GraphBuilder
from app.graph.resolver import ImportResolver
from app.services.scanner import RepositoryScanner


def test_resolver_resolves_python_dotted_import():
    resolver = ImportResolver(["pkg/utils.py", "main.py", "pkg/__init__.py"])
    assert resolver.resolve("main.py", "pkg.utils") == "pkg/utils.py"


def test_resolver_resolves_relative_js_import():
    resolver = ImportResolver(["pkg/utils.js", "app.js"])
    assert resolver.resolve("app.js", "./pkg/utils") == "pkg/utils.js"


def test_resolver_resolves_python_relative_import():
    resolver = ImportResolver(["pkg/utils.py", "pkg/main.py"])
    assert resolver.resolve("pkg/main.py", ".utils") == "pkg/utils.py"


def test_resolver_returns_none_for_external_import():
    resolver = ImportResolver(["main.py"])
    assert resolver.resolve("main.py", "os") is None
    assert resolver.resolve("main.py", "numpy") is None


def test_resolver_resolves_directory_index():
    resolver = ImportResolver(["pkg/index.ts", "app.ts"])
    assert resolver.resolve("app.ts", "./pkg") == "pkg/index.ts"


def test_graph_builder_produces_nodes_and_edges(sample_repo):
    scan = RepositoryScanner().scan(sample_repo)
    build = GraphBuilder().build(scan)

    paths = {f.path for f in build.files}
    assert {"main.py", "pkg/utils.py", "app.js"} <= paths

    # main.py imports pkg/utils.py -> an internal edge must exist.
    edge_pairs = {(e.source, e.target) for e in build.edges}
    assert ("main.py", "pkg/utils.py") in edge_pairs
    assert ("app.js", "pkg/utils.py") in edge_pairs


def test_graph_builder_computes_metrics(sample_repo):
    scan = RepositoryScanner().scan(sample_repo)
    build = GraphBuilder().build(scan)
    by_path = {f.path: f for f in build.files}

    utils = by_path["pkg/utils.py"]
    assert utils.num_classes == 1      # class Helper
    assert utils.num_functions == 1    # def add
    assert utils.lines_of_code > 0
    # The actual declared names are captured, not just the counts.
    assert "Helper" in utils.class_names
    assert "add" in utils.function_names
