"""
acronym_expander.py — SPE Volve NLP pre-processing module

Disambiguates and expands acronyms found in daily drilling reports
(DailyReport.summary_24hr, Message.message_text) before embedding,
improving recall in vector search.

Acronym dictionary is curated from data/acronyms.json (1157 entries)
and embedded here — no JSON is read at runtime.

Usage (CLI):
    echo "RIH to 4200m MD, ROP 35 m/hr, WOB 12 klbs" | python acronym_expander.py
"""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import Driver


# ---------------------------------------------------------------------------
# Curated drilling acronym dictionary
# Source: data/acronyms.json filtered to drilling-relevant categories,
# augmented with industry-standard terms not present in the source file.
# ---------------------------------------------------------------------------

DRILLING_ACRONYMS: dict[str, str] = {
    # -----------------------------------------------------------------------
    # Operations
    # -----------------------------------------------------------------------
    "RIH": "Running In Hole",
    "POOH": "Pulling Out of Hole",
    "POH": "Pull Out of Hole",
    "TIH": "Trip in Hole",
    "TOH": "Trip Out of Hole",
    "GIH": "Going In Hole",
    "WIH": "Went in Hole",
    "WOW": "Waiting on Weather",
    "WOC": "Waiting on Cement",           # default; polysemic — see CONTEXT_SENSITIVE_ACRONYMS
    "POB": "Personnel on Board",
    "DWOP": "Drilling Well on Paper",
    "DRLG": "Drilling",
    "DA": "Drilling Ahead",
    "DD": "Drilling Deeper",
    "MPD": "Managed Pressure Drilling",
    "DGD": "Dual-Gradient Drilling",
    "PMCD": "Pressurized Mud Cap Drilling",
    "CTD": "Coiled Tubing Drilling",
    "SDP": "Simultaneous Drilling and Production",
    "JPD": "Jointed Pipe Drilling",
    "AWD": "Analysis While Drilling",
    "PWD": "Pressure While Drilling",
    "IDC": "Intangible Drilling Costs",
    "TDC": "Tangible Drilling Costs",
    "BDP": "Daily Drilling Report",
    "DDA": "Drilling Data Acquisition System",
    "DIP": "Drilling Instrumentation Package",
    "ACZ": "Acidizing",
    "CRG": "Coring",
    "LWI": "Light Well Intervention",
    "W/O": "Workover",
    "WO": "Workover",
    "WKO": "Workover",
    "C/WO": "Completion and Workover",
    "IWOCS": "Installation and Workover Control System",
    "WOCS": "Workover Control System",
    "EOR": "Enhanced Oil Recovery",
    "IOR": "Improved Oil Recovery",
    "GL": "Gas Lift",
    "GLC": "Continuous Gas Lift",
    "GI": "Gas Injection",
    "FPSO": "Floating Production Storage and Offloading",
    "E&P": "Exploration and Production",
    "KOP": "Kick-Off Point",
    "C&CM": "Circulate and Condition the Mud",
    "LCM": "Lost Circulation Material",
    "GCM": "Gas Cut Mud",
    "SRT": "Step Rate Test",
    "PCD": "Pressure Controlled Drilling",
    "PDCL": "Perforating Depth Control Log",
    "OGEOMEC": "Geomechanical Occurrences",
    "RMG": "Geomechanical Monitoring Report",
    "OWDD": "Old Well Drilled Deeper",
    "J&A": "Junked and Abandoned",
    "DMA": "Unmooring Movement and Mooring",
    # -----------------------------------------------------------------------
    # Drilling performance
    # -----------------------------------------------------------------------
    "ROP": "Rate of Penetration",
    "WOB": "Weight on Bit",
    "RPM": "Revolutions per Minute",
    "TQ": "Torque",
    "SPP": "Standpipe Pressure",
    "GPM": "Gallons per Minute",
    "ECD": "Equivalent Circulating Density",
    "EMW": "Equivalent Mud Weight",
    "MW": "Mud Weight",
    "HHP": "Hydraulic Horsepower",
    "BUR": "Buildup Rate",
    "DLS": "Dog Leg Severity",
    "DSL": "Dog Leg Severity",
    "MUT": "Makeup Torque",
    "IDR": "Instantaneous Drilling Rate",
    # -----------------------------------------------------------------------
    # BHA and equipment
    # -----------------------------------------------------------------------
    "BHA": "Bottom-Hole Assembly",
    "PDC": "Polycrystalline Diamond Compact",
    "MWD": "Measure While Drilling",
    "LWD": "Logging While Drilling",
    "RSS": "Rotary Steerable System",
    "PDM": "Positive Displacement Motor",
    "NBI": "New Bit Installed",
    "HWDP": "Heavy Weight Drillpipe",
    "HW": "Heavy Weight Drillpipe",
    "DC": "Drill Collar",
    "STBL": "Stabilizer",
    "BOP": "Blowout Preventer",
    "IBOP": "Internal Blowout Preventer",
    "KB": "Kelly Bushing",
    "RKB": "Rotary Kelly Bushing",
    "RT": "Rotary Table",
    "DF": "Derrick Floor",
    "DPP": "Drill Pipe Pressure",
    "DPR": "Drill Pipe Riser",
    "CT": "Coiled Tubing",
    "CTM": "Coiled Tubing Measurement",
    "DSC": "Drill String Compensator",
    "JB": "Junk Basket",
    "PKR": "Packer",
    "PCP": "Progressive Cavity Pump",
    "ESP": "Electrical Submersible Pump",
    "SBR": "Shear Blind Ram",
    "LPR": "Lower Pipe Ram",
    "UPR": "Upper Pipe Ram",
    "VBR": "Variable Bore Rams",
    "LMRP": "Lower Marine Riser Package",
    "RTCB": "Round Trip to Change the Bit",
    "NB": "New Bit",
    "RU": "Rigging Up",
    "NU": "Nippling Up",
    "SIDPP": "Shut-in Drill Pipe Pressure",
    "BHHP": "Bit Hydraulic Horsepower",
    "PSB": "Weight on Bit",
    "DST": "Drill Stem Test",
    "MDT": "Modular Formation Dynamics Tester",
    "ABT": "Annular Barrier Tool",
    "CDRS": "Common Drilling Reporting System",
    "DCP": "Drillers Control Panel",
    "FERJAT": "Wellhead Jetting Tool",
    "LDDP": "Lay Down Drill Pipe",
    "ML": "Mud Logging",
    "MLP": "Mudlift Pump",
    # -----------------------------------------------------------------------
    # Survey and directional measurements
    # -----------------------------------------------------------------------
    "MD": "Measured Depth",
    "TVD": "True Vertical Depth",
    "THL": "Total Hole Length",
    "VD": "Vertical Depth",
    "INC": "Inclination",
    "AZM": "Azimuth",
    "DIP": "Dip Angle",
    "TD": "Total Depth",
    "ATD": "Authorized Total Depth",
    "OTD": "Old Total Depth",
    "KT": "Kick Tolerance",
    "PBD": "Plug-Back Depth",
    # -----------------------------------------------------------------------
    # Wireline and petrophysical logs
    # -----------------------------------------------------------------------
    "GR": "Gamma Ray",
    "RT": "Resistivity",                  # context-sensitive vs Rotary Table
    "MSFL": "Micro Spherically Focused Log",
    "NPHI": "Neutron Porosity",
    "RHOB": "Bulk Density",
    "SP": "Spontaneous Potential",         # polysemic — see CONTEXT_SENSITIVE_ACRONYMS
    "PLT": "Production Logging Tool",
    "CBL": "Cement Bond Log",
    "FDC": "Formation Density Compensated",
    "FDL": "Formation Density Log",
    "E LOG": "Electric Log",
    "CCL": "Casing Collar Locator",
    "CCCL": "Casing Collar Counter Log",
    "DSN": "Dual-Spaced Neutron Log",
    "DPL": "Deep Propagation Log",
    "EPL": "Electromagnetic Propagation Log",
    "FAL": "Formation Analysis Log",
    "DRX": "X-Ray Diffraction",
    "FRX": "X-Ray Fluorescence",
    "VDL": "Variable Density Log",
    "PCMO": "Passenger Car Motor Oil",
    "PDG": "Permanent Downhole Gauge",
    "DHPT": "Downhole Pressure and Temperature",
    "DPTT": "Downhole Pressure and Temperature Transmitter",
    "RTD": "Resistance Temperature Detector",
    "DTS": "Distributed Temperature Sensing",
    "NMR": "Nuclear Magnetic Resonance",
    "MRI": "Magnetic Resonance Imaging",
    # -----------------------------------------------------------------------
    # Non-productive time and problems
    # -----------------------------------------------------------------------
    "NPT": "Non-Productive Time",
    "ST": "Sidetrack",                    # polysemic — see CONTEXT_SENSITIVE_ACRONYMS
    "SC": "Stuck Condition",
    "HC": "Hydrocarbon",
    "WC": "Water Cut",                    # polysemic — see CONTEXT_SENSITIVE_ACRONYMS
    "LC": "Lost Circulation",
    "LCO": "Lost Circulation Occurrence",
    "DT": "Downtime",
    "SD": "Shutdown",
    "HAZOP": "Hazard and Operability Study",
    "HAZID": "Hazard Identification",
    # -----------------------------------------------------------------------
    # Well tests
    # -----------------------------------------------------------------------
    "LOT": "Leak Off Test",
    "FIT": "Formation Integrity Test",
    "RFT": "Repeat Formation Test",
    "XLOT": "Extended Leak Off Test",
    "AOF": "Absolute Open Flow",
    "DST": "Drill Stem Test",
    "TF": "Open Hole Drill Stem Test",
    "TFR": "Cased Hole Drill Stem Test",
    "ITT": "Isolation Test Tool",
    "SRT": "Step Rate Test",
    "PWD": "Pressure While Drilling",
    "TLD": "Long Duration Test",
    "MIT": "Materials In Transit",
    # -----------------------------------------------------------------------
    # Drilling fluids
    # -----------------------------------------------------------------------
    "OBM": "Oil Base Mud",
    "WBM": "Water Based Mud",
    "SBM": "Synthetic Base Mud",
    "FBA": "Water Based Mud",
    "pH": "Power of Hydrogen",
    "PV": "Plastic Viscosity",
    "YP": "Yield Point",
    "MBT": "Methylene Blue Test",
    "MBTE": "Methylene Blue Test Equivalent",
    "HTHP": "High Temperature High Pressure",
    "HP/HT": "High Pressure High Temperature",
    "HPHT": "High Pressure High Temperature",
    "HTHS": "High Temperature and High Shear",
    "GCU": "Gas Carried Under",
    "GTS": "Gas to Surface",
    "MTS": "Mud to Surface",
    "PHPA": "Partially Hydrolyzed PolyAcrylamide",
    "CMC": "Carboxymethyl Cellulose",
    "DEO": "Diesel Engine Oil",
    "MEG": "Monoethylene Glycol",
    "LDHI": "Low Dosage Hydrate Inhibitor",
    "CRA": "Corrosion-Resistant Alloy",
    "BWOC": "By Weight of Cement",
    "BWOW": "By Weight of Water",
    "DRA": "Drag Reducer Agent",
    # -----------------------------------------------------------------------
    # Casing and cement
    # -----------------------------------------------------------------------
    "CSG": "Casing",
    "LNG": "Liner",
    "LNR": "Liner",
    "TLBG": "Top of Liner Below Ground",
    "TOC": "Top of Cement",
    "WOC": "Waiting on Cement",
    "ECP": "External Casing Packer",
    "CHP": "Casing Head Pressure",
    "CH": "Casing Head",
    "CP": "Casing Pressure",
    "CPSI": "Casing Pressure Shut-In",
    "SICP": "Shut-In Casing Pressure",
    "CPN": "Casing Profile Nipple",
    "CMT": "Cement",
    # -----------------------------------------------------------------------
    # Production and reservoir
    # -----------------------------------------------------------------------
    "GOR": "Gas-Oil Ratio",
    "API": "American Petroleum Institute",
    "WCT": "Wet Christmas Tree",
    "WHP": "Wellhead Pressure",
    "WHT": "Wellhead Temperature",
    "THP": "Tubing Head Pressure",
    "BHP": "Bottom-Hole Pressure",
    "FTP": "Flowing Tubing Pressure",
    "FTHP": "Flowing Tubing Head Pressure",
    "SIBHP": "Shut-In Bottom-Hole Pressure",
    "BHFP": "Bottom-Hole Flow Pressure",
    "BHT": "Bottom-Hole Temperature",
    "BHS": "Bottom-Hole Sample",
    "BH": "Bottom Hole",
    "BHPSI": "Bottom-Hole Pressure Shut-In",
    "SIWH": "Stabilized Shut-In Wellhead Pressure",
    "SITHP": "Shut-In Tubing Head Pressure",
    "SITP": "Shut-In Tubing Pressure",
    "FP": "Flowing Pressure",
    "IFP": "Initial Flowing Pressure",
    "FFP": "Final Flowing Pressure",
    "FHP": "Final Hydrostatic Pressure",
    "ISIP": "Initial Shut-In Pressure",
    "FSIP": "Final Shut-In Pressure",
    "CIP": "Closed-In Pressure",
    "HP": "Hydrostatic Pressure",
    "MAOP": "Maximum Allowable Operating Pressure",
    "MASP": "Maximum Anticipated Surface Pressure",
    "MAWP": "Maximum Allowable Working Pressure",
    "WP": "Working Pressure",
    "OWC": "Oil-Water Contact",
    "GOC": "Gas-Oil Contact",
    "WOR": "Water-Oil Ratio",
    "RAO": "Water-Oil Ratio",
    "WGR": "Water-Gas Ratio",
    "RGO": "Gas-Oil Ratio",
    "RGL": "Gas-Liquid Ratio",
    "BOPD": "Barrels of Oil per Day",
    "BWPD": "Barrels of Water per Day",
    "BFPD": "Barrels of Fluid per Day",
    "BCPD": "Barrels of Condensate per Day",
    "BOEPD": "Barrels of Oil Equivalent per Day",
    "OOIP": "Original Oil In Place",
    "VOIP": "Volume of Oil in Place",
    "IP": "Productivity Index",
    "PI": "Productivity Index",
    "IPR": "Inflow Performance Relationship",
    "II": "Injectivity Index",
    "AOF": "Absolute Open Flow",
    "MER": "Maximum Efficient Rate",
    "GIR": "Gas Injection Rate",
    "PWRI": "Produced Water Reinjection",
    "DHI": "Direct Hydrocarbon Indicator",
    "OOIP": "Original Oil In Place",
    "ROS": "Residual Oil Saturation",
    "BSW": "Basic Sediments and Water",
    "S&W": "Sediment and Water",
    "GC": "Gas Cut",
    "OS": "Oil Show",
    "SO": "Show of Oil",
    "SG": "Show of Gas",
    "NOS": "No Oil Show",
    "SO&G": "Show of Oil and Gas",
    "SSO": "Slight Show of Oil",
    "SSG": "Slight Show of Gas",
    "NSO": "No Show of Oil",
    "O&G": "Oil and Gas",
    "BO": "Barrels of Oil",
    "BOE": "Barrels of Oil Equivalent",
    "WTI": "West Texas Intermediate",
    "LPG": "Liquefied Petroleum Gas",
    "GTL": "Gas to Liquid",
    "MEOR": "Microbial Enhanced Oil Recovery",
    "PVT": "Pressure Volume and Temperature",
    # -----------------------------------------------------------------------
    # Formations and lithology
    # -----------------------------------------------------------------------
    # SS is intentionally absent from DRILLING_ACRONYMS because its meaning
    # ("Sandstone" vs "Semi-Submersible Rig" vs "Stainless Steel") must be
    # resolved via CONTEXT_SENSITIVE_ACRONYMS with context-aware defaults.
    "SH": "Shale",
    "LS": "Limestone",
    "DOLO": "Dolomite",
    "DOLIC": "Dolomitic",
    "ANHY": "Anhydrite",
    "COAL": "Coal",
    "GYP": "Gypsum",
    "CALC": "Calcareous",
    "CARB": "Carbonaceous",
    "CONGL": "Conglomerate",
    "FRAC": "Fractured",
    "POR": "Porous",
    "ARGIL": "Argillaceous",
    "MICAC": "Micaceous",
    "GRAN": "Granular",
    "FRI": "Friable",
    "CRS": "Coarse",
    "CTGS": "Cuttings",
    "CVGS": "Cavings",
    "SWC": "Sidewall Core",
    "FORAM": "Foraminifera",
    "OOL": "Oolitic",
    "SRTD": "Sorted",
    "CONSOL": "Consolidated",
    "LAM": "Laminated",
    "VFG": "Very Fine Grain",
    "XBD": "Crossbedded",
    "TR": "Trace",
    "BAR": "Barite",
    "LITH": "Lithology",
    "CRE": "Calcarenite",
    "MTX": "Matrix",
    "FLH": "Shale",
    "MICXLN": "Microcrystalline",
    "EOC": "Eocene",
    "FM": "Formation",
    # -----------------------------------------------------------------------
    # Service companies and tools
    # -----------------------------------------------------------------------
    "HAL": "Halliburton",
    "SLB": "Schlumberger",
    "BHI": "Baker Hughes",
    "WFT": "Weatherford",
    "NOV": "National Oilwell Varco",
    "ANP": "National Petroleum Agency Brazil",
    "WITS": "Wellsite Information Transfer Specification",
    "SCADA": "Supervisory Control and Data Acquisition",
    # -----------------------------------------------------------------------
    # Wellbore geometry and pressures
    # -----------------------------------------------------------------------
    "OH": "Open Hole",
    "MASP": "Maximum Anticipated Surface Pressure",
    "PSD": "Production Shutdown",
    "ESCP": "Well Control System Equipment",
    "WELLCAP": "Well Control Accreditation Program",
    "HSE": "Health Safety and Environment",
    "QHSE": "Quality Health Safety and Environment",
    "JSA": "Job Safety Analysis",
    "SJA": "Safe Job Analysis",
    "HAZID": "Hazard Identification",
    "HAZOP": "Hazard and Operability Study",
    # -----------------------------------------------------------------------
    # Rig / vessel types
    # -----------------------------------------------------------------------
    "FPSO": "Floating Production Storage and Offloading",
    "TLP": "Tension Leg Platform",
    "TLWP": "Tension Leg Wellhead Platform",
    "FPS": "Floating Production System",
    "FPU": "Floating Production Unit",
    "SS": "Semi-Submersible Rig",          # overridden in CONTEXT_SENSITIVE_ACRONYMS
    "AHTS": "Anchor Handling Towing and Supply",
    "AUV": "Autonomous Underwater Vehicle",
    "ROV": "Remotely Operated Vehicle",
    "DSV": "Diving Support Vessel",
    "PSV": "Platform Supply Vessel",
    "MSV": "Multi Service Vessel",
    "NS": "Drillship",
    # -----------------------------------------------------------------------
    # Subsea / completion equipment
    # -----------------------------------------------------------------------
    "ANM": "Wet Christmas Tree",
    "ANMH": "Horizontal Wet Christmas Tree",
    "XT": "Christmas Tree",
    "HXT": "Horizontal Christmas Tree",
    "HWCT": "Horizontal Wet Christmas Tree",
    "TH": "Tubing Hanger",
    "TBG HGR": "Tubing Hanger",
    "THRT": "Tubing Hanger Running Tool",
    "PKR": "Packer",
    "TCP": "Tubing Conveyed Perforation",
    "STV": "Standing Valve",
    "TKV": "Tubing Kill Valve",
    "TP": "Tubing Pressure",
    "TPSI": "Tubing Pressure Shut-In",
    "SCSSV": "Surface-Controlled Subsurface Safety Valve",
    "SSCSV": "Subsurface Controlled Safety Valve",
    "SSSV": "Subsurface Safety Valve",
    "DHSV": "Downhole Safety Valve",
    "ASSV": "Annulus Subsurface Safety Valve",
    "USV": "Underwater Safety Valve",
    "SDV": "Shutdown Valve",
    "FSV": "Flow Safety Valve",
    "PSV": "Pressure Safety Valve",
    "BPV": "Back-Pressure Valve",
    "AWV": "Annulus Wing Valve",
    "ASV": "Annulus Swab Valve",
    "PLEM": "Pipeline End Manifold",
    "PLET": "Pipeline End Termination",
    "SCR": "Steel Catenary Riser",
    "SLWR": "Steel Lazy Wave Riser",
    "LMRP": "Lower Marine Riser Package",
    "LRP": "Lower Riser Package",
    "LWRP": "Lower Workover Riser Package",
    # -----------------------------------------------------------------------
    # Units (abbreviated where commonly used in reports)
    # -----------------------------------------------------------------------
    "PPG": "Pounds per Gallon",
    "PSI": "Pounds per Square Inch",
    "BBL": "Barrel",
    "SCF": "Standard Cubic Foot",
    "MCF": "Thousand Cubic Feet",
    "MMCF": "Million Cubic Feet",
    "BCF": "Billion Cubic Feet",
    "MMBBL": "Million Barrels",
    "BBBL": "Billion Barrels",
    "TCF": "Trillion Cubic Feet",
    "HP": "Horsepower",
    "RHP": "Rotary Horsepower",
    "OD": "Outer Diameter",
    "ID": "Inside Diameter",
    "PPM": "Parts per Million",
    "DWT": "Dead Weight Tonnage",
    # -----------------------------------------------------------------------
    # Well states and classification
    # -----------------------------------------------------------------------
    "P&A": "Plugged and Abandoned",
    "D&A": "Dry and Abandoned",
    "TA": "Temporarily Abandoned",
    "CW": "Commercial Well",
    "SI": "Shut-In",
    "ERW": "Extended Reach Well",
    "KO": "Kicked Off",
    "MSL": "Mean Sea Level",
    "OWPB": "Old Well Plugged Back",
    # -----------------------------------------------------------------------
    # Geophysics
    # -----------------------------------------------------------------------
    "AVO": "Amplitude Variation with Offset",
    "AVA": "Amplitude Variation with Angle of Incidence",
    "VSP": "Vertical Seismic Profiling",
    "PSV": "Vertical Seismic Profile",
    "CDP": "Common Depth Point",
    "CMP": "Common Mid Point",
    "CRP": "Common Reflection Point",
    "OBC": "Ocean Bottom Cable",
    "OBN": "Ocean Bottom Node",
    "GPR": "Ground Penetrating Radar",
    "BS": "Bright Spot",
}


