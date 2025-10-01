#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="${SCRIPT_DIR%/bin}"
VENV_DIR="$ROOT_DIR/frontend/.venv"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "Frontend venv missing. Run: make frontend-deps"; exit 1; fi
source "$VENV_DIR/bin/activate"
export QTWEBENGINE_DISABLE_SANDBOX=1
# Ensure a safe runtime dir for Qt/Chromium
if [ -z "${XDG_RUNTIME_DIR:-}" ]; then
  export XDG_RUNTIME_DIR="/tmp/xdg-runtime-$(id -u)"
  mkdir -p "$XDG_RUNTIME_DIR" 2>/dev/null || true
  chmod 700 "$XDG_RUNTIME_DIR" 2>/dev/null || true
fi
# Prefer XCB/X11 for stability across WSL/VMs
export QT_QPA_PLATFORM=xcb
export QT_OPENGL=desktop
# Let main.py choose stable Chromium flags by default; do not set here
if grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null || [ -n "${WSL_DISTRO_NAME:-}" ]; then
  # WSL: use software rendering and disable charts up front (more stable)
  export EMAX_DISABLE_CHARTS=1
  export EMAX_DISABLE_MAP_REFRESH=${EMAX_DISABLE_MAP_REFRESH:-1}
  export QT_OPENGL=software
  export QSG_RHI_BACKEND=opengl
  export QT_QUICK_BACKEND=software
  export LIBGL_ALWAYS_SOFTWARE=1
  export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-gpu-compositing --in-process-gpu --single-process --no-zygote --disable-software-rasterizer"
  # Remove single-process/zygote flags to avoid V8 proxy resolver warnings
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-gpu-compositing"
fi

python "$ROOT_DIR/frontend/main.py" --debug || {
  echo "Primary launch failed, retrying with software rendering..."; 
  export EMAX_DISABLE_CHARTS=1
  export QT_OPENGL=software
  export QSG_RHI_BACKEND=opengl
  export QT_QUICK_BACKEND=software
  export LIBGL_ALWAYS_SOFTWARE=1
  export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-gpu-compositing --in-process-gpu --single-process --no-zygote --disable-software-rasterizer"
  python "$ROOT_DIR/frontend/main.py" --debug; }
