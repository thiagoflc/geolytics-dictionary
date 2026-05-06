"""Semantic pressure classification for SPE Volve PressurePoint nodes.

Classifies 76 340 PressurePoint nodes from the Volve Neo4j graph into formal
geomechanical vocabulary: pore-pressure regimes (subnormal / normal /
mild-overpressure / moderate-overpressure / severe-overpressure) and mud-window
classes (tight / narrow / normal / wide), following GEOMEC001 and GEOMEC003
from the Petrobras Corporate Geomechanics Ontology (v1.5.0) and the North Sea
Volve field stratigraphy (Hugin / Draupne / evaporite).

Ontology anchors
----------------
GEOMEC001  Pore Pressure (Pp)                  — standard unit ppg (lb/gal)
GEOMEC002  Minimum Horizontal Stress / FG       — defines upper mud-window bound
GEOMEC003  Operational Mud-Weight Window        — bounded by collapse GF and FG
GEOMEC019  ECD                                 — must stay inside window
Sources: PE-2RES-00009, PP-2E&P-00322, Fjaer et al. 2008, Zoback 2010.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. PRESSURE_REGIME_THRESHOLDS
# ---------------------------------------------------------------------------
# EMW limits in ppg (lb/gal).
# Anchored to GEOMEC001 — Pressão de Poros (Pp).
# Normal hydrostatic gradient for seawater ≈ 8.5–8.7 ppg.
# North Sea typical hydrostatic: 8.6 ppg (Volve field).
# Ranges follow Fjaer et al. 2008 §2.4 and Zoback 2010 §2.2.
PRESSURE_REGIME_THRESHOLDS: dict[str, dict[str, Any]] = {
    "subnormal": {
        "min_emw": 0.0,
        "max_emw": 8.5,
        "label": "subnormal",
        "description": (
            "Pore pressure below hydrostatic gradient. Common in depleted reservoirs "
            "or well-drained aquifers. Drilling risk: potential formation damage from "
            "excessive overbalance and lost circulation."
        ),
    },
    "normal_pore_pressure": {
        "min_emw": 8.5,
        "max_emw": 9.2,
        "label": "normal",
        "description": (
            "Pore pressure in normal hydrostatic range for seawater column "
            "(~8.5–9.2 ppg). Volve Hugin reservoir sands typically fall here at "
            "target depth. Standard mud-weight design applies."
        ),
    },
    "mild_overpressure": {
        "min_emw": 9.2,
        "max_emw": 10.5,
        "label": "mild_overpressure",
        "description": (
            "Mild geopressure above hydrostatic. Often caused by compaction "
            "disequilibrium or lateral stress transfer. Mud weight must be raised "
            "carefully to avoid fracturing. Draupne shale transitions may show this."
        ),
    },
    "moderate_overpressure": {
        "min_emw": 10.5,
        "max_emw": 12.0,
        "label": "moderate_overpressure",
        "description": (
            "Moderate overpressure. Mud-window typically narrows significantly. "
            "MPD or staged casing design may be required. Associated with "
            "under-compacted shales or sealed compartments."
        ),
    },
    "severe_overpressure": {
        "min_emw": 12.0,
        "max_emw": 20.0,
        "label": "severe_overpressure",
        "description": (
            "Severe geopressure — mud weight approaches fracture gradient. "
            "High kick and blowout risk. Managed Pressure Drilling (GEOMEC020 / MPD) "
            "is typically required. Well-control procedures must be reviewed."
        ),
    },
}

# ---------------------------------------------------------------------------
# 2. MUD_WINDOW_CLASSIFICATION
# ---------------------------------------------------------------------------
# Window = frac_gradient_emw − pore_pressure_emw  (ppg).
# Anchored to GEOMEC003 — Janela Operacional de Lama.
# Lower bound: collapse gradient (or Pp as conservative proxy here).
# Upper bound: fracture gradient (Shmin / S3, GEOMEC002).
MUD_WINDOW_CLASSIFICATION: dict[str, dict[str, Any]] = {
    "tight": {
        "window_ppg": (0.0, 0.5),
        "risk": "high",
        "note": (
            "Tight mud window — risk of lost circulation if overbalanced, "
            "influx/kick if underbalanced. MPD or continuous ECD monitoring required "
            "(GEOMEC019). Equivalent to janela operacional estreita in Petrobras "
            "standard PE-2RES-00009."
        ),
    },
    "narrow": {
        "window_ppg": (0.5, 1.5),
        "risk": "medium",
        "note": (
            "Narrow mud window. Standard overbalance margins are reduced. "
            "Careful ECD management required; avoid excessive surge/swab. "
            "Typical for Draupne shale overburden in Volve."
        ),
    },
    "normal": {
        "window_ppg": (1.5, 3.0),
        "risk": "low",
        "note": (
            "Normal mud window. Adequate margin for conventional drilling. "
            "Standard overbalance (100–200 psi) is achievable without fracturing. "
            "Hugin reservoir sands in Volve typically exhibit this window."
        ),
    },
    "wide": {
        "window_ppg": (3.0, 99.0),
        "risk": "very_low",
        "note": (
            "Wide mud window. Large operating margin. Possible in shallow sections, "
            "subnormal-pressure zones, or highly competent formations. "
            "Verify data integrity if window exceeds 5 ppg."
        ),
    },
}

# ---------------------------------------------------------------------------
# 3. VOLVE_KNOWN_PRESSURE_ZONES
# ---------------------------------------------------------------------------
# Field: Volve, North Sea (Norwegian sector, block 15/9).
# Reference: SPE-Volve open dataset; Equinor field geology reports.
# Depths are approximate TVD below mudline (TVDML) in metres.
VOLVE_KNOWN_PRESSURE_ZONES: dict[str, dict[str, Any]] = {
    "hugin_fm": {
        "formation": "Hugin Formation",
        "age": "Middle Jurassic",
        "lithology": "Fluvial-deltaic sandstone",
        "tvd_range_m": (3050, 3350),
        "expected_pp_regime": "normal",
        "expected_pp_emw_range": (8.6, 9.2),
        "expected_mud_window": "normal",
        "notes": (
            "Main reservoir at Volve. Normal hydrostatic pore pressure. "
            "Good-quality sandstone with porosities 15–25%. "
            "Frac gradient ~12–13 ppg at target depth; mud window 3–4 ppg. "
            "Risk of compartmentalisation causing local depletion sub-zones."
        ),
    },
    "draupne_fm": {
        "formation": "Draupne Formation (Kimmeridge Clay equivalent)",
        "age": "Late Jurassic",
        "lithology": "Organic-rich marine shale",
        "tvd_range_m": (2800, 3060),
        "expected_pp_regime": "mild_overpressure",
        "expected_pp_emw_range": (9.0, 10.5),
        "expected_mud_window": "narrow",
        "notes": (
            "Supra-reservoir caprock shale. Source rock with high TOC. "
            "Compaction-disequilibrium overpressure expected. "
            "Mud window can narrow to <1.5 ppg — careful transition required "
            "when drilling from Draupne into Hugin. "
            "Wellbore stability risk: breakouts (GEOMEC023) in anisotropic shale."
        ),
    },
    "evaporite_zone": {
        "formation": "Zechstein Evaporites / Salt sequences",
        "age": "Permian",
        "lithology": "Halite, anhydrite, carnallite",
        "tvd_range_m": (1200, 2500),
        "expected_pp_regime": "normal",
        "expected_pp_emw_range": (9.0, 10.0),
        "expected_mud_window": "tight",
        "notes": (
            "Salt and evaporite sequences exhibit time-dependent creep (GEOMEC021 / APB). "
            "In situ horizontal stresses converge toward overburden (Sv) in halite: "
            "SH ≈ Sh ≈ Sv (lithostatic regime). Mud weight must approach overburden "
            "gradient to minimise creep closure (PE-2RES-00009). "
            "Fracture gradient equals overburden gradient — mud window is effectively "
            "controlled by creep tolerance rather than hydraulic fracturing. "
            "Salt welds and stringers (anhydrite) create abrupt pressure transitions."
        ),
    },
    "utsira_fm_shallow": {
        "formation": "Utsira / Skade Sands (shallow aquifer)",
        "age": "Miocene–Pliocene",
        "lithology": "Unconsolidated sand",
        "tvd_range_m": (200, 900),
        "expected_pp_regime": "normal",
        "expected_pp_emw_range": (8.5, 8.9),
        "expected_mud_window": "wide",
        "notes": (
            "Shallow CO₂ storage aquifer and unconsolidated sand. "
            "Normal hydrostatic gradient. Low fracture gradient in shallow section. "
            "Wide mud window but low fracture resistance — avoid surge pressures."
        ),
    },
}

# ---------------------------------------------------------------------------
# 4. classify_pressure_point
# ---------------------------------------------------------------------------

def classify_pressure_point(
    tvd_m: float | None,
    pore_pressure_emw: float | None,
    frac_gradient_emw: float | None,
    is_permeable: str | None = None,
) -> dict[str, Any]:
    """Classify a single PressurePoint into pressure regime and mud-window class.

    Parameters
    ----------
    tvd_m:
        True vertical depth in metres. Used for formation-zone context notes.
    pore_pressure_emw:
        Pore pressure expressed as equivalent mud weight in ppg (lb/gal).
        None or non-positive values are treated as missing.
    frac_gradient_emw:
        Fracture gradient (minimum horizontal stress proxy) in ppg.
        None or non-positive values are treated as missing.
    is_permeable:
        String flag from the PressurePoint node ("true"/"false"/None).
        Informs the geomechanic note.

    Returns
    -------
    dict with keys:
        pore_pressure_regime : str  — one of the PRESSURE_REGIME_THRESHOLDS labels
        mud_window_class     : str  — one of the MUD_WINDOW_CLASSIFICATION keys
        mud_window_ppg       : float — frac_gradient_emw − pore_pressure_emw
        drilling_risk        : str  — from MUD_WINDOW_CLASSIFICATION risk field
        geomechanic_note     : str  — human-readable explanatory string
    """
    # --- Guard: missing or invalid pore pressure ---
    pp = _safe_float(pore_pressure_emw)
    fg = _safe_float(frac_gradient_emw)
    depth = _safe_float(tvd_m)
    permeable = _parse_permeable(is_permeable)

    if pp is None or pp <= 0.0:
        return {
            "pore_pressure_regime": "unknown",
            "mud_window_class": "unknown",
            "mud_window_ppg": None,
            "drilling_risk": "unknown",
            "geomechanic_note": "Pore pressure EMW is missing or zero — classification skipped.",
        }

    # --- Classify pore-pressure regime ---
    regime_key = _classify_regime(pp)
    regime = PRESSURE_REGIME_THRESHOLDS[regime_key]

    # --- Classify mud window ---
    if fg is None or fg <= 0.0:
        mud_class_key = "unknown"
        mud_window_ppg = None
        risk = "unknown"
        window_note = "Fracture gradient missing — mud window cannot be computed."
    else:
        mud_window_ppg = round(fg - pp, 3)
        if mud_window_ppg < 0.0:
            # Inverted window: Pp > FG — physically anomalous or data error
            mud_class_key = "inverted"
            risk = "critical"
            window_note = (
                f"INVERTED mud window ({mud_window_ppg:.2f} ppg): pore pressure "
                f"({pp:.2f} ppg) exceeds fracture gradient ({fg:.2f} ppg). "
                "Possible data error or catastrophic overpressure condition — "
                "verify raw data before use."
            )
        else:
            mud_class_key = _classify_mud_window(mud_window_ppg)
            mud_cls = MUD_WINDOW_CLASSIFICATION[mud_class_key]
            risk = mud_cls["risk"]
            window_note = mud_cls["note"]

    # --- Build geomechanic note ---
    note_parts = [
        f"Pp = {pp:.2f} ppg ({regime['label']}). ",
        regime["description"],
        " | ",
        window_note,
    ]

    # Formation context from depth
    zone_hint = _get_zone_hint(depth)
    if zone_hint:
        note_parts.append(f" | Formation context: {zone_hint}")

    # Permeability qualifier
    if permeable is True:
        note_parts.append(
            " | Permeable zone: pore pressure is directly communicated — "
            "formation test data is likely reliable."
        )
    elif permeable is False:
        note_parts.append(
            " | Non-permeable zone: Pp may be inferred/extrapolated — "
            "treat with higher uncertainty."
        )

    return {
        "pore_pressure_regime": regime["label"],
        "mud_window_class": mud_class_key,
        "mud_window_ppg": mud_window_ppg,
        "drilling_risk": risk,
        "geomechanic_note": "".join(note_parts),
    }


# ---------------------------------------------------------------------------
# 5. classify_wellbore_pressure_profile
# ---------------------------------------------------------------------------

def classify_wellbore_pressure_profile(pressure_points: list[dict]) -> dict[str, Any]:
    """Analyse the full pressure profile of a wellbore.

    Parameters
    ----------
    pressure_points:
        List of dicts, each representing a PressurePoint node with keys:
        tvd_m, pore_pressure_emw, frac_gradient_emw, is_permeable.

    Returns
    -------
    dict with keys:
        overall_risk      : str   — worst-case risk across all points
        critical_zones    : list[dict]  — tight/inverted intervals (tvd_m, details)
        avg_mud_window    : float — mean mud window in ppg (valid points only)
        max_pore_pressure_emw : float — maximum Pp EMW seen in the wellbore
    """
    if not pressure_points:
        return {
            "overall_risk": "unknown",
            "critical_zones": [],
            "avg_mud_window": None,
            "max_pore_pressure_emw": None,
        }

    _risk_rank = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "critical": 4, "unknown": -1}

    classified = []
    for pt in pressure_points:
        result = classify_pressure_point(
            tvd_m=pt.get("tvd_m"),
            pore_pressure_emw=pt.get("pore_pressure_emw"),
            frac_gradient_emw=pt.get("frac_gradient_emw"),
            is_permeable=pt.get("is_permeable"),
        )
        classified.append({"point": pt, "classification": result})

    # Worst-case overall risk
    worst_risk = "unknown"
    worst_rank = -1
    for item in classified:
        r = item["classification"]["drilling_risk"]
        rank = _risk_rank.get(r, -1)
        if rank > worst_rank:
            worst_rank = rank
            worst_risk = r

    # Critical zones: tight or inverted windows, or severe overpressure
    critical_zones: list[dict] = []
    for item in classified:
        cls = item["classification"]
        pt = item["point"]
        if cls["drilling_risk"] in ("high", "critical") or cls["mud_window_class"] == "inverted":
            critical_zones.append(
                {
                    "tvd_m": pt.get("tvd_m"),
                    "pore_pressure_emw": pt.get("pore_pressure_emw"),
                    "frac_gradient_emw": pt.get("frac_gradient_emw"),
                    "mud_window_ppg": cls["mud_window_ppg"],
                    "mud_window_class": cls["mud_window_class"],
                    "pore_pressure_regime": cls["pore_pressure_regime"],
                    "drilling_risk": cls["drilling_risk"],
                    "geomechanic_note": cls["geomechanic_note"],
                }
            )

    # Sort critical zones by TVD ascending
    critical_zones.sort(key=lambda z: (z["tvd_m"] is None, z["tvd_m"] or 0))

    # Average mud window (valid numeric values only)
    valid_windows = [
        item["classification"]["mud_window_ppg"]
        for item in classified
        if isinstance(item["classification"]["mud_window_ppg"], float)
        and item["classification"]["mud_window_ppg"] >= 0.0
    ]
    avg_window = round(sum(valid_windows) / len(valid_windows), 3) if valid_windows else None

    # Max pore pressure
    valid_pp = [
        pt.get("pore_pressure_emw")
        for pt in pressure_points
        if isinstance(pt.get("pore_pressure_emw"), (int, float))
        and pt["pore_pressure_emw"] > 0
    ]
    max_pp = round(max(valid_pp), 3) if valid_pp else None

    return {
        "overall_risk": worst_risk,
        "critical_zones": critical_zones,
        "avg_mud_window": avg_window,
        "max_pore_pressure_emw": max_pp,
    }


# ---------------------------------------------------------------------------
# 6. build_enrichment_cypher
# ---------------------------------------------------------------------------

def build_enrichment_cypher() -> str:
    """Return the Cypher statement that sets pressure classification properties.

    The query:
    - Matches each PressurePoint with valid EMW data.
    - Computes mud_window_ppg inline.
    - Sets pressure_regime, mud_window_class, and drilling_risk.
    - Uses a CASE expression for regime and window class to avoid
      Python UDF overhead on 76 k nodes.
    - Designed for idempotent re-runs (SET overwrites).

    Usage
    -----
    Run via ``run_classification`` or directly in Neo4j Browser / cypher-shell.
    """
    return """\
