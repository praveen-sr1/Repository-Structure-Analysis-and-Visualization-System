# Architecture

This document describes how the Repository Analyzer is structured and how data
flows through the system.

## High-level overview

```
┌─────────────────────────┐     REST / JSON     ┌──────────────────────────┐
│   Frontend (Vite/React) │ ◄─────────────────► │   Backend (FastAPI)       │
│   React Flow + Zustand  │                     │   Scan → Parse → Graph    │
│   React Query + shadcn  │                     └────────────┬──────────────┘
└─────────────────────────┘                                  │
                                                  ┌───────────┴───────────┐
                                                  │  SQLite (graph +       │
                                                  │  AI summary cache)     │
                                                  └───────────┬───────────┘
                                                              │ on node click
                                                  ┌───────────┴───────────┐
                                                  │ AI provider (OpenAI /  │
                                                  │ Gemini), SHA-256 cache │
                                                  └────────────────────────┘
```

## Backend pipeline

The analysis is a linear, side-effect-free pipeline. **No repository code is
ever imported or executed** — every step works on text and ASTs only.

1. **Scanner** (`services/scanner.py`)
   Walks the directory with `os.walk`, prunes ignored directories in place
   (`.git`, `node_modules`, `venv`, …), reads each supported file as UTF-8,
   skips binary/oversized files, and computes a SHA-256 content hash.

2. **Parsers** (`parsers/`)
   A `ParserRegistry` selects a parser by language. The Python parser uses the
   standard-library `ast` module; JS/TS/Java/C/C++ use carefully scoped regex
   parsers that first strip comments and string literals. Each parser returns a
   `ParseResult` of imports, classes, and functions.

3. **Metrics** (`metrics/`)
   `loc.py` counts non-blank, non-comment lines (language-aware). `complexity.py`
   approximates cyclomatic complexity — precisely via the AST for Python, and by
   counting branch keywords/boolean operators for other languages.

4. **Graph builder + resolver** (`graph/`)
   `GraphBuilder` analyses every file, then `ImportResolver` turns each raw
   import token into a concrete target file *within the repo*. Only resolvable
   internal imports become edges; external/library imports are ignored for
   edges but still counted in each file's `num_imports` metric.

5. **Persistence** (`services/analysis_service.py`, `models/`)
   The result is written to SQLite via SQLAlchemy as `Repository`, `FileNode`,
   and `Dependency` rows. Rescanning replaces a repository's nodes/edges in a
   single transaction.

6. **AI summaries** (`services/ai_service.py`, `cache/`)
   On request, the current file contents are read and hashed. The
   `SummaryCache` is checked by `(file_path, sha256)`; a miss calls the
   configured provider and stores the result. Because the key is the content
   hash, edits automatically invalidate stale summaries.

## Frontend architecture

- **React Query** owns all server state (scan, graph, stats, metrics, summary)
  with caching, loading, and error states.
- **Zustand** owns UI state: `uiStore` (active repo, selected node, theme,
  sidebar, search) and `graphStore` (highlight sets derived from the selection).
- **React Flow** renders the canvas with a custom `FileNode`, MiniMap, Controls,
  Background grid, zoom/pan, and draggable nodes.
- **Layout**: a three-pane IDE shell — sidebar (explorer + stats), graph canvas,
  and a details panel (metrics + AI explanation) that appears on selection.

Selecting a node computes its connected nodes/edges in `graphStore`, dims the
rest of the canvas, and drives the metrics and AI panels.

## Design principles

- **Clean separation**: the analysis core (`scanner`, `parsers`, `metrics`,
  `graph`) is free of framework/DB concerns and is unit-tested in isolation.
- **Resilience over completeness**: a single malformed file never aborts a scan
  (`BaseParser.safe_parse`).
- **Honest AI**: with no provider configured, the API returns an explicit
  "not configured" response instead of a fabricated summary.
- **Extensibility**: adding a language is a new `BaseParser` subclass plus one
  registry line and an extension mapping.
