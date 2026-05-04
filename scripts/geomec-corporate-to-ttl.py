#!/usr/bin/env python3
"""Serialize data/geomechanics-corporate.json to Turtle (RDF/TTL).

Output: stdout — pipe into pyshacl/validate-shacl.py.

Maps JSON entities to geo:GeomechCorporateEntity instances under the
geo: namespace, and relations to geo:GeomechCorporateRelation blank nodes,
suitable for validation against the SHACL shapes in
data/geolytics-shapes.ttl (shapes 23+).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "geomechanics-corporate.json"

GEO = "https://geolytics.petrobras.com.br/dict/"


def lit(s: str | None, lang: str | None = None) -> str | None:
    if s is None or s == "":
        return None
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")
    return f'"{s}"@{lang}' if lang else f'"{s}"'


def emit(data: dict) -> str:
    out: list[str] = []
    a = out.append
    a("# Generated from data/geomechanics-corporate.json")
    a("# Run: python scripts/geomec-corporate-to-ttl.py > /tmp/geomec.ttl")
    a("")
    a("@prefix geo:  <https://geolytics.petrobras.com.br/dict/> .")
    a("@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    a("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    a("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .")
    a("@prefix owl:  <http://www.w3.org/2002/07/owl#> .")
    a("@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .")
    a("")
    a("# Class declarations (idempotent — also defined in vocab if reused)")
    a("geo:GeomechCorporateEntity   a owl:Class ; rdfs:label \"Geomechanics Corporate Entity\"@en .")
    a("geo:GeomechCorporateRelation a owl:Class ; rdfs:label \"Geomechanics Corporate Relation\"@en .")
    a("geo:GeomechCorporateSource   a owl:Class ; rdfs:label \"Geomechanics Corporate Source\"@en .")
    a("")

    # Set of corporate entity IDs (active — not deprecated).
    # Required by Shape 29 (geo:targetEntity must reference declared corp entity).
    corp_ids: set[str] = {e["id"] for e in data["entities"] if not e.get("deprecated")}

    # Deprecation map: deprecated_id -> survivor_id. Mirrors the JS pipeline
    # in scripts/generate.js (buildGeomecCorporateGraph). Edges to deprecated
    # entities are rerouted to their survivor and tagged geo:repointedFrom for
    # provenance. Without this, Shape 27 (active reference to deprecated)
    # would fire for every relationship pointing at GEOMEC003/004/013/026B/049/050
    # (F4 merges) or pre-existing splits (GEOMEC026/052/053).
    deprecation_map: dict[str, str] = {}
    for e in data["entities"]:
        dep = e.get("deprecated")
        if isinstance(dep, dict):
            rb = dep.get("replaced_by") or []
            if isinstance(rb, list) and rb:
                deprecation_map[e["id"]] = rb[0]

    def resolve_target(tid: str) -> tuple[str, str | None]:
        """Returns (final_target_id, repointed_from_id|None)."""
        if tid in deprecation_map:
            return deprecation_map[tid], tid
        return tid, None

    def is_corporate(tid: str) -> bool:
        """Whether target ID is an active corporate entity in this module.
        Edges crossing module boundaries (e.g., GEOMEC013→GM017 after F4
        merge with academic backbone) are NOT emitted in the corporate
        TTL — they live in the entity-graph TTL output instead. Shape 29
        requires geo:targetEntity to reference a declared corp entity."""
        return tid in corp_ids

    for e in data["entities"]:
        eid = e["id"]
        subj = f"geo:{eid}"
        a(f"{subj} a geo:GeomechCorporateEntity ;")
        a(f'    geo:corporateId "{eid}" ;')
        if e.get("label_pt"):
            a(f"    geo:labelPt {lit(e['label_pt'], 'pt')} ;")
            a(f"    skos:prefLabel {lit(e['label_pt'], 'pt')} ;")
        if e.get("label_en"):
            a(f"    geo:labelEn {lit(e['label_en'], 'en')} ;")
            a(f"    skos:prefLabel {lit(e['label_en'], 'en')} ;")
        for ac in e.get("acronym") or []:
            a(f"    skos:altLabel {lit(ac)} ;")
        for v in e.get("observed_variants") or []:
            a(f"    skos:altLabel {lit(v)} ;")
        if e.get("definition_pt"):
            a(f"    geo:definitionPt {lit(e['definition_pt'], 'pt')} ;")
            a(f"    skos:definition {lit(e['definition_pt'], 'pt')} ;")
        if e.get("definition_en"):
            a(f"    geo:definitionEn {lit(e['definition_en'], 'en')} ;")
        if e.get("standard_unit"):
            a(f"    geo:standardUnit {lit(e['standard_unit'])} ;")
        for u in e.get("units_observed") or []:
            a(f"    geo:unitObserved {lit(u)} ;")
        if e.get("category"):
            a(f"    geo:category {lit(e['category'])} ;")
        if e.get("confidence"):
            a(f"    geo:confidence {lit(e['confidence'])} ;")
        for g in e.get("evidence_gaps") or []:
            a(f"    geo:evidenceGap {lit(g, 'pt')} ;")
        if e.get("osdu_mapping"):
            a(f"    geo:osduMapping {lit(e['osdu_mapping'])} ;")
        if e.get("priority_tier"):
            a(f"    geo:priorityTier {lit(e['priority_tier'])} ;")
        if e.get("external_id_chatpetrobras"):
            a(f"    geo:externalIdChatPetrobras {lit(e['external_id_chatpetrobras'])} ;")
        if e.get("owner_department"):
            a(f"    geo:ownerDepartment {lit(e['owner_department'])} ;")
        if e.get("official_datastore"):
            v = e["official_datastore"]
            for ds in (v if isinstance(v, list) else [v]):
                a(f"    geo:officialDatastore {lit(ds)} ;")
        for tool in e.get("internal_tools") or []:
            a(f"    geo:internalTool {lit(tool)} ;")
        for std in e.get("internal_standards") or []:
            a(f"    geo:internalStandard {lit(std)} ;")

        # Sources — accept both legacy [string] and structured [{doc_id,section,citation}]
        for src in e.get("sources") or []:
            if isinstance(src, str):
                a(f"    geo:source [ a geo:GeomechCorporateSource ; geo:sourceDocId {lit(src)} ] ;")
            elif isinstance(src, dict):
                doc_id = src.get("doc_id") or src.get("docId")
                section = src.get("section")
                citation = src.get("citation")
                inner = [f"a geo:GeomechCorporateSource"]
                if doc_id: inner.append(f"geo:sourceDocId {lit(doc_id)}")
                if section: inner.append(f"geo:sourceSection {lit(section)}")
                if citation: inner.append(f"geo:sourceCitation {lit(citation, 'pt')}")
                a(f"    geo:source [ {' ; '.join(inner)} ] ;")

        # Deprecation
        if e.get("deprecated"):
            dep = e["deprecated"]
            a("    geo:isDeprecated true ;")
            for rid in dep.get("replaced_by") or []:
                a(f"    geo:replacedBy geo:{rid} ;")
            if dep.get("reason"):
                a(f"    geo:deprecationReason {lit(dep['reason'], 'pt')} ;")

        # Out-of-scope
        if e.get("out_of_scope_flag"):
            oos = e["out_of_scope_flag"]
            a("    geo:isOutOfScope true ;")
            if oos.get("in_scope_for_module"):
                a(f"    geo:inScopeForModule {lit(oos['in_scope_for_module'])} ;")

        # Formula
        if e.get("formula"):
            f = e["formula"]
            if f.get("expression"):
                a(f"    geo:formulaExpression {lit(f['expression'])} ;")
            for vname, vdesc in (f.get("variables") or {}).items():
                a(f"    geo:formulaVariable [")
                a(f'        geo:variableName "{vname}" ;')
                a(f"        geo:variableDescription {lit(vdesc, 'pt')} ] ;")

        # Relations as blank nodes. If the target is deprecated, redirect
        # to the survivor and tag geo:repointedFrom so provenance is kept
        # (mirrors JS pipeline buildGeomecCorporateGraph.resolve()).
        # Cross-module edges (target outside corp module after redirect)
        # are dropped — they live in the entity-graph TTL output.
        emitted_keys: set[tuple[str, str]] = set()
        for r in e.get("relationships") or []:
            raw_tgt = r.get("target_id")
            if not raw_tgt:
                continue
            tgt, auto_repoint = resolve_target(raw_tgt)
            # Skip self-loops introduced by reroute.
            if tgt == e["id"]:
                continue
            # Skip edges whose final target is outside the corp module.
            # Shape 29 enforces internal-only references; cross-module
            # edges are represented elsewhere (entity-graph TTL).
            if not is_corporate(tgt):
                continue
            rel_type = r.get("relation_type", "")
            key = (tgt, rel_type)
            if key in emitted_keys:
                continue
            emitted_keys.add(key)
            a("    geo:hasRelation [")
            a("        a geo:GeomechCorporateRelation ;")
            a(f'        geo:relationType "{rel_type}" ;')
            a(f"        geo:targetEntity geo:{tgt} ;")
            if r.get("target_label"):
                a(f"        rdfs:label {lit(r['target_label'], 'pt')} ;")
            if r.get("edge_note"):
                a(f"        geo:edgeNote {lit(r['edge_note'], 'pt')} ;")
            # Existing _repointed_from from the JSON source takes precedence,
            # else use auto-repoint marker we computed.
            repointed = r.get("_repointed_from") or auto_repoint
            if repointed:
                a(f"        geo:repointedFrom geo:{repointed} ;")
            a("    ] ;")

        # Close entity (replace last ' ;' with ' .')
        if out[-1].endswith(" ;"):
            out[-1] = out[-1][:-2] + " ."
        elif out[-1].endswith(" ;\n"):
            out[-1] = out[-1].replace(" ;\n", " .\n")
        a("")

    return "\n".join(out) + "\n"


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    sys.stdout.write(emit(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