MATCH (p:PressurePoint)
WHERE p.pore_pressure_emw IS NOT NULL
  AND p.pore_pressure_emw > 0
  AND p.frac_gradient_emw IS NOT NULL
  AND p.frac_gradient_emw > 0
WITH p,
     p.pore_pressure_emw   AS pp,
     p.frac_gradient_emw   AS fg,
     p.frac_gradient_emw - p.pore_pressure_emw AS window_ppg

// --- pressure regime ---
WITH p, pp, fg, window_ppg,
     CASE
       WHEN pp < 8.5  THEN 'subnormal'
       WHEN pp < 9.2  THEN 'normal'
       WHEN pp < 10.5 THEN 'mild_overpressure'
       WHEN pp < 12.0 THEN 'moderate_overpressure'
       ELSE                'severe_overpressure'
     END AS pressure_regime,

// --- mud window class ---
     CASE
       WHEN window_ppg < 0.0 THEN 'inverted'
       WHEN window_ppg < 0.5 THEN 'tight'
       WHEN window_ppg < 1.5 THEN 'narrow'
       WHEN window_ppg < 3.0 THEN 'normal'
       ELSE                       'wide'
     END AS mud_window_class,

// --- drilling risk ---
     CASE
       WHEN window_ppg < 0.0 THEN 'critical'
       WHEN window_ppg < 0.5 THEN 'high'
       WHEN window_ppg < 1.5 THEN 'medium'
       WHEN window_ppg < 3.0 THEN 'low'
       ELSE                       'very_low'
     END AS drilling_risk

