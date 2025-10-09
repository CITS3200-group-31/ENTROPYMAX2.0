"""
Persistence helpers for saving and loading previously opened data files.
Stores a small JSON file under the app's cache root (outside the volatile 'cache' subdir)
so it survives cleanup on exit.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .cache_paths import ensure_cache_root


def _store_path() -> Path:
    """Return the JSON file path used to store recent files info."""
    # Write directly under the cache root so it is not removed by cleanup_entire_cache()
    return ensure_cache_root() / "recent_files.json"


def save_recent_files(input_file: Optional[str], gps_file: Optional[str]) -> None:
    """Persist the names and full paths of the currently opened data files.

    Only the names are strictly required by the spec, but we also store full paths
    for potential future restore UX.
    """
    data: Dict[str, Any] = {
        "saved_at": datetime.now().isoformat(timespec='seconds'),
        "input": None,
        "gps": None,
    }

    if input_file:
        data["input"] = {
            "name": os.path.basename(input_file),
            "path": input_file,
        }
    if gps_file:
        data["gps"] = {
            "name": os.path.basename(gps_file),
            "path": gps_file,
        }

    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_recent_files() -> Dict[str, Any]:
    """Load the recent files JSON. Returns an empty dict when absent or malformed."""
    path = _store_path()
    try:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except Exception:
        return {}
