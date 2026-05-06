"""Semantic enrichment of DrillingPhase nodes in the SPE Volve Neo4j graph.

Assigns to each DrillingPhase:
  - role_3w          — Petrobras 3W role: 'event_observation' | 'signal_concept'
  - iadc_class       — IADC canonical activity code
  - time_category    — 'productive_time' | 'non_productive_time' |
                       'invisible_lost_time'
  - npt              — bool
  - npt_severity     — None | 'low' | 'medium' | 'high' | 'critical'

References:
  Vargas R. et al. (2019). 3W Dataset: A Realistic and Public Dataset with
  Rare Undesirable Real Events in Oil Wells. Petrobras / SPE-195981-MS.

  IADC Drilling Manual, 13th Edition — Activity Classification System.

Public API:
    PHASE_TAXONOMY         — dict[str, dict]
    PRODUCTIVE_PHASES      — frozenset[str]
    NPT_PHASES             — frozenset[str]
    classify_phase(name, summary_text) -> dict
    run_enrichment(driver)             -> dict
    compute_npt_stats(driver, wellbore_uid) -> dict
"""

from __future__ import annotations

import logging
import re
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PHASE_TAXONOMY
# Mapping from Volve inferred phase name → semantic classification.
# Keys are the snake_case names produced by the regex inference pipeline.
# Minimum 40 phase types as required.
# ---------------------------------------------------------------------------
PHASE_TAXONOMY: dict[str, dict[str, Any]] = {
    # ------------------------------------------------------------------
    # DRILLING — forward progress
    # ------------------------------------------------------------------
    "drilling": {
        "role_3w": "event_observation",
        "iadc_class": "rotary_drilling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Active rotary or slide drilling forward, making hole.",
    },
    "rotary_drilling": {
        "role_3w": "event_observation",
        "iadc_class": "rotary_drilling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Rotary table or top drive turns the drill string to advance bit.",
    },
    "slide_drilling": {
        "role_3w": "event_observation",
        "iadc_class": "slide_drilling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Motor-only (non-rotating) slide drilling for directional control.",
    },
    "directional_drilling": {
        "role_3w": "event_observation",
        "iadc_class": "directional_drilling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Planned directional drilling to hit a target trajectory.",
    },
    "motor_drilling": {
        "role_3w": "event_observation",
        "iadc_class": "motor_drilling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Drilling with a positive displacement downhole motor (PDM).",
    },
    "rotary_steerable": {
        "role_3w": "event_observation",
        "iadc_class": "rotary_steerable_drilling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Drilling with a rotary steerable system (RSS) for directional control.",
    },
    "coring": {
        "role_3w": "event_observation",
        "iadc_class": "coring",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Cutting a formation core sample for geological analysis.",
    },
    "hole_opening": {
        "role_3w": "event_observation",
        "iadc_class": "hole_opening",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Enlarging an existing borehole to a larger diameter.",
    },
    "underreaming": {
        "role_3w": "event_observation",
        "iadc_class": "underreaming",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Opening the hole below casing shoe using an underreamer.",
    },

    # ------------------------------------------------------------------
    # TRIPPING — moving pipe in or out of the wellbore
    # ------------------------------------------------------------------
    "tripping": {
        "role_3w": "event_observation",
        "iadc_class": "tripping",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Generic tripping operation (direction not specified).",
    },
    "tripping_in": {
        "role_3w": "event_observation",
        "iadc_class": "tripping_in_hole",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Running drill string into the wellbore (RIH).",
    },
    "tripping_out": {
        "role_3w": "event_observation",
        "iadc_class": "pulling_out_of_hole",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Pulling drill string out of the wellbore (POOH).",
    },
    "rih": {
        "role_3w": "event_observation",
        "iadc_class": "tripping_in_hole",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Running In Hole — lowering drill string to bottom.",
    },
    "pooh": {
        "role_3w": "event_observation",
        "iadc_class": "pulling_out_of_hole",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Pulling Out Of Hole — retrieving drill string to surface.",
    },
    "wiper_trip": {
        "role_3w": "event_observation",
        "iadc_class": "wiper_trip",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Full wiper trip to condition the wellbore before casing or logging.",
    },
    "short_trip": {
        "role_3w": "event_observation",
        "iadc_class": "short_trip",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Partial POOH and RIH to check hole conditions.",
    },

    # ------------------------------------------------------------------
    # CASING & CEMENTING
    # ------------------------------------------------------------------
    "casing": {
        "role_3w": "event_observation",
        "iadc_class": "casing_running",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Running casing string to protect the wellbore section.",
    },
    "casing_running": {
        "role_3w": "event_observation",
        "iadc_class": "casing_running",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Running casing string to protect the wellbore section.",
    },
    "liner_running": {
        "role_3w": "event_observation",
        "iadc_class": "liner_running",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Installing a liner (partial casing) from a depth point to TD.",
    },
    "cementing": {
        "role_3w": "event_observation",
        "iadc_class": "cementing",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Primary cementing job — displacing cement behind casing.",
    },
    "squeeze_cementing": {
        "role_3w": "event_observation",
        "iadc_class": "squeeze_cementing",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Remedial squeeze job to repair zonal isolation or lost circulation.",
    },

    # ------------------------------------------------------------------
    # COMPLETIONS & WELL TESTING
    # ------------------------------------------------------------------
    "completions": {
        "role_3w": "event_observation",
        "iadc_class": "completion_operations",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Well completion operations (tubing, packers, safety valves).",
    },
    "perforation": {
        "role_3w": "event_observation",
        "iadc_class": "perforating",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Perforating the casing to establish reservoir communication.",
    },
    "testing": {
        "role_3w": "event_observation",
        "iadc_class": "formation_testing",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Well or formation testing — measuring reservoir deliverability.",
    },
    "dst": {
        "role_3w": "event_observation",
        "iadc_class": "drill_stem_test",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Drill Stem Test — temporary production test on open hole.",
    },

    # ------------------------------------------------------------------
    # LOGGING & SURVEYS
    # ------------------------------------------------------------------
    "logging": {
        "role_3w": "event_observation",
        "iadc_class": "wireline_logging",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Wireline logging run to acquire formation evaluation data.",
    },
    "wireline_logging": {
        "role_3w": "event_observation",
        "iadc_class": "wireline_logging",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Wireline logging run to acquire formation evaluation data.",
    },
    "survey": {
        "role_3w": "event_observation",
        "iadc_class": "directional_survey",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Directional survey — measuring wellbore inclination and azimuth.",
    },

    # ------------------------------------------------------------------
    # BOREHOLE MAINTENANCE
    # ------------------------------------------------------------------
    "circulating": {
        "role_3w": "event_observation",
        "iadc_class": "circulating",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Pumping mud to condition the wellbore or break gel.",
    },
    "reaming": {
        "role_3w": "event_observation",
        "iadc_class": "reaming",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Reaming tight spots while tripping in to maintain gauge hole.",
    },
    "washing": {
        "role_3w": "event_observation",
        "iadc_class": "washing_down",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Washing down — jetting or circulating to clean the wellbore.",
    },
    "milling": {
        "role_3w": "event_observation",
        "iadc_class": "milling",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": "Milling metal obstructions (float equipment, junk, fish).",
    },
    "fishing": {
        "role_3w": "event_observation",
        "iadc_class": "fishing",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "Fishing operation to recover lost/stuck pipe or tools.",
    },

    # ------------------------------------------------------------------
    # NPT — STUCK PIPE
    # ------------------------------------------------------------------
    "stuck_pipe": {
        "role_3w": "event_observation",
        "iadc_class": "stuck_pipe",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "Drill string is stuck in the wellbore; jar or work-over required.",
    },
    "differential_sticking": {
        "role_3w": "event_observation",
        "iadc_class": "stuck_pipe_differential",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": (
            "Pipe held against permeable formation by differential pressure "
            "between hydrostatic mud column and formation pore pressure."
        ),
    },
    "mechanical_stuck": {
        "role_3w": "event_observation",
        "iadc_class": "stuck_pipe_mechanical",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "Pipe stuck by mechanical causes: keyseats, ledges, pack-off.",
    },
    "twist_off": {
        "role_3w": "event_observation",
        "iadc_class": "twist_off",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "critical",
        "description": "Drill string parted by torsional fatigue or over-torque.",
    },

    # ------------------------------------------------------------------
    # NPT — WELL CONTROL & FLUID
    # ------------------------------------------------------------------
    "lost_circulation": {
        "role_3w": "event_observation",
        "iadc_class": "lost_circulation",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "Loss of drilling fluid into the formation (partial or total).",
    },
    "kick": {
        "role_3w": "event_observation",
        "iadc_class": "well_control_kick",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "critical",
        "description": "Unplanned influx of formation fluid into the wellbore.",
    },
    "well_control": {
        "role_3w": "event_observation",
        "iadc_class": "well_control",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "critical",
        "description": "Active well control procedures (shut-in, kill operations).",
    },
    "h2s_event": {
        "role_3w": "event_observation",
        "iadc_class": "well_control_h2s",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "critical",
        "description": "Hydrogen sulphide (H2S) detection event triggering safety protocols.",
    },

    # ------------------------------------------------------------------
    # NPT — WELLBORE INTEGRITY
    # ------------------------------------------------------------------
    "wellbore_collapse": {
        "role_3w": "event_observation",
        "iadc_class": "wellbore_collapse",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "critical",
        "description": "Partial or total collapse of the open hole section.",
    },
    "tight_hole": {
        "role_3w": "event_observation",
        "iadc_class": "tight_hole",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Increased drag/over-pull while tripping — hole gauge reduced.",
    },
    "pack_off": {
        "role_3w": "event_observation",
        "iadc_class": "pack_off",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "Cuttings or cavings pack off around the BHA, restricting circulation.",
    },
    "keyseating": {
        "role_3w": "event_observation",
        "iadc_class": "key_seating",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "Lateral groove cut into formation by drill pipe rotation in a dog-leg.",
    },

    # ------------------------------------------------------------------
    # NPT — EQUIPMENT FAILURES
    # ------------------------------------------------------------------
    "equipment_failure": {
        "role_3w": "event_observation",
        "iadc_class": "equipment_failure",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Generic equipment failure causing unplanned downtime.",
    },
    "bha_failure": {
        "role_3w": "event_observation",
        "iadc_class": "bha_failure",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": "BHA component (MWD, motor, jar) failure requiring POOH.",
    },
    "washout": {
        "role_3w": "event_observation",
        "iadc_class": "washout",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Erosion of drill pipe, bit, or BHA connection by mud flow.",
    },
    "pump_failure": {
        "role_3w": "event_observation",
        "iadc_class": "pump_failure",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Rig mud pump failure causing loss of circulation or flow.",
    },
    "bop_test": {
        "role_3w": "event_observation",
        "iadc_class": "bop_test",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "low",
        "description": "Planned BOP pressure test per regulatory requirement.",
    },

    # ------------------------------------------------------------------
    # NPT — LOGISTICS & WAITING
    # ------------------------------------------------------------------
    "waiting_on_weather": {
        "role_3w": "event_observation",
        "iadc_class": "waiting_on_weather",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "low",
        "description": "Operations suspended due to adverse weather conditions.",
    },
    "waiting_on_cement": {
        "role_3w": "event_observation",
        "iadc_class": "waiting_on_cement",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "low",
        "description": "Waiting for cement to set before resuming drilling.",
    },
    "waiting_on_orders": {
        "role_3w": "event_observation",
        "iadc_class": "waiting_on_orders",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "low",
        "description": "Rig is ready but waiting on operator or regulatory decision.",
    },
    "waiting_on_equipment": {
        "role_3w": "event_observation",
        "iadc_class": "waiting_on_equipment",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Operations halted waiting for delivery of tools or parts.",
    },
    "rig_repair": {
        "role_3w": "event_observation",
        "iadc_class": "rig_repair",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": "Unplanned rig maintenance or repair causing downtime.",
    },

    # ------------------------------------------------------------------
    # INVISIBLE LOST TIME
    # ------------------------------------------------------------------
    "connection_time": {
        "role_3w": "event_observation",
        "iadc_class": "connection_time",
        "time_category": "invisible_lost_time",
        "npt": False,
        "npt_severity": None,
        "description": "Time to break, add, and re-make a drill pipe connection.",
    },
    "flat_time": {
        "role_3w": "event_observation",
        "iadc_class": "flat_time",
        "time_category": "invisible_lost_time",
        "npt": False,
        "npt_severity": None,
        "description": "Zero or near-zero ROP periods not classified as NPT.",
    },
    "invisible_lost_time": {
        "role_3w": "event_observation",
        "iadc_class": "invisible_lost_time",
        "time_category": "invisible_lost_time",
        "npt": False,
        "npt_severity": None,
        "description": "Performance gap vs benchmark not appearing in conventional NPT.",
    },

    # ------------------------------------------------------------------
    # SIGNAL CONCEPTS — subsurface condition indicators (3W)
    # ------------------------------------------------------------------
    "overpressure_zone": {
        "role_3w": "signal_concept",
        "iadc_class": "abnormal_pressure_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": (
            "Formation pore pressure exceeds normal gradient — indicates risk "
            "of kick, requires mud weight increase."
        ),
    },
    "wellbore_instability": {
        "role_3w": "signal_concept",
        "iadc_class": "formation_instability_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": (
            "Formation tendency to collapse, swell, or produce cavings — "
            "root cause of tight hole, pack-off, and stuck pipe."
        ),
    },
    "formation_damage": {
        "role_3w": "signal_concept",
        "iadc_class": "formation_damage_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": (
            "Impairment of near-wellbore permeability by filtrate invasion, "
            "fines migration, or emulsion blockage."
        ),
    },
    "depleted_zone": {
        "role_3w": "signal_concept",
        "iadc_class": "depleted_reservoir_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": (
            "Reservoir sector with pressure below original — risk of lost "
            "circulation and differential sticking."
        ),
    },
    "thief_zone": {
        "role_3w": "signal_concept",
        "iadc_class": "thief_zone_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": (
            "High-permeability layer that absorbs drilling fluid — "
            "primary driver of total lost circulation events."
        ),
    },
    "shallow_gas": {
        "role_3w": "signal_concept",
        "iadc_class": "shallow_gas_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "critical",
        "description": (
            "Free gas trapped in shallow unconsolidated sediment above "
            "main casing strings — blowout risk during conductor/surface sections."
        ),
    },
    "reactive_shale": {
        "role_3w": "signal_concept",
        "iadc_class": "shale_reactivity_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": (
            "Water-sensitive clay-rich shale that hydrates and swells on "
            "contact with water-based mud, causing wellbore instability."
        ),
    },
    "natural_fracture": {
        "role_3w": "signal_concept",
        "iadc_class": "natural_fracture_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": (
            "Pre-existing fracture network in the formation — indicates risk "
            "of sudden total losses and difficult ECD management."
        ),
    },
    "abnormal_pressure": {
        "role_3w": "signal_concept",
        "iadc_class": "abnormal_pressure_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "high",
        "description": (
            "General abnormal pore pressure condition (over or under) — "
            "umbrella signal concept for pressure-related drilling hazards."
        ),
    },
    "salt_section": {
        "role_3w": "signal_concept",
        "iadc_class": "evaporite_indicator",
        "time_category": "non_productive_time",
        "npt": True,
        "npt_severity": "medium",
        "description": (
            "Mobile evaporite (salt) section indicating potential plastic "
            "flow, casing collapse risk, and fluid contamination."
        ),
    },
}

