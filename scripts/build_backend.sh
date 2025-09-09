#!/usr/bin/env bash
set -euo pipefail

# Build the C backend using CMake. Supports an optional clean and build type.
# Usage:
#   ./scripts/build_backend.sh [clean] [Debug|Release|RelWithDebInfo|MinSizeRel]

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_TYPE="${2:-RelWithDebInfo}"

if [[ "${1:-}" == "clean" ]]; then
  rm -rf "$ROOT_DIR/backend/build"
fi

cmake -S "$ROOT_DIR/backend" -B "$ROOT_DIR/backend/build" -DCMAKE_BUILD_TYPE="$BUILD_TYPE"
cmake --build "$ROOT_DIR/backend/build" --config "$BUILD_TYPE" -j

echo "\nArtifacts:"
echo "- Library: $ROOT_DIR/backend/build/libentropymax.*"
echo "- CLI:     $ROOT_DIR/backend/build/emx_cli"

