"""bha_normalizer.py — Normalize BHAComponent.type free-text to canonical WITSML/IADC vocabulary.

Enriches the 10,650 BHAComponent nodes in the SPE Volve Neo4j graph by mapping
free-text strings from WITSML/EDM parsing to the WITSML 2.0 ComponentType enumeration.

BHAComponent node schema:
    component_id, assembly_id, type, description, od_in, length_ft, position

Usage::

    from neo4j import GraphDatabase
    from integrations.spe_volve.ingestion.bha_normalizer import run_normalization

    driver = GraphDatabase.driver(uri, auth=(user, password))
    stats = run_normalization(driver)
    print(stats)
"""

from __future__ import annotations

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical WITSML 2.0 ComponentType vocabulary
# Energistics namespace: http://www.energistics.org/energyml/data/witsmlv2/2.0#
# ---------------------------------------------------------------------------

_NS = "http://www.energistics.org/energyml/data/witsmlv2/2.0#"

WITSML_COMPONENT_TYPES: dict[str, dict[str, Any]] = {
    "bit": {
        "witsml_type": "Bit",
        "witsml_uri": f"{_NS}Bit",
        "category": "cutting",
        "subtypes": ["pdc", "roller_cone", "hybrid", "coring_bit", "mill", "diamond"],
        "function": "Rock cutting at bottom of wellbore",
        "iadc_code": "8-1-X",
        "iso_standard": "ISO 10407-2",
    },
    "motor": {
        "witsml_type": "MudMotor",
        "witsml_uri": f"{_NS}MudMotor",
        "category": "directional",
        "subtypes": ["pdm", "turbodrill"],
        "function": "Converts hydraulic energy to rotational mechanical energy",
        "iadc_code": None,
    },
    "mwd": {
        "witsml_type": "MwdTool",
        "witsml_uri": f"{_NS}MwdTool",
        "category": "measurement",
        "subtypes": ["pulser", "em_telemetry", "acoustic_telemetry", "wired_pipe"],
        "function": "Measurement While Drilling — directional surveys and telemetry",
        "iadc_code": None,
    },
    "lwd": {
        "witsml_type": "LwdTool",
        "witsml_uri": f"{_NS}LwdTool",
        "category": "measurement",
        "subtypes": [
            "gamma_ray",
            "resistivity",
            "density_neutron",
            "sonic",
            "nmr",
            "formation_pressure",
            "caliper",
            "img",
        ],
        "function": "Logging While Drilling — formation evaluation in real time",
        "iadc_code": None,
    },
    "rss": {
        "witsml_type": "RotarySteerableTool",
        "witsml_uri": f"{_NS}RotarySteerableTool",
        "category": "directional",
        "subtypes": ["push_the_bit", "point_the_bit", "hybrid"],
        "function": "Rotary Steerable System — continuous rotation with directional control",
        "iadc_code": None,
    },
    "stabilizer": {
        "witsml_type": "Stabilizer",
        "witsml_uri": f"{_NS}Stabilizer",
        "category": "stabilization",
        "subtypes": ["near_bit", "string", "roller", "sleeve", "eccentric"],
        "function": "Keeps BHA concentric in wellbore, controls pendulum tendency",
        "iadc_code": None,
    },
    "drill_collar": {
        "witsml_type": "DrillCollar",
        "witsml_uri": f"{_NS}DrillCollar",
        "category": "weight",
        "subtypes": ["slick", "spiral", "non_magnetic"],
        "function": "Provides weight on bit and bottom-hole stiffness",
        "iadc_code": None,
    },
    "jar": {
        "witsml_type": "Jar",
        "witsml_uri": f"{_NS}Jar",
        "category": "fishing",
        "subtypes": ["mechanical", "hydraulic", "hydro_mechanical"],
        "function": "Delivers impact force to free stuck pipe",
        "iadc_code": None,
    },
    "crossover": {
        "witsml_type": "CrossoverSub",
        "witsml_uri": f"{_NS}CrossoverSub",
        "category": "adapter",
        "subtypes": [],
        "function": "Connects components with different thread types or ODs",
        "iadc_code": None,
    },
    "float_sub": {
        "witsml_type": "FloatValve",
        "witsml_uri": f"{_NS}FloatValve",
        "category": "valve",
        "subtypes": ["flapper", "poppet", "dual"],
        "function": "Prevents backflow (u-tubing) when pumps are off",
        "iadc_code": None,
    },
    "reamer": {
        "witsml_type": "Reamer",
        "witsml_uri": f"{_NS}Reamer",
        "category": "hole_opening",
        "subtypes": ["underreamer", "hole_opener", "bi_center"],
        "function": "Enlarges wellbore to final gauge after pilot bit",
        "iadc_code": None,
    },
    "shock_sub": {
        "witsml_type": "ShockSub",
        "witsml_uri": f"{_NS}ShockSub",
        "category": "vibration_dampening",
        "subtypes": ["axial", "torsional", "combination"],
        "function": "Isolates sensitive tools from drill string vibrations",
        "iadc_code": None,
    },
    "agitator": {
        "witsml_type": "Agitator",
        "witsml_uri": f"{_NS}Agitator",
        "category": "friction_reduction",
        "subtypes": [],
        "function": "Creates axial oscillations to reduce friction in extended reach wells",
        "iadc_code": None,
    },
    "heavyweight_drill_pipe": {
        "witsml_type": "HeavyweightDrillPipe",
        "witsml_uri": f"{_NS}HeavyweightDrillPipe",
        "category": "transition",
        "subtypes": [],
        "function": "Transition element between drill pipe and drill collars",
        "iadc_code": None,
    },
    "nmdc": {
        "witsml_type": "NonMagneticDrillCollar",
        "witsml_uri": f"{_NS}NonMagneticDrillCollar",
        "category": "measurement_support",
        "subtypes": [],
        "function": "Non-magnetic spacing around MWD to eliminate magnetic interference",
        "iadc_code": None,
    },
    "pony_collar": {
        "witsml_type": "PonyCollar",
        "witsml_uri": f"{_NS}PonyCollar",
        "category": "weight",
        "subtypes": [],
        "function": "Short drill collar used for fine WOB adjustment",
        "iadc_code": None,
    },
    "survey_tool": {
        "witsml_type": "SurveyTool",
        "witsml_uri": f"{_NS}SurveyTool",
        "category": "measurement",
        "subtypes": ["single_shot", "multi_shot", "gyro", "magnetic"],
        "function": "Measures borehole inclination and azimuth for directional surveys",
        "iadc_code": None,
    },
    "turbine": {
        "witsml_type": "Turbodrill",
        "witsml_uri": f"{_NS}Turbodrill",
        "category": "power",
        "subtypes": [],
        "function": "High-speed downhole turbine driven by drilling fluid",
        "iadc_code": None,
    },
    "coring_assembly": {
        "witsml_type": "CoringAssembly",
        "witsml_uri": f"{_NS}CoringAssembly",
        "category": "coring",
        "subtypes": ["conventional", "sidewall", "pressure", "sponge"],
        "function": "Retrieves cylindrical rock samples for geological analysis",
        "iadc_code": None,
    },
    "bit_sub": {
        "witsml_type": "BitSub",
        "witsml_uri": f"{_NS}BitSub",
        "category": "adapter",
        "subtypes": [],
        "function": "Connects bit to motor or BHA string",
        "iadc_code": None,
    },
    "mud_motor_sub": {
        "witsml_type": "MudMotorSub",
        "witsml_uri": f"{_NS}MudMotorSub",
        "category": "adapter",
        "subtypes": ["bent_housing", "adjustable_housing"],
        "function": "Bent housing or adjustable sub on motor for directional work",
        "iadc_code": None,
    },
    "drill_pipe": {
        "witsml_type": "DrillPipe",
        "witsml_uri": f"{_NS}DrillPipe",
        "category": "conveyance",
        "subtypes": ["standard", "premium", "s135", "heavyweight"],
        "function": "Transmits rotation and fluid from surface to BHA",
        "iadc_code": None,
    },
    "accelerator": {
        "witsml_type": "Accelerator",
        "witsml_uri": f"{_NS}Accelerator",
        "category": "fishing",
        "subtypes": [],
        "function": "Stores energy and amplifies jar impact force",
        "iadc_code": None,
    },
    "mule_shoe": {
        "witsml_type": "MuleShoeSub",
        "witsml_uri": f"{_NS}MuleShoeSub",
        "category": "orientation",
        "subtypes": [],
        "function": "Orients a deflection tool or whipstock in directional operations",
        "iadc_code": None,
    },
    "bend_sub": {
        "witsml_type": "BentSub",
        "witsml_uri": f"{_NS}BentSub",
        "category": "directional",
        "subtypes": [],
        "function": "Fixed-angle bend to create directional deviation with motor",
        "iadc_code": None,
    },
    "unknown": {
        "witsml_type": "UnknownComponent",
        "witsml_uri": f"{_NS}DownholeComponent",
        "category": "unknown",
        "subtypes": [],
        "function": "Component type could not be determined from available data",
        "iadc_code": None,
    },
}

