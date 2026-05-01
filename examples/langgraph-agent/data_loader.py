"""Load and cache ontology data from the repository's data/ directory.

All loaders are module-level singletons: the files are read once and
held in memory for the process lifetime.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

# Resolve the repo root relative to this file's location
_HERE = Path(__file__).parent
_REPO_ROOT = _HERE.parent.parent  # examples/langgraph-agent -> repo root
_DATA_DIR = _REPO_ROOT / "data"
_AI_DIR = _REPO_ROOT / "ai"


@lru_cache(maxsize=1)
def load_entity_graph() -> dict[str, Any]:
    """Return the parsed entity-graph.json."""
    path = _DATA_DIR / "entity-graph.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def load_taxonomies() -> dict[str, Any]:
    """Return the parsed taxonomies.json (top-level dict with 'taxonomies' key)."""
    path = _DATA_DIR / "taxonomies.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def load_rag_corpus() -> list[dict[str, Any]]:
    """Return all chunks from ai/rag-corpus.jsonl."""
    path = _AI_DIR / "rag-corpus.jsonl"
    chunks: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


@lru_cache(maxsize=1)
def load_acronyms() -> list[dict[str, Any]]:
    """Return the parsed acronyms.json list."""
    path = _DATA_DIR / "acronyms.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
