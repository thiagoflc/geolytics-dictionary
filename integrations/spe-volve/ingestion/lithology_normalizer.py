"""
lithology_normalizer.py
=======================
Normalizes free-text lithology descriptions (MudLogInterval.lithology) to the
CGI Simple Lithology canonical vocabulary (~437 concepts), enriching Neo4j nodes
with `cgi_lithology_id` and `cgi_lithology_uri` properties.

Source vocabulary: CGI Simple Lithology 201211 (OWL)
https://github.com/opengeospatial/GeoSciML/blob/master/ontology/CGI-SimpleLithology201211.ttl

Standalone — the CGI concept map is embedded directly; no runtime JSON read.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CGI_BASE_URI = "http://resource.geosciml.org/classifier/cgi/lithOntology/"

# ---------------------------------------------------------------------------
# CGI_LITHOLOGY_MAP
# Mapping: normalised raw string -> canonical CGI concept ID.
#
# Keys are lower-cased and stripped; values are verbatim CGI IDs from the
# cgi-lithology.json vocabulary (437 concepts, maintainer CGI/IUGS).
#
# Coverage strategy:
#   - Siliciclastics/arenaceous (sandstone, arkose, greywacke, …)
#   - Pelites (shale, mudstone, claystone, siltstone, …)
#   - Carbonates (limestone, chalk, dolostone/dolomite, wackestone, …)
#   - Evaporites (halite/salt, anhydrite, gypsum, …)
#   - Igneous — volcanic (basalt, rhyolite, andesite, trachyte, dacite, …)
#   - Igneous — plutonic (granite, diorite, gabbro, tonalite, …)
#   - Metamorphic (schist, gneiss, quartzite, phyllite, marble, …)
#   - Organic / coal-bearing (coal, lignite, peat, …)
#   - Volve-specific field usages (Hugin Fm sandstone, Draupne/Sleipner shale, …)
#   - Misc (breccia, conglomerate, chert, evaporite, tuff, …)
# ---------------------------------------------------------------------------

CGI_LITHOLOGY_MAP: dict[str, str] = {
    # ------------------------------------------------------------------
    # Sandstone / arenaceous
    # ------------------------------------------------------------------
    "sandstone": "generic_sandstone",
    "sand stone": "generic_sandstone",
    "clastic sandstone": "clastic_sandstone",
    "sand": "sand",
    "sandy": "sand_size_sediment",
    "arenite": "arenite",
    "arkose": "arenite",              # arkosic arenite -> arenite (closest CGI)
    "arkosic arenite": "arenite",
    "arkosic sandstone": "arenite",
    "greywacke": "generic_sandstone",
    "graywacke": "generic_sandstone",
    "wacke": "wackestone",            # wacke in clastic sense -> wackestone label in CGI
    "quartzarenite": "arenite",
    "quartz arenite": "arenite",
    "sublitharenite": "arenite",
    "lithic sandstone": "generic_sandstone",
    "fine sandstone": "generic_sandstone",
    "medium sandstone": "generic_sandstone",
    "coarse sandstone": "generic_sandstone",
    "fine-grained sandstone": "generic_sandstone",
    "medium-grained sandstone": "generic_sandstone",
    "coarse-grained sandstone": "generic_sandstone",
    "very fine sandstone": "generic_sandstone",
    "very coarse sandstone": "generic_sandstone",
    "calcareous sandstone": "generic_sandstone",
    "silty sandstone": "generic_sandstone",
    "sandy limestone": "impure_limestone",
    "sandy shale": "clastic_mudstone",

    # ------------------------------------------------------------------
    # Pelites / mudstones / shales
    # ------------------------------------------------------------------
    "shale": "shale",
    "mudstone": "clastic_mudstone",
    "mud stone": "clastic_mudstone",
    "claystone": "claystone",
    "clay stone": "claystone",
    "siltstone": "siltstone",
    "silt stone": "siltstone",
    "mudrock": "clastic_mudstone",
    "clay": "clay",
    "silt": "silt",
    "mud": "mud",
    "argillite": "clastic_mudstone",
    "argillaceous": "clastic_mudstone",
    "silty shale": "shale",
    "calcareous shale": "shale",
    "silty mudstone": "clastic_mudstone",
    "sandy mudstone": "clastic_mudstone",
    "black shale": "shale",
    "organic shale": "shale",
    "dark shale": "shale",
    "calcareous mudstone": "carbonate_mudstone",
    "carbonate mudstone": "carbonate_mudstone",
    "calcareous siltstone": "siltstone",
    "calcareous claystone": "claystone",
    "carbonaceous shale": "shale",
    "carbonaceous mudstone": "clastic_mudstone",
    "organic mudstone": "organic_bearing_mudstone",
    "organic-bearing mudstone": "organic_bearing_mudstone",
    "siliceous mudstone": "silicate_mudstone",

    # ------------------------------------------------------------------
    # Carbonates
    # ------------------------------------------------------------------
    "limestone": "limestone",
    "chalk": "chalk",
    "dolostone": "dolostone",
    "dolomite": "dolostone",
    "dolomitic limestone": "impure_limestone",
    "impure limestone": "impure_limestone",
    "impure dolostone": "impure_dolostone",
    "calcarenite": "arenite",         # calcareous arenite -> arenite
    "wackestone": "wackestone",
    "packstone": "packstone",
    "grainstone": "grainstone",
    "boundstone": "boundstone",
    "framestone": "framestone",
    "carbonate": "carbonate_sedimentary_rock",
    "carbonate rock": "carbonate_sedimentary_rock",
    "carbonate sedimentary rock": "carbonate_sedimentary_rock",
    "calcareous": "calcareous_carbonate_sedimentary_rock",
    "travertine": "travertine",
    "micrite": "carbonate_mudstone",
    "bioclastic limestone": "limestone",
    "oolitic limestone": "limestone",
    "reefal limestone": "limestone",
    "reef limestone": "limestone",
    "muddy limestone": "impure_limestone",
    "dolomitic rock": "dolomitic_or_magnesian_sedimentary_rock",
    "dolomitic sedimentary rock": "dolomitic_or_magnesian_sedimentary_rock",

    # ------------------------------------------------------------------
    # Evaporites
    # ------------------------------------------------------------------
    "salt": "rock_salt",
    "halite": "rock_salt",
    "rock salt": "rock_salt",
    "anhydrite": "rock_gypsum_or_anhydrite",
    "gypsum": "rock_gypsum_or_anhydrite",
    "gypsum or anhydrite": "rock_gypsum_or_anhydrite",
    "evaporite": "evaporite",
    "exotic evaporite": "exotic_evaporite",
    "potash": "evaporite",
    "sylvite": "evaporite",
    "carnallite": "evaporite",

    # ------------------------------------------------------------------
    # Siliceous / chert
    # ------------------------------------------------------------------
    "chert": "non_clastic_siliceous_sedimentary_rock",
    "flint": "non_clastic_siliceous_sedimentary_rock",
    "radiolarite": "non_clastic_siliceous_sedimentary_rock",
    "diatomite": "biogenic_silica_sedimentary_rock",
    "siliceous ooze": "siliceous_ooze",
    "siliceous rock": "non_clastic_siliceous_sedimentary_rock",
    "novaculite": "non_clastic_siliceous_sedimentary_rock",

    # ------------------------------------------------------------------
    # Phosphatic
    # ------------------------------------------------------------------
    "phosphorite": "phosphorite",
    "phosphate": "phosphorite",
    "phosphatic": "phosphatic_sediment",

    # ------------------------------------------------------------------
    # Iron-rich
    # ------------------------------------------------------------------
    "ironstone": "iron_rich_sedimentary_rock",
    "banded iron formation": "iron_rich_sedimentary_rock",
    "bif": "iron_rich_sedimentary_rock",
    "ferruginous": "iron_rich_sedimentary_rock",

    # ------------------------------------------------------------------
    # Coarse clastic / conglomerates / breccia
    # ------------------------------------------------------------------
    "conglomerate": "generic_conglomerate",
    "breccia": "breccia",
    "diamictite": "diamictite",
    "diamicton": "diamicton",
    "gravel": "gravel",
    "cobble gravel": "cobble_gravel_size_sediment",
    "pebble gravel": "pebble_gravel_size_sediment",
    "boulder gravel": "boulder_gravel_size_sediment",
    "rudite": "generic_conglomerate",
    "clastic conglomerate": "clastic_conglomerate",

    # ------------------------------------------------------------------
    # Organic / coal
    # ------------------------------------------------------------------
    "coal": "coal",
    "lignite": "lignite",
    "peat": "peat",
    "anthracite": "anthracite_coal",
    "anthracite coal": "anthracite_coal",
    "bituminous coal": "bituminous_coal",
    "sub-bituminous coal": "bituminous_coal",
    "subbituminous coal": "bituminous_coal",
    "sapropel": "sapropel",
    "organic material": "organic_rich_sedimentary_rock",
    "carbonaceous material": "organic_rich_sedimentary_rock",

    # ------------------------------------------------------------------
    # Igneous — basaltic / mafic volcanic
    # ------------------------------------------------------------------
    "basalt": "basalt",
    "basaltic": "basalt",
    "tholeiitic basalt": "tholeiitic_basalt",
    "alkali basalt": "alkali_olivine_basalt",
    "alkali olivine basalt": "alkali_olivine_basalt",
    "basanite": "basanite",
    "spilite": "spilite",
    "boninite": "boninite",

    # ------------------------------------------------------------------
    # Igneous — intermediate volcanic
    # ------------------------------------------------------------------
    "andesite": "andesite",
    "andesitic": "andesite",
    "trachyte": "trachyte",
    "trachytic rock": "trachytic_rock",
    "latite": "latite",
    "phonolite": "phonolite",
    "tephrite": "tephrite",
    "dacite": "dacite",

    # ------------------------------------------------------------------
    # Igneous — felsic volcanic
    # ------------------------------------------------------------------
    "rhyolite": "rhyolite",
    "rhyolitic": "rhyolite",
    "obsidian": "glassy_igneous_rock",
    "pumice": "pyroclastic_rock",
    "foidite": "foidite",
    "alkali feldspar rhyolite": "alkali_feldspar_rhyolite",

    # ------------------------------------------------------------------
    # Pyroclastic / volcaniclastic
    # ------------------------------------------------------------------
    "tuff": "pyroclastic_rock",
    "volcanic tuff": "pyroclastic_rock",
    "ash tuff": "ash_tuff_lapillistone_and_lapilli_tuff",
    "lapillistone": "ash_tuff_lapillistone_and_lapilli_tuff",
    "tephra": "tephra",
    "agglomerate": "tuff_breccia_agglomerate_or_pyroclastic_breccia",
    "pyroclastic breccia": "tuff_breccia_agglomerate_or_pyroclastic_breccia",
    "volcanic breccia": "tuff_breccia_agglomerate_or_pyroclastic_breccia",
    "tuffite": "tuffite",
    "pyroclastic rock": "pyroclastic_rock",
    "pyroclastics": "pyroclastic_rock",
    "ash and lapilli": "ash_and_lapilli",

    # ------------------------------------------------------------------
    # Igneous — plutonic
    # ------------------------------------------------------------------
    "granite": "granite",
    "granitic": "granite",
    "granitoid": "granitoid",
    "granodiorite": "granodiorite",
    "monzogranite": "monzogranite",
    "syenogranite": "syenogranite",
    "tonalite": "tonalite",
    "syenite": "syenite",
    "monzonite": "monzonite",
    "diorite": "diorite",
    "dioritic rock": "dioritic_rock",
    "gabbro": "gabbro",
    "gabbroic rock": "gabbroic_rock",
    "anorthosite": "anorthosite",
    "peridotite": "peridotite",
    "dunite": "peridotite",
    "pyroxenite": "pyroxenite",
    "hornblendite": "hornblendite",
    "pegmatite": "pegmatite",
    "aplite": "aplite",
    "carbonatite": "carbonatite",
    "quartz diorite": "quartz_diorite",
    "quartz monzonite": "quartz_monzonite",
    "quartz gabbro": "quartz_gabbro",

    # ------------------------------------------------------------------
    # Igneous — ultramafic
    # ------------------------------------------------------------------
    "ultramafic": "ultramafic_igneous_rock",
    "ultramafic rock": "ultramafic_igneous_rock",
    "komatiite": "komatiitic_rock",
    "serpentinite": "serpentinite",
    "kimberlite": "exotic_composition_igneous_rock",

    # ------------------------------------------------------------------
    # Metamorphic — foliated
    # ------------------------------------------------------------------
    "schist": "schist",
    "mica schist": "mica_schist",
    "gneiss": "gneiss",
    "orthogneiss": "orthogneiss",
    "paragneiss": "paragneiss",
    "phyllite": "phyllite",
    "slate": "slate",
    "mylonite": "mylonitic_rock",
    "phyllonite": "phyllonite",

    # ------------------------------------------------------------------
    # Metamorphic — non-foliated / high-grade
    # ------------------------------------------------------------------
    "quartzite": "quartzite",
    "marble": "marble",
    "hornfels": "hornfels",
    "amphibolite": "amphibolite",
    "granulite": "granulite",
    "eclogite": "eclogite",
    "skarn": "skarn",
    "migmatite": "migmatite",
    "granofels": "granofels",
    "greenstone": "chlorite_actinolite_epidote_metamorphic_rock",
    "greenschist": "chlorite_actinolite_epidote_metamorphic_rock",
    "blueschist": "glaucophane_lawsonite_epidote_metamorphic_rock",
    "glaucophane schist": "glaucophane_lawsonite_epidote_metamorphic_rock",

    # ------------------------------------------------------------------
    # Cataclastic / fault-related
    # ------------------------------------------------------------------
    "cataclasite": "cataclasite_series",
    "fault gouge": "cataclasite_series",
    "fault breccia": "cataclasite_series",
    "fault rock": "fault",

    # ------------------------------------------------------------------
    # Unconsolidated sediment
    # ------------------------------------------------------------------
    "unconsolidated sand": "sand",
    "unconsolidated gravel": "gravel",
    "unconsolidated mud": "mud",
    "unconsolidated clay": "clay",
    "unconsolidated silt": "silt",
    "alluvium": "material_formed_in_surficial_environment",
    "colluvium": "material_formed_in_surficial_environment",
    "soil": "material_formed_in_surficial_environment",
    "till": "diamicton",
    "glacial till": "diamicton",
    "loess": "silt",

    # ------------------------------------------------------------------
    # Residual / weathering
    # ------------------------------------------------------------------
    "laterite": "residual_material",
    "bauxite": "bauxite",
    "regolith": "material_formed_in_surficial_environment",
    "duricrust": "duricrust",

    # ------------------------------------------------------------------
    # Volve field — specific formation lithologies
    # (Hugin Fm, Sleipner Fm, Draupne Fm, Åre Fm)
    # ------------------------------------------------------------------
    "hugin sandstone": "generic_sandstone",
    "sleipner shale": "shale",
    "draupne shale": "shale",
    "draupne formation": "shale",
    "are sandstone": "generic_sandstone",         # Åre Fm sandstone
    "are limestone": "limestone",
    "are coal": "coal",
    "skagerrak sandstone": "generic_sandstone",
    "amundsen shale": "shale",
    "heather shale": "shale",
    "ness sandstone": "generic_sandstone",
    "etive sandstone": "generic_sandstone",
    "rannoch siltstone": "siltstone",

    # ------------------------------------------------------------------
    # Generic / catch-all sedimentary
    # ------------------------------------------------------------------
    "sedimentary rock": "sedimentary_rock",
    "sediment": "sediment",
    "clastic sedimentary rock": "clastic_sedimentary_rock",
    "hybrid sedimentary rock": "hybrid_sedimentary_rock",
    "rock": "rock",
    "unknown": "rock_material",
    "not reported": "rock_material",
    "no sample": "rock_material",
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalise_key(raw: str) -> str:
    """Lower-case, strip whitespace, collapse internal spaces."""
    return re.sub(r"\s+", " ", raw.strip().lower())


# Pre-build a lookup with normalised keys for O(1) access.
_NORMALISED_MAP: dict[str, str] = {
    _normalise_key(k): v for k, v in CGI_LITHOLOGY_MAP.items()
}


# Words that indicate compound descriptions — strip these to get the dominant type.
_COMPOUND_SEPARATORS = re.compile(
    r"\s+with\s+|\s+and\s+|\s+/\s+|,\s*|\s+interbedded\s+with\s+"
    r"|\s+bearing\s+|\s+rich\s+|\s+dominated\s+|\s+laminae\b|\s+laminites?\b"
    r"|\s+intercalations?\b|\s+streaks?\b|\s+nodules?\b|\s+bands?\b",
    re.IGNORECASE,
)

_MODIFIER_WORDS = frozenset(
    [
        "very", "fine", "medium", "coarse", "grained", "grain", "size",
        "silty", "sandy", "muddy", "calcareous", "dolomitic", "organic",
        "carbonaceous", "bituminous", "dark", "grey", "gray", "green",
        "red", "brown", "black", "white", "light", "hard", "soft",
        "tight", "porous", "fractured", "cemented", "glauconitic",
        "ferruginous", "pyritic", "micaceous", "fossiliferous",
        "laminated", "massive", "cross-bedded", "cross", "bedded",
        "interbedded", "thin", "thick", "bedded", "argillaceous",
        "minor", "trace", "occasional", "abundant", "dominant",
        "some", "rare", "partly", "partially", "highly",
        "slightly", "strongly", "weakly",
    ]
)


def _extract_dominant_type(normalised: str) -> str:
    """
    From a compound string (already lower-cased), extract the dominant
    lithology token — the first substantial word or phrase.
    """
    # Split on compound separators and take the first segment.
    parts = _COMPOUND_SEPARATORS.split(normalised)
    dominant = parts[0].strip()
    return dominant


def _fuzzy_match(normalised: str) -> str | None:
    """
    Try progressively looser matches:
    1. Exact normalised key match.
    2. Dominant-type extraction then exact match.
    3. Token-level scan — find the longest key that is a substring.
    """
    # 1. Exact.
    hit = _NORMALISED_MAP.get(normalised)
    if hit:
        return hit

    # 2. Dominant part.
    dominant = _extract_dominant_type(normalised)
    if dominant != normalised:
        hit = _NORMALISED_MAP.get(dominant)
        if hit:
            return hit

    # 3. Longest substring key match (greedy).
    best_key: str | None = None
    best_len = 0
    for key in _NORMALISED_MAP:
        if key in normalised and len(key) > best_len:
            best_key = key
            best_len = len(key)
    if best_key:
        return _NORMALISED_MAP[best_key]

    # 4. Single-token fallback — check each word.
    tokens = normalised.split()
    for token in tokens:
        if token not in _MODIFIER_WORDS:
            hit = _NORMALISED_MAP.get(token)
            if hit:
                return hit

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_lithology(raw: str) -> dict[str, Any]:
    """
    Normalise a free-text lithology string to a CGI Simple Lithology concept.

    Parameters
    ----------
    raw:
        Raw lithology string from MudLogInterval.lithology, e.g.
        "Sandstone with shale laminae", "sh", "LST", "SILTST".

    Returns
    -------
    dict with keys:
        cgi_id       : str  — CGI concept id (e.g. "generic_sandstone")
        cgi_uri      : str  — full URI
        raw          : str  — original input unchanged
        confidence   : float — 1.0 exact, 0.8 dominant-type, 0.6 substring, 0.4 token
        broader      : str | None — first parent concept id (static mapping)
    """
    if not raw or not raw.strip():
        return {
            "cgi_id": None,
            "cgi_uri": None,
            "raw": raw,
            "confidence": 0.0,
            "broader": None,
        }

    normalised = _normalise_key(raw)
    confidence = 0.0
    cgi_id: str | None = None

    # --- Exact match ---
    hit = _NORMALISED_MAP.get(normalised)
    if hit:
        cgi_id = hit
        confidence = 1.0
    else:
        # --- Dominant-type extraction ---
        dominant = _extract_dominant_type(normalised)
        if dominant != normalised:
            hit = _NORMALISED_MAP.get(dominant)
            if hit:
                cgi_id = hit
                confidence = 0.8

        if cgi_id is None:
            # --- Longest-substring scan ---
            best_key: str | None = None
            best_len = 0
            for key in _NORMALISED_MAP:
                if key in normalised and len(key) > best_len:
                    best_key = key
                    best_len = len(key)
            if best_key:
                cgi_id = _NORMALISED_MAP[best_key]
                confidence = 0.6

        if cgi_id is None:
            # --- Single-token fallback ---
            for token in normalised.split():
                if token not in _MODIFIER_WORDS:
                    hit = _NORMALISED_MAP.get(token)
                    if hit:
                        cgi_id = hit
                        confidence = 0.4
                        break

    cgi_uri = f"{CGI_BASE_URI}{cgi_id}" if cgi_id else None
    broader = _BROADER_MAP.get(cgi_id) if cgi_id else None

    return {
        "cgi_id": cgi_id,
        "cgi_uri": cgi_uri,
        "raw": raw,
        "confidence": confidence,
        "broader": broader,
    }


def build_lithology_cypher_batch(wellbore_uid: str | None = None) -> str:
    """
    Generate a Cypher script that enriches MudLogInterval nodes in Neo4j
    with CGI lithology properties.

    The script uses a static lookup expression (CASE WHEN … END) built from
    CGI_LITHOLOGY_MAP so no external Python call is needed at query time.

    Parameters
    ----------
    wellbore_uid:
        Optional filter — only process intervals belonging to this wellbore.

    Returns
    -------
    Cypher query string ready for neo4j.Session.run().
    """
    where_clauses = ["m.lithology IS NOT NULL", "m.cgi_lithology_id IS NULL"]
    if wellbore_uid:
        where_clauses.append("m.wellbore_uid = $wellbore_uid")

    where_block = "\n  AND ".join(where_clauses)

    # Build CASE expression mapping normalised raw values to CGI ids.
    # We use toLower(trim(m.lithology)) for server-side normalisation.
    case_lines: list[str] = []
    for raw_key, cgi_id in CGI_LITHOLOGY_MAP.items():
        escaped = raw_key.replace("'", "\\'")
        case_lines.append(f"    WHEN toLower(trim(m.lithology)) = '{escaped}' THEN '{cgi_id}'")

    case_expr = "CASE\n" + "\n".join(case_lines) + "\n    ELSE null\n  END"

    cypher = f"""// CGI Simple Lithology enrichment — generated by lithology_normalizer.py
