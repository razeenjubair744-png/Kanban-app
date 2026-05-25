#!/usr/bin/env bash
set -euo pipefail

if command -v lsof >/dev/null 2>&1; then
  pids=$(lsof -ti tcp:8000 || true)
  if [ -n "$pids" ]; then
    echo "Stopping process on port 8000: $pids"
    kill -9 $pids
  else
    echo "No process listening on port 8000."
  fi
else
  echo "lsof is required to stop the server from this script."
  exit 1
fi
