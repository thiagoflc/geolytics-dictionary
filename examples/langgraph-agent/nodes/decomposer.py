"""Decomposer node — breaks a multi-hop question into atomic sub-queries.

Each sub-query targets a single entity or relation in the ontology graph.
In --no-llm mode, falls back to a simple sentence-split heuristic.

SWEET expansion: when a query mentions a term that has a skos:exactMatch or
skos:closeMatch SWEET alignment, _expand_with_sweet appends the aligned SWEET
class label(s) to the sub-query string. This lets downstream retrieval nodes
find documents that use the SWEET vocabulary without explicit term overlap.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from state import AgentState

# ---------------------------------------------------------------------------
# SWEET expansion helper (~25 lines)
# ---------------------------------------------------------------------------

def _load_sweet_alignment() -> dict[str, list[dict]]:
    """Load sweet-alignment.json and index by geolytics_id.

    Returns a dict mapping term id -> list of alignment records.
    Returns an empty dict if the file is not found.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "..", "..", "..", "data", "sweet-alignment.json")
    try:
        with open(candidate, encoding="utf-8") as fh:
            data = json.load(fh)
        index: dict[str, list[dict]] = {}
        for a in data.get("alignments", []):
            tid = a.get("geolytics_id")
            if tid:
                index.setdefault(tid, []).append(a)
        return index
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_SWEET_INDEX: dict[str, list[dict]] | None = None

_CLOSE_MATCH_TYPES = {"skos:exactMatch", "skos:closeMatch"}


def _expand_with_sweet(sub_query: str, sweet_index: dict[str, list[dict]]) -> str:
    """Append SWEET class labels to sub_query when a strong alignment exists.

    Iterates over known term IDs and checks if the sub_query mentions any of
    them. For each hit with exactMatch or closeMatch, appends the SWEET class
    local name(s) to the query string so semantic search can match SWEET-
    vocabulary documents.

    Only appends when not already present to avoid duplicating expansion.
    """
    lower = sub_query.lower()
    additions: list[str] = []
    for term_id, alignments in sweet_index.items():
        term_label = term_id.replace("-", " ")
        if term_label not in lower:
            continue
        for a in alignments:
            if a.get("alignment_type") not in _CLOSE_MATCH_TYPES:
                continue
            for uri in a.get("sweet_uris", []):
                # Extract the local name after the last '/'
                local = uri.rsplit("/", 1)[-1]
                if local.lower() not in lower:
                    additions.append(local)
    if additions:
        return sub_query + " [SWEET: " + ", ".join(additions) + "]"
    return sub_query


# ---------------------------------------------------------------------------
# Decomposer
# ---------------------------------------------------------------------------

def _heuristic_decompose(question: str) -> list[str]:
    """Split the question into sub-queries by conjunctions / punctuation."""
    parts = re.split(r"[;,] | e | ou | depois | seguido de ", question, flags=re.IGNORECASE)
    sub_queries = [p.strip() for p in parts if p.strip()]
    if len(sub_queries) == 1:
        # No natural break found: treat the whole question as a single hop
        return [question]
    return sub_queries


def decomposer_node(state: AgentState, llm: Any | None = None) -> AgentState:
    """Decompose a multi-hop question into a list of sub-queries.

    Writes `decomposed` (list[str]) into state.
    If the question is not multi_hop this node is a no-op (returns unchanged state).

    SWEET expansion is applied to each sub-query when a strong alignment exists.
    """
    global _SWEET_INDEX
    if _SWEET_INDEX is None:
        _SWEET_INDEX = _load_sweet_alignment()

    if state.get("classification") != "multi_hop":
        sub_queries = [state["question"]]
        expanded = [_expand_with_sweet(q, _SWEET_INDEX) for q in sub_queries]
        return {**state, "decomposed": expanded}

    question = state["question"]

    if llm is None:
        sub_queries = _heuristic_decompose(question)
        expanded = [_expand_with_sweet(q, _SWEET_INDEX) for q in sub_queries]
        return {**state, "decomposed": expanded}

    system = SystemMessage(
        content=(
            "Voce e um agente especializado em ontologia de petroleo e gas. "
            "Dada uma pergunta de multiplos passos, decomponha-a em sub-consultas atomicas. "
            "Cada sub-consulta deve referir-se a um unico conceito ou relacao do dominio. "
            "Retorne APENAS uma lista JSON de strings, sem nenhum texto adicional.\n"
            'Exemplo: ["Qual o operador do Campo de Buzios?", "Qual o regime contratual de Buzios?"]'
        )
    )
    human = HumanMessage(content=question)
    response = llm.invoke([system, human])
    raw = response.content.strip()

    # Parse the JSON list
    try:
        import json as _json
        sub_queries: list[str] = _json.loads(raw)
        if not isinstance(sub_queries, list):
            raise ValueError("Expected a list")
    except Exception:
        sub_queries = _heuristic_decompose(question)

    expanded = [_expand_with_sweet(q, _SWEET_INDEX) for q in sub_queries]
    return {**state, "decomposed": expanded}
