"""
vector_only.py — BM25 retrieval over ai/rag-corpus.jsonl.

Returns the top-k passages concatenated as the answer.
No graph, no validator, no network calls.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Answer:
    text: str
    entities_cited: list[str] = field(default_factory=list)
    validations: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Corpus loading (cached at module level)
# ---------------------------------------------------------------------------

_corpus: list[dict] | None = None
_bm25: BM25Okapi | None = None


def _load_corpus(corpus_path: Path) -> tuple[list[dict], BM25Okapi]:
    global _corpus, _bm25
    if _corpus is not None and _bm25 is not None:
        return _corpus, _bm25

    docs: list[dict] = []
    with corpus_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                docs.append(json.loads(line))

    tokenized = [_tokenize(d["text"]) for d in docs]
    _corpus = docs
    _bm25 = BM25Okapi(tokenized)
    return _corpus, _bm25


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúâêôãõüçàèì\w]+", text.lower())


# ---------------------------------------------------------------------------
# Entity extraction from metadata
# ---------------------------------------------------------------------------

def _extract_entities(docs: list[dict]) -> list[str]:
    seen: set[str] = set()
    entities: list[str] = []
    for doc in docs:
        meta = doc.get("metadata", {})
        eid = meta.get("id") or doc.get("id", "")
        if eid and eid not in seen:
            seen.add(eid)
            entities.append(eid)
    return entities


# ---------------------------------------------------------------------------
# Runner entry point
# ---------------------------------------------------------------------------

def run(question: str, top_k: int = 5, corpus_path: Path | None = None) -> Answer:
    """Return an Answer built from BM25-retrieved passages."""
    if corpus_path is None:
        corpus_path = Path(__file__).resolve().parents[2] / "ai" / "rag-corpus.jsonl"

    corpus, bm25 = _load_corpus(corpus_path)

    tokens = _tokenize(question)
    scores = bm25.get_scores(tokens)

    # Grab top-k indices by score
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    top_docs = [corpus[i] for i in top_indices]

    # Build answer text from retrieved passages
    passages = [doc["text"] for doc in top_docs]
    answer_text = "\n\n".join(passages)

    entities = _extract_entities(top_docs)

    return Answer(text=answer_text, entities_cited=entities, validations=[])
