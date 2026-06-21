"""Import resolver.

Turns raw import tokens (as produced by the parsers) into concrete target files
within the scanned repository. Only imports that resolve to a file actually
present in the repo become graph edges; external/library imports are ignored for
edge-building (they are still reflected in each file's ``num_imports`` metric).

Resolution is path-based and language-aware but never executes code or touches
the network — it only consults the set of relative paths discovered by the
scanner.
"""
from __future__ import annotations

from pathlib import PurePosixPath


class ImportResolver:
    """Resolves import tokens to repository-relative file paths.

    The resolver builds several lookup indexes from the known file set so that
    imports written in different styles (relative JS paths, dotted Python
    modules, Java packages, C include paths) can all be matched efficiently.
    """

    # Extensions tried when an import omits the file extension.
    _CANDIDATE_EXTENSIONS = (
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".java",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
        ".cc",
        ".hh",
    )
    # Index files tried when an import points at a directory (JS/TS packages).
    _INDEX_BASENAMES = ("index", "__init__")

    def __init__(self, relative_paths: list[str]) -> None:
        # All known repo-relative POSIX paths.
        self._paths: set[str] = set(relative_paths)

        # path-without-extension -> actual path (for extensionless imports).
        self._by_stem_path: dict[str, str] = {}
        # dotted module path (a/b/c -> "a.b.c") -> actual path (Python/Java).
        self._by_dotted: dict[str, str] = {}
        # basename (with and without extension) -> list of actual paths.
        self._by_basename: dict[str, list[str]] = {}

        for path in self._paths:
            p = PurePosixPath(path)
            stem_path = path[: -len(p.suffix)] if p.suffix else path
            self._by_stem_path.setdefault(stem_path, path)
            self._by_dotted.setdefault(stem_path.replace("/", "."), path)
            self._by_basename.setdefault(p.name, []).append(path)
            self._by_basename.setdefault(p.stem, []).append(path)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def resolve(self, importer_path: str, token: str) -> str | None:
        """Resolve ``token`` imported by ``importer_path`` to a repo path.

        Returns the matched repository-relative path, or ``None`` if the import
        refers to something outside the repository (a third-party/library import).
        """
        token = token.strip()
        if not token:
            return None

        if token.startswith("."):
            return self._resolve_relative(importer_path, token)

        # Bare/absolute style: try path-like, then dotted, then C-style include.
        return (
            self._resolve_pathlike(token)
            or self._resolve_dotted(token)
            or self._resolve_include(token)
        )

    # ------------------------------------------------------------------ #
    # Resolution strategies
    # ------------------------------------------------------------------ #
    def _resolve_relative(self, importer_path: str, token: str) -> str | None:
        """Resolve JS/TS/Python relative imports like ``./utils`` or ``..pkg.mod``."""
        importer_dir = PurePosixPath(importer_path).parent

        if "/" in token or token in (".", ".."):
            # JS/TS style: ./foo, ../bar/baz
            target = (importer_dir / token).as_posix()
            return self._match_path(self._normalise(target))

        # Python style: leading dots denote how many packages to go up.
        leading = len(token) - len(token.lstrip("."))
        remainder = token[leading:]
        base = importer_dir
        # One dot = current package; each extra dot climbs one level.
        for _ in range(leading - 1):
            base = base.parent
        sub = remainder.replace(".", "/") if remainder else ""
        target = (base / sub).as_posix() if sub else base.as_posix()
        return self._match_path(self._normalise(target))

    def _resolve_pathlike(self, token: str) -> str | None:
        """Resolve imports that look like paths (contain ``/``)."""
        if "/" not in token:
            return None
        return self._match_path(self._normalise(token))

    def _resolve_dotted(self, token: str) -> str | None:
        """Resolve dotted modules (``pkg.sub.mod``) for Python/Java."""
        if "." not in token:
            # Single bare name: match by basename if unambiguous.
            return self._match_basename(token)
        # Java wildcard imports (``a.b.*``) → drop the star.
        cleaned = token[:-2] if token.endswith(".*") else token
        if cleaned in self._by_dotted:
            return self._by_dotted[cleaned]
        # Try as a path too (``a/b/mod``).
        as_path = cleaned.replace(".", "/")
        return self._match_path(as_path) or self._match_basename(
            PurePosixPath(as_path).name
        )

    def _resolve_include(self, token: str) -> str | None:
        """Resolve C/C++ ``#include`` targets (``dir/header.h`` or ``header.h``)."""
        direct = self._match_path(self._normalise(token))
        if direct:
            return direct
        return self._match_basename(PurePosixPath(token).name)

    # ------------------------------------------------------------------ #
    # Matching helpers
    # ------------------------------------------------------------------ #
    def _match_path(self, path: str) -> str | None:
        """Match a path that may or may not include its extension/index file."""
        if path in self._paths:
            return path
        if path in self._by_stem_path:
            return self._by_stem_path[path]
        # Try appending known extensions.
        for ext in self._CANDIDATE_EXTENSIONS:
            candidate = f"{path}{ext}"
            if candidate in self._paths:
                return candidate
        # Try directory index files (foo -> foo/index.ts, foo/__init__.py).
        for base in self._INDEX_BASENAMES:
            for ext in self._CANDIDATE_EXTENSIONS:
                candidate = f"{path}/{base}{ext}"
                if candidate in self._paths:
                    return candidate
        return None

    def _match_basename(self, name: str) -> str | None:
        """Match by file basename, but only when it is unambiguous."""
        for key in (name, *(f"{name}{ext}" for ext in self._CANDIDATE_EXTENSIONS)):
            matches = self._by_basename.get(key)
            if matches and len(set(matches)) == 1:
                return matches[0]
        return None

    @staticmethod
    def _normalise(path: str) -> str:
        """Collapse ``.``/``..`` segments into a clean POSIX path."""
        parts: list[str] = []
        for segment in path.split("/"):
            if segment in ("", "."):
                continue
            if segment == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(segment)
        return "/".join(parts)
