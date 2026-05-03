# CGI Vocabularies (Layer 1b — GeoSciML)

## Overview

CGI (IUGS Commission for Geoscience Information) publishes open geoscience vocabularies under the GeoSciML standard, covering lithology, geologic time, structural geology, and stratigraphy. This project includes these vocabularies as Layer 1b of the semantic architecture, providing internationally recognised URIs that anchor entity-graph nodes to external standards. Layer 1b sits between Layer 1 (BFO+GeoCore ontology) and Layer 2 (OSDU data model), acting as the semantic bridge that enables cross-standard crosswalks.

---

## Vocabulary table

| File | Concepts | Description | OSDU mapping |
|---|---|---|---|
| `data/cgi-lithology.json` | 437 | CGI Simple Lithology — OWL ontology of rock types with multilingual labels and parent hierarchy | Yes — see `cgi-osdu-lithology-map.json` |
| `data/cgi-osdu-lithology-map.json` | 152 | Bilateral crosswalk CGI Simple Lithology ↔ OSDU LithologyType (exactMatch, closeMatch, broadMatch, narrowMatch) | N/A (is the mapping itself) |
| `data/cgi-geologic-time.json` | 52 | ICS 2023 geologic time scale: eons, eras, periods, epochs with start/end Ma and ICS colour codes | No |
| `data/cgi-fault-type.json` | 15 | CGI fault type concepts (e.g. normal fault, reverse fault, strike-slip fault) | No |
| `data/cgi-deformation-style.json` | 12 | CGI deformation style concepts (e.g. brittle, ductile, mixed) | No |
| `data/cgi-contact-type.json` | 12 | CGI contact type concepts (e.g. unconformity, intrusive contact, fault contact) | No |
| `data/cgi-stratigraphic-rank.json` | 28 | CGI stratigraphic rank concepts (e.g. group, formation, member, bed) | No |

---

## Structure

Each concept in `cgi-lithology.json` follows this schema (real example — `QAPF1`):

```json
{
  "id": "QAPF1",
  "label_en": "QAPF1",
  "label_pt": "campo QAPF 1 (Streckeisen)",
  "parents": [],
  "definition_en": null,
  "uri": "http://resource.geosciml.org/classifier/cgi/lithOntology/QAPF1"
}
```

Key fields:

| Field | Type | Description |
|---|---|---|
| `id` | string | Short identifier (CGI code or slug) |
| `label_en` | string | English preferred label |
| `label_pt` | string | Portuguese preferred label |
| `parents` | string[] | Parent concept IDs (OWL hierarchy) |
| `definition_en` | string \| null | Scope note in English |
| `uri` | string | Canonical CGI/GeoSciML URI |

Geologic time units (`cgi-geologic-time.json`) use a different schema with `rank`, `start_ma`, `end_ma`, `color`, `parent`, `children`, and `brazil_notes`.

---

## Cross-links

Entity-graph nodes that represent lithological or structural concepts carry a `geosciml_uri` property pointing to the canonical CGI/GeoSciML URI. This property is the join key for all CGI-based crosswalks:

```cypher
MATCH (n)
WHERE n.geosciml_uri IS NOT NULL
RETURN n.id, n.label, n.geosciml_uri
```

The file `data/layer1-layer1b-equivalence.json` contains 14 `owl:equivalentClass` / `skos:exactMatch` mappings between Layer 1 GeoCore classes (e.g. `geocore#GeologicUnit`) and GeoSciML classes (e.g. `gsmlb#GeologicUnit`). These mappings enable SPARQL reasoning across the two namespaces without duplicating class definitions.

---

## Usage examples

### Python

```python
from geolytics_dictionary import LithologyDictionary

d = LithologyDictionary()
d.lookup("arenito")
```

### API

```
GET /api/v1/cgi-lithology.json
GET /api/v1/cgi-geologic-time.json
```

Both endpoints return the full JSON file. Use query parameters (when supported by the serving layer) to filter by `label_pt`, `label_en`, or `rank`.

### MCP

```
lookup_lithology(query="sandstone")
lookup_geologic_time(query="Aptian")
```

---

## Cypher queries

Two reference queries in `docs/queries/` target Layer 1b data directly:

- **Query 07** (`07-litologia-cgi-osdu-crosswalk.cypher`): finds reservoirs whose lithology nodes carry a `geosciml_uri` and returns the CGI URI alongside the OSDU `osdu_kind` for crosswalk validation.
- **Query 08** (`08-escala-tempo-geologico-presal.cypher`): retrieves geologic formations in the pre-salt context (Aptian–Albian) and links them to ICS time units; includes a note on filtering `cgi-geologic-time.json` by `brazil_notes`.

---

## Cross-references

- [EXTERNAL_STANDARDS.md](EXTERNAL_STANDARDS.md) — OSDU LithologyType reference data, Petro KGraph, PPDM, SPE-PRMS
- [ARCHITECTURE.md](ARCHITECTURE.md) — 8-layer semantic architecture diagram showing where Layer 1b fits
- [ONTOLOGY.md](ONTOLOGY.md) — GeoCore class reference and Layer 1 ↔ Layer 1b equivalences
