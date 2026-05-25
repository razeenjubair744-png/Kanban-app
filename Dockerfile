FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ .
RUN npm install && npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 1. Install uv globally via pip
RUN pip install --no-cache-dir uv

# 2. Copy backend configuration files first (for caching layers)
COPY backend/pyproject.toml backend/uv.lock ./backend/

# 3. Change directory to the backend where pyproject.toml lives
WORKDIR /app/backend

# 4. FIX: Use 'uv sync' instead of 'uv install' to install dependencies
RUN uv sync --no-dev

# 5. Copy the rest of the backend source code
COPY backend ./

# 6. Copy the static frontend build from the first stage
COPY --from=frontend-build /app/frontend/out /app/frontend/out

# 7. Reset WORKDIR to root so your python module resolution works smoothly
WORKDIR /app

EXPOSE 8000

# 8. Use the virtual environment's uvicorn that uv sync created
CMD ["/app/backend/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]