# Installation & Quick Start

## Prerequisites

- **Python** 3.11+
- **Node.js** 20+
- **npm** 10+
- (optional) **Docker** + Docker Compose

## Option A — Local development

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (optional) configure AI + settings
cp .env.example .env                 # then edit as needed

uvicorn app.main:app --reload
```

The API is now at <http://localhost:8000> with interactive docs at
<http://localhost:8000/docs>.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env                 # defaults to http://localhost:8000/api
npm run dev
```

Open <http://localhost:5173>.

### 3. Use it

1. Click **Scan** in the sidebar.
2. Enter the **absolute path** to a local repository (e.g.
   `/home/you/projects/some-repo`).
3. Explore the graph; click a node to see metrics and (if AI is configured) an
   explanation.

## Option B — Docker Compose

```bash
# optional: export AI_PROVIDER / OPENAI_API_KEY / GEMINI_API_KEY first
docker compose up --build
```

- Frontend: <http://localhost:8080>
- Backend: <http://localhost:8000>

> To scan repositories from inside the container, mount them by uncommenting the
> `volumes` entry in `docker-compose.yml` and scanning the mounted path.

## Running tests

```bash
# Backend
cd backend && source .venv/bin/activate
pytest

# Frontend
cd frontend
npm test
```
