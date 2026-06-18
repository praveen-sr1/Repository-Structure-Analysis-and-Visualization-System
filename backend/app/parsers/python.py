"""Python parser built on the standard-library :mod:`ast` module.

``ast.parse`` compiles source into an abstract syntax tree without executing it,
which makes it both accurate and safe for analysing untrusted repositories.
"""
from __future__ import annotations

import ast

from app.parsers.base import BaseParser, ParseResult


class PythonParser(BaseParser):
    """Extracts imports, classes, and functions from Python source."""

    language = "python"

    def parse(self, source: str) -> ParseResult:
        tree = ast.parse(source)
        result = ParseResult()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # `import a, b.c` -> tokens "a", "b.c"
                for alias in node.names:
                    result.imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                # Preserve relative-import dots so the resolver can locate the
                # sibling/parent module: `from .utils import x` -> ".utils".
                prefix = "." * (node.level or 0)
                module = node.module or ""
                token = f"{prefix}{module}" if module else prefix
                if token:
                    result.imports.append(token)

            elif isinstance(node, ast.ClassDef):
                result.classes.append(node.name)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.functions.append(node.name)

        return result
