#!/usr/bin/env python3
"""Add LabTest support to SHACL shapes and policy enum.

Idempotent. Re-running produces no further changes.

Edits:
1. data/geolytics-shapes.ttl
   - Adds "LabTest" to the sh:in (...) enum on geo:category inside
     geo:GeomechCorporateEntityShape.
   - Appends advisory shape geo:GeomechLabTestProvenanceShape
     (severity=Warning) at the end of the file.
2. data/geomechanics-corporate.json
   - Adds "LabTest" to meta.schema_policy.category_extension_recommended
     (alphabetically positioned).

Usage:
    python scripts/add-labtest-shacl-2026-05-02.py [--dry-run]

Default behaviour writes files in place. --dry-run only reports what
would change.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHAPES_PATH = ROOT / "data" / "geolytics-shapes.ttl"
JSON_PATH = ROOT / "data" / "geomechanics-corporate.json"

NEW_CATEGORY = "LabTest"

# ─────────────────────────────────────────────────────────────────────────────
# New advisory shape (Warning) — appended only if not already present
# ─────────────────────────────────────────────────────────────────────────────
NEW_SHAPE_NAME = "GeomechLabTestProvenanceShape"

NEW_SHAPE_TEMPLATE = """
# ─────────────────────────────────────────────────────────────────────────────
# Shape {n}: {shape} — LabTest deve ter MEASURES ou IS_INPUT_FOR (advisory)
# ─────────────────────────────────────────────────────────────────────────────

geo:{shape}
    a sh:NodeShape ;
    sh:name "{shape}" ;
    rdfs:label "LabTest deve ter relação MEASURES ou IS_INPUT_FOR (advisory)"@pt ;
    sh:targetClass geo:GeomechCorporateEntity ;
    sh:severity sh:Warning ;
    sh:sparql [
        sh:message "Entidade categoria=LabTest deveria ter ao menos uma relação MEASURES ou IS_INPUT_FOR documentando quais propriedades o ensaio produz."@pt ;
        sh:prefixes geo: ;
        sh:select \"\"\"
PREFIX geo: <https://geolytics.petrobras.com.br/dict/>
SELECT $this
WHERE {{
    $this geo:category "LabTest" .
    FILTER NOT EXISTS {{
        $this geo:hasRelation ?r .
        ?r geo:relationType ?rt .
        FILTER ( ?rt = "MEASURES" || ?rt = "IS_INPUT_FOR" )
    }}
}}
\"\"\" ;
    ] .
"""


def update_shapes_ttl(text: str) -> tuple[str, list[str]]:
    """Return (new_text, change_log)."""
    changes: list[str] = []

    # ── 1. Add "LabTest" to GeomechCorporateEntityShape enum ────────────────
    # Locate the shape block, then the sh:in (...) for geo:category within it.
    shape_re = re.compile(
        r"(geo:GeomechCorporateEntityShape\b.*?)(\.\s*\n)",
        re.DOTALL,
    )
    m = shape_re.search(text)
    if not m:
        raise RuntimeError("Could not locate geo:GeomechCorporateEntityShape block")

    shape_block = m.group(1)
    block_end = m.group(2)

    # Within shape block, find the sh:property [ ... sh:path geo:category ; ... sh:in (...) ... ]
    cat_prop_re = re.compile(
        r"(sh:property\s*\[\s*[^\]]*?sh:path\s+geo:category\b[^\]]*?sh:in\s*\()([^)]*)(\)[^\]]*?\])",
        re.DOTALL,
    )
    cm = cat_prop_re.search(shape_block)
    if not cm:
        raise RuntimeError("Could not locate sh:in enum on geo:category")

    enum_inner = cm.group(2)
    # Tokenize quoted string literals
    tokens = re.findall(r'"([^"]*)"', enum_inner)
    if NEW_CATEGORY in tokens:
        changes.append(f"enum already contains {NEW_CATEGORY!r} (no change)")
    else:
        new_tokens = sorted(set(tokens + [NEW_CATEGORY]))
        new_enum_inner = " " + " ".join(f'"{t}"' for t in new_tokens) + " "
        new_cat_prop = cm.group(1) + new_enum_inner + cm.group(3)
        new_shape_block = shape_block[: cm.start()] + new_cat_prop + shape_block[cm.end() :]
        text = text[: m.start()] + new_shape_block + block_end + text[m.end() :]
        changes.append(
            f"added {NEW_CATEGORY!r} to GeomechCorporateEntityShape category enum"
        )

    # ── 2. Append advisory shape if not present ─────────────────────────────
    if f"geo:{NEW_SHAPE_NAME}" in text:
        changes.append(f"shape {NEW_SHAPE_NAME} already present (no change)")
    else:
        # Determine next shape number. Includes both "# Shape N:" lines and
        # range comments like "# Shapes 41-44:" so the new shape lands after
        # all already-allocated numbers (numbered or grouped).
        nums = [int(x) for x in re.findall(r"^# Shape\s+(\d+)\b", text, re.MULTILINE)]
        for lo, hi in re.findall(r"^# Shapes\s+(\d+)-(\d+)\b", text, re.MULTILINE):
            nums.append(int(hi))
        next_n = (max(nums) if nums else 0) + 1
        new_block = NEW_SHAPE_TEMPLATE.format(n=next_n, shape=NEW_SHAPE_NAME)
        if not text.endswith("\n"):
            text += "\n"
        text += new_block
        changes.append(f"appended advisory shape {NEW_SHAPE_NAME} as Shape {next_n}")

    return text, changes


def update_corporate_json(data: dict) -> tuple[dict, list[str]]:
    changes: list[str] = []
    meta = data.setdefault("meta", {})
    sp = meta.setdefault("schema_policy", {})
    arr = sp.setdefault("category_extension_recommended", [])
    if NEW_CATEGORY in arr:
        changes.append(
            f"category_extension_recommended already contains {NEW_CATEGORY!r}"
        )
    else:
        arr.append(NEW_CATEGORY)
        arr.sort()
        changes.append(
            f"added {NEW_CATEGORY!r} to meta.schema_policy.category_extension_recommended"
        )
    return data, changes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = p.parse_args()

    if not SHAPES_PATH.exists():
        print(f"ERROR: missing {SHAPES_PATH}", file=sys.stderr)
        return 2
    if not JSON_PATH.exists():
        print(f"ERROR: missing {JSON_PATH}", file=sys.stderr)
        return 2

    ttl_orig = SHAPES_PATH.read_text(encoding="utf-8")
    ttl_new, ttl_changes = update_shapes_ttl(ttl_orig)

    json_orig_text = JSON_PATH.read_text(encoding="utf-8")
    json_obj = json.loads(json_orig_text)
    json_new, json_changes = update_corporate_json(json_obj)
    json_new_text = json.dumps(json_new, ensure_ascii=False, indent=2) + "\n"

    print("== TTL changes ==")
    for c in ttl_changes:
        print(f"  - {c}")
    print("== JSON changes ==")
    for c in json_changes:
        print(f"  - {c}")

    if args.dry_run:
        print("\n[dry-run] no files written")
        return 0

    if ttl_new != ttl_orig:
        SHAPES_PATH.write_text(ttl_new, encoding="utf-8")
        print(f"wrote {SHAPES_PATH}")
    else:
        print(f"unchanged {SHAPES_PATH}")

    if json_new_text != json_orig_text:
        JSON_PATH.write_text(json_new_text, encoding="utf-8")
        print(f"wrote {JSON_PATH}")
    else:
        print(f"unchanged {JSON_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
