#!/usr/bin/env python3
"""Apply canonical relation vocabulary per data governance team approval (2026-05-02).

Migrates the 49 affected edges across the 66 → 34 verb canonicalization,
introduces 3 new predicates (AUTHORITATIVE_FOR, OWNED_BY, AMPLIFIES), and
records 5 disambiguation rules in schema_policy.canonical_relation_enum.

Idempotent — re-running on a canonicalized JSON is a no-op.

Usage: python3 scripts/apply-vocabulary-canonicalization-2026-05-02.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

# Verb migration map.
# action ∈ { "merge", "merge_with_note", "flip", "flip_with_note" }
#   merge:     rename relation_type in place, keep direction
#   merge_w/n: rename in place + append edge_note
#   flip:      swap (source, target), rename relation_type
#   flip_w/n:  flip + append edge_note
MERGE_MAP: dict[str, tuple[str, str, str | None]] = {
    # merged (same direction)
    "IS_COMPONENT_OF":      ("merge", "IS_PART_OF", None),
    "CONTAINS_FORECAST":    ("merge_with_note", "CONTAINS", "forecast"),
    "IS_DETERMINED_FROM":   ("merge", "IS_CALCULATED_FROM", None),
    "COMPUTES_1D":          ("merge_with_note", "COMPUTES", "dimensão 1D"),
    "ALLOWS_ESTIMATION":    ("merge", "ESTIMATES", None),
    "DETERMINES":           ("merge", "INFLUENCES", None),
    "DETERMINES_DIRECTION": ("merge_with_note", "INFLUENCES", "direção/azimute"),
    "CONTROLS":             ("merge", "INFLUENCES", None),
    "MANIPULATES":          ("merge", "INFLUENCES", None),
    "EXPLOITS":             ("merge", "INFLUENCES", None),
    "IS_RELATED_TO":        ("merge", "RELATED_TO", None),
    "GENERATES":            ("merge", "PRODUCES", None),
    "OUTPUTS":              ("merge", "PRODUCES", None),
    "MANAGED_BY":           ("merge", "GOVERNED_BY", None),
    "IMPLEMENTED_BY":       ("merge", "PERFORMED_BY", None),
    "INTERFACES_WITH":      ("merge", "USED_WITH", None),
    "ANALYZES":             ("merge", "MONITORS", None),
    "SATISFIES":            ("merge_with_note", "FORMALIZES", "conformidade"),
    "REQUIRES_VALIDATION":  ("merge_with_note", "REQUIRES", "validação"),
    "REQUIRES_KNOWLEDGE":   ("merge_with_note", "REQUIRES", "conhecimento prévio"),
    "REQUIRES_ANALYSIS":    ("merge_with_note", "REQUIRES", "análise"),
    "ENABLES_DESIGN":       ("merge_with_note", "ENABLES", "design"),
    # flipped (origin and target swap)
    "MEASURED_BY":            ("flip", "MEASURES", None),
    "OBTAINED_BY":            ("flip", "MEASURES", None),
    "IS_DETERMINED_BY":       ("flip", "MEASURES", None),
    "IS_CALIBRATED_BY":       ("flip", "CALIBRATES", None),
    "INCLUDES":               ("flip", "IS_PART_OF", None),
    "IS_USED_TO_CALCULATE":   ("flip", "IS_CALCULATED_FROM", None),
    "LIMITED_BY":             ("flip", "CONSTRAINS", None),
    "MUST_STAY_IN":           ("flip", "CONSTRAINS", None),
    "UPPER_BOUND_DEFINED_BY": ("flip", "DEFINES_UPPER_BOUND", None),
    "LOWER_BOUND_DEFINED_BY": ("flip", "DEFINES_LOWER_BOUND", None),
    "OPERATES_ABOVE":         ("flip", "DEFINES_LOWER_BOUND", None),
    "TRIGGERED_BY":           ("flip", "INFLUENCES", None),
    "CONTROLLED_BY":          ("flip", "INFLUENCES", None),
    "DEPENDS_ON":             ("flip", "INFLUENCED_BY", None),
    "DETERMINED_BY":          ("flip", "INFLUENCED_BY", None),
    "PRODUCED_BY":            ("flip", "PRODUCES", None),
    "OUTPUT_OF":              ("flip", "PRODUCES", None),
    "IS_CLASSIFICATION_OF":   ("flip", "IS_SPECIALIZATION_OF", None),
    "IS_REQUIRED_BY":         ("flip", "REQUIRES", None),
    "IS_REQUIRED_FOR":        ("flip", "REQUIRES", None),
    "USED_BY":                ("flip", "REQUIRES", None),
    "COMPLEMENTED_BY":        ("flip", "USED_WITH", None),
    "GOVERNS_UPDATE":         ("flip_with_note", "GOVERNED_BY", "ciclo de atualização"),
}

CANONICAL_VERBS = sorted({
    # 31 from proposal
    "IS_PART_OF", "CONTAINS", "RELATED_TO",
    "IS_CALCULATED_FROM", "COMPUTES", "ESTIMATES", "DERIVED_FROM",
    "MEASURES", "CO_MEASURED_WITH", "MONITORS", "CALIBRATES",
    "CONSTRAINS", "DEFINES_UPPER_BOUND", "DEFINES_LOWER_BOUND",
    "INFLUENCES", "INFLUENCED_BY", "MAY_TRIGGER",
    "PRODUCES", "STORAGE_FOR",
    "IS_SPECIALIZATION_OF",
    "REQUIRES", "REQUIRES_INPUT", "IS_INPUT_FOR",
    "GOVERNED_BY",
    "SUPPORTS", "ENABLES", "USED_WITH",
    "PRECEDED_BY", "PERFORMED_BY",
    "FORMALIZES",
    "IS_RISK_FOR",
    # 3 added by team
    "AUTHORITATIVE_FOR",
    "OWNED_BY",
    "AMPLIFIES",
})


def _add_edge_note(rec: dict, note: str) -> None:
    if rec.get("edge_note"):
        # don't duplicate
        if note in rec["edge_note"]:
            return
        rec["edge_note"] = f"{rec['edge_note']} | {note}"
    else:
        rec["edge_note"] = note


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}

    log: list[str] = []
    pending_flips: list[tuple[str, str, str, str, str | None, str, str]] = []
    merge_count = 0
    flip_count = 0
    skip_count = 0

    # Pass 1 — in-place merges + collect flips
    # NOTE: also processes deprecated entities — their historical relations
    # must still be canonical for SHACL conformance (verbs in the enum),
    # even though the entities themselves don't represent active state.
    for e in data["entities"]:
        new_rels = []
        for r in list(e.get("relationships") or []):
            verb = r.get("relation_type")
            tgt_id = r.get("target_id")
            if verb not in MERGE_MAP:
                new_rels.append(r)
                continue
            action, new_verb, note = MERGE_MAP[verb]
            if action == "merge":
                r2 = dict(r)
                r2["relation_type"] = new_verb
                new_rels.append(r2)
                merge_count += 1
                log.append(f"  MERGE  {e['id']} {verb}→{tgt_id}  ⇒  {new_verb}")
            elif action == "merge_with_note":
                r2 = dict(r)
                r2["relation_type"] = new_verb
                _add_edge_note(r2, note)
                new_rels.append(r2)
                merge_count += 1
                log.append(f"  MERGE  {e['id']} {verb}→{tgt_id}  ⇒  {new_verb} [edge_note: {note}]")
            elif action in ("flip", "flip_with_note"):
                # Edge migrates to a different source
                pending_flips.append((
                    tgt_id,            # new source
                    new_verb,
                    e["id"],           # new target
                    e.get("label_pt"),
                    note if action == "flip_with_note" else None,
                    f"{e['id']}",      # original source
                    f"{verb}→{tgt_id}",
                ))
                log.append(f"  FLIP   {e['id']} {verb}→{tgt_id}  ⇒  {tgt_id} {new_verb}→{e['id']}"
                           + (f" [edge_note: {note}]" if note else ""))
        e["relationships"] = new_rels

    # Pass 2 — apply flips on the new source entities
    for new_src, new_verb, new_tgt, new_tgt_label, note, orig_src, orig_what in pending_flips:
        ent = by_id.get(new_src)
        if not ent:
            log.append(f"  SKIP   FLIP target {new_src} not found")
            skip_count += 1
            continue
        rels = ent.setdefault("relationships", [])
        if any(r.get("relation_type") == new_verb and r.get("target_id") == new_tgt for r in rels):
            log.append(f"  SKIP   {new_src} {new_verb}→{new_tgt}: already exists")
            skip_count += 1
            continue
        rec = {
            "target_id": new_tgt,
            "relation_type": new_verb,
            "target_label": new_tgt_label,
            "_flipped_from": f"{orig_src} {orig_what}",
        }
        if note:
            rec["edge_note"] = note
        rels.append(rec)
        flip_count += 1

    # ─── Schema policy: canonical_relation_enum (the authoritative section) ───
    sp = data["meta"].setdefault("schema_policy", {})
    sp["canonical_relation_enum"] = {
        "version": "2026-05-02",
        "approved_by": "Gestão e Governança de Dados — Geomecânica E&P",
        "total_canonical_verbs": len(CANONICAL_VERBS),
        "verbs": CANONICAL_VERBS,
        "predicates_added_v2": [
            {
                "name": "AUTHORITATIVE_FOR",
                "type": "ObjectProperty",
                "symmetric": False,
                "transitive": False,
                "domain": ["Tool"],
                "range": ["Property", "Document", "Model", "Measurement"],
                "definition": (
                    "Sistema X é a fonte da verdade (golden source) para a entidade Y. "
                    "Diferente de STORAGE_FOR (que pode ter múltiplos repositórios) e de "
                    "GOVERNED_BY (que é normativo/regulatório, não técnico)."
                ),
                "canonical_use": [
                    "SIRR AUTHORITATIVE_FOR Modelo Geomecânico 3D",
                    "SIPLEX AUTHORITATIVE_FOR Laudo Geomecânico",
                    "BDIEP AUTHORITATIVE_FOR Perfil de Imagem",
                ],
                "cardinality": "Único por entidade — uma entidade tem no máximo 1 sistema authoritative",
            },
            {
                "name": "OWNED_BY",
                "type": "ObjectProperty",
                "symmetric": False,
                "transitive": False,
                "domain": ["Property", "Process", "Document", "Model", "Measurement", "Tool"],
                "range": ["Department", "Property"],
                "definition": (
                    "Custódia operacional — qual gerência/departamento é responsável pela "
                    "entidade e responde por ela. Distinto de GOVERNED_BY (governança normativa)."
                ),
                "canonical_use": [
                    "Modelo Geomecânico 3D OWNED_BY RES/TR/GMR",
                    "Gradiente de Colapso OWNED_BY POÇOS/SPO/PEP/PROJ-PERF",
                ],
                "evidence": "PE-2RES-00009 §3.2 — separação RES vs POÇOS para gradientes",
            },
            {
                "name": "AMPLIFIES",
                "type": "ObjectProperty",
                "subPropertyOf": "INFLUENCES",
                "symmetric": False,
                "transitive": False,
                "domain": ["Property", "Process", "Risk"],
                "range": ["Property", "Risk"],
                "definition": (
                    "A aumenta a magnitude ou probabilidade de B além da causalidade base "
                    "já capturada por INFLUENCES. Toda aresta AMPLIFIES é também INFLUENCES "
                    "(via subPropertyOf — consultas em INFLUENCES devem incluir AMPLIFIES)."
                ),
                "canonical_use": [
                    "Depleção AMPLIFIES APB",
                    "Fluência do Sal AMPLIFIES Gradiente de Colapso",
                ],
            },
        ],
        "disambiguation_rules": {
            "INFLUENCES_vs_INFLUENCED_BY": (
                "INFLUENCES quando A é agente primário e B é efeito. "
                "INFLUENCED_BY quando B é o foco e 'B é afetado por A' é a leitura mais "
                "natural. Evitar INFLUENCED_BY quando A já tem alto grau de saída "
                "(over-centrality risk em PageRank/betweenness)."
            ),
            "REQUIRES_vs_REQUIRES_INPUT": (
                "REQUIRES: dependência genérica de processo — edge_note obrigatório "
                "(validação/análise/conhecimento). "
                "REQUIRES_INPUT: dependência computacional direta — alvo deve ser "
                "Property ou Measurement."
            ),
            "STORAGE_FOR_vs_AUTHORITATIVE_FOR": (
                "STORAGE_FOR: o sistema contém o dado (pode haver múltiplos). "
                "AUTHORITATIVE_FOR: o sistema é o golden source (único por entidade)."
            ),
            "GOVERNED_BY_vs_OWNED_BY": (
                "GOVERNED_BY: padrão normativo (PE-XXX, política corporativa, comitê). "
                "OWNED_BY: gerência/departamento responsável operacionalmente."
            ),
            "MAY_TRIGGER_vs_INFLUENCES": (
                "INFLUENCES: causalidade afirmada — reasoner pode encadear inferências. "
                "MAY_TRIGGER: causalidade epistemicamente incerta — reasoner não deve "
                "encadear sem qualificação probabilística. Crítico para análise de risco "
                "(ex.: Subsidência MAY_TRIGGER Reativação de Falhas, mas não obrigatoriamente)."
            ),
        },
        "non_blocking_reservations_for_v2": [
            "IS_PART_OF transitiva: adicionar sh:class constraint diferenciando Property "
            "vs Process para evitar inferências entre níveis hierárquicos distintos.",
            "IS_SPECIALIZATION_OF transitiva: adicionar sh:maxCount 1 no inversePath para "
            "garantir hierarquia linear (evita inferências indevidas em DAGs com herança "
            "múltipla).",
            "REQUIRES sh:minCount 1 em edge_note quando alvo não é Document.",
            "CONTAINS sh:class Document como restrição de domínio.",
        ],
        "rejected_predicates_in_review": {
            "STORED_IN": "Coberto pela convenção 'uma direção por par' — inverso de STORAGE_FOR é inferido.",
            "IS_PART_OF (extended definition)": "Definição expandida 'co-medido' viola meronimia formal.",
            "CO_OCCURS_WITH": "Implicaria co-ocorrência obrigatória — incorreto para o par Washout↔Breakout.",
        },
    }

    notes = data["meta"].setdefault("architecture_notes", [])
    note_str = (
        "Vocabulário Canonical 2026-05-02 — Gestão e Governança de Dados aprovou enum de "
        f"{len(CANONICAL_VERBS)} verbos canônicos: 31 da proposta inicial + 3 adicionais "
        "(AUTHORITATIVE_FOR, OWNED_BY, AMPLIFIES). Migrados: "
        f"{merge_count} mesclas + {flip_count} inversões = {merge_count+flip_count} arestas "
        "alteradas. 5 regras de desambiguação documentadas em "
        "schema_policy.canonical_relation_enum.disambiguation_rules. 4 ressalvas SHACL "
        "registradas como non-blocking para v2."
    )
    if note_str not in notes:
        notes.append(note_str)

    print("\n".join(log) if log else "(nenhuma migração necessária — já canônico)")
    print()
    print(f"Mesclas:  {merge_count}")
    print(f"Inversões: {flip_count}")
    print(f"Skips:    {skip_count}")

    if args.dry_run:
        print("\n[dry-run] master JSON NÃO foi modificado.")
        return 0

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✓ Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
