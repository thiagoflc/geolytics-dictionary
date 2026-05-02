#!/usr/bin/env python3
"""Apply vocabulary decisions from data governance team — 2026-05-02.

Surgical changes to specific (entity, relation_type, target_id) tuples
based on the team's review of 10 semantic ambiguities. See commit message
for full justification per item.

Usage: python scripts/apply-vocabulary-decisions-2026-05-02.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

# Tuple format:
#   ("REMOVE", source_id, relation_type, target_id, _, _)
#   ("ADD",    source_id, relation_type, target_id, target_label, edge_note_or_None)
PATCHES = [
    # ─── Block I — direção MEASURED_BY/IS_CALCULATED_FROM corrigida ───
    ("REMOVE", "GEOMEC042", "MEASURED_BY",        "GEOMEC031", None, None),
    ("ADD",    "GEOMEC031", "MEASURES",           "GEOMEC042",
        "ISIP — Pressão Instantânea de Fechamento", None),

    ("REMOVE", "GEOMEC043", "MEASURED_BY",        "GEOMEC002", None, None),
    ("ADD",    "GEOMEC043", "ESTIMATES",          "GEOMEC002",
        "Tensão Mínima Horizontal (Gradiente de Fratura)", None),

    ("REMOVE", "GEOMEC045", "MEASURED_BY",        "GEOMEC025", None, None),
    ("ADD",    "GEOMEC025", "MONITORS",           "GEOMEC045",
        "Prisão de Coluna", None),

    ("REMOVE", "GEOMEC006", "MEASURED_BY",        "GEOMEC002", None, None),
    ("ADD",    "GEOMEC006", "MEASURES",           "GEOMEC002",
        "Tensão Mínima Horizontal (Gradiente de Fratura)", None),

    ("REMOVE", "GEOMEC042", "IS_CALCULATED_FROM", "GEOMEC002", None, None),
    ("ADD",    "GEOMEC042", "ESTIMATES",          "GEOMEC002",
        "Tensão Mínima Horizontal (Gradiente de Fratura)", None),

    # ─── Block II — IS_PART_OF entre constantes elásticas → CO_MEASURED_WITH (1 aresta por par) ───
    ("REMOVE", "GEOMEC010", "IS_PART_OF",         "GEOMEC011", None, None),
    ("REMOVE", "GEOMEC011", "IS_PART_OF",         "GEOMEC012", None, None),
    ("REMOVE", "GEOMEC011", "IS_PART_OF",         "GEOMEC010", None, None),  # redundante por simetria
    ("REMOVE", "GEOMEC012", "IS_PART_OF",         "GEOMEC011", None, None),  # redundante por simetria
    ("ADD",    "GEOMEC010", "CO_MEASURED_WITH",   "GEOMEC011",
        "Módulo de Young", None),
    ("ADD",    "GEOMEC011", "CO_MEASURED_WITH",   "GEOMEC012",
        "Coeficiente de Poisson", None),

    # ─── Block III — DERIVED_FROM entre mecanismos distintos → RELATED_TO + edge_note ───
    ("REMOVE", "GEOMEC044", "DERIVED_FROM",       "GEOMEC023", None, None),
    ("ADD",    "GEOMEC044", "RELATED_TO",         "GEOMEC023",
        "Breakouts e Fraturas Induzidas (Perfil de Imagem)",
        "Washout (erosão mecânica/química) e breakout (falha por cisalhamento) "
        "produzem o mesmo sinal observável no caliper (alargamento), mas têm "
        "mecanismos físicos distintos e independentes. Coexistência possível, "
        "não obrigatória."),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}

    log: list[str] = []
    skipped = 0
    for patch in PATCHES:
        action, src, rt, tgt = patch[0], patch[1], patch[2], patch[3]
        ent = by_id.get(src)
        if not ent:
            log.append(f"  SKIP — {src} not found")
            skipped += 1
            continue
        rels = ent.setdefault("relationships", [])
        if action == "REMOVE":
            before = len(rels)
            rels[:] = [
                r for r in rels
                if not (r.get("relation_type") == rt and r.get("target_id") == tgt)
            ]
            removed = before - len(rels)
            if removed:
                log.append(f"  {src} REMOVE {rt}→{tgt}: {removed} edge(s)")
            else:
                log.append(f"  {src} REMOVE {rt}→{tgt}: NOT FOUND (already absent?)")
                skipped += 1
        elif action == "ADD":
            tgt_label = patch[4]
            edge_note = patch[5]
            if any(r.get("relation_type") == rt and r.get("target_id") == tgt for r in rels):
                log.append(f"  {src} ADD {rt}→{tgt}: already exists (skip)")
                skipped += 1
                continue
            rec: dict = {"target_id": tgt, "relation_type": rt, "target_label": tgt_label}
            if edge_note:
                rec["edge_note"] = edge_note
            rels.append(rec)
            log.append(f"  {src} ADD {rt}→{tgt}{'  + edge_note' if edge_note else ''}")

    # ─── Update schema_policy ───
    sp = data["meta"].setdefault("schema_policy", {})
    sp["vocabulary_decisions"] = {
        "decision_date": "2026-05-02",
        "decided_by": "Gestão e Governança de Dados — Geomecânica E&P",
        "predicates_added": [
            {
                "name": "CO_MEASURED_WITH",
                "type": "ObjectProperty",
                "symmetric": True,
                "transitive": False,
                "domain": ["Property", "Measurement"],
                "range": ["Property", "Measurement"],
                "definition": (
                    "Ambas as entidades são derivadas do mesmo ensaio, operação ou perfil "
                    "de poço, mas são grandezas ontologicamente independentes (não há "
                    "relação parte-todo entre elas)."
                ),
                "canonical_use": "E ↔ ν (DTC/DTS); UCS ↔ E (Scratch Test/triaxial); E ↔ Biot (sônico+densidade)",
                "implementation_note": (
                    "Apenas uma aresta por par no grafo — reasoner OWL ou consumidor "
                    "downstream infere a direção inversa."
                ),
            },
        ],
        "predicates_clarified": {
            "MEASURES": "Origem = método/teste/sistema; Alvo = grandeza física quantificada",
            "MEASURED_BY": "Origem = grandeza; Alvo = método/sistema que a quantifica (inverso de MEASURES)",
            "ESTIMATES": "Origem = grandeza observada; Alvo = grandeza inferida (não calculada matematicamente)",
            "MONITORS": "Origem = sistema/processo; Alvo = evento ou estado operacional detectado",
            "CALIBRATES": "Reservado para relação modelo↔dado de campo, não grandeza↔grandeza",
        },
        "predicates_rejected": {
            "CO_OCCURS_WITH": "Implicaria co-ocorrência obrigatória — incorreto para o par Washout↔Breakout (mecanismos distintos, podem ocorrer independentemente)",
            "IS_PART_OF (extended definition)": "Expansão para incluir 'co-medido' viola meronimia formal SHACL/OWL e quebra interoperabilidade com reasoners externos",
        },
        "edge_note_field": (
            "Relacionamentos podem opcionalmente carregar 'edge_note' (string) "
            "explicando nuance da relação (ex.: convergência de observação sem "
            "co-ocorrência obrigatória)."
        ),
    }

    notes = data["meta"].setdefault("architecture_notes", [])
    note_str = (
        "Decisão de Vocabulário 2026-05-02 — Gestão e Governança de Dados aplicou 10 "
        "ajustes semânticos: 5 inversões de direção MEASURED_BY/IS_CALCULATED_FROM, "
        "4 trocas IS_PART_OF→CO_MEASURED_WITH (predicado simétrico novo) entre "
        "constantes elásticas independentes, e 1 troca DERIVED_FROM→RELATED_TO "
        "com edge_note para o par Washout↔Breakout. CO_OCCURS_WITH avaliado e "
        "rejeitado. Detalhes em schema_policy.vocabulary_decisions."
    )
    if note_str not in notes:
        notes.append(note_str)

    print("\n".join(log) if log else "(no changes)")
    print(f"\nApplied: {len(PATCHES) - skipped}/{len(PATCHES)}  (skipped: {skipped})")

    if args.dry_run:
        print("[dry-run] master JSON NÃO foi modificado.")
        return 0

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
