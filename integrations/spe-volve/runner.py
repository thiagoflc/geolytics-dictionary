"""
Geolytics → SPE Volve Enrichment Runner
========================================
Orchestrates all semantic enrichment steps in the correct order.

Usage:
    python runner.py --sprint 1          # Quick wins (domain knowledge, RAG, acronyms, phases)
    python runner.py --sprint 2          # Medium effort (NER, lithology, formations)
    python runner.py --sprint 3          # Scale enrichment (BHA, pressure, WITSML URIs)
    python runner.py --all               # Full pipeline (all 10 enrichments)
    python runner.py --dry-run --all     # Validate without writing to Neo4j
    python runner.py --stats             # Show corpus and graph stats only
    python runner.py --step E1           # Run a single enrichment step
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Step registry
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EnrichmentStep:
    id: str
    name: str
    sprint: int
    module: str
    run_fn: str
    requires_neo4j: bool = True
    requires_openai: bool = False
    nodes_affected: str = ""
    node_count: str = ""
    description: str = ""


STEPS: list[EnrichmentStep] = [
    EnrichmentStep(
        id="E1",
        name="Domain Knowledge Expansion",
        sprint=1,
        module="agent.tools.domain_knowledge_enriched",
        run_fn=None,  # drop-in replacement, no runner needed
        requires_neo4j=False,
        requires_openai=False,
        nodes_affected="Tool layer",
        node_count="—",
        description="Replaces domain_knowledge.py with 11 topics (5 original + 6 new: "
                    "geomechanics_pressure, lithology_vocabulary, bha_component_vocabulary, "
                    "drilling_fluids, pvt_properties, npt_event_taxonomy).",
    ),
    EnrichmentStep(
        id="E2",
        name="NER Entity Extractor Expansion",
        sprint=2,
        module="ingestion.entity_extractor_enriched",
        run_fn=None,  # drop-in replacement
        requires_neo4j=True,
        requires_openai=True,
        nodes_affected="ReportChunk → graph",
        node_count="163 chunks → new entity nodes",
        description="Expands LLMGraphTransformer from 6 node types / 5 relations to "
                    "14 / 13. Re-run on existing ReportChunks to extract richer entities.",
    ),
    EnrichmentStep(
        id="E3",
        name="Lithology Normalization",
        sprint=2,
        module="ingestion.lithology_normalizer",
        run_fn="run_normalization",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="MudLogInterval",
        node_count="2,882 nodes",
        description="Maps raw lithology strings to CGI Simple Lithology canonical IDs "
                    "(437 concepts). Adds cgi_lithology_id + cgi_lithology_uri properties.",
    ),
    EnrichmentStep(
        id="E4",
        name="Formation Stratigraphic Classification",
        sprint=2,
        module="ingestion.formation_classifier",
        run_fn="run_classification",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="Formation",
        node_count="1,268 nodes",
        description="Adds formal_name, stratigraphic_rank, geologic_age, period, "
                    "cgi_lithology_uri, geosciml_uri to Formation nodes. "
                    "Covers 16 formations of Block 15/9 (Rotliegend → Shetland).",
    ),
    EnrichmentStep(
        id="E5",
        name="BHA Component Type Normalization",
        sprint=3,
        module="ingestion.bha_normalizer",
        run_fn="run_normalization",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="BHAComponent",
        node_count="10,650 nodes",
        description="Normalizes BHAComponent.type to WITSML 2.0 canonical types "
                    "(26 types, 171 exact mappings, 57 regex patterns). "
                    "Adds canonical_type, subtype, category, witsml_uri.",
    ),
    EnrichmentStep(
        id="E6",
        name="Geolytics RAG Corpus Injection",
        sprint=1,
        module="ingestion.inject_geolytics_rag",
        run_fn="inject_corpus",
        requires_neo4j=True,
        requires_openai=True,
        nodes_affected="ReportChunk (vector index)",
        node_count="+78 domain knowledge chunks",
        description="Injects 78 geolytics ontology terms as ReportChunks with "
                    "text-embedding-3-large embeddings into the vector index. "
                    "Enriches semantic search with petroleum domain knowledge.",
    ),
    EnrichmentStep(
        id="E7",
        name="Pressure Regime Classification",
        sprint=3,
        module="ingestion.pressure_classifier",
        run_fn="run_classification",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="PressurePoint",
        node_count="76,340 nodes",
        description="Classifies PressurePoint nodes into pressure regimes "
                    "(subnormal/normal/mild_overpressure/moderate/severe) and mud window "
                    "classes (tight/narrow/normal/wide). Uses APOC if available for "
                    "server-side batch processing.",
    ),
    EnrichmentStep(
        id="E8",
        name="Acronym Expansion for Reports",
        sprint=1,
        module="nlp.acronym_expander",
        run_fn="enrich_daily_reports",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="DailyReport",
        node_count="1,759 nodes",
        description="Expands drilling acronyms in DailyReport.summary_24hr before "
                    "re-embedding. Saves expanded text to summary_24hr_expanded. "
                    "Improves vector search recall for acronym-heavy queries.",
    ),
    EnrichmentStep(
        id="E9",
        name="DrillingPhase Role Enrichment (3W)",
        sprint=1,
        module="ingestion.phase_role_enricher",
        run_fn="run_enrichment",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="DrillingPhase",
        node_count="599 nodes",
        description="Adds role_3w (event_observation/signal_concept), iadc_class, "
                    "time_category, npt, npt_severity to DrillingPhase nodes. "
                    "Based on Petrobras 3W v2.0.0 and IADC drilling classification.",
    ),
    EnrichmentStep(
        id="E10",
        name="WITSML/OSDU URI Alignment",
        sprint=3,
        module="ingestion.witsml_uri_aligner",
        run_fn="run_alignment",
        requires_neo4j=True,
        requires_openai=False,
        nodes_affected="Well, Wellbore, TrajectoryStation, BHARun, DailyReport, ...",
        node_count="~4,700+ structural nodes",
        description="Adds witsml_uri, osdu_kind, geosciml_uri to structural nodes "
                    "parsed from WITSML XML. Enables semantic interoperability with "
                    "OSDU and GeoSciML ecosystems.",
    ),
]

STEPS_BY_ID: dict[str, EnrichmentStep] = {s.id: s for s in STEPS}


# ─────────────────────────────────────────────────────────────────────────────
# Neo4j driver helper
# ─────────────────────────────────────────────────────────────────────────────

def _get_driver():
    try:
        from neo4j import GraphDatabase
    except ImportError:
        log.error("neo4j package not installed. Run: uv pip install neo4j")
        sys.exit(1)

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    driver = GraphDatabase.driver(uri, auth=(user, password) if password else ("neo4j", ""))
    try:
        driver.verify_connectivity()
        log.info("Neo4j connected: %s", uri)
    except Exception as exc:
        log.error("Cannot connect to Neo4j at %s: %s", uri, exc)
        sys.exit(1)
    return driver


def _get_embedder():
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError:
        log.error("langchain-openai not installed.")
        sys.exit(1)

    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        log.error("OPENAI_API_KEY not set.")
        sys.exit(1)
    return OpenAIEmbeddings(model="text-embedding-3-large", dimensions=3072)


# ─────────────────────────────────────────────────────────────────────────────
# Step runners
# ─────────────────────────────────────────────────────────────────────────────

def _import_module(step: EnrichmentStep):
    """Dynamically import a step's module from this package."""
    import importlib
    pkg = "integrations.spe_volve"
    try:
        return importlib.import_module(f"{step.module}")
    except ModuleNotFoundError:
        # Try with package prefix
        try:
            return importlib.import_module(f"{pkg}.{step.module}")
        except ModuleNotFoundError as exc:
            log.error("Cannot import %s: %s", step.module, exc)
            return None


