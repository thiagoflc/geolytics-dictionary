# Geomechanics / MEM — P2.7 Module Documentation

## Overview

The Mechanical Earth Model (MEM) is the core deliverable of petroleum geomechanics. It is a quantitative description of the mechanical state of a formation — the subsurface geometry, pore fluid pressure, in situ stresses, and elastic and strength properties of the rock. The MEM is the starting point for every geomechanical application: wellbore stability analysis, sand production prediction, hydraulic fracture design, reservoir compaction modelling, and fault reactivation risk.

This module covers `data/geomechanics.json` (26 classes, 22 properties, 12 relations, 6 instances) and `data/geomechanics-fractures.json` (17 fracture classes, 7 properties, 8 GSO crosswalk mappings).

---

## The Four Pillars of the MEM

A valid 1D or 3D MEM must integrate all four pillars. Missing one pillar makes the model incomplete and the downstream predictions unreliable.

```mermaid
flowchart TD
    P1["Pillar 1\nIn Situ Stress\n(Sv, SHmax, Shmin)\nAnderson Regime"]
    P2["Pillar 2\nPore Pressure (Pp)\nEaton / Bowers / MDT-RFT"]
    P3["Pillar 3\nElastic Moduli\n(E, nu, K, G, Biot)"]
    P4["Pillar 4\nContainment Geometry\nStructure + Stratigraphy"]

    MEM["Mechanical Earth Model\n(1D or 3D)"]

    P1 --> MEM
    P2 --> MEM
    P3 --> MEM
    P4 --> MEM

    MEM --> WS["Wellbore Stability\nMud Window Design"]
    MEM --> SP["Sand Production\nCritical Drawdown"]
    MEM --> HF["Hydraulic Fracture\nHeight / Azimuth"]
    MEM --> RC["Reservoir Compaction\nSubsidence"]
    MEM --> FR["Fault Reactivation\nSeal Integrity (SGR)"]
```

### Pillar 1 — In Situ Stress

Three principal stresses act at every point in the subsurface:

| Symbol | Name | Measurement Method |
|---|---|---|
| Sv | Vertical (overburden) stress | Density log integration |
| SHmax | Maximum horizontal stress | Breakout azimuth, DITF, offset wellbore analysis |
| Shmin | Minimum horizontal stress | LOT / XLOT / mini-frac closure pressure |

Anderson (1951) defined three stress regimes based on which principal stress is largest:

- **Normal faulting** (NF): Sv > SHmax > Shmin — passive margins, rift basins
- **Strike-slip** (SS): SHmax > Sv > Shmin — transform boundaries
- **Reverse faulting** (RF): SHmax > Shmin > Sv — fold-thrust belts

The Santos Basin (Buzios/pre-salt) is predominantly a normal-faulting regime.

### Pillar 2 — Pore Pressure

Pore pressure (Pp) controls effective stress via the Biot-Terzaghi principle:

```
sigma_effective = sigma_total - alpha * Pp
```

where alpha is the Biot coefficient (0 to 1). Normal pore pressure gradient is 0.433-0.465 psi/ft. Overpressure (> 0.6 psi/ft) requires elevated mud weight and narrows the drilling window.

Calibration sources: RFT/MDT direct measurements, formation pressures from DST, drilling events (kicks, mud weight changes), seismic velocity inversion (Eaton method).

### Pillar 3 — Elastic and Strength Properties

Key rock mechanical properties and their units:

| Property | Symbol | Unit | Typical Range |
|---|---|---|---|
| Uniaxial Compressive Strength | UCS | MPa | 5 - 600 |
| Young's Modulus | E | GPa | 1 - 100 |
| Poisson's Ratio | nu | dimensionless | 0.0 - 0.5 |
| Bulk Modulus | K | GPa | 2 - 80 |
| Shear Modulus | G | GPa | 1 - 40 |
| Biot Coefficient | alpha | dimensionless | 0.5 - 1.0 |

**Critical distinction**: Static properties (from laboratory triaxial tests) and dynamic properties (derived from sonic velocities Vp/Vs) differ by 20-40% for UCS and 10-30% for Young's modulus. Dynamic values must not be used for engineering design without a static-dynamic calibration.

### Pillar 4 — Containment Geometry

Structural and stratigraphic geometry defines the 3D boundaries within which the MEM is built: fault locations, formation tops, layer geometries, dipping horizons. This pillar is the link to the seismic interpretation and geological model.

---

## JSON Structure Mapping to MEM Pillars

The JSON files map to the MEM pillars as follows:

```
data/geomechanics.json
  classes
    GM001  StressTensor             -> Pillar 1
    GM002  PrincipalStress          -> Pillar 1
    GM003  ShearStress              -> Pillar 1
    GM004  PorePressure             -> Pillar 2
    GM005  MudWindow                -> downstream application (Wellbore Stability)
    GM007-009  FailureCriterion     -> Pillar 3 (strength)
    GM010-012  MechanicalEarthModel -> integration of all 4 pillars
    GM013-019  RockMechProperty     -> Pillar 3 (elastic moduli)
    GM020-022  RockMassRating/GSI/RQD -> Pillar 3 (rock mass quality)
    GM023  Anisotropy               -> Pillar 3 (directional dependence)
    GM024  Brittleness              -> Pillar 3 (failure style)
    GM025  AndersonStressRegime     -> Pillar 1 (regime classification)
    GM026  Wellbore                 -> observation point for calibration

  properties
    GP001-010  elastic moduli + principal stresses  -> Pillar 1 + 3
    GP004      porePressureGradient                 -> Pillar 2
    GP020-021  mudWeightLower/Upper                 -> downstream: Mud Window
    GP022      stressRegime                         -> Pillar 1

  relations
    GR002, GR007  controls_mud_window / bounds_drilling_window  -> Pillar 2 -> Mud Window
    GR008  calibrated_by                            -> Pillar 1/2/3 calibration

  instances
    mem-buzios-1d           -> full 1D MEM example (Santos Basin pre-salt)
    failure-mohr-coulomb    -> Pillar 3 strength example
    hoek-brown-carbonate    -> Pillar 3 rock mass example
    normal-faulting-regime  -> Pillar 1 stress regime
    mud-window-depleted     -> downstream: depleted reservoir mud window

data/geomechanics-fractures.json
    fracture classes        -> Pillar 4 (structural/containment geometry)
    anderson regimes        -> Pillar 1
    fracture_to_gso.json    -> alignment to GSO Layer 7
```

---

## Downstream Applications

### Mud Weight Prediction (Wellbore Stability)

The mud weight window is bounded by:
- **Lower bound**: pore pressure gradient (prevent kick/influx)
- **Upper bound**: fracture gradient (prevent lost circulation)

Collapse pressure may be higher than pore pressure in weak or highly stressed formations, further narrowing the window.

### Sand Production Prediction

Sand production risk is evaluated by comparing the near-wellbore stress concentration against rock strength (UCS). The critical drawdown pressure below which sand is mobilized is computed from the MEM using Mohr-Coulomb or similar criteria.

### Fault Reactivation / Seal Integrity

The Shale Gouge Ratio (SGR) is computed along fault surfaces using the stress state and lithological column. SGR > 18-20% indicates potentially sealing; below that, the fault may be conductive to flow. Computed in TrapTester (Badley Geoscience) at Petrobras.

### Reservoir Compaction and Surface Subsidence

Depletion of reservoir pressure (Pp decrease) causes the effective stress to increase, leading to compaction (reduction of porosity and permeability) and potentially surface subsidence. Governed by Young's modulus and Biot coefficient from Pillar 3.

---

## Key Disambiguation Notes

| Term | Module | Definition |
|---|---|---|
| Janela de Lama | M9 Geomechanics | Safe mud weight range between collapse and fracture pressure. Unit: ppg or g/cm3. |
| Janela de Geracao | M7 Geochemistry | Kerogen maturation window based on vitrinite reflectance Ro%. Completely different concept. |
| UCS estatico | M9 | UCS from laboratory triaxial test — the authoritative value for engineering design. |
| UCS dinamico | M9 | UCS estimated from sonic DTC/DTS logs via empirical correlation. Differs 20-40% from static; requires calibration before use. |
| SGR (Shale Gouge Ratio) | M9 | Fault sealing proxy (%). Not to be confused with SAR (geochemistry) or SGR (gas). |

---

## Sources

- Fjaer E., Holt R.M., Horsrud P., Raaen A.M., Risnes R. — *Petroleum Related Rock Mechanics*, 2nd ed. Elsevier 2008 (ISBN 978-0-444-50260-5)
- Zoback M.D. — *Reservoir Geomechanics*, Cambridge University Press 2010 (ISBN 978-0-521-14619-7)
- Hoek E., Brown E.T. — The Hoek-Brown Failure Criterion and GSI: 2018 Edition. *Journal of Rock Mechanics and Geotechnical Engineering* 11(3):445-463, 2019
- Anderson E.M. — *The Dynamics of Faulting*, Oliver & Boyd 1951
- Bieniawski Z.T. — *Engineering Rock Mass Classifications*, Wiley 1989
- ISRM — *The Complete ISRM Suggested Methods for Rock Characterization, Testing and Monitoring 1974-2006*
- Plumb R. et al. — The Mechanical Earth Model Concept and its Application to High-Risk Well Construction Projects. SPE/IADC 65118, 2000
- Caine J.S., Evans J.P., Forster C.B. — Fault zone architecture and permeability structure. *Geology* 24(11):1025-1028, 1996
- Brodaric B., Richard S. — Geoscience Ontology (GSO) v1.0.2. GSC Open File 8796, DOI 10.4095/328296, 2021
