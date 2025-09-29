#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="${SCRIPT_DIR%/bin}"
VENV_DIR="$ROOT_DIR/frontend/.venv"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "Frontend venv missing. Run: make frontend-deps"; exit 1; fi
source "$VENV_DIR/bin/activate"
export QTWEBENGINE_DISABLE_SANDBOX=1
if [ -n "$WAYLAND_DISPLAY" ]; then
  export QT_QPA_PLATFORM=wayland
  export QT_OPENGL=desktop
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --ozone-platform=wayland"
else
  export QT_QPA_PLATFORM=xcb
  export QT_OPENGL=desktop
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"
fi
python "$ROOT_DIR/frontend/main.py" --debug || {
  echo "Primary launch failed, retrying with software rendering..."; 
  export QT_OPENGL=software; export QSG_RHI_BACKEND=software; export LIBGL_ALWAYS_SOFTWARE=1; export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe;
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-gpu-compositing --in-process-gpu --single-process --no-zygote --disable-software-rasterizer";
  export EMAX_DISABLE_CHARTS=1;
  python "$ROOT_DIR/frontend/main.py" --debug; }
