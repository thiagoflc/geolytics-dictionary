#!/usr/bin/env python3
"""Validate data/geomechanics-corporate.json against SHACL shapes 23-30.

Runs end-to-end:
  1. Serializes the JSON module to TTL (in-memory).
  2. Loads data/geolytics-shapes.ttl.
  3. Runs pyshacl with rdfs inference.
  4. Prints PT-BR report; exits 0 on conformance, 1 on violations.

Usage:
    python scripts/validate-geomec-corporate.py
    python scripts/validate-geomec-corporate.py --verbose
"""
from __future__ import annotations
import argparse
import importlib.util
import sys
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHAPES = ROOT / "data" / "geolytics-shapes.ttl"

# Reuse serializer module
spec = importlib.util.spec_from_file_location(
    "geomec_ttl", ROOT / "scripts" / "geomec-corporate-to-ttl.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> int:
    p = argparse.ArgumentParser(description="SHACL validator — Geomech Corporate L6")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--write-ttl", help="Also write the serialized TTL to this path")
    args = p.parse_args()

    try:
        import json
        import pyshacl
        from rdflib import Graph
    except ImportError as e:
        print(f"ERRO: dependência ausente — {e}. Rode: pip install -r scripts/requirements.txt", file=sys.stderr)
        return 2

    src_json = ROOT / "data" / "geomechanics-corporate.json"
    print(f"Lendo {src_json.relative_to(ROOT)} …")
    data_obj = json.loads(src_json.read_text(encoding="utf-8"))
    n_ent = len(data_obj["entities"])
    n_rel = sum(len(e.get("relationships") or []) for e in data_obj["entities"])
    print(f"  entidades: {n_ent}  relações: {n_rel}")

    ttl = mod.emit(data_obj)
    if args.write_ttl:
        Path(args.write_ttl).write_text(ttl, encoding="utf-8")
        print(f"  TTL escrito em {args.write_ttl}")

    data_g = Graph().parse(data=ttl, format="turtle")
    shapes_g = Graph().parse(SHAPES, format="turtle")
    print(f"Validando contra {SHAPES.relative_to(ROOT)} ({len(shapes_g)} triples) …")

    conforms, results_g, results_text = pyshacl.validate(
        data_graph=data_g,
        shacl_graph=shapes_g,
        inference="rdfs",
        abort_on_first=False,
        allow_warnings=True,
    )

    from rdflib.namespace import RDF
    from rdflib import Namespace
    SH = Namespace("http://www.w3.org/ns/shacl#")
    viols = list(results_g.subjects(RDF.type, SH.ValidationResult))

    if conforms:
        print(f"\n✓ CONFORME — {n_ent} entidades, {n_rel} relações, 0 violações.")
        return 0

    print(f"\n✗ NÃO-CONFORME — {len(viols)} violações:")
    for v in viols:
        focus = next(iter(results_g.objects(v, SH.focusNode)), "?")
        msg = next(iter(results_g.objects(v, SH.resultMessage)), "?")
        path = next(iter(results_g.objects(v, SH.resultPath)), None)
        focus_short = str(focus).split("/")[-1] if str(focus).startswith("http") else str(focus)
        path_short = f" [{str(path).split('/')[-1]}]" if path else ""
        print(f"  • {focus_short}{path_short}: {msg}")
    if args.verbose:
        print("\n--- Relatório completo (pyshacl) ---")
        print(results_text)
    return 1


if __name__ == "__main__":
    sys.exit(main())
