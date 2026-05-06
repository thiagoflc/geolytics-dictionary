# Python Package — `geobrain`

SDK Python para integrar o GeoBrain em pipelines, notebooks ou agentes próprios. Fornece **4 classes principais** com API limpa e idiomática.

📦 PyPI: `pip install geobrain`
📁 Diretório: [`python/geobrain/`](https://github.com/thiagoflc/geolytics-dictionary/tree/main/python/geobrain)
📁 README: [python/README.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/python/README.md)

---

## Instalação

```bash
# Versão básica (apenas Dictionary, Validator)
pip install geobrain

# Com suporte a grafo (NetworkX)
pip install "geobrain[graph]"

# Com suporte a RAG (BM25 + corpus)
pip install "geobrain[rag]"

# Tudo
pip install "geobrain[graph,rag]"
```

> Versão mínima do Python: 3.10. Testado em CI em 3.10, 3.11 e 3.12.

---

## API pública (4 classes principais)

```python
from geolytics_dictionary import (
    Dictionary,
    KnowledgeGraph,
    Validator,
    SweetExpander,
)
```

| Classe            | Para que serve                                        | Módulo de implementação |
| ----------------- | ----------------------------------------------------- | ------------------------ |
| `Dictionary`      | Busca em glossário, siglas, camadas                   | `geobrain/dictionary.py` |
| `KnowledgeGraph`  | Manipulação do grafo de entidades (NetworkX)          | `geobrain/graph.py`      |
| `Validator`       | Validação semântica de claims em texto                | `geobrain/validator.py`  |
| `SweetExpander`   | Expansão SKOS com SWEET (NASA/ESIPFed)                | `geobrain/sweet.py`      |

Mais módulos auxiliares: `crosswalk.py`, `lithology.py`, `rag.py`, `data.py`.

---

## Quickstart

```python
from geolytics_dictionary import Dictionary

d = Dictionary()
results = d.lookup("Pre-sal")
for term in results:
    print(term.label, term.geocoverage, term.description[:80])
# → "Pré-sal" ['L5', 'L6'] "Província petrolífera offshore brasileira..."
```

---

## `Dictionary` — busca em glossário e siglas

```python
from geolytics_dictionary import Dictionary

d = Dictionary()

# Lookup por termo (PT/EN, sinônimos)
terms = d.lookup("Pre-sal")              # list[Term]
terms = d.lookup("BOP", fuzzy=True)      # tolera typos

# Expandir sigla
acronyms = d.acronym("BOP")              # list[Acronym]
for a in acronyms:
    print(a.expansion, a.layer, a.context)
# → "Blowout Preventer" "L4" "Drilling equipment"
# → "Bandeira de Operação Padrão" "L6" "Petrobras corporate"

# Listar camadas
for layer in d.layers():
    print(layer.id, layer.name)
# → L1 "BFO + GeoCore"
# → L1b "GeoSciML / CGI"
# ...
```

### Estrutura de `Term`

```python
@dataclass
class Term:
    id: str
    label: str
    description: str
    layer: str               # layer principal
    geocoverage: list[str]   # todas as camadas que cobrem
    petrokgraph_uri: str | None
    osdu_kind: str | None
    geosciml_uri: str | None
    synonyms: list[str]
    anp_normative: list[str]
```

---

## `KnowledgeGraph` — exploração do grafo

```python
from geolytics_dictionary import KnowledgeGraph

kg = KnowledgeGraph.from_local()           # carrega data/entity-graph.json
# Alternativa: KnowledgeGraph.from_url("https://thiagoflc.github.io/geobrain/api/v1/entities.json")

# Inspecionar nó
e = kg.entity("poco")
print(e.label, e.type, e.geocoverage)

# Vizinhos (1 ou N hops)
neighbors_1 = kg.neighbors("poco", hops=1)
neighbors_2 = kg.neighbors("poco", hops=2)

# Caminho mínimo
path = kg.shortest_path("poco", "regime-contratual")
print(" → ".join(path))
# → "poco → bloco → contrato-ep → regime-contratual"

# Filtrar
contratuais = [e for e in kg.entities() if e.type == "Contractual"]

# Exportar para Cypher (string)
cypher = kg.cypher_export(filter=lambda e: e.type == "Operational")
```

> Requer `pip install "geobrain[graph]"` (NetworkX).

---

## `Validator` — validação semântica

```python
from geolytics_dictionary import Validator

v = Validator()

# Validar uma claim
report = v.validate("Reserva 4P do Campo de Buzios")
print(report.valid)               # False
for vio in report.violations:
    print(vio.rule, vio.severity, vio.evidence)
# → SPE_PRMS_INVALID_CATEGORY error 4P

# Listar todas as regras disponíveis
for rule in v.rules():
    print(rule.id, rule.severity, rule.source_layer)

# Validar batch (claims de um relatório, por exemplo)
claims = [
    "Bloco BS-500 sob regime de Concessão.",
    "Reserva 4P do Campo de Buzios estimada em 5 bi boe.",
]
reports = [v.validate(c) for c in claims]
```

### Estrutura de `Report`

```python
@dataclass
class Violation:
    rule: str
    severity: str             # "error" | "warning" | "info"
    evidence: str
    suggested_fix: str
    source_layer: str

@dataclass
class Report:
    valid: bool
    violations: list[Violation]
    warnings: list[Violation]
```

> Mesma lógica de [`scripts/semantic-validator.js`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/scripts/semantic-validator.js) — paridade JS↔Python testada em CI.

---

## `SweetExpander` — alinhamento SWEET

```python
from geolytics_dictionary import SweetExpander

ex = SweetExpander()

# Expansão de um termo via SKOS
result = ex.expand("formacao-marizal", strategy="closeMatch")
print(result.sweet_uris)
# → ["http://sweetontology.net/realmGeolStratiUnit#Formation", ...]
print(result.broader_terms)    # termos mais gerais
print(result.narrower_terms)   # termos mais específicos

# Estratégias suportadas: exact, close, related
```

Útil para enriquecer queries com termos correlatos do SWEET.

---

## Módulos auxiliares

### `crosswalk` — mapeamentos cross-camada

```python
from geolytics_dictionary.crosswalk import CrosswalkIndex

cw = CrosswalkIndex()
cw.find("bloco", from_layer="L5", to_layer="L4")  # OSDU equivalente
cw.find("poco", from_layer="L5", to_layer="L4")   # → osdu:work-product-component--Wellbore
```

### `lithology` — CGI Simple Lithology

```python
from geolytics_dictionary.lithology import LithologyDictionary

lith = LithologyDictionary()
lith.lookup("granite")                # CGI URI + descrições
lith.osdu_equivalent("granite")       # mapping OSDU
```

### `rag` — corpus para BM25/embeddings

```python
from geolytics_dictionary.rag import RAGCorpus

corpus = RAGCorpus.from_local()
results = corpus.search_bm25("regime contratual concessão", top_k=5)
for r in results:
    print(r.id, r.text[:80], r.metadata)
```

---

## Integração com LangChain / LlamaIndex

```python
from langchain.schema import Document
from geolytics_dictionary.rag import RAGCorpus

# Corpus → list[Document] LangChain
corpus = RAGCorpus.from_local()
docs = [Document(page_content=c.text, metadata=c.metadata) for c in corpus.chunks]

# Indexar com seu vector store favorito
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
vs = FAISS.from_documents(docs, OpenAIEmbeddings())
```

---

## Carregar dados via URL (sem clonar repo)

```python
kg = KnowledgeGraph.from_url(
    "https://thiagoflc.github.io/geobrain/api/v1/entities.json"
)
```

GitHub Pages serve `api/v1/*` com cache eterno (versionado por commit). Bom para apps de produção.

---

## Versionamento

```python
import geolytics_dictionary
print(geolytics_dictionary.__version__)
# → "0.4.2"
```

Versão definida em [`python/geobrain/_version.py`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/python/geobrain/_version.py) (single source of truth — pyproject.toml lê dinamicamente).

---

## Testes

```bash
cd python
pytest -v
```

Cobertura ~85%. CI em [.github/workflows/test-python.yml](https://github.com/thiagoflc/geolytics-dictionary/blob/main/.github/workflows/test-python.yml).

---

## Padrões de design

### 🟢 Lazy loading

JSON é carregado só quando necessário. `Dictionary()` é instantâneo; primeira chamada a `.lookup()` carrega o glossário.

### 🟢 Imutabilidade

`Term`, `Entity`, `Report` são `@dataclass(frozen=True)`. Sem mutação acidental.

### 🟢 Compatibilidade com type hints

API completamente tipada. `mypy --strict` passa.

### 🟢 Sem flutuação semântica entre versões

Major bumps (0.x → 1.x) reservados para breaking changes. SDK e MCP server compartilham mesmo schema de dados.

---

## Roadmap

- [ ] `geobrain.agent` — agente LangGraph empacotado
- [ ] `geobrain.neo4j` — driver wrapper para Cypher convencional
- [ ] Async API completa (`async def lookup`)
- [ ] Tipos `Pydantic v2` opcionais para validação client-side

---

## Troubleshooting

| Erro                                              | Causa                              | Fix                                        |
| ------------------------------------------------- | ---------------------------------- | ------------------------------------------ |
| `ImportError: networkx required`                  | Faltou install com `[graph]`        | `pip install "geobrain[graph]"`            |
| `RAGCorpus from_local() vazio`                    | Pacote não tem `rag-corpus.jsonl`   | Use `from_url()` ou clone o repo            |
| `Validator port out of date`                      | Lógica JS evoluiu, Python ficou para trás | Issue no GitHub — paridade é teste de CI |

---

> **Próximo:** ver o [[MCP Server]] (mesma base, interface diferente) ou subir o grafo no [[Neo4j Setup]].
