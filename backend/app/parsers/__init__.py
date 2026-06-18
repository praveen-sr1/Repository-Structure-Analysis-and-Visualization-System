"""Static source parsers.

Each parser extracts imports, class definitions, and function definitions from a
file's text **without executing it**. Parsers are keyed by language in the
:data:`registry` and selected automatically by the analysis service.
"""
from app.parsers.base import BaseParser, ParseResult
from app.parsers.registry import ParserRegistry, registry

__all__ = ["BaseParser", "ParseResult", "ParserRegistry", "registry"]
