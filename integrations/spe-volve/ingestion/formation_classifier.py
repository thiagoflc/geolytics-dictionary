"""
formation_classifier.py
-----------------------
Enriches Formation nodes in the SPE Volve Neo4j graph with:
  - Formal stratigraphic name and rank (CGI/GeoSciML vocabulary)
  - Geologic age (stage, epoch, period)
  - Dominant lithology and CGI lithology URI
  - GeoSciML GeologicUnit URI

The Volve field (Block 15/9, Norwegian North Sea) penetrates a stratigraphic
column ranging from Permian evaporites at the base through Quaternary sediments
at the top. The Jurassic Hugin Formation is the main oil reservoir.

Sources used for geological data:
  - NPD (Norwegian Petroleum Directorate) FactPages — Block 15/9 lithostratigraphy
  - Isaksen & Tonstad 1989, NPD Bulletin No. 5 — Viking Graben stratigraphy
  - Vollset & Dore 1984, NPF Spec. Pub. 1 — North Sea lithostratigraphic nomenclature
  - CGI Simple Lithology 201211 (OGC/IUGS) — lithology URIs
  - GeoSciML 4.1 gsmlb module — GeologicUnit URI
"""

from __future__ import annotations

import re
from typing import Optional

# ---------------------------------------------------------------------------
# CGI / GeoSciML base URIs (from cgi-stratigraphic-rank.json and ontology-map.json)
# ---------------------------------------------------------------------------
_CGI_RANK_NS = "http://resource.geosciml.org/classifier/cgi/stratigraphicrank/"
_CGI_LITH_NS = "http://resource.geosciml.org/classifier/cgi/lithOntology/"
_GSMLB_GEOLOGIC_UNIT = "http://geosciml.org/def/gsmlb#GeologicUnit"