# ---------------------------------------------------------------------------
# RAW_TYPE_MAP — free-text strings → (canonical_type, subtype | None)
# Covers real WITSML/EDM strings from SPE Volve and North Sea datasets.
# Keys are upper-cased at match time; values are (canonical_type, subtype).
# ---------------------------------------------------------------------------

RAW_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # --- Bit ---
    "BIT": ("bit", None),
    "PDC BIT": ("bit", "pdc"),
    "PDC": ("bit", "pdc"),
    "PDC CORE BIT": ("bit", "pdc"),
    "BICONE": ("bit", "roller_cone"),
    "ROLLER CONE": ("bit", "roller_cone"),
    "ROLLER CONE BIT": ("bit", "roller_cone"),
    "TCI BIT": ("bit", "roller_cone"),
    "INSERT BIT": ("bit", "roller_cone"),
    "DIAMOND BIT": ("bit", "diamond"),
    "IMPREG BIT": ("bit", "diamond"),
    "IMPREGNATED BIT": ("bit", "diamond"),
    "HYBRID BIT": ("bit", "hybrid"),
    "MILL": ("bit", "mill"),
    "JUNK MILL": ("bit", "mill"),
    "SECTION MILL": ("bit", "mill"),
    "CORING BIT": ("bit", "coring_bit"),
    "CORE BIT": ("bit", "coring_bit"),
    # Diameter-prefixed variants (e.g. "8.5 PDC", "12.25 BIT")
    "8.5 PDC": ("bit", "pdc"),
    "8 1/2 PDC": ("bit", "pdc"),
    "12.25 BIT": ("bit", None),
    "12 1/4 BIT": ("bit", None),
    "17.5 BIT": ("bit", None),
    "17 1/2 BIT": ("bit", None),
    "6 BIT": ("bit", None),
    "6.0 BIT": ("bit", None),

    # --- Motor ---
    "MOTOR": ("motor", "pdm"),
    "MUD MOTOR": ("motor", "pdm"),
    "PDM": ("motor", "pdm"),
    "PDM MOTOR": ("motor", "pdm"),
    "POSITIVE DISPLACEMENT MOTOR": ("motor", "pdm"),
    "SCREW MOTOR": ("motor", "pdm"),
    "TURBODRILL": ("motor", "turbodrill"),
    "TURBINE": ("turbine", None),

    # --- MWD ---
    "MWD": ("mwd", None),
    "MWD TOOL": ("mwd", None),
    "MWD PULSER": ("mwd", "pulser"),
    "MWD/LWD": ("mwd", None),
    "PULSER": ("mwd", "pulser"),
    "EM MWD": ("mwd", "em_telemetry"),
    "WIRED PIPE MWD": ("mwd", "wired_pipe"),
    "INTELLISERV": ("mwd", "wired_pipe"),
    "POWERPULSE": ("mwd", "pulser"),
    "DIRECTIONAL TOOL": ("mwd", None),

    # --- LWD ---
    "LWD": ("lwd", None),
    "LWD TOOL": ("lwd", None),
    "GR LWD": ("lwd", "gamma_ray"),
    "GAMMA RAY LWD": ("lwd", "gamma_ray"),
    "ARCVISION": ("lwd", "resistivity"),
    "ADNVISION": ("lwd", "density_neutron"),
    "PERISCOPE": ("lwd", "resistivity"),
    "SONICVISION": ("lwd", "sonic"),
    "VISION": ("lwd", None),
    "DENSITY LWD": ("lwd", "density_neutron"),
    "NEUTRON LWD": ("lwd", "density_neutron"),
    "SONIC LWD": ("lwd", "sonic"),
    "RESISTIVITY LWD": ("lwd", "resistivity"),
    "NIMBLE": ("lwd", "resistivity"),
    "ULTRASONIC LWD": ("lwd", "img"),
    "IMAGE LWD": ("lwd", "img"),

    # --- RSS ---
    "RSS": ("rss", None),
    "ROTARY STEERABLE": ("rss", None),
    "ROTARY STEERABLE SYSTEM": ("rss", None),
    "POWERDRIVE": ("rss", "push_the_bit"),
    "AUTOTRAK": ("rss", "push_the_bit"),
    "GEOPILOT": ("rss", "point_the_bit"),
    "XCEED": ("rss", "push_the_bit"),

    # --- Stabilizer ---
    "STAB": ("stabilizer", None),
    "STABILIZER": ("stabilizer", None),
    "STRING STAB": ("stabilizer", "string"),
    "STRING STABILIZER": ("stabilizer", "string"),
    "NBS": ("stabilizer", "near_bit"),
    "NBS STAB": ("stabilizer", "near_bit"),
    "NEAR BIT STAB": ("stabilizer", "near_bit"),
    "NEAR BIT STABILIZER": ("stabilizer", "near_bit"),
    "ROLLER STAB": ("stabilizer", "roller"),
    "ROLLER REAMER": ("reamer", None),
    "SLEEVE STAB": ("stabilizer", "sleeve"),
    "ECCENTRIC STAB": ("stabilizer", "eccentric"),
    "8.5 STAB": ("stabilizer", None),
    "8 1/2 STAB": ("stabilizer", None),
    "12.25 STAB": ("stabilizer", None),

    # --- Jar ---
    "JAR": ("jar", None),
    "HYD JAR": ("jar", "hydraulic"),
    "HYDRAULIC JAR": ("jar", "hydraulic"),
    "MECH JAR": ("jar", "mechanical"),
    "MECHANICAL JAR": ("jar", "mechanical"),
    "HYDROMECH JAR": ("jar", "hydro_mechanical"),
    "HM JAR": ("jar", "hydro_mechanical"),

    # --- Crossover / Sub ---
    "X-OVER": ("crossover", None),
    "XOVER": ("crossover", None),
    "XO": ("crossover", None),
    "X OVER": ("crossover", None),
    "CROSSOVER": ("crossover", None),
    "CROSSOVER SUB": ("crossover", None),
    "ADAPTOR SUB": ("crossover", None),
    "ADAPTER SUB": ("crossover", None),
    "LIFT SUB": ("crossover", None),
    "LIFT NIP": ("crossover", None),
    "SAVER SUB": ("crossover", None),
    "SLICK JOINT": ("crossover", None),

    # --- Float sub / valve ---
    "FLOAT SUB": ("float_sub", None),
    "FLOAT": ("float_sub", None),
    "FLOAT VALVE": ("float_sub", None),
    "FLOAT COLLAR": ("float_sub", None),
    "FLAPPER VALVE": ("float_sub", "flapper"),
    "POPPET VALVE": ("float_sub", "poppet"),
    "BACK PRESSURE VALVE": ("float_sub", None),
    "BPV": ("float_sub", None),
    "CHECK VALVE": ("float_sub", None),

    # --- Drill Collar ---
    "DC": ("drill_collar", "slick"),
    "D/C": ("drill_collar", "slick"),
    "DRILL COLLAR": ("drill_collar", "slick"),
    "DRILL COLLARS": ("drill_collar", "slick"),
    "SLICK DC": ("drill_collar", "slick"),
    "SPIRAL DC": ("drill_collar", "spiral"),
    "SPIRAL DRILL COLLAR": ("drill_collar", "spiral"),
    "NMDC": ("nmdc", None),
    "NM DC": ("nmdc", None),
    "NON MAG DC": ("nmdc", None),
    "NON MAGNETIC DC": ("nmdc", None),
    "NON-MAGNETIC DRILL COLLAR": ("nmdc", None),
    "8 DC": ("drill_collar", "slick"),
    "8.0 DC": ("drill_collar", "slick"),

    # --- HWDP ---
    "HWDP": ("heavyweight_drill_pipe", None),
    "HW DRILL PIPE": ("heavyweight_drill_pipe", None),
    "HEAVY WEIGHT DP": ("heavyweight_drill_pipe", None),
    "HEAVYWEIGHT DP": ("heavyweight_drill_pipe", None),

    # --- Drill Pipe ---
    "DP": ("drill_pipe", "standard"),
    "DRILL PIPE": ("drill_pipe", "standard"),
    "S135 DP": ("drill_pipe", "s135"),

    # --- Reamer ---
    "REAMER": ("reamer", None),
    "UNDERREAMER": ("reamer", "underreamer"),
    "HOLE OPENER": ("reamer", "hole_opener"),
    "BI CENTER": ("reamer", "bi_center"),
    "BICENTER": ("reamer", "bi_center"),

    # --- Shock sub ---
    "SHOCK SUB": ("shock_sub", None),
    "SHOCK TOOL": ("shock_sub", None),
    "VIBRATION DAMPENER": ("shock_sub", None),
    "VIB DAMPENER": ("shock_sub", None),
    "BUMPER SUB": ("shock_sub", "axial"),

    # --- Agitator ---
    "AGITATOR": ("agitator", None),
    "OSCILLATION TOOL": ("agitator", None),
    "FRICTION REDUCER": ("agitator", None),

    # --- Pony collar ---
    "PONY COLLAR": ("pony_collar", None),
    "PC": ("pony_collar", None),
    "SHORT DC": ("pony_collar", None),

    # --- Survey tools ---
    "SURVEY TOOL": ("survey_tool", None),
    "GYRO": ("survey_tool", "gyro"),
    "GYROSCOPE": ("survey_tool", "gyro"),
    "SINGLE SHOT": ("survey_tool", "single_shot"),
    "MULTI SHOT": ("survey_tool", "multi_shot"),
    "MULTISHOT": ("survey_tool", "multi_shot"),

    # --- Coring ---
    "CORE BARREL": ("coring_assembly", "conventional"),
    "CORING ASSEMBLY": ("coring_assembly", "conventional"),
    "CONVENTIONAL CORE": ("coring_assembly", "conventional"),
    "PRESSURE CORE": ("coring_assembly", "pressure"),
    "SPONGE CORE": ("coring_assembly", "sponge"),

    # --- Bent sub / mud motor sub ---
    "BENT SUB": ("bend_sub", None),
    "BEND SUB": ("bend_sub", None),
    "ADJUSTABLE BENT SUB": ("mud_motor_sub", "adjustable_housing"),
    "ABS": ("mud_motor_sub", "adjustable_housing"),
    "BENT HOUSING": ("mud_motor_sub", "bent_housing"),
    "BEARING SECTION": ("mud_motor_sub", None),

    # --- Bit sub ---
    "BIT SUB": ("bit_sub", None),
    "BIT BOX": ("bit_sub", None),

    # --- Accelerator ---
    "ACCELERATOR": ("accelerator", None),
    "JAR ACCELERATOR": ("accelerator", None),

    # --- Mule shoe ---
    "MULE SHOE": ("mule_shoe", None),
    "MULE SHOE SUB": ("mule_shoe", None),
    "WHIPSTOCK": ("mule_shoe", None),
}

