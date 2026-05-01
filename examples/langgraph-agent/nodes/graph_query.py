"""GraphQuery node — executes queries against the in-memory NetworkX graph.

Data source: data/entity-graph.json (loaded once via data_loader).

Neo4j stub
----------
To swap in a real Neo4j instance, uncomment the block marked NEO4J and
set the environment variables NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD.
The stub shows a Bolt connection pattern; the NetworkX path runs standalone.

# NEO4J STUB (commented) ------------------------------------------------
# from neo4j import GraphDatabase
#
# _NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
# _NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
# _NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "")
#
# def _neo4j_query(cypher: str, params: dict) -> list[dict]:
#     driver = GraphDatabase.driver(_NEO4J_URI, auth=(_NEO4J_USER, _NEO4J_PASS))
#     with driver.session() as session:
#         result = session.run(cypher, **params)
#         return [dict(record) for record in result]
# -------------------------------------------------------------------------
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

import networkx as nx

from data_loader import load_entity_graph
from state import AgentState


@lru_cache(maxsize=1)
def _build_graph() -> nx.DiGraph:
    """Build and cache the NetworkX directed graph from entity-graph.json."""
    raw = load_entity_graph()
    g: nx.DiGraph = nx.DiGraph()

    for node in raw["nodes"]:
        g.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            label_en=node.get("label_en", ""),
            definition=node.get("definition", ""),
            definition_en=node.get("definition_en_canonical", ""),
            type=node.get("type", ""),
            synonyms_pt=node.get("synonyms_pt", []),
            synonyms_en=node.get("synonyms_en", []),
            examples=node.get("examples", []),
            geocoverage=node.get("geocoverage", []),
        )

    for edge in raw["edges"]:
        g.add_edge(
            edge["source"],
            edge["target"],
            relation=edge.get("relation", ""),
            relation_label_pt=edge.get("relation_label_pt", ""),
            relation_label_en=edge.get("relation_label_en", ""),
        )

    return g


def _find_node_by_text(g: nx.DiGraph, text: str) -> str | None:
    """Return the node id whose label or synonyms best match `text`.

    Case-insensitive substring matching; returns None if nothing found.
    """
    text_lower = text.lower()
    # Exact id match
    if text_lower in g:
        return text_lower
    # Label match
    for node_id, attrs in g.nodes(data=True):
        label = attrs.get("label", "").lower()
        label_en = attrs.get("label_en", "").lower()
        if text_lower in label or text_lower in label_en:
            return node_id
    # Synonym match
    for node_id, attrs in g.nodes(data=True):
        for syn in attrs.get("synonyms_pt", []) + attrs.get("synonyms_en", []):
            if text_lower in syn.lower():
                return node_id
    return None


def _node_to_dict(g: nx.DiGraph, node_id: str) -> dict[str, Any]:
    attrs = dict(g.nodes[node_id])
    return {"id": node_id, **attrs}


def _neighbours(g: nx.DiGraph, node_id: str) -> list[dict[str, Any]]:
    """Return all edges (in + out) for a node."""
    results: list[dict[str, Any]] = []
    for src, tgt, edge_data in g.out_edges(node_id, data=True):
        results.append(
            {
                "direction": "out",
                "from": src,
                "to": tgt,
                **edge_data,
            }
        )
    for src, tgt, edge_data in g.in_edges(node_id, data=True):
        results.append(
            {
                "direction": "in",
                "from": src,
                "to": tgt,
                **edge_data,
            }
        )
    return results


def _query_one(g: nx.DiGraph, sub_query: str) -> list[dict[str, Any]]:
    """Execute a single sub-query against the graph."""
    node_id = _find_node_by_text(g, sub_query)
    if node_id is None:
        return [{"query": sub_query, "found": False, "results": []}]

    node_data = _node_to_dict(g, node_id)
    neighbours = _neighbours(g, node_id)
    return [
        {
            "query": sub_query,
            "found": True,
            "node": node_data,
            "neighbours": neighbours,
        }
    ]


def graph_query_node(state: AgentState) -> AgentState:
    """Execute graph queries for all sub-queries and store results in state."""
    g = _build_graph()
    sub_queries = state.get("decomposed") or [state["question"]]

    all_results: list[dict[str, Any]] = []
    for sub_query in sub_queries:
        all_results.extend(_query_one(g, sub_query))

    return {**state, "graph_results": all_results}
