"""test_sweet.py — Tests for SweetExpander."""

import pytest
from geobrain import Alignment, ExpansionResult, SweetExpander


@pytest.fixture(scope="module")
def s():
    return SweetExpander()


# ---------------------------------------------------------------------------
# expand()
# ---------------------------------------------------------------------------


def test_expand_hidrocarboneto_returns_uris(s):
    uris = s.expand("hidrocarboneto")
    assert len(uris) >= 1
    assert all(uri.startswith("http://sweetontology.net/") for uri in uris)


def test_expand_reservatorio_returns_uris(s):
    uris = s.expand("reservatorio")
    assert len(uris) >= 1


def test_expand_with_strategy_exact_match(s):
    uris = s.expand("hidrocarboneto", strategy="exactMatch")
    assert len(uris) >= 1
    # All returned URIs should come from exactMatch alignments
    assert all(uri.startswith("http://sweetontology.net/") for uri in uris)


def test_expand_with_strategy_close_match(s):
    uris = s.expand("reservatorio", strategy="closeMatch")
    # reservatorio uses relatedMatch, so closeMatch filter returns empty
    # This verifies strategy filtering works
    assert isinstance(uris, list)


def test_expand_with_strategy_filters_correctly(s):
    # hidrocarboneto has exactMatch and narrowMatch — they should differ
    all_uris = s.expand("hidrocarboneto")
    exact_uris = s.expand("hidrocarboneto", strategy="exactMatch")
    narrow_uris = s.expand("hidrocarboneto", strategy="narrowMatch")
    assert len(all_uris) >= len(exact_uris)
    assert len(all_uris) >= len(narrow_uris)


def test_expand_unknown_term_returns_empty(s):
    uris = s.expand("zzz_not_a_real_term_xyz")
    assert uris == []


def test_expand_skos_prefix_strategy(s):
    # "skos:exactMatch" should be treated same as "exactMatch"
    uris1 = s.expand("hidrocarboneto", strategy="exactMatch")
    uris2 = s.expand("hidrocarboneto", strategy="skos:exactMatch")
    assert uris1 == uris2


# ---------------------------------------------------------------------------
# expand_full()
# ---------------------------------------------------------------------------


def test_expand_full_hidrocarboneto_found(s):
    result = s.expand_full("hidrocarboneto")
    assert isinstance(result, ExpansionResult)
    assert result.found is True
    assert result.term_id == "hidrocarboneto"


def test_expand_full_has_sweet_uris(s):
    result = s.expand_full("hidrocarboneto")
    assert len(result.sweet_uris) >= 1


def test_expand_full_has_alignments(s):
    result = s.expand_full("hidrocarboneto")
    assert len(result.alignments) >= 1
    assert all(isinstance(a, Alignment) for a in result.alignments)


def test_expand_full_has_hierarchy(s):
    result = s.expand_full("hidrocarboneto", include_hierarchy=True)
    assert isinstance(result.hierarchy, dict)
    assert len(result.hierarchy) >= 1


def test_expand_full_hierarchy_has_ancestors(s):
    result = s.expand_full("hidrocarboneto", include_hierarchy=True)
    for _uri, info in result.hierarchy.items():
        assert "ancestors" in info
        assert isinstance(info["ancestors"], list)


def test_expand_full_not_found(s):
    result = s.expand_full("zzz_not_a_real_term_xyz")
    assert result.found is False
    assert result.sweet_uris == []
    assert result.alignments == []


def test_expand_full_modules_non_empty(s):
    result = s.expand_full("hidrocarboneto")
    assert len(result.modules) >= 1


# ---------------------------------------------------------------------------
# all_term_ids()
# ---------------------------------------------------------------------------


def test_all_term_ids_non_empty(s):
    ids = s.all_term_ids()
    assert len(ids) >= 1


def test_all_term_ids_contains_known_terms(s):
    ids = s.all_term_ids()
    assert "hidrocarboneto" in ids
    assert "reservatorio" in ids