# ---------------------------------------------------------------------------
# Fuzzy keyword patterns for fallback matching (ordered by specificity)
# Each entry: (regex_pattern, canonical_type, subtype | None)
# ---------------------------------------------------------------------------

_FUZZY_PATTERNS: list[tuple[re.Pattern[str], str, str | None]] = [
    # Bits — must come before "motor" to catch "PDC" before "PDM"
    (re.compile(r"\bPDC\b"), "bit", "pdc"),
    (re.compile(r"\bROLL(?:ER)?\s*CONE\b"), "bit", "roller_cone"),
    (re.compile(r"\bIMPREG\b"), "bit", "diamond"),
    (re.compile(r"\bBICONE\b"), "bit", "roller_cone"),
    (re.compile(r"\bMILL\b"), "bit", "mill"),
    (re.compile(r"\bCORE?\s*BIT\b"), "bit", "coring_bit"),
    (re.compile(r"\bBIT\b"), "bit", None),
    # Motor / turbine
    (re.compile(r"\bPDM\b"), "motor", "pdm"),
    (re.compile(r"\bMOTOR\b"), "motor", "pdm"),
    (re.compile(r"\bTURBODRILL\b"), "motor", "turbodrill"),
    (re.compile(r"\bTURBINE?\b"), "turbine", None),
    # MWD / LWD — check LWD before MWD to avoid "MWD/LWD" confusion
    (re.compile(r"\bLWD\b"), "lwd", None),
    (re.compile(r"\bMWD\b"), "mwd", None),
    (re.compile(r"\bPULSER\b"), "mwd", "pulser"),
    (re.compile(r"\bARCVISION\b"), "lwd", "resistivity"),
    (re.compile(r"\bADNVISION\b"), "lwd", "density_neutron"),
    # RSS
    (re.compile(r"\bRSS\b"), "rss", None),
    (re.compile(r"\bROTARY\s*STEER"), "rss", None),
    (re.compile(r"\bPOWERDRIVE\b"), "rss", "push_the_bit"),
    (re.compile(r"\bAUTOTRAK\b"), "rss", "push_the_bit"),
    # Stabilizer
    (re.compile(r"\bNBS\b"), "stabilizer", "near_bit"),
    (re.compile(r"\bNEAR\s*BIT\b"), "stabilizer", "near_bit"),
    (re.compile(r"\bSTAB(?:ILIZ)?\b"), "stabilizer", None),
    # Jar
    (re.compile(r"\bHYD(?:RAULIC)?\s*JAR\b"), "jar", "hydraulic"),
    (re.compile(r"\bMECH(?:ANICAL)?\s*JAR\b"), "jar", "mechanical"),
    (re.compile(r"\bJAR\b"), "jar", None),
    # Crossover
    (re.compile(r"\bX\s*-?\s*OVER\b"), "crossover", None),
    (re.compile(r"\bCROSSO?VER\b"), "crossover", None),
    (re.compile(r"\bADAP(?:T(?:ER|OR))?\s*SUB\b"), "crossover", None),
    # Float
    (re.compile(r"\bFLOAT\b"), "float_sub", None),
    # Drill collar and NMDC
    (re.compile(r"\bNMDC\b"), "nmdc", None),
    (re.compile(r"\bNON\s*-?\s*MAG\b"), "nmdc", None),
    (re.compile(r"\bDRILL\s*COLLAR\b"), "drill_collar", "slick"),
    (re.compile(r"\b\bD/?C\b"), "drill_collar", "slick"),
    # HWDP
    (re.compile(r"\bHWDP\b"), "heavyweight_drill_pipe", None),
    (re.compile(r"\bHEAVY\s*WEIGHT\b"), "heavyweight_drill_pipe", None),
    # Drill pipe
    (re.compile(r"\bDRILL\s*PIPE\b"), "drill_pipe", "standard"),
    # Reamer
    (re.compile(r"\bUNDERREAMER\b"), "reamer", "underreamer"),
    (re.compile(r"\bHOLE\s*OPENER\b"), "reamer", "hole_opener"),
    (re.compile(r"\bBI\s*-?\s*CENT(?:ER|RE)\b"), "reamer", "bi_center"),
    (re.compile(r"\bREAMER\b"), "reamer", None),
    # Shock / vibration
    (re.compile(r"\bSHOCK\b"), "shock_sub", None),
    (re.compile(r"\bBUMPER\s*SUB\b"), "shock_sub", "axial"),
    (re.compile(r"\bVIB(?:RATION)?\b"), "shock_sub", None),
    # Agitator
    (re.compile(r"\bAGITATOR\b"), "agitator", None),
    (re.compile(r"\bOSCILL"), "agitator", None),
    # Survey
    (re.compile(r"\bGYRO\b"), "survey_tool", "gyro"),
    (re.compile(r"\bSURVEY\b"), "survey_tool", None),
    # Coring
    (re.compile(r"\bCORE\s*BARREL\b"), "coring_assembly", "conventional"),
    (re.compile(r"\bCORING\b"), "coring_assembly", None),
    # Bent / motor sub
    (re.compile(r"\bBENT\b"), "mud_motor_sub", "bent_housing"),
    (re.compile(r"\bBEARING\s*SECT"), "mud_motor_sub", None),
    # Bit sub
    (re.compile(r"\bBIT\s*SUB\b"), "bit_sub", None),
    # Accelerator
    (re.compile(r"\bACCELERATOR\b"), "accelerator", None),
    # Pony collar
    (re.compile(r"\bPONY\b"), "pony_collar", None),
    # Mule shoe
    (re.compile(r"\bMULE\s*SHOE\b"), "mule_shoe", None),
    (re.compile(r"\bWHIPSTOCK\b"), "mule_shoe", None),
]

