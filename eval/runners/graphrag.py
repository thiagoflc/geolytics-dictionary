"""
graphrag.py — Graph-augmented retrieval using NetworkX over data/entity-graph.json.

Steps:
  1. BM25 over rag-corpus to find seed entity IDs.
  2. Build a 2-hop neighbourhood in the entity graph.
  3. Synthesize a templated answer mentioning the entities found.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx
from rank_bm25 import BM25Okapi

from .vector_only import Answer, _load_corpus, _tokenize

# ---------------------------------------------------------------------------
# Graph loading (cached at module level)
# ---------------------------------------------------------------------------

_graph: nx.Graph | None = None


def _load_graph(graph_path: Path) -> nx.Graph:
    global _graph
    if _graph is not None:
        return _graph

    with graph_path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    g = nx.Graph()
    for node in data.get("nodes", []):
        g.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for edge in data.get("edges", []):
        g.add_edge(edge["source"], edge["target"],
                   relation=edge.get("relation", ""),
                   relation_label_pt=edge.get("relation_label_pt", ""))

    _graph = g
    return _graph


# ---------------------------------------------------------------------------
# Seed entity identification via BM25 score → node ID matching
# ---------------------------------------------------------------------------

def _find_seed_entities(
    question: str,
    graph: nx.Graph,
    corpus: list[dict],
    bm25: BM25Okapi,
    top_k: int = 5,
) -> list[str]:
    tokens = _tokenize(question)
    scores = bm25.get_scores(tokens)

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    top_docs = [corpus[i] for i in top_indices]

    # Collect entity IDs from corpus metadata, filtered to graph nodes
    seeds: list[str] = []
    seen: set[str] = set()
    for doc in top_docs:
        eid = doc.get("metadata", {}).get("id") or doc.get("id", "")
        if eid and eid in graph and eid not in seen:
            seeds.append(eid)
            seen.add(eid)

    # Fallback: substring-match question tokens against node IDs
    if not seeds:
        q_lower = question.lower()
        for node_id in graph.nodes():
            if node_id.replace("-", " ").replace("_", " ") in q_lower:
                if node_id not in seen:
                    seeds.append(node_id)
                    seen.add(node_id)
                if len(seeds) >= top_k:
                    break

    return seeds[:top_k]


# ---------------------------------------------------------------------------
# 2-hop neighbourhood expansion
# ---------------------------------------------------------------------------

def _two_hop_neighbours(graph: nx.Graph, seeds: list[str]) -> set[str]:
    neighbourhood: set[str] = set(seeds)
    for seed in seeds:
        if seed not in graph:
            continue
        for hop1 in graph.neighbors(seed):
            neighbourhood.add(hop1)
            for hop2 in graph.neighbors(hop1):
                neighbourhood.add(hop2)
    return neighbourhood


# ---------------------------------------------------------------------------
# Answer synthesis
# ---------------------------------------------------------------------------

def _synthesize(
    question: str,
    seeds: list[str],
    neighbours: set[str],
    graph: nx.Graph,
) -> str:
    if not seeds:
        return f"Nenhuma entidade relevante encontrada para: {question}"

    lines: list[str] = []
    lines.append(f"Entidades identificadas para a pergunta: {question}")
    lines.append("")

    for seed in seeds:
        if seed not in graph:
            continue
        attrs = graph.nodes[seed]
        label = attrs.get("label") or seed
        label_en = attrs.get("label_en", "")
        definition = attrs.get("definition", "")
        label_str = f"{label} ({label_en})" if label_en else label
        lines.append(f"- {label_str}: {definition[:200]}")

    related = neighbours - set(seeds)
    if related:
        related_labels = []
        for nid in sorted(related)[:8]:
            if nid in graph:
                attrs = graph.nodes[nid]
                related_labels.append(attrs.get("label") or nid)
        lines.append("")
        lines.append(f"Conceitos relacionados: {', '.join(related_labels)}.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Runner entry point
# ---------------------------------------------------------------------------

def run(
    question: str,
    top_k: int = 5,
    corpus_path: Path | None = None,
    graph_path: Path | None = None,
) -> Answer:
    """Return an Answer built from graph-augmented retrieval."""
    root = Path(__file__).resolve().parents[2]
    if corpus_path is None:
        corpus_path = root / "ai" / "rag-corpus.jsonl"
    if graph_path is None:
        graph_path = root / "data" / "entity-graph.json"

    corpus, bm25 = _load_corpus(corpus_path)
    graph = _load_graph(graph_path)

    seeds = _find_seed_entities(question, graph, corpus, bm25, top_k)
    neighbours = _two_hop_neighbours(graph, seeds)
    text = _synthesize(question, seeds, neighbours, graph)

    return Answer(text=text, entities_cited=sorted(neighbours), validations=[])