def run_step(step: EnrichmentStep, dry_run: bool = False) -> dict:
    """Execute a single enrichment step. Returns result dict."""
    t0 = time.monotonic()
    log.info("═" * 60)
    log.info("Starting %s — %s", step.id, step.name)
    log.info("  Nodes: %s (%s)", step.nodes_affected, step.node_count)

    # E1 and E2 are drop-in replacements — no run_fn
    if step.run_fn is None:
        log.info(
            "  %s is a drop-in replacement module. Copy %s to the SPE project "
            "to activate. No runtime action needed.",
            step.id,
            step.module,
        )
        return {"step": step.id, "status": "info", "message": "drop-in replacement"}

    mod = _import_module(step)
    if mod is None:
        return {"step": step.id, "status": "error", "message": "import failed"}

    fn = getattr(mod, step.run_fn, None)
    if fn is None:
        log.error("Function %s not found in %s", step.run_fn, step.module)
        return {"step": step.id, "status": "error", "message": f"{step.run_fn} not found"}

    if dry_run:
        log.info("  [DRY RUN] Would call %s.%s()", step.module, step.run_fn)
        return {"step": step.id, "status": "dry_run"}

    # Build kwargs
    kwargs: dict = {}

    if step.requires_neo4j:
        kwargs["driver"] = _get_driver()

    if step.id == "E6" and step.requires_openai:
        kwargs["embedder"] = _get_embedder()

    try:
        result = fn(**kwargs)
        elapsed = time.monotonic() - t0
        log.info("  ✓ %s completed in %.1fs: %s", step.id, elapsed, result)
        return {"step": step.id, "status": "ok", "elapsed_s": round(elapsed, 1), "result": result}
    except Exception as exc:
        elapsed = time.monotonic() - t0
        log.exception("  ✗ %s failed after %.1fs: %s", step.id, elapsed, exc)
        return {"step": step.id, "status": "error", "elapsed_s": round(elapsed, 1), "error": str(exc)}
    finally:
        if "driver" in kwargs:
            kwargs["driver"].close()


