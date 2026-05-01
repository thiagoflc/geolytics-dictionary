"""RAGRetrieve node — retrieves relevant chunks from ai/rag-corpus.jsonl.

Two retrieval backends are supported:
  BM25 (default, always available) — uses rank_bm25; no model downloads required.
  Embeddings (optional)            — uses sentence-transformers + cosine similarity.
                                     Enabled when USE_EMBEDDINGS=1 env var is set
                                     and sentence-transformers is installed.

The node writes `rag_results` (list of chunk dicts, each with a `score` field)
into the agent state.
"""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from typing import Any

from data_loader import load_rag_corpus
from state import AgentState

_TOP_K = 5


# ---------------------------------------------------------------------------
# BM25 backend
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer (language-agnostic)."""
    return re.findall(r"\w+", text.lower())


@lru_cache(maxsize=1)
def _build_bm25():  # type: ignore[return]
    """Build and cache the BM25 index over the RAG corpus."""
    from rank_bm25 import BM25Okapi  # type: ignore[import]

    corpus = load_rag_corpus()
    tokenized = [_tokenize(chunk["text"]) for chunk in corpus]
    return BM25Okapi(tokenized), corpus


def _bm25_retrieve(query: str, top_k: int = _TOP_K) -> list[dict[str, Any]]:
    bm25, corpus = _build_bm25()
    scores: list[float] = bm25.get_scores(_tokenize(query)).tolist()
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for idx, score in ranked:
        if score > 0:
            chunk = dict(corpus[idx])
            chunk["score"] = round(score, 4)
            chunk["retrieval_method"] = "bm25"
            results.append(chunk)
    return results


# ---------------------------------------------------------------------------
# Embeddings backend (optional)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _build_embeddings():  # type: ignore[return]
    """Build and cache sentence-transformer embeddings for the corpus."""
    from sentence_transformers import SentenceTransformer  # type: ignore[import]
    import numpy as np  # type: ignore[import]

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    corpus = load_rag_corpus()
    texts = [chunk["text"] for chunk in corpus]
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return model, corpus, embeddings


def _cosine(a: Any, b: Any) -> float:
    import numpy as np  # type: ignore[import]

    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _embed_retrieve(query: str, top_k: int = _TOP_K) -> list[dict[str, Any]]:
    import numpy as np  # type: ignore[import]

    model, corpus, embeddings = _build_embeddings()
    query_vec = model.encode([query], show_progress_bar=False, convert_to_numpy=True)[0]
    scores = [_cosine(query_vec, emb) for emb in embeddings]
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for idx, score in ranked:
        chunk = dict(corpus[idx])
        chunk["score"] = round(score, 4)
        chunk["retrieval_method"] = "embeddings"
        results.append(chunk)
    return results


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def rag_retrieve_node(state: AgentState, use_embeddings: bool = False) -> AgentState:
    """Retrieve the most relevant corpus chunks for the question.

    Uses embeddings when `use_embeddings=True` AND sentence-transformers is
    installed; otherwise falls back to BM25.
    """
    question = state["question"]

    if use_embeddings:
        try:
            results = _embed_retrieve(question)
        except ImportError:
            results = _bm25_retrieve(question)
    else:
        results = _bm25_retrieve(question)

    return {**state, "rag_results": results}
