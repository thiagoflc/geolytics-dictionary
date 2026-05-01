# SWEET Ontology Alignment

## What is SWEET

SWEET (Semantic Web for Earth and Environmental Terminology) is an upper-mid ontology maintained by the [ESIP Federation](https://www.esipfed.org/) under NASA/JPL original development. It is published as open Turtle files at https://github.com/ESIPFed/sweet under the Apache 2.0 license.

SWEET comprises approximately 6,000 concepts organized in roughly 200 modular Turtle files. Concepts are grouped into five broad namespaces:

| Namespace prefix | Domain |
|---|---|
| `matr*` | Materials — rocks, minerals, organics, fluids |
| `proc*` | Processes — geological, hydrological, atmospheric |
| `realm*` | Realms — physical domains of the Earth system |
| `prop*` | Properties — physical, chemical, geometric |
| `repr*` | Representations — units, time, geometry, science |

The canonical URI base is `http://sweetontology.net/`. A typical class looks like:

```
http://sweetontology.net/matrOrganics/Hydrocarbon
http://sweetontology.net/procGeo/Diagenesis
http://sweetontology.net/realmGeolTectonic/Fault
```

## How SWEET complements GeoCore

The Geolytics semantic stack uses two different upper-level frameworks that address different questions:

**GeoCore (UFRGS/Geosiris) — formal geology realism**

GeoCore follows a realist ontology tradition. Its classes represent the real-world entities as the geological community formally defines them: `GeologicalUnit`, `GeologicalBody`, `RockMaterial`. GeoCore is the right framework for saying "what kind of entity is a reservoir?" and for aligning with OSDU data schemas that inherit from similar traditions.

**SWEET — upper-mid environmental physics**

SWEET is not primarily a formal geology ontology; it is an environmental science ontology that happens to have excellent coverage of geological materials, processes, and realms. Its design is broader but shallower: it models the *physical universe* that geological science studies. This makes it the right framework for the complementary question "what physical concept does this term refer to?".

Concretely, consider `diagênese`:

- GeoCore defines it as a `GeologicalProcess` subtype with formal identity conditions.
- SWEET defines `procGeo:Diagenesis` as a `GeologicProcess` that modifies rock material.
- Neither is a substitute for the other. Together, they triangulate the concept from different angles, which is exactly what semantic query expansion requires.

The key use case is **synonym expansion**: when an agent searches for documents about "diagênese", SWEET alignment tells it that documents mentioning `GeologicProcess`, `Sedimentation`, or other sibling processes are also relevant candidate contexts — without any false equivalence claims.

## How alignments are curated

Each alignment record in `data/sweet-alignment.json` has the following fields:

```json
{
  "geolytics_id": "diagenese",
  "sweet_uris": [
    "http://sweetontology.net/procGeo/Diagenesis",
    "http://sweetontology.net/procGeo/GeologicProcess"
  ],
  "alignment_type": "skos:exactMatch",
  "sweet_module": "procGeo",
  "rationale_pt": "..."
}
```

### Alignment type guidelines

The alignment type follows the [SKOS mapping properties](https://www.w3.org/TR/skos-reference/#mapping):

| Type | When to use |
|---|---|
| `skos:exactMatch` | The concepts are equivalent: same definition, same scope. Use only when both labels and definitions correspond. |
| `skos:closeMatch` | Highly similar but not identical. Scope differences exist (e.g. one is broader in practice, or covers a slightly different range). |
| `skos:broadMatch` | The SWEET class is broader — the Geolytics term is a specialization of the SWEET concept. |
| `skos:narrowMatch` | The SWEET class is narrower — the Geolytics term covers more than one SWEET class. |
| `skos:relatedMatch` | Related but neither hierarchically similar nor equivalent. Use when the best available SWEET match is a sibling or associated concept rather than a direct match. |

**Conservative policy**: `skos:exactMatch` is only assigned when the concept scope is verified to be the same in both ontologies. When uncertain, use `skos:relatedMatch` or `skos:closeMatch`. Records marked with `"verification_note": "to-be-verified"` require human review against the live SWEET Turtle files.

### SWEET module assignments

Each alignment is tagged with its primary SWEET module (the Turtle file namespace, without `.ttl`). The module catalog is in `data/sweet-modules.json` and covers:

- `matrOrganics` — hydrocarbons, kerogen, oil, gas
- `matrRockSedimentary` / `matrRockIgneous` / `matrRockMetamorphic` — rock types
- `matrMineral` — minerals
- `matr` — base materials (water, brine)
- `procGeo` — geological processes
- `realmGeol` / `realmGeolTectonic` / `realmGeolBasin` / `realmHydro` — physical realms
- `propPressure` / `propTemperature` / `propMass` / `propFluidTransport` / `propSpaceMultidimensional` / `propSpaceDistance` — physical properties
- `reprSciUnits` — measurement units
- `reprTimeGeologic` — geologic time intervals

## How the TTL output uses alignments

When `scripts/generate.js` runs, it loads `data/sweet-alignment.json` and passes it to `buildTtl` (in `scripts/ttl-serializer.js`). The serializer adds SKOS mapping property triples directly to each class:

```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

geo:diagenese a owl:Class ;
    skos:prefLabel "Diagênese"@pt ;
    skos:exactMatch <http://sweetontology.net/procGeo/Diagenesis> ;
    skos:exactMatch <http://sweetontology.net/procGeo/GeologicProcess> .
```

To verify after regeneration:

```bash
node scripts/generate.js
grep -n "sweetontology\|exactMatch\|closeMatch" data/geolytics.ttl | head -20
```

## How agents use the alignments

### sweet-expand.js

The primary agent interface is `scripts/sweet-expand.js`:

```javascript
import { expand } from './scripts/sweet-expand.js';

const result = expand('hidrocarboneto', { includeHierarchy: true });
// result.sweetUris — all aligned SWEET URIs
// result.hierarchy — parent/child/sibling URIs from embedded SWEET hierarchy
// result.alignments — full alignment records with rationale
// result.modules — which SWEET modules are involved
```

The function embeds a curated SWEET hierarchy snippet so agents can walk up and down the class tree without network calls. For example, expanding `hidrocarboneto` gives access to:

- `matrOrganics/Hydrocarbon` (exactMatch)
- Parent: `matrOrganics/OrganicCompound`
- Children: `Oil`, `NaturalGas`, `Condensate`

This allows the agent to widen a search from "hidrocarboneto" to cover "óleo cru" and "gás natural" via genuine ontological subsumption rather than keyword guessing.

### CLI usage

```bash
node scripts/sweet-expand.js hidrocarboneto
node scripts/sweet-expand.js diagenese --json
node scripts/sweet-expand.js falha-cisalhante --include-siblings
```

### LangGraph decomposer integration

The LangGraph decomposer node (`examples/langgraph-agent/nodes/decomposer.py`) includes a `_expand_with_sweet` helper. When a query mentions a term that has a SWEET alignment with `skos:exactMatch` or `skos:closeMatch`, the helper appends sibling concept labels to the decomposed sub-queries, effectively broadening the semantic search without changing the query's main intent.

## Human review checklist

Alignments marked `"verification_note": "to-be-verified"` in `data/sweet-alignment.json` need to be checked against the canonical Turtle files. For each one:

1. Fetch the module file from `https://raw.githubusercontent.com/ESIPFed/sweet/master/src/<module>.ttl`
2. Confirm the class name exists in that file
3. Compare the `rdfs:comment` or `skos:definition` with the Geolytics term definition
4. Adjust the `alignment_type` if needed (downgrade from `exactMatch` to `closeMatch` if scopes differ)
5. Remove the `verification_note` field once verified

Terms currently requiring review:

- `unidade-darcy` — `reprSciUnits/Darcy` — confirm Darcy unit exists as a class (vs. as a data property)
- `magmatismo` — `procGeo/Magmatism` — confirm spelling (some versions use `Magmatism`, others `Magmatic`)
- `mecanismo-deformacao` — `procGeo/Deformation` — confirm scope matches deformation mechanisms rather than just deformation events
