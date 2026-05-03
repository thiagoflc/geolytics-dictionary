"""Tests for python/geobrain/crosswalk.py."""
import pytest
from geobrain.crosswalk import CrosswalkIndex, CrosswalkEntry


@pytest.fixture(scope="module")
def cx():
    return CrosswalkIndex()


class TestCrosswalkLoad:
    def test_loads_all_entries(self, cx):
        entries = cx.all_entries()
        assert len(entries) >= 30, f"Expected >=30 total entries, got {len(entries)}"

    def test_witsml_entries_present(self, cx):
        witsml = [e for e in cx.all_entries() if e.standard == "witsml"]
        assert len(witsml) >= 20, f"Expected >=20 WITSML entries, got {len(witsml)}"

    def test_prodml_entries_present(self, cx):
        prodml = [e for e in cx.all_entries() if e.standard == "prodml"]
        assert len(prodml) >= 10, f"Expected >=10 ProdML entries, got {len(prodml)}"

    def test_all_entries_returns_crosswalk_entry_objects(self, cx):
        entries = cx.all_entries()
        assert all(isinstance(e, CrosswalkEntry) for e in entries)


class TestCrosswalkEntryFields:
    def test_entries_have_required_fields(self, cx):
        for entry in cx.all_entries()[:5]:
            assert entry.source_class, f"Entry missing source_class: {entry}"
            assert entry.rdf_class, f"Entry missing rdf_class: {entry}"
            assert entry.standard in {"witsml", "prodml"}, f"Unexpected standard: {entry.standard}"

    def test_witsml_entries_have_standard_set(self, cx):
        witsml_entries = [e for e in cx.all_entries() if e.standard == "witsml"]
        assert all(e.standard == "witsml" for e in witsml_entries)

    def test_entries_have_rdf_uri(self, cx):
        entries = cx.all_entries()
        assert any(e.rdf_uri for e in entries)


class TestCrosswalkLookup:
    def test_lookup_by_class_well(self, cx):
        results = cx.lookup_by_class("Well")
        assert len(results) >= 1
        assert all("well" in e.source_class.lower() for e in results)

    def test_lookup_by_class_case_insensitive(self, cx):
        results = cx.lookup_by_class("well")
        assert len(results) >= 1

    def test_lookup_by_layer(self, cx):
        results = cx.lookup_by_layer("layer4")
        assert len(results) >= 1
        assert all(e.layer == "layer4" for e in results)

    def test_lookup_by_osdu_kind_well(self, cx):
        results = cx.lookup_by_osdu_kind("opendes:osdu:master-data--Well:1.0.0")
        assert len(results) >= 1

    def test_lookup_by_class_nonexistent_returns_empty(self, cx):
        results = cx.lookup_by_class("zzz_nonexistent_class_xyz")
        assert results == []