# ---------------------------------------------------------------------------
# Context-sensitive (polysemic) acronyms
# ---------------------------------------------------------------------------

CONTEXT_SENSITIVE_ACRONYMS: dict[str, dict[str, str]] = {
    "WOC": {
        "drilling_context": "Waiting on Cement",
        "production_context": "Water-Oil Contact",
        "default": "Waiting on Cement",
    },
    "ST": {
        "drilling_context": "Sidetrack",
        "test_context": "Stem Test",
        "default": "Sidetrack",
    },
    "SS": {
        # In daily drilling reports "SS" almost always denotes the lithology
        # (sandstone). The rig type (semi-submersible) is written as "semi-sub"
        # or qualified as "SS rig" in context.
        "lithology_context": "Sandstone",
        "rig_context": "Semi-Submersible Rig",
        "general_context": "Stainless Steel",
        "default": "Sandstone",
    },
    "SP": {
        "drilling_context": "Stuck Pipe",
        "log_context": "Spontaneous Potential",
        "seismic_context": "Shot Point",
        "default": "Spontaneous Potential",
    },
    "RT": {
        "drilling_context": "Rotary Table",
        "log_context": "Resistivity",
        "default": "Rotary Table",
    },
    "DC": {
        "drilling_context": "Drill Collar",
        "regulatory_context": "Commerciality Declaration",
        "default": "Drill Collar",
    },
    "WC": {
        "production_context": "Water Cut",
        "fluid_context": "Water Cushion",
        "well_context": "Wildcat",
        "default": "Water Cut",
    },
    "SC": {
        "drilling_context": "Stuck Condition",
        "equipment_context": "Conventional Rig",
        "default": "Stuck Condition",
    },
    "LC": {
        "drilling_context": "Lost Circulation",
        "default": "Lost Circulation",
    },
    "HC": {
        "fluid_context": "Hydrocarbon",
        "default": "Hydrocarbon",
    },
    "PV": {
        "drilling_context": "Plastic Viscosity",
        "measurement_context": "True Vertical Depth",
        "default": "Plastic Viscosity",
    },
    "IP": {
        "production_context": "Productivity Index",
        "geophysics_context": "Induced Polarization",
        "default": "Productivity Index",
    },
    "MBT": {
        "drilling_context": "Methylene Blue Test",
        "general_context": "Bathythermograph",
        "default": "Methylene Blue Test",
    },
    "TOC": {
        "cement_context": "Top of Cement",
        "geochemistry_context": "Total Organic Carbon",
        "default": "Top of Cement",
    },
    "GI": {
        "production_context": "Gas Injection",
        "fluid_context": "Initial Gel Strength",
        "default": "Gas Injection",
    },
    "SG": {
        "fluid_context": "Specific Gravity",
        "show_context": "Show of Gas",
        "default": "Specific Gravity",
    },
    "FR": {
        "measurement_context": "Flow Rate",
        "geophysics_context": "Froude Number",
        "default": "Flow Rate",
    },
    "DIP": {
        "survey_context": "Dip Angle",
        "drilling_context": "Drilling Instrumentation Package",
        "default": "Dip Angle",
    },
    "NS": {
        "vessel_context": "Drillship",
        "general_context": "No Show",
        "default": "No Show",
    },
    "PSV": {
        "vessel_context": "Platform Supply Vessel",
        "equipment_context": "Pressure Safety Valve",
        "seismic_context": "Vertical Seismic Profile",
        "default": "Platform Supply Vessel",
    },
    "BT": {
        "general_context": "Bathythermograph",
        "reservoir_context": "Total Formation Volume Factor",
        "default": "Total Formation Volume Factor",
    },
    "FL": {
        "measurement_context": "Flow Line",
        "fluid_context": "Fluid Level",
        "default": "Flow Line",
    },
    "CBL": {
        "log_context": "Cement Bond Log",
        "lithology_context": "Core Barrel",
        "default": "Cement Bond Log",
    },
    "FLH": {
        "lithology_context": "Shale",
        "equipment_context": "Flowline Hub",
        "default": "Shale",
    },
}


