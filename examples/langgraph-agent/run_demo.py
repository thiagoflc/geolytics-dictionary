"""CLI entry point for the Geolytics LangGraph reference agent.

Usage
-----
    python run_demo.py "Em qual regime contratual esta o Bloco BS-500?"
    python run_demo.py "Reserva 4P do Campo de Buzios" --no-llm
    python run_demo.py "Qual a relacao entre poco e campo?" --no-llm --no-embed

Flags
-----
--no-llm    Run without any LLM call; LLM nodes use deterministic stubs.
            The validator always runs (it never calls an LLM).
--no-embed  Disable sentence-transformer embeddings; use BM25 for retrieval
            (BM25 is already the default, this flag is a no-op unless you
            have enabled embeddings via USE_EMBEDDINGS=1).
--verbose   Print the full intermediate state between each node transition.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap

# Make the package importable when running from the repo root or the
# examples/langgraph-agent/ directory
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import agent as _agent_module
from state import AgentState


def _print_separator(title: str) -> None:
    width = 72
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def _print_state_transition(label: str, state: AgentState, verbose: bool) -> None:
    _print_separator(label)
    if verbose:
        # Pretty-print full state (truncate long strings for readability)
        for key, value in state.items():
            if isinstance(value, str) and len(value) > 300:
                print(f"  {key}: {value[:300]}... [truncated]")
            elif isinstance(value, list) and len(str(value)) > 400:
                print(f"  {key}: [{len(value)} items] {str(value)[:300]}...")
            else:
                print(f"  {key}: {value!r}")
    else:
        # Summary only
        print(f"  classification : {state.get('classification', 'N/A')}")
        print(f"  decomposed     : {state.get('decomposed', [])}")
        print(f"  graph_found    : {sum(1 for r in (state.get('graph_results') or []) if r.get('found'))}")
        print(f"  rag_chunks     : {len(state.get('rag_results') or [])}")
        valid = state.get("validation", {})
        if valid:
            print(f"  valid          : {valid.get('valid', True)}")
            for v in valid.get("violations", []):
                print(f"    VIOLATION [{v['rule']}]: {v['evidence']}")
        print(f"  iteration      : {state.get('iteration', 0)}")


def _print_final_answer(state: AgentState) -> None:
    _print_separator("RESPOSTA FINAL")
    answer = state.get("final_answer") or state.get("draft") or "(sem resposta)"
    print(textwrap.fill(answer, width=80, subsequent_indent="  ") if "\n" not in answer else answer)


def _build_graph_with_hooks(
    no_llm: bool,
    use_embeddings: bool,
    verbose: bool,
) -> tuple[Any, dict]:
    """Build the graph and a step collector dict."""
    from langgraph.graph import END, StateGraph
    import agent as _ag

    llm = None if no_llm else _ag._make_llm()
    graph = _ag.build_graph(llm=llm, use_embeddings=use_embeddings)
    return graph, {}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Geolytics LangGraph reference agent demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python run_demo.py "O que e Bloco exploratorio?"
              python run_demo.py "Reserva 4P do Campo de Buzios" --no-llm
              python run_demo.py "Qual a relacao entre poco e bloco?" --no-llm --verbose
            """
        ),
    )
    parser.add_argument("question", help="Question to answer (in Portuguese)")
    parser.add_argument(
        "--no-llm",
        action="store_true",
        default=False,
        help="Run offline; LLM nodes use deterministic stubs (validator always runs).",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        default=False,
        help="Disable sentence-transformer embeddings; use BM25 (this is already the default).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print full intermediate state at each transition.",
    )

    args = parser.parse_args()

    use_embeddings = not args.no_embed and os.getenv("USE_EMBEDDINGS", "0") == "1"

    _print_separator("GEOLYTICS LANGGRAPH AGENT — DEMO")
    print(f"  question    : {args.question}")
    print(f"  no_llm      : {args.no_llm}")
    print(f"  embeddings  : {use_embeddings}")

    # Run the graph
    try:
        from agent import invoke
        final_state = invoke(
            question=args.question,
            no_llm=args.no_llm,
            use_embeddings=use_embeddings,
        )
    except Exception as exc:
        print(f"\nERRO ao executar o agente: {exc}", file=sys.stderr)
        raise

    _print_state_transition("ESTADO FINAL", final_state, verbose=args.verbose)
    _print_final_answer(final_state)

    # Exit with code 1 if validation failed (useful for CI)
    validation = final_state.get("validation", {})
    if validation and not validation.get("valid", True):
        sys.exit(1)


# Allow importing from tests without running main()
Any = object  # noqa: N816

if __name__ == "__main__":
    main()
