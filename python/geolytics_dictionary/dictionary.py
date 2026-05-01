"""dictionary.py — Dictionary class: terms, acronyms, and layers."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from .data import load_json


@dataclass(frozen=True)
class Term:
    """A glossary or extended term entry."""

    id: str
    termo: str
    termo_en: str
    categoria: str
    definicao: str
    fonte: str | None = None
    legal_source: str | None = None
    apareceEm: list[str] = field(default_factory=list)
    geocoverage: list[str] = field(default_factory=list)
    synonyms_pt: list[str] = field(default_factory=list)
    synonyms_en: list[str] = field(default_factory=list)
    osdu_kind: str | None = None
    petrokgraph_uri: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


@dataclass(frozen=True)
class Acronym:
    """An acronym/abbreviation entry."""

    id: str
    sigla: str
    expansion_pt: str
    expansion_en: str
    category: str
    it_generic: bool = False
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


@dataclass(frozen=True)
class Layer:
    """An ontology layer in the knowledge graph."""

    id: str
    name: str
    maintainer: str
    type: str
    description: str
    concepts_count: int
    language: str
    owl_url: str | None = None
    github: str | None = None
    geolytics_coverage: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


def _norm(s: str) -> str:
    """Normalize a string for fuzzy matching: lowercase, strip accents."""
    nfkd = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _term_from_dict(d: dict[str, Any]) -> Term:
    return Term(
        id=d.get("id", ""),
        termo=d.get("termo", d.get("id", "")),
        termo_en=d.get("termo_en", ""),
        categoria=d.get("categoria", ""),
        definicao=d.get("definicao", ""),
        fonte=d.get("fonte"),
        legal_source=d.get("legal_source"),
        apareceEm=d.get("apareceEm", []),
        geocoverage=d.get("geocoverage", []),
        synonyms_pt=d.get("synonyms_pt", []),
        synonyms_en=d.get("synonyms_en", []),
        osdu_kind=d.get("osdu_kind"),
        petrokgraph_uri=d.get("petrokgraph_uri"),
        raw=d,
    )


def _acronym_from_dict(d: dict[str, Any]) -> Acronym:
    return Acronym(
        id=d.get("id", d.get("sigla", "").lower()),
        sigla=d.get("sigla", ""),
        expansion_pt=d.get("expansion_pt", ""),
        expansion_en=d.get("expansion_en", ""),
        category=d.get("category", ""),
        it_generic=d.get("it_generic", False),
        raw=d,
    )


def _layer_from_dict(d: dict[str, Any]) -> Layer:
    return Layer(
        id=d.get("id", ""),
        name=d.get("name", ""),
        maintainer=d.get("maintainer", ""),
        type=d.get("type", ""),
        description=d.get("description", ""),
        concepts_count=d.get("concepts_count", 0),
        language=d.get("language", ""),
        owl_url=d.get("owl_url"),
        github=d.get("github"),
        geolytics_coverage=d.get("geolytics_coverage", []),
        raw=d,
    )


class Dictionary:
    """High-level access to the Geolytics Dictionary data.

    Loads bundled data once on construction. All lookups are case-insensitive
    and accent-insensitive.

    Example::

        d = Dictionary()
        d.lookup("Pré-sal")          # list[Term]
        d.acronym("BOP")             # list[Acronym]
        d.layers()                   # list[Layer]
    """

    def __init__(self) -> None:
        self._full: dict[str, Any] = load_json("full.json")

    @cached_property
    def _terms(self) -> list[Term]:
        glossary = [_term_from_dict(t) for t in self._full.get("glossary", [])]
        extended = [_term_from_dict(t) for t in self._full.get("extended_terms", [])]
        return glossary + extended

    @cached_property
    def _acronyms(self) -> list[Acronym]:
        return [_acronym_from_dict(a) for a in self._full.get("acronyms", [])]

    @cached_property
    def _layers(self) -> list[Layer]:
        layers_data = self._full.get("ontology_map", {}).get("layers", [])
        return [_layer_from_dict(layer) for layer in layers_data]

    def lookup(self, query: str) -> list[Term]:
        """Search terms by name, ID, or synonym (case/accent-insensitive).

        Returns all terms where the normalized query matches the term id,
        termo, termo_en, or any synonym.
        """
        q = _norm(query)
        results = []
        for term in self._terms:
            candidates = [
                term.id,
                term.termo,
                term.termo_en,
                *term.synonyms_pt,
                *term.synonyms_en,
            ]
            if any(q in _norm(c) for c in candidates if c):
                results.append(term)
        return results

    def get(self, term_id: str) -> Term | None:
        """Get a single term by exact ID."""
        for term in self._terms:
            if term.id == term_id:
                return term
        return None

    def acronym(self, sigla: str) -> list[Acronym]:
        """Look up acronyms by sigla (case-insensitive)."""
        upper = sigla.upper()
        return [a for a in self._acronyms if a.sigla.upper() == upper]

    def layers(self) -> list[Layer]:
        """Return all ontology layers."""
        return list(self._layers)

    def all_terms(self) -> list[Term]:
        """Return all terms (glossary + extended)."""
        return list(self._terms)

    def all_acronyms(self) -> list[Acronym]:
        """Return all acronyms."""
        return list(self._acronyms)

    def meta(self) -> dict[str, Any]:
        """Return the dataset metadata dict."""
        return dict(self._full.get("meta", {}))
