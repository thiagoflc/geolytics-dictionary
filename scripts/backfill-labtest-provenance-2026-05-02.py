#!/usr/bin/env python3
"""Backfill lab-test provenance on geomechanical property entities — 2026-05-02.

Adds a structured `obtained_from_lab_tests` array to 6 property entities
(GEOMEC010–014, GEOMEC024) documenting which lab tests produce the property
and which is the primary method.

Each item has the shape:
    {test_id, test_label, primary, method_note}

The field is REPLACE semantics (not union/append): re-running with the same
curated list is a no-op; if a different list is already present, the previous
value is archived to `_legacy.obtained_from_lab_tests_prev`.

This backfill DEPENDS on lab-test entities GEOMEC061–067 created in parallel
by another script (Frente 1). If a referenced test_id is not yet present in
the JSON at run time, the script emits a WARNING per missing id but still
writes the data — forward-compatible: the IDs will resolve once Frente 1 is
applied.

Idempotent — re-running on a patched JSON is a no-op.
Usage: python3 scripts/backfill-labtest-provenance-2026-05-02.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

NEW_FIELD = "obtained_from_lab_tests"
LEGACY_PREV_KEY = "obtained_from_lab_tests_prev"


# ─────────────────────────────────────────────────────────────────────────
# Curated provenance — one list per property entity
# ─────────────────────────────────────────────────────────────────────────
PROVENANCE: dict[str, list[dict]] = {
    "GEOMEC010": [  # UCS
        {"test_id": "GEOMEC062", "test_label": "Ensaio UCS (Uniaxial sem Confinamento)", "primary": True,
         "method_note": "Método primário — medição direta na ruptura uniaxial sem confinamento."},
        {"test_id": "GEOMEC061", "test_label": "Ensaio Triaxial", "primary": False,
         "method_note": "Componente uniaxial extraído da envoltória de ruptura."},
        {"test_id": "GEOMEC022", "test_label": "Scratch Test", "primary": False,
         "method_note": "Estimativa contínua ao longo do testemunho via correlação de força de arranhamento."},
    ],
    "GEOMEC011": [  # Módulo de Young
        {"test_id": "GEOMEC061", "test_label": "Ensaio Triaxial", "primary": True,
         "method_note": "Método primário (estático) — derivado da curva tensão-deformação confinada."},
        {"test_id": "GEOMEC062", "test_label": "Ensaio UCS", "primary": False,
         "method_note": "Estático uniaxial sem confinamento."},
    ],
    "GEOMEC012": [  # Coeficiente de Poisson
        {"test_id": "GEOMEC061", "test_label": "Ensaio Triaxial", "primary": True,
         "method_note": "Razão deformação lateral/axial em ensaio triaxial drenado."},
        {"test_id": "GEOMEC062", "test_label": "Ensaio UCS", "primary": False,
         "method_note": "Razão deformação lateral/axial em ensaio uniaxial."},
    ],
    "GEOMEC013": [  # Biot-Willis
        {"test_id": "GEOMEC063", "test_label": "Ensaio Hidrostático", "primary": True,
         "method_note": "Calculado da rigidez bulk Kb (hidrostático) e Ks tabelado da literatura — ver PE-2RES-00014 §3.4.2.5."},
        {"test_id": "GEOMEC061", "test_label": "Ensaio Triaxial", "primary": False,
         "method_note": "Estimativa indireta via módulos elásticos."},
    ],
    "GEOMEC014": [  # Compressibilidade de Poros (geral)
        {"test_id": "GEOMEC063", "test_label": "Ensaio Hidrostático", "primary": True,
         "method_note": "Estado de tensão hidrostático isotrópico — Cb."},
        {"test_id": "GEOMEC065", "test_label": "Ensaio Oedométrico", "primary": False,
         "method_note": "Caso particular uniaxial — alimenta GEOMEC024."},
    ],
    "GEOMEC024": [  # Compressibilidade de Poros Uniaxial
        {"test_id": "GEOMEC065", "test_label": "Ensaio Oedométrico", "primary": True,
         "method_note": "Método primário — deformação lateral nula, vertical permitida."},
    ],
}


# Schema-policy documentation for the new field.
LAB_TEST_PROVENANCE_SCHEMA = {
    "field_name": NEW_FIELD,
    "form": "structured",
    "semantics": "REPLACE",
    "semantics_note": (
        "Curated list per property entity. The script does not union/append; "
        "re-running with the same curated list is a no-op. If a different list "
        "is already present, the previous value is archived to "
        "_legacy.obtained_from_lab_tests_prev and replaced."
    ),
    "item_shape": {
        "test_id": "string — REQUIRED — id of the lab-test entity (e.g. GEOMEC061)",
        "test_label": "string — REQUIRED — human-readable label of the test",
        "primary": "boolean — REQUIRED — true iff this is the primary method for the property",
        "method_note": "string — REQUIRED — short note describing how the property is obtained from this test",
    },
    "primary_cardinality": "exactly one item per property must have primary=true",
    "depends_on": "lab-test entities GEOMEC061–067 (Frente 1)",
}


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────
def _provenance_equal(a: list[dict] | None, b: list[dict]) -> bool:
    """Order-sensitive deep equality on the curated shape."""
    if not isinstance(a, list) or len(a) != len(b):
        return False
    keys = ("test_id", "test_label", "primary", "method_note")
    for x, y in zip(a, b):
        if not isinstance(x, dict):
            return False
        for k in keys:
            if x.get(k) != y.get(k):
                return False
    return True


def apply_provenance(by_id: dict, eid: str, items: list[dict], log: list[str]) -> None:
    e = by_id.get(eid)
    if not e:
        log.append(f"  SKIP {eid}: entity not found")
        return
    current = e.get(NEW_FIELD)
    if _provenance_equal(current, items):
        log.append(f"  NOOP  {eid}: obtained_from_lab_tests already up to date ({len(items)} item(s))")
        return
    if current not in (None, [], {}):
        legacy = e.setdefault("_legacy", {})
        legacy.setdefault(LEGACY_PREV_KEY, current)
        log.append(f"  ARCHIVE {eid}._legacy.{LEGACY_PREV_KEY} ← previous value ({len(current) if isinstance(current, list) else 'non-list'})")
    e[NEW_FIELD] = items
    primary = next((i["test_id"] for i in items if i.get("primary")), None)
    log.append(f"  SET   {eid}: {len(items)} test(s), primary={primary}")


def warn_missing_test_ids(by_id: dict, log: list[str]) -> None:
    referenced = {i["test_id"] for items in PROVENANCE.values() for i in items}
    missing = sorted(t for t in referenced if t not in by_id)
    if not missing:
        log.append(f"  CHECK lab-test ids: all {len(referenced)} referenced ids resolve in the JSON")
        return
    log.append(
        f"  WARN  {len(missing)} referenced lab-test id(s) not yet present in JSON "
        f"(forward-compatible — proceeding): {', '.join(missing)}"
    )


def update_schema_policy(data: dict, log: list[str]) -> None:
    sp = data["meta"].setdefault("schema_policy", {})
    rec = sp.setdefault("recommended_normalized_fields", [])
    if NEW_FIELD not in rec:
        rec.append(NEW_FIELD)
        log.append(f"  POLICY recommended_normalized_fields ← +{NEW_FIELD}")
    else:
        log.append(f"  NOOP  recommended_normalized_fields already lists {NEW_FIELD}")

    existing = sp.get("lab_test_provenance_schema")
    if existing != LAB_TEST_PROVENANCE_SCHEMA:
        sp["lab_test_provenance_schema"] = LAB_TEST_PROVENANCE_SCHEMA
        log.append("  POLICY lab_test_provenance_schema ← installed/updated")
    else:
        log.append("  NOOP  lab_test_provenance_schema already up to date")


def update_architecture_notes(data: dict, log: list[str]) -> None:
    notes = data["meta"].setdefault("architecture_notes", [])
    note = (
        "Lab-test provenance backfill 2026-05-02 — adicionado campo "
        "`obtained_from_lab_tests` (REPLACE) a 6 entidades de propriedade "
        "geomecânica (GEOMEC010, 011, 012, 013, 014, 024), amarrando-as às "
        "entidades de ensaio de laboratório GEOMEC061–067 criadas em paralelo "
        "pela Frente 1. Cada item registra test_id, test_label, primary e "
        "method_note; exatamente um item por propriedade tem primary=true. "
        "Esquema do campo documentado em meta.schema_policy.lab_test_provenance_schema."
    )
    if note not in notes:
        notes.append(note)
        log.append("  POLICY architecture_notes ← appended backfill note")
    else:
        log.append("  NOOP  architecture_notes already contains backfill note")


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}
    log: list[str] = []

    # 1. Forward-compat warning for missing lab-test ids.
    warn_missing_test_ids(by_id, log)

    # 2. Apply curated provenance to each target property entity.
    for eid, items in PROVENANCE.items():
        apply_provenance(by_id, eid, items, log)

    # 3. Update schema_policy.
    update_schema_policy(data, log)

    # 4. Architecture notes.
    update_architecture_notes(data, log)

    print("\n".join(log))
    print(f"\nTotal log lines: {len(log)}")
    print(f"Entities now: {len(data['entities'])}")

    if args.dry_run:
        print("\n[dry-run] master JSON NÃO foi modificado.")
        return 0

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✓ Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
