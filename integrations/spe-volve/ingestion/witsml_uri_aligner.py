"""WITSML URI Aligner — add semantic URIs to SPE Volve Neo4j nodes.

Parsed WITSML XML structural data ingested into Neo4j lacks ontological
alignment.  This module adds WITSML 2.0 and OSDU URIs to existing nodes so
that the graph can participate in federated SPARQL queries, RDF export, and
standards-compliant agent reasoning.

Public API
----------
NODE_TYPE_ALIGNMENT   — dict: Neo4j label -> WITSML/OSDU/GeoSciML URI mapping
PROPERTY_ALIGNMENT    — dict: Neo4j property -> WITSML property + QUDT unit URI
build_node_uri_cypher — generate Cypher SET statement for one node label
run_alignment         — execute batch alignment against a live Neo4j driver
generate_rdf_triples  — export a Turtle sample for semantic validation

Source crosswalk: data/witsml-rdf-crosswalk.json (geolytics-dictionary)
WITSML namespace:  http://www.energistics.org/energyml/data/witsmlv2/2.0#
OSDU schema base:  https://schema.osdu.opengroup.org/json/master-data/
GeoSciML gsmlbh:   http://geosciml.org/def/gsmlbh#
GeoSciML gsmlb:    http://geosciml.org/def/gsmlb#
QUDT units:        http://qudt.org/vocab/unit/
QUDT quantities:   http://qudt.org/vocab/quantitykind/
"""

from __future__ import annotations

import logging
import textwrap
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Namespace constants
# ---------------------------------------------------------------------------

_WITSML_NS = "http://www.energistics.org/energyml/data/witsmlv2/2.0#"
_OSDU_BASE = "https://schema.osdu.opengroup.org/json/master-data/"
_OSDU_WPC_BASE = "https://schema.osdu.opengroup.org/json/work-product-component/"
_OSDU_REF_BASE = "https://schema.osdu.opengroup.org/json/reference-data/"
_GEO_NS = "https://geolytics.petrobras.com.br/dict/"
_GSMLBH_NS = "http://geosciml.org/def/gsmlbh#"
_GSMLB_NS = "http://geosciml.org/def/gsmlb#"
_QUDT_UNIT = "http://qudt.org/vocab/unit/"
_QUDT_QK = "http://qudt.org/vocab/quantitykind/"
_PROV_NS = "https://www.w3.org/ns/prov#"

# ---------------------------------------------------------------------------
# NODE_TYPE_ALIGNMENT
# Maps every Neo4j label present in the Volve graph to its canonical URIs.
# Keys must match cypher_label values used by entity_extractor_enriched.py.
# ---------------------------------------------------------------------------