# ---------------------------------------------------------------------------
# Unit normalization map used by preprocess_report_chunk
# ---------------------------------------------------------------------------

_UNIT_NORMALIZATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bppg\b", re.IGNORECASE), "pounds per gallon"),
    (re.compile(r"\bpsi\b", re.IGNORECASE), "pounds per square inch"),
    (re.compile(r"\bbbl\b", re.IGNORECASE), "barrels"),
    (re.compile(r"\bbbls\b", re.IGNORECASE), "barrels"),
    (re.compile(r"\bm/hr\b", re.IGNORECASE), "meters per hour"),
    (re.compile(r"\bm/h\b", re.IGNORECASE), "meters per hour"),
    (re.compile(r"\bklbs\b", re.IGNORECASE), "kilopounds"),
    (re.compile(r"\bklb\b", re.IGNORECASE), "kilopounds"),
    (re.compile(r"\brpm\b", re.IGNORECASE), "revolutions per minute"),
    (re.compile(r"\bgpm\b", re.IGNORECASE), "gallons per minute"),
    (re.compile(r"\bhp\b", re.IGNORECASE), "horsepower"),
    (re.compile(r"\bft\b", re.IGNORECASE), "feet"),
    (re.compile(r"\bft/hr\b", re.IGNORECASE), "feet per hour"),
    (re.compile(r"\bpcf\b", re.IGNORECASE), "pounds per cubic foot"),
    (re.compile(r"\bscf\b", re.IGNORECASE), "standard cubic feet"),
    (re.compile(r"\bmcf\b", re.IGNORECASE), "thousand cubic feet"),
    (re.compile(r"\bmmcf\b", re.IGNORECASE), "million cubic feet"),
    (re.compile(r"\bstb\b", re.IGNORECASE), "stock tank barrel"),
    (re.compile(r"\bdeg\b", re.IGNORECASE), "degrees"),
    (re.compile(r"\bdeg\.?\s*f\b", re.IGNORECASE), "degrees Fahrenheit"),
    (re.compile(r"\bdeg\.?\s*c\b", re.IGNORECASE), "degrees Celsius"),
]