# ---------------------------------------------------------------------------
# Derived lookup sets for fast membership testing
# ---------------------------------------------------------------------------
PRODUCTIVE_PHASES: frozenset[str] = frozenset(
    name
    for name, meta in PHASE_TAXONOMY.items()
    if meta["time_category"] == "productive_time"
)

NPT_PHASES: frozenset[str] = frozenset(
    name
    for name, meta in PHASE_TAXONOMY.items()
    if meta["npt"] is True
)

# Signal concepts are a subset — useful for RAG corpus filtering
SIGNAL_CONCEPT_PHASES: frozenset[str] = frozenset(
    name
    for name, meta in PHASE_TAXONOMY.items()
    if meta["role_3w"] == "signal_concept"
)

# ---------------------------------------------------------------------------
# Keyword-to-phase mapping for text-based fallback classification
# Keys are regex-ready patterns; values are PHASE_TAXONOMY keys.
# Used by classify_phase() when the phase name alone is ambiguous.
# ---------------------------------------------------------------------------
_TEXT_PATTERNS: list[tuple[str, str]] = [
    (r"\bstuck\s+pipe\b",          "stuck_pipe"),
    (r"\bdifferential\s+stick",    "differential_sticking"),
    (r"\btwist.?off\b",            "twist_off"),
    (r"\blost\s+circ",             "lost_circulation"),
    (r"\btotal\s+loss",            "lost_circulation"),
    (r"\bpartial\s+loss",          "lost_circulation"),
    (r"\bkick\b",                  "kick"),
    (r"\binflux\b",                "kick"),
    (r"\bwell\s+control\b",        "well_control"),
    (r"\bh2s\b|hydrogen\s+sulph",  "h2s_event"),
    (r"\bwashout\b",               "washout"),
    (r"\bpack.?off\b",             "pack_off"),
    (r"\bkey.?seat",               "keyseating"),
    (r"\btight\s+hole\b",          "tight_hole"),
    (r"\bcaving",                  "wellbore_instability"),
    (r"\bsloughing\b",             "wellbore_instability"),
    (r"\bover.?press",             "overpressure_zone"),
    (r"\babnormal\s+press",        "abnormal_pressure"),
    (r"\bshallow\s+gas\b",         "shallow_gas"),
    (r"\breactive\s+shale\b",      "reactive_shale"),
    (r"\bdepleted\b",              "depleted_zone"),
    (r"\bthief\s+zone\b",          "thief_zone"),
    (r"\bnatural\s+frac",          "natural_fracture"),
    (r"\bwiper\s+trip\b",          "wiper_trip"),
    (r"\bshort\s+trip\b",          "short_trip"),
    (r"\bream",                    "reaming"),
    (r"\bcircul",                  "circulating"),
    (r"\bcement",                  "cementing"),
    (r"\bcasing\b",                "casing"),
    (r"\blinear\s+running\b",      "liner_running"),
    (r"\bperforation\b",           "perforation"),
    (r"\bdst\b|drill\s+stem\s+test", "dst"),
    (r"\bloggi",                   "logging"),
    (r"\bsurvey\b",                "survey"),
    (r"\bfishing\b",               "fishing"),
    (r"\bmilling\b",               "milling"),
    (r"\brig\s+repair\b",          "rig_repair"),
    (r"\bpump\s+fail",             "pump_failure"),
    (r"\bbha\s+fail",              "bha_failure"),
    (r"\bbop\s+test\b",            "bop_test"),
    (r"\bwaiting\s+on\s+weather\b", "waiting_on_weather"),
    (r"\bwaiting\s+on\s+cement\b",  "waiting_on_cement"),
    (r"\bwaiting\s+on\s+orders?\b", "waiting_on_orders"),
    (r"\bconnection\s+time\b",     "connection_time"),
]

