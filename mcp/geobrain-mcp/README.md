# geobrain-mcp

MCP server exposing the Geolytics O&G semantic dictionary as AI tools.

Runs fully offline using the bundled JSON data. No API keys, no embedding provider.
Designed for local use with Claude Desktop, Claude Code, Cursor, and LangGraph agents.

---

## Installation

```bash
cd mcp/geobrain-mcp
npm install
npm run build
```

The compiled entry point is `dist/index.js`. The binary can be run directly:

```bash
node dist/index.js
```

---

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/absolute/path/to/geobrain/mcp/geobrain-mcp/dist/index.js"]
    }
  }
}
```

### Claude Code (CLI)

Add to your project's `.claude/settings.json`:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/absolute/path/to/geobrain/mcp/geobrain-mcp/dist/index.js"]
    }
  }
}
```

Or add globally in `~/.claude/settings.json` to use across all projects.

### Cursor

In `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/absolute/path/to/geobrain/mcp/geobrain-mcp/dist/index.js"]
    }
  }
}
```

---

## Neo4j (optional)

`cypher_query` is disabled by default. To enable it:

```bash
# Start Neo4j and load data
docker compose up -d
docker compose run --rm loader

# Export environment variables before starting the MCP server
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=geolytics123
```

Or pass them in the MCP config:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/path/to/dist/index.js"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "geolytics123"
      }
    }
  }
}
```

If `cypher_query` is called without Neo4j configured, it returns a helpful error with setup instructions rather than crashing.

---

## Tools

### 1. `lookup_term`

Search glossary, extended-terms and ontopetro classes by name (PT or EN).

**Input:**

```json
{ "term": "bacia", "fuzzy": false }
```

**Response shape:**

```json
{
  "found": true,
  "query": "bacia",
  "fuzzy": false,
  "glossary": [
    {
      "source": "glossary",
      "id": "bacia-sedimentar",
      "termo": "Bacia Sedimentar",
      "termo_en": "Sedimentary Basin",
      "categoria": "geologia",
      "definicao": "Depressão da crosta terrestre onde se acumulam rochas sedimentares...",
      "legal_source": "Lei nº 9478, de 06/08/1997",
      "petrokgraph_uri": "https://...#SedimentaryBasin",
      "osdu_kind": "opendes:osdu:master-data--Basin:1.0.0",
      "geocoverage": ["layer1", "layer2", "layer3", "layer4", "layer5"],
      "synonyms_pt": ["bacia", "bacia sedimentar"],
      "synonyms_en": ["basin", "sedimentary basin"],
      "examples": ["Bacia de Campos", "Bacia de Santos"]
    }
  ],
  "extended": [],
  "ontopetro": []
}
```

---

### 2. `expand_acronym`

Expand an O&G sigla. Excludes `it_generic` entries by default.

**Input:**

```json
{ "sigla": "ANP" }
```

**Response shape:**

```json
{
  "found": true,
  "sigla": "ANP",
  "senses_count": 1,
  "disambiguation_needed": false,
  "disambiguation_hint": null,
  "senses": [
    {
      "id": "anp",
      "sigla": "ANP",
      "expansion_pt": "Agência Nacional do Petróleo, Gás Natural e Biocombustíveis, Brasil",
      "expansion_en": "National Petroleum, Natural Gas and Biofuels Agency, Brazil",
      "category": "regulator",
      "it_generic": false
    }
  ]
}
```

**Disambiguation example** — `BOP` has multiple senses:

```json
{ "sigla": "BOP" }
// -> disambiguation_needed: true, hint lists categories, all senses returned
```

---

### 3. `get_entity`

Fetch a single entity node with all outgoing and incoming relations resolved.

**Input:**

```json
{ "id": "poco" }
```

**Response shape:**

```json
{
  "found": true,
  "entity": {
    "id": "poco",
    "label": "Poço",
    "label_en": "Well",
    "type": "operational",
    "definition": "...",
    "petrokgraph_uri": "https://...#Well",
    "osdu_kind": "opendes:osdu:master-data--Well:1.0.0",
    "geosciml_uri": "http://geosciml.org/def/gsmlbh#Borehole"
  },
  "outgoing": [
    {
      "relation": "drilled_in",
      "relation_label_pt": "perfurado em",
      "relation_label_en": "drilled in",
      "target": { "id": "bloco", "label": "Bloco", ... }
    }
  ],
  "incoming": []
}
```

---

### 4. `get_entity_neighbors`

Multi-hop BFS traversal of the entity graph.

**Input:**

```json
{ "id": "poco", "hops": 2, "edge_types": ["drilled_in", "classified_by"] }
```

**Response shape:**

```json
{
  "found": true,
  "origin": { "id": "poco", "label": "Poço", "label_en": "Well" },
  "hops": 2,
  "edge_types": ["drilled_in", "classified_by"],
  "neighbors_count": 4,
  "neighbors": [
    {
      "id": "bloco",
      "label": "Bloco",
      "via_relation": "drilled_in",
      "direction": "outgoing",
      "hop": 1,
      "petrokgraph_uri": "https://...#ExplorationBlock",
      "osdu_kind": "opendes:osdu:master-data--AcquisitionSurvey:1.0.0"
    }
  ]
}
```

---

### 5. `validate_claim`

Validate a natural-language claim against the ontology (requires P1.4 `scripts/semantic-validator.js`).

**Input:**

```json
{ "text": "O poco perfurado na bacia sedimentar produziu oleo" }
```

**Response shape (validator present):**

```json
{
  "valid": true,
  "violations": [],
  "warnings": []
}
```

**Response shape (validator absent):**

```json
{
  "valid": null,
  "error": "validator unavailable",
  "detail": "scripts/semantic-validator.js not found. This tool requires P1.4 to be implemented."
}
```

---

### 6. `cypher_query`

Execute a Cypher query. Only active when `NEO4J_URI` is set.

**Input:**

```json
{ "query": "MATCH (p:Entity {id:'poco'})-[r]->(b:Entity) RETURN p.label, type(r), b.label LIMIT 5" }
```

**Response shape (Neo4j available):**

```json
{
  "ok": true,
  "records_count": 5,
  "records": [{ "p.label": "Poço", "type(r)": "DRILLED_IN", "b.label": "Bloco" }]
}
```

**Response shape (Neo4j not configured):**

```json
{
  "error": "Neo4j not configured",
  "detail": "To enable cypher_query, start Neo4j and set NEO4J_URI=bolt://localhost:7687 ..."
}
```

---

### 7. `search_rag`

BM25 full-text search over `ai/rag-corpus.jsonl`. No external dependencies.

**Input:**

```json
{ "query": "reservatorio poroso permeavel hidrocarbonetos", "k": 3 }
```

**Response shape:**

```json
{
  "query": "reservatorio poroso permeavel hidrocarbonetos",
  "k": 3,
  "total_corpus": 1245,
  "results_count": 3,
  "results": [
    {
      "score": 15.502,
      "id": "ontopetro_class_C003",
      "type": "ontopetro_class",
      "text": "Reservatório (Reservoir): ...",
      "metadata": { "id": "reservatorio", "category": "geologia" }
    }
  ]
}
```

---

### 8. `list_layers`

List all semantic layers. No input parameters required.

**Input:**

```json
{}
```

**Response shape:**

```json
{
  "count": 7,
  "layers": [
    {
      "id": "layer1",
      "name": "BFO + GeoCore",
      "maintainer": "UFRGS/BDI + Geosiris (França)",
      "type": "formal_ontology",
      "description": "Ontologia formal de geologia com 11 classes baseadas em BFO...",
      "concepts_count": 11,
      "language": "OWL/RDF",
      "geolytics_coverage": ["bacia-sedimentar", "presal", ...]
    }
  ]
}
```

---

### 9. `crosswalk_lookup`

Find equivalent terms across ontology layers.

**Input:**

```json
{ "uri": "bacia-sedimentar", "target_layer": "osdu" }
```

**Response shape:**

```json
{
  "found": true,
  "uri": "bacia-sedimentar",
  "target_layer": "osdu",
  "matches_count": 1,
  "matches": [
    {
      "id": "bacia-sedimentar",
      "label": "Bacia Sedimentar",
      "label_en": "Sedimentary Basin",
      "type": "geological",
      "geocoverage": ["layer1", "layer2", "layer3", "layer4", "layer5"],
      "uris": {
        "petrokgraph": "https://...#SedimentaryBasin",
        "osdu": "opendes:osdu:master-data--Basin:1.0.0",
        "geosciml": "http://geosciml.org/def/gsmlb#GeologicUnit",
        "gso": null,
        "owl": "https://w3id.org/osdu#Basin"
      }
    }
  ]
}
```

Also accepts OSDU kinds as input:

```json
{ "uri": "opendes:osdu:master-data--Well:1.0.0" }
// finds the entity that has this osdu_kind and returns all its cross-layer URIs
```

### 10. `lookup_lithology`

Search the 437-concept CGI Simple Lithology vocabulary (Layer 1b — GeoSciML/IUGS).

**Input:**

```json
{ "query": "sandstone", "lang": "en", "parent": "clastic_sedimentary_rock", "max_results": 5 }
```

- `query` — search term (matches `label_en`, `label_pt`, or concept `id`)
- `lang` — `"en"` (default) or `"pt"`
- `parent` — optional CGI parent ID to restrict search within a subtree
- `max_results` — defaults to 10

**Response shape:**

```json
{
  "query": "sandstone",
  "count": 2,
  "results": [
    {
      "id": "sandstone",
      "label_en": "sandstone",
      "label_pt": "arenito",
      "definition": "Clastic sedimentary rock...",
      "parents": ["clastic_sedimentary_rock"],
      "uri": "http://resource.geosciml.org/classifier/cgi/lithology/sandstone"
    }
  ]
}
```

---

### 11. `lookup_geologic_time`

Search the 52-unit ICS 2023 geologic time scale (Layer 1b — CGI/GeoSciML).

**Input:**

```json
{ "query": "Cretaceous", "rank": "Period" }
```

- `query` — search term (matches unit name or abbreviation)
- `rank` — optional filter: `"Eon"`, `"Era"`, `"Period"`, `"Epoch"`, `"Age"`

**Response shape:**

```json
{
  "query": "Cretaceous",
  "count": 1,
  "results": [
    {
      "id": "Cretaceous",
      "label": "Cretaceous",
      "rank": "Period",
      "start_ma": 145.0,
      "end_ma": 66.0,
      "duration_ma": 79.0,
      "uri": "http://resource.geosciml.org/classifier/ics/ischart/Cretaceous",
      "brazil_notes": "Período com maior geração de HC no pré-sal (Aptiano-Albiano)"
    }
  ]
}
```

---

## Development

```bash
npm run dev      # tsc --watch, recompiles on change
npm run build    # production build to dist/
```

The server reads data files from the repository root at runtime.
All 7 data sources are loaded once at startup and kept in memory:
`data/glossary.json`, `data/extended-terms.json`, `data/acronyms.json`,
`data/entity-graph.json`, `data/ontopetro.json`,
`ai/ontology-map.json`, `ai/rag-corpus.jsonl`.
