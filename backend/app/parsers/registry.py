"""Parser registry — maps language names to parser instances.

A module-level :data:`registry` is created and populated with every built-in
parser at import time. Adding a new language is a two-line change: implement a
``BaseParser`` subclass and register it here.
"""
from __future__ import annotations

from app.parsers.base import BaseParser, ParseResult


class ParserRegistry:
    """Holds parser instances keyed by canonical language name."""

    def __init__(self) -> None:
        self._parsers: dict[str, BaseParser] = {}

    def register(self, parser: BaseParser) -> None:
        """Register ``parser`` under its declared language."""
        self._parsers[parser.language] = parser

    def get(self, language: str) -> BaseParser | None:
        """Return the parser for ``language`` or ``None`` if unsupported."""
        return self._parsers.get(language)

    def supports(self, language: str) -> bool:
        return language in self._parsers

    def parse(self, language: str, source: str) -> ParseResult:
        """Parse ``source`` using the parser for ``language``.

        Returns an empty :class:`ParseResult` when the language is unsupported,
        so callers can treat every file uniformly.
        """
        parser = self._parsers.get(language)
        if parser is None:
            return ParseResult()
        return parser.safe_parse(source)

    @property
    def languages(self) -> list[str]:
        return sorted(self._parsers)


# ---------------------------------------------------------------------------
# Build and populate the shared registry.
# ---------------------------------------------------------------------------
registry = ParserRegistry()


def _register_builtin_parsers() -> None:
    """Import and register all built-in parsers.

    Imports are local to avoid a circular import at module load time (parsers
    import :mod:`app.parsers.base`, which this module also imports).
    """
    from app.parsers.c_cpp import CCppParser
    from app.parsers.java import JavaParser
    from app.parsers.javascript import JavaScriptParser
    from app.parsers.python import PythonParser
    from app.parsers.typescript import TypeScriptParser

    for parser in (
        PythonParser(),
        JavaScriptParser(),
        TypeScriptParser(),
        JavaParser(),
        CCppParser(),
    ):
        registry.register(parser)

    # The C/C++ parser handles both languages; ``detect_language`` reports plain
    # C sources/headers as "c", so alias that to the same parser instance.
    registry._parsers["c"] = registry._parsers["cpp"]


_register_builtin_parsers()