SET p.pressure_regime  = pressure_regime,
    p.mud_window_class = mud_window_class,
    p.mud_window_ppg   = round(window_ppg * 1000) / 1000.0,
    p.drilling_risk    = drilling_risk
"""


# ---------------------------------------------------------------------------
# 7. run_classification
# ---------------------------------------------------------------------------

def run_classification(driver: Any, batch_size: int = 1000) -> dict[str, Any]:
    """Execute batch classification on all PressurePoint nodes.

    Attempts to use ``apoc.periodic.iterate`` for server-side batching
    (preferred — avoids pulling 76 k rows over the wire).  Falls back to
    Python-driven batched SKIP/LIMIT if APOC is unavailable.

    Parameters
    ----------
    driver:
        ``neo4j.GraphDatabase`` driver instance (already authenticated).
    batch_size:
        Number of nodes per commit batch.  Default 1 000.

    Returns
    -------
    dict with:
        total_processed : int
        stats_by_regime : dict[str, int]  — count per pressure_regime label
        stats_by_risk   : dict[str, int]  — count per drilling_risk label
        batches         : int
        apoc_used       : bool
    """
    log.info("Starting PressurePoint classification. batch_size=%d", batch_size)

    enrichment_cypher = build_enrichment_cypher()
    apoc_used = _apoc_available(driver)

    if apoc_used:
        _run_with_apoc(driver, enrichment_cypher, batch_size)
    else:
        _run_with_python_batches(driver, enrichment_cypher, batch_size)

    stats = _collect_stats(driver)
    log.info("Classification complete. stats=%s", stats)
    return stats


def _apoc_available(driver: Any) -> bool:
    """Return True if the APOC plugin is present in the Neo4j instance."""
    try:
        with driver.session() as session:
            result = session.run(
                "RETURN apoc.version() AS v"
            )
            result.single()
            return True
    except Exception:  # noqa: BLE001
        return False


def _run_with_apoc(driver: Any, inner_query: str, batch_size: int) -> None:
    """Use apoc.periodic.iterate for efficient server-side batching."""
    # apoc.periodic.iterate expects two query strings:
    # 1. a query that yields the nodes to iterate over
    # 2. the update query operating on each node
    iterate_query = (
        "MATCH (p:PressurePoint) "
        "WHERE p.pore_pressure_emw IS NOT NULL AND p.pore_pressure_emw > 0 "
        "  AND p.frac_gradient_emw IS NOT NULL AND p.frac_gradient_emw > 0 "
        "RETURN p"
    )
    update_query = """\