# Description-based signals: substring → (canonical_type, subtype | None)
# Applied when raw-type match fails. Checked in order; first match wins.
_DESCRIPTION_SIGNALS: list[tuple[str, str, str | None]] = [
    ("ARCVISION", "lwd", "resistivity"),
    ("ADNVISION", "lwd", "density_neutron"),
    ("SONICVISION", "lwd", "sonic"),
    ("GAMMA RAY", "lwd", "gamma_ray"),
    ("HALLIBURTON MWD", "mwd", None),
    ("SCHLUMBERGER MWD", "mwd", None),
    ("BAKER MWD", "mwd", None),
    ("DIRECTIONAL SENSOR", "mwd", None),
    ("PDM", "motor", "pdm"),
    ("POSITIVE DISPLACEMENT", "motor", "pdm"),
    ("NEAR BIT", "stabilizer", "near_bit"),
    ("ROLLER REAMER", "reamer", None),
    ("TURBODRILL", "motor", "turbodrill"),
    ("POWERDRIVE", "rss", "push_the_bit"),
    ("AUTOTRAK", "rss", "push_the_bit"),
    ("GEOPILOT", "rss", "point_the_bit"),
]


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------


def normalize_bha_component(
    raw_type: str,
    description: str = "",
) -> dict[str, Any]:
    """Map a free-text BHA component type to the canonical WITSML vocabulary.

    Matching strategy (first hit wins):
    1. Exact match in RAW_TYPE_MAP (upper-cased, stripped).
    2. Fuzzy regex patterns applied to upper-cased raw_type.
    3. Description signals — if raw_type yields no confident match.
    4. Fallback to "unknown" with confidence 0.0.

    Args:
        raw_type:    Raw string from BHAComponent.type (e.g. "8.5 STAB").
        description: Optional BHAComponent.description for disambiguation.

    Returns:
        dict with keys:
            canonical_type (str): key into WITSML_COMPONENT_TYPES
            subtype (str | None):  sub-classification within the type
            category (str):        functional category
            witsml_uri (str):      Energistics WITSML 2.0 URI
            confidence (float):    0.0–1.0 (1.0 = exact, 0.8 = fuzzy, 0.5 = desc)
    """
    if not raw_type:
        return _build_result("unknown", None, 0.0)

    normalised = raw_type.strip().upper()

    # 1. Exact lookup
    if normalised in RAW_TYPE_MAP:
        ctype, subtype = RAW_TYPE_MAP[normalised]
        return _build_result(ctype, subtype, 1.0)

    # 2. Fuzzy regex on raw_type
    for pattern, ctype, subtype in _FUZZY_PATTERNS:
        if pattern.search(normalised):
            return _build_result(ctype, subtype, 0.8)

    # 3. Description signals
    desc_upper = description.strip().upper()
    for signal, ctype, subtype in _DESCRIPTION_SIGNALS:
        if signal in desc_upper:
            return _build_result(ctype, subtype, 0.5)

    # 4. Fallback
    logger.debug("No match for raw_type=%r description=%r", raw_type, description)
    return _build_result("unknown", None, 0.0)


