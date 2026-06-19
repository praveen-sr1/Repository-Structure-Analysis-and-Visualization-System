"""JavaScript parser (regex-based static analysis).

Handles ES module ``import``/``export ... from`` statements, CommonJS
``require(...)`` calls, and dynamic ``import(...)`` expressions, plus class and
function declarations. It does not execute the code.
"""
from __future__ import annotations

import re

from app.parsers._textutils import (
    strip_c_style_comments,
    unique_preserving_order,
)
from app.parsers.base import BaseParser, ParseResult

# `import ... from 'x'`  and  `export ... from 'x'`
_IMPORT_FROM = re.compile(
    r"""(?:import|export)\b[^;'"]*?\bfrom\s*['"]([^'"]+)['"]""", re.DOTALL
)
# bare `import 'x'` (side-effect import)
_IMPORT_BARE = re.compile(r"""import\s*['"]([^'"]+)['"]""")
# `require('x')`
_REQUIRE = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")
# dynamic `import('x')`
_DYNAMIC_IMPORT = re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""")

_CLASS = re.compile(r"\bclass\s+([A-Za-z_$][\w$]*)")
# function declarations + `const foo = (…) =>` / `const foo = function`
_FUNCTION = re.compile(
    r"\bfunction\s*\*?\s+([A-Za-z_$][\w$]*)"
    r"|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>)"
)


class JavaScriptParser(BaseParser):
    """Extracts imports, classes, and functions from JavaScript source."""

    language = "javascript"

    def parse(self, source: str) -> ParseResult:
        code = strip_c_style_comments(source)
        result = ParseResult()

        imports: list[str] = []
        for pattern in (_IMPORT_FROM, _IMPORT_BARE, _REQUIRE, _DYNAMIC_IMPORT):
            imports.extend(pattern.findall(code))
        result.imports = unique_preserving_order(imports)

        result.classes = unique_preserving_order(_CLASS.findall(code))

        functions: list[str] = []
        for decl, assigned in _FUNCTION.findall(code):
            name = decl or assigned
            if name:
                functions.append(name)
        result.functions = unique_preserving_order(functions)

        return result
