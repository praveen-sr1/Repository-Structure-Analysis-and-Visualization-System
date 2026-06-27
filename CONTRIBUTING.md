# Contributing

Thanks for your interest in improving Repository Analyzer! This guide covers the
basics for local development and submitting changes.

## Development setup

See [docs/INSTALLATION.md](./docs/INSTALLATION.md) for full setup. In short:

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Project layout

- `backend/app/` — FastAPI app, organised into `routers`, `services`, `parsers`,
  `graph`, `metrics`, `models`, `schemas`, `cache`, `utils`, `config`.
- `frontend/src/` — React app, organised into `components`, `pages`, `hooks`,
  `services`, `stores`, `types`, `utils`, `layouts`.

## Coding standards

- **Python**: type hints everywhere, small focused modules, docstrings on public
  classes/functions. The analysis core stays free of framework/DB imports.
- **TypeScript**: strict mode, no `any` unless unavoidable, components small and
  composable. Server state via React Query; UI state via Zustand.
- Keep files small — prefer adding a new module over growing a monolith.

## Adding a language parser

1. Create `backend/app/parsers/<lang>.py` subclassing `BaseParser`.
2. Register it in `backend/app/parsers/registry.py`.
3. Add its extension(s) to `EXTENSION_LANGUAGE_MAP` in
   `backend/app/utils/file_utils.py`.
4. Add tests in `backend/tests/test_parsers.py`.

## Tests

All changes should keep tests green and add coverage for new behaviour.

```bash
cd backend && pytest
cd frontend && npm test
```

## Pull requests

1. Fork and branch from `main` (e.g. `feat/rust-parser`).
2. Make focused commits with clear messages.
3. Ensure backend and frontend tests pass.
4. Open a PR describing the change and the motivation.

## Commit messages

Use clear, imperative summaries (e.g. "Add Rust parser", "Fix edge resolution
for path aliases"). Group related changes together.
