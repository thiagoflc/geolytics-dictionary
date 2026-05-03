# geobrain

Python SDK for the [Geolytics O&G Domain Dictionary](https://github.com/thiagoflc/geobrain) — a bilingual (Portuguese/English) semantic knowledge base for petroleum exploration and production.

## Features

- **Dictionary** — look up terms, acronyms, and ontology layers from the bundled dataset
- **KnowledgeGraph** — NetworkX-backed graph with entity lookup, neighborhood traversal, and shortest-path queries
- **Validator** — deterministic semantic validator with rule parity to `scripts/semantic-validator.js`; catches invalid SPE-PRMS categories, malformed ANP well codes, invalid regime contratual, and more
- **SweetExpander** — SWEET ontology URI expansion for Geolytics terms
- **CrosswalkIndex** — WITSML/ProdML RDF crosswalk lookup
- **BM25Retriever** — BM25 full-text retrieval over the RAG corpus
- **CLI** — `geolytics-validate` command for pipeline integration

## Installation

```bash
pip install geobrain
```

With optional extras:

```bash
# Knowledge graph support (requires networkx)
pip install "geobrain[graph]"

# BM25 RAG retrieval (requires rank-bm25)
pip install "geobrain[rag]"

# All extras
pip install "geobrain[graph,rag]"
```

## Quickstart

### Dictionary

```python
from geobrain import Dictionary

d = Dictionary()

# Search terms (case/accent-insensitive)
terms = d.lookup("Pré-sal")
print(terms[0].termo, terms[0].definicao)

# Acronym lookup
senses = d.acronym("BOP")
print(senses[0].expansion_pt)  # "Preventor de Erupção, Obturador de Segurança"

# List ontology layers
layers = d.layers()
for layer in layers:
    print(layer.id, layer.name, layer.concepts_count)
```

### Knowledge Graph

```python
from geobrain import KnowledgeGraph

kg = KnowledgeGraph.from_local()

# Entity lookup
entity = kg.entity("poco")
print(entity.label, entity.type)

# Neighbors within 2 hops
neighbors = kg.neighbors("poco", hops=2)
print([n.id for n in neighbors[:5]])

# Shortest path between two entities
path = kg.shortest_path("poco", "reservatorio")
print([e.id for e in path])

# Export to Cypher (Neo4j)
cypher = kg.cypher_export()
```

### Semantic Validator

```python
from geobrain import Validator

v = Validator()

# Free-text validation
report = v.validate("Reserva 4P do Campo de Búzios")
print(report.valid)           # False
print(report.violations[0].rule)  # "SPE_PRMS_INVALID_CATEGORY"
print(report.violations[0].suggested_fix)

# Validate with structural context (LAYER_COVERAGE_MISMATCH)
report = v.validate({
    "value": "poco",
    "context": {"entity_id": "poco", "layer": "layer1"},
})
print(report.valid)  # True

# Valid case
report = v.validate("Reservas 2P certificadas do Campo de Santos")
print(report.valid)  # True
```

### SWEET Expander

```python
from geobrain import SweetExpander

s = SweetExpander()

# Get SWEET URIs for a term
uris = s.expand("hidrocarboneto", strategy="exactMatch")
# ["http://sweetontology.net/matrOrganics/Hydrocarbon", ...]

# Full expansion with hierarchy
result = s.expand_full("reservatorio")
print(result.found)
print(result.sweet_uris)
print(result.hierarchy)
```

### CLI Validator

```bash
# Validate a claim
geolytics-validate "Reserva 4P do Campo de Búzios"

# Output JSON report
geolytics-validate --json "Bloco BS-500 em regime de Privatização"

# Read from stdin
echo "Reservas 2P certificadas" | geolytics-validate -
```

## LangChain Integration

```python
from langchain.tools import Tool
from geobrain import Validator, Dictionary

v = Validator()
d = Dictionary()

validate_tool = Tool(
    name="geolytics_validate",
    func=lambda text: str(v.validate(text)),
    description="Validates O&G domain claims against canonical SPE-PRMS and ANP rules.",
)

lookup_tool = Tool(
    name="geolytics_lookup",
    func=lambda q: str(d.lookup(q)),
    description="Looks up petroleum engineering terms in the Geolytics dictionary.",
)
```

## LlamaIndex Integration

```python
from llama_index.core.tools import FunctionTool
from geobrain import Dictionary

d = Dictionary()

dictionary_tool = FunctionTool.from_defaults(
    fn=lambda query: [t.definicao for t in d.lookup(query)],
    name="geobrain",
    description="Returns Portuguese/English definitions for O&G terms.",
)
```

## Bundled Data

The package ships with data bundled in `geobrain/_data/`:

| File                        | Description                                                           |
| --------------------------- | --------------------------------------------------------------------- |
| `full.json`                 | Complete dictionary: glossary, extended terms, acronyms, ontology map |
| `entity-graph.json`         | Knowledge graph nodes and edges                                       |
| `taxonomies.json`           | Canonical taxonomies (SPE-PRMS, lithology, well types, etc.)          |
| `sweet-alignment.json`      | SWEET ontology alignments for Geolytics terms                         |
| `witsml-rdf-crosswalk.json` | WITSML to RDF crosswalk                                               |
| `prodml-rdf-crosswalk.json` | ProdML to RDF crosswalk                                               |
| `rag-corpus.jsonl`          | BM25-indexed RAG corpus                                               |

## Validation Rules

The `Validator` implements deterministic rules with parity to `scripts/semantic-validator.js`:

| Rule ID                     | Severity | Description                                                                              |
| --------------------------- | -------- | ---------------------------------------------------------------------------------------- |
| `SPE_PRMS_INVALID_CATEGORY` | error    | Flags non-standard categories (4P, 5P, etc.). Valid: 1P, 2P, 3P, C1C, C2C, C3C           |
| `RESERVA_AMBIGUITY`         | warning  | Detects mixed O&G and environmental reserve signals in the same text                     |
| `REGIME_CONTRATUAL_INVALID` | error    | Flags regimes other than Concessao, Partilha de Producao, Cessao Onerosa                 |
| `TIPO_POCO_INVALID`         | error    | Validates ANP well code prefixes (1-, 2-, 3-, 4-, 6-, 7-)                                |
| `LITOLOGIA_INVALID`         | warning  | Checks lithology values against CGI/GeoSciML taxonomy                                    |
| `JANELA_GERACAO_INVALID`    | warning  | Validates maturity window terms against the generation window taxonomy                   |
| `ACRONYM_AMBIGUOUS`         | warning  | Flags known-ambiguous acronyms (PAD, UTS, GAS, BOP, etc.) without disambiguation context |
| `OSDU_KIND_FORMAT`          | error    | Validates OSDU kind strings against `opendes:osdu:<domain>--<Type>:<semver>`             |
| `LAYER_COVERAGE_MISMATCH`   | warning  | Checks entity geocoverage against asserted ontology layer                                |

## License

MIT. See [LICENSE](https://github.com/thiagoflc/geobrain/blob/main/LICENSE).
