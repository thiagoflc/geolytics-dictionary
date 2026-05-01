"""test_dictionary.py — Tests for the Dictionary class."""

import pytest

from geolytics_dictionary import Dictionary, Term, Acronym, Layer


@pytest.fixture(scope="module")
def d():
    return Dictionary()


# ---------------------------------------------------------------------------
# lookup()
# ---------------------------------------------------------------------------

def test_lookup_presal_returns_results(d):
    results = d.lookup("Pré-sal")
    assert len(results) >= 1, "Expected at least 1 result for 'Pré-sal'"


def test_lookup_presal_returns_terms(d):
    results = d.lookup("Pré-sal")
    assert all(isinstance(t, Term) for t in results)


def test_lookup_case_insensitive(d):
    lower = d.lookup("pré-sal")
    upper = d.lookup("PRÉ-SAL")
    assert len(lower) >= 1
    assert len(upper) >= 1


def test_lookup_accent_insensitive(d):
    # "Pre-sal" without accent should still match "Pré-sal"
    results = d.lookup("Pre-sal")
    assert len(results) >= 1


def test_lookup_unknown_returns_empty(d):
    results = d.lookup("zzz_this_term_does_not_exist_xyz")
    assert results == []


def test_lookup_partial_match(d):
    # "reservatorio" should match reservoir-related terms
    results = d.lookup("reservatorio")
    assert len(results) >= 1


# ---------------------------------------------------------------------------
# acronym()
# ---------------------------------------------------------------------------

def test_acronym_bop_returns_results(d):
    results = d.acronym("BOP")
    assert len(results) >= 1, "Expected at least 1 sense for 'BOP'"


def test_acronym_bop_returns_acronym_objects(d):
    results = d.acronym("BOP")
    assert all(isinstance(a, Acronym) for a in results)


def test_acronym_bop_has_expansion(d):
    results = d.acronym("BOP")
    assert any(a.expansion_pt for a in results)


def test_acronym_case_insensitive(d):
    upper = d.acronym("BOP")
    lower = d.acronym("bop")
    assert len(upper) == len(lower)


def test_acronym_unknown_returns_empty(d):
    results = d.acronym("ZZZNOTEXIST")
    assert results == []


# ---------------------------------------------------------------------------
# layers()
# ---------------------------------------------------------------------------

def test_layers_returns_at_least_seven(d):
    layers = d.layers()
    assert len(layers) >= 7, f"Expected >=7 layers, got {len(layers)}"


def test_layers_returns_layer_objects(d):
    layers = d.layers()
    assert all(isinstance(layer, Layer) for layer in layers)


def test_layers_have_ids(d):
    layers = d.layers()
    assert all(layer.id for layer in layers)


def test_layers_have_names(d):
    layers = d.layers()
    assert all(layer.name for layer in layers)


# ---------------------------------------------------------------------------
# meta()
# ---------------------------------------------------------------------------

def test_meta_returns_dict(d):
    meta = d.meta()
    assert isinstance(meta, dict)


# ---------------------------------------------------------------------------
# all_terms() / all_acronyms()
# ---------------------------------------------------------------------------

def test_all_terms_non_empty(d):
    terms = d.all_terms()
    assert len(terms) > 0


def test_all_acronyms_non_empty(d):
    acronyms = d.all_acronyms()
    assert len(acronyms) > 0
