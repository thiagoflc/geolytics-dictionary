"""LangGraph DAG for the Geolytics reference agent.

Graph topology
--------------

                      +----------+
        question ---> |  Router  |
                      +-----+----+
                            |
              +-------------+--------------+
              |             |              |
           lookup       multi_hop      validation
              |             |              |
              v             v              |
         +--------+   +----------+        |
         |  RAG   |   |Decomposer|        |
         |Retrieve|   +----+-----+        |
         +---+----+        |              |
             |         +---+----+         |
             |         |GraphQry|         |
             |         +---+----+         |
             |             |              |
             +------+-------+-------------+
                    |
               +----+----+
               |Validator|
               +----+----+
                    |
          +---------+---------+
          | valid?            |
          |                   |
    yes (or max iter)    no (iter<2)
          |                   |
     +----+----+       +------+------+
     |Synthesize|      | Synthesize  |
     |(final)   |      |(draft+corr) |
     +----------+      +------+------+
                              |
                           (loop back to Validator)

Edges
-----
Router    -> RAGRetrieve  (lookup)
Router    -> Decomposer   (multi_hop)
Router    -> Validator    (validation — skip retrieval, validate claim directly)
Decomposer-> GraphQuery
GraphQuery-> RAGRetrieve
RAGRetrieve-> Validator
Validator -> Synthesizer  (valid=True OR iteration>=2)
Validator -> Synthesizer  (valid=False, iteration<2) with correction request
Synthesizer-> END         (always; loop is managed by the conditional edge)
"""

from __future__ import annotations

import functools
import os
from typing import Any

from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph

from state import AgentState
from nodes.router import router_node
from nodes.decomposer import decomposer_node
from nodes.graph_query import graph_query_node
from nodes.rag_retrieve import rag_retrieve_node
from nodes.validator import validator_node
from nodes.synthesizer import synthesizer_node

_MAX_ITERATIONS = 2


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------


def _make_llm() -> Runnable | None:
    """Instantiate the LLM based on env-var LLM_PROVIDER.

    Returns None if no API key is available (graceful degradation).
    """
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        from langchain_openai import ChatOpenAI  # type: ignore[import]

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, api_key=api_key)

    # Default: anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    from langchain_anthropic import ChatAnthropic  # type: ignore[import]

    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    return ChatAnthropic(model=model, api_key=api_key)


# ---------------------------------------------------------------------------
# Node wrappers that capture llm + config at compile time
# ---------------------------------------------------------------------------


def _wrap_router(llm: Runnable | None) -> Any:
    def _node(state: AgentState) -> AgentState:
        return router_node(state, llm=llm)

    _node.__name__ = "router"
    return _node


def _wrap_decomposer(llm: Runnable | None) -> Any:
    def _node(state: AgentState) -> AgentState:
        return decomposer_node(state, llm=llm)

    _node.__name__ = "decomposer"
    return _node


def _wrap_rag(use_embeddings: bool) -> Any:
    def _node(state: AgentState) -> AgentState:
        return rag_retrieve_node(state, use_embeddings=use_embeddings)

    _node.__name__ = "rag_retrieve"
    return _node


def _wrap_synthesizer(llm: Runnable | None) -> Any:
    def _node(state: AgentState) -> AgentState:
        return synthesizer_node(state, llm=llm)

    _node.__name__ = "synthesizer"
    return _node


# ---------------------------------------------------------------------------
# Conditional edge logic
# ---------------------------------------------------------------------------


def _route_from_router(state: AgentState) -> str:
    """Direct traffic after Router based on classification."""
    classification = state.get("classification", "lookup")
    if classification == "multi_hop":
        return "decomposer"
    if classification == "validation":
        return "validator"
    # lookup: go straight to RAG
    return "rag_retrieve"


def _route_after_validator(state: AgentState) -> str:
    """Loop back to synthesizer for corrections or proceed to final answer."""
    iteration = state.get("iteration", 0)
    validation = state.get("validation", {})
    valid = validation.get("valid", True)

    if valid or iteration >= _MAX_ITERATIONS:
        return "synthesizer_final"
    return "synthesizer_draft"


# ---------------------------------------------------------------------------
# Graph compilation
# ---------------------------------------------------------------------------


def build_graph(
    llm: Runnable | None = None,
    use_embeddings: bool = False,
) -> Any:
    """Build and compile the LangGraph StateGraph.

    Parameters
    ----------
    llm:
        Language model instance.  Pass None to run fully offline.
    use_embeddings:
        When True, the RAGRetrieve node attempts sentence-transformer embeddings.
    """
    builder: StateGraph = StateGraph(AgentState)

    # --- Register nodes ---
    builder.add_node("router", _wrap_router(llm))
    builder.add_node("decomposer", _wrap_decomposer(llm))
    builder.add_node("graph_query", graph_query_node)
    builder.add_node("rag_retrieve", _wrap_rag(use_embeddings))
    builder.add_node("validator", validator_node)

    # Two synthesizer aliases: one for draft (correction loop), one for final
    builder.add_node("synthesizer_final", _wrap_synthesizer(llm))
    builder.add_node("synthesizer_draft", _wrap_synthesizer(llm))

    # --- Entry point ---
    builder.set_entry_point("router")

    # --- Static edges ---
    builder.add_edge("decomposer", "graph_query")
    builder.add_edge("graph_query", "rag_retrieve")
    builder.add_edge("rag_retrieve", "validator")
    builder.add_edge("synthesizer_final", END)

    # synthesizer_draft increments iteration and loops back to validator
    def _increment_and_validate(state: AgentState) -> AgentState:
        """Increment iteration counter then run validator again."""
        state = dict(state)
        state["iteration"] = state.get("iteration", 0) + 1
        return validator_node(state)  # type: ignore[arg-type]

    builder.add_node("revalidate", _increment_and_validate)
    builder.add_edge("synthesizer_draft", "revalidate")
    builder.add_conditional_edges(
        "revalidate",
        _route_after_validator,
        {"synthesizer_final": "synthesizer_final", "synthesizer_draft": "synthesizer_draft"},
    )

    # --- Conditional edge from router ---
    builder.add_conditional_edges(
        "router",
        _route_from_router,
        {
            "decomposer": "decomposer",
            "rag_retrieve": "rag_retrieve",
            "validator": "validator",
        },
    )

    # --- Conditional edge from first validator pass ---
    builder.add_conditional_edges(
        "validator",
        _route_after_validator,
        {"synthesizer_final": "synthesizer_final", "synthesizer_draft": "synthesizer_draft"},
    )

    return builder.compile()


def invoke(question: str, no_llm: bool = False, use_embeddings: bool = False) -> AgentState:
    """Convenience wrapper: build graph and run a single question.

    Parameters
    ----------
    question:
        The natural-language question to answer.
    no_llm:
        When True, skip LLM instantiation (offline mode).
    use_embeddings:
        Pass True to enable sentence-transformer retrieval.
    """
    llm = None if no_llm else _make_llm()
    graph = build_graph(llm=llm, use_embeddings=use_embeddings)
    initial_state: AgentState = {
        "question": question,
        "iteration": 0,
    }
    final_state: AgentState = graph.invoke(initial_state)
    return final_state
