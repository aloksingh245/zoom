# Class Scheduler Backend (POC)

## Setup
- Install deps: `uv pip install -r <(uv export)` or `uv sync` (uses `pyproject.toml`).
- Create `.env` based on `.env.example`.

## Run
`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Endpoints
- GET /health
- GET /api/courses
- POST /api/courses
- GET /api/classes
- GET /api/classes/{id}
- POST /api/classes
- PUT /api/classes/{id}
- DELETE /api/classes/{id}