NODE_TYPE_ALIGNMENT: dict[str, dict[str, str | None]] = {
    # ------------------------------------------------------------------
    # Well — root entity, single surface location
    # ------------------------------------------------------------------
    "Well": {
        "witsml_class": "Well",
        "witsml_uri": f"{_WITSML_NS}Well",
        "osdu_kind": "opendes:osdu:master-data--Well:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Well.1.0.0.json",
        "geosciml_class": "gsmlbh:Borehole",
        "geosciml_uri": f"{_GSMLBH_NS}Borehole",
        "geo_uri": f"{_GEO_NS}Well",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # Wellbore — individual borehole within a well
    # ------------------------------------------------------------------
    "Wellbore": {
        "witsml_class": "Wellbore",
        "witsml_uri": f"{_WITSML_NS}Wellbore",
        "osdu_kind": "opendes:osdu:master-data--Wellbore:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Wellbore.1.0.0.json",
        "geosciml_class": "gsmlbh:Borehole",
        "geosciml_uri": f"{_GSMLBH_NS}Borehole",
        "geo_uri": f"{_GEO_NS}Wellbore",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # Trajectory — directional survey of a wellbore
    # ------------------------------------------------------------------
    "Trajectory": {
        "witsml_class": "Trajectory",
        "witsml_uri": f"{_WITSML_NS}Trajectory",
        "osdu_kind": "opendes:osdu:master-data--Trajectory:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Trajectory.1.0.0.json",
        "geosciml_class": "gsmlbh:BoreholeInterval",
        "geosciml_uri": f"{_GSMLBH_NS}BoreholeInterval",
        "geo_uri": f"{_GEO_NS}Trajectory",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # TrajectoryStation — individual survey measurement (MD/Inc/Az)
    # ------------------------------------------------------------------
    "TrajectoryStation": {
        "witsml_class": "TrajectoryStation",
        "witsml_uri": f"{_WITSML_NS}TrajectoryStation",
        "osdu_kind": "opendes:osdu:master-data--TrajectoryStation:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}TrajectoryStation.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}TrajectoryStation",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # WellboreMarker — formation top intersection with wellbore
    # ------------------------------------------------------------------
    "WellboreMarker": {
        "witsml_class": "WellboreMarker",
        "witsml_uri": f"{_WITSML_NS}WellboreMarker",
        "osdu_kind": "opendes:osdu:master-data--WellboreMarker:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}WellboreMarker.1.0.0.json",
        "geosciml_class": "gsmlbh:BoreholeInterval",
        "geosciml_uri": f"{_GSMLBH_NS}BoreholeInterval",
        "geo_uri": f"{_GEO_NS}WellboreMarker",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # FormationMarker — geological formation top identified in wellbore
    # ------------------------------------------------------------------
    "FormationMarker": {
        "witsml_class": "FormationMarker",
        "witsml_uri": f"{_WITSML_NS}FormationMarker",
        "osdu_kind": "opendes:osdu:master-data--FormationMarker:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}FormationMarker.1.0.0.json",
        "geosciml_class": "gsmlbh:BoreholeInterval",
        "geosciml_uri": f"{_GSMLBH_NS}BoreholeInterval",
        "geo_uri": f"{_GEO_NS}FormationMarker",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # Formation — geological unit (used by Volve entity extractor)
    # Mapped to GeoSciML GeologicUnit rather than a WITSML class.
    # ------------------------------------------------------------------
    "Formation": {
        "witsml_class": None,
        "witsml_uri": None,
        "osdu_kind": "opendes:osdu:reference-data--GeologicUnitType:1.0.0",
        "osdu_uri": f"{_OSDU_REF_BASE}GeologicUnitType.1.0.0.json",
        "geosciml_class": "gsmlb:GeologicUnit",
        "geosciml_uri": f"{_GSMLB_NS}GeologicUnit",
        "geo_uri": f"{_GEO_NS}Formacao",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # MudLog — drilling fluid gas and cuttings log
    # ------------------------------------------------------------------
    "MudLog": {
        "witsml_class": "MudLog",
        "witsml_uri": f"{_WITSML_NS}MudLog",
        "osdu_kind": "opendes:osdu:master-data--MudLog:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}MudLog.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}MudLog",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # MudLogInterval / MudLogReport — per-interval cuttings report
    # The Volve graph uses "MudLogInterval" as the Neo4j label.
    # ------------------------------------------------------------------
    "MudLogInterval": {
        "witsml_class": "MudLog",
        "witsml_uri": f"{_WITSML_NS}MudLog",
        "osdu_kind": "opendes:osdu:master-data--MudLog:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}MudLog.1.0.0.json",
        "geosciml_class": "gsmlbh:BoreholeInterval",
        "geosciml_uri": f"{_GSMLBH_NS}BoreholeInterval",
        "geo_uri": f"{_GEO_NS}MudLogReport",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # LogCurve — well log depth-indexed data curve
    # ------------------------------------------------------------------
    "LogCurve": {
        "witsml_class": "LogCurve",
        "witsml_uri": f"{_WITSML_NS}LogCurve",
        "osdu_kind": "opendes:osdu:master-data--LogCurve:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}LogCurve.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}LogCurve",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # Channel — real-time MWD/LWD data channel
    # ------------------------------------------------------------------
    "Channel": {
        "witsml_class": "Channel",
        "witsml_uri": f"{_WITSML_NS}Channel",
        "osdu_kind": "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
        "osdu_uri": f"{_OSDU_WPC_BASE}TimeSeriesData.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}Channel",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # ChannelSet — collection of channels sharing one depth/time index
    # ------------------------------------------------------------------
    "ChannelSet": {
        "witsml_class": "ChannelSet",
        "witsml_uri": f"{_WITSML_NS}ChannelSet",
        "osdu_kind": "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
        "osdu_uri": f"{_OSDU_WPC_BASE}TimeSeriesData.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}ChannelSet",
        "prov_alignment": f"{_PROV_NS}Collection",
    },
    # ------------------------------------------------------------------
    # Rig — drilling rig (platform, FPSS, land rig)
    # ------------------------------------------------------------------
    "Rig": {
        "witsml_class": "Rig",
        "witsml_uri": f"{_WITSML_NS}Rig",
        "osdu_kind": "opendes:osdu:master-data--Rig:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Rig.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}Rig",
        "prov_alignment": f"{_PROV_NS}Agent",
    },
    # ------------------------------------------------------------------
    # BHARun — bottom hole assembly run period
    # Volve uses "BHARun" as Neo4j label.
    # ------------------------------------------------------------------
    "BHARun": {
        "witsml_class": "BhaRun",
        "witsml_uri": f"{_WITSML_NS}BhaRun",
        "osdu_kind": "opendes:osdu:master-data--BhaRun:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}BhaRun.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}BhaRun",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # Tubular — BHA component assembly
    # ------------------------------------------------------------------
    "Tubular": {
        "witsml_class": "Tubular",
        "witsml_uri": f"{_WITSML_NS}Tubular",
        "osdu_kind": "opendes:osdu:master-data--Tubular:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Tubular.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}Tubular",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # BitRecord — drill bit usage record (IADC grading)
    # ------------------------------------------------------------------
    "BitRecord": {
        "witsml_class": "BitRecord",
        "witsml_uri": f"{_WITSML_NS}BitRecord",
        "osdu_kind": "opendes:osdu:master-data--BitRecord:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}BitRecord.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}BitRecord",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # DailyReport / OpsReport — 24-hour operational summary (DDR)
    # Volve entity extractor writes "DailyReport" as the label.
    # ------------------------------------------------------------------
    "DailyReport": {
        "witsml_class": "OpsReport",
        "witsml_uri": f"{_WITSML_NS}OpsReport",
        "osdu_kind": "opendes:osdu:master-data--OpsReport:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}OpsReport.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}OpsReport",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # DrillingActivity — coded time-interval activity within a DDR
    # ------------------------------------------------------------------
    "DrillingActivity": {
        "witsml_class": "DrillingActivity",
        "witsml_uri": f"{_WITSML_NS}DrillingActivity",
        "osdu_kind": "opendes:osdu:master-data--DrillingActivity:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}DrillingActivity.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}DrillingActivity",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # Message — WITSML real-time message object
    # ------------------------------------------------------------------
    "Message": {
        "witsml_class": "Message",
        "witsml_uri": f"{_WITSML_NS}Message",
        "osdu_kind": "opendes:osdu:master-data--Message:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Message.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}Message",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # FluidsReport — drilling fluid rheology report
    # ------------------------------------------------------------------
    "FluidsReport": {
        "witsml_class": "FluidsReport",
        "witsml_uri": f"{_WITSML_NS}FluidsReport",
        "osdu_kind": "opendes:osdu:master-data--FluidsReport:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}FluidsReport.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}FluidsReport",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # CementJob — primary / remedial cementing operation
    # ------------------------------------------------------------------
    "CementJob": {
        "witsml_class": "CementJob",
        "witsml_uri": f"{_WITSML_NS}CementJob",
        "osdu_kind": "opendes:osdu:master-data--CementJob:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}CementJob.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}CementJob",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # CasingDesign — casing string design specification
    # Volve ingestion may not have a WITSML 2.0 direct equivalent;
    # mapped to the closest available OSDU kind.
    # ------------------------------------------------------------------
    "CasingDesign": {
        "witsml_class": "CasingDesign",
        "witsml_uri": f"{_WITSML_NS}CasingDesign",
        "osdu_kind": "opendes:osdu:master-data--CasingDesign:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}CasingDesign.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}CasingDesign",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # Risk — operational risk record
    # ------------------------------------------------------------------
    "Risk": {
        "witsml_class": "Risk",
        "witsml_uri": f"{_WITSML_NS}Risk",
        "osdu_kind": "opendes:osdu:master-data--Risk:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Risk.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}Risk",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # SurveyProgram — directional survey program specification
    # ------------------------------------------------------------------
    "SurveyProgram": {
        "witsml_class": "SurveyProgram",
        "witsml_uri": f"{_WITSML_NS}SurveyProgram",
        "osdu_kind": "opendes:osdu:master-data--SurveyProgram:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}SurveyProgram.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}SurveyProgram",
        "prov_alignment": f"{_PROV_NS}Plan",
    },
    # ------------------------------------------------------------------
    # WellTest — DST / RFT / production test
    # ------------------------------------------------------------------
    "WellTest": {
        "witsml_class": "WellTest",
        "witsml_uri": f"{_WITSML_NS}WellTest",
        "osdu_kind": "opendes:osdu:master-data--WellTest:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}WellTest.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}WellTest",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # StimJob — hydraulic fracturing / acidizing job
    # ------------------------------------------------------------------
    "StimJob": {
        "witsml_class": "StimJob",
        "witsml_uri": f"{_WITSML_NS}StimJob",
        "osdu_kind": "opendes:osdu:master-data--StimJob:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}StimJob.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}StimJob",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
    # ------------------------------------------------------------------
    # Drillstring — complete drill string assembly
    # ------------------------------------------------------------------
    "Drillstring": {
        "witsml_class": "Drillstring",
        "witsml_uri": f"{_WITSML_NS}Drillstring",
        "osdu_kind": "opendes:osdu:master-data--Tubular:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}Tubular.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}Drillstring",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # Lithology — CGI Simple Lithology vocabulary concept
    # Not a WITSML class; referenced as a controlled vocabulary value.
    # ------------------------------------------------------------------
    "Lithology": {
        "witsml_class": None,
        "witsml_uri": None,
        "osdu_kind": "opendes:osdu:reference-data--LithologyType:1.0.0",
        "osdu_uri": f"{_OSDU_REF_BASE}LithologyType.1.0.0.json",
        "geosciml_class": "gsmlb:GeologicUnit",
        "geosciml_uri": f"{_GSMLB_NS}GeologicUnit",
        "geo_uri": f"{_GEO_NS}Litologia",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # DrillingFluid — fluid system used during drilling
    # ------------------------------------------------------------------
    "DrillingFluid": {
        "witsml_class": "FluidsReport",
        "witsml_uri": f"{_WITSML_NS}FluidsReport",
        "osdu_kind": "opendes:osdu:master-data--FluidsReport:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}FluidsReport.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}FluidsReport",
        "prov_alignment": f"{_PROV_NS}Entity",
    },
    # ------------------------------------------------------------------
    # DrillingEvent — NPT or operational event (stuck pipe, kick, etc.)
    # ------------------------------------------------------------------
    "DrillingEvent": {
        "witsml_class": "DrillingActivity",
        "witsml_uri": f"{_WITSML_NS}DrillingActivity",
        "osdu_kind": "opendes:osdu:master-data--DrillingActivity:1.0.0",
        "osdu_uri": f"{_OSDU_BASE}DrillingActivity.1.0.0.json",
        "geosciml_class": None,
        "geosciml_uri": None,
        "geo_uri": f"{_GEO_NS}DrillingActivity",
        "prov_alignment": f"{_PROV_NS}Activity",
    },
}

# ---------------------------------------------------------------------------
# PROPERTY_ALIGNMENT
# Maps Neo4j property names (as stored after Volve ingestion) to WITSML 2.0
# property names, physical units, and QUDT ontology URIs.
# ---------------------------------------------------------------------------

PROPERTY_ALIGNMENT: dict[str, dict[str, str | None]] = {
    # --- depth properties ---
    "md_m": {
        "witsml_property": "md",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "Measured depth in metres",
    },
    "tvd_m": {
        "witsml_property": "tvd",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "True vertical depth in metres",
    },
    "tvdss_m": {
        "witsml_property": "tvdss",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "True vertical depth sub-sea in metres",
    },
    "md_top_m": {
        "witsml_property": "mdTop",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "Measured depth of interval top",
    },
    "md_bottom_m": {
        "witsml_property": "mdBottom",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "Measured depth of interval base",
    },
    # --- directional survey ---
    "incl_deg": {
        "witsml_property": "incl",
        "witsml_uom": "dega",
        "qudt_unit": f"{_QUDT_UNIT}DEG",
        "qudt_quantity": f"{_QUDT_QK}Angle",
        "description": "Borehole inclination from vertical [0–180 deg]",
    },
    "azi_deg": {
        "witsml_property": "azi",
        "witsml_uom": "dega",
        "qudt_unit": f"{_QUDT_UNIT}DEG",
        "qudt_quantity": f"{_QUDT_QK}Angle",
        "description": "Borehole azimuth from true north [0–360 deg]",
    },
    "dls_deg_30m": {
        "witsml_property": "dls",
        "witsml_uom": "dega/30m",
        "qudt_unit": f"{_QUDT_UNIT}DEG-PER-M",
        "qudt_quantity": f"{_QUDT_QK}Curvature",
        "description": "Dog leg severity in degrees per 30 metres",
    },
    "disp_ns_m": {
        "witsml_property": "dispNs",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "Cumulative North-South displacement",
    },
    "disp_ew_m": {
        "witsml_property": "dispEw",
        "witsml_uom": "m",
        "qudt_unit": f"{_QUDT_UNIT}M",
        "qudt_quantity": f"{_QUDT_QK}Length",
        "description": "Cumulative East-West displacement",
    },
    # --- drilling performance ---
    "rop_m_h": {
        "witsml_property": "rop",
        "witsml_uom": "m/h",
        "qudt_unit": f"{_QUDT_UNIT}M-PER-HR",
        "qudt_quantity": f"{_QUDT_QK}Speed",
        "description": "Rate of penetration in metres per hour",
    },
    "wob_kn": {
        "witsml_property": "wob",
        "witsml_uom": "kN",
        "qudt_unit": f"{_QUDT_UNIT}KiloN",
        "qudt_quantity": f"{_QUDT_QK}Force",
        "description": "Weight on bit in kilonewtons",
    },
    "torque_kn_m": {
        "witsml_property": "torque",
        "witsml_uom": "kN.m",
        "qudt_unit": f"{_QUDT_UNIT}N-M",
        "qudt_quantity": f"{_QUDT_QK}Torque",
        "description": "Rotary torque in kilonewton-metres",
    },
    "rpm": {
        "witsml_property": "rpm",
        "witsml_uom": "rpm",
        "qudt_unit": f"{_QUDT_UNIT}REV-PER-MIN",
        "qudt_quantity": f"{_QUDT_QK}AngularVelocity",
        "description": "Rotary speed in revolutions per minute",
    },
    "flow_rate_l_min": {
        "witsml_property": "flowrateMud",
        "witsml_uom": "L/min",
        "qudt_unit": f"{_QUDT_UNIT}L-PER-MIN",
        "qudt_quantity": f"{_QUDT_QK}VolumeFlowRate",
        "description": "Mud circulating flow rate in litres per minute",
    },
    # --- fluid properties ---
    "mud_density_kg_m3": {
        "witsml_property": "density",
        "witsml_uom": "kg/m3",
        "qudt_unit": f"{_QUDT_UNIT}KiloGM-PER-M3",
        "qudt_quantity": f"{_QUDT_QK}MassDensity",
        "description": "Mud density in kilograms per cubic metre",
    },
    "mud_viscosity_s": {
        "witsml_property": "visFunnel",
        "witsml_uom": "s",
        "qudt_unit": f"{_QUDT_UNIT}SEC",
        "qudt_quantity": f"{_QUDT_QK}Time",
        "description": "Marsh funnel viscosity in seconds",
    },
    "plastic_viscosity_mpa_s": {
        "witsml_property": "pv",
        "witsml_uom": "mPa.s",
        "qudt_unit": f"{_QUDT_UNIT}MilliPA-SEC",
        "qudt_quantity": f"{_QUDT_QK}DynamicViscosity",
        "description": "Plastic viscosity (PV) in millipascal-seconds",
    },
    "yield_point_pa": {
        "witsml_property": "yp",
        "witsml_uom": "Pa",
        "qudt_unit": f"{_QUDT_UNIT}PA",
        "qudt_quantity": f"{_QUDT_QK}Pressure",
        "description": "Yield point in pascals",
    },
    # --- pressure ---
    "pore_pressure_psi": {
        "witsml_property": "presShutIn",
        "witsml_uom": "psi",
        "qudt_unit": f"{_QUDT_UNIT}PSI",
        "qudt_quantity": f"{_QUDT_QK}Pressure",
        "description": "Pore pressure / shut-in pressure in PSI",
    },
    "standpipe_pressure_psi": {
        "witsml_property": "presSpm",
        "witsml_uom": "psi",
        "qudt_unit": f"{_QUDT_UNIT}PSI",
        "qudt_quantity": f"{_QUDT_QK}Pressure",
        "description": "Standpipe pressure in PSI",
    },
    # --- temperature ---
    "temp_bottom_hole_c": {
        "witsml_property": "tempBottomHole",
        "witsml_uom": "degC",
        "qudt_unit": f"{_QUDT_UNIT}DEG_C",
        "qudt_quantity": f"{_QUDT_QK}Temperature",
        "description": "Bottom-hole temperature in degrees Celsius",
    },
    # --- formation / dip ---
    "dip_angle_deg": {
        "witsml_property": "dipAngle",
        "witsml_uom": "dega",
        "qudt_unit": f"{_QUDT_UNIT}DEG",
        "qudt_quantity": f"{_QUDT_QK}Angle",
        "description": "Formation dip angle in degrees",
    },
    "dip_direction_deg": {
        "witsml_property": "dipDirection",
        "witsml_uom": "dega",
        "qudt_unit": f"{_QUDT_UNIT}DEG",
        "qudt_quantity": f"{_QUDT_QK}Angle",
        "description": "Formation dip direction azimuth in degrees",
    },
    # --- gas shows ---
    "total_gas_ppm": {
        "witsml_property": "gas",
        "witsml_uom": "ppm",
        "qudt_unit": f"{_QUDT_UNIT}PPM",
        "qudt_quantity": f"{_QUDT_QK}DimensionlessRatio",
        "description": "Total gas concentration in parts per million",
    },
    "methane_c1_ppm": {
        "witsml_property": "c1",
        "witsml_uom": "ppm",
        "qudt_unit": f"{_QUDT_UNIT}PPM",
        "qudt_quantity": f"{_QUDT_QK}DimensionlessRatio",
        "description": "Methane (C1) concentration in PPM",
    },
}

# ---------------------------------------------------------------------------
# Cypher helpers
# ---------------------------------------------------------------------------

_SET_TEMPLATE = """\
MATCH (n:{label})
WHERE n.witsml_uri IS NULL
SET
  n.witsml_uri   = $witsml_uri,
  n.witsml_class = $witsml_class,
  n.osdu_kind    = $osdu_kind,
  n.osdu_uri     = $osdu_uri,
  n.geosciml_uri = $geosciml_uri,
  n.geo_uri      = $geo_uri,
  n.prov_alignment = $prov_alignment,
  n._aligned     = true
RETURN count(n) AS updated
"""


def build_node_uri_cypher(node_label: str) -> str:
    """Return a parameterised Cypher statement that adds URI properties to all
    nodes of *node_label* that have not yet been aligned (``_aligned IS NULL``).

    The statement uses named parameters so it can be executed with::

        driver.execute_query(cypher, alignment[node_label])

    Parameters
    ----------
    node_label:
        A Neo4j label present in NODE_TYPE_ALIGNMENT.

    Returns
    -------
    str
        Cypher string with ``{label}`` substituted.

    Raises
    ------
    KeyError
        If *node_label* is not in NODE_TYPE_ALIGNMENT.
    """
    if node_label not in NODE_TYPE_ALIGNMENT:
        raise KeyError(
            f"Label '{node_label}' not in NODE_TYPE_ALIGNMENT. "
            f"Available: {sorted(NODE_TYPE_ALIGNMENT)}"
        )
    return _SET_TEMPLATE.format(label=node_label)


# ---------------------------------------------------------------------------
# run_alignment
# ---------------------------------------------------------------------------

def run_alignment(
    driver: Any,
    labels: list[str] | None = None,
) -> dict[str, int]:
    """Add WITSML/OSDU semantic URI properties to Neo4j nodes in batch.

    Iterates over *labels* (or all labels in NODE_TYPE_ALIGNMENT if None),
    runs one Cypher SET statement per label, and returns a summary of how
    many nodes were updated per label.

    Parameters
    ----------
    driver:
        A ``neo4j.GraphDatabase.driver`` instance (or any object exposing
        ``execute_query(query, parameters_)``).
    labels:
        Optional list of Neo4j labels to align.  Defaults to all labels
        in NODE_TYPE_ALIGNMENT.

    Returns
    -------
    dict[str, int]
        ``{label: count_updated}`` for every label processed.
    """
    target_labels: list[str] = labels or list(NODE_TYPE_ALIGNMENT.keys())
    results: dict[str, int] = {}

    for label in target_labels:
        if label not in NODE_TYPE_ALIGNMENT:
            log.warning("Skipping unknown label: %s", label)
            results[label] = 0
            continue

        alignment = NODE_TYPE_ALIGNMENT[label]
        cypher = build_node_uri_cypher(label)

        try:
            records, _, _ = driver.execute_query(cypher, alignment)
            updated = records[0]["updated"] if records else 0
            results[label] = updated
            log.info("Aligned %-24s — %d node(s) updated", label, updated)
        except Exception:  # noqa: BLE001
            log.exception("Failed to align label '%s'", label)
            results[label] = -1

    total = sum(v for v in results.values() if v > 0)
    log.info("Alignment complete. Total nodes updated: %d", total)
    return results


# ---------------------------------------------------------------------------
# generate_rdf_triples
# ---------------------------------------------------------------------------

_TURTLE_PREFIXES = """\
@prefix geo:    <https://geolytics.petrobras.com.br/dict/> .
@prefix witsml: <http://www.energistics.org/energyml/data/witsmlv2/2.0#> .
@prefix gsmlbh: <http://geosciml.org/def/gsmlbh#> .
@prefix gsmlb:  <http://geosciml.org/def/gsmlb#> .
@prefix inst:   <https://geolytics.petrobras.com.br/dict/instance/> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:    <http://www.w3.org/2002/07/owl#> .
@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .
@prefix qudt:   <http://qudt.org/vocab/unit/> .
@prefix prov:   <https://www.w3.org/ns/prov#> .

"""

_NODE_QUERY = """\
MATCH (n:{label})
WHERE n.witsml_uri IS NOT NULL
RETURN
  n.name        AS name,
  elementId(n)  AS eid,
  properties(n) AS props
LIMIT {limit}
"""

_SCALAR_PROPS = {
    "name": "skos:prefLabel",
    "md_m": "geo:md",
    "tvd_m": "geo:tvd",
    "tvdss_m": "geo:tvdss",
    "incl_deg": "geo:incl",
    "azi_deg": "geo:azi",
    "dls_deg_30m": "geo:dls",
    "dip_angle_deg": "geo:dipAngle",
    "dip_direction_deg": "geo:dipDirection",
    "total_gas_ppm": "geo:gas",
    "mud_density_kg_m3": "geo:density",
    "temp_bottom_hole_c": "geo:tempBottomHole",
}


def _sanitise_id(raw: str) -> str:
    """Convert a Neo4j elementId or name into a safe URI fragment."""
    return str(raw).replace(":", "-").replace(" ", "_").replace("/", "-")


def generate_rdf_triples(
    driver: Any,
    node_label: str,
    limit: int = 100,
) -> str:
    """Generate a Turtle serialisation for a sample of aligned Neo4j nodes.

    Useful for:
    - Spot-checking WITSML → RDF alignment correctness
    - Loading into a SPARQL triplestore (Apache Jena Fuseki, GraphDB) for
      federated query development
    - Validation with ``python scripts/validate-shacl.py`` from
      geolytics-dictionary

    Parameters
    ----------
    driver:
        A ``neo4j.GraphDatabase.driver`` instance.
    node_label:
        Neo4j label to sample (must be in NODE_TYPE_ALIGNMENT).
    limit:
        Maximum number of nodes to emit.  Defaults to 100.

    Returns
    -------
    str
        Valid Turtle document as a string.

    Raises
    ------
    KeyError
        If *node_label* is not in NODE_TYPE_ALIGNMENT.
    """
    if node_label not in NODE_TYPE_ALIGNMENT:
        raise KeyError(
            f"Label '{node_label}' not in NODE_TYPE_ALIGNMENT. "
            f"Available: {sorted(NODE_TYPE_ALIGNMENT)}"
        )

    alignment = NODE_TYPE_ALIGNMENT[node_label]
    geo_class_uri = alignment.get("geo_uri", "")
    # Derive prefixed class name from URI
    geo_class_curie = geo_class_uri.replace(
        "https://geolytics.petrobras.com.br/dict/", "geo:"
    )
    witsml_uri = alignment.get("witsml_uri")
    geosciml_uri = alignment.get("geosciml_uri")
    prov_uri = alignment.get("prov_alignment")

    query = _NODE_QUERY.format(label=node_label, limit=limit)

    try:
        records, _, _ = driver.execute_query(query)
    except Exception:  # noqa: BLE001
        log.exception("Could not query '%s' nodes for RDF export", node_label)
        return ""

    lines: list[str] = [_TURTLE_PREFIXES]
    lines.append(f"# {node_label} — {len(records)} node(s) exported\n")

    for rec in records:
        eid = _sanitise_id(rec["eid"])
        name = rec.get("name") or eid
        props: dict[str, Any] = rec.get("props") or {}

        subject = f"inst:{node_label.lower()}-{eid}"

        triples: list[str] = [f"{subject}"]
        triples.append(f"    a {geo_class_curie} ;")

        if witsml_uri:
            triples.append(f'    owl:sameAs <{witsml_uri}> ;')
        if geosciml_uri:
            triples.append(f'    owl:sameAs <{geosciml_uri}> ;')
        if prov_uri:
            triples.append(f'    prov:wasAttributedTo <{prov_uri}> ;')

        safe_name = str(name).replace('"', '\\"')
        triples.append(f'    skos:prefLabel "{safe_name}"@en ;')

        for neo_prop, rdf_predicate in _SCALAR_PROPS.items():
            value = props.get(neo_prop)
            if value is None:
                continue
            if neo_prop == "name":
                continue  # already emitted above
            try:
                float_val = float(value)
                triples.append(
                    f'    {rdf_predicate} "{float_val}"^^xsd:decimal ;'
                )
            except (TypeError, ValueError):
                safe_v = str(value).replace('"', '\\"')
                triples.append(
                    f'    {rdf_predicate} "{safe_v}"^^xsd:string ;'
                )

        # Replace last ";" with "."
        if triples[-1].endswith(" ;"):
            triples[-1] = triples[-1][:-2] + " ."
        else:
            triples.append("    .")

        lines.append("\n".join(triples))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import os

    from neo4j import GraphDatabase  # type: ignore[import-untyped]

    parser = argparse.ArgumentParser(
        description="Add WITSML/OSDU semantic URIs to SPE Volve Neo4j nodes."
    )
    parser.add_argument(
        "--labels",
        nargs="*",
        help="Node labels to align (default: all in NODE_TYPE_ALIGNMENT).",
    )
    parser.add_argument(
        "--rdf-label",
        help="Export RDF Turtle for this label after alignment.",
    )
    parser.add_argument(
        "--rdf-limit",
        type=int,
        default=100,
        help="Max nodes to include in RDF export (default: 100).",
    )
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    )
    parser.add_argument(
        "--user",
        default=os.getenv("NEO4J_USER", "neo4j"),
    )
    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PASSWORD", ""),
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s  %(message)s",
    )

    with GraphDatabase.driver(args.uri, auth=(args.user, args.password)) as drv:
        summary = run_alignment(drv, args.labels)
        for lbl, count in summary.items():
            print(f"  {lbl:<28} {count:>6} node(s) updated")

        if args.rdf_label:
            turtle = generate_rdf_triples(drv, args.rdf_label, args.rdf_limit)
            print("\n" + turtle)
