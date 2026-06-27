# Troubleshooting

## The frontend says "Cannot reach the backend"

- Confirm the backend is running: `curl http://localhost:8000/api/health`.
- Check `VITE_API_BASE_URL` in `frontend/.env` matches the backend URL.
- Ensure the frontend origin is listed in `CORS_ORIGINS` on the backend.

## Scan returns 404 "Path does not exist"

- The `path` must be an **absolute** path on the machine running the backend.
- In Docker, the host path is not visible unless you mount it (see
  `docker-compose.yml` `volumes`) and scan the **mounted** path.

## The graph is empty after scanning

- The repository may contain no supported source files (Python, JS, TS, Java,
  C/C++). Check `GET /api/repositories/{id}/stats` for the language breakdown.
- Files larger than `MAX_FILE_SIZE` are skipped — raise it if needed.

## No edges appear even though files import each other

- Only imports that resolve to a file **inside the scanned repo** become edges.
  Third-party/library imports are intentionally not drawn (but are still counted
  in each file's import metric).
- Unusual import styles or path aliases may not resolve; the import still counts
  toward metrics.

## AI explanation says "not configured"

- Set `AI_PROVIDER` and the matching API key, then restart the backend. See
  [CONFIGURATION.md](./CONFIGURATION.md).

## AI returns a 502 error

- The provider call failed (bad key, rate limit, or network). The exact provider
  message is included in the error `detail`. Verify the key and model name.

## Summary doesn't update after I edit a file

- Summaries are keyed by file content hash. Re-open the file in the UI — the
  backend re-reads the file, computes a new hash, and regenerates. If you only
  changed metrics, **rescan** the repository to refresh the graph.

## Port already in use

- Backend: change `PORT` (env) or `--port` on the Uvicorn command.
- Frontend: set `server.port` in `vite.config.ts` or run `npm run dev -- --port 5174`.

## Database seems stale or corrupted

- Stop the backend and delete `backend/data/analyzer.db`. It is recreated on the
  next start; just rescan your repositories.
