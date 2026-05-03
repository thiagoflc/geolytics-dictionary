# Changelog

All notable changes to the GeoBrain knowledge graph are documented here.
Versioning follows [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.

---

## [1.1.0] — 2026-05-03

### Added — Petrobras 3W Dataset v2.0.0 integration (CC-BY 4.0)

Source: Vargas et al. (2019), DOI [10.1016/j.petrol.2019.106223](https://doi.org/10.1016/j.petrol.2019.106223).
License: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

**Entity graph (+51 nodes, ~165 new edges):**
- 27 sensor/instrument nodes (TW001–TW027): 27 canonical 3W sensor variables (P-PDG, T-PDG, P-TPT, T-TPT, ABER-CKGL, ABER-CKP, ESTADO-DHSV, ESTADO-M1, ESTADO-M2, ESTADO-PXO, ESTADO-SDV-GL, ESTADO-SDV-P, ESTADO-W1, ESTADO-W2, ESTADO-XO, P-ANULAR, P-JUS-BS, P-JUS-CKGL, P-JUS-CKP, P-MON-CKGL, P-MON-CKP, P-MON-SDV-P, P-PT-P, QBS, QGL, T-JUS-CKP, T-MON-CKP) with full WITSML/SWEET/OSDU crosswalk.
- 13 new Xmas-tree equipment nodes (TW028–TW040): PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK, TPT, SP, ANM.
- 1 ANM (Subsea Xmas-tree assembly) wrapper node (TW041).
- 10 operational event nodes (TW042–TW051): Normal, BSW Increase, Spurious DHSV Closure, Severe Slugging, Flow Instability, Rapid Production Loss, Quick PCK Restriction, PCK Scaling, Production Line Hydrate, Service Line Hydrate.
- Patch to existing `dhsv` node: added failure_modes, monitored_by, OSDU kind, 3W-specific fields.

**Taxonomies (+4 entries in `data/taxonomies.json`):**
- `operational_event_class_3w`: 10 event classes with transient flag, window/step parameters, signature tags.
- `instance_origin_3w`: WELL_ / SIMULATED_ / DRAWN_ instance prefixes.
- `event_phase_3w`: steady (offset 0) vs. transient (TRANSIENT_OFFSET=100).
- `valve_state_3w`: 0=closed, 0.5=partial, 1=open.

**Crosswalks:**
- WITSML 2.0: +5 entries (30 total).
- PRODML 2.x: +4 entries (19 total).
- SWEET alignment: +14 entries (83 total).

**Datasets:**
- `dataset-3w` registry entry added to `data/datasets.json` (9 total).

**Semantic validation (+3 rules, +6 tests):**
- `3W_INVALID_LABEL`: rejects any label outside 0–9, 101, 102, 105–109.
- `3W_TRANSIENT_FORBIDDEN_FOR_STEADY`: classes 3 and 4 have no transient variant.
- `3W_VALVE_STATE_DOMAIN`: ESTADO-* must be 0, 0.5 or 1.

**SHACL (+3 NodeShapes, 48 total):**
- `geo:OperationalEventShape`: validates `geo:threew_label` against canonical set.
- `geo:Sensor3WShape`: requires `geo:threew_unit` and `geo:threew_quantity_kind`.
- `geo:ValveStateShape`: validates `geo:value` ∈ {0, 0.5, 1}.

**RAG corpus (+59 chunks, 2212 total):**
- 10 `threew_event` chunks (one per event class, bilingual PT/EN).
- 49 WITSML/PRODML crosswalk chunks (up from 40).

**Few-shot examples:**
- Text2Cypher: +5 examples (50 total).
- Text2SPARQL: +3 examples (28 total).

**System prompts:**
- `ai/system-prompt-ptbr.md` and `ai/system-prompt-en.md`: added §8 (PT) / §"Petrobras 3W Dataset" (EN) section.

**Polysemy disambiguation (+3 cards):**
- PCK: Production Choke (3W/ANM) vs. Pilot-operated Check Valve.
- BSW: fluid property vs. `event_bsw_increase` (class 1 event).
- state: 3W sensor state vs. `well_state` ANP taxonomy.

**Provenance files (CC-BY 4.0 compliance):**
- `data/sources/threew/dataset.ini` — snapshot SHA-256: `c5ffad72bc1c46bccffa1e18412f2ddb87ca0e96eb7d2dfba92a4bc38a45bba2`
- `data/sources/threew/enums.py` — snapshot SHA-256: `fef829488c82f5c28b150d2bb9cf5c85fb06a7bcc2aa5316208aba758b2dccac`
- `data/sources/threew/PROVENANCE.md` — attribution record with DOI, authors, license.

### Changed

- `data/entity-graph.json`: 170 → 221 nodes, 259 → 370 edges, version bumped to 1.1.0.
- `data/full.json`: version bumped to 1.1.0; source list updated.
- `data/taxonomies.json`, `data/datasets.json`, `data/acronyms.json`: version 1.1.0.
- `data/witsml-rdf-crosswalk.json`: 25 → 30 classes, version 1.1.0.
- `data/prodml-rdf-crosswalk.json`: 15 → 19 classes, version 1.1.0.
- `data/sweet-alignment.json`: 66 → 83 alignments, version 1.1.0.
- `python/geobrain/_version.py`: 0.1.0 → 0.2.0.
- `docs/EXTERNAL_STANDARDS.md`: added Petrobras 3W v2.0.0 section.
- `README.md`: updated node/edge counts, RAG corpus size, SHACL count, crosswalk counts.

---

## [1.0.0] — 2025 (baseline)

Initial release: 170 entity nodes, 259 edges, 36 ANP glossary terms, 8 datasets (ANP/SEP SIGEP), OSDU integration, GeoSciML/CGI lithology, GSO/Loop3D (Layer 7), SWEET alignment (66 entries), geomechanics module (P2.7), seismic module (P2.8), geomechanics corporate entities (P2.10), WITSML/PRODML crosswalks (25+15 classes), 45 Text2Cypher + 25 Text2SPARQL few-shots, 1245 RAG chunks, SHACL 30 NodeShapes.
