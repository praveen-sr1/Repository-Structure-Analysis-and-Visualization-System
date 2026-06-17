"""Repository scanner.

Walks a local directory recursively, applying configurable ignore rules, and
returns a lightweight description of every supported source file found. The
scanner deliberately performs **no parsing and no code execution** — it only
discovers files, reads their text, and computes a content hash. Parsing and
metric calculation happen downstream in the analysis service.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config import settings
from app.utils.file_utils import detect_language, iter_source_files, read_text_safe
from app.utils.hashing import hash_text


@dataclass(slots=True)
class ScannedFile:
    """A single discovered source file and its raw text content."""

    path: Path                 # absolute path on disk
    relative_path: str         # path relative to the repository root
    name: str
    extension: str
    language: str
    content: str
    content_hash: str


@dataclass(slots=True)
class ScanResult:
    """The outcome of scanning a repository directory."""

    root: Path
    name: str
    files: list[ScannedFile] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)


class RepositoryScanner:
    """Discovers and reads supported source files under a repository root."""

    def __init__(
        self,
        *,
        ignored_dirs: set[str] | None = None,
        max_file_size: int | None = None,
    ) -> None:
        self._ignored_dirs = ignored_dirs or set(settings.ignored_dirs)
        self._max_file_size = (
            max_file_size if max_file_size is not None else settings.max_file_size
        )

    def scan(self, root: str | Path) -> ScanResult:
        """Scan ``root`` and return every readable, supported source file.

        Raises:
            FileNotFoundError: if ``root`` does not exist.
            NotADirectoryError: if ``root`` is not a directory.
        """
        root_path = Path(root).expanduser().resolve()
        if not root_path.exists():
            raise FileNotFoundError(f"Path does not exist: {root_path}")
        if not root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root_path}")

        result = ScanResult(root=root_path, name=root_path.name)

        for file_path in iter_source_files(
            root_path,
            ignored_dirs=self._ignored_dirs,
            max_size=self._max_file_size,
        ):
            content = read_text_safe(file_path, max_size=self._max_file_size)
            if content is None:
                # Binary, too large, or unreadable — skip silently.
                continue

            relative = file_path.relative_to(root_path).as_posix()
            result.files.append(
                ScannedFile(
                    path=file_path,
                    relative_path=relative,
                    name=file_path.name,
                    extension=file_path.suffix.lower(),
                    language=detect_language(file_path),
                    content=content,
                    content_hash=hash_text(content),
                )
            )

        # Deterministic ordering keeps graph output stable across scans.
        result.files.sort(key=lambda f: f.relative_path)
        return result
