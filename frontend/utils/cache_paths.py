"""Cross-platform cache path utilities for EntropyMax frontend."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

APP_NAME = "EntropyMax"
_CACHE_ENV_VAR = "ENTROPYMAX_CACHE_DIR"


def _default_cache_root() -> Path:
    """Return the default cache root based on the current platform."""
    system = platform.system()

    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    elif system == "Windows":
        local_app_data = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if local_app_data:
            base = Path(local_app_data) / APP_NAME
        else:
            base = Path.home() / "AppData" / "Local" / APP_NAME
    else:
        xdg_cache_home = os.getenv("XDG_CACHE_HOME")
        if xdg_cache_home:
            base = Path(xdg_cache_home) / APP_NAME
        else:
            base = Path.home() / ".cache" / APP_NAME

    return base / "entro_cache"


def resolve_cache_root() -> Path:
    """Resolve the cache root without creating it."""
    override = os.getenv(_CACHE_ENV_VAR)
    if override:
        return Path(override).expanduser()
    return _default_cache_root()


def _legacy_cache_locations() -> list[Path]:
    """Return possible legacy cache locations that need migration."""
    locations: list[Path] = []

    if getattr(sys, "frozen", False):
        locations.append(Path(sys.executable).parent / "entro_cache")

    module_root = Path(__file__).resolve().parent.parent
    locations.append(module_root / "entro_cache")

    return locations


def migrate_legacy_cache(target: Path) -> None:
    """Move cache contents from legacy locations into the new target directory."""
    if target.exists() and any(target.iterdir()):
        return

    for legacy_path in _legacy_cache_locations():
        if not legacy_path.exists() or legacy_path == target:
            continue

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(legacy_path), str(target))
            logger.info("Migrated legacy cache from %s to %s", legacy_path, target)
            return
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.warning("Failed to migrate legacy cache from %s: %s", legacy_path, exc)


def ensure_cache_root() -> Path:
    """Ensure the cache root exists, performing legacy migration if needed."""
    target = resolve_cache_root()

    if not target.exists():
        migrate_legacy_cache(target)

    target.mkdir(parents=True, exist_ok=True)
    return target


def ensure_cache_subdir(*parts: str) -> Path:
    """Ensure a cache subdirectory exists and return it."""
    base = ensure_cache_root()
    subdir = base.joinpath(*parts)
    subdir.mkdir(parents=True, exist_ok=True)
    return subdir


def get_cache_subdir(*parts: str) -> Path:
    """Return a cache subdirectory without creating it."""
    return resolve_cache_root().joinpath(*parts)
