"""Synthesizer node — composes the final answer with citations.

When `llm` is provided the node calls the language model to produce a
natural-language answer grounded in the graph and RAG results.
In --no-llm mode it produces a deterministic template-based answer.

Citations reference entity ids (from the graph) and source layers
(geocoverage fields).
"""

from __future__ import annotations

import json
import textwrap
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from state import AgentState

_SYSTEM_PROMPT = textwrap.dedent(
    """
    Voce e um especialista em petroleo e gas (E&P) brasileiro.
    Responda a pergunta do usuario usando EXCLUSIVAMENTE as informacoes fornecidas
    nos contextos abaixo (grafo ontologico + corpus RAG).
    Regras obrigatorias:
    - Cite os ids das entidades do grafo entre colchetes, ex: [regime-contratual].
    - Mencione a camada de origem (geocoverage) quando relevante.
    - Se houver violacoes de validacao, incorpore a correcao na resposta.
    - Responda em portugues, de forma concisa e tecnicamente precisa.
    - Nao invente informacoes que nao estao nos contextos fornecidos.
    """
).strip()


def _build_context(state: AgentState) -> str:
    """Serialize graph and RAG results into a compact text context."""
    parts: list[str] = []

    graph_results = state.get("graph_results") or []
    if graph_results:
        parts.append("=== CONTEXTO DO GRAFO ONTOLOGICO ===")
        for item in graph_results:
            if not item.get("found"):
                parts.append(f"[nao encontrado para: {item.get('query','')}]")
                continue
            node = item.get("node", {})
            parts.append(
                f"Entidade: {node.get('id')} | {node.get('label')} ({node.get('label_en','')})"
            )
            if node.get("definition"):
                parts.append(f"Definicao: {node['definition'][:300]}")
            if node.get("examples"):
                parts.append(f"Exemplos: {', '.join(node['examples'][:3])}")
            if node.get("geocoverage"):
                parts.append(f"Camadas: {', '.join(node['geocoverage'])}")
            neighbours = item.get("neighbours", [])
            if neighbours:
                rels = [
                    f"{n['from']} --[{n.get('relation_label_pt', n.get('relation',''))}]--> {n['to']}"
                    for n in neighbours[:5]
                ]
                parts.append("Relacoes: " + "; ".join(rels))
        parts.append("")

    rag_results = state.get("rag_results") or []
    if rag_results:
        parts.append("=== CONTEXTO DO CORPUS RAG ===")
        for chunk in rag_results[:3]:
            parts.append(f"[{chunk.get('id','')}] {chunk.get('text','')[:400]}")
        parts.append("")

    validation = state.get("validation")
    if validation and validation.get("violations"):
        errors = [v for v in validation["violations"] if v.get("severity", "error") == "error"]
        provisionals = [v for v in validation["violations"] if v.get("severity") == "provisional"]
        warns = [v for v in validation["violations"] if v.get("severity") == "warn"]
        if errors:
            parts.append("=== VIOLACOES DE VALIDACAO SEMANTICA ===")
            for v in errors:
                parts.append(f"Regra: {v['rule']}")
                parts.append(f"Evidencia: {v['evidence']}")
                parts.append(f"Correcao: {v['suggested_fix']}")
            parts.append("")
        if provisionals:
            parts.append("=== AVISO: RESPOSTA PROVISORIA (baixa confiança das fontes) ===")
            for v in provisionals:
                parts.append(f"Regra: {v['rule']}")
                parts.append(f"Evidencia: {v['evidence']}")
                parts.append(f"Orientacao: {v['suggested_fix']}")
            parts.append("")
        if warns:
            parts.append("=== AVISOS NAO-BLOQUEANTES ===")
            for v in warns:
                parts.append(f"Regra: {v['rule']}")
                parts.append(f"Evidencia: {v['evidence']}")
                parts.append(f"Orientacao: {v['suggested_fix']}")
            parts.append("")

    return "\n".join(parts)


def _template_answer(state: AgentState) -> str:
    """Produce a deterministic answer (--no-llm mode)."""
    question = state.get("question", "")
    graph_results = state.get("graph_results") or []
    rag_results = state.get("rag_results") or []
    validation = state.get("validation")

    lines: list[str] = [f"Pergunta: {question}", ""]

    # Findings come first — split by severity
    if validation and validation.get("violations"):
        errors = [v for v in validation["violations"] if v.get("severity", "error") == "error"]
        provisionals = [v for v in validation["violations"] if v.get("severity") == "provisional"]
        warns = [v for v in validation["violations"] if v.get("severity") == "warn"]
        if errors:
            lines.append("AVISO DE VALIDACAO SEMANTICA:")
            for v in errors:
                lines.append(f"  [{v['rule']}] {v['evidence']}")
                lines.append(f"  Correcao: {v['suggested_fix']}")
            lines.append("")
        if provisionals:
            lines.append("RESPOSTA PROVISORIA — baixa confianca das fontes corporativas:")
            for v in provisionals:
                lines.append(f"  [{v['rule']}] {v['evidence']}")
                lines.append(f"  Orientacao: {v['suggested_fix']}")
            lines.append("")
        if warns:
            lines.append("AVISOS NAO-BLOQUEANTES:")
            for v in warns:
                lines.append(f"  [{v['rule']}] {v['evidence']}")
                lines.append(f"  Orientacao: {v['suggested_fix']}")
            lines.append("")

    # Graph findings
    found_nodes: list[str] = []
    for item in graph_results:
        if item.get("found"):
            node = item.get("node", {})
            entity_id = node.get("id", "")
            label = node.get("label", "")
            definition = node.get("definition", "")[:200]
            layers = ", ".join(node.get("geocoverage", []))
            found_nodes.append(
                f"[{entity_id}] {label}: {definition} (camadas: {layers})"
            )

    if found_nodes:
        lines.append("Entidades encontradas no grafo:")
        lines.extend(f"  - {n}" for n in found_nodes)
        lines.append("")

    # RAG findings
    if rag_results:
        lines.append("Trechos relevantes do corpus:")
        for chunk in rag_results[:2]:
            lines.append(f"  [{chunk.get('id','')}] {chunk.get('text','')[:200]}...")
        lines.append("")

    if not found_nodes and not rag_results:
        lines.append("Nenhuma informacao relevante encontrada no corpus para esta consulta.")

    return "\n".join(lines)


def synthesizer_node(state: AgentState, llm: Any | None = None) -> AgentState:
    """Compose the final answer.

    If a previous `draft` exists (correction loop), the validation context
    is included so the LLM can address the violations.
    """
    if llm is None:
        draft = _template_answer(state)
        return {**state, "draft": draft, "final_answer": draft}

    context = _build_context(state)
    question = state["question"]

    # On second pass include the prior draft for correction
    prior_draft = state.get("draft", "")
    iteration = state.get("iteration", 0)

    user_content = f"Pergunta: {question}\n\n{context}"
    if prior_draft and iteration > 0:
        user_content += f"\n\n=== RASCUNHO ANTERIOR (corrigir as violacoes acima) ===\n{prior_draft}"

    system = SystemMessage(content=_SYSTEM_PROMPT)
    human = HumanMessage(content=user_content)
    response = llm.invoke([system, human])
    draft = response.content.strip()

    return {**state, "draft": draft, "final_answer": draft}
