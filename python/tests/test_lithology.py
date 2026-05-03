"""Tests for python/geobrain/lithology.py."""
import pytest
from geobrain.lithology import LithologyConcept, LithologyDictionary, LithologyMapping


@pytest.fixture(scope="module")
def ld():
    return LithologyDictionary()


class TestLithologyDictionaryLoad:
    def test_loads_437_concepts(self, ld):
        assert len(ld) == 437

    def test_all_concepts_have_id_and_label(self, ld):
        for c in ld.all_concepts():
            assert c.id, f"Concept missing id: {c}"
            assert c.label_en, f"Concept {c.id} missing label_en"

    def test_pt_labels_present(self, ld):
        with_pt = [c for c in ld.all_concepts() if c.label_pt]
        assert len(with_pt) >= 1, "Expected at least 1 PT label"

    def test_all_concepts_returns_list_of_lithology_concepts(self, ld):
        concepts = ld.all_concepts()
        assert len(concepts) == 437
        assert all(isinstance(c, LithologyConcept) for c in concepts)


class TestLithologyLookup:
    def test_lookup_limestone_en(self, ld):
        results = ld.lookup("limestone")
        assert any(c.id == "limestone" for c in results)

    def test_lookup_calcario_pt(self, ld):
        results = ld.lookup("calcário")
        assert any(c.label_pt == "calcário" for c in results)

    def test_lookup_case_insensitive(self, ld):
        r1 = ld.lookup("Limestone")
        r2 = ld.lookup("limestone")
        assert len(r1) == len(r2)

    def test_lookup_empty_returns_empty(self, ld):
        results = ld.lookup("xyzzy_nonexistent_9999")
        assert results == []

    def test_lookup_sandstone_returns_results(self, ld):
        results = ld.lookup("sandstone")
        assert len(results) >= 1

    def test_lookup_returns_lithology_concept_objects(self, ld):
        results = ld.lookup("limestone")
        assert all(isinstance(c, LithologyConcept) for c in results)


class TestLithologyById:
    def test_by_id_limestone(self, ld):
        c = ld.by_id("limestone")
        assert c is not None
        assert c.label_en == "limestone"
        assert c.label_pt == "calcário"

    def test_by_id_nonexistent_returns_none(self, ld):
        assert ld.by_id("nonexistent_xyz") is None

    def test_by_id_igneous_material(self, ld):
        c = ld.by_id("igneous_material")
        assert c is not None

    def test_by_id_shale(self, ld):
        c = ld.by_id("shale")
        assert c is not None
        assert c.label_en == "shale"


class TestLithologyHierarchy:
    def test_roots_not_empty(self, ld):
        roots = ld.roots()
        assert len(roots) >= 1

    def test_root_concepts_have_no_parents(self, ld):
        for root in ld.roots():
            assert root.is_root is True
            assert len(root.parents) == 0

    def test_children_returns_list(self, ld):
        children = ld.children("rock_material")
        assert isinstance(children, list)


class TestOsduMapping:
    def test_limestone_maps_to_osdu(self, ld):
        m = ld.osdu_mapping("limestone")
        assert m is not None
        assert m.osdu_value == "Limestone"
        assert m.match_kind == "exactMatch"

    def test_nonexistent_returns_none(self, ld):
        assert ld.osdu_mapping("nonexistent_xyz") is None

    def test_mapping_returns_lithology_mapping_object(self, ld):
        m = ld.osdu_mapping("limestone")
        assert isinstance(m, LithologyMapping)

    def test_mappings_have_match_kind(self, ld):
        known = ["limestone", "shale"]
        for cgi_id in known:
            m = ld.osdu_mapping(cgi_id)
            if m:
                assert m.match_kind in {"exactMatch", "broadMatch", "closeMatch", "narrowMatch"}

    def test_shale_maps_to_osdu(self, ld):
        m = ld.osdu_mapping("shale")
        assert m is not None
        assert m.osdu_value == "Shale"
