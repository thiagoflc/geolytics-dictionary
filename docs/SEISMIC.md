# Seismic Module — P2.8

GeoBrain P2.8 adds formal coverage of the seismic geophysics lifecycle across three sub-domains: **Acquisition**, **Processing** and **Inversion / Attributes**. The module is structured as three JSON data files that are merged into `data/full.json` and served individually as `api/v1/seismic.json`.

---

## 1. Sub-domain Overview

### 1.1 Acquisition (`data/seismic-acquisition.json`)

Covers the controlled experiment of injecting seismic energy and recording the returning wavefield.

- **Survey types**: SeismicSurvey (abstract), LandSurvey, MarineSurvey, OBNSurvey (Ocean-Bottom Node), OBSSurvey
- **Sources**: Source (abstract), Airgun, Vibroseis, Dynamite, SparkerArray
- **Receivers**: Receiver (abstract), Hydrophone, Geophone, AccelerometerMEMS, OBC
- **Geometry**: AcquisitionGeometry (abstract), StreamerLayout, NodalLayout
- **Sampling**: SamplingParameters, Aliasing
- **Key constraint**: samplingInterval_ms <= 500 / signalBandwidthMax_Hz (Nyquist theorem). Validated by `geo:SamplingIntervalShape` SHACL constraint.

References: Yilmaz (2001) ch. 1-3; Sheriff & Geldart (1995).

### 1.2 Processing (`data/seismic-processing.json`)

Ordered sequence of transforms from raw shot gathers to migrated seismic image.

- **Flow**: ProcessingFlow (ordered list of steps)
- **Noise suppression**: NoiseSuppressionFilter (abstract), DATVF, FXEdit, DenoiseFK
- **Deconvolution**: Deconvolution (abstract), PredictiveDeconvolution, SpikingDeconvolution
- **Kinematics**: NMO, DMO, StaticCorrection
- **Summation**: Stacking
- **Amplitude**: AmplitudeCompensation (abstract), SphericalDivergenceCorrection, QCompensation
- **Imaging**: Migration (abstract), KirchhoffMigration, RTM

Canonical 15-step processing sequence is defined in `data/taxonomies.json` under `seismic_processing_steps_canonical`.

References: Yilmaz (2001) ch. 2-7.

### 1.3 Inversion and Attributes (`data/seismic-inversion-attributes.json`)

Quantitative interpretation and characterisation of the imaged seismic volume.

- **Inversion**: SeismicInversion (abstract), PostStackInversion, PreStackInversion, AVOInversion, ElasticImpedanceInversion (Connolly 1999), FullWaveformInversion
- **Rock properties**: AcousticImpedance, ElasticImpedance, VpVsRatio, LambdaRho (Russell 1988), MuRho
- **Attributes**: SeismicAttribute (abstract), Coherence, Curvature, RMS, SpectralDecomposition, InstantaneousPhase, Dip, Azimuth
- **DHI**: DHI (Direct Hydrocarbon Indicator), AVOAnomaly (Classes I, II, IIp, III, IV)
- **ML**: SOM (Coleou et al. 2003), PCA, FaciesClassification, SweetSpot

AVO class constraint validated by `geo:AVOClassShape` SHACL shape.

References: Russell (1988); Connolly (1999); Chopra & Marfurt (2007); Coleou et al. (2003).

---

## 2. Lifecycle Sequence Diagram

```mermaid
sequenceDiagram
    participant ACQ as Acquisition
    participant PRO as Processing
    participant INV as Inversion
    participant ATR as Attributes
    participant INT as Interpretation

    ACQ->>PRO: Raw shot gathers (field SEGY)
    Note over ACQ: Sources, Receivers, Geometry, SamplingParameters
    PRO->>PRO: Noise suppression, Deconvolution
    PRO->>PRO: NMO + DMO + Stacking
    PRO->>PRO: Migration (Kirchhoff or RTM)
    PRO->>INV: Migrated / stacked seismic volume
    Note over PRO: ProcessingFlow, AmplitudeCompensation
    INV->>INV: Wavelet extraction + low-frequency model from wells
    INV->>INV: PostStackInversion -> AcousticImpedance
    INV->>INV: PreStackInversion -> Ip, Is, rho -> VpVsRatio, LambdaRho, MuRho
    INV->>ATR: Rock property volumes
    Note over INV: ElasticImpedance (Connolly 1999), FWI
    ATR->>ATR: Coherence, Curvature, RMS
    ATR->>ATR: SpectralDecomposition, Dip, Azimuth
    ATR->>ATR: AVOAnomaly (Class I-IV)
    ATR->>INT: DHI, SweetSpot, FaciesClassification (SOM/PCA)
    Note over ATR: Chopra & Marfurt 2007; Coleou et al. 2003
    INT->>INT: Well-to-seismic calibration + prospect delineation
```