def _build_result(
    canonical_type: str,
    subtype: str | None,
    confidence: float,
) -> dict[str, Any]:
    """Construct the normalizer return dict from a canonical type key."""
    meta = WITSML_COMPONENT_TYPES.get(canonical_type, WITSML_COMPONENT_TYPES["unknown"])
    return {
        "canonical_type": canonical_type,
        "subtype": subtype,
        "category": meta["category"],
        "witsml_uri": meta["witsml_uri"],
        "confidence": confidence,
    }


# ---------------------------------------------------------------------------
# BHA string classifier
# ---------------------------------------------------------------------------

# LWD tool subtypes mapped to capabilities they imply
_LWD_SUBTYPE_CAPABILITIES: dict[str, str] = {
    "gamma_ray": "gamma_ray",
    "resistivity": "resistivity",
    "density_neutron": "density_neutron",
    "sonic": "sonic",
    "nmr": "nmr",
    "formation_pressure": "formation_pressure",
    "img": "borehole_image",
}

# BHA run type decision matrix
_BHA_RUN_TYPES = {
    "coring": "coring",
    "rss": "rss",
    "motor": "directional_motor",
    "fishing": "fishing",
    "rotary": "rotary",
}


def classify_bha_string(components: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify a BHA run from its list of normalised component dicts.

    Args:
        components: List of component dicts, each containing at minimum:
            - type (str): raw type string
            - description (str, optional)
            Additional keys are ignored.

    Returns:
        dict with keys:
            bha_run_type (str):    "rotary" | "directional_motor" | "rss" |
                                   "coring" | "fishing"
            has_mwd (bool):        MWD tool present
            has_lwd (bool):        LWD tool present
            has_rss (bool):        RSS present
            has_motor (bool):      mud motor / PDM present
            has_jar (bool):        jar present
            capabilities (list[str]):  inferred measurement / operational capabilities
            component_count (int): total number of components
    """
    normalised = [
        normalize_bha_component(c.get("type", ""), c.get("description", ""))
        for c in components
    ]

    types_present = {n["canonical_type"] for n in normalised}
    lwd_subtypes = {n["subtype"] for n in normalised if n["canonical_type"] == "lwd"}

    has_mwd = "mwd" in types_present
    has_lwd = "lwd" in types_present
    has_rss = "rss" in types_present
    has_motor = "motor" in types_present
    has_jar = "jar" in types_present
    has_coring = "coring_assembly" in types_present
    has_fishing = has_jar and "bit" not in types_present  # jar-only run = fishing

    # Determine primary BHA run type (priority order)
    if has_coring:
        bha_run_type = "coring"
    elif has_rss:
        bha_run_type = "rss"
    elif has_motor:
        bha_run_type = "directional_motor"
    elif has_fishing:
        bha_run_type = "fishing"
    else:
        bha_run_type = "rotary"

    # Build capabilities list
    capabilities: list[str] = []
    if has_mwd:
        capabilities.append("directional")
    if has_rss or has_motor:
        capabilities.append("steering")
    for subtype, cap in _LWD_SUBTYPE_CAPABILITIES.items():
        if subtype in lwd_subtypes:
            capabilities.append(cap)
    if has_lwd and not lwd_subtypes:
        # LWD present but subtype unknown — add generic
        capabilities.append("formation_evaluation")
    if has_coring:
        capabilities.append("coring")
    if has_jar:
        capabilities.append("jar_available")

    return {
        "bha_run_type": bha_run_type,
        "has_mwd": has_mwd,
        "has_lwd": has_lwd,
        "has_rss": has_rss,
        "has_motor": has_motor,
        "has_jar": has_jar,
        "capabilities": sorted(set(capabilities)),
        "component_count": len(components),
    }


# ---------------------------------------------------------------------------
# Neo4j Cypher enrichment
# ---------------------------------------------------------------------------

_CYPHER_ENRICHMENT = """\
// BHAComponent type enrichment — apply normalised WITSML vocabulary
// Parameters: $updates — list of {component_id, canonical_type, subtype,
//             category, witsml_uri, confidence}
UNWIND $updates AS u
MATCH (c:BHAComponent {component_id: u.component_id})
SET
  c.canonical_type  = u.canonical_type,
  c.subtype         = u.subtype,
  c.category        = u.category,
  c.witsml_uri      = u.witsml_uri,
  c.type_confidence = u.confidence,
  c.normalised_at   = datetime()
RETURN count(c) AS updated
"""


def build_enrichment_cypher() -> str:
    """Return the parameterised Cypher query for BHAComponent enrichment.

    Expected parameter ``$updates`` is a list of dicts with keys:
        component_id, canonical_type, subtype, category, witsml_uri, confidence.

    Returns:
        Cypher string ready for use with ``session.run()``.
    """
    return _CYPHER_ENRICHMENT


_FETCH_CYPHER = """\
MATCH (c:BHAComponent)
WHERE c.canonical_type IS NULL
RETURN c.component_id AS component_id,
       c.type          AS type,
       c.description   AS description
ORDER BY c.component_id
"""

_BATCH_SIZE = 500


def run_normalization(driver: Any) -> dict[str, Any]:
    """Batch-enrich all un-normalised BHAComponent nodes in Neo4j.

    Fetches nodes where ``canonical_type`` is NULL, runs
    :func:`normalize_bha_component` on each, then writes back in batches
    of :data:`_BATCH_SIZE` using the parameterised Cypher from
    :func:`build_enrichment_cypher`.

    Args:
        driver: An active ``neo4j.GraphDatabase.driver`` instance.

    Returns:
        dict with keys:
            total_fetched (int):   nodes read from graph
            total_updated (int):   nodes written back
            by_canonical_type (dict[str, int]):  count per canonical type
            low_confidence (int):  nodes with confidence < 0.8 (needs review)
            unknown_count (int):   nodes mapped to "unknown"
    """
    cypher_fetch = _FETCH_CYPHER
    cypher_update = build_enrichment_cypher()

    total_fetched = 0
    total_updated = 0
    by_type: dict[str, int] = {}
    low_confidence = 0
    unknown_count = 0

    with driver.session() as session:
        records = list(session.run(cypher_fetch))
        total_fetched = len(records)
        logger.info("Fetched %d un-normalised BHAComponent nodes", total_fetched)

        batch: list[dict[str, Any]] = []
        for record in records:
            result = normalize_bha_component(
                raw_type=record["type"] or "",
                description=record["description"] or "",
            )
            update = {
                "component_id": record["component_id"],
                "canonical_type": result["canonical_type"],
                "subtype": result["subtype"],
                "category": result["category"],
                "witsml_uri": result["witsml_uri"],
                "confidence": result["confidence"],
            }
            batch.append(update)

            ctype = result["canonical_type"]
            by_type[ctype] = by_type.get(ctype, 0) + 1
            if result["confidence"] < 0.8:
                low_confidence += 1
            if ctype == "unknown":
                unknown_count += 1

            if len(batch) >= _BATCH_SIZE:
                result_summary = session.run(cypher_update, updates=batch)
                total_updated += result_summary.single()["updated"]
                batch.clear()

        if batch:
            result_summary = session.run(cypher_update, updates=batch)
            total_updated += result_summary.single()["updated"]

    logger.info(
        "Enrichment complete: %d fetched, %d updated, %d low-confidence, %d unknown",
        total_fetched,
        total_updated,
        low_confidence,
        unknown_count,
    )

    return {
        "total_fetched": total_fetched,
        "total_updated": total_updated,
        "by_canonical_type": by_type,
        "low_confidence": low_confidence,
        "unknown_count": unknown_count,
    }


# ---------------------------------------------------------------------------
# __main__ — 25 test cases covering real WITSML/EDM strings from SPE Volve
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    _GREEN = "\033[32m"
    _RED = "\033[31m"
    _RESET = "\033[0m"

    # (raw_type, description, expected_canonical_type, min_confidence)
    TEST_CASES: list[tuple[str, str, str, float]] = [
        # 1  — exact PDC bit
        ("PDC BIT", "", "bit", 1.0),
        # 2  — diameter-prefixed PDC
        ("8.5 PDC", "", "bit", 1.0),
        # 3  — plain "BIT" resolves to bit
        ("BIT", "", "bit", 1.0),
        # 4  — mud motor via PDM acronym
        ("PDM", "", "motor", 1.0),
        # 5  — MWD full name
        ("MWD TOOL", "", "mwd", 1.0),
        # 6  — Schlumberger ArcVision (LWD resistivity)
        ("ARCVISION", "", "lwd", 1.0),
        # 7  — Schlumberger ADNvision (LWD density-neutron)
        ("ADNVISION", "", "lwd", 1.0),
        # 8  — rotary steerable system abbreviation
        ("RSS", "", "rss", 1.0),
        # 9  — near-bit stabilizer abbreviation
        ("NBS", "", "stabilizer", 1.0),
        # 10 — diameter-prefixed stabilizer
        ("8.5 STAB", "", "stabilizer", 1.0),
        # 11 — hydraulic jar abbreviation
        ("HYD JAR", "", "jar", 1.0),
        # 12 — crossover with hyphen
        ("X-OVER", "", "crossover", 1.0),
        # 13 — XO abbreviation
        ("XO", "", "crossover", 1.0),
        # 14 — float sub
        ("FLOAT SUB", "", "float_sub", 1.0),
        # 15 — drill collar abbreviation
        ("DC", "", "drill_collar", 1.0),
        # 16 — non-magnetic drill collar
        ("NMDC", "", "nmdc", 1.0),
        # 17 — heavyweight drill pipe
        ("HWDP", "", "heavyweight_drill_pipe", 1.0),
        # 18 — reamer
        ("UNDERREAMER", "", "reamer", 1.0),
        # 19 — shock sub
        ("SHOCK SUB", "", "shock_sub", 1.0),
        # 20 — coring assembly
        ("CORE BARREL", "", "coring_assembly", 1.0),
        # 21 — fuzzy: raw "MUD MOTOR" not in exact map → fuzzy
        ("MUD MOTOR", "", "motor", 0.8),
        # 22 — description signal: "Halliburton MWD" in description
        ("DOWNHOLE TOOL", "Halliburton MWD pulser system", "mwd", 0.5),
        # 23 — PowerDrive (Schlumberger RSS)
        ("POWERDRIVE", "", "rss", 1.0),
        # 24 — empty string → unknown
        ("", "", "unknown", 0.0),
        # 25 — completely unrecognised string → unknown
        ("MYSTERY TOOL XYZ", "unknown component", "unknown", 0.0),
    ]

    passed = 0
    failed = 0

    print(f"\nRunning {len(TEST_CASES)} BHA normalizer test cases\n{'─' * 60}")

    for idx, (raw, desc, expected_type, min_conf) in enumerate(TEST_CASES, start=1):
        result = normalize_bha_component(raw, desc)
        ok = (
            result["canonical_type"] == expected_type
            and result["confidence"] >= min_conf
        )
        status = f"{_GREEN}PASS{_RESET}" if ok else f"{_RED}FAIL{_RESET}"
        if ok:
            passed += 1
        else:
            failed += 1
        print(
            f"  [{idx:02d}] {status}  raw={raw!r:<25s}  "
            f"got={result['canonical_type']!r:<25s}  "
            f"want={expected_type!r:<25s}  "
            f"conf={result['confidence']:.1f}"
        )
        if not ok:
            print(f"         desc={desc!r}  result={result}")

    print(f"\n{'─' * 60}")
    print(f"Results: {passed}/{len(TEST_CASES)} passed", end="")
    if failed:
        print(f"  ({_RED}{failed} failed{_RESET})")
        sys.exit(1)
    else:
        print(f"  ({_GREEN}all OK{_RESET})")

    # Demonstrate classify_bha_string with a directional MWD+LWD run
    print("\nClassify BHA string demo:")
    demo_components = [
        {"type": "PDC BIT", "description": ""},
        {"type": "PDM", "description": "Positive Displacement Motor 6.75 inch"},
        {"type": "MWD TOOL", "description": "Pulser telemetry"},
        {"type": "ARCVISION", "description": "Resistivity LWD"},
        {"type": "ADNVISION", "description": "Density-Neutron LWD"},
        {"type": "NBS", "description": "Near bit stabilizer"},
        {"type": "DC", "description": "8.0 drill collar x1"},
        {"type": "NMDC", "description": "Non-mag collar x2"},
        {"type": "HWDP", "description": "Heavy weight drill pipe"},
    ]
    classification = classify_bha_string(demo_components)
    for k, v in classification.items():
        print(f"  {k:<20s}: {v}")
