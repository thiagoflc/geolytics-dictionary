#!/usr/bin/env python3
"""Resolve overlap between GEOMEC036.formula.variables and GEOMEC038/GEOMEC039 — 2026-05-02.

Architectural decision: variables in formulas are promoted to first-class
entity references. The formula no longer carries inline variable
descriptions; instead it references existing entities by id via
formula.variable_refs, and explicit relationships REQUIRES_INPUT /
IS_INPUT_FOR connect the formula to its variables.

The previous formula.variables dict is preserved (audit) under
entity._legacy.formula_variables — matching the existing _legacy
convention used by backfill scripts.

Idempotent: re-running performs no further mutation; if
formula.variable_refs already exists on GEOMEC036 the migration is
skipped and only the relationship/schema_policy invariants are verified.

Usage: python scripts/resolve-formula-variable-overlap-2026-05-02.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

FORMULA_ID = "GEOMEC036"
PH_ID = "GEOMEC038"
DPA_ID = "GEOMEC039"

VARIABLE_REFS = [
    {"symbol": "Ph", "entity_id": PH_ID},
    {"symbol": "ΔPa", "entity_id": DPA_ID},
    {"symbol": "L", "entity_id": None},
]

L_EVIDENCE_GAP = (
    "Variável L (profundidade vertical no ponto avaliado) ainda não existe como "
    "entidade de primeira classe — formula.variable_refs carrega entity_id=null. "
    "Promover em iteração futura (provável GEOMEC054) ou alinhar com o esforço da "
    "Frente F antes da ingestão definitiva."
)

ARCH_NOTE = (
    "Resolução de Overlap 2026-05-02 — Variáveis de fórmulas promovidas a entidades "
    "de primeira classe. GEOMEC036.formula.variables (dict) substituído por "
    "formula.variable_refs (list[{symbol, entity_id}]) e relacionamentos "
    "REQUIRES_INPUT/IS_INPUT_FOR explícitos entre GEOMEC036 ↔ GEOMEC038/GEOMEC039. "
    "Variável L permanece como referência sem entity_id (gap registrado). Dicionário "
    "antigo movido para entity._legacy.formula_variables para auditoria."
)


def ensure_relationship(ent: dict, rt: str, tgt: str, tgt_label: str, log: list[str]) -> bool:
    """Append a relationship if not present. Returns True if added."""
    rels = ent.setdefault("relationships", [])
    if any(r.get("relation_type") == rt and r.get("target_id") == tgt for r in rels):
        log.append(f"  {ent['id']} {rt}→{tgt}: already exists (skip)")
        return False
    rels.append({"target_id": tgt, "relation_type": rt, "target_label": tgt_label})
    log.append(f"  {ent['id']} ADD {rt}→{tgt}")
    return True


def migrate_formula_variables(ent: dict, log: list[str]) -> bool:
    """Move formula.variables → _legacy.formula_variables, write variable_refs.

    Returns True if migration was performed (or partially completed).
    """
    formula = ent.get("formula")
    if not isinstance(formula, dict):
        log.append(f"  {ent['id']}: no formula object — nothing to migrate")
        return False

    if "variable_refs" in formula:
        log.append(f"  {ent['id']}: formula.variable_refs already present — skip migration")
        # Verify structural shape but don't rewrite.
        return False

    legacy_vars = formula.get("variables")
    if legacy_vars is not None:
        legacy_bucket = ent.setdefault("_legacy", {})
        if "formula_variables" not in legacy_bucket:
            legacy_bucket["formula_variables"] = legacy_vars
            log.append(
                f"  {ent['id']}: moved formula.variables → _legacy.formula_variables "
                f"({len(legacy_vars)} entries)"
            )
        else:
            log.append(
                f"  {ent['id']}: _legacy.formula_variables already exists — leaving as-is"
            )
        del formula["variables"]
        log.append(f"  {ent['id']}: removed formula.variables (deprecated)")

    formula["variable_refs"] = VARIABLE_REFS
    log.append(
        f"  {ent['id']}: wrote formula.variable_refs ({len(VARIABLE_REFS)} refs)"
    )
    return True


def ensure_l_evidence_gap(ent: dict, log: list[str]) -> bool:
    gaps = ent.setdefault("evidence_gaps", [])
    if L_EVIDENCE_GAP in gaps:
        log.append(f"  {ent['id']}: L-promotion evidence_gap already present (skip)")
        return False
    gaps.append(L_EVIDENCE_GAP)
    log.append(f"  {ent['id']}: appended L-promotion evidence_gap")
    return True


def update_schema_policy(data: dict, log: list[str]) -> bool:
    sp = data["meta"].setdefault("schema_policy", {})
    desired = {
        "canonical_field": "formula.variable_refs",
        "canonical_shape": (
            "list[{symbol: string, entity_id: string|null}] — symbol é o token "
            "exato como aparece em formula.expression; entity_id referencia uma "
            "entidade de primeira classe (Property/Measurement) do dicionário, "
            "ou null quando a variável ainda não foi promovida (registrar "
            "evidence_gap correspondente)."
        ),
        "deprecated_field": "formula.variables",
        "deprecated_note": (
            "Dicionário inline {symbol: description} preterido — descrições devem "
            "viver na entidade referenciada para evitar drift. Não escrever em "
            "novas ingestões. Valores legados são movidos para "
            "entity._legacy.formula_variables pelo script "
            "scripts/resolve-formula-variable-overlap-2026-05-02.py."
        ),
        "companion_relationships": {
            "forward": "REQUIRES_INPUT (Formula → Property/Measurement)",
            "inverse": "IS_INPUT_FOR (Property/Measurement → Formula)",
            "note": (
                "Para fórmulas optou-se por armazenar AMBAS as direções "
                "explicitamente — relaxa a política 'apenas uma aresta por par' "
                "do CO_MEASURED_WITH (vocabulary_decisions 2026-05-02) porque "
                "o par é assimétrico (Formula vs Variável) e consumidores "
                "downstream comuns (cards de variável, expansão de fórmula) "
                "leem cada direção independentemente sem reasoner OWL."
            ),
        },
        "established": "2026-05-02",
    }
    existing = sp.get("formula_schema")
    if existing == desired:
        log.append("  schema_policy.formula_schema: already up to date (skip)")
        return False
    sp["formula_schema"] = desired
    log.append("  schema_policy.formula_schema: updated")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}

    log: list[str] = []
    mutated = False

    formula_ent = by_id.get(FORMULA_ID)
    ph_ent = by_id.get(PH_ID)
    dpa_ent = by_id.get(DPA_ID)

    if not formula_ent:
        print(f"FATAL: {FORMULA_ID} not found in master JSON", file=sys.stderr)
        return 1
    if not ph_ent:
        print(f"FATAL: {PH_ID} not found in master JSON", file=sys.stderr)
        return 1
    if not dpa_ent:
        print(f"FATAL: {DPA_ID} not found in master JSON", file=sys.stderr)
        return 1

    # 1. Migrate formula.variables → variable_refs (+ _legacy bucket).
    log.append(f"[1] Migrate {FORMULA_ID}.formula.variables → variable_refs")
    if migrate_formula_variables(formula_ent, log):
        mutated = True

    # 2. Add L-promotion evidence_gap on the formula.
    log.append(f"[2] Ensure L-promotion evidence_gap on {FORMULA_ID}")
    if ensure_l_evidence_gap(formula_ent, log):
        mutated = True

    # 3. Forward relationships: GEOMEC036 REQUIRES_INPUT → GEOMEC038, GEOMEC039.
    log.append(f"[3] Forward relationships {FORMULA_ID} REQUIRES_INPUT → ...")
    if ensure_relationship(
        formula_ent, "REQUIRES_INPUT", PH_ID,
        "Pressão Hidrostática do Fluido de Perfuração", log,
    ):
        mutated = True
    if ensure_relationship(
        formula_ent, "REQUIRES_INPUT", DPA_ID,
        "Perda de Carga Anular", log,
    ):
        mutated = True

    # 4. Inverse relationships: GEOMEC038/GEOMEC039 IS_INPUT_FOR → GEOMEC036.
    log.append(f"[4] Inverse relationships ... IS_INPUT_FOR → {FORMULA_ID}")
    if ensure_relationship(
        ph_ent, "IS_INPUT_FOR", FORMULA_ID, "Fórmula de ECD", log,
    ):
        mutated = True
    if ensure_relationship(
        dpa_ent, "IS_INPUT_FOR", FORMULA_ID, "Fórmula de ECD", log,
    ):
        mutated = True

    # 5. Schema policy update.
    log.append("[5] Update schema_policy.formula_schema")
    if update_schema_policy(data, log):
        mutated = True

    # Architecture note (idempotent).
    notes = data["meta"].setdefault("architecture_notes", [])
    if ARCH_NOTE not in notes:
        notes.append(ARCH_NOTE)
        log.append("  architecture_notes: appended overlap-resolution note")
        mutated = True
    else:
        log.append("  architecture_notes: overlap-resolution note already present (skip)")

    print("\n".join(log))
    print(f"\nMutated: {mutated}")

    if args.dry_run:
        print("[dry-run] master JSON NÃO foi modificado.")
        return 0

    if mutated:
        TARGET.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"✓ Wrote {TARGET.relative_to(ROOT)}")
    else:
        print("(no changes — file untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