# WITSML artifact patterns to strip or normalize
_WITSML_ARTIFACTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"<[^>]+>"), " "),               # XML/HTML tags
    (re.compile(r"&amp;"), "&"),
    (re.compile(r"&lt;"), "<"),
    (re.compile(r"&gt;"), ">"),
    (re.compile(r"&nbsp;"), " "),
    (re.compile(r"\s{2,}"), " "),                # collapse whitespace
]

# Critical acronyms to always expand for embedding (subset of full dict)
_EMBEDDING_CRITICAL: set[str] = {
    "RIH", "POOH", "TIH", "TOH", "WOW", "WOC", "POB", "DRLG", "DA",
    "ROP", "WOB", "RPM", "ECD", "EMW", "MW", "BHA", "PDC", "MWD", "LWD",
    "RSS", "PDM", "HWDP", "DC", "MD", "TVD", "INC", "AZM", "GR", "NPHI",
    "RHOB", "NPT", "ST", "SC", "LC", "DST", "LOT", "FIT", "RFT", "XLOT",
    "OBM", "WBM", "SBM", "PV", "YP", "MBT", "HTHP", "CSG", "LNG", "TOC",
    "GOR", "WHP", "THP", "BHP", "FTP", "SS", "SH", "LS", "DOLO", "ANHY",
    "BOP", "SPP", "TQ", "WOB", "GPM", "DLS", "KOP", "KT", "SICP",
    "SIDPP", "GOR", "WCT", "WHT", "FTP", "BOPD", "BWPD",
}

