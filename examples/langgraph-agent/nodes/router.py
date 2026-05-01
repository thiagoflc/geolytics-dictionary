"""Router node — classifies the incoming question.

Classification:
  lookup     — single-term definition or acronym lookup
  multi_hop  — requires traversing multiple graph nodes / relations
  validation — user is making a claim that needs semantic checking
"""

from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from state import AgentState

# Keywords that signal a validation intent
_VALIDATION_SIGNALS = [
    "é válido",
    "valido",
    "é correto",
    "correto",
    "é chamado de",
    "pode ser classificado",
    "pode ser considerado",
    "reserva 4p",
    "4p",
    "reserva ambiental",
    "regime contratual",
]

# Keywords that signal multi-hop traversal
_MULTI_HOP_SIGNALS = [
    "qual a relação",
    "como se relaciona",
    "quais os campos",
    "quais os blocos",
    "quem opera",
    "lista de",
    "todos os",
    "percurso",
    "cadeia",
    "rota",
    "caminho",
    "vizinhos",
    "conectados",
    "adjacentes",
]


def _heuristic_classify(question: str) -> str:
    """Fast regex/keyword classifier — used in --no-llm mode and as fallback."""
    q = question.lower()
    for sig in _VALIDATION_SIGNALS:
        if sig in q:
            return "validation"
    for sig in _MULTI_HOP_SIGNALS:
        if sig in q:
            return "multi_hop"
    return "lookup"


def router_node(state: AgentState, llm: Any | None = None) -> AgentState:
    """Classify the question and write `classification` into state.

    When `llm` is None (--no-llm mode), falls back to the heuristic classifier.
    """
    question = state["question"]

    if llm is None:
        classification = _heuristic_classify(question)
        return {**state, "classification": classification}

    system = SystemMessage(
        content=(
            "Voce e um classificador de perguntas sobre petroleo e gas no Brasil. "
            "Classifique a pergunta do usuario em EXATAMENTE uma das tres categorias:\n"
            "  lookup     — busca de definicao ou acronimo de um unico termo\n"
            "  multi_hop  — requer traversal de multiplos nos ou relacoes no grafo\n"
            "  validation — o usuario faz uma afirmacao que precisa de checagem semantica\n"
            "Responda com apenas a palavra da categoria, sem pontuacao."
        )
    )
    human = HumanMessage(content=question)
    response = llm.invoke([system, human])
    raw = response.content.strip().lower()

    if raw not in {"lookup", "multi_hop", "validation"}:
        classification = _heuristic_classify(question)
    else:
        classification = raw

    return {**state, "classification": classification}
