# GWML2 — GroundWaterML2 WellConstruction (Layer 1b)

## Overview

GWML2 (GroundWaterML2) is an OGC standard (version 2.2) that models the physical construction components of boreholes and wells, covering casing strings, screens, sealing elements, filtration packs, and bore intervals. In O&G well modeling it provides a rigorous vocabulary for describing well integrity and completion architecture that complements the stratigraphic and structural concepts covered by GeoSciML. This project imports the GWML2 WellConstruction module as part of Layer 1b, alongside CGI vocabularies and GeoSciML Borehole (gsmlbh), to anchor `poco` nodes to internationally recognised URIs.

---

## WellConstruction classes

All 9 classes share namespace `http://www.opengis.net/gwml-well/2.2/` and map to the `poco` entity.

| Class | PT-BR | Description | Related gsmlbh |
|---|---|---|---|
| `WellConstruction` | Construcao de Poco | Abstract parent class for all well construction components; covers casing, sealing, screen, and filter. | `gsmlbh:Borehole` |
| `CasingComponent` | Componente de Revestimento | Individual element of a casing string; tubular segment installed to stabilise bore walls and isolate pressure zones. | `gsmlbh:Borehole` |
| `Screen` | Tela de Filtracao | Perforated interval or screen installed in the productive zone to allow fluid entry while excluding sediment. | `gsmlbh:Borehole` |
| `SealingComponent` | Componente de Vedacao | Cement or seal element placed between casing and borehole wall to isolate pressure zones and prevent fluid migration. | `gsmlbh:Borehole` |
| `FiltrationComponent` | Componente de Filtracao | Gravel pack or filter material installed around the screen to prevent fines migration and improve production efficiency. | `gsmlbh:Borehole` |
| `BoreCollar` | Cabeca do Poco | Structural element representing the top of the well; depth reference point and connection to surface infrastructure. | `gsmlbh:Borehole` |
| `BoreInterval` | Intervalo do Poco | Defined interval along the well with homogeneous construction or geological characteristics; used for zonation and log correlation. | `gsmlbh:Borehole` |
| `WellPump` | Bomba de Poco | Pumping equipment installed in the well to lift fluids from the formation to surface; includes submersible and rod pumps. | `gsmlbh:Borehole` |
| `CasingString` | Coluna de Revestimento | Complete string of connected casing tubes forming a continuous column; aggregation of CasingComponents (conductor, surface, intermediate, production). | `gsmlbh:Borehole` |

---

## gsmlbh properties

All 4 properties share namespace `http://geosciml.org/def/gsmlbh#`, apply to the `poco` entity, and are governed by `sh:PropertyShape` with `minCount: 0` and `maxCount: 1`.

| Property | XSD type | Description |
|---|---|---|
| `boreholeDiameter` | `xsd:decimal` | Borehole diameter at a given depth interval, expressed in millimetres (unit: `qudt:MilliMeter`). |
| `dateOfDrilling` | `xsd:date` | Date drilling commenced, expressed in ISO 8601 format (YYYY-MM-DD). |
| `drillingMethod` | `xsd:string` | Method used to drill the well (e.g. rotary, percussion, air rotary, cable tool). Linked to controlled vocabulary `gsmlbh:DrillingMethod`. |
| `inclinationType` | `xsd:string` | Well inclination type: `vertical` (< 5 deg), `deviated` (5–85 deg), or `horizontal` (> 85 deg). |

---

## Cross-links

`poco` nodes in the entity graph carry a `geosciml_uri` property whose value is `http://geosciml.org/def/gsmlbh#Borehole`. This URI is the join key that connects the internal `poco` entity to the external GeoSciML Borehole class:

```cypher
MATCH (p:Poco)
WHERE p.geosciml_uri IS NOT NULL
RETURN p.id, p.label, p.geosciml_uri
```

The formal `owl:equivalentClass` mapping between the internal `geocore#Borehole` (Layer 1) and `gsmlbh:Borehole` (Layer 1b) is recorded in `data/layer1-layer1b-equivalence.json`. That file holds 14 mappings covering classes such as `GeologicUnit`, `GeologicStructure`, `MappedFeature`, and `Borehole`, enabling SPARQL reasoning across namespaces without duplicating class definitions.

---

## SHACL shapes

The `data/geobrain.ttl` file declares a `geo:PocoShape` NodeShape that validates `poco` nodes. It uses `sh:property` to enforce the 4 gsmlbh properties listed above — each as an individual `sh:PropertyShape` with the constraints (`sh:datatype`, `sh:maxCount`) derived from `gsmlbh-properties.json`. Run validation with:

```bash
python scripts/validate-shacl.py
```

See [SHACL.md](SHACL.md) for the full list of 30 NodeShapes and instructions for adding new shapes.

---

## Usage examples

### API

```
GET /api/v1/gwml2.json
GET /api/v1/gsmlbh-properties.json
```

Both endpoints return the full JSON file. `gwml2.json` contains the 9 WellConstruction classes; `gsmlbh-properties.json` contains the 4 borehole properties with their SHACL constraints and unit annotations.

### Cypher

**Query 09** (`docs/queries/09-componentes-poco-gwml2.cypher`) retrieves well construction components linked to a `poco` node and returns their GWML2 URIs alongside construction type labels. Use this query to validate that all construction components in the graph are typed against the GWML2 WellConstruction hierarchy.

---

## Cross-references

- [CGI.md](CGI.md) — CGI vocabularies (Layer 1b): lithology, geologic time, fault type, deformation style, contact type, stratigraphic rank
- [EXTERNAL_STANDARDS.md](EXTERNAL_STANDARDS.md) — OGC, OSDU, PPDM, SPE-PRMS, Petro KGraph reference data
- [SHACL.md](SHACL.md) — Full SHACL shapes documentation: 30 NodeShapes, validation workflow, how to add new shapes
