"""TypeScript parser.

Extends the JavaScript parser (same import/require syntax) and additionally
recognises TypeScript-only declarations: ``interface``, ``enum``, and
``type`` aliases are counted alongside classes as type declarations.
"""
from __future__ import annotations

import re

from app.parsers._textutils import (
    strip_c_style_comments,
    unique_preserving_order,
)
from app.parsers.base import ParseResult
from app.parsers.javascript import JavaScriptParser

_INTERFACE = re.compile(r"\binterface\s+([A-Za-z_$][\w$]*)")
_ENUM = re.compile(r"\benum\s+([A-Za-z_$][\w$]*)")
_TYPE_ALIAS = re.compile(r"\btype\s+([A-Za-z_$][\w$]*)\s*=")


class TypeScriptParser(JavaScriptParser):
    """JavaScript parser plus TypeScript type declarations."""

    language = "typescript"

    def parse(self, source: str) -> ParseResult:
        result = super().parse(source)
        code = strip_c_style_comments(source)

        type_decls = (
            _INTERFACE.findall(code)
            + _ENUM.findall(code)
            + _TYPE_ALIAS.findall(code)
        )
        # Treat interfaces/enums/type-aliases as class-like declarations.
        result.classes = unique_preserving_order(result.classes + type_decls)
        return result
