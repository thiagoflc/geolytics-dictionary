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

        # Relations as blank nodes
        for r in e.get("relationships") or []:
            tgt = r.get("target_id")
            if not tgt:
                continue
            a("    geo:hasRelation [")
            a("        a geo:GeomechCorporateRelation ;")
            a(f'        geo:relationType "{r.get("relation_type","")}" ;')
            a(f"        geo:targetEntity geo:{tgt} ;")
            if r.get("target_label"):
                a(f"        rdfs:label {lit(r['target_label'], 'pt')} ;")
            if r.get("edge_note"):
                a(f"        geo:edgeNote {lit(r['edge_note'], 'pt')} ;")
            if r.get("_repointed_from"):
                a(f'        geo:repointedFrom geo:{r["_repointed_from"]} ;')
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
