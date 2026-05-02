#!/usr/bin/env python3
"""Deterministic backfill for data/geomechanics-corporate.json.

Reads a YAML or JSON file describing field updates per entity (matched by
either id or label_pt), applies them with declared merge policies, preserves
overwritten values under entity._legacy.<field>, and writes the result back.

Designed for the Gestão e Governança de Dados workflow: the team sends rich
content (cards) for a subset of entities; this script applies it without
manually editing the master JSON.

Usage:
    python scripts/backfill-geomec-corporate.py INPUT.yaml [--dry-run] [--out PATH]
    python scripts/backfill-geomec-corporate.py INPUT.json [--dry-run]

Input shape (one entry per entity):
    - match_id: GEOMEC001         # OR
      match_label_pt: "Pressão de Poros"
      apply:
        confidence: high
        definition_pt: "..."
        definition_en: "..."
        standard_unit: "ppg (lb/gal)"
        units_observed_union: [psi, ppg, kgf/cm²/m]   # union with existing
        acronym_union: [Pp, PP, poropressão]
        observed_variants_union: [...]
        owner_department: "RES"
        official_datastore: ["SIRR"]                  # replace
        internal_tools: ["GeomecBR"]                  # replace
        internal_standards: ["PE-2RES-00009"]         # replace
        sources_append:                               # append (de-dup by doc_id+section)
          - doc_id: PE-2RES-00009
            section: "3.10.2 Perfuração de Fases com Retorno"
            citation: "O peso mínimo utilizado deve considerar a máxima pressão de poros esperada."
        priority_tier: core_15
        external_id_chatpetrobras: GEO_MEC_001
        relationships_replace:                        # full replace (use with care)
          - relation_type: IS_PART_OF
            target_id: GEOMEC003
            target_label: "Janela Operacional de Lama"

Merge policy summary
--------------------
  REPLACE (with provenance to _legacy):
    confidence, definition_pt, definition_en, standard_unit, owner_department,
    official_datastore, internal_tools, internal_standards, priority_tier,
    external_id_chatpetrobras, osdu_mapping
  UNION (suffix `_union`):
    acronym_union, observed_variants_union, units_observed_union
  APPEND (suffix `_append`, de-duplicated):
    sources_append (key = doc_id + "::" + section)
    evidence_gaps_append
  REPLACE-ALL (suffix `_replace`):
    relationships_replace
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

REPLACE_FIELDS = {
    "confidence", "definition_pt", "definition_en", "standard_unit",
    "owner_department", "priority_tier", "external_id_chatpetrobras", "osdu_mapping",
    "label_pt", "label_en", "category",
}
REPLACE_LIST_FIELDS = {
    "official_datastore", "internal_tools", "internal_standards",
}
UNION_FIELDS = {
    "acronym_union": "acronym",
    "observed_variants_union": "observed_variants",
    "units_observed_union": "units_observed",
}
APPEND_FIELDS = {
    "sources_append": "sources",
    "evidence_gaps_append": "evidence_gaps",
}
REPLACE_ALL_FIELDS = {
    "relationships_replace": "relationships",
}


def load_input(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            print("ERRO: pyyaml não instalado. Use --input JSON ou: pip install pyyaml", file=sys.stderr)
            sys.exit(2)
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, list):
        print(f"ERRO: input deve ser uma lista de entradas. Recebido: {type(data).__name__}", file=sys.stderr)
        sys.exit(2)
    return data


def match_entity(entry: dict, entities: list[dict]) -> dict | None:
    if "match_id" in entry:
        for e in entities:
            if e["id"] == entry["match_id"]:
                return e
        return None
    if "match_label_pt" in entry:
        wanted = entry["match_label_pt"].strip().lower()
        for e in entities:
            if (e.get("label_pt") or "").strip().lower() == wanted:
                return e
        return None
    if "match_external_id" in entry:
        wanted = entry["match_external_id"].strip()
        for e in entities:
            if e.get("external_id_chatpetrobras") == wanted:
                return e
        return None
    return None


def _archive_legacy(entity: dict, field: str, old_value) -> None:
    if old_value in (None, "", [], {}):
        return
    legacy = entity.setdefault("_legacy", {})
    if field in legacy and legacy[field] == old_value:
        return  # already archived
    legacy[field] = old_value


def _source_key(s) -> str:
    if isinstance(s, str):
        return f"legacy::{s}"
    if isinstance(s, dict):
        # Include citation prefix so two distinct citations from the same
        # doc/section don't collapse. 60 chars is enough to disambiguate
        # while tolerating minor whitespace differences.
        cit = (s.get("citation") or "").strip()[:60]
        return f"{s.get('doc_id') or s.get('docId') or ''}::{s.get('section') or ''}::{cit}"
    return repr(s)


def _normalize_source(s) -> dict | str:
    """Accept structured dict (preferred) or plain string (legacy)."""
    if isinstance(s, str):
        return s
    if isinstance(s, dict):
        out = {}
        if "doc_id" in s or "docId" in s:
            out["doc_id"] = s.get("doc_id") or s.get("docId")
        if s.get("section"):
            out["section"] = s["section"]
        if s.get("citation"):
            out["citation"] = s["citation"]
        return out
    raise ValueError(f"source malformado: {s!r}")


def apply_entry(entity: dict, apply_block: dict, log: list[str]) -> None:
    eid = entity["id"]
    for field, value in apply_block.items():
        if field in REPLACE_FIELDS or field in REPLACE_LIST_FIELDS:
            old = entity.get(field)
            if old != value:
                _archive_legacy(entity, field, old)
                entity[field] = value
                log.append(f"  {eid}: replace {field} (old archived to _legacy)")
            continue

        if field in UNION_FIELDS:
            target_field = UNION_FIELDS[field]
            if not isinstance(value, list):
                raise ValueError(f"{eid}: {field} requires a list")
            existing = list(entity.get(target_field) or [])
            seen = {x.lower() if isinstance(x, str) else repr(x) for x in existing}
            for item in value:
                key = item.lower() if isinstance(item, str) else repr(item)
                if key not in seen:
                    existing.append(item)
                    seen.add(key)
            if existing != (entity.get(target_field) or []):
                entity[target_field] = existing
                log.append(f"  {eid}: union into {target_field} (now {len(existing)} items)")
            continue

        if field in APPEND_FIELDS:
            target_field = APPEND_FIELDS[field]
            if not isinstance(value, list):
                raise ValueError(f"{eid}: {field} requires a list")
            existing = list(entity.get(target_field) or [])
            if target_field == "sources":
                seen = {_source_key(s) for s in existing}
                added = 0
                for raw in value:
                    norm = _normalize_source(raw)
                    k = _source_key(norm)
                    if k not in seen:
                        existing.append(norm)
                        seen.add(k)
                        added += 1
                if added:
                    entity[target_field] = existing
                    log.append(f"  {eid}: appended {added} sources (now {len(existing)})")
            else:
                seen = {repr(x) for x in existing}
                added = 0
                for item in value:
                    if repr(item) not in seen:
                        existing.append(item)
                        seen.add(repr(item))
                        added += 1
                if added:
                    entity[target_field] = existing
                    log.append(f"  {eid}: appended {added} to {target_field}")
            continue

        if field in REPLACE_ALL_FIELDS:
            target_field = REPLACE_ALL_FIELDS[field]
            old = entity.get(target_field)
            if old != value:
                _archive_legacy(entity, target_field, old)
                entity[target_field] = value
                log.append(f"  {eid}: REPLACE-ALL {target_field} ({len(value)} new items, {len(old or [])} old archived)")
            continue

        raise ValueError(
            f"{eid}: campo '{field}' desconhecido. Use sufixo _union, _append ou _replace, "
            f"ou um campo da lista REPLACE_FIELDS."
        )


def main() -> int:
    p = argparse.ArgumentParser(description="Backfill geomechanics-corporate.json")
    p.add_argument("input", type=Path, help="YAML or JSON file with backfill entries")
    p.add_argument("--dry-run", action="store_true", help="Print plan without writing")
    p.add_argument("--out", type=Path, default=TARGET, help="Output JSON path (default: data/geomechanics-corporate.json)")
    args = p.parse_args()

    if not args.input.exists():
        print(f"ERRO: input não encontrado: {args.input}", file=sys.stderr)
        return 2

    entries = load_input(args.input)
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    entities = data["entities"]

    print(f"Lendo {args.input.name}: {len(entries)} entrada(s)")
    print(f"Master JSON: {len(entities)} entidades")

    log: list[str] = []
    matched = 0
    not_found: list[dict] = []

    for entry in entries:
        if "apply" not in entry:
            print(f"AVISO: entrada sem bloco 'apply', ignorada: {entry}", file=sys.stderr)
            continue
        ent = match_entity(entry, entities)
        if ent is None:
            not_found.append(entry)
            continue
        matched += 1
        log.append(f"\n→ {ent['id']} ({ent.get('label_pt')}) — match via "
                   f"{'match_id' if 'match_id' in entry else 'match_label_pt' if 'match_label_pt' in entry else 'match_external_id'}")
        apply_entry(ent, entry["apply"], log)

    print(f"\nMatched: {matched}/{len(entries)}")
    if not_found:
        print(f"NÃO encontradas ({len(not_found)}):")
        for nf in not_found:
            print(f"  • {nf.get('match_id') or nf.get('match_label_pt') or nf.get('match_external_id')}")

    print("\nDetalhe das mudanças:")
    print("\n".join(log) if log else "  (nenhuma mudança)")

    if args.dry_run:
        print("\n[dry-run] master JSON NÃO foi modificado.")
        return 0

    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✓ Escrito: {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}")
    if not_found:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
