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
from .dictionary import Dictionary, Term, Acronym, Layer
from .graph import KnowledgeGraph, Entity
from .validator import Validator, Violation, Report
from .sweet import SweetExpander, Alignment, ExpansionResult
from .crosswalk import CrosswalkIndex, CrosswalkEntry

__all__ = [
    "__version__",
    # dictionary
    "Dictionary",
    "Term",
    "Acronym",
    "Layer",
    # graph
    "KnowledgeGraph",
    "Entity",
    # validator
    "Validator",
    "Violation",
    "Report",
    # sweet
    "SweetExpander",
    "Alignment",
    "ExpansionResult",
    # crosswalk
    "CrosswalkIndex",
    "CrosswalkEntry",
]
