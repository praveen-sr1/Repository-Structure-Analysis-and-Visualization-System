"""Approximate cyclomatic complexity.

Cyclomatic complexity ≈ 1 + (number of decision points). For Python we count
decision nodes precisely via the AST; for other languages we count branching
keywords and boolean operators on comment/string-stripped source.

These are approximations intended for comparing relative complexity between
files, not for formal certification.
"""
from __future__ import annotations

import ast
import re

from app.parsers._textutils import strip_c_style_comments, strip_string_literals

# Branching constructs for non-Python languages (word-boundary matched).
_KEYWORD_PATTERN = re.compile(
    r"\b(if|else\s+if|elif|for|while|case|catch|except)\b"
)
# Boolean / ternary operators that introduce additional paths.
_OPERATOR_PATTERN = re.compile(r"&&|\|\||\?(?!\.)|\band\b|\bor\b")

# AST node types that each add one decision point in Python.
_PY_DECISION_NODES: tuple[type[ast.AST], ...] = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncWith,
    ast.Assert,
    ast.comprehension,
    ast.IfExp,
)


def estimate_complexity(source: str, language: str = "unknown") -> int:
    """Return an approximate cyclomatic complexity for ``source``."""
    if language == "python":
        return _python_complexity(source)
    return _keyword_complexity(source)


def _python_complexity(source: str) -> int:
    """Precise-ish complexity for Python using the AST."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _keyword_complexity(source)

    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, _PY_DECISION_NODES):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            # `a and b and c` adds (operands - 1) decision points.
            complexity += len(node.values) - 1
    return complexity


def _keyword_complexity(source: str) -> int:
    """Keyword/operator-based complexity for non-Python languages."""
    code = strip_string_literals(strip_c_style_comments(source))
    complexity = 1
    complexity += len(_KEYWORD_PATTERN.findall(code))
    complexity += len(_OPERATOR_PATTERN.findall(code))
    return complexity
