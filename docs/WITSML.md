# WITSML to RDF — Concept, Crosswalk, and Conversion

## Why WITSML to RDF matters: from linear schemas to 3D graphs

WITSML (Well Information Transfer Standard Markup Language) is the Energistics XML schema for real-time drilling and well data. It is excellent for data exchange — but its structure is hierarchical and flat: a `Trajectory` has `trajectoryStation` children, a `Well` has `Wellbore` children, and everything terminates in a text node or a typed scalar.

A hierarchical tree answers questions like "give me all stations for wellbore X" but struggles with:

- "Which wells intersect the Barra Velha Formation between 5000 m and 5500 m TVD?"
- "For all wells with incl > 30 degrees in the Santos Basin, show me the correlation between DLS and formation type at the kick-off point."
- "Find all WellboreMarkers with dipAngle > 15 degrees that are within 200 m TVD of the salt base in any well."

These are graph traversal questions. A SPARQL query over an RDF triple store — or a Cypher query over a Neo4j graph — answers them in a single statement. The transformation from WITSML XML to RDF triples is the bridge that enables this.

### The linear-to-graph argument

In WITSML XML, data is nested: a `Well` contains `Wellbore`s which contain `Trajectory`s which contain `TrajectoryStation`s. Queries must navigate this tree from the root.

In RDF, every entity becomes a named node and every relationship becomes a typed arc. The graph is 3D in the sense that you can traverse it from any starting point and in any direction:

```
geo:WellboreMarker mrkr-top-salt
    geo:md "1850.0"^^xsd:decimal
    geo:tvd "1847.2"^^xsd:decimal
    geo:dipAngle "2.1"^^xsd:decimal
    geo:partOfWellbore wb-buz-1-rjs-main
                |
                v
    geo:partOfWell well-buz-1-rjs
                |
                v
    geo:hasTrajectory traj-buz-1-rjs-final
                |
                v
    geo:TrajectoryStation stn-003
        geo:md "3000.0"^^xsd:decimal
        geo:incl "18.7"^^xsd:decimal
```

A single SPARQL `SELECT` can traverse this graph in any direction. The same data structure also feeds Cypher in Neo4j, where graph algorithms (shortest path, community detection) apply directly.

## Crosswalk schema

Both `data/witsml-rdf-crosswalk.json` and `data/prodml-rdf-crosswalk.json` follow this schema per class entry:

```json
{
  "witsml_class": "WellboreMarker",
  "witsml_uri": "http://www.energistics.org/energyml/data/witsmlv2/2.0#WellboreMarker",
  "rdf_class": "geo:WellboreMarker",
  "rdf_uri": "https://geolytics.petrobras.com.br/dict/WellboreMarker",
  "geocore_alignment": "...",
  "osdu_kind": "opendes:osdu:master-data--WellboreMarker:1.0.0",
  "layer": "layer4",
  "description_pt": "...",
  "description_en": "...",
  "primitive_properties": [
    {
      "name": "md",
      "type": "xsd:decimal",
      "unit": "m",
      "description_pt": "Profundidade Medida do topo"
    }
  ],
  "object_properties": [
    {
      "name": "inWellbore",
      "range": "geo:Wellbore",
      "description_pt": "Marcador pertence a um wellbore"
    }
  ],
  "shacl_shape": "geo:WellboreMarkerShape",
  "sparql_path": "geo:WellboreMarker",
  "cypher_label": "WellboreMarker"
}
```

### Field definitions