# Pre-compiled word-boundary pattern cache
_pattern_cache: dict[str, re.Pattern[str]] = {}


def _word_boundary_pattern(acronym: str) -> re.Pattern[str]:
    """Return (cached) regex that matches acronym as a whole word.

    The lookarounds treat ``/`` as a valid token separator so that compound
    expressions such as ``MWD/LWD`` expand both sides correctly.  Letters and
    digits remain excluded so that e.g. ``ROP`` is not matched inside
    ``EUROPE``.
    """
    if acronym not in _pattern_cache:
        escaped = re.escape(acronym)
        _pattern_cache[acronym] = re.compile(
            rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
        )
    return _pattern_cache[acronym]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def expand_acronyms(text: str, context: str = "drilling") -> str:
    """Expand acronyms in *text*, adding the expansion inline in parentheses.

    Parameters
    ----------
    text:
        Input text, e.g. a daily drilling report excerpt.
    context:
        Disambiguation context for polysemic acronyms.  Accepted values map to
        the ``*_context`` keys in ``CONTEXT_SENSITIVE_ACRONYMS`` plus the
        special value ``"drilling"`` (used as the default fallback).

    Returns
    -------
    str
        Text with expansions inserted: ``"ROP (Rate of Penetration)"``.
        The original casing of the acronym is preserved.

    Notes
    -----
    * Matching uses word boundaries so ``"ROP"`` is not replaced inside
      ``"EUROPE"`` or ``"GROPING"``.
    * Each acronym is expanded only once per call (first occurrence).
    """
    if not text:
        return text

    result = text
    already_expanded: set[str] = set()

    def _replacement(acr: str, expansion: str, src: str) -> str:
        """Return ``acr (expansion)`` if *acr* not yet expanded in *src*."""
        pattern = _word_boundary_pattern(acr)
        expanded = False

        def _replace_once(m: re.Match[str]) -> str:
            nonlocal expanded
            if expanded:
                return m.group(0)
            expanded = True
            return f"{m.group(0)} ({expansion})"

        return pattern.sub(_replace_once, src)

    # Resolve context-sensitive acronyms first (they have priority)
    for acr, mappings in CONTEXT_SENSITIVE_ACRONYMS.items():
        if acr in already_expanded:
            continue
        context_key = f"{context}_context"
        expansion = mappings.get(context_key) or mappings.get("default", "")
        if not expansion:
            continue
        new_result = _replacement(acr, expansion, result)
        if new_result != result:
            already_expanded.add(acr)
            result = new_result

    # Then handle all remaining acronyms from the main dictionary
    for acr, expansion in DRILLING_ACRONYMS.items():
        if acr in already_expanded:
            continue
        # Skip short generic tokens that could cause false positives
        if len(acr) < 2:
            continue
        new_result = _replacement(acr, expansion, result)
        if new_result != result:
            already_expanded.add(acr)
            result = new_result

    return result