MATCH (m:MudLogInterval)
WHERE {where_block}
WITH m,
  {case_expr} AS cgi_id
WHERE cgi_id IS NOT NULL
SET
  m.cgi_lithology_id  = cgi_id,
  m.cgi_lithology_uri = '{CGI_BASE_URI}' + cgi_id
RETURN count(m) AS enriched_count
"""
    return cypher


def run_normalization(
    driver: Any,
    wellbore_uid: str | None = None,
    batch_size: int = 500,
) -> dict[str, Any]:
    """
    Execute lithology normalisation in batch against a Neo4j database.

    Reads all MudLogInterval nodes that have a `lithology` property but no
    `cgi_lithology_id`, normalises each via `normalize_lithology`, then
    writes back in batches of `batch_size`.

    Parameters
    ----------
    driver:
        neo4j.GraphDatabase.driver instance (or compatible).
    wellbore_uid:
        Optional filter to process only one wellbore's intervals.
    batch_size:
        Number of nodes to MERGE per transaction.  Default 500.

    Returns
    -------
    dict with keys:
        processed       : int
        matched         : int
        unmatched       : int
        unmatched_values: list[str]
    """
    # --- Read phase ---
    read_query = """
        MATCH (m:MudLogInterval)
        WHERE m.lithology IS NOT NULL
          AND m.cgi_lithology_id IS NULL
        {wellbore_filter}
        RETURN m.uid AS uid, m.lithology AS lithology
    """.format(
        wellbore_filter=(
            "AND m.wellbore_uid = $wellbore_uid" if wellbore_uid else ""
        )
    )

    params: dict[str, Any] = {}
    if wellbore_uid:
        params["wellbore_uid"] = wellbore_uid

    with driver.session() as session:
        records = list(session.run(read_query, **params))

    processed = len(records)
    matched = 0
    unmatched_values: list[str] = []

    # --- Normalise ---
    enriched: list[dict[str, Any]] = []
    for rec in records:
        uid: str = rec["uid"]
        lithology: str = rec["lithology"]
        result = normalize_lithology(lithology)
        if result["cgi_id"]:
            matched += 1
            enriched.append(
                {
                    "uid": uid,
                    "cgi_lithology_id": result["cgi_id"],
                    "cgi_lithology_uri": result["cgi_uri"],
                }
            )
        else:
            unmatched_values.append(lithology)

    # --- Write phase (batched MERGE) ---
    write_query = """
        UNWIND $rows AS row
        MATCH (m:MudLogInterval {uid: row.uid})
        SET m.cgi_lithology_id  = row.cgi_lithology_id,
            m.cgi_lithology_uri = row.cgi_lithology_uri
    """

    with driver.session() as session:
        for offset in range(0, len(enriched), batch_size):
            batch = enriched[offset : offset + batch_size]
            session.run(write_query, rows=batch)

    return {
        "processed": processed,
        "matched": matched,
        "unmatched": processed - matched,
        "unmatched_values": sorted(set(unmatched_values)),
    }


# ---------------------------------------------------------------------------
# Broader (parent) concept map — one-level up for key rock types.
# Sourced from parents[] in cgi-lithology.json.
# ---------------------------------------------------------------------------

_BROADER_MAP: dict[str, str | None] = {
    "generic_sandstone": "rock_material",
    "clastic_sandstone": "rock_material",
    "arenite": "rock_material",
    "sand": "rock_material",
    "sand_size_sediment": "rock_material",
    "shale": None,
    "clastic_mudstone": "rock_material",
    "claystone": "rock_material",
    "siltstone": "rock_material",
    "mud": "rock_material",
    "clay": "rock_material",
    "silt": "rock_material",
    "silicate_mudstone": "rock_material",
    "organic_bearing_mudstone": "rock_material",
    "carbonate_mudstone": None,
    "limestone": "rock_material",
    "chalk": "rock_material",
    "dolostone": "rock_material",
    "impure_limestone": "rock_material",
    "impure_dolostone": "rock_material",
    "carbonate_sedimentary_rock": None,
    "calcareous_carbonate_sedimentary_rock": None,
    "dolomitic_or_magnesian_sedimentary_rock": None,
    "wackestone": None,
    "packstone": None,
    "grainstone": None,
    "boundstone": None,
    "framestone": None,
    "travertine": "rock_material",
    "rock_salt": "rock_material",
    "rock_gypsum_or_anhydrite": "rock_material",
    "evaporite": None,
    "exotic_evaporite": "rock_material",
    "non_clastic_siliceous_sedimentary_rock": None,
    "biogenic_silica_sedimentary_rock": None,
    "siliceous_ooze": "rock_material",
    "phosphorite": None,
    "phosphatic_sediment": None,
    "iron_rich_sedimentary_rock": None,
    "generic_conglomerate": "rock_material",
    "breccia": None,
    "diamictite": None,
    "diamicton": None,
    "gravel": "rock_material",
    "cobble_gravel_size_sediment": "rock_material",
    "pebble_gravel_size_sediment": "rock_material",
    "boulder_gravel_size_sediment": "rock_material",
    "clastic_conglomerate": None,
    "coal": None,
    "lignite": "rock_material",
    "peat": None,
    "anthracite_coal": "rock_material",
    "bituminous_coal": "rock_material",
    "sapropel": "rock_material",
    "organic_rich_sedimentary_rock": None,
    "basalt": "rock_material",
    "tholeiitic_basalt": "rock_material",
    "alkali_olivine_basalt": "rock_material",
    "basanite": "rock_material",
    "spilite": "rock_material",
    "boninite": "rock_material",
    "andesite": None,
    "trachyte": "rock_material",
    "trachytic_rock": "rock_material",
    "latite": "rock_material",
    "phonolite": "rock_material",
    "tephrite": "rock_material",
    "dacite": "rock_material",
    "rhyolite": "rock_material",
    "glassy_igneous_rock": "rock_material",
    "foidite": "rock_material",
    "alkali_feldspar_rhyolite": "rock_material",
    "pyroclastic_rock": None,
    "ash_tuff_lapillistone_and_lapilli_tuff": None,
    "tephra": None,
    "tuff_breccia_agglomerate_or_pyroclastic_breccia": None,
    "tuffite": None,
    "ash_and_lapilli": "rock_material",
    "granite": None,
    "granitoid": None,
    "granodiorite": None,
    "monzogranite": "rock_material",
    "syenogranite": "rock_material",
    "tonalite": None,
    "syenite": None,
    "monzonite": None,
    "diorite": None,
    "dioritic_rock": None,
    "gabbro": None,
    "gabbroic_rock": None,
    "anorthosite": "rock_material",
    "peridotite": None,
    "pyroxenite": "rock_material",
    "hornblendite": "rock_material",
    "pegmatite": "rock_material",
    "aplite": None,
    "carbonatite": None,
    "quartz_diorite": None,
    "quartz_monzonite": None,
    "quartz_gabbro": None,
    "ultramafic_igneous_rock": "rock_material",
    "komatiitic_rock": None,
    "serpentinite": None,
    "exotic_composition_igneous_rock": None,
    "schist": None,
    "mica_schist": None,
    "gneiss": None,
    "orthogneiss": "rock_material",
    "paragneiss": None,
    "phyllite": "rock_material",
    "slate": None,
    "mylonitic_rock": "foliated_metamorphic_rock",
    "phyllonite": None,
    "quartzite": None,
    "marble": None,
    "hornfels": None,
    "amphibolite": None,
    "granulite": "rock_material",
    "eclogite": None,
    "skarn": "rock_material",
    "migmatite": None,
    "granofels": None,
    "chlorite_actinolite_epidote_metamorphic_rock": None,
    "glaucophane_lawsonite_epidote_metamorphic_rock": None,
    "cataclasite_series": None,
    "fault": None,
    "material_formed_in_surficial_environment": "rock_material",
    "residual_material": "rock_material",
    "bauxite": None,
    "duricrust": None,
    "sedimentary_rock": None,
    "sediment": None,
    "clastic_sedimentary_rock": None,
    "hybrid_sedimentary_rock": "rock_material",
    "rock": None,
    "rock_material": None,
}

# ---------------------------------------------------------------------------
# Standalone test suite
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    TEST_CASES: list[tuple[str, str | None, str]] = [
        # (raw_input, expected_cgi_id_or_None, description)
        # 1. Exact match — sandstone
        ("sandstone", "generic_sandstone", "exact: sandstone"),
        # 2. Exact match — shale
        ("shale", "shale", "exact: shale"),
        # 3. Exact match — limestone
        ("limestone", "limestone", "exact: limestone"),
        # 4. Exact match — coal (Åre Fm)
        ("coal", "coal", "exact: coal (Volve Åre)"),
        # 5. Exact match — dolostone
        ("dolostone", "dolostone", "exact: dolostone"),
        # 6. Exact match — chalk
        ("chalk", "chalk", "exact: chalk"),
        # 7. Exact match — halite -> rock_salt
        ("halite", "rock_salt", "exact: halite -> rock_salt"),
        # 8. Exact match — salt -> rock_salt
        ("salt", "rock_salt", "exact: salt -> rock_salt"),
        # 9. Exact match — anhydrite
        ("anhydrite", "rock_gypsum_or_anhydrite", "exact: anhydrite"),
        # 10. Exact match — granite
        ("granite", "granite", "exact: granite"),
        # 11. Exact match — basalt
        ("basalt", "basalt", "exact: basalt"),
        # 12. Exact match — gabbro
        ("gabbro", "gabbro", "exact: gabbro"),
        # 13. Exact match — schist
        ("schist", "schist", "exact: schist"),
        # 14. Exact match — quartzite
        ("quartzite", "quartzite", "exact: quartzite"),
        # 15. Fuzzy — compound "sandstone with shale laminae" -> sandstone
        (
            "sandstone with shale laminae",
            "generic_sandstone",
            "fuzzy compound: sandstone dominates",
        ),
        # 16. Fuzzy — "grey fine-grained sandstone" -> sandstone (substring)
        (
            "grey fine-grained sandstone",
            "generic_sandstone",
            "fuzzy substring: grey fine-grained sandstone",
        ),
        # 17. Volve-specific — Draupne shale
        ("draupne shale", "shale", "Volve specific: Draupne shale"),
        # 18. Volve-specific — Hugin sandstone
        ("hugin sandstone", "generic_sandstone", "Volve specific: Hugin sandstone"),
        # 19. Token fallback — "calcareous wackestone facies" -> wackestone
        (
            "calcareous wackestone facies",
            "wackestone",
            "fuzzy substring: calcareous wackestone",
        ),
        # 20. Unmapped — should return None
        (
            "xenolithic intrusion with haüyne phenocrysts",
            None,
            "unmapped exotic description (no recognizable lithology token)",
        ),
    ]

    print("=" * 70)
    print("Lithology Normalizer — Standalone Test Suite")
    print("=" * 70)

    passed = 0
    failed = 0

    for idx, (raw, expected_id, description) in enumerate(TEST_CASES, start=1):
        result = normalize_lithology(raw)
        got_id = result["cgi_id"]
        ok = got_id == expected_id
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        print(
            f"[{idx:02d}] {status}  {description}\n"
            f"       raw={raw!r}\n"
            f"       expected={expected_id!r}  got={got_id!r}"
            f"  confidence={result['confidence']:.1f}"
            f"  broader={result['broader']!r}\n"
            f"       uri={result['cgi_uri']}"
        )

    print("=" * 70)
    print(f"Results: {passed}/{len(TEST_CASES)} passed, {failed} failed.")

    # Also exercise build_lithology_cypher_batch
    print("\n--- build_lithology_cypher_batch (no wellbore_uid) ---")
    cypher = build_lithology_cypher_batch()
    line_count = cypher.count("\n")
    print(f"Generated Cypher: {line_count} lines, {len(cypher)} chars.")

    print("\n--- build_lithology_cypher_batch (with wellbore_uid) ---")
    cypher_wb = build_lithology_cypher_batch(wellbore_uid="15/9-F-1B")
    assert "m.wellbore_uid = $wellbore_uid" in cypher_wb
    print("wellbore_uid filter present: OK")

    # Verify URI construction
    result_uri = normalize_lithology("sandstone")
    assert result_uri["cgi_uri"] == (
        "http://resource.geosciml.org/classifier/cgi/lithOntology/generic_sandstone"
    ), f"URI mismatch: {result_uri['cgi_uri']}"
    print("\nURI construction: OK")

    sys.exit(0 if failed == 0 else 1)
