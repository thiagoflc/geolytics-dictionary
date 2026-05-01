"""crosswalk.py — cross-layer URI lookup (WITSML, ProdML, OSDU crosswalks)."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from .data import load_json


@dataclass(frozen=True)
class CrosswalkEntry:
    """A single row in a crosswalk table."""

    source_class: str
    source_uri: str
    rdf_class: str
    rdf_uri: str
    layer: str
    osdu_kind: str | None
    standard: str  # e.g. "witsml", "prodml"
    description_pt: str
    description_en: str
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


def _entry_from_dict(d: dict[str, Any], standard: str) -> CrosswalkEntry:
    # WITSML uses *_class; ProdML uses same pattern
    return CrosswalkEntry(
        source_class=d.get("witsml_class", d.get("prodml_class", d.get("source_class", ""))),
        source_uri=d.get("witsml_uri", d.get("prodml_uri", d.get("source_uri", ""))),
        rdf_class=d.get("rdf_class", ""),
        rdf_uri=d.get("rdf_uri", ""),
        layer=d.get("layer", ""),
        osdu_kind=d.get("osdu_kind"),
        standard=standard,
        description_pt=d.get("description_pt", ""),
        description_en=d.get("description_en", ""),
        raw=d,
    )


class CrosswalkIndex:
    """In-memory index over the WITSML and ProdML RDF crosswalk files.

    Usage::

        from geolytics_dictionary import CrosswalkIndex
        cx = CrosswalkIndex()
        entries = cx.lookup_by_osdu_kind("opendes:osdu:master-data--Well:1.0.0")
        entries = cx.lookup_by_class("Well")
    """

    def __init__(self) -> None:
        self._witsml_data: list[dict[str, Any]] = []
        self._prodml_data: list[dict[str, Any]] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        try:
            witsml = load_json("witsml-rdf-crosswalk.json")
            self._witsml_data = witsml.get("classes", [])
        except FileNotFoundError:
            pass
        try:
            prodml = load_json("prodml-rdf-crosswalk.json")
            self._prodml_data = prodml.get("classes", [])
        except FileNotFoundError:
            pass
        self._loaded = True

    @cached_property
    def _all_entries(self) -> list[CrosswalkEntry]:
        self._ensure_loaded()
        entries = [
            _entry_from_dict(d, "witsml") for d in self._witsml_data
        ] + [
            _entry_from_dict(d, "prodml") for d in self._prodml_data
        ]
        return entries

    def all_entries(self) -> list[CrosswalkEntry]:
        """Return all crosswalk entries."""
        return list(self._all_entries)

    def lookup_by_class(self, class_name: str) -> list[CrosswalkEntry]:
        """Find entries by source class name (case-insensitive partial match)."""
        lower = class_name.lower()
        return [e for e in self._all_entries if lower in e.source_class.lower()]

    def lookup_by_osdu_kind(self, osdu_kind: str) -> list[CrosswalkEntry]:
        """Find entries by OSDU kind string (exact match)."""
        return [e for e in self._all_entries if e.osdu_kind == osdu_kind]

    def lookup_by_rdf_uri(self, rdf_uri: str) -> list[CrosswalkEntry]:
        """Find entries by RDF URI (exact match)."""
        return [e for e in self._all_entries if e.rdf_uri == rdf_uri]

    def lookup_by_layer(self, layer: str) -> list[CrosswalkEntry]:
        """Return all entries that belong to a given ontology layer."""
        return [e for e in self._all_entries if e.layer == layer]