def expand_for_embedding(text: str) -> str:
    """Aggressively expand all known acronyms to maximise embedding recall.

    Unlike ``expand_acronyms``, this version:
    * Expands *every* occurrence of each acronym (not just the first).
    * Uses the default context for all polysemic terms.
    * Is designed to feed text into a vector embedding pipeline, not for
      human readability.

    Returns
    -------
    str
        Text with acronym expansions appended after each match.
    """
    if not text:
        return text

    result = text

    # Build a merged dictionary: context-sensitive defaults override the base
    # dict so we do one unified pass.
    merged: dict[str, str] = dict(DRILLING_ACRONYMS)
    for acr, mappings in CONTEXT_SENSITIVE_ACRONYMS.items():
        merged[acr] = mappings.get("default", DRILLING_ACRONYMS.get(acr, ""))

    # Longest-first to avoid partial overlaps (e.g., POOH before POH)
    for acr in sorted(merged, key=len, reverse=True):
        expansion = merged[acr]
        if not expansion or len(acr) < 2:
            continue
        pattern = _word_boundary_pattern(acr)
        result = pattern.sub(lambda m: f"{m.group(0)} ({expansion})", result)

    return result


def detect_acronyms(text: str) -> list[dict]:
    """Detect acronyms in *text* and return metadata for each match.

    Parameters
    ----------
    text:
        Input text to scan.

    Returns
    -------
    list[dict]
        Each element has the keys:
        * ``acronym`` (str): matched token.
        * ``expansion`` (str): resolved expansion, or empty string if unknown.
        * ``position`` (int): character offset of the match start.
        * ``confidence`` (float): 1.0 if in the dictionary, 0.7 if it
          looks like an acronym (2-6 uppercase letters) but is unknown.
    """
    if not text:
        return []

    # Build a union of known acronyms
    known: set[str] = set(DRILLING_ACRONYMS.keys()) | set(
        CONTEXT_SENSITIVE_ACRONYMS.keys()
    )

    results: list[dict] = []
    # Scan every word-boundary delimited token of 2-6 uppercase chars
    for m in re.finditer(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9&/]{1,5})(?![A-Za-z0-9])", text):
        token = m.group(1)
        if token in known:
            expansion = CONTEXT_SENSITIVE_ACRONYMS.get(token, {}).get(
                "default", DRILLING_ACRONYMS.get(token, "")
            )
            confidence = 1.0
        else:
            expansion = ""
            confidence = 0.7

        results.append(
            {
                "acronym": token,
                "expansion": expansion,
                "position": m.start(1),
                "confidence": confidence,
            }
        )

    return results


