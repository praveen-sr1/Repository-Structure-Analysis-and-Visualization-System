"""Repository Analyzer backend application package.

A FastAPI service that statically analyses local repositories: it scans the
file tree, parses source files to extract dependencies and metrics, builds a
dependency graph, and serves the result as JSON for the frontend visualiser.
"""

__version__ = "0.1.0"
