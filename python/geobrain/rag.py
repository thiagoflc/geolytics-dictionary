"""rag.py — BM25 retrieval over the Geolytics RAG corpus.

Requires the ``rank-bm25`` optional dependency:

    pip install geobrain[rag]
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from .data import load_jsonl


@dataclass(frozen=True)
class RAGDocument:
    """A document from the RAG corpus."""

    id: str
    type: str
    text: str
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


def _norm(s: str) -> str:
    """Lowercase + strip accents for token normalization."""
    nfkd = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _tokenize(text: str) -> list[str]:
    """Simple whitespace tokenizer with normalization."""
    return _norm(text).split()


@dataclass
class SearchResult:
    """A single BM25 search result."""

    document: RAGDocument
    score: float


class BM25Retriever:
    """BM25 retriever over ``ai/rag-corpus.jsonl``.

    Requires ``rank-bm25``:

        pip install geobrain[rag]

    Usage::

        from geobrain.rag import BM25Retriever
        r = BM25Retriever()
        results = r.search("reservatorio carbonatico pre-sal", top_k=5)
        for hit in results:
            print(hit.score, hit.document.id, hit.document.text[:80])
    """

    def __init__(self) -> None:
        try:
            from rank_bm25 import BM25Okapi  # type: ignore[import]
            self._BM25Okapi = BM25Okapi
        except ImportError as exc:
            raise ImportError(
                "rank-bm25 is required for BM25Retriever. "
                "Install it with: pip install geobrain[rag]"
            ) from exc

    @cached_property
    def _documents(self) -> list[RAGDocument]:
        rows = load_jsonl("rag-corpus.jsonl")
        return [
            RAGDocument(
                id=row.get("id", ""),
                type=row.get("type", ""),
                text=row.get("text", ""),
                raw=row,
            )
            for row in rows
        ]

    @cached_property
    def _bm25(self) -> Any:
        tokenized = [_tokenize(doc.text) for doc in self._documents]
        return self._BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """Return up to ``top_k`` documents ranked by BM25 score.

        Args:
            query: Free-text query (Portuguese or English).
            top_k: Maximum number of results to return.

        Returns:
            List of :class:`SearchResult` sorted by descending score.
            Documents with score 0 are excluded.
        """
        tokens = _tokenize(query)
        scores = self._bm25.get_scores(tokens)
        docs = self._documents

        ranked = sorted(
            zip(scores, docs),
            key=lambda x: x[0],
            reverse=True,
        )

        results = []
        for score, doc in ranked[:top_k]:
            if score > 0:
                results.append(SearchResult(document=doc, score=float(score)))
        return results

    def document_count(self) -> int:
        """Return the number of documents in the corpus."""
        return len(self._documents)
