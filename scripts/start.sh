#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if command -v uv >/dev/null 2>&1; then
  uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
else
  python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
fi
