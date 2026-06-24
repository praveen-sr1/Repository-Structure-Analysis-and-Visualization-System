"""Tests for the repository scanner."""
from __future__ import annotations

from app.services.scanner import RepositoryScanner


def test_scanner_discovers_supported_files(sample_repo):
    scanner = RepositoryScanner()
    result = scanner.scan(sample_repo)

    paths = {f.relative_path for f in result.files}
    assert "main.py" in paths
    assert "pkg/utils.py" in paths
    assert "app.js" in paths


def test_scanner_ignores_configured_directories(sample_repo):
    scanner = RepositoryScanner()
    result = scanner.scan(sample_repo)

    # Nothing from node_modules should appear.
    assert all("node_modules" not in f.relative_path for f in result.files)


def test_scanner_sets_language_and_hash(sample_repo):
    scanner = RepositoryScanner()
    result = scanner.scan(sample_repo)

    by_path = {f.relative_path: f for f in result.files}
    assert by_path["main.py"].language == "python"
    assert by_path["app.js"].language == "javascript"
    assert len(by_path["main.py"].content_hash) == 64  # sha-256 hex


def test_scanner_results_are_sorted(sample_repo):
    scanner = RepositoryScanner()
    result = scanner.scan(sample_repo)
    paths = [f.relative_path for f in result.files]
    assert paths == sorted(paths)


def test_scanner_raises_for_missing_path(tmp_path):
    scanner = RepositoryScanner()
    try:
        scanner.scan(tmp_path / "does-not-exist")
    except FileNotFoundError:
        return
    raise AssertionError("Expected FileNotFoundError")
