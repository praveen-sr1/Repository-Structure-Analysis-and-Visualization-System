# API Reference

Base URL: `http://localhost:8000/api`

Interactive OpenAPI docs are available at `http://localhost:8000/docs`.

All responses are JSON. Errors use standard HTTP status codes with a
`{ "detail": "..." }` body.

---

## Health

### `GET /api/health`

```json
{ "status": "ok", "version": "0.1.0" }
```

---

## Repositories

### `POST /api/repositories/scan`

Scan (or refresh) a local repository.

**Request body**

```json
{ "path": "/absolute/path/to/repo", "name": "optional-display-name" }
```

**Response** `201 Created`

```json
{
  "repository": {
    "id": 1,
    "name": "my-repo",
    "path": "/absolute/path/to/repo",
    "total_files": 42,
    "total_lines": 3571,
    "total_dependencies": 67,
    "created_at": "2026-06-27T10:00:00Z",
    "last_scanned_at": "2026-06-27T10:00:00Z"
  },
  "nodes_created": 42,
  "edges_created": 67,
  "message": "Scan completed successfully."
}
```

**Errors**: `404` path not found · `400` path is not a directory.

### `GET /api/repositories`

List analysed repositories (most recently scanned first).

### `GET /api/repositories/{id}`

Get a single repository. `404` if unknown.

### `POST /api/repositories/{id}/rescan`

Re-run analysis using the stored path. `404` unknown · `410` path gone.

### `DELETE /api/repositories/{id}`

Delete a repository and its analysis. `204 No Content`.

---

## Graph & statistics

### `GET /api/repositories/{id}/graph`

```json
{
  "repository_id": 1,
  "nodes": [
    {
      "id": "src/main.py",
      "label": "main.py",
      "path": "src/main.py",
      "language": "python",
      "metrics": {
        "lines_of_code": 120,
        "num_imports": 5,
        "num_classes": 2,
        "num_functions": 8,
        "cyclomatic_complexity": 14
      }
    }
  ],
  "edges": [
    {
      "id": "1-2",
      "source": "src/main.py",
      "target": "src/utils.py",
      "raw_import": "utils"
    }
  ]
}
```

### `GET /api/repositories/{id}/stats`

```json
{
  "repository_id": 1,
  "total_files": 42,
  "total_lines": 3571,
  "total_dependencies": 67,
  "total_classes": 18,
  "total_functions": 130,
  "average_complexity": 4.7,
  "languages": [
    { "language": "python", "files": 30, "lines": 2800 },
    { "language": "typescript", "files": 12, "lines": 771 }
  ]
}
```

---

## File metrics & AI summary

### `GET /api/repositories/{id}/files/metrics?path={relativePath}`

Returns `FileMetrics` for one file. `404` if the file is not in the repo.

### `GET /api/repositories/{id}/files/summary?path={relativePath}`

Returns a (possibly cached) AI explanation.

```json
{
  "file_path": "src/main.py",
  "content_hash": "9f86d0818...",
  "summary": "This module is the application entry point…",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "cached": false,
  "available": true
}
```

- `available: false` means no AI provider is configured; `summary` then contains
  a short notice and nothing is cached.
- `cached: true` means the summary was served from the local SHA-256 cache.

**Errors**: `404` file not in repo · `410` file unreadable on disk · `502`
AI provider error.