WITH p,
     p.pore_pressure_emw AS pp,
     p.frac_gradient_emw - p.pore_pressure_emw AS window_ppg
SET p.pressure_regime = CASE
      WHEN pp < 8.5  THEN 'subnormal'
      WHEN pp < 9.2  THEN 'normal'
      WHEN pp < 10.5 THEN 'mild_overpressure'
      WHEN pp < 12.0 THEN 'moderate_overpressure'
      ELSE                'severe_overpressure'
    END,
    p.mud_window_class = CASE
      WHEN window_ppg < 0.0 THEN 'inverted'
      WHEN window_ppg < 0.5 THEN 'tight'
      WHEN window_ppg < 1.5 THEN 'narrow'
      WHEN window_ppg < 3.0 THEN 'normal'
      ELSE                       'wide'
    END,
    p.mud_window_ppg = round(window_ppg * 1000) / 1000.0,
    p.drilling_risk = CASE
      WHEN window_ppg < 0.0 THEN 'critical'
      WHEN window_ppg < 0.5 THEN 'high'
      WHEN window_ppg < 1.5 THEN 'medium'
      WHEN window_ppg < 3.0 THEN 'low'
      ELSE                       'very_low'
    END
"""
    apoc_cypher = (
        "CALL apoc.periodic.iterate($iterate_q, $update_q, "
        "{batchSize: $batch_size, parallel: false, iterateList: true}) "
        "YIELD batches, total, errorMessages "
        "RETURN batches, total, errorMessages"
    )
    with driver.session() as session:
        result = session.run(
            apoc_cypher,
            iterate_q=iterate_query,
            update_q=update_query,
            batch_size=batch_size,
        )
        summary = result.single()
        if summary and summary["errorMessages"]:
            log.warning("APOC errors: %s", summary["errorMessages"])
        log.info(
            "APOC run complete. batches=%s total=%s",
            summary["batches"] if summary else "?",
            summary["total"] if summary else "?",
        )


def _run_with_python_batches(driver: Any, cypher: str, batch_size: int) -> None:
    """Fallback: Python-driven batching when APOC is unavailable.

    Uses a filter-and-mark approach: each batch selects the next LIMIT unclassified
    nodes (pressure_regime IS NULL with valid EMW values), classifies them, then the
    next iteration naturally picks up the remaining unclassified nodes without SKIP.
    This avoids the SKIP/LIMIT pagination bug where shrinking filtered sets cause nodes
    to be skipped when a static total count is used as the loop bound.
    """
    count_q = (
        "MATCH (p:PressurePoint) "
        "WHERE p.pore_pressure_emw IS NOT NULL AND p.pore_pressure_emw > 0 "
        "  AND p.frac_gradient_emw IS NOT NULL AND p.frac_gradient_emw > 0 "
        "  AND p.pressure_regime IS NULL "
        "RETURN count(p) AS n"
    )
    count_result = _run_single_query(driver, count_q)
    total = count_result[0]["n"] if count_result else 0
    log.info("Python-batch mode. eligible nodes=%d batch_size=%d", total, batch_size)

    if total == 0:
        return

    processed = 0
    while True:
        batch_cypher = (
            "MATCH (p:PressurePoint) "
            "WHERE p.pore_pressure_emw IS NOT NULL AND p.pore_pressure_emw > 0 "
            "  AND p.frac_gradient_emw IS NOT NULL AND p.frac_gradient_emw > 0 "
            "  AND p.pressure_regime IS NULL "
            f"LIMIT {batch_size} "
            "WITH p, "
            "     p.pore_pressure_emw AS pp, "
            "     p.frac_gradient_emw - p.pore_pressure_emw AS window_ppg "
            "SET p.pressure_regime = CASE "
            "      WHEN pp < 8.5  THEN 'subnormal' "
            "      WHEN pp < 9.2  THEN 'normal' "
            "      WHEN pp < 10.5 THEN 'mild_overpressure' "
            "      WHEN pp < 12.0 THEN 'moderate_overpressure' "
            "      ELSE                'severe_overpressure' "
            "    END, "
            "    p.mud_window_class = CASE "
            "      WHEN window_ppg < 0.0 THEN 'inverted' "
            "      WHEN window_ppg < 0.5 THEN 'tight' "
            "      WHEN window_ppg < 1.5 THEN 'narrow' "
            "      WHEN window_ppg < 3.0 THEN 'normal' "
            "      ELSE                       'wide' "
            "    END, "
            "    p.mud_window_ppg = round(window_ppg * 1000) / 1000.0, "
            "    p.drilling_risk = CASE "
            "      WHEN window_ppg < 0.0 THEN 'critical' "
            "      WHEN window_ppg < 0.5 THEN 'high' "
            "      WHEN window_ppg < 1.5 THEN 'medium' "
            "      WHEN window_ppg < 3.0 THEN 'low' "
            "      ELSE                       'very_low' "
            "    END "
        )
        with driver.session() as session:
            summary = session.run(batch_cypher).consume()
        if summary.counters.properties_set == 0:
            break
        processed += batch_size
        log.debug("Processed ~%d / %d nodes", min(processed, total), total)


def _collect_stats(driver: Any) -> dict[str, Any]:
    """Aggregate classification stats from the graph after enrichment."""
    regime_rows = _run_single_query(
        driver,
        "MATCH (p:PressurePoint) WHERE p.pressure_regime IS NOT NULL "
        "RETURN p.pressure_regime AS regime, count(p) AS n ORDER BY n DESC",
    )
    risk_rows = _run_single_query(
        driver,
        "MATCH (p:PressurePoint) WHERE p.drilling_risk IS NOT NULL "
        "RETURN p.drilling_risk AS risk, count(p) AS n ORDER BY n DESC",
    )
    total = _run_single_query(
        driver,
        "MATCH (p:PressurePoint) RETURN count(p) AS n",
    )
    return {
        "total_processed": total[0]["n"] if total else 0,
        "stats_by_regime": {row["regime"]: row["n"] for row in regime_rows},
        "stats_by_risk": {row["risk"]: row["n"] for row in risk_rows},
        "apoc_used": _apoc_available(driver),
    }


def _run_single_query(driver: Any, cypher: str) -> list[dict]:
    with driver.session() as session:
        result = session.run(cypher)
        return [dict(record) for record in result]


# ---------------------------------------------------------------------------
# 8. generate_pressure_report
# ---------------------------------------------------------------------------

def generate_pressure_report(driver: Any, wellbore_uid: str) -> str:
    """Generate a plain-text pressure profile report for a single wellbore.

    The report is suitable for injection into an LLM agent domain context
    (RAG / system prompt augmentation).

    Parameters
    ----------
    driver:
        Authenticated neo4j driver.
    wellbore_uid:
        Unique identifier of the wellbore (matches PressurePoint.wellbore_uid).

    Returns
    -------
    A multi-line string report.
    """
    rows = _run_single_query(
        driver,
        "MATCH (p:PressurePoint {wellbore_uid: $uid}) "
        "RETURN p.point_id AS point_id, p.tvd_m AS tvd_m, "
        "       p.pore_pressure_emw AS pp_emw, p.frac_gradient_emw AS fg_emw, "
        "       p.is_permeable AS is_permeable, p.data_type AS data_type, "
        "       p.pressure_regime AS regime, p.mud_window_class AS mw_class, "
        "       p.mud_window_ppg AS mw_ppg, p.drilling_risk AS risk "
        "ORDER BY p.tvd_m ASC",
    )
    if not rows:
        return (
            f"No PressurePoint data found for wellbore '{wellbore_uid}'. "
            "Ensure ingestion has run and wellbore_uid is correct."
        )

    # Build profile in memory for summary statistics
    points_raw = [
        {
            "tvd_m": r["tvd_m"],
            "pore_pressure_emw": r["pp_emw"],
            "frac_gradient_emw": r["fg_emw"],
            "is_permeable": r["is_permeable"],
        }
        for r in rows
    ]
    # If classification properties not yet set, classify on-the-fly
    need_classify = any(r["regime"] is None for r in rows)
    if need_classify:
        profile = classify_wellbore_pressure_profile(points_raw)
    else:
        # Re-derive from stored values for report consistency
        profile = classify_wellbore_pressure_profile(points_raw)

    lines: list[str] = [
        "=" * 72,
        f"PRESSURE PROFILE REPORT — Wellbore: {wellbore_uid}",
        "=" * 72,
        f"Total pressure points : {len(rows)}",
        f"TVD range             : "
        f"{_safe_min(r['tvd_m'] for r in rows):.1f} — "
        f"{_safe_max(r['tvd_m'] for r in rows):.1f} m",
        f"Max Pp EMW            : {profile['max_pore_pressure_emw']} ppg",
        f"Avg mud window        : {profile['avg_mud_window']} ppg",
        f"Overall drilling risk : {profile['overall_risk'].upper()}",
        "",
    ]

    # Regime distribution
    regime_counts: dict[str, int] = {}
    for r in rows:
        reg = r["regime"] or "unclassified"
        regime_counts[reg] = regime_counts.get(reg, 0) + 1
    lines.append("Pore-pressure regime distribution:")
    for reg, cnt in sorted(regime_counts.items(), key=lambda x: -x[1]):
        pct = 100.0 * cnt / len(rows)
        lines.append(f"  {reg:<28s} {cnt:>6d} pts  ({pct:.1f}%)")
    lines.append("")

    # Mud window distribution
    mw_counts: dict[str, int] = {}
    for r in rows:
        mw = r["mw_class"] or "unclassified"
        mw_counts[mw] = mw_counts.get(mw, 0) + 1
    lines.append("Mud-window class distribution:")
    for mw, cnt in sorted(mw_counts.items(), key=lambda x: -x[1]):
        pct = 100.0 * cnt / len(rows)
        lines.append(f"  {mw:<28s} {cnt:>6d} pts  ({pct:.1f}%)")
    lines.append("")

    # Critical zones
    if profile["critical_zones"]:
        lines.append(f"Critical zones ({len(profile['critical_zones'])} high-risk intervals):")
        for z in profile["critical_zones"][:20]:  # cap at 20 for readability
            tvd = z["tvd_m"]
            lines.append(
                f"  TVD {tvd:>7.1f} m | "
                f"Pp {z['pore_pressure_emw']:.2f} ppg | "
                f"FG {z['frac_gradient_emw']:.2f} ppg | "
                f"Window {z['mud_window_ppg']:.2f} ppg | "
                f"Risk: {z['drilling_risk']}"
            )
        if len(profile["critical_zones"]) > 20:
            lines.append(f"  ... and {len(profile['critical_zones']) - 20} more critical points.")
    else:
        lines.append("No high-risk (tight/inverted) mud-window zones detected.")
    lines.append("")

    # Volve formation context
    lines.append("Volve formation context (depth-based):")
    for zone_key, zone in VOLVE_KNOWN_PRESSURE_ZONES.items():
        z_min, z_max = zone["tvd_range_m"]
        pts_in_zone = [r for r in rows if r["tvd_m"] and z_min <= r["tvd_m"] <= z_max]
        if pts_in_zone:
            pp_in_zone = [
                r["pp_emw"] for r in pts_in_zone if r["pp_emw"] and r["pp_emw"] > 0
            ]
            avg_pp = round(sum(pp_in_zone) / len(pp_in_zone), 3) if pp_in_zone else None
            lines.append(
                f"  {zone['formation']:<42s} "
                f"{len(pts_in_zone):>4d} pts | avg Pp {avg_pp} ppg | "
                f"expected: {zone['expected_pp_regime']}"
            )
    lines.append("")

    lines.append(
        "Ontology anchors: GEOMEC001 (Pp), GEOMEC002 (FG/Shmin), "
        "GEOMEC003 (Mud Window), GEOMEC019 (ECD)."
    )
    lines.append("=" * 72)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _safe_float(value: Any) -> float | None:
    """Convert to float, returning None if conversion fails."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_permeable(value: Any) -> bool | None:
    """Parse the is_permeable string field."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None


def _classify_regime(pp_emw: float) -> str:
    """Return the PRESSURE_REGIME_THRESHOLDS key for a given Pp EMW value."""
    for key, cfg in PRESSURE_REGIME_THRESHOLDS.items():
        if cfg["min_emw"] <= pp_emw < cfg["max_emw"]:
            return key
    # Fallback: clamp to severe overpressure if EMW >= 20
    return "severe_overpressure"


def _classify_mud_window(window_ppg: float) -> str:
    """Return the MUD_WINDOW_CLASSIFICATION key for a given window width."""
    for key, cfg in MUD_WINDOW_CLASSIFICATION.items():
        lo, hi = cfg["window_ppg"]
        if lo <= window_ppg < hi:
            return key
    return "wide"


def _get_zone_hint(tvd_m: float | None) -> str | None:
    """Return a formation hint string based on TVD depth."""
    if tvd_m is None:
        return None
    for zone in VOLVE_KNOWN_PRESSURE_ZONES.values():
        z_min, z_max = zone["tvd_range_m"]
        if z_min <= tvd_m <= z_max:
            return f"{zone['formation']} ({zone['lithology']})"
    return None


def _safe_min(iterable: Any) -> float:
    vals = [v for v in iterable if v is not None]
    return min(vals) if vals else 0.0


def _safe_max(iterable: Any) -> float:
    vals = [v for v in iterable if v is not None]
    return max(vals) if vals else 0.0


# ---------------------------------------------------------------------------
# 9. __main__ — tests covering all regimes and edge cases
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    _PASS = "\033[32mPASS\033[0m"
    _FAIL = "\033[31mFAIL\033[0m"

    failures: list[str] = []

    def _check(label: str, got: Any, expected: Any) -> None:
        ok = got == expected
        status = _PASS if ok else _FAIL
        print(f"  [{status}] {label}: got={got!r}  expected={expected!r}")
        if not ok:
            failures.append(label)

    # ------------------------------------------------------------------
    # Test data: 30 PressurePoints covering all regimes and edge cases
    # ------------------------------------------------------------------
    # Format: (description, tvd_m, pp_emw, fg_emw, is_permeable,
    #          expected_regime, expected_mud_class, expected_risk)
    #
    # Mud-window boundaries (ppg):  tight [0, 0.5)  narrow [0.5, 1.5)
    #                                normal [1.5, 3.0)  wide [3.0, 99)
    # Pressure regime boundaries:   subnormal [0, 8.5)  normal [8.5, 9.2)
    #   mild_overpressure [9.2, 10.5)  moderate [10.5, 12.0)  severe [12.0, 20)
    TEST_CASES: list[tuple] = [
        # --- Subnormal ---
        # pp=7.5  fg=11.0  window=3.5  → wide
        ("Subnormal — depleted reservoir",          3100.0,  7.5, 11.0, "true",  "subnormal",             "wide",    "very_low"),
        # pp=8.49 fg=11.5  window=3.01 → wide
        ("Subnormal — boundary 8.49",               3200.0,  8.49, 11.5, "false", "subnormal",             "wide",    "very_low"),
        # pp=8.0  fg=8.4   window=0.4  → tight
        ("Subnormal — tight window",                3050.0,  8.0,  8.4, "true",  "subnormal",             "tight",   "high"),
        # --- Normal ---
        # pp=8.6  fg=12.0  window=3.4  → wide
        ("Normal — Hugin typical",                  3150.0,  8.6, 12.0, "true",  "normal",                "wide",    "very_low"),
        # pp=8.5  fg=10.5  window=2.0  → normal
        ("Normal — boundary 8.5 exact",             3100.0,  8.5, 10.5, "true",  "normal",                "normal",  "low"),
        # pp=9.0  fg=9.8   window=0.8  → narrow
        ("Normal — narrow window",                  3200.0,  9.0,  9.8, "false", "normal",                "narrow",  "medium"),
        # pp=9.1  fg=9.4   window=0.3  → tight
        ("Normal — tight window",                   3300.0,  9.1,  9.4, "true",  "normal",                "tight",   "high"),
        # pp=9.19 fg=12.0  window=2.81 → normal [1.5, 3.0)
        ("Normal — boundary 9.19",                  3100.0,  9.19, 12.0, "true", "normal",                "normal",  "low"),
        # --- Mild overpressure ---
        # pp=9.5  fg=12.0  window=2.5  → normal [1.5, 3.0)
        ("Mild overpressure — Draupne typical",     2900.0,  9.5, 12.0, "false", "mild_overpressure",     "normal",  "low"),
        # pp=9.8  fg=11.0  window=1.2  → narrow [0.5, 1.5)
        ("Mild overpressure — narrow window",       2950.0,  9.8, 11.0, "false", "mild_overpressure",     "narrow",  "medium"),
        # pp=10.2 fg=10.6  window=0.4  → tight [0, 0.5)
        ("Mild overpressure — tight window",        3000.0, 10.2, 10.6, "false", "mild_overpressure",     "tight",   "high"),
        # pp=9.2  fg=12.5  window=3.3  → wide
        ("Mild overpressure — boundary 9.2",        3000.0,  9.2, 12.5, "true",  "mild_overpressure",     "wide",    "very_low"),
        # pp=10.49 fg=13.0 window=2.51 → normal [1.5, 3.0)
        ("Mild overpressure — boundary 10.49",      2800.0, 10.49, 13.0, "false","mild_overpressure",     "normal",  "low"),
        # --- Moderate overpressure ---
        # pp=11.0 fg=14.5  window=3.5  → wide
        ("Moderate overpressure — normal window",   2500.0, 11.0, 14.5, "false", "moderate_overpressure", "wide",    "very_low"),
        # pp=11.5 fg=12.8  window=1.3  → narrow
        ("Moderate overpressure — narrow window",   2600.0, 11.5, 12.8, "false", "moderate_overpressure", "narrow",  "medium"),
        # pp=11.9 fg=12.3  window=0.4  → tight
        ("Moderate overpressure — tight",           2700.0, 11.9, 12.3, "false", "moderate_overpressure", "tight",   "high"),
        # pp=10.5 fg=13.5  window=3.0  → wide (3.0 maps to wide: [3.0, 99))
        ("Moderate overpressure — boundary 10.5",   2800.0, 10.5, 13.5, "true",  "moderate_overpressure", "wide",    "very_low"),
        # --- Severe overpressure ---
        # pp=13.0 fg=16.5  window=3.5  → wide
        ("Severe overpressure — wide window",       2000.0, 13.0, 16.5, "false", "severe_overpressure",   "wide",    "very_low"),
        # pp=14.5 fg=14.9  window=0.4  → tight
        ("Severe overpressure — tight window",      2200.0, 14.5, 14.9, "false", "severe_overpressure",   "tight",   "high"),
        # pp=12.0 fg=15.0  window=3.0  → wide (boundary: [3.0, 99))
        ("Severe overpressure — boundary 12.0",     2400.0, 12.0, 15.0, "false", "severe_overpressure",   "wide",    "very_low"),
        # pp=18.5 fg=19.0  window=0.5  → narrow [0.5, 1.5) — 0.5 is lower bound of narrow
        ("Severe overpressure — very high EMW",     1800.0, 18.5, 19.0, "false", "severe_overpressure",   "narrow",  "medium"),
        # --- Edge cases ---
        # pp=12.5 fg=11.0  window=-1.5 → inverted
        ("Inverted window — Pp > FG",               3000.0, 12.5, 11.0, "false", "severe_overpressure",   "inverted","critical"),
        # pp=0.0 → unknown
        ("Zero pore pressure",                      3100.0,  0.0, 12.0, "true",  "unknown",               "unknown", "unknown"),
        # pp=None → unknown
        ("Null pore pressure",                      3100.0, None, 12.0, "true",  "unknown",               "unknown", "unknown"),
        # fg=None → regime classified, window unknown
        ("Null frac gradient",                      3100.0,  9.0, None, "true",  "normal",                "unknown", "unknown"),
        # tvd=None → regime and window still classify from EMW values
        ("Null depth",                              None,    9.0, 12.0, "true",  "normal",                "wide",    "very_low"),
        # is_permeable=None → result unchanged, permeability note omitted
        ("Null is_permeable",                       3100.0,  9.0, 12.0, None,    "normal",                "wide",    "very_low"),
        # pp=-1 → treated as missing
        ("Negative pore pressure",                  3000.0, -1.0, 12.0, "true",  "unknown",               "unknown", "unknown"),
        # pp=9.5 [9.2, 10.5) → mild_overpressure; window=0.4 → tight
        ("Evaporite zone — salt creep",             1800.0,  9.5,  9.9, "false", "mild_overpressure",     "tight",   "high"),
        # pp=8.7 [8.5, 9.2) → normal; window=2.8 → normal [1.5, 3.0)
        ("Utsira shallow aquifer",                   600.0,  8.7, 11.5, "true",  "normal",                "normal",  "low"),
    ]

    print("\n" + "=" * 72)
    print("pressure_classifier.py — unit tests (30 points)")
    print("=" * 72)

    for (desc, tvd, pp, fg, perm,
         exp_regime, exp_mw_class, exp_risk) in TEST_CASES:
        result = classify_pressure_point(tvd, pp, fg, perm)
        print(f"\nTest: {desc}")
        _check(
            "pore_pressure_regime",
            result["pore_pressure_regime"],
            exp_regime,
        )
        _check(
            "mud_window_class",
            result["mud_window_class"],
            exp_mw_class,
        )
        _check(
            "drilling_risk",
            result["drilling_risk"],
            exp_risk,
        )

    # --- Profile test ---
    print("\n" + "-" * 72)
    print("classify_wellbore_pressure_profile — integration test")
    print("-" * 72)

    profile_points = [
        {"tvd_m": tvd, "pore_pressure_emw": pp, "frac_gradient_emw": fg, "is_permeable": perm}
        for (_, tvd, pp, fg, perm, _, _, _) in TEST_CASES
    ]
    profile = classify_wellbore_pressure_profile(profile_points)
    print(f"  overall_risk          : {profile['overall_risk']}")
    print(f"  critical_zones count  : {len(profile['critical_zones'])}")
    print(f"  avg_mud_window        : {profile['avg_mud_window']} ppg")
    print(f"  max_pore_pressure_emw : {profile['max_pore_pressure_emw']} ppg")

    _check("overall_risk is critical",   profile["overall_risk"], "critical")
    _check("critical_zones > 0",         len(profile["critical_zones"]) > 0, True)
    _check("avg_mud_window not None",     profile["avg_mud_window"] is not None, True)
    _check("max_pore_pressure_emw > 12", profile["max_pore_pressure_emw"] > 12, True)

    # --- Cypher snippet smoke test ---
    print("\n" + "-" * 72)
    print("build_enrichment_cypher — smoke test (non-empty, contains SET)")
    print("-" * 72)
    cypher = build_enrichment_cypher()
    _check("cypher is str",     isinstance(cypher, str), True)
    _check("cypher has SET",    "SET" in cypher,         True)
    _check("cypher has CASE",   "CASE" in cypher,        True)
    _check("cypher mentions pressure_regime", "pressure_regime" in cypher, True)

    # --- Summary ---
    print("\n" + "=" * 72)
    if failures:
        print(f"RESULT: {len(failures)} FAILURE(S): {failures}")
    else:
        print("RESULT: ALL TESTS PASSED")
    print("=" * 72)