| Field | Type | Description |
|---|---|---|
| `witsml_class` | string | Class name in the WITSML 2.0 XSD schema |
| `witsml_uri` | URI | Energistics namespace URI for this class |
| `rdf_class` | CURIE | `geo:` prefixed class in the Geolytics vocabulary |
| `rdf_uri` | URI | Full URI of the geo: class |
| `geocore_alignment` | string | Closest GeoCore / OGC / W3C class alignment with note |
| `osdu_kind` | string | OSDU kind in `opendes:osdu:master-data--Type:major.minor.patch` format |
| `layer` | string | Geolytics layer identifier (always `layer4` for WITSML/PRODML/OSDU) |
| `primitive_properties` | array | Scalar properties with XSD type, unit, and PT description |
| `object_properties` | array | Relationships to other classes with range and description |
| `shacl_shape` | URI (optional) | SHACL shape in `data/geolytics-shapes.ttl` that validates instances |
| `sparql_path` | CURIE | Class reference for SPARQL queries |
| `cypher_label` | string | Neo4j label for Cypher queries |

## Conversion pattern — worked example

Given this WITSML XML fragment:

```xml
<WellboreMarker uid="mrkr-top-bv">
  <name>Topo da Formacao Barra Velha</name>
  <uidWell>well-buz-1-rjs</uidWell>
  <uidWellbore>wb-buz-1-rjs-main</uidWellbore>
  <md uom="m">5240.0</md>
  <tvd uom="m">4620.8</tvd>
  <tvdss uom="m">6720.8</tvdss>
  <dipAngle uom="deg">8.7</dipAngle>
  <dipDirection uom="deg">95.0</dipDirection>
  <chrono>Barremian</chrono>
  <litho>carbonate</litho>
  <showRating>good</showRating>
</WellboreMarker>
```

The converter (`scripts/witsml-to-rdf.js`) produces:

```turtle
@prefix geo:   <https://geolytics.petrobras.com.br/dict/> .
@prefix witsml: <http://www.energistics.org/energyml/data/witsmlv2/2.0#> .
@prefix inst:  <https://geolytics.petrobras.com.br/dict/instance/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .

inst:wellbore-marker-mrkr-top-bv
    a geo:WellboreMarker ;
    owl:sameAs witsml:WellboreMarker ;
    skos:prefLabel "Topo da Formacao Barra Velha"@en ;
    geo:partOfWell inst:well-well-buz-1-rjs ;
    geo:partOfWellbore inst:wellbore-wb-buz-1-rjs-main ;
    geo:md "5240.0"^^xsd:decimal ;
    geo:tvd "4620.8"^^xsd:decimal ;
    geo:tvdss "6720.8"^^xsd:decimal ;
    geo:dipAngle "8.7"^^xsd:decimal ;
    geo:dipDirection "95.0"^^xsd:decimal ;
    geo:chrono "Barremian"^^xsd:string ;
    geo:litho "carbonate"^^xsd:string ;
    geo:showRating "good"^^xsd:string .
```

### What the converter does

1. Parses the XML without external libraries — uses a lightweight regex extractor designed for WITSML's predictable element structure.
2. Looks up each top-level element tag in `data/witsml-rdf-crosswalk.json` to resolve the `geo:` class URI and the Energistics `witsml:` URI.
3. Extracts scalar children and maps them to `geo:property "value"^^xsd:type` triples, using the type hints in `XSD_TYPE_HINTS` and the crosswalk `primitive_properties` entries.
4. Resolves parent links (`uidWell`, `uidWellbore`) into `geo:partOfWell` and `geo:partOfWellbore` object property triples.
5. For `Trajectory` elements, iterates over nested `trajectoryStation` blocks and emits one `geo:TrajectoryStation` node per station linked via `geo:inTrajectory`.
6. Prefixes all instance URIs under `inst:` (configurable).

### SPARQL query example

After loading the turtle into a triplestore (e.g. Apache Jena Fuseki or GraphDB):

```sparql
PREFIX geo: <https://geolytics.petrobras.com.br/dict/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# All wellbore markers in the carbonate lithology with showRating = good
SELECT ?marker ?md ?tvd ?chrono
WHERE {
  ?marker a geo:WellboreMarker ;
          geo:litho "carbonate"^^xsd:string ;
          geo:showRating "good"^^xsd:string ;
          geo:md ?md ;
          geo:tvd ?tvd ;
          geo:chrono ?chrono .
}
ORDER BY DESC(?md)
```

