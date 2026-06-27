# Configuration

All backend configuration is environment-based, loaded via `pydantic-settings`
from environment variables and an optional `.env` file (project root or
`backend/.env`). Copy `.env.example` to `.env` to get started.

## Environment variables

| Variable          | Default                          | Description                                                            |
| ----------------- | -------------------------------- | ---------------------------------------------------------------------- |
| `APP_NAME`        | `Repository Analyzer`            | Display name of the service.                                           |
| `ENVIRONMENT`     | `development`                    | `development` or `production`.                                         |
| `LOG_LEVEL`       | `INFO`                           | `DEBUG` / `INFO` / `WARNING` / `ERROR`.                                |
| `HOST`            | `0.0.0.0`                        | Bind host for Uvicorn.                                                 |
| `PORT`            | `8000`                           | Bind port for Uvicorn.                                                 |
| `DATABASE_URL`    | `sqlite:///./data/analyzer.db`   | SQLAlchemy database URL.                                               |
| `CORS_ORIGINS`    | `http://localhost:5173,...`      | Comma-separated allowed origins.                                       |
| `IGNORED_DIRS`    | `.git,node_modules,venv,...`     | Comma-separated directory names to skip while scanning.                |
| `MAX_FILE_SIZE`   | `1048576`                        | Max file size (bytes) to read for parsing; larger files are skipped.  |
| `AI_PROVIDER`     | `none`                           | `openai`, `gemini`, or `none`.                                         |
| `OPENAI_API_KEY`  | _(empty)_                        | Required when `AI_PROVIDER=openai`.                                    |
| `OPENAI_MODEL`    | `gpt-4o-mini`                    | OpenAI chat model.                                                     |
| `GEMINI_API_KEY`  | _(empty)_                        | Required when `AI_PROVIDER=gemini`.                                    |
| `GEMINI_MODEL`    | `gemini-1.5-flash`               | Gemini model.                                                          |
| `AI_MAX_TOKENS`   | `600`                            | Max tokens for AI responses.                                           |
| `AI_TEMPERATURE`  | `0.2`                            | Sampling temperature for AI responses.                                 |

### Frontend

| Variable             | Default                     | Description                          |
| -------------------- | --------------------------- | ------------------------------------ |
| `VITE_API_BASE_URL`  | `http://localhost:8000/api` | Base URL the frontend calls.         |

## Enabling AI summaries

AI is **optional** — the app works fully without it (the explanation panel shows
a "not configured" notice). To enable:

**OpenAI**

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**Gemini**

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash
```

Restart the backend after changing the provider. Summaries are cached in SQLite
by file content hash and regenerated only when a file changes.

## Customising ignored directories

Set `IGNORED_DIRS` to a comma-separated list. The scanner prunes these directory
names anywhere in the tree, so large or generated folders never slow down a scan.

```env
IGNORED_DIRS=.git,node_modules,venv,.venv,dist,build,__pycache__,target,vendor
```