_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(pat, re.IGNORECASE), phase)
    for pat, phase in _TEXT_PATTERNS
]


def classify_phase(phase_name: str, summary_text: str = "") -> dict[str, Any]:
    """Classify a drilling phase into 3W role, IADC class, and NPT category.

    Lookup order:
    1. Exact match in PHASE_TAXONOMY (canonical name).
    2. Normalised underscore name (strip whitespace, lower, replace spaces).
    3. Regex scan of summary_text for known event patterns.
    4. Fallback: generic 'event_observation / unclassified'.

    Args:
        phase_name:   The `name` property of the DrillingPhase node.
        summary_text: Optional raw text (e.g. summary_24hr) for text-based
                      fallback when the name alone is insufficient.

    Returns:
        Dict with keys: role_3w, iadc_class, time_category, npt,
        npt_severity, description, source ('taxonomy'|'text_match'|'fallback').
    """
    # 1 — exact match
    if phase_name in PHASE_TAXONOMY:
        return {**PHASE_TAXONOMY[phase_name], "source": "taxonomy"}

    # 2 — normalised match
    normalised = phase_name.strip().lower().replace(" ", "_").replace("-", "_")
    if normalised in PHASE_TAXONOMY:
        return {**PHASE_TAXONOMY[normalised], "source": "taxonomy"}

    # 3 — text-based pattern match on summary
    if summary_text:
        for pattern, mapped_phase in _COMPILED_PATTERNS:
            if pattern.search(summary_text):
                base = PHASE_TAXONOMY.get(mapped_phase, {})
                return {
                    **base,
                    "source": "text_match",
                    "matched_phase": mapped_phase,
                }

    # 4 — fallback
    return {
        "role_3w": "event_observation",
        "iadc_class": "unclassified_operation",
        "time_category": "productive_time",
        "npt": False,
        "npt_severity": None,
        "description": f"Unrecognised phase: '{phase_name}' — defaulted to event_observation.",
        "source": "fallback",
    }