### Cypher query example (Neo4j)

If loaded into Neo4j via the `build/neo4j/` pipeline:

```cypher
// Trajectory stations with inclination > 30 degrees linked to their well
MATCH (stn:TrajectoryStation)-[:inTrajectory]->(traj:Trajectory)
MATCH (traj)-[:partOfWellbore]->(wb:Wellbore)-[:partOfWell]->(w:Well)
WHERE toFloat(stn.incl) > 30.0
RETURN w.name AS well, traj.name AS trajectory,
       stn.md AS md, stn.incl AS inclination, stn.azi AS azimuth
ORDER BY toFloat(stn.incl) DESC
LIMIT 20
```

## Running the converter

```bash
# Convert the bundled sample
node scripts/witsml-to-rdf.js

# Convert a custom WITSML XML file
node scripts/witsml-to-rdf.js path/to/your-well.xml

# Pipe into a file
node scripts/witsml-to-rdf.js data/witsml-sample.xml > output.ttl
```

The script exits with code 0 on success. Errors (file not found, malformed XML root) exit with code 1.

## SHACL validation

Two SHACL shapes in `data/geolytics-shapes.ttl` validate WITSML-derived instances:

### WellboreMarkerShape

Validates any `geo:WellboreMarker` instance:
- `geo:md` is mandatory (exactly one), `xsd:decimal`, value >= 0
- `geo:tvd` is optional; if present, must be <= `geo:md` (TVD is always at most MD)
- `geo:dipAngle` if present: decimal in [0..90] degrees
- `geo:dipDirection` if present: decimal in [0..360] degrees

The TVD <= MD constraint is enforced with a SPARQL-based SHACL rule that fires when `tvd > md`.

### TrajectoryStationShape

Validates any `geo:TrajectoryStation` instance:
- `geo:md` is mandatory, >= 0
- `geo:incl` is mandatory, in [0..180] degrees (0 = vertical, 90 = horizontal, 180 = inverted)
- `geo:azi` is mandatory, in [0..360] degrees
- `geo:tvd` optional, if present <= `geo:md`
- `geo:inTrajectory` links to exactly one `geo:Trajectory`

Run SHACL validation:

```bash
python scripts/validate-shacl.py
```

## WITSML vs. PRODML

| Dimension | WITSML 2.0 | PRODML 2.x |
|---|---|---|
| Focus | Drilling and well construction | Production monitoring and allocation |
| Key objects | Well, Wellbore, Trajectory, MudLog, BHA, Cement | ProductionWell, FlowMeasurement, DTS/DAS, ProductionVolume |
| Temporal scope | During drilling (real-time) | During production (surface + downhole) |
| Crosswalk file | `data/witsml-rdf-crosswalk.json` | `data/prodml-rdf-crosswalk.json` |
| Primary classes | 25 classes | 15 classes |
| Fiber optics | Not covered | DtsMeasurement, DasMeasurement, FiberOpticPath |
| OSDU alignment | Wellbore, Trajectory, Well | Well, WellLog (DTS), ProductionVolume |

Both crosswalks use the same schema and share the `geo:` namespace. PRODML DTS/DAS data models the fiber optic path, interrogator, and measurement separately — enabling SPARQL queries like "find all DTS anomalies above 80°C in wellbores with FiberOpticPath.installationMethod = control line."

## Coverage

| File | Classes | Properties per class (avg) |
|---|---|---|
| `data/witsml-rdf-crosswalk.json` | 25 | ~9 primitive + ~2 object |
| `data/prodml-rdf-crosswalk.json` | 15 | ~8 primitive + ~2 object |
| `data/geolytics-vocab.ttl` | 5 WITSML classes declared with `owl:sameAs` | Well, Wellbore, WellboreMarker, Trajectory, LogCurve |
| `data/geolytics-shapes.ttl` | 2 new SHACL shapes | WellboreMarkerShape, TrajectoryStationShape |