# ---------------------------------------------------------------------------
# VOLVE_FORMATION_CATALOG
# ---------------------------------------------------------------------------
# Keys are normalized names (lowercase, stripped of spaces and punctuation).
# All geological ages follow the ICS International Chronostratigraphic Chart 2023.
# Lithology URIs are from CGI Simple Lithology 201211.
# Stratigraphic rank URIs are from CGI StratigraphicRank 201202.
# ---------------------------------------------------------------------------
VOLVE_FORMATION_CATALOG: dict[str, dict] = {
    # ------------------------------------------------------------------
    # JURASSIC — Humber Group (syn. Viking Group in older NPD usage)
    # ------------------------------------------------------------------
    "draupne": {
        "formal_name": "Draupne Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Kimmeridgian-Tithonian",
        "period": "Jurassic",
        "epoch": "Late Jurassic",
        "lithology_dominant": "shale",
        "cgi_lithology_uri": _CGI_LITH_NS + "shale",
        "description": (
            "Late Jurassic organic-rich marine shale; primary source rock and "
            "regional seal for the Hugin reservoir in Volve field. "
            "Equivalent to Kimmeridge Clay in the UK sector."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Humber Group",
        "age_order": 1,  # youngest in Volve column (lower age_order = shallower)
    },
    "hugin": {
        "formal_name": "Hugin Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Callovian-Oxfordian",
        "period": "Jurassic",
        "epoch": "Middle-Late Jurassic",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Middle-Late Jurassic marginal-marine to fluvio-deltaic sandstone; "
            "main producing reservoir formation in the Volve field (Block 15/9). "
            "Lateral equivalent of the Fulmar Formation (UK sector)."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Humber Group",
        "age_order": 2,
    },
    "sleipner": {
        "formal_name": "Sleipner Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Bathonian-Callovian",
        "period": "Jurassic",
        "epoch": "Middle Jurassic",
        "lithology_dominant": "shale",
        "cgi_lithology_uri": _CGI_LITH_NS + "shale",
        "description": (
            "Middle Jurassic marine mudstone/shale; intra-Jurassic seal between "
            "Hugin and Brent interval. Part of the Humber Group in the southern "
            "Viking Graben."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Humber Group",
        "age_order": 3,
    },
    "heather": {
        "formal_name": "Heather Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Bathonian-Oxfordian",
        "period": "Jurassic",
        "epoch": "Middle-Late Jurassic",
        "lithology_dominant": "shale",
        "cgi_lithology_uri": _CGI_LITH_NS + "shale",
        "description": (
            "Middle-Late Jurassic open-marine mudstone; regionally extensive "
            "within the Viking Graben. Conformably underlies the Draupne "
            "Formation and overlies the Brent Group."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Humber Group",
        "age_order": 3,
    },
    # ------------------------------------------------------------------
    # JURASSIC — Brent Group (Middle Jurassic deltaic)
    # ------------------------------------------------------------------
    "brent": {
        "formal_name": "Brent Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Bajocian-Bathonian",
        "period": "Jurassic",
        "epoch": "Middle Jurassic",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Middle Jurassic regressive-transgressive deltaic sequence comprising "
            "the Broom, Rannoch, Etive, Ness, and Tarbert formations. Major "
            "reservoir interval in many North Sea fields; present but thin in the "
            "Volve area."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Viking Group (sensu lato)",
        "age_order": 4,
    },
    # ------------------------------------------------------------------
    # JURASSIC — Dunlin Group (Early Jurassic)
    # ------------------------------------------------------------------
    "dunlin": {
        "formal_name": "Dunlin Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Pliensbachian-Aalenian",
        "period": "Jurassic",
        "epoch": "Early-Middle Jurassic",
        "lithology_dominant": "shale",
        "cgi_lithology_uri": _CGI_LITH_NS + "shale",
        "description": (
            "Early Jurassic marine mudstone and minor sandstone; comprises the "
            "Amundsen, Burton, Cook, and Drake formations. Acts as regional seal "
            "above the Statfjord Group."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Dunlin Group",
        "age_order": 5,
    },
    "cook": {
        "formal_name": "Cook Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Pliensbachian-Toarcian",
        "period": "Jurassic",
        "epoch": "Early Jurassic",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Early Jurassic shallow-marine to deltaic sandstone intercalated within "
            "the Dunlin Group mudstones. Secondary reservoir target in some Viking "
            "Graben wells."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Dunlin Group",
        "age_order": 5,
    },
    # ------------------------------------------------------------------
    # TRIASSIC-JURASSIC — Statfjord Group
    # ------------------------------------------------------------------
    "statfjord": {
        "formal_name": "Statfjord Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Rhaetian-Hettangian",
        "period": "Triassic-Jurassic",
        "epoch": "Late Triassic-Early Jurassic",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Late Triassic to Early Jurassic fluvio-deltaic sandstone and "
            "mudstone; comprises the Raude, Eiriksson, and Nansen formations. "
            "Important reservoir in the Statfjord and adjacent fields."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Statfjord Group",
        "age_order": 6,
    },
    # ------------------------------------------------------------------
    # TRIASSIC — Hegre Group
    # ------------------------------------------------------------------
    "skagerrak": {
        "formal_name": "Skagerrak Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Carnian-Norian",
        "period": "Triassic",
        "epoch": "Late Triassic",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Late Triassic fluvial red-bed sandstone and mudstone; deposited in "
            "alluvial fan and braided river systems. Part of the Hegre Group in "
            "the central North Sea."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Hegre Group",
        "age_order": 7,
    },
    "are": {
        "formal_name": "Are Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Rhaetian",
        "period": "Triassic",
        "epoch": "Late Triassic",
        "lithology_dominant": "mudstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "mudstone",
        "description": (
            "Latest Triassic (Rhaetian) coal-bearing mudstone, siltstone, and "
            "sandstone; deposited in swampy fluvial to deltaic environments. "
            "Marks the transition between the Triassic Hegre Group and the "
            "Jurassic Statfjord Group."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Hegre Group",
        "age_order": 7,
    },
    "lunde": {
        "formal_name": "Lunde Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Norian-Rhaetian",
        "period": "Triassic",
        "epoch": "Late Triassic",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Late Triassic fluvial and aeolian sandstone with interbedded mudstone; "
            "part of the Hegre Group. Prospective reservoir in the deeper Triassic "
            "section of the Viking Graben."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Hegre Group",
        "age_order": 8,
    },
    "smith_bank": {
        "formal_name": "Smith Bank Formation",
        "stratigraphic_rank": "Formation",
        "cgi_rank_uri": _CGI_RANK_NS + "formation",
        "geologic_age": "Induan-Anisian",
        "period": "Triassic",
        "epoch": "Early-Middle Triassic",
        "lithology_dominant": "mudstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "mudstone",
        "description": (
            "Early-Middle Triassic red-bed mudstone, siltstone, and evaporite "
            "intercalations; deposited in alluvial to sabkha environments. "
            "Forms the base of the Triassic Hegre Group in the central North Sea."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Hegre Group",
        "age_order": 9,
    },
    # ------------------------------------------------------------------
    # PERMIAN
    # ------------------------------------------------------------------
    "zechstein": {
        "formal_name": "Zechstein Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Lopingian (Wuchiapingian-Changhsingian)",
        "period": "Permian",
        "epoch": "Late Permian",
        "lithology_dominant": "rock_salt",
        "cgi_lithology_uri": _CGI_LITH_NS + "rock_salt",
        "description": (
            "Late Permian evaporite sequence (halite, anhydrite, carbonates) "
            "deposited in a restricted epicontinental basin across NW Europe. "
            "Acts as a regional seal and creates complex salt structures (diapirs, "
            "pillows) that influence trap geometry in overlying Mesozoic intervals."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Zechstein Group",
        "age_order": 10,
    },
    "rotliegend": {
        "formal_name": "Rotliegend Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Cisuralian-Guadalupian (Asselian-Wordian)",
        "period": "Permian",
        "epoch": "Early-Middle Permian",
        "lithology_dominant": "sandstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "sandstone",
        "description": (
            "Early-Middle Permian red-bed aeolian and fluvial sandstone (Lower "
            "Rotliegend) capped by lacustrine and sabkha deposits (Upper "
            "Rotliegend). Major gas reservoir across the southern North Sea; "
            "deep basement section in the Volve area."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Rotliegend Group",
        "age_order": 11,
    },
    # ------------------------------------------------------------------
    # CRETACEOUS — regional overburden (encountered in Volve wells)
    # ------------------------------------------------------------------
    "chalk": {
        "formal_name": "Chalk Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Cenomanian-Maastrichtian",
        "period": "Cretaceous",
        "epoch": "Late Cretaceous",
        "lithology_dominant": "limestone",
        "cgi_lithology_uri": _CGI_LITH_NS + "limestone",
        "description": (
            "Late Cretaceous pelagic carbonate (chalk) deposited during a period "
            "of high sea level across NW Europe. Regional overburden unit above "
            "the Jurassic reservoir in the Volve field."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Chalk Group",
        "age_order": 0,  # shallower than Draupne
    },
    "shetland": {
        "formal_name": "Shetland Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Campanian-Maastrichtian",
        "period": "Cretaceous",
        "epoch": "Late Cretaceous",
        "lithology_dominant": "shale",
        "cgi_lithology_uri": _CGI_LITH_NS + "shale",
        "description": (
            "Late Cretaceous marine shale and marl of the Shetland Group; "
            "overlies the Chalk Group in the northern North Sea. Equivalent to "
            "parts of the Tor and Ekofisk formations in some regional schemes."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Shetland Group",
        "age_order": 0,
    },
    "cromer_knoll": {
        "formal_name": "Cromer Knoll Group",
        "stratigraphic_rank": "Group",
        "cgi_rank_uri": _CGI_RANK_NS + "group",
        "geologic_age": "Berriasian-Albian",
        "period": "Cretaceous",
        "epoch": "Early Cretaceous",
        "lithology_dominant": "mudstone",
        "cgi_lithology_uri": _CGI_LITH_NS + "mudstone",
        "description": (
            "Early Cretaceous marine mudstone, marl, and minor sandstone; "
            "conformably overlies the Upper Jurassic Humber Group across much "
            "of the central North Sea. Includes the Valhall, Åsgard, and Rødby "
            "formations in the Norwegian sector."
        ),
        "geosciml_uri": _GSMLB_GEOLOGIC_UNIT,
        "group": "Cromer Knoll Group",
        "age_order": 0,
    },
}

# ---------------------------------------------------------------------------
# AGE_HIERARCHY
# ---------------------------------------------------------------------------
# Stratigraphic order for the Volve wellbore column, deepest → shallowest.
# Index 0 = deepest (oldest); highest index = shallowest (youngest).
# Groups and formations are intermixed as encountered in wellbore data.
# ---------------------------------------------------------------------------
AGE_HIERARCHY: list[dict] = [
    {
        "normalized_key": "rotliegend",
        "formal_name": "Rotliegend Group",
        "period": "Permian",
        "age_ma_base": 298.9,
        "age_ma_top": 259.1,
    },
    {
        "normalized_key": "zechstein",
        "formal_name": "Zechstein Group",
        "period": "Permian",
        "age_ma_base": 259.1,
        "age_ma_top": 251.9,
    },
    {
        "normalized_key": "smith_bank",
        "formal_name": "Smith Bank Formation",
        "period": "Triassic",
        "age_ma_base": 251.9,
        "age_ma_top": 241.5,
    },
    {
        "normalized_key": "skagerrak",
        "formal_name": "Skagerrak Formation",
        "period": "Triassic",
        "age_ma_base": 237.0,
        "age_ma_top": 208.5,
    },
    {
        "normalized_key": "lunde",
        "formal_name": "Lunde Formation",
        "period": "Triassic",
        "age_ma_base": 216.5,
        "age_ma_top": 201.3,
    },
    {
        "normalized_key": "are",
        "formal_name": "Are Formation",
        "period": "Triassic",
        "age_ma_base": 208.5,
        "age_ma_top": 201.3,
    },
    {
        "normalized_key": "statfjord",
        "formal_name": "Statfjord Group",
        "period": "Triassic-Jurassic",
        "age_ma_base": 201.3,
        "age_ma_top": 193.8,
    },
    {
        "normalized_key": "dunlin",
        "formal_name": "Dunlin Group",
        "period": "Jurassic",
        "age_ma_base": 190.8,
        "age_ma_top": 174.1,
    },
    {
        "normalized_key": "cook",
        "formal_name": "Cook Formation",
        "period": "Jurassic",
        "age_ma_base": 190.8,
        "age_ma_top": 182.7,
    },
    {
        "normalized_key": "brent",
        "formal_name": "Brent Group",
        "period": "Jurassic",
        "age_ma_base": 170.3,
        "age_ma_top": 166.1,
    },
    {
        "normalized_key": "sleipner",
        "formal_name": "Sleipner Formation",
        "period": "Jurassic",
        "age_ma_base": 168.3,
        "age_ma_top": 163.5,
    },
    {
        "normalized_key": "heather",
        "formal_name": "Heather Formation",
        "period": "Jurassic",
        "age_ma_base": 168.3,
        "age_ma_top": 157.3,
    },
    {
        "normalized_key": "hugin",
        "formal_name": "Hugin Formation",
        "period": "Jurassic",
        "age_ma_base": 163.5,
        "age_ma_top": 152.1,
    },
    {
        "normalized_key": "draupne",
        "formal_name": "Draupne Formation",
        "period": "Jurassic",
        "age_ma_base": 157.3,
        "age_ma_top": 145.0,
    },
    {
        "normalized_key": "cromer_knoll",
        "formal_name": "Cromer Knoll Group",
        "period": "Cretaceous",
        "age_ma_base": 145.0,
        "age_ma_top": 100.5,
    },
    {
        "normalized_key": "chalk",
        "formal_name": "Chalk Group",
        "period": "Cretaceous",
        "age_ma_base": 100.5,
        "age_ma_top": 66.0,
    },
    {
        "normalized_key": "shetland",
        "formal_name": "Shetland Group",
        "period": "Cretaceous",
        "age_ma_base": 83.6,
        "age_ma_top": 66.0,
    },
]

# Lookup: normalized_key → depth index (0 = deepest)
_AGE_HIERARCHY_INDEX: dict[str, int] = {
    entry["normalized_key"]: idx for idx, entry in enumerate(AGE_HIERARCHY)
}

# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------
# Suffixes commonly appended to formation names in raw well data
_FORMATION_SUFFIXES = re.compile(
    r"\b(formation|fm\.?|group|gp\.?|member|mbr\.?|unit|interval|shale|sand|sst)\b",
    re.IGNORECASE,
)

# Prefixes that appear before names (e.g. "UPPER HUGIN", "LWR STATFJORD")
_POSITION_PREFIXES = re.compile(
    r"^(upper|lower|lwr|upr|mid|middle|basal|top|base)\b[\s_-]*",
    re.IGNORECASE,
)


def normalize_formation_name(raw: str) -> str:
    """Normalize a raw formation name to a catalog lookup key.

    Handles common variations found in Volve wellbore data:
      - Case: "HUGIN FM" → "hugin"
      - Suffixes: "Hugin Formation", "Hugin Fm.", "Hugin Fm" → "hugin"
      - Position qualifiers: "Upper Hugin", "Lower Statfjord" → base name
      - Underscores and hyphens used as word separators
      - Compound names with underscores: "smith_bank" → "smith_bank"

    Returns
    -------
    str
        Lowercase key suitable for lookup in VOLVE_FORMATION_CATALOG.
        Returns the cleaned string even if not present in the catalog.
    """
    if not raw or not isinstance(raw, str):
        return ""

    name = raw.strip()

    # Remove position qualifiers (Upper, Lower, Mid, etc.)
    name = _POSITION_PREFIXES.sub("", name)

    # Remove formation-rank suffixes (handles "Fm", "Fm.", "Formation", etc.)
    name = _FORMATION_SUFFIXES.sub("", name)

    # Strip stray punctuation left after suffix removal (e.g. trailing ".")
    name = name.strip(" .")

    # Collapse whitespace/hyphens/underscores, then lowercase
    name = re.sub(r"[\s\-]+", "_", name.strip())
    name = name.lower().strip("_")

    # Collapse repeated underscores
    name = re.sub(r"_+", "_", name)

    return name


def classify_formation(raw_name: str) -> Optional[dict]:
    """Return the full classification record for a raw formation name.

    Parameters
    ----------
    raw_name:
        Raw formation name as stored in the Neo4j Formation node (e.g.
        "HUGIN FM", "Sleipner Formation", "STATFJORD GP").

    Returns
    -------
    dict | None
        A copy of the catalog entry enriched with the matched key, or
        ``None`` if the name is not recognized.
    """
    key = normalize_formation_name(raw_name)
    entry = VOLVE_FORMATION_CATALOG.get(key)
    if entry is None:
        return None
    return {"catalog_key": key, **entry}


# ---------------------------------------------------------------------------
# Cypher generation
# ---------------------------------------------------------------------------

def build_enrichment_cypher() -> str:
    """Return a Cypher script that enriches all Formation nodes in Neo4j.

    The script iterates over every Formation node. For recognized names
    it sets the enrichment properties; for unrecognized names it sets a
    flag so analysts can review them. At the end it returns a coverage
    summary projection.

    The CASE block is generated programmatically from VOLVE_FORMATION_CATALOG
    so the catalog is the single source of truth.

    Returns
    -------
    str
        Complete Cypher script (can be executed via ``neo4j.Session.run()``
        or pasted into Neo4j Browser / cypher-shell).
    """
    when_clauses: list[str] = []

    for key, entry in VOLVE_FORMATION_CATALOG.items():
        # Build a list of raw name patterns that normalize to this key
        patterns = _known_raw_patterns(key, entry["formal_name"])
        pattern_list = ", ".join(f'"{p}"' for p in patterns)
        props = _format_props(key, entry)
        when_clauses.append(f"  WHEN toUpper(trim(f.name)) IN [{pattern_list}]\n    THEN {props}")

    when_block = "\n".join(when_clauses)

    cypher = f"""\
// ============================================================
// Formation Enrichment — SPE Volve (Block 15/9, Norwegian North Sea)
// Generated by formation_classifier.py :: build_enrichment_cypher()
// CGI/GeoSciML URIs from cgi-stratigraphic-rank.json
// ============================================================

// Phase 1: enrich recognized formations
MATCH (f:Formation)
WITH f,
  CASE
{when_block}
  ELSE null
  END AS props
WHERE props IS NOT NULL
SET
  f.formal_name        = props.formal_name,
  f.stratigraphic_rank = props.stratigraphic_rank,
  f.cgi_rank_uri       = props.cgi_rank_uri,
  f.geologic_age       = props.geologic_age,
  f.period             = props.period,
  f.epoch              = props.epoch,
  f.lithology_dominant = props.lithology_dominant,
  f.cgi_lithology_uri  = props.cgi_lithology_uri,
  f.description        = props.description,
  f.geosciml_uri       = props.geosciml_uri,
  f.parent_group       = props.group,
  f.enriched           = true,
  f.enriched_by        = 'formation_classifier.py'

// Phase 2: flag unrecognized formations for review
WITH count(f) AS enriched_count
MATCH (u:Formation)
WHERE u.enriched IS NULL OR u.enriched = false
SET u.enriched = false,
    u.enrichment_status = 'UNRECOGNIZED'

// Phase 3: return coverage statistics
WITH enriched_count
MATCH (total:Formation)
WITH enriched_count, count(total) AS total_count
MATCH (unrecognized:Formation {{enriched: false}})
RETURN
  enriched_count                                              AS enriched,
  count(unrecognized)                                        AS unrecognized,
  total_count                                                AS total,
  round(100.0 * enriched_count / total_count, 2)            AS coverage_pct
"""
    return cypher


def _known_raw_patterns(key: str, formal_name: str) -> list[str]:
    """Return uppercase raw name variants likely to appear in Volve data."""
    base = key.replace("_", " ").upper()
    formal_upper = formal_name.upper()

    patterns: list[str] = []

    # e.g. "HUGIN FM", "HUGIN FORMATION", "HUGIN GP", "HUGIN GROUP"
    patterns.append(base + " FM")
    patterns.append(base + " FORMATION")
    patterns.append(base + " GP")
    patterns.append(base + " GROUP")
    patterns.append(base)

    # Formal name uppercased
    if formal_upper not in patterns:
        patterns.append(formal_upper)

    # Remove duplicates while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def _format_props(key: str, entry: dict) -> str:
    """Format a Cypher map literal from a catalog entry."""
    fields = {
        "formal_name": entry["formal_name"],
        "stratigraphic_rank": entry["stratigraphic_rank"],
        "cgi_rank_uri": entry["cgi_rank_uri"],
        "geologic_age": entry["geologic_age"],
        "period": entry["period"],
        "epoch": entry["epoch"],
        "lithology_dominant": entry["lithology_dominant"],
        "cgi_lithology_uri": entry["cgi_lithology_uri"],
        "description": entry["description"],
        "geosciml_uri": entry["geosciml_uri"],
        "group": entry["group"],
    }
    pairs = ", ".join(f'{k}: "{v}"' for k, v in fields.items())
    return "{" + pairs + "}"


# ---------------------------------------------------------------------------
# Neo4j batch classification
# ---------------------------------------------------------------------------

def run_classification(driver) -> dict:
    """Execute formation classification in batch against a live Neo4j instance.

    For each Formation node the function:
      1. Reads the raw ``name`` property.
      2. Looks up the classification via ``classify_formation()``.
      3. Writes enrichment properties in a single parameterized query.

    Parameters
    ----------
    driver:
        A ``neo4j.Driver`` instance (from the official ``neo4j`` package).

    Returns
    -------
    dict with keys:
        total        — number of Formation nodes processed
        enriched     — number of nodes successfully classified
        unrecognized — list of raw names that were not matched
        coverage_pct — float, percentage of nodes enriched
    """
    fetch_query = "MATCH (f:Formation) RETURN f.formation_id AS fid, f.name AS name"

    write_query = """\
MATCH (f:Formation {formation_id: $fid})
SET
  f.formal_name        = $formal_name,
  f.stratigraphic_rank = $stratigraphic_rank,
  f.cgi_rank_uri       = $cgi_rank_uri,
  f.geologic_age       = $geologic_age,
  f.period             = $period,
  f.epoch              = $epoch,
  f.lithology_dominant = $lithology_dominant,
  f.cgi_lithology_uri  = $cgi_lithology_uri,
  f.description        = $description,
  f.geosciml_uri       = $geosciml_uri,
  f.parent_group       = $group,
  f.enriched           = true,
  f.enriched_by        = 'formation_classifier.py'
"""

    flag_query = """\
MATCH (f:Formation {formation_id: $fid})
SET f.enriched = false,
    f.enrichment_status = 'UNRECOGNIZED'
"""

    total = 0
    enriched = 0
    unrecognized: list[str] = []

    with driver.session() as session:
        records = session.run(fetch_query).data()
        total = len(records)

        for record in records:
            fid = record["fid"]
            raw_name = record.get("name") or ""
            classification = classify_formation(raw_name)

            if classification:
                params = {
                    "fid": fid,
                    "formal_name": classification["formal_name"],
                    "stratigraphic_rank": classification["stratigraphic_rank"],
                    "cgi_rank_uri": classification["cgi_rank_uri"],
                    "geologic_age": classification["geologic_age"],
                    "period": classification["period"],
                    "epoch": classification["epoch"],
                    "lithology_dominant": classification["lithology_dominant"],
                    "cgi_lithology_uri": classification["cgi_lithology_uri"],
                    "description": classification["description"],
                    "geosciml_uri": classification["geosciml_uri"],
                    "group": classification["group"],
                }
                session.run(write_query, params)
                enriched += 1
            else:
                session.run(flag_query, {"fid": fid})
                if raw_name not in unrecognized:
                    unrecognized.append(raw_name)

    coverage_pct = round(100.0 * enriched / total, 2) if total > 0 else 0.0

    return {
        "total": total,
        "enriched": enriched,
        "unrecognized": unrecognized,
        "coverage_pct": coverage_pct,
    }


# ---------------------------------------------------------------------------
# Stratigraphic order validation helper
# ---------------------------------------------------------------------------

def validate_stratigraphic_order(raw_names: list[str]) -> dict:
    """Check whether a list of formation tops is in correct depth order.

    In a normally deposited (non-inverted) wellbore the formations should
    appear from youngest (shallowest) to oldest (deepest) as depth increases.
    This function checks whether the recognized formations follow the expected
    AGE_HIERARCHY order. AGE_HIERARCHY index 0 = deepest/oldest; a top-to-bottom
    list must have non-increasing indices (each unit older than the one above).

    Parameters
    ----------
    raw_names:
        Formation names ordered by increasing depth (as encountered in a
        wellbore log, top → bottom).

    Returns
    -------
    dict with keys:
        valid        — bool, True if the recognized sequence is monotonically
                       deepening (i.e. AGE_HIERARCHY index is non-increasing
                       from top to bottom, since index 0 = deepest/oldest)
        violations   — list of (upper_name, lower_name) pairs that are
                       out of sequence (lower unit has a higher list index,
                       meaning it is shallower than expected)
        recognized   — list of (raw_name, normalized_key, age_idx) tuples
        unrecognized — list of raw names not in the catalog
    """
    recognized: list[tuple[str, str, int]] = []
    unrecognized_names: list[str] = []

    for raw in raw_names:
        key = normalize_formation_name(raw)
        idx = _AGE_HIERARCHY_INDEX.get(key)
        if idx is not None:
            recognized.append((raw, key, idx))
        else:
            unrecognized_names.append(raw)

    # AGE_HIERARCHY: index 0 = deepest (oldest), highest = shallowest (youngest).
    # A wellbore list is ordered top→bottom (increasing depth), so each successive
    # formation must have an equal or lower index (older = deeper = lower index).
    # A violation occurs when a unit placed deeper has a higher index (is younger).
    violations: list[tuple[str, str]] = []
    for i in range(1, len(recognized)):
        prev_raw, prev_key, prev_idx = recognized[i - 1]
        curr_raw, curr_key, curr_idx = recognized[i]
        if curr_idx > prev_idx:
            violations.append((prev_raw, curr_raw))

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "recognized": recognized,
        "unrecognized": unrecognized_names,
    }


# ---------------------------------------------------------------------------
# __main__ — 15 test cases
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    passed = 0
    failed = 0

    def check(description: str, condition: bool, detail: str = "") -> None:
        global passed, failed
        status = "PASS" if condition else "FAIL"
        if condition:
            passed += 1
        else:
            failed += 1
        suffix = f" — {detail}" if detail else ""
        print(f"  [{status}] {description}{suffix}")

    print("=" * 65)
    print("formation_classifier.py — test suite (15 cases)")
    print("=" * 65)

    # ------------------------------------------------------------------
    # Section A: normalize_formation_name
    # ------------------------------------------------------------------
    print("\nA. normalize_formation_name")

    check(
        "HUGIN FM → hugin",
        normalize_formation_name("HUGIN FM") == "hugin",
    )
    check(
        "Hugin Formation → hugin",
        normalize_formation_name("Hugin Formation") == "hugin",
    )
    check(
        "DRAUPNE FM → draupne",
        normalize_formation_name("DRAUPNE FM") == "draupne",
    )
    check(
        "STATFJORD GP → statfjord",
        normalize_formation_name("STATFJORD GP") == "statfjord",
    )
    check(
        "Skagerrak Fm. → skagerrak",
        normalize_formation_name("Skagerrak Fm.") == "skagerrak",
    )
    check(
        "Upper Hugin → hugin (position qualifier stripped)",
        normalize_formation_name("Upper Hugin") == "hugin",
    )
    check(
        "SMITH BANK FM → smith_bank",
        normalize_formation_name("SMITH BANK FM") == "smith_bank",
    )

    # ------------------------------------------------------------------
    # Section B: classify_formation
    # ------------------------------------------------------------------
    print("\nB. classify_formation")

    result_hugin = classify_formation("HUGIN FM")
    check(
        "HUGIN FM → formal_name = 'Hugin Formation'",
        result_hugin is not None and result_hugin["formal_name"] == "Hugin Formation",
    )
    check(
        "HUGIN FM → stratigraphic_rank = 'Formation'",
        result_hugin is not None and result_hugin["stratigraphic_rank"] == "Formation",
    )
    check(
        "HUGIN FM → period = 'Jurassic'",
        result_hugin is not None and result_hugin["period"] == "Jurassic",
    )
    check(
        "HUGIN FM → cgi_rank_uri contains 'formation'",
        result_hugin is not None
        and "formation" in result_hugin["cgi_rank_uri"],
    )

    result_statfjord = classify_formation("STATFJORD GP")
    check(
        "STATFJORD GP → stratigraphic_rank = 'Group'",
        result_statfjord is not None
        and result_statfjord["stratigraphic_rank"] == "Group",
    )

    result_unknown = classify_formation("NORDLAND GP")
    check(
        "NORDLAND GP → None (unrecognized)",
        result_unknown is None,
        f"got {result_unknown}",
    )

    # ------------------------------------------------------------------
    # Section C: validate_stratigraphic_order
    # ------------------------------------------------------------------
    print("\nC. validate_stratigraphic_order")

    # Correct order: Chalk (shallow) → Draupne → Hugin → Brent → Statfjord → Zechstein (deep)
    correct_sequence = [
        "CHALK GROUP",
        "DRAUPNE FM",
        "HUGIN FM",
        "BRENT GROUP",
        "STATFJORD GP",
        "Zechstein Group",
    ]
    result_correct = validate_stratigraphic_order(correct_sequence)
    check(
        "Correct stratigraphic order detected as valid",
        result_correct["valid"] is True,
        f"violations={result_correct['violations']}",
    )

    # Inverted: Hugin listed above Draupne (wrong — Hugin is deeper than Draupne)
    # Correct depth order top→bottom: Draupne (idx=13) then Hugin (idx=12).
    # Inverted means Hugin (idx=12) listed first, then Draupne (idx=13) below it —
    # curr_idx(13) > prev_idx(12) triggers a violation.
    inverted_sequence = ["HUGIN FM", "DRAUPNE FM"]
    result_inverted = validate_stratigraphic_order(inverted_sequence)
    check(
        "Inverted order (Hugin above Draupne top-to-bottom) detected as invalid",
        result_inverted["valid"] is False,
        f"violations={result_inverted['violations']}",
    )

    # ------------------------------------------------------------------
    # Section D: build_enrichment_cypher sanity check
    # ------------------------------------------------------------------
    print("\nD. build_enrichment_cypher")

    cypher = build_enrichment_cypher()
    check(
        "Cypher contains MATCH (f:Formation)",
        "MATCH (f:Formation)" in cypher,
    )
    check(
        "Cypher references cgi_lithology_uri property",
        "cgi_lithology_uri" in cypher,
    )
    check(
        "Cypher references coverage_pct in RETURN clause",
        "coverage_pct" in cypher,
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 65)
    total_tests = passed + failed
    print(f"Results: {passed}/{total_tests} passed, {failed} failed")
    if failed > 0:
        print("Some tests FAILED — review output above.")
        sys.exit(1)
    else:
        print("All tests passed.")