def run_enrichment(driver: Any) -> dict[str, int]:
    """Enrich all DrillingPhase nodes in Neo4j with 3W and IADC metadata.

    Processes nodes in batches of 200. For each node, calls classify_phase()
    with the node's `name` and optionally the linked DailyReport summary_24hr
    text (fetched via HAS_PHASE relationship).

    Args:
        driver: A neo4j.Driver instance (or compatible object with a
                .session() context manager returning a neo4j.Session).

    Returns:
        Dict with counts: {
            'total': int,       # DrillingPhase nodes found
            'enriched': int,    # nodes successfully updated
            'taxonomy': int,    # classified via PHASE_TAXONOMY
            'text_match': int,  # classified via text patterns
            'fallback': int,    # fell back to generic classification
        }
    """
    FETCH_QUERY = """
    MATCH (p:DrillingPhase)
    OPTIONAL MATCH (r:DailyReport)-[:HAS_PHASE]->(p)
    RETURN
        p.phase_id    AS phase_id,
        p.name        AS name,
        r.summary_24hr AS summary_24hr
    ORDER BY p.phase_id
    SKIP $skip
    LIMIT $limit
    """

    UPDATE_QUERY = """
    UNWIND $rows AS row
    MATCH (p:DrillingPhase {phase_id: row.phase_id})
    SET
        p.role_3w            = row.role_3w,
        p.iadc_activity_class = row.iadc_class,
        p.time_category      = row.time_category,
        p.npt_severity       = row.npt_severity,
        p.enriched           = true
    """

    counts: dict[str, int] = {
        "total": 0,
        "enriched": 0,
        "taxonomy": 0,
        "text_match": 0,
        "fallback": 0,
    }

    batch_size = 200
    skip = 0

    with driver.session() as session:
        while True:
            rows = session.run(
                FETCH_QUERY, skip=skip, limit=batch_size
            ).data()

            if not rows:
                break

            counts["total"] += len(rows)
            updates: list[dict[str, Any]] = []

            for row in rows:
                name: str = row.get("name") or ""
                summary: str = row.get("summary_24hr") or ""
                result = classify_phase(name, summary)

                updates.append({
                    "phase_id":    row["phase_id"],
                    "role_3w":     result["role_3w"],
                    "iadc_class":  result["iadc_class"],
                    "time_category": result["time_category"],
                    "npt_severity": result.get("npt_severity"),
                })

                counts["enriched"] += 1
                src = result.get("source", "fallback")
                if src == "taxonomy":
                    counts["taxonomy"] += 1
                elif src == "text_match":
                    counts["text_match"] += 1
                else:
                    counts["fallback"] += 1

            session.run(UPDATE_QUERY, rows=updates)
            log.info(
                "Enriched batch skip=%d: %d nodes processed (total so far: %d)",
                skip, len(rows), counts["enriched"],
            )

            skip += batch_size

    log.info(
        "run_enrichment complete — total=%d enriched=%d "
        "(taxonomy=%d text_match=%d fallback=%d)",
        counts["total"], counts["enriched"],
        counts["taxonomy"], counts["text_match"], counts["fallback"],
    )
    return counts