# ─────────────────────────────────────────────────────────────────────────────
# Summary / stats
# ─────────────────────────────────────────────────────────────────────────────

def print_stats():
    """Print corpus and step overview without connecting to Neo4j."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║   Geolytics → SPE Volve Enrichment — Step Overview          ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    for sprint in (1, 2, 3):
        sprint_steps = [s for s in STEPS if s.sprint == sprint]
        print(f"  Sprint {sprint} — {'Quick wins' if sprint == 1 else 'Medium effort' if sprint == 2 else 'Scale'}")
        for s in sprint_steps:
            neo4j_flag = "Neo4j" if s.requires_neo4j else "     "
            oai_flag = "OpenAI" if s.requires_openai else "      "
            print(f"    [{s.id}] {s.name:<40} {neo4j_flag}  {oai_flag}  {s.node_count}")
        print()

    # RAG corpus stats
    try:
        from ingestion.inject_geolytics_rag import get_corpus_stats
        stats = get_corpus_stats()
        print(f"  RAG Corpus: {stats['total']} chunks | "
              f"avg text {stats['avg_text_length']:.0f} chars | "
              f"{len(stats['by_category'])} categories")
        for cat, cnt in stats["by_category"].items():
            print(f"    • {cat}: {cnt} chunks")
    except Exception as exc:
        print(f"  RAG Corpus stats unavailable: {exc}")

    print()


def print_run_summary(results: list[dict]):
    """Print a summary table of run results."""
    ok = [r for r in results if r.get("status") == "ok"]
    err = [r for r in results if r.get("status") == "error"]
    info = [r for r in results if r.get("status") in ("info", "dry_run")]

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║   Enrichment Run Summary                                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    print(f"  Total steps: {len(results)}")
    print(f"  ✓ Completed: {len(ok)}")
    print(f"  ℹ Info/dry-run: {len(info)}")
    print(f"  ✗ Errors: {len(err)}")

    if err:
        print("\n  Errors:")
        for r in err:
            print(f"    [{r['step']}] {r.get('error', 'unknown error')}")

    total_elapsed = sum(r.get("elapsed_s", 0) for r in results)
    if total_elapsed > 0:
        print(f"\n  Total elapsed: {total_elapsed:.1f}s")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Geolytics → SPE Volve semantic enrichment runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--all", action="store_true", help="Run all enrichment steps")
    parser.add_argument("--sprint", type=int, choices=[1, 2, 3], help="Run all steps in a sprint")
    parser.add_argument("--step", metavar="ID", help="Run a single step (e.g. E3)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing to Neo4j")
    parser.add_argument("--stats", action="store_true", help="Show corpus stats and exit")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.stats:
        print_stats()
        return

    # Select steps
    if args.step:
        step_id = args.step.upper()
        if step_id not in STEPS_BY_ID:
            parser.error(f"Unknown step: {step_id}. Valid: {', '.join(STEPS_BY_ID)}")
        selected = [STEPS_BY_ID[step_id]]
    elif args.sprint:
        selected = [s for s in STEPS if s.sprint == args.sprint]
    elif args.all:
        selected = STEPS
    else:
        parser.print_help()
        return

    log.info("Running %d enrichment step(s) [dry_run=%s]", len(selected), args.dry_run)
    log.info("Started: %s", datetime.now().isoformat(timespec="seconds"))

    results = []
    for step in selected:
        result = run_step(step, dry_run=args.dry_run)
        results.append(result)

    print_run_summary(results)

    # Exit non-zero if any errors
    if any(r.get("status") == "error" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