def preprocess_report_chunk(text: str) -> str:
    """Full pre-processing pipeline for a daily drilling report chunk.

    Steps:
    1. Remove WITSML XML artifacts.
    2. Expand critical drilling acronyms (not all — avoids over-expansion).
    3. Normalise common unit abbreviations.
    4. Collapse excess whitespace.

    Designed to prepare text for vector embedding (e.g., OpenAI
    ``text-embedding-3-small``).

    Parameters
    ----------
    text:
        Raw text from ``DailyReport.summary_24hr`` or similar field.

    Returns
    -------
    str
        Cleaned, acronym-expanded text ready for embedding.
    """
    if not text:
        return text

    result = text

    # 1. Strip WITSML/XML artifacts
    for pattern, replacement in _WITSML_ARTIFACTS:
        result = pattern.sub(replacement, result)

    # 2. Expand critical acronyms only
    already_expanded: set[str] = set()

    def _expand_critical(acr: str, expansion: str, src: str) -> str:
        pattern = _word_boundary_pattern(acr)
        expanded = False

        def _replace_once(m: re.Match[str]) -> str:
            nonlocal expanded
            if expanded:
                return m.group(0)
            expanded = True
            return f"{m.group(0)} ({expansion})"

        return pattern.sub(_replace_once, src)

    # Context-sensitive first with drilling as default
    for acr, mappings in CONTEXT_SENSITIVE_ACRONYMS.items():
        if acr not in _EMBEDDING_CRITICAL or acr in already_expanded:
            continue
        expansion = mappings.get("drilling_context") or mappings.get("default", "")
        if not expansion:
            continue
        new_result = _expand_critical(acr, expansion, result)
        if new_result != result:
            already_expanded.add(acr)
            result = new_result

    # Main dictionary — critical subset
    for acr in _EMBEDDING_CRITICAL:
        if acr in already_expanded:
            continue
        expansion = DRILLING_ACRONYMS.get(acr, "")
        if not expansion:
            continue
        new_result = _expand_critical(acr, expansion, result)
        if new_result != result:
            already_expanded.add(acr)
            result = new_result

    # 3. Normalise units
    for pattern, replacement in _UNIT_NORMALIZATIONS:
        result = pattern.sub(replacement, result)

    # 4. Final whitespace cleanup
    result = re.sub(r" {2,}", " ", result).strip()

    return result


