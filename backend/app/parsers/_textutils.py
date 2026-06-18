"""Shared helpers for regex-based parsers.

Regex parsing is inherently approximate. To reduce false positives we first
strip comments and string literals so that tokens appearing inside them are not
mistaken for real imports or declarations.
"""
from __future__ import annotations

import re

# Matches block comments (/* ... */) and line comments (// ...).
_C_STYLE_COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.DOTALL)
# Matches '#' line comments (Python-style; also used to strip C preprocessor
# lines selectively elsewhere, so kept separate).
_HASH_COMMENTS = re.compile(r"#[^\n]*")
# Matches single/double/back-quoted string literals (no multiline for quotes).
_STRINGS = re.compile(
    r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`",
    re.DOTALL,
)


def strip_c_style_comments(source: str) -> str:
    """Remove ``/* */`` and ``//`` comments from C-family source."""
    return _C_STYLE_COMMENTS.sub(" ", source)


def strip_string_literals(source: str) -> str:
    """Replace string/template literals with empty quotes to neutralise content."""
    return _STRINGS.sub('""', source)


def unique_preserving_order(items: list[str]) -> list[str]:
    """Return ``items`` de-duplicated while preserving first-seen order."""
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
