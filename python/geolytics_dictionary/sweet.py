"""sweet.py — SweetExpander: SWEET ontology URI expansion for Geolytics terms."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from .data import load_json


# Embedded SWEET hierarchy (mirrors sweet-expand.js SWEET_HIERARCHY).
# Each tuple: (uri, parent_uri | None, module, label)
_SWEET_HIERARCHY_RAW: list[tuple[str, str | None, str, str]] = [
    # matr
    ("http://sweetontology.net/matr/Matter", None, "matr", "Matter"),
    ("http://sweetontology.net/matr/Substance", "http://sweetontology.net/matr/Matter", "matr", "Substance"),
    ("http://sweetontology.net/matr/Water", "http://sweetontology.net/matr/Substance", "matr", "Water"),
    ("http://sweetontology.net/matr/Brine", "http://sweetontology.net/matr/Water", "matr", "Brine"),
    ("http://sweetontology.net/matr/SalineWater", "http://sweetontology.net/matr/Water", "matr", "SalineWater"),
    # matrOrganics
    ("http://sweetontology.net/matrOrganics/OrganicCompound", "http://sweetontology.net/matr/Substance", "matrOrganics", "OrganicCompound"),
    ("http://sweetontology.net/matrOrganics/Hydrocarbon", "http://sweetontology.net/matrOrganics/OrganicCompound", "matrOrganics", "Hydrocarbon"),
    ("http://sweetontology.net/matrOrganics/Oil", "http://sweetontology.net/matrOrganics/Hydrocarbon", "matrOrganics", "Oil"),
    ("http://sweetontology.net/matrOrganics/NaturalGas", "http://sweetontology.net/matrOrganics/Hydrocarbon", "matrOrganics", "NaturalGas"),
    ("http://sweetontology.net/matrOrganics/Condensate", "http://sweetontology.net/matrOrganics/Hydrocarbon", "matrOrganics", "Condensate"),
    ("http://sweetontology.net/matrOrganics/Methane", "http://sweetontology.net/matrOrganics/NaturalGas", "matrOrganics", "Methane"),
    ("http://sweetontology.net/matrOrganics/Kerogen", "http://sweetontology.net/matrOrganics/OrganicCompound", "matrOrganics", "Kerogen"),
    # matrRock
    ("http://sweetontology.net/matrRock/Rock", "http://sweetontology.net/matr/Substance", "matrRock", "Rock"),
    # matrRockIgneous
    ("http://sweetontology.net/matrRockIgneous/IgneousRock", "http://sweetontology.net/matrRock/Rock", "matrRockIgneous", "IgneousRock"),
    ("http://sweetontology.net/matrRockIgneous/IntrusiveRock", "http://sweetontology.net/matrRockIgneous/IgneousRock", "matrRockIgneous", "IntrusiveRock"),
    ("http://sweetontology.net/matrRockIgneous/ExtrusiveRock", "http://sweetontology.net/matrRockIgneous/IgneousRock", "matrRockIgneous", "ExtrusiveRock"),
    ("http://sweetontology.net/matrRockIgneous/Granite", "http://sweetontology.net/matrRockIgneous/IntrusiveRock", "matrRockIgneous", "Granite"),
    ("http://sweetontology.net/matrRockIgneous/Basalt", "http://sweetontology.net/matrRockIgneous/ExtrusiveRock", "matrRockIgneous", "Basalt"),
    # matrRockSedimentary
    ("http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "http://sweetontology.net/matrRock/Rock", "matrRockSedimentary", "SedimentaryRock"),
    ("http://sweetontology.net/matrRockSedimentary/Sandstone", "http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "matrRockSedimentary", "Sandstone"),
    ("http://sweetontology.net/matrRockSedimentary/Limestone", "http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "matrRockSedimentary", "Limestone"),
    ("http://sweetontology.net/matrRockSedimentary/Shale", "http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "matrRockSedimentary", "Shale"),
    ("http://sweetontology.net/matrRockSedimentary/Dolostone", "http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "matrRockSedimentary", "Dolostone"),
    ("http://sweetontology.net/matrRockSedimentary/EvaporiteRock", "http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "matrRockSedimentary", "EvaporiteRock"),
    ("http://sweetontology.net/matrRockSedimentary/SaltRock", "http://sweetontology.net/matrRockSedimentary/EvaporiteRock", "matrRockSedimentary", "SaltRock"),
    ("http://sweetontology.net/matrRockSedimentary/CarbonatiteRock", "http://sweetontology.net/matrRockSedimentary/SedimentaryRock", "matrRockSedimentary", "CarbonatiteRock"),
    # matrRockMetamorphic
    ("http://sweetontology.net/matrRockMetamorphic/MetamorphicRock", "http://sweetontology.net/matrRock/Rock", "matrRockMetamorphic", "MetamorphicRock"),
    # matrMineral
    ("http://sweetontology.net/matrMineral/Mineral", "http://sweetontology.net/matr/Substance", "matrMineral", "Mineral"),
    ("http://sweetontology.net/matrMineral/Quartz", "http://sweetontology.net/matrMineral/Mineral", "matrMineral", "Quartz"),
    ("http://sweetontology.net/matrMineral/Calcite", "http://sweetontology.net/matrMineral/Mineral", "matrMineral", "Calcite"),
    ("http://sweetontology.net/matrMineral/Dolomite", "http://sweetontology.net/matrMineral/Mineral", "matrMineral", "Dolomite"),
    ("http://sweetontology.net/matrMineral/Pyrite", "http://sweetontology.net/matrMineral/Mineral", "matrMineral", "Pyrite"),
    ("http://sweetontology.net/matrMineral/Magnetite", "http://sweetontology.net/matrMineral/Mineral", "matrMineral", "Magnetite"),
    # procGeo
    ("http://sweetontology.net/proc/Process", None, "proc", "Process"),
    ("http://sweetontology.net/procGeo/GeologicProcess", "http://sweetontology.net/proc/Process", "procGeo", "GeologicProcess"),
    ("http://sweetontology.net/procGeo/TectonicProcess", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "TectonicProcess"),
    ("http://sweetontology.net/procGeo/Sedimentation", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "Sedimentation"),
    ("http://sweetontology.net/procGeo/Diagenesis", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "Diagenesis"),
    ("http://sweetontology.net/procGeo/Erosion", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "Erosion"),
    ("http://sweetontology.net/procGeo/Faulting", "http://sweetontology.net/procGeo/TectonicProcess", "procGeo", "Faulting"),
    ("http://sweetontology.net/procGeo/Folding", "http://sweetontology.net/procGeo/TectonicProcess", "procGeo", "Folding"),
    ("http://sweetontology.net/procGeo/Rifting", "http://sweetontology.net/procGeo/TectonicProcess", "procGeo", "Rifting"),
    ("http://sweetontology.net/procGeo/Metamorphism", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "Metamorphism"),
    ("http://sweetontology.net/procGeo/Magmatism", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "Magmatism"),
    ("http://sweetontology.net/procGeo/FluidMigration", "http://sweetontology.net/procGeo/GeologicProcess", "procGeo", "FluidMigration"),
    ("http://sweetontology.net/procGeo/Deformation", "http://sweetontology.net/procGeo/TectonicProcess", "procGeo", "Deformation"),
    # realmGeol
    ("http://sweetontology.net/realm/PlanetaryRealm", None, "realm", "PlanetaryRealm"),
    ("http://sweetontology.net/realmGeol/Lithosphere", "http://sweetontology.net/realm/PlanetaryRealm", "realmGeol", "Lithosphere"),
    ("http://sweetontology.net/realmGeol/Crust", "http://sweetontology.net/realmGeol/Lithosphere", "realmGeol", "Crust"),
    ("http://sweetontology.net/realmGeol/Mantle", "http://sweetontology.net/realmGeol/Lithosphere", "realmGeol", "Mantle"),
    ("http://sweetontology.net/realmGeol/GeologicFeature", None, "realmGeol", "GeologicFeature"),
    ("http://sweetontology.net/realmGeol/Unconformity", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeol", "Unconformity"),
    ("http://sweetontology.net/realmGeol/GeologicContact", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeol", "GeologicContact"),
    ("http://sweetontology.net/realmGeol/Borehole", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeol", "Borehole"),
    # realmGeolTectonic
    ("http://sweetontology.net/realmGeolTectonic/Fault", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeolTectonic", "Fault"),
    ("http://sweetontology.net/realmGeolTectonic/FaultZone", "http://sweetontology.net/realmGeolTectonic/Fault", "realmGeolTectonic", "FaultZone"),
    ("http://sweetontology.net/realmGeolTectonic/Fold", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeolTectonic", "Fold"),
    ("http://sweetontology.net/realmGeolTectonic/Anticline", "http://sweetontology.net/realmGeolTectonic/Fold", "realmGeolTectonic", "Anticline"),
    ("http://sweetontology.net/realmGeolTectonic/Syncline", "http://sweetontology.net/realmGeolTectonic/Fold", "realmGeolTectonic", "Syncline"),
    ("http://sweetontology.net/realmGeolTectonic/Foliation", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeolTectonic", "Foliation"),
    # realmGeolBasin
    ("http://sweetontology.net/realmGeolBasin/SedimentaryBasin", "http://sweetontology.net/realmGeol/GeologicFeature", "realmGeolBasin", "SedimentaryBasin"),
    ("http://sweetontology.net/realmGeolBasin/RiftBasin", "http://sweetontology.net/realmGeolBasin/SedimentaryBasin", "realmGeolBasin", "RiftBasin"),
    # realmHydro
    ("http://sweetontology.net/realmHydro/Hydrosphere", "http://sweetontology.net/realm/PlanetaryRealm", "realmHydro", "Hydrosphere"),
    ("http://sweetontology.net/realmHydro/Ocean", "http://sweetontology.net/realmHydro/Hydrosphere", "realmHydro", "Ocean"),
    ("http://sweetontology.net/realmHydro/HydrospherePart", "http://sweetontology.net/realmHydro/Hydrosphere", "realmHydro", "HydrospherePart"),
    # prop
    ("http://sweetontology.net/prop/PhysicalProperty", None, "prop", "PhysicalProperty"),
    ("http://sweetontology.net/propPressure/Pressure", "http://sweetontology.net/prop/PhysicalProperty", "propPressure", "Pressure"),
    ("http://sweetontology.net/propTemperature/Temperature", "http://sweetontology.net/prop/PhysicalProperty", "propTemperature", "Temperature"),
    ("http://sweetontology.net/propMass/Density", "http://sweetontology.net/prop/PhysicalProperty", "propMass", "Density"),
    ("http://sweetontology.net/propFluidTransport/Viscosity", "http://sweetontology.net/prop/PhysicalProperty", "propFluidTransport", "Viscosity"),
    ("http://sweetontology.net/propFluidTransport/Permeability", "http://sweetontology.net/prop/PhysicalProperty", "propFluidTransport", "Permeability"),
    ("http://sweetontology.net/propSpaceMultidimensional/Porosity", "http://sweetontology.net/prop/PhysicalProperty", "propSpaceMultidimensional", "Porosity"),
    ("http://sweetontology.net/propSpaceDistance/Depth", "http://sweetontology.net/prop/PhysicalProperty", "propSpaceDistance", "Depth"),
    # reprSciUnits
    ("http://sweetontology.net/reprSciUnits/Pascal", None, "reprSciUnits", "Pascal"),
    ("http://sweetontology.net/reprSciUnits/Kelvin", None, "reprSciUnits", "Kelvin"),
    ("http://sweetontology.net/reprSciUnits/Meter", None, "reprSciUnits", "Meter"),
    ("http://sweetontology.net/reprSciUnits/Darcy", None, "reprSciUnits", "Darcy"),
    # reprTimeGeologic
    ("http://sweetontology.net/reprTimeGeologic/GeochronologicEra", None, "reprTimeGeologic", "GeochronologicEra"),
    ("http://sweetontology.net/reprTimeGeologic/Mesozoic", "http://sweetontology.net/reprTimeGeologic/GeochronologicEra", "reprTimeGeologic", "Mesozoic"),
    ("http://sweetontology.net/reprTimeGeologic/Cretaceous", "http://sweetontology.net/reprTimeGeologic/GeochronologicEra", "reprTimeGeologic", "Cretaceous"),
    ("http://sweetontology.net/reprTimeGeologic/Aptian", "http://sweetontology.net/reprTimeGeologic/Cretaceous", "reprTimeGeologic", "Aptian"),
    ("http://sweetontology.net/reprTimeGeologic/Albian", "http://sweetontology.net/reprTimeGeologic/Cretaceous", "reprTimeGeologic", "Albian"),
]

# Build lookup dicts
_HIERARCHY_BY_URI: dict[str, tuple[str | None, str, str]] = {
    uri: (parent, module, label)
    for uri, parent, module, label in _SWEET_HIERARCHY_RAW
}


@dataclass(frozen=True)
class Alignment:
    """A SWEET alignment for a single Geolytics term."""

    geolytics_id: str
    sweet_uris: list[str]
    alignment_type: str
    sweet_module: str
    rationale_pt: str
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


@dataclass
class ExpansionResult:
    """Result of a SWEET expansion for a term."""

    term_id: str
    found: bool
    alignments: list[Alignment]
    sweet_uris: list[str]
    # uri -> {"label", "module", "parent", "ancestors", "children"}
    hierarchy: dict[str, Any]
    modules: list[str]


class SweetExpander:
    """SWEET ontology URI expander for Geolytics terms.

    Loads ``sweet-alignment.json`` once and provides fast in-process
    expansion without network calls.

    Usage::

        s = SweetExpander()
        s.expand("rocha-reservatorio", strategy="closeMatch")  # list[str] of SWEET URIs
        s.expand_full("hidrocarboneto")  # ExpansionResult with hierarchy
    """

    @cached_property
    def _alignments_data(self) -> list[dict[str, Any]]:
        try:
            data = load_json("sweet-alignment.json")
            return data.get("alignments", [])
        except FileNotFoundError:
            return []

    @cached_property
    def _alignments(self) -> list[Alignment]:
        return [
            Alignment(
                geolytics_id=a.get("geolytics_id", ""),
                sweet_uris=a.get("sweet_uris", []),
                alignment_type=a.get("alignment_type", ""),
                sweet_module=a.get("sweet_module", ""),
                rationale_pt=a.get("rationale_pt", ""),
                raw=a,
            )
            for a in self._alignments_data
        ]

    @cached_property
    def _by_term(self) -> dict[str, list[Alignment]]:
        result: dict[str, list[Alignment]] = {}
        for a in self._alignments:
            result.setdefault(a.geolytics_id, []).append(a)
        return result

    def _ancestors(self, uri: str) -> list[str]:
        result = []
        current_uri = uri
        while True:
            entry = _HIERARCHY_BY_URI.get(current_uri)
            if entry is None or entry[0] is None:
                break
            parent_uri = entry[0]
            result.append(parent_uri)
            current_uri = parent_uri
        return result

    def _children(self, uri: str) -> list[str]:
        return [u for u, (p, _, _) in _HIERARCHY_BY_URI.items() if p == uri]

    def expand(
        self,
        term_id: str,
        strategy: str | None = None,
    ) -> list[str]:
        """Return SWEET URIs for a Geolytics term.

        Args:
            term_id: Geolytics term identifier (e.g. ``"hidrocarboneto"``).
            strategy: Optional SKOS alignment type filter, e.g.
                ``"closeMatch"``, ``"exactMatch"``, ``"broadMatch"``,
                ``"narrowMatch"``, ``"relatedMatch"``. When ``None``, all
                alignments are returned.

        Returns:
            Deduplicated list of SWEET URI strings.
        """
        term_alignments = self._by_term.get(term_id, [])
        if strategy:
            # Accept both "closeMatch" and "skos:closeMatch"
            norm = strategy.replace("skos:", "")
            term_alignments = [
                a for a in term_alignments
                if a.alignment_type.replace("skos:", "") == norm
            ]
        uris: list[str] = []
        seen: set[str] = set()
        for a in term_alignments:
            for uri in a.sweet_uris:
                if uri not in seen:
                    seen.add(uri)
                    uris.append(uri)
        return uris

    def expand_full(
        self,
        term_id: str,
        include_hierarchy: bool = True,
        include_siblings: bool = False,
    ) -> ExpansionResult:
        """Return full expansion data including hierarchy.

        Mirrors the JS ``expand()`` return shape.
        """
        term_alignments = self._by_term.get(term_id, [])
        if not term_alignments:
            return ExpansionResult(
                term_id=term_id,
                found=False,
                alignments=[],
                sweet_uris=[],
                hierarchy={},
                modules=[],
            )

        # Collect all unique SWEET URIs
        uris_seen: set[str] = set()
        uris: list[str] = []
        for a in term_alignments:
            for uri in a.sweet_uris:
                if uri not in uris_seen:
                    uris_seen.add(uri)
                    uris.append(uri)

        modules = list({a.sweet_module for a in term_alignments if a.sweet_module})

        hierarchy: dict[str, Any] = {}
        if include_hierarchy:
            for uri in uris:
                entry = _HIERARCHY_BY_URI.get(uri)
                ancestor_uris = self._ancestors(uri)
                child_uris = self._children(uri)
                sibling_uris: list[str] = []
                if include_siblings and entry and entry[0]:
                    sibling_uris = [
                        u for u in self._children(entry[0]) if u != uri
                    ]
                hierarchy[uri] = {
                    "label": entry[2] if entry else None,
                    "module": entry[1] if entry else None,
                    "parent": entry[0] if entry else None,
                    "ancestors": ancestor_uris,
                    "children": child_uris,
                    "siblings": sibling_uris,
                }

        return ExpansionResult(
            term_id=term_id,
            found=True,
            alignments=term_alignments,
            sweet_uris=uris,
            hierarchy=hierarchy,
            modules=modules,
        )

    def all_term_ids(self) -> list[str]:
        """Return all Geolytics term IDs that have SWEET alignments."""
        return list(self._by_term.keys())
