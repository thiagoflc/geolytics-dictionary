"""test_rag.py — Tests for the rag module (RAGDocument, SearchResult, BM25Retriever)."""

import pytest
from geobrain.rag import RAGDocument, SearchResult, _norm, _tokenize

# ---------------------------------------------------------------------------
# _norm and _tokenize helpers
# ---------------------------------------------------------------------------


def test_norm_lowercases():
    assert _norm("Pré-sal") == "pre-sal"


def test_norm_strips_accents():
    assert _norm("reservatório") == "reservatorio"


def test_norm_handles_plain_ascii():
    assert _norm("BOP") == "bop"


def test_tokenize_splits_on_whitespace():
    tokens = _tokenize("carbonato evaporito")
    assert tokens == ["carbonato", "evaporito"]


def test_tokenize_normalizes_accents():
    tokens = _tokenize("Pré-sal reservatório")
    assert "pre-sal" in tokens
    assert "reservatorio" in tokens


# ---------------------------------------------------------------------------
# RAGDocument dataclass
# ---------------------------------------------------------------------------


def test_ragdocument_fields():
    doc = RAGDocument(id="d1", type="term", text="Pré-sal definition")
    assert doc.id == "d1"
    assert doc.type == "term"
    assert doc.text == "Pré-sal definition"
    assert doc.raw == {}


def test_ragdocument_frozen():
    doc = RAGDocument(id="d1", type="term", text="some text")
    with pytest.raises((AttributeError, TypeError)):
        doc.id = "changed"  # type: ignore[misc]


def test_ragdocument_raw_not_compared():
    doc_a = RAGDocument(id="x", type="t", text="t", raw={"extra": 1})
    doc_b = RAGDocument(id="x", type="t", text="t", raw={})
    assert doc_a == doc_b


# ---------------------------------------------------------------------------
# BM25Retriever (requires rank-bm25)
# ---------------------------------------------------------------------------

rank_bm25 = pytest.importorskip("rank_bm25", reason="rank-bm25 not installed")


@pytest.fixture(scope="module")
def retriever():
    from geobrain.rag import BM25Retriever

    return BM25Retriever()


def test_retriever_document_count_positive(retriever):
    assert retriever.document_count() > 0


def test_retriever_documents_are_ragdocuments(retriever):
    # Access internal cached property for structural checks
    docs = retriever._documents
    assert all(isinstance(d, RAGDocument) for d in docs)


def test_retriever_documents_have_nonempty_ids(retriever):
    docs = retriever._documents
    assert all(d.id for d in docs)


def test_retriever_documents_have_nonempty_text(retriever):
    # CGI vocabulary entries (lithology, geologic_time, etc.) may have null definition
    _CGI_TYPES = {
        "lithology",
        "geologic_time",
        "stratigraphic_rank",
        "fault_type",
        "deformation_style",
        "contact_type",
    }
    docs = [d for d in retriever._documents if getattr(d, "type", None) not in _CGI_TYPES]
    assert all(d.text for d in docs)


def test_search_returns_list(retriever):
    results = retriever.search("reservatorio carbonatico")
    assert isinstance(results, list)


def test_search_returns_search_result_objects(retriever):
    results = retriever.search("reservatorio carbonatico")
    assert all(isinstance(r, SearchResult) for r in results)


def test_search_results_have_positive_scores(retriever):
    results = retriever.search("reservatorio carbonatico")
    assert all(r.score > 0 for r in results)


def test_search_results_sorted_descending(retriever):
    results = retriever.search("poco poco producao")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_top_k_limits_results(retriever):
    results = retriever.search("poco", top_k=3)
    assert len(results) <= 3


def test_search_empty_query_returns_list(retriever):
    results = retriever.search("")
    # An empty query produces no token scores — result must be a list (possibly empty)
    assert isinstance(results, list)


def test_search_unknown_term_returns_empty_or_low_results(retriever):
    results = retriever.search("zzz_nonexistent_xyzxyz_qqqq")
    # Should return an empty list since no tokens match
    assert results == []
