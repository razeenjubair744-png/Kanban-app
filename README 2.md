# Project Management MVP

A local full-stack Project Management MVP with a single-board Kanban UI, backend persistence, auth, and AI integration.

## Overview

- Frontend: Next.js static app
- Backend: Python FastAPI with SQLite persistence
- AI: OpenRouter integration via `OPENROUTER_API_KEY`
- Container: Docker multi-stage build

## Features

- User sign in with fixed credentials
- Single Kanban board with column rename, card add/delete, and drag-and-drop
- Backend data storage in SQLite
- AI sidebar for board assistance via OpenRouter
- Static frontend served by FastAPI in production

## Requirements

- Node.js 20+
- npm
- Python 3.12+ (or compatible Python 3 environment)
- Docker (optional)

## Local setup

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Install backend dependencies:

```bash
cd ../backend
python3 -m pip install -e .
```

3. Create environment variables:

```bash
cp ../.env.example ../.env
# set OPENROUTER_API_KEY if you want AI support
```

## Run locally

### Frontend only

From `frontend`:

```bash
npm run dev
```

### Full stack backend + frontend

From project root:

```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000`.

### Login

- Username: `user`
- Password: `password`

## Docker

Build the container:

```bash
docker build -t pm-app .
```

Run the container:

```bash
docker run --rm -p 8000:8000 pm-app
```

Open `http://localhost:8000`.

## Tests

### Backend

From project root:

```bash
python3 -m pytest backend/tests/test_main.py
```

### Frontend

From `frontend`:

```bash
npm run test:unit
```

## Notes

- The backend serves the built static frontend from `frontend/out`.
- If `OPENROUTER_API_KEY` is not configured, the AI endpoint returns an explanatory fallback message.
- Use `./scripts/start.sh` and `./scripts/stop.sh` for simple local server control on macOS/Linux.
