"""Tests for metrics: lines of code and cyclomatic complexity."""
from __future__ import annotations

from app.metrics import count_lines_of_code, estimate_complexity


def test_loc_excludes_blank_and_comment_lines_python():
    source = (
        "# a comment\n"
        "\n"
        "import os\n"
        "x = 1  # inline comment counts as code\n"
        "\n"
        "def f():\n"
        "    return x\n"
    )
    # Code lines: import os, x = 1, def f():, return x  -> 4
    assert count_lines_of_code(source, "python") == 4


def test_loc_handles_block_comments_c_style():
    source = (
        "/* header\n"
        "   block comment */\n"
        "int main() {\n"
        "    return 0; // done\n"
        "}\n"
    )
    # Code lines: int main() {, return 0;, } -> 3
    assert count_lines_of_code(source, "c") == 3


def test_python_complexity_counts_decision_points():
    source = (
        "def f(n):\n"
        "    if n > 0 and n < 10:\n"
        "        for i in range(n):\n"
        "            pass\n"
        "    return n\n"
    )
    # base 1 + if(1) + boolop(1) + for(1) = 4
    assert estimate_complexity(source, "python") == 4


def test_simple_python_function_has_complexity_one():
    assert estimate_complexity("def f():\n    return 1\n", "python") == 1


def test_keyword_complexity_for_javascript():
    source = (
        "function f(a, b) {\n"
        "  if (a && b) { return 1; }\n"
        "  for (let i = 0; i < 10; i++) {}\n"
        "  return 0;\n"
        "}\n"
    )
    # base 1 + if + && + for = 4
    assert estimate_complexity(source, "javascript") == 4
