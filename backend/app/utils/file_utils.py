"""Filesystem helpers: language detection, safe reading, and directory walking.

None of these helpers execute repository code — they only read file contents as
text and inspect file extensions.
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

# Map of file extension -> canonical language name.
EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
}


def detect_language(path: str | os.PathLike[str]) -> str:
    """Return the canonical language for ``path`` based on its extension."""
    ext = Path(path).suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(ext, "unknown")


def is_supported_source(path: str | os.PathLike[str]) -> bool:
    """True when the file extension maps to a language we can parse."""
    return Path(path).suffix.lower() in EXTENSION_LANGUAGE_MAP


def read_text_safe(
    path: str | os.PathLike[str], *, max_size: int | None = None
) -> str | None:
    """Read a file as UTF-8 text, returning ``None`` if it cannot be read.

    Binary files, files exceeding ``max_size``, and files that raise OS errors
    are skipped gracefully (returns ``None``) rather than raising.
    """
    p = Path(path)
    try:
        if max_size is not None and p.stat().st_size > max_size:
            return None
        return p.read_text(encoding="utf-8", errors="strict")
    except (UnicodeDecodeError, OSError, ValueError):
        return None


def iter_source_files(
    root: str | os.PathLike[str],
    *,
    ignored_dirs: set[str],
    max_size: int | None = None,
) -> Iterator[Path]:
    """Yield supported source files under ``root``, skipping ignored directories.

    Directory pruning happens in-place on ``os.walk``'s dirnames list so that
    ignored trees (e.g. ``node_modules``) are never descended into.
    """
    root_path = Path(root)
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune ignored directories in place (also skips hidden dirs like .git).
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if not is_supported_source(file_path):
                continue
            if max_size is not None:
                try:
                    if file_path.stat().st_size > max_size:
                        continue
                except OSError:
                    continue
            yield file_path
