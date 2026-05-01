#!/usr/bin/env python3
"""
validate-shacl.py — Valida data/geolytics.ttl contra data/geolytics-shapes.ttl
usando pyshacl.

Saida: relatorio legivel em PT-BR no stdout.
Codigo de saida: 0 se conforme, 1 se houver violacoes.

Uso:
    python scripts/validate-shacl.py
    python scripts/validate-shacl.py --data path/to/data.ttl
    python scripts/validate-shacl.py --shapes path/to/shapes.ttl
    python scripts/validate-shacl.py --ontology path/to/vocab.ttl
    python scripts/validate-shacl.py --verbose
"""

import sys
import os
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validador SHACL do Geolytics Dictionary (PT-BR)"
    )
    parser.add_argument(
        "--data",
        default=None,
        help="Caminho para o grafo de dados (padrao: data/geolytics.ttl)",
    )
    parser.add_argument(
        "--shapes",
        default=None,
        help="Caminho para o arquivo de shapes (padrao: data/geolytics-shapes.ttl)",
    )
    parser.add_argument(
        "--ontology",
        default=None,
        help="Caminho para o vocabulario OWL de apoio (padrao: data/geolytics-vocab.ttl)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe o relatorio SHACL completo (ingles) alem do resumo PT-BR",
    )
    parser.add_argument(
        "--no-ontology",
        action="store_true",
        help="Nao carrega o vocabulario OWL de apoio",
    )
    args = parser.parse_args()

    # Resolve root directory (one level above this script)
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent

    data_path = Path(args.data) if args.data else root / "data" / "geolytics.ttl"
    shapes_path = (
        Path(args.shapes) if args.shapes else root / "data" / "geolytics-shapes.ttl"
    )
    vocab_path = (
        Path(args.ontology)
        if args.ontology
        else root / "data" / "geolytics-vocab.ttl"
    )

    # Check files exist
    for label, p in [
        ("Dados", data_path),
        ("Shapes", shapes_path),
    ]:
        if not p.exists():
            print(f"[ERRO] {label}: arquivo nao encontrado: {p}", file=sys.stderr)
            return 2

    # Attempt import — helpful message if not installed
    try:
        from pyshacl import validate
        from rdflib import Graph
    except ImportError as exc:
        print(
            "\n[ERRO] Dependencias nao instaladas.\n"
            "Execute:\n"
            "    python3 -m pip install --user pyshacl rdflib\n"
            "ou, para o ambiente atual:\n"
            "    pip install -r scripts/requirements.txt\n"
            f"\nDetalhe: {exc}",
            file=sys.stderr,
        )
        return 2

    # Load data graph
    print("=" * 70)
    print("Validador SHACL — Geolytics Dictionary")
    print("=" * 70)
    print(f"  Dados   : {data_path}")
    print(f"  Shapes  : {shapes_path}")

    data_graph = Graph()
    try:
        data_graph.parse(str(data_path), format="turtle")
    except Exception as exc:
        print(f"[ERRO] Falha ao parsear dados: {exc}", file=sys.stderr)
        return 2

    print(f"  Triplas no grafo de dados: {len(data_graph)}")

    # Load shapes graph
    shapes_graph = Graph()
    try:
        shapes_graph.parse(str(shapes_path), format="turtle")
    except Exception as exc:
        print(f"[ERRO] Falha ao parsear shapes: {exc}", file=sys.stderr)
        return 2

    print(f"  Shapes carregados: {len(shapes_graph)} triplas")

    # Optionally load ontology / vocabulary graph
    ont_graph = None
    if not args.no_ontology and vocab_path.exists():
        ont_graph = Graph()
        try:
            ont_graph.parse(str(vocab_path), format="turtle")
            print(f"  Vocabulario OWL : {vocab_path} ({len(ont_graph)} triplas)")
        except Exception as exc:
            print(
                f"[AVISO] Nao foi possivel carregar o vocabulario OWL: {exc}",
                file=sys.stderr,
            )
            ont_graph = None
    elif args.no_ontology:
        print("  Vocabulario OWL : desabilitado (--no-ontology)")
    else:
        print(
            f"  Vocabulario OWL : nao encontrado em {vocab_path} (continuando sem ele)"
        )

    print()

    # Run SHACL validation
    try:
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            ont_graph=ont_graph,
            inference="rdfs",
            abort_on_first=False,
            allow_warnings=True,
            meta_shacl=False,
            advanced=True,
            js=False,
            debug=False,
        )
    except Exception as exc:
        print(f"[ERRO] Falha durante validacao SHACL: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2

    # Parse results for PT-BR summary
    violations = _parse_violations(results_graph)

    # Print PT-BR report
    _print_report(conforms, violations, args.verbose, results_text)

    return 0 if conforms else 1


def _parse_violations(results_graph) -> list[dict]:
    """Extract violation details from the results graph."""
    try:
        from rdflib import Graph, Namespace, RDF, SH
        from rdflib.namespace import SH as SH_NS
    except ImportError:
        return []

    violations = []
    SH = Namespace("http://www.w3.org/ns/shacl#")

    for result in results_graph.subjects(
        predicate=None, object=SH.ValidationResult
    ):
        pass

    # Use SPARQL for robustness
    q = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT ?focus ?path ?message ?severity ?value ?sourceShape
    WHERE {
        ?result a sh:ValidationResult .
        ?result sh:focusNode ?focus .
        OPTIONAL { ?result sh:resultPath ?path }
        OPTIONAL { ?result sh:resultMessage ?message }
        OPTIONAL { ?result sh:resultSeverity ?severity }
        OPTIONAL { ?result sh:value ?value }
        OPTIONAL { ?result sh:sourceShape ?sourceShape }
    }
    ORDER BY ?focus ?path
    """
    try:
        for row in results_graph.query(q):
            violations.append(
                {
                    "focus": str(row.focus) if row.focus else "—",
                    "path": str(row.path) if row.path else "—",
                    "message": str(row.message) if row.message else "",
                    "severity": _short_severity(str(row.severity)) if row.severity else "Violacao",
                    "value": str(row.value) if row.value else "—",
                    "source_shape": str(row.sourceShape) if row.sourceShape else "—",
                }
            )
    except Exception:
        pass

    return violations


def _short_severity(uri: str) -> str:
    """Convert SHACL severity URI to short PT-BR label."""
    mapping = {
        "http://www.w3.org/ns/shacl#Violation": "Violacao",
        "http://www.w3.org/ns/shacl#Warning": "Aviso",
        "http://www.w3.org/ns/shacl#Info": "Informacao",
    }
    return mapping.get(uri, uri.split("#")[-1] if "#" in uri else uri)


def _shorten(uri: str, max_len: int = 80) -> str:
    """Shorten a URI for display."""
    prefixes = {
        "https://geolytics.petrobras.com.br/dict/": "geo:",
        "http://www.w3.org/ns/shacl#": "sh:",
        "http://www.w3.org/2002/07/owl#": "owl:",
        "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
        "http://www.w3.org/2004/02/skos/core#": "skos:",
        "https://w3id.org/osdu#": "osdu:",
    }
    for prefix, short in prefixes.items():
        if uri.startswith(prefix):
            uri = short + uri[len(prefix):]
            break
    return uri[:max_len] + ("..." if len(uri) > max_len else "")


def _print_report(conforms: bool, violations: list[dict], verbose: bool, raw_text: str) -> None:
    """Print a human-readable PT-BR validation report."""
    print("─" * 70)
    if conforms:
        print("RESULTADO: CONFORME")
        print("O grafo de dados esta em conformidade com todos os shapes SHACL.")
    else:
        n = len(violations)
        print(f"RESULTADO: NAO CONFORME — {n} violacao(oes) encontrada(s)")
        print()
        print("NOTA: Violacoes em classes de instancias (geo:Poco, geo:Bloco, etc.)")
        print("      indicam que o grafo-alvo contem dados de instancia que nao")
        print("      satisfazem os shapes. Violacoes em owl:Class / owl:ObjectProperty")
        print("      sao esperadas quando o dados.ttl usa as classes como schema,")
        print("      nao como instancias.")
        print()

    if violations:
        print("─" * 70)
        print("DETALHES DAS VIOLACOES:")
        print()
        for i, v in enumerate(violations, 1):
            print(f"  [{i}] {v['severity']}")
            print(f"       No          : {_shorten(v['focus'])}")
            if v["path"] != "—":
                print(f"       Propriedade : {_shorten(v['path'])}")
            if v["value"] != "—":
                print(f"       Valor       : {_shorten(v['value'])}")
            if v["message"]:
                # Print only the first 200 chars to keep report readable
                msg = v["message"][:200]
                print(f"       Mensagem    : {msg}")
            if v["source_shape"] != "—":
                print(f"       Shape       : {_shorten(v['source_shape'])}")
            print()

    print("─" * 70)

    # Categorize findings
    if violations:
        severity_counts: dict[str, int] = {}
        for v in violations:
            severity_counts[v["severity"]] = severity_counts.get(v["severity"], 0) + 1
        print("RESUMO POR SEVERIDADE:")
        for sev, count in sorted(severity_counts.items()):
            print(f"  {sev}: {count}")
        print()
        print("INTERPRETACAO:")
        print("  Violacoes de shapes que targetam owl:Class ou owl:ObjectProperty")
        print("  sao 'achados de dados' — indicam que o TTL usa essas entidades como")
        print("  schema (sem instancias de geo:Poco, geo:Bloco etc.). Para validar")
        print("  instancias, popule o grafo com dados de instancia conforme o")
        print("  vocabulario em data/geolytics-vocab.ttl.")

    if verbose and raw_text:
        print()
        print("=" * 70)
        print("RELATORIO SHACL COMPLETO (ingles):")
        print("=" * 70)
        print(raw_text)


if __name__ == "__main__":
    sys.exit(main())
