"""C / C++ parser (regex-based static analysis).

Extracts ``#include`` directives, class/struct declarations (C++), and function
definitions. Comments and string literals are stripped first; ``#include`` is
matched on the original text since it is a preprocessor directive.
"""
from __future__ import annotations

import re

from app.parsers._textutils import (
    strip_c_style_comments,
    strip_string_literals,
    unique_preserving_order,
)
from app.parsers.base import BaseParser, ParseResult

# #include <header>  or  #include "header"
_INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]', re.MULTILINE)
# class / struct Name (C++)
_TYPE_DECL = re.compile(r"\b(?:class|struct)\s+([A-Za-z_]\w*)")
# Function definitions: `returnType name(args) {`  (definition, not declaration).
_FUNCTION = re.compile(
    r"\b([A-Za-z_]\w*)\s*\([^;{}()]*\)\s*(?:const\s*)?(?:noexcept\s*)?\{"
)

# Keywords that look like calls but are control flow, not function definitions.
_CONTROL_KEYWORDS = {
    "if", "for", "while", "switch", "catch", "return", "sizeof", "do",
}


class CCppParser(BaseParser):
    """Extracts includes, type declarations, and functions from C/C++ source."""

    language = "cpp"  # also handles plain C; registered for both via detection

    def parse(self, source: str) -> ParseResult:
        result = ParseResult()

        # Includes come from the raw source (preprocessor lines).
        result.imports = unique_preserving_order(_INCLUDE.findall(source))

        code = strip_string_literals(strip_c_style_comments(source))
        result.classes = unique_preserving_order(_TYPE_DECL.findall(code))

        functions = [
            name
            for name in _FUNCTION.findall(code)
            if name not in _CONTROL_KEYWORDS
        ]
        result.functions = unique_preserving_order(functions)
        return result
