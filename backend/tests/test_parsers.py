"""Tests for the language parsers."""
from __future__ import annotations

from app.parsers import registry
from app.parsers.c_cpp import CCppParser
from app.parsers.java import JavaParser
from app.parsers.javascript import JavaScriptParser
from app.parsers.python import PythonParser
from app.parsers.typescript import TypeScriptParser


def test_python_parser_extracts_structure():
    source = (
        "import os\n"
        "from collections import defaultdict\n"
        "from .utils import helper\n"
        "\n"
        "class Foo:\n"
        "    def method(self):\n"
        "        pass\n"
        "\n"
        "def free_function():\n"
        "    return 1\n"
    )
    result = PythonParser().parse(source)
    assert "os" in result.imports
    assert "collections" in result.imports
    assert ".utils" in result.imports
    assert "Foo" in result.classes
    assert "method" in result.functions
    assert "free_function" in result.functions


def test_javascript_parser_handles_import_styles():
    source = (
        "import defaultExport from 'a';\n"
        "import { named } from './b';\n"
        "const c = require('c');\n"
        "const lazy = import('./d');\n"
        "export class Widget {}\n"
        "function go() {}\n"
        "const arrow = () => 42;\n"
    )
    result = JavaScriptParser().parse(source)
    assert set(result.imports) >= {"a", "./b", "c", "./d"}
    assert "Widget" in result.classes
    assert "go" in result.functions
    assert "arrow" in result.functions


def test_typescript_parser_counts_type_declarations():
    source = (
        "import type { T } from './types';\n"
        "interface Shape { x: number; }\n"
        "enum Color { Red, Green }\n"
        "type Alias = string;\n"
        "class Impl implements Shape { x = 1; }\n"
    )
    result = TypeScriptParser().parse(source)
    assert "./types" in result.imports
    assert {"Shape", "Color", "Alias", "Impl"} <= set(result.classes)


def test_java_parser_extracts_imports_and_types():
    source = (
        "package com.example;\n"
        "import java.util.List;\n"
        "import static java.lang.Math.PI;\n"
        "public class Service {\n"
        "    public List<String> items() { return null; }\n"
        "    private int helper(int n) { if (n > 0) { return n; } return 0; }\n"
        "}\n"
    )
    result = JavaParser().parse(source)
    assert "java.util.List" in result.imports
    assert "Service" in result.classes
    assert "items" in result.functions
    assert "helper" in result.functions


def test_cpp_parser_extracts_includes_and_functions():
    source = (
        "#include <vector>\n"
        '#include "myheader.h"\n'
        "struct Point { int x; };\n"
        "int add(int a, int b) {\n"
        "    return a + b;\n"
        "}\n"
    )
    result = CCppParser().parse(source)
    assert "vector" in result.imports
    assert "myheader.h" in result.imports
    assert "Point" in result.classes
    assert "add" in result.functions


def test_registry_routes_by_language():
    assert registry.supports("python")
    assert registry.supports("c")  # aliased to the cpp parser
    py = registry.parse("python", "import os\n")
    assert "os" in py.imports
    # Unsupported language yields an empty result, not an error.
    empty = registry.parse("brainfuck", "++++.")
    assert empty.num_imports == 0