def compute_npt_stats(
    driver: Any,
    wellbore_uid: str | None = None,
) -> dict[str, Any]:
    """Compute NPT statistics for enriched DrillingPhase nodes.

    Optionally scoped to a single wellbore. Requires run_enrichment() to have
    been called first so that `time_category` is populated.

    Args:
        driver:       A neo4j.Driver instance.
        wellbore_uid: Optional wellbore identifier (e.g. '15/9-F-5').
                      When None, aggregates across all wellbores.

    Returns:
        Dict with the following structure::

            {
                "total_phases":   int,
                "npt_phases":     int,
                "productive_phases": int,
                "ilt_phases":     int,
                "npt_pct":        float,    # % of total
                "by_type": {
                    "<iadc_activity_class>": {
                        "count": int,
                        "role_3w": str,
                        "npt_severity": str | None,
                    },
                    ...
                },
                "by_severity": {
                    "critical": int,
                    "high": int,
                    "medium": int,
                    "low": int,
                    "none": int,
                },
                "wellbore_uid": str | None,
            }
    """
    base_filter = "WHERE p.wellbore_uid = $wellbore_uid" if wellbore_uid else ""

    summary_query = f"""
    MATCH (p:DrillingPhase)
    {base_filter}
    RETURN
        p.time_category  AS time_category,
        count(p)         AS cnt
    """

    by_type_query = f"""
    MATCH (p:DrillingPhase)
    {base_filter}
    WHERE p.time_category = 'non_productive_time'
    RETURN
        p.iadc_activity_class AS iadc_class,
        p.role_3w             AS role_3w,
        p.npt_severity        AS npt_severity,
        count(p)              AS cnt
    ORDER BY cnt DESC
    """

    by_severity_query = f"""
    MATCH (p:DrillingPhase)
    {base_filter}
    WHERE p.time_category = 'non_productive_time'
    RETURN
        coalesce(p.npt_severity, 'none') AS severity,
        count(p) AS cnt
    """

    params = {"wellbore_uid": wellbore_uid}

    with driver.session() as session:
        summary_rows = session.run(summary_query, **params).data()
        by_type_rows = session.run(by_type_query, **params).data()
        by_severity_rows = session.run(by_severity_query, **params).data()

    total = 0
    npt = 0
    productive = 0
    ilt = 0

    for row in summary_rows:
        cat = row["time_category"] or "productive_time"
        cnt = row["cnt"]
        total += cnt
        if cat == "non_productive_time":
            npt += cnt
        elif cat == "productive_time":
            productive += cnt
        elif cat == "invisible_lost_time":
            ilt += cnt

    npt_pct = round(npt / total * 100, 2) if total > 0 else 0.0

    by_type: dict[str, dict[str, Any]] = {}
    for row in by_type_rows:
        key = row["iadc_class"] or "unknown"
        by_type[key] = {
            "count":        row["cnt"],
            "role_3w":      row["role_3w"],
            "npt_severity": row["npt_severity"],
        }

    by_severity: dict[str, int] = {
        "critical": 0, "high": 0, "medium": 0, "low": 0, "none": 0,
    }
    for row in by_severity_rows:
        sev = row["severity"] or "none"
        by_severity[sev] = row["cnt"]

    return {
        "total_phases":      total,
        "npt_phases":        npt,
        "productive_phases": productive,
        "ilt_phases":        ilt,
        "npt_pct":           npt_pct,
        "by_type":           by_type,
        "by_severity":       by_severity,
        "wellbore_uid":      wellbore_uid,
    }