---

## 3. OSDU Mapping

| Geolytics Class | OSDU Kind | OSDU Schema Notes |
|---|---|---|
| `SeismicSurvey` (all subtypes) | `opendes:osdu:work-product-component--SeismicAcquisitionSurvey:1.0.0` | Survey geometry, sampling parameters, source/receiver metadata |
| `LandSurvey` | `opendes:osdu:work-product-component--SeismicAcquisitionSurvey:1.0.0` | See `AcquisitionSurvey.SurveyType = LAND` |
| `MarineSurvey` | `opendes:osdu:work-product-component--SeismicAcquisitionSurvey:1.0.0` | See `AcquisitionSurvey.SurveyType = MARINE` |
| `OBNSurvey` / `OBSSurvey` | `opendes:osdu:work-product-component--SeismicAcquisitionSurvey:1.0.0` | 4C node / OBC variant |
| `ProcessingFlow` | `opendes:osdu:work-product-component--SeismicProcessingProject:1.0.0` | Ordered step list; `ProcessingProjectName`, `Vintage` |
| `RTM` / `KirchhoffMigration` | `opendes:osdu:work-product-component--SeismicProcessingProject:1.0.0` | `MigrationMethod` field |
| `FullWaveformInversion` | `opendes:osdu:work-product-component--SeismicProcessingProject:1.0.0` | FWI iteration as processing project |
| `PostStackInversion` | `opendes:osdu:work-product-component--SeismicTraceData:1.0.0` | Acoustic impedance volume as trace data |
| `PreStackInversion` | `opendes:osdu:work-product-component--SeismicTraceData:1.0.0` | Partial-angle stacks and simultaneous inversion output |
| `AVOInversion` | `opendes:osdu:work-product-component--SeismicTraceData:1.0.0` | Intercept/gradient volumes |
| `SeismicAttribute` (all subtypes) | `opendes:osdu:work-product-component--SeismicTraceData:1.0.0` | Coherence, curvature, RMS, spectral decomp volumes |
| `AcousticImpedance` | `opendes:osdu:work-product-component--SeismicTraceData:1.0.0` | `TraceDataType = ACOUSTIC_IMPEDANCE` |

---

## 4. SHACL Constraints Added (P2.8)

| Shape | Target | Rule |
|---|---|---|
| `geo:SamplingIntervalShape` | `geo:SamplingParameters` | `samplingInterval_ms <= 500 / signalBandwidthMax_Hz` (Nyquist); SPARQL constraint |
| `geo:OffsetShape` | subjects of `geo:offset` | `offset >= 0` (non-negative) |
| `geo:AVOClassShape` | subjects of `geo:avoClass` | `sh:in ( "I" "II" "IIp" "III" "IV" )` (Rutherford-Williams) |

---

## 5. Taxonomies Added (P2.8)

All in `data/taxonomies.json`:

| Key | Values | Notes |
|---|---|---|
| `seismic_source_types` | airgun, vibroseis, dynamite, weight_drop, sparker | Canonical seismic source enum |
| `seismic_receiver_types` | hydrophone, geophone_3c, geophone_1c, obn, obc, mems | Canonical receiver enum |
| `seismic_processing_steps_canonical` | 15 ordered steps | Ordered canonical processing flow |
| `avo_classes` | I, II, IIp, III, IV | Rutherford-Williams AVO classification |

---

## 6. Key References

- Yilmaz, O. (2001). *Seismic Data Analysis*. SEG Investigations in Geophysics No. 10. ISBN 1-56080-094-1.
- Sheriff, R.E. & Geldart, L.P. (1995). *Exploration Seismology* (2nd ed.). Cambridge University Press.
- Russell, B.H. (1988). *Introduction to Seismic Inversion Methods*. SEG Course Notes Series Vol. 2.
- Connolly, P. (1999). Elastic Impedance. *The Leading Edge*, 18(4), 438-452. DOI 10.1190/1.1438307.
- Chopra, S. & Marfurt, K.J. (2007). *Seismic Attributes for Stratigraphic and Structural Interpretation*. SEG Distinguished Instructor Short Course Vol. 11.
- Coleou, T., Poupon, M. & Azbel, K. (2003). Unsupervised seismic facies classification: A review and comparison of techniques and implementation. *The Leading Edge*, 22(10), 942-953.
