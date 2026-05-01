#!/usr/bin/env python3
"""
Geolytics × GLOSIS validation pipeline.

Validates instance data (TTL/JSON-LD) against the SHACL shapes in
data/glosis/geolytics-shapes.ttl and reports conformance summary.

Usage:
  python scripts/validate.py <data-file>           # validate one instance file
  python scripts/validate.py --self-check          # smoke-test the shapes
  python scripts/validate.py --crosswalk-audit     # check crosswalk consistency
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SHAPES = ROOT / "data" / "glosis" / "geolytics-shapes.ttl"
ONTOLOGY_FILES = [
    ROOT / "data" / "glosis" / "geolytics-glosis-ext.ttl",
    ROOT / "data" / "glosis" / "geolytics-modules.ttl",
    ROOT / "data" / "glosis" / "geolytics-units.ttl",
    ROOT / "data" / "glosis" / "pvt-procedures.ttl",
    ROOT / "data" / "glosis" / "geolytics-ep-backbone.ttl",
]


def parse_ttl_files() -> "rdflib.Graph":
    """Load all Geolytics × GLOSIS ontology files into one graph."""
    import rdflib

    g = rdflib.Graph()
    for f in ONTOLOGY_FILES:
        if not f.exists():
            print(f"  WARN: missing {f.relative_to(ROOT)}", file=sys.stderr)
            continue
        g.parse(f, format="turtle")
        print(f"  parsed {f.relative_to(ROOT)}", file=sys.stderr)
    return g


def validate_instance(data_path: Path) -> int:
    """Validate one TTL/JSON-LD instance file against the shapes."""
    import pyshacl
    import rdflib

    if not SHAPES.exists():
        print(f"ERROR: shapes file missing: {SHAPES}", file=sys.stderr)
        return 2

    fmt = "json-ld" if data_path.suffix == ".jsonld" else "turtle"
    data = rdflib.Graph()
    data.parse(data_path, format=fmt)
    print(f"loaded {len(data)} instance triples from {data_path}")

    # Include the ontology graph as inference scaffold
    onto = parse_ttl_files()

    conforms, results_graph, results_text = pyshacl.validate(
        data_graph=data,
        shacl_graph=str(SHAPES),
        ont_graph=onto,
        inference="rdfs",
        meta_shacl=False,
        debug=False,
    )
    print()
    print(results_text)
    print(f"\nResult: {'PASS' if conforms else 'FAIL'}")
    return 0 if conforms else 1


def self_check() -> int:
    """Parse all ontology + shape files and report triple counts."""
    import rdflib

    overall_ok = True
    files = [SHAPES] + ONTOLOGY_FILES + [
        ROOT / "data" / "glosis" / f for f in [
            "lithology.json", "petrography-codelists.json",
            "lithology-crosswalk-cgi.json", "lithology-crosswalk-inspire-geomorph.json",
            "inspire-geomorph-codelists.json", "cgi-version-strategy.json",
        ]
    ]
    for f in files:
        if not f.exists():
            print(f"  MISSING  {f.relative_to(ROOT)}")
            overall_ok = False
            continue
        try:
            if f.suffix == ".ttl":
                g = rdflib.Graph()
                g.parse(f, format="turtle")
                print(f"  OK ({len(g):4d} triples)  {f.relative_to(ROOT)}")
            elif f.suffix == ".json":
                json.loads(f.read_text())
                print(f"  OK (json)         {f.relative_to(ROOT)}")
        except Exception as e:
            print(f"  FAIL  {f.relative_to(ROOT)}: {e}")
            overall_ok = False
    return 0 if overall_ok else 1


def crosswalk_audit() -> int:
    """Audit lithology crosswalks for consistency and dangling IRIs."""
    cw_cgi = json.loads((ROOT / "data" / "glosis" / "lithology-crosswalk-cgi.json").read_text())
    cw_insp = json.loads((ROOT / "data" / "glosis" / "lithology-crosswalk-inspire-geomorph.json").read_text())
    litho = json.loads((ROOT / "data" / "glosis" / "lithology.json").read_text())["data"]
    cgi = json.loads((ROOT / "data" / "cgi-lithology.json").read_text())["concepts"]
    cgi_ids = {c["id"] for c in cgi}

    issues = []

    # 1. Every GLOSIS lithology concept must appear in the crosswalk
    glosis_in_cw = {m["glosis_id"] for m in cw_cgi["mappings"]}
    missing = set(litho.keys()) - glosis_in_cw
    if missing:
        issues.append(f"GLOSIS concepts missing from CGI crosswalk: {sorted(missing)}")

    # 2. Every cgi_id (and cgi_targets[].id) must exist in cgi-lithology.json
    for m in cw_cgi["mappings"]:
        if m["match"] == "noMatch":
            continue
        if m.get("cgi_id") and m["cgi_id"] not in cgi_ids:
            # CGI 2016.01 has different IRIs — accept if marked as such
            if "2016.01" not in (m.get("note") or ""):
                issues.append(f"  {m['glosis_id']}: cgi_id '{m['cgi_id']}' not in cgi-lithology.json")
        for t in m.get("cgi_targets") or []:
            if t["id"] not in cgi_ids:
                issues.append(f"  {m['glosis_id']}: cgi_targets.id '{t['id']}' not in cgi-lithology.json")

    # 3. INSPIRE crosswalk must only reference codes that were noMatch in CGI
    cgi_no_match = {m["glosis_id"] for m in cw_cgi["mappings"] if m["match"] == "noMatch"}
    insp_codes = {m["glosis_id"] for m in cw_insp["mappings"]}
    overlap = insp_codes - cgi_no_match - {f"lithologyValueCode-{c}" for c in ["IB3"]}  # IB3 was promoted
    if overlap:
        issues.append(f"INSPIRE crosswalk references non-noMatch GLOSIS codes (after IB3 promotion): {sorted(overlap)}")

    # 4. Match-kind enum integrity
    valid_kinds = {"exactMatch", "closeMatch", "broadMatch", "narrowMatch", "relatedMatch", "noMatch"}
    for m in cw_cgi["mappings"] + cw_insp["mappings"]:
        if m.get("match") not in valid_kinds:
            issues.append(f"  invalid match kind: {m.get('match')} on {m.get('glosis_id')}")

    # Summary
    print(f"GLOSIS lithology concepts: {len(litho)}")
    print(f"CGI crosswalk mappings: {len(cw_cgi['mappings'])}")
    print(f"  of which noMatch: {sum(1 for m in cw_cgi['mappings'] if m['match']=='noMatch')}")
    print(f"INSPIRE crosswalk mappings: {len(cw_insp['mappings'])}")
    print(f"  with INSPIRE targets: {sum(1 for m in cw_insp['mappings'] if m.get('inspire_targets'))}")
    print()
    if issues:
        print(f"FAIL — {len(issues)} issue(s):")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("PASS — crosswalks consistent")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("data", nargs="?", help="Instance TTL/JSON-LD to validate")
    p.add_argument("--self-check", action="store_true", help="Parse all ontology + shape files")
    p.add_argument("--crosswalk-audit", action="store_true", help="Audit crosswalk consistency")
    args = p.parse_args()

    if args.crosswalk_audit:
        return crosswalk_audit()
    if args.self_check or not args.data:
        return self_check()
    return validate_instance(Path(args.data))


if __name__ == "__main__":
    sys.exit(main())
