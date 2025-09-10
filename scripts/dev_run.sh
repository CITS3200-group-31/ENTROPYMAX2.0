#!/usr/bin/env bash
set -euo pipefail

# Run the PyQt app for development.
# If running the standalone frontend, activate its venv first and execute main.py.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -f "$ROOT_DIR/frontend/.venv/bin/activate" ]]; then
  # Prefer the standalone frontend
  source "$ROOT_DIR/frontend/.venv/bin/activate"
  cd "$ROOT_DIR/frontend"
  exec python main.py
else
  # Fallback to src/app entrypoint
  cd "$ROOT_DIR"
  exec python -m app
fi

