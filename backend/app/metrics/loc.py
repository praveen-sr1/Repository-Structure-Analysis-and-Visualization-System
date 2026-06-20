"""Lines-of-code counting.

Counts *source* lines: blank lines and full-line comments are excluded. Comment
syntax is language-aware so the count reflects meaningful code rather than raw
file length.
"""
from __future__ import annotations

# Single-line comment prefixes per language.
_LINE_COMMENT_PREFIXES: dict[str, tuple[str, ...]] = {
    "python": ("#",),
    "javascript": ("//",),
    "typescript": ("//",),
    "java": ("//",),
    "c": ("//",),
    "cpp": ("//",),
}

# Block comment delimiters per language (start, end).
_BLOCK_COMMENTS: dict[str, tuple[str, str]] = {
    "javascript": ("/*", "*/"),
    "typescript": ("/*", "*/"),
    "java": ("/*", "*/"),
    "c": ("/*", "*/"),
    "cpp": ("/*", "*/"),
}


def count_lines_of_code(source: str, language: str = "unknown") -> int:
    """Return the number of non-blank, non-comment lines in ``source``.

    Block comments are tracked across lines. A line containing both code and an
    inline comment still counts as code. This is an approximation suitable for
    relative comparison between files, not a certified SLOC tool.
    """
    line_prefixes = _LINE_COMMENT_PREFIXES.get(language, ())
    block = _BLOCK_COMMENTS.get(language)
    block_start, block_end = block if block else ("", "")

    count = 0
    in_block = False

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if in_block:
            # Inside a block comment: does it close on this line?
            if block_end and block_end in line:
                in_block = False
                after = line.split(block_end, 1)[1].strip()
                if after and not _is_pure_comment(after, line_prefixes):
                    count += 1
            continue

        # Whole-line single-line comment.
        if line_prefixes and line.startswith(line_prefixes):
            continue

        # Block comment opening on this line.
        if block_start and block_start in line:
            before = line.split(block_start, 1)[0].strip()
            remainder = line.split(block_start, 1)[1]
            if block_end and block_end in remainder:
                # Opened and closed on the same line; code may surround it.
                after = remainder.split(block_end, 1)[1].strip()
                if before or after:
                    count += 1
                continue
            # Block stays open past this line.
            in_block = True
            if before:
                count += 1
            continue

        count += 1

    return count


def _is_pure_comment(text: str, line_prefixes: tuple[str, ...]) -> bool:
    return bool(line_prefixes) and text.startswith(line_prefixes)
