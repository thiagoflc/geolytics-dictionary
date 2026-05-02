"""data.py — data loading helpers (local bundled + remote GitHub Pages)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).parent / "_data"

# Remote base — GitHub Pages for this repo
_REMOTE_BASE = "https://raw.githubusercontent.com/thiagoflc/geobrain/main/data"


def _local_path(filename: str) -> Path:
    return _DATA_DIR / filename


def load_json(filename: str) -> Any:
    """Load a JSON file from the bundled _data directory."""
    p = _local_path(filename)
    if not p.exists():
        raise FileNotFoundError(
            f"Bundled data file not found: {p}. "
            "Run python/build_data.py to copy data files, or install from a built wheel."
        )
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(filename: str) -> list[dict[str, Any]]:
    """Load a JSONL file from the bundled _data directory."""
    p = _local_path(filename)
    if not p.exists():
        raise FileNotFoundError(
            f"Bundled data file not found: {p}. "
            "Run python/build_data.py to copy data files."
        )
    lines = []
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    return lines


def fetch_json(path: str) -> Any:
    """Fetch a JSON file from the remote GitHub Pages endpoint.

    Requires the ``requests`` package.
    """
    try:
        import requests  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "requests is required for remote loading. "
            "Install it with: pip install requests"
        ) from exc

    url = f"{_REMOTE_BASE}/{path}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def data_dir() -> Path:
    """Return the bundled data directory path."""
    return _DATA_DIR
