"""Decomposer node — breaks a multi-hop question into atomic sub-queries.

Each sub-query targets a single entity or relation in the ontology graph.
In --no-llm mode, falls back to a simple sentence-split heuristic.
"""

from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from state import AgentState


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
    """
    if state.get("classification") != "multi_hop":
        return {**state, "decomposed": [state["question"]]}

    question = state["question"]

    if llm is None:
        sub_queries = _heuristic_decompose(question)
        return {**state, "decomposed": sub_queries}

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
        import json
        sub_queries: list[str] = json.loads(raw)
        if not isinstance(sub_queries, list):
            raise ValueError("Expected a list")
    except Exception:
        sub_queries = _heuristic_decompose(question)

    return {**state, "decomposed": sub_queries}
