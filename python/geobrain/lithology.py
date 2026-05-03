"""lithology.py — CGI Simple Lithology vocabulary access (layer1b)."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from .data import load_json


@dataclass(frozen=True)
class LithologyConcept:
    """A single CGI Simple Lithology concept."""
    id: str
    label_en: str
    label_pt: str | None
    definition: str | None
    parents: list[str]
    uri: str | None
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    @property
    def is_root(self) -> bool:
        """True if this concept has no parents (top of hierarchy)."""
        return len(self.parents) == 0


@dataclass(frozen=True)
class LithologyMapping:
    """A CGI ↔ OSDU LithologyType mapping entry."""
    cgi_id: str
    cgi_label: str
    osdu_value: str
    match_kind: str  # exactMatch, broadMatch, closeMatch, narrowMatch
    notes: str = ""


class LithologyDictionary:
    """Access the 437-concept CGI Simple Lithology vocabulary with PT-BR labels.

    Examples:
        >>> ld = LithologyDictionary()
        >>> ld.lookup("limestone")
        [LithologyConcept(id='limestone', label_en='limestone', label_pt='calcário', ...)]
        >>> ld.osdu_mapping("limestone")
        LithologyMapping(cgi_id='limestone', osdu_value='Limestone', match_kind='exactMatch')
        >>> ld.children("sedimentary_material")
        [LithologyConcept(...), ...]
    """

    @cached_property
    def _concepts(self) -> list[LithologyConcept]:
        raw = load_json("cgi-lithology.json")
        # cgi-lithology.json may be a dict with a 'concepts' key or a plain array
        if isinstance(raw, dict):
            items_raw = raw.get("concepts", [])
        else:
            items_raw = raw
        items = [x for x in items_raw if isinstance(x, dict) and "id" in x and isinstance(x.get("id"), str)]
        return [
            LithologyConcept(
                id=x["id"],
                label_en=x.get("label_en", x["id"]),
                label_pt=x.get("label_pt"),
                definition=x.get("definition_en"),
                parents=x.get("parents", []),
                uri=x.get("uri"),
                raw=x,
            )
            for x in items
        ]

    @cached_property
    def _osdu_map(self) -> dict[str, LithologyMapping]:
        raw = load_json("cgi-osdu-lithology-map.json")
        # file may be a dict with a 'mappings' key or a plain array
        if isinstance(raw, dict):
            entries = raw.get("mappings", [])
        else:
            entries = raw
        result = {}
        for entry in entries:
            if isinstance(entry, dict) and "cgi_id" in entry:
                cgi_id = entry["cgi_id"]
                result[cgi_id] = LithologyMapping(
                    cgi_id=cgi_id,
                    cgi_label=entry.get("cgi_label_en", entry.get("cgi_label", cgi_id)),
                    osdu_value=entry.get("osdu_value", ""),
                    match_kind=entry.get("match_kind", "closeMatch"),
                    notes=entry.get("note", entry.get("notes", "")) or "",
                )
        return result

    def __len__(self) -> int:
        return len(self._concepts)

    def lookup(self, query: str, lang: str = "both") -> list[LithologyConcept]:
        """Search concepts by label or id.

        Args:
            query: Search string (case-insensitive substring match).
            lang: 'en', 'pt', or 'both' (default).

        Returns:
            List of matching LithologyConcept objects.
        """
        q = query.lower()
        results = []
        for c in self._concepts:
            if c.id.lower() == q or c.id.lower().replace("_", " ") == q:
                results.insert(0, c)  # exact ID match first
            elif (lang in ("en", "both") and q in c.label_en.lower()) or \
                 (lang in ("pt", "both") and c.label_pt and q in c.label_pt.lower()):
                results.append(c)
        return results

    def by_id(self, concept_id: str) -> LithologyConcept | None:
        """Get a concept by its exact CGI id."""
        for c in self._concepts:
            if c.id == concept_id:
                return c
        return None

    def children(self, parent_id: str) -> list[LithologyConcept]:
        """Return all direct children of a parent concept."""
        return [c for c in self._concepts if parent_id in c.parents]

    def osdu_mapping(self, cgi_id: str) -> LithologyMapping | None:
        """Get the OSDU LithologyType mapping for a CGI concept id."""
        return self._osdu_map.get(cgi_id)

    def all_concepts(self) -> list[LithologyConcept]:
        """Return all 437 concepts."""
        return list(self._concepts)

    def roots(self) -> list[LithologyConcept]:
        """Return top-level (root) concepts."""
        return [c for c in self._concepts if c.is_root]
