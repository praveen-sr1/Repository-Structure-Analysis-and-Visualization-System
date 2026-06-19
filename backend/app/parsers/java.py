"""Java parser (regex-based static analysis).

Extracts ``import`` statements, type declarations (class/interface/enum/record),
and method declarations without executing the code.
"""
from __future__ import annotations

import re

from app.parsers._textutils import (
    strip_c_style_comments,
    strip_string_literals,
    unique_preserving_order,
)
from app.parsers.base import BaseParser, ParseResult

# `import a.b.C;` and `import static a.b.C.d;`
_IMPORT = re.compile(r"\bimport\s+(?:static\s+)?([\w.]+(?:\.\*)?)\s*;")
# class / interface / enum / record / annotation-type declarations
_TYPE_DECL = re.compile(
    r"\b(?:class|interface|enum|record)\s+([A-Za-z_$][\w$]*)"
)
# Method declarations: modifiers, return type, name, parameter list.
_METHOD = re.compile(
    r"(?:public|private|protected|static|final|abstract|synchronized|native|default|\s)+"
    r"[\w<>\[\],.?$ ]+\s+([A-Za-z_$][\w$]*)\s*\([^;{}]*\)\s*(?:throws[\w,.\s]+)?\{"
)

# Java keywords that can precede a "(" but are not methods.
_CONTROL_KEYWORDS = {"if", "for", "while", "switch", "catch", "synchronized", "return"}


class JavaParser(BaseParser):
    """Extracts imports, type declarations, and methods from Java source."""

    language = "java"

    def parse(self, source: str) -> ParseResult:
        code = strip_string_literals(strip_c_style_comments(source))
        result = ParseResult()

        result.imports = unique_preserving_order(_IMPORT.findall(code))
        result.classes = unique_preserving_order(_TYPE_DECL.findall(code))

        methods = [
            name
            for name in _METHOD.findall(code)
            if name not in _CONTROL_KEYWORDS
        ]
        result.functions = unique_preserving_order(methods)
        return result
