"""geobrain — Python SDK for the Geolytics O&G domain dictionary.

Core exports::

    from geobrain import Dictionary, KnowledgeGraph, Validator, SweetExpander

    d = Dictionary()
    d.lookup("Pré-sal")           # list[Term]
    d.acronym("BOP")              # list[Acronym]
    d.layers()                    # list[Layer]

    kg = KnowledgeGraph.from_local()
    kg.entity("poco")
    kg.neighbors("poco", hops=2)
    kg.shortest_path("poco", "anp")
    kg.cypher_export()

    v = Validator()
    report = v.validate("Reserva 4P do Campo de Búzios")

    s = SweetExpander()
    s.expand("rocha-reservatorio", strategy="closeMatch")
"""

from ._version import __version__
from .crosswalk import CrosswalkEntry, CrosswalkIndex
from .dictionary import Acronym, Dictionary, Layer, Term
from .graph import Entity, KnowledgeGraph
from .lithology import LithologyDictionary
from .sweet import Alignment, ExpansionResult, SweetExpander
from .validator import Report, Validator, Violation

__all__ = [
    "Acronym",
    "Alignment",
    "CrosswalkEntry",
    # crosswalk
    "CrosswalkIndex",
    # dictionary
    "Dictionary",
    "Entity",
    "ExpansionResult",
    # graph
    "KnowledgeGraph",
    "Layer",
    # lithology
    "LithologyDictionary",
    "Report",
    # sweet
    "SweetExpander",
    "Term",
    # validator
    "Validator",
    "Violation",
    "__version__",
]