# ---------------------------------------------------------------------------
# __main__ — smoke tests with 20 phase names including edge cases
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    _TEST_CASES: list[tuple[str, str]] = [
        # (phase_name, summary_excerpt)
        ("drilling",               ""),
        ("tripping",               ""),
        ("rih",                    ""),
        ("pooh",                   ""),
        ("casing",                 ""),
        ("cementing",              ""),
        ("logging",                ""),
        ("testing",                ""),
        ("stuck_pipe",             ""),
        ("lost_circulation",       ""),
        ("kick",                   ""),
        ("wellbore_instability",   ""),
        ("overpressure_zone",      ""),
        ("shallow_gas",            ""),
        ("formation_damage",       ""),
        # edge cases — name not in taxonomy, relies on text
        ("unknown_phase",          "stuck pipe observed at 3200m MD, worked free after 4 hrs"),
        ("section_boundary",       "kicked off at top of 8.5 section, drilled ahead"),
        ("keyword_inference",      "total losses encountered in Heimdal sands, no returns"),
        # whitespace / hyphen normalisation
        ("Rotary Drilling",        ""),
        ("wiper-trip",             ""),
    ]

    print("=" * 60)
    print("phase_role_enricher — classify_phase smoke test")
    print("=" * 60)

    pass_count = 0
    for name, summary in _TEST_CASES:
        result = classify_phase(name, summary)
        status = "OK"

        # Basic sanity assertions
        assert result["role_3w"] in ("event_observation", "signal_concept"), \
            f"Invalid role_3w for '{name}': {result['role_3w']}"
        assert result["time_category"] in (
            "productive_time", "non_productive_time", "invisible_lost_time"
        ), f"Invalid time_category for '{name}': {result['time_category']}"
        assert result["npt"] in (True, False), \
            f"npt must be bool for '{name}'"
        if result["npt"]:
            assert result["npt_severity"] in (
                "low", "medium", "high", "critical"
            ), f"npt=True but npt_severity is {result['npt_severity']!r} for '{name}'"
        else:
            assert result["npt_severity"] is None, \
                f"npt=False but npt_severity is {result['npt_severity']!r} for '{name}'"

        pass_count += 1
        print(
            f"  [{status}] '{name}' -> role={result['role_3w']}, "
            f"iadc={result['iadc_class']}, "
            f"cat={result['time_category']}, "
            f"npt={result['npt']}, "
            f"severity={result['npt_severity']}, "
            f"source={result['source']}"
        )

    print("-" * 60)
    print(f"  {pass_count}/{len(_TEST_CASES)} cases passed")

    print("\nPRODUCTIVE_PHASES sample (first 10):")
    print(" ", sorted(PRODUCTIVE_PHASES)[:10])

    print("\nNPT_PHASES sample (first 10):")
    print(" ", sorted(NPT_PHASES)[:10])

    print("\nSIGNAL_CONCEPT_PHASES:")
    print(" ", sorted(SIGNAL_CONCEPT_PHASES))

    print("\nPHASE_TAXONOMY size:", len(PHASE_TAXONOMY), "entries")
    assert len(PHASE_TAXONOMY) >= 40, \
        f"PHASE_TAXONOMY has only {len(PHASE_TAXONOMY)} entries; need >= 40"
    print("  taxonomy size >= 40 requirement: OK")