def enrich_daily_reports(driver) -> dict:
    """Apply ``preprocess_report_chunk`` to every ``DailyReport`` node.

    Reads ``summary_24hr`` from each node, expands acronyms, and writes the
    result to a new property ``summary_24hr_expanded``.

    Parameters
    ----------
    driver:
        An active ``neo4j.Driver`` instance.

    Returns
    -------
    dict
        Summary statistics:
        ``{"processed": int, "skipped": int, "errors": int}``.
    """
    stats: dict[str, int] = {"processed": 0, "skipped": 0, "errors": 0}

    query_read = (
        "MATCH (d:DailyReport) "
        "WHERE d.summary_24hr IS NOT NULL "
        "RETURN id(d) AS node_id, d.summary_24hr AS text"
    )
    query_write = (
        "MATCH (d:DailyReport) WHERE id(d) = $node_id "
        "SET d.summary_24hr_expanded = $expanded"
    )

    with driver.session() as session:
        records = session.run(query_read).data()

    for record in records:
        node_id = record["node_id"]
        raw_text = record.get("text")
        if not raw_text or not raw_text.strip():
            stats["skipped"] += 1
            continue
        try:
            expanded = preprocess_report_chunk(raw_text)
            with driver.session() as session:
                session.run(query_write, node_id=node_id, expanded=expanded)
            stats["processed"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            # Surface the error without crashing the whole batch
            import traceback
            traceback.print_exc()

    return stats


# ---------------------------------------------------------------------------
# Embedded tests — 20 real-language daily drilling report sentences
# ---------------------------------------------------------------------------

def _run_tests() -> None:
    """Run embedded regression tests against real drilling report language."""

    test_cases: list[tuple[str, list[str]]] = [
        # (input_text, list_of_expected_substrings_in_output)
        (
            "RIH to 4200m MD with new BHA, ROP averaging 35 m/hr.",
            ["Running In Hole", "Measured Depth", "Bottom-Hole Assembly", "Rate of Penetration"],
        ),
        (
            "POOH to surface for bit change, NPT 3.5 hrs due to stuck pipe (SP).",
            ["Pulling Out of Hole", "Non-Productive Time", "Stuck Pipe"],
        ),
        (
            "WOB maintained at 15 klbs, RPM 120, TQ 18 kNm, SPP 3200 psi.",
            ["Weight on Bit", "Revolutions per Minute", "Torque", "Standpipe Pressure"],
        ),
        (
            "ECD reached 14.2 ppg EMW — approaching formation fracture gradient.",
            ["Equivalent Circulating Density", "Equivalent Mud Weight"],
        ),
        (
            "LWD data shows NPHI 0.22 and RHOB 2.45 g/cc across the reservoir SS.",
            ["Logging While Drilling", "Neutron Porosity", "Bulk Density", "Sandstone"],
        ),
        (
            "GR log indicates transition from SH to SS at 3980m TVD.",
            ["Gamma Ray", "Shale", "Sandstone", "True Vertical Depth"],
        ),
        (
            "LOT conducted at 2850m MD, EMW 13.8 ppg. FIT passed.",
            ["Leak Off Test", "Equivalent Mud Weight", "Formation Integrity Test"],
        ),
        (
            "DST on zone A: BHP 5200 psi, GOR 850 scf/bbl, WCT 12%.",
            ["Drill Stem Test", "Bottom-Hole Pressure", "Gas-Oil Ratio", "Wet Christmas Tree"],
        ),
        (
            "WOC period of 8 hrs before resuming drilling operations.",
            ["Waiting on Cement"],
        ),
        (
            "OBM properties: MW 11.4 ppg, PV 28 cP, YP 18 lbf/100sqft, MBT 12.",
            ["Oil Base Mud", "Plastic Viscosity", "Yield Point", "Methylene Blue Test"],
        ),
        (
            "DLS at 3° /30m, INC 62°, AZM 215° — on plan trajectory.",
            ["Dog Leg Severity", "Inclination", "Azimuth"],
        ),
        (
            "CSG 9-5/8\" set at 2780m MD, TOC at 1950m, WOC 12 hrs.",
            ["Casing", "Top of Cement", "Waiting on Cement"],
        ),
        (
            "RFT pressure at 3210m TVD: BHP 4850 psi, reservoir pressure confirmed.",
            ["Repeat Formation Test", "Bottom-Hole Pressure", "True Vertical Depth"],
        ),
        (
            "BHA: PDC bit 8.5\", RSS, MWD/LWD, PDM, HWDP x8, DC x12.",
            [
                "Bottom-Hole Assembly",
                "Polycrystalline Diamond Compact",
                "Rotary Steerable System",
                "Measure While Drilling",
                "Logging While Drilling",
                "Positive Displacement Motor",
                "Heavy Weight Drillpipe",
                "Drill Collar",
            ],
        ),
        (
            "HTHP filtrate test: filtrate 3.2 ml at 300°F, 500 psi.",
            ["High Temperature High Pressure"],
        ),
        (
            "Formation evaluation: DOLO 15m, LS 8m, SS 42m (net pay), ANHY 3m.",
            ["Dolomite", "Limestone", "Sandstone", "Anhydrite"],
        ),
        (
            "POB 128 persons on board. WOW since 06:00 due to 25kt winds.",
            ["Personnel on Board", "Waiting on Weather"],
        ),
        (
            "Production test: THP 1850 psi, WHT 65°C, BOPD 4200, GOR 620 scf/bbl.",
            ["Tubing Head Pressure", "Wellhead Temperature", "Barrels of Oil per Day", "Gas-Oil Ratio"],
        ),
        (
            "DWOP identified LC risk at 3400m — LCM pills prepared.",
            ["Drilling Well on Paper", "Lost Circulation", "Lost Circulation Material"],
        ),
        (
            "Trip completed TIH — new BHA: PDC 8.5\", with SLB MWD tool. RIH to KOP at 1200m MD.",
            [
                "Trip in Hole",
                "Bottom-Hole Assembly",
                "Polycrystalline Diamond Compact",
                "Schlumberger",
                "Measure While Drilling",
                "Running In Hole",
                "Kick-Off Point",
                "Measured Depth",
            ],
        ),
    ]

    passed = 0
    failed = 0

    for i, (input_text, expected_substrings) in enumerate(test_cases, 1):
        output = expand_acronyms(input_text)
        missing = [s for s in expected_substrings if s not in output]
        if missing:
            print(f"  FAIL test {i:02d}: missing expansions {missing}")
            print(f"    input:  {input_text}")
            print(f"    output: {output}")
            failed += 1
        else:
            print(f"  PASS test {i:02d}: {input_text[:60]}...")
            passed += 1

    print(f"\n{'='*60}")
    print(f"Tests: {passed} passed, {failed} failed out of {len(test_cases)} total")
    if failed:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: read text from stdin and write expanded text to stdout.

    Usage::

        echo "RIH to 4200m MD with BHA" | python acronym_expander.py
        echo "RIH with BHA" | python acronym_expander.py --mode embedding
        python acronym_expander.py --test
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Expand drilling acronyms in text (reads from stdin by default).",
    )
    parser.add_argument(
        "--mode",
        choices=["expand", "embedding", "detect"],
        default="expand",
        help=(
            "expand: inline expansion for each acronym (default); "
            "embedding: aggressive expansion for vector search; "
            "detect: print detected acronyms as JSON."
        ),
    )
    parser.add_argument(
        "--context",
        default="drilling",
        help="Disambiguation context for polysemic acronyms (default: drilling).",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run embedded regression tests and exit.",
    )
    args = parser.parse_args()

    if args.test:
        print("Running embedded tests...\n")
        _run_tests()
        return

    raw = sys.stdin.read()

    if args.mode == "expand":
        print(expand_acronyms(raw, context=args.context))
    elif args.mode == "embedding":
        print(expand_for_embedding(raw))
    elif args.mode == "detect":
        import json
        detections = detect_acronyms(raw)
        print(json.dumps(detections, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
