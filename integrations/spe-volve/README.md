# SPE Volve — Geolytics Integration

This directory contains enrichment modules that bridge the
[SPE 2026 challenge](https://github.com/geolytics-energy/spe-2026-challenge)
drilling-agent project with the
[geolytics-dictionary](https://github.com/geolytics-energy/geolytics-dictionary)
semantic knowledge layer.

The SPE project ingests raw Volve daily drilling reports into Neo4j and builds
a conversational agent on top of them.  These modules add:

- **Richer entity extraction** — node types drawn from PetroGold NER and Volve
  domain knowledge rather than the minimal original schema.
- **Controlled vocabularies** — CGI Simple Lithology, IADC codes, PPFG
  classification, drilling-phase coding.
- **Semantic URI alignment** — WITSML 2.0 and OSDU URIs attached to every
  existing Neo4j node, enabling SPARQL federation and standards-compliant
  reporting.
- **RAG context injection** — geolytics-dictionary corpus injected into the
  agent's retrieval pipeline.
- **NLP utilities** — acronym expansion, formation classifier, pressure
  classifier.

---

## Directory layout

```
integrations/spe-volve/
├── agent/
│   └── tools/
│       └── domain_knowledge_enriched.py    # E1 — enriched agent tool layer
├── ingestion/
│   ├── entity_extractor_enriched.py        # E2 — LLM entity extractor (drop-in)
│   ├── lithology_normalizer.py             # E3 — CGI Simple Lithology mapping
│   ├── formation_classifier.py             # E4 — formation / stratigraphy tagger
│   ├── bha_normalizer.py                   # E5 — BHA component type normalization
│   ├── inject_geolytics_rag.py             # E6 — inject dictionary corpus into RAG
│   ├── pressure_classifier.py              # E7 — PPFG / pore-pressure classification
│   ├── phase_role_enricher.py              # E9 — drilling-phase role tagging
│   └── witsml_uri_aligner.py               # E10 — WITSML 2.0 + OSDU URI alignment
├── nlp/
│   └── acronym_expander.py                 # E8 — domain acronym expansion
├── graph/
│   └── cypher/
│       └── enrich_drilling_phases.cypher   # E9 — Cypher for phase enrichment
└── README.md
```

---

## Prerequisites

| Requirement | Version / detail |
|---|---|
| Python | 3.11+ |
| Neo4j | 5.x running at `bolt://localhost:7687` |
| `neo4j` driver | `pip install neo4j` |
| `langchain-openai` | `pip install langchain-openai` |
| `langchain-neo4j` | `pip install langchain-neo4j` |
| `OPENAI_API_KEY` | Set in environment |
| `NEO4J_URI` | Set in environment (default `bolt://localhost:7687`) |
| `NEO4J_USER` | Set in environment (default `neo4j`) |
| `NEO4J_PASSWORD` | Set in environment |
| Volve data ingested | Run the base SPE project ingestion first |

Install all Python dependencies in one step:

```bash
pip install neo4j langchain-openai langchain-neo4j
```

---

## Recommended execution order

Run the modules in sprint order.  Each sprint builds on the graph state left
by the previous one.

### Sprint 1 — Graph enrichment (no LLM required)

These modules operate directly on Neo4j with Cypher and do not call the OpenAI
API.

| Step | Module | What it does |
|---|---|---|
| 1 | `ingestion/witsml_uri_aligner.py` | Adds WITSML 2.0 + OSDU URIs to all nodes |
| 2 | `ingestion/lithology_normalizer.py` | Maps free-text lithology to CGI Simple Lithology URIs |
| 3 | `ingestion/bha_normalizer.py` | Normalizes BHA component type strings |
| 4 | `ingestion/pressure_classifier.py` | Tags pore-pressure regime per depth interval |
| 5 | `graph/cypher/enrich_drilling_phases.cypher` | Creates drilling-phase nodes and relationships |

### Sprint 2 — NLP enrichment

| Step | Module | What it does |
|---|---|---|
| 6 | `nlp/acronym_expander.py` | Expands domain acronyms in all node text properties |
| 7 | `ingestion/formation_classifier.py` | Tags formation nodes with GeoSciML age + rank |
| 8 | `ingestion/phase_role_enricher.py` | Assigns semantic roles to drilling-phase intervals |

### Sprint 3 — Agent integration (requires OPENAI_API_KEY)

| Step | Module | What it does |
|---|---|---|
| 9 | `ingestion/inject_geolytics_rag.py` | Injects geolytics RAG corpus into vector store |
| 10 | `ingestion/entity_extractor_enriched.py` | Re-extracts entities with enriched schema |
| 11 | `agent/tools/domain_knowledge_enriched.py` | Deploy enriched tool layer in the agent |

---

## Module usage

### E10 — witsml_uri_aligner.py

Adds `witsml_uri`, `osdu_kind`, `osdu_uri`, `geosciml_uri`, and `geo_uri`
properties to all existing Neo4j nodes.  Nodes that already have `witsml_uri`
set are skipped (idempotent).

**Align all node types:**

```python
from neo4j import GraphDatabase
from integrations.spe_volve.ingestion.witsml_uri_aligner import run_alignment

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
results = run_alignment(driver)
# returns {"Well": 3, "Wellbore": 8, "TrajectoryStation": 4200, ...}
driver.close()
```

**Align specific labels only:**

```python
results = run_alignment(driver, labels=["Well", "Wellbore", "TrajectoryStation"])
```

**Export RDF Turtle for validation:**

```python
from integrations.spe_volve.ingestion.witsml_uri_aligner import generate_rdf_triples

turtle = generate_rdf_triples(driver, "TrajectoryStation", limit=50)
with open("trajectory_stations.ttl", "w") as f:
    f.write(turtle)
```

**CLI:**

```bash
python -m integrations.spe_volve.ingestion.witsml_uri_aligner \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password secret \
    --rdf-label TrajectoryStation \
    --rdf-limit 50
```

**Load generated Turtle into Apache Jena Fuseki for SPARQL queries:**

```bash
curl -X POST http://localhost:3030/volve/data \
     -H "Content-Type: text/turtle" \
     --data-binary @trajectory_stations.ttl
```

---

### E2 — entity_extractor_enriched.py

Drop-in replacement for `src/volve/ingestion/entity_extractor.py` in the SPE
project.  Expands the allowed node and relationship types to capture the full
Volve drilling domain.

```python
from integrations.spe_volve.ingestion.entity_extractor_enriched import (
    extract_entities_from_chunks,
    write_graph_documents_to_neo4j,
)

# documents: list[langchain_core.documents.Document]
graph_docs = extract_entities_from_chunks(documents)
write_graph_documents_to_neo4j(graph_docs)
```

To see the enriched entity schema:

```python
from integrations.spe_volve.ingestion.entity_extractor_enriched import get_entity_schema
print(get_entity_schema())
```

---

### E3 — lithology_normalizer.py

Maps free-text lithology strings in `Lithology` and `Formation` nodes to
canonical CGI Simple Lithology URIs from
`data/cgi-lithology.json` in geolytics-dictionary.

```python
from integrations.spe_volve.ingestion.lithology_normalizer import normalize_lithologies

driver = GraphDatabase.driver(...)
normalize_lithologies(driver)  # mutates Lithology + Formation nodes in-place
```

---

### E4 — formation_classifier.py

Tags `Formation` nodes with GeoSciML `gsmlb:GeologicUnit` rank, CGI
chronostratigraphic age, and OSDU `reference-data--GeologicUnitType` kind,
sourced from `data/cgi-geologic-time.json` and `data/cgi-stratigraphic-rank.json`.

```python
from integrations.spe_volve.ingestion.formation_classifier import classify_formations

classify_formations(driver)
```

---

### E5 — bha_normalizer.py

Normalizes `BHAComponentType` and `Tubular` node type strings to IADC
vocabulary.  Adds `iadc_code` and `component_class` properties.

```python
from integrations.spe_volve.ingestion.bha_normalizer import normalize_bha_types

normalize_bha_types(driver)
```

---

### E6 — inject_geolytics_rag.py

Injects the geolytics-dictionary RAG corpus (`ai/rag-corpus.jsonl`) into the
agent's vector store (LangChain + Neo4j vector index).

```python
from integrations.spe_volve.ingestion.inject_geolytics_rag import inject_corpus

inject_corpus(
    driver=driver,
    corpus_path="path/to/geolytics-dictionary/ai/rag-corpus.jsonl",
    index_name="geolytics_rag",
)
```

---

### E7 — pressure_classifier.py

Classifies pore-pressure regimes (normal, sub-normal, over-pressure) for
depth intervals using the PPFG model from
`data/geomechanics-1d-curves-crosswalk.json`.

```python
from integrations.spe_volve.ingestion.pressure_classifier import classify_pressure_regimes

classify_pressure_regimes(driver)
```

---

### E8 — acronym_expander.py

Expands O&G acronyms in free-text node properties using `data/acronyms.json`
from geolytics-dictionary.

```python
from integrations.spe_volve.nlp.acronym_expander import expand_acronyms_in_graph

expand_acronyms_in_graph(driver, properties=["remarks", "description", "summary"])
```

---

### E9 — phase_role_enricher.py and enrich_drilling_phases.cypher

First run the Cypher to create `DrillingPhase` nodes and `IN_PHASE`
relationships:

```bash
cypher-shell -u neo4j -p secret < integrations/spe_volve/graph/cypher/enrich_drilling_phases.cypher
```

Then tag semantic roles on each phase:

```python
from integrations.spe_volve.ingestion.phase_role_enricher import enrich_phase_roles

enrich_phase_roles(driver)
```

---

### E1 — domain_knowledge_enriched.py

See the dedicated section below.

---

## Deploying domain_knowledge_enriched.py in the SPE project

`agent/tools/domain_knowledge_enriched.py` is a drop-in replacement for the
agent tool file that handles domain knowledge queries in the SPE project.

1. Locate the original file in the SPE project:

   ```
   spe-2026-challenge/src/volve/agent/tools/domain_knowledge.py
   ```

2. Back it up:

   ```bash
   cp src/volve/agent/tools/domain_knowledge.py \
      src/volve/agent/tools/domain_knowledge.original.py
   ```

3. Copy the enriched version:

   ```bash
   cp integrations/spe_volve/agent/tools/domain_knowledge_enriched.py \
      src/volve/agent/tools/domain_knowledge.py
   ```

4. No import changes are needed — the external function signatures are
   identical.  The enriched version adds:
   - WITSML/OSDU URI context in graph queries
   - Geolytics RAG corpus as fallback retrieval
   - Richer Cypher patterns for formation, BHA, and trajectory queries

---

## Expected impact by enrichment

| Module | Node types affected | Estimated volume (Volve) | Agent improvement |
|---|---|---|---|
| E10 witsml_uri_aligner | All 30 node types | ~15 000 nodes | SPARQL federation enabled; OSDU export ready |
| E2 entity_extractor | Well, Wellbore, Formation, BHARun, DailyReport | ~5 000 nodes | +40% entity recall vs. original 6-type schema |
| E3 lithology_normalizer | Lithology, Formation | ~800 nodes | CGI-canonical lithology enables cross-well correlation |
| E4 formation_classifier | Formation | ~120 nodes | Stratigraphic age + rank precision for depth queries |
| E5 bha_normalizer | Tubular, BHARun | ~300 nodes | IADC codes enable component-type filtering |
| E6 inject_geolytics_rag | Vector index | ~2 000 chunks | Dictionary definitions in agent RAG fallback |
| E7 pressure_classifier | TrajectoryStation, FormationMarker | ~4 500 nodes | Pore-pressure regime context for hazard queries |
| E8 acronym_expander | All text properties | ~12 000 properties | LLM comprehension of domain shorthand |
| E9 phase_role_enricher | DrillingActivity, DailyReport | ~600 nodes | Time-structured "what happened during section X" |

---

## Troubleshooting

### Neo4j connection refused

```
ServiceUnavailable: Failed to establish connection to bolt://localhost:7687
```

Check that Neo4j is running and the bolt port is accessible:

```bash
neo4j status
# or
docker ps | grep neo4j
```

Verify the credentials match those set during ingestion.

---

### `witsml_uri` already set — no nodes updated

The aligner is idempotent: it skips nodes where `witsml_uri IS NOT NULL`.
If you need to re-align (e.g., after a schema change), clear the flag first:

```cypher
MATCH (n) WHERE n.witsml_uri IS NOT NULL
REMOVE n.witsml_uri, n._aligned
```

---

### ImportError on `src.volve.config`

`entity_extractor_enriched.py` imports from the SPE project's own config module.
Run all scripts from the SPE project root, or set `PYTHONPATH`:

```bash
export PYTHONPATH=/path/to/spe-2026-challenge:$PYTHONPATH
```

---

### OPENAI_API_KEY not set

Modules in Sprint 3 (E2, E6, E1) require the OpenAI key:

```bash
export OPENAI_API_KEY=sk-...
```

---

### RDF Turtle load fails in Fuseki

If generated Turtle fails to load:

1. Validate locally with `riot` (Apache Jena CLI):

   ```bash
   riot --validate trajectory_stations.ttl
   ```

2. Check that the node being exported has been aligned first.  Nodes without
   `witsml_uri` are skipped by `generate_rdf_triples`.

---

### CGI lithology not found for a value

`lithology_normalizer.py` uses exact match and then fuzzy fallback against
`data/cgi-lithology.json`.  If a lithology string has no match, the node
receives `lithology_cgi_uri = null` and a `lithology_normalized = false` flag.
Add the missing mapping to the local override file in
`integrations/spe-volve/ingestion/lithology_overrides.json` (created on first
run).

---

## Related resources

- SPE 2026 challenge project: https://github.com/geolytics-energy/spe-2026-challenge
- geolytics-dictionary: https://github.com/geolytics-energy/geolytics-dictionary
- WITSML 2.0 crosswalk: `geolytics-dictionary/data/witsml-rdf-crosswalk.json`
- OSDU schema browser: https://schema.osdu.opengroup.org
- GeoSciML Borehole ontology: http://geosciml.org/def/gsmlbh
- CGI Simple Lithology: https://resource.geosciml.org/classifier/cgi/lithology
- QUDT units: https://qudt.org/vocab/unit/
