#!/usr/bin/env python3
"""build_data.py — Copy data files from the repo root into the package bundle.

Run this before building a wheel to ensure geolytics_dictionary/_data/ is
populated with all required JSON and JSONL files.

Usage::

    cd python/
    python build_data.py

The script copies (not symlinks) the source files so the wheel is
self-contained and does not depend on the parent repository at runtime.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO_ROOT = HERE.parent
DATA_SRC = REPO_ROOT / "data"
AI_SRC = REPO_ROOT / "ai"
DATA_DEST = HERE / "geolytics_dictionary" / "_data"

# Files to copy from data/
DATA_FILES = [
    "full.json",
    "entity-graph.json",
    "taxonomies.json",
    "acronyms.json",
    "sweet-alignment.json",
    "sweet-modules.json",
    "witsml-rdf-crosswalk.json",
    "prodml-rdf-crosswalk.json",
    "glossary.json",
    "extended-terms.json",
    "ontology-types.json",
    "systems.json",
    "datasets.json",
    "pvt-dictionary.json",
    "geomechanics.json",
    "geomechanics-fractures.json",
    "seismic-acquisition.json",
    "seismic-processing.json",
    "seismic-inversion-attributes.json",
    "osdu-mapping.json",
    "osdu-gso-crosswalk.json",
    "fracture_to_gso.json",
    "cgi-lithology.json",
]

# Files to copy from ai/
AI_FILES = [
    "rag-corpus.jsonl",
    "ontology-map.json",
]


def main() -> int:
    DATA_DEST.mkdir(parents=True, exist_ok=True)

    # Write a .gitkeep so the directory is tracked even when empty
    (DATA_DEST / ".gitkeep").touch()

    missing: list[str] = []

    for fname in DATA_FILES:
        src = DATA_SRC / fname
        if not src.exists():
            print(f"  SKIP (not found): {src}")
            missing.append(str(src))
            continue
        dest = DATA_DEST / fname
        shutil.copy2(src, dest)
        print(f"  COPY  {src.name}  ({src.stat().st_size // 1024} KB)")

    for fname in AI_FILES:
        src = AI_SRC / fname
        if not src.exists():
            print(f"  SKIP (not found): {src}")
            missing.append(str(src))
            continue
        dest = DATA_DEST / fname
        shutil.copy2(src, dest)
        print(f"  COPY  {src.name}  ({src.stat().st_size // 1024} KB)")

    if missing:
        print(f"\nWarning: {len(missing)} file(s) not found and were skipped.")
        for m in missing:
            print(f"  {m}")
    else:
        print(f"\nAll files copied to {DATA_DEST}")

    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
