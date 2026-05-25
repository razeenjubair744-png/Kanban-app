FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ .
RUN npm install && npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir uv
COPY backend/pyproject.toml ./backend/pyproject.toml
WORKDIR /app/backend
RUN uv install
COPY backend ./backend
COPY --from=frontend-build /app/frontend/out ./frontend/out
WORKDIR /app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
