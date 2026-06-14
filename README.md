# Repository Structure Analysis & Visualisation System

> An analysis engine that parses local Git repositories to visually map their
> folder structure, inter-file dependencies, and code-complexity metrics —
> making it easier to **onboard onto, refactor, or simply understand** large,
> unfamiliar codebases.

![python](https://img.shields.io/badge/python-3.11%2B-blue)
![fastapi](https://img.shields.io/badge/FastAPI-0.111%2B-009688)
![react](https://img.shields.io/badge/react-18-61dafb)
![typescript](https://img.shields.io/badge/TypeScript-5-3178c6)
![reactflow](https://img.shields.io/badge/React%20Flow-11-ff0072)

---

## Overview

Jumping into a massive, unfamiliar codebase is overwhelming — where do you start,
and how do the modules connect? This tool answers those questions by **statically
analysing** a local repository (it never executes your code), extracting its
dependencies and metrics, and rendering an **interactive dependency graph** in a
modern, IDE-style web UI. Click any file to see its metrics and an **AI-generated
plain-English explanation**.

It is built as two cleanly separated services:

- a **Python / FastAPI backend** that scans, parses, measures, and serves the data, and
- a **React / TypeScript frontend** that visualises it with React Flow.

## Features

**Analysis engine (backend)**
- Recursively scans an entire local repository.
- Skips configurable directories (`.git`, `node_modules`, `venv`, `dist`, `build`, `__pycache__`, …).
- Detects dependencies **without executing code** for:
  - **Python** — via the standard-library `ast`
  - **JavaScript**, **TypeScript**, **Java**, **C / C++** — via robust static parsing
- Computes per-file metrics: **lines of code, number of imports, classes, functions,** and an **approximate cyclomatic complexity** — plus the actual **class & function names**.
- Resolves imports into a real dependency graph (only edges to files that exist in the repo).
- Persists results in SQLite; supports **re-scanning** a repository on demand.

**Visualisation (frontend)**
- Interactive **React Flow** graph: draggable nodes, zoom/pan, **MiniMap**, **controls**, and a **background grid**.
- Selecting a node **highlights its connected dependencies** and dims the rest.
- **Search bar** to filter files, a **repository sidebar** with live statistics, and a **details panel** showing metrics + AI explanation.
- **AI explanations** (OpenAI **or** Google Gemini): click a node → "Explain what this code does in 3 simple sentences." Summaries are **cached locally by SHA-256** and regenerated only when the file changes.
- Polished, professional UI: dark mode, loading skeletons, toast notifications, responsive layout.

## Tech stack

| Layer    | Technologies                                                                 |
| -------- | ---------------------------------------------------------------------------- |
| Backend  | Python · FastAPI · Uvicorn · SQLAlchemy · SQLite · Pydantic · httpx           |
| Frontend | React · TypeScript · Vite · React Flow · Tailwind CSS · React Query · Zustand |
| AI       | Google Gemini **or** OpenAI, with SHA-256-based local summary caching         |

## Repository structure

```
.
├── backend/                 # FastAPI analysis engine
│   ├── app/
│   │   ├── main.py          # app entrypoint + router wiring
│   │   ├── config.py        # settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── models/          # ORM models
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── routers/         # REST endpoints
│   │   ├── services/        # scanner, analysis, graph, AI
│   │   ├── parsers/         # per-language static parsers
│   │   ├── graph/           # builder + import resolver
│   │   ├── metrics/         # LOC + complexity
│   │   ├── cache/           # AI summary cache
│   │   └── utils/           # hashing, file helpers
│   └── tests/               # pytest suite
├── frontend/                # React + React Flow UI
│   └── src/
│       ├── components/      # ui, graph, panels, sidebar, common
│       ├── hooks/           # React Query hooks
│       ├── stores/          # Zustand stores
│       ├── services/        # typed API client
│       ├── types/ utils/ layouts/ pages/
└── docs/                    # architecture, API, configuration, troubleshooting
```

---

## Getting started

### Prerequisites

- **Python** 3.11+ (tested up to 3.14)
- **Node.js** 20+ and **npm** 10+
- (optional) **Docker** + Docker Compose

### 1 · Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (optional) configure AI — see "Enabling AI" below
cp .env.example .env

# start the API (use --reload-dir app so DB writes don't trigger reloads)
uvicorn app.main:app --reload --reload-dir app
```

- API: <http://localhost:8000>
- Interactive API docs (Swagger UI): <http://localhost:8000/docs>
- Health check: `curl http://localhost:8000/api/health`

### 2 · Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env                # defaults to http://localhost:8000/api
npm run dev
```

Open <http://localhost:5173>.

### 3 · Use it

1. Click **Scan** in the sidebar.
2. Enter the **absolute path** to a local repository, e.g. `/home/you/projects/some-repo`
   (you can even point it at this project's own `backend/` folder to try it out).
3. Explore the graph — drag nodes, zoom, search. Click a node to see its metrics
   and AI explanation.

---

## Enabling AI explanations

AI is **optional** — without it, the explanation panel simply shows a
"not configured" notice. To enable it, edit `backend/.env`:

**Google Gemini** (free tier — get a key at <https://aistudio.google.com/apikey>):

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
```

**OpenAI**:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

Restart the backend after changing the provider. See
[`docs/CONFIGURATION.md`](./docs/CONFIGURATION.md) for all options.

> **Note:** free-tier model quotas vary per model. If you get an HTTP 429
> (quota exceeded), try a different model such as `gemini-2.5-flash` /
> `gemini-2.5-flash-lite`.

---

## Testing

**Backend** (32 tests — scanner, parsers, metrics, graph, full API flow):

```bash
cd backend && source .venv/bin/activate
pytest                 # or: pytest -v
```

**Frontend** (Vitest — unit + component tests):

```bash
cd frontend
npm test               # watch mode: npm run test:watch
```

**Production build** (type-checks + bundles the frontend):

```bash
cd frontend
npm run build
```

---

## Run with Docker

```bash
# optional: export AI_PROVIDER / GEMINI_API_KEY (or OPENAI_API_KEY) first
docker compose up --build
```

- Frontend: <http://localhost:8080>
- Backend: <http://localhost:8000>

To scan your own repositories from inside the container, mount them via the
`volumes` entry in `docker-compose.yml` and scan the mounted path.

---

## API reference (summary)

Base URL: `http://localhost:8000/api`

| Method   | Endpoint                                        | Description                          |
| -------- | ----------------------------------------------- | ------------------------------------ |
| `POST`   | `/repositories/scan`                            | Scan (or refresh) a local repository |
| `GET`    | `/repositories`                                 | List analysed repositories           |
| `GET`    | `/repositories/{id}`                            | Get a repository                     |
| `POST`   | `/repositories/{id}/rescan`                     | Re-run analysis                      |
| `DELETE` | `/repositories/{id}`                            | Delete a repository                  |
| `GET`    | `/repositories/{id}/graph`                      | Dependency graph (nodes + edges)     |
| `GET`    | `/repositories/{id}/stats`                      | Aggregate statistics                 |
| `GET`    | `/repositories/{id}/files/metrics?path=…`       | Metrics for one file                 |
| `GET`    | `/repositories/{id}/files/summary?path=…`       | AI explanation for one file          |

Full details in [`docs/API.md`](./docs/API.md).

---

## Documentation

- [Architecture](./docs/ARCHITECTURE.md)
- [Installation & Quick Start](./docs/INSTALLATION.md)
- [API Reference](./docs/API.md)
- [Configuration](./docs/CONFIGURATION.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [Contributing](./CONTRIBUTING.md)

---

© 2026 Praveen Singh Rana. All rights reserved.
