# Geolytics Dictionary

Ontologia semântica do domínio de **Exploração & Produção (E&P) de petróleo e gás natural no Brasil**, derivada do módulo Dicionário da plataforma Geolytics. Dados oficiais da **ANP/SEP — SIGEP**, organizados como JSON estático, grafo de entidades e corpus pronto para RAG.

**Visualização interativa:** https://thiagoflc.github.io/geolytics-dictionary

## Python Package

```bash
pip install geolytics-dictionary
```

```python
from geolytics_dictionary import Dictionary, KnowledgeGraph, Validator, SweetExpander

d = Dictionary()
d.lookup("Pré-sal")          # list[Term]
d.acronym("BOP")             # list[Acronym]
d.layers()                   # list[Layer]

kg = KnowledgeGraph.from_local()
kg.entity("poco")
kg.shortest_path("poco", "reservatorio")

v = Validator()
v.validate("Reserva 4P do Campo de Búzios")  # Report with SPE_PRMS_INVALID_CATEGORY violation

s = SweetExpander()
s.expand("hidrocarboneto", strategy="exactMatch")  # list of SWEET URIs
```

See [`python/README.md`](python/README.md) for full documentation.

---

## Notebooks

Quatro notebooks Jupyter didáticos para cientistas de dados em geociências. Executáveis após `pip install -r notebooks/requirements.txt`.

| Notebook | Descrição |
|---|---|
| [`notebooks/01_explore_graph.ipynb`](notebooks/01_explore_graph.ipynb) | Exploração do grafo de entidades com NetworkX: estatísticas, sub-grafo ao redor de `poco`, caminho mais curto, comunidades e exportação GraphML. |
| [`notebooks/02_rag_with_validator.ipynb`](notebooks/02_rag_with_validator.ipynb) | Pipeline RAG sobre o `rag-corpus.jsonl` com índice BM25 (sem API key), demonstração de recuperação correta e detecção de alucinação via validador semântico. |
| [`notebooks/03_langgraph_multiagent.ipynb`](notebooks/03_langgraph_multiagent.ipynb) | Execução do agente LangGraph multi-nó com roteamento, decomposição multi-hop, validação e síntese; renderização do DAG em Mermaid e troca de provedor LLM. |
| [`notebooks/04_geomec_qa.ipynb`](notebooks/04_geomec_qa.ipynb) | Estudo de caso em geomecânica: consulta de propriedades elásticas para MEM 1D, Círculo de Mohr, validação SHACL `StressTensorShape` e crosswalk fratura-GSO. |

---

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `data/glossary.json` | 23 termos ANP enriquecidos (alinhamento ontológico, sinônimos PT/EN, exemplos) |
| `data/extended-terms.json` | 20 termos geológicos derivados de GeoCore/O3PO/GeoReservoir com `sweet_uri` |
| `data/sweet-alignment.json` | 66 alinhamentos SKOS com a ontologia SWEET (NASA/ESIPFed) — `sweet_uri`, `alignment_type`, `rationale_pt` |
| `data/sweet-modules.json` | Catálogo dos 20 módulos SWEET usados (id, full URI, descrição, contagem de termos) |
| `scripts/sweet-expand.js` | Módulo Node: `expand(termId)` — retorna URIs SWEET + hierarquia embutida para expansão semântica |
| `docs/SWEET.md` | O que é SWEET, como complementa o GeoCore, como os alinhamentos são curados, como agentes os usam |
| `data/datasets.json` | 8 datasets ANP/SEP-SIGEP com metadados de colunas |
| `data/entity-graph.json` | Grafo de 75 entidades + 80 relações com `petrokgraph_uri`, `osdu_kind`, `geocoverage` |
| `data/ontology-types.json` | Tipologia geoquímica (7) + níveis de processamento (3) + 4 domínios |
| `data/ontopetro.json` | Ontologia de domínio formal — 6 módulos (20 classes, 20 properties, 20 relations, 10 instances) |
| `data/taxonomies.json` | 13 enumerações canônicas (litologia, trapa, tipo poço ANP, SPE-PRMS, querogênio, janela de geração, seismic sources/receivers, AVO classes…) |
| `data/modules-extended.json` | Módulos M7 Geoquímica, M8 Rocha, M9 Geomecânica, M10 Fluidos (camada 6 — Petrobras) |
| `data/pvt-dictionary.json` | 34 campos PVT do sistema SIRR Petrobras com completude real |
| `data/systems.json` | 8 sistemas corporativos (GEOQWIN, SIRR, LIMS, AIDA, GDA, GEOMECBR, GERESIM, TrapTester) |
| `data/regis-ner-schema.json` | Mapeamento PetroGold (PUC-Rio) ↔ entity-graph para pipelines NER |
| `data/acronyms.json` | 1.102 siglas O&G PT/EN categorizadas (equipment, regulator, contract, env etc.) |
| `data/seismic-acquisition.json` | Modulo sismico P2.8 — Aquisicao: 20 classes, 17 propriedades, 9 relacoes, 3 instancias (Yilmaz 2001, Sheriff & Geldart 1995) |
| `data/seismic-processing.json` | Modulo sismico P2.8 — Processamento: 18 classes, 13 propriedades, 7 relacoes, 3 instancias (Yilmaz 2001) |
| `data/seismic-inversion-attributes.json` | Modulo sismico P2.8 — Inversao e Atributos: 25 classes, 15 propriedades, 9 relacoes, 4 instancias (Russell 1988, Connolly 1999, Chopra & Marfurt 2007, Coleou et al. 2003) |
| `data/full.json` | Merge de tudo acima (inclui modulo sismico P2.8) |
| `api/v1/seismic.json` | Modulo sismico consolidado (63 classes, 45 propriedades, 25 relacoes, 10 instancias) |
| `ai/ontology-map.json` | Mapa das **6 camadas** semânticas (BFO+GeoCore, O3PO, Petro KGraph, OSDU, ANP, Petrobras Internal) |
| `ontopetro.txt` | Ontologia de Geociências de Petróleo (fonte primária — não modificar) |
| `api/v1/index.json` | Manifesto da API com URLs de todos os endpoints |
| `api/v1/terms.json` | Lista plana de termos |
| `api/v1/entities.json` | Entidades com relações outgoing/incoming pré-computadas |
| `api/v1/datasets.json` | Datasets com lista de termos referenciados |
| `api/v1/acronyms.json` | API de siglas com counts por categoria |
| `api/v1/search-index.json` | Índice de busca client-side (id, text, type, tokens) |
| `ai/rag-corpus.jsonl` | 1.245 chunks para embedding (term, column, entity, domain, type, acronym) |
| `ai/system-prompt-ptbr.md` | System prompt PT-BR (~800 tokens) |
| `ai/system-prompt-en.md` | System prompt EN (~800 tokens) |
| `index.html` | Visualização D3 interativa (GitHub Pages) |
| `gso-cards.html` | Cards pyLODE-style das 213 classes GSO/Loop3D (camada 7, CC BY 4.0) |
| `data/gso-{faults,folds,foliations,lineations,contacts}.json` | 213 classes GSO L7 com `owl_uri`, parents, sources |
| `data/osdu-gso-crosswalk.json` | 14 mapeamentos SKOS OSDU↔GSO |
| `scripts/gso-extract.js` | Parser Turtle minimal para módulos GSO (sem rdflib) |
| `scripts/generate.js` | Regenera `/data`, `/api` e `/ai` |
| `data/geomechanics.json` | Ontologia geomecânica MEM (26 classes, 22 propriedades, 12 relações, 6 instâncias — P2.7) |
| `data/geomechanics-fractures.json` | Ramo de fraturas: 17 classes (DeformationMechanism, FaultZone, DamageZone, etc.) + regimes de Anderson (P2.7) |
| `data/fracture_to_gso.json` | 8 mapeamentos SKOS fracturas Geolytics ↔ GSO/Loop3D (P2.7) |
| `api/v1/geomechanics.json` | Endpoint consolidado (geomechanics + fractures + crosswalk) |
| `docs/GEOMECHANICS.md` | Conceito MEM, quatro pilares, mapeamento JSON, diagrama Mermaid, downstream applications (P2.7) |
| `data/geolytics-shapes.ttl` | 22 NodeShapes SHACL (inclui UCSValueShape, PoissonRatioShape, StressTensorShape — P2.7) |
| `data/geolytics-vocab.ttl` | Vocabulario OWL minimo de apoio (classes + propriedades) |
| `api/v1/geolytics-shapes.ttl` | Shapes SHACL servidos publicamente |
| `api/v1/geolytics-vocab.ttl` | Vocabulario OWL servido publicamente |
| `scripts/validate-shacl.py` | Validador Python (pyshacl) |
| `scripts/validate-shacl.js` | Wrapper Node.js (delega ao Python se necessario) |
| `docs/SHACL.md` | Documentacao do sistema SHACL |
| `docs/SEISMIC.md` | Documentacao do modulo sismico P2.8 (Aquisicao, Processamento, Inversao + diagrama Mermaid + mapeamento OSDU) |
| `data/witsml-rdf-crosswalk.json` | 25 classes WITSML 2.0 mapeadas para `geo:` + OSDU kind + GeoCore alignment (P2.9) |
| `data/prodml-rdf-crosswalk.json` | 15 classes PRODML 2.x mapeadas para `geo:` — inclui DTS, DAS, FiberOpticPath, FlowMeasurement (P2.9) |
| `data/witsml-sample.xml` | XML WITSML 2.0 realista: Well + Wellbore + Trajectory (5 estacoes) + 3 WellboreMarkers (P2.9) |
| `scripts/witsml-to-rdf.js` | Conversor WITSML XML → Turtle sem dependencias externas; CLI e API (P2.9) |
| `api/v1/witsml-rdf-crosswalk.json` | Crosswalk WITSML servido publicamente (copiado de data/) |
| `api/v1/prodml-rdf-crosswalk.json` | Crosswalk PRODML servido publicamente (copiado de data/) |
| `docs/WITSML.md` | Documentacao do mapeamento WITSML/PRODML → RDF: argumento linear→grafo, schema do crosswalk, exemplos SPARQL/Cypher |

---

## Alinhamento SWEET (Layer 8 — NASA/ESIPFed)

O Geolytics inclui **66 alinhamentos SKOS** com a ontologia [SWEET](https://github.com/ESIPFed/sweet) (Semantic Web for Earth and Environmental Terminology). Os alinhamentos cobrem tipos de rocha, minerais, fluidos, processos geológicos, reinos planetários, propriedades físicas, unidades de medida e intervalos de tempo geológico.

### Expansao semantica via sweet-expand.js

```bash
node scripts/sweet-expand.js hidrocarboneto
node scripts/sweet-expand.js diagenese --json
node scripts/sweet-expand.js falha-cisalhante --include-siblings
```

```javascript
import { expand } from './scripts/sweet-expand.js';
const result = expand('hidrocarboneto', { includeHierarchy: true });
// result.sweetUris    — URIs SWEET alinhadas
// result.hierarchy    — pais/filhos da hierarquia embutida
// result.alignments   — registros completos com rationale
```

As triplas SKOS (`skos:exactMatch`, `skos:closeMatch`, etc.) sao emitidas automaticamente em `data/geolytics.ttl` durante `node scripts/generate.js`.

Veja `docs/SWEET.md` para documentacao completa.

---

## Validacao SHACL formal

O grafo `data/geolytics.ttl` pode ser validado contra restricoes formais usando [SHACL](https://www.w3.org/TR/shacl/).

### Instalacao rapida

```bash
pip install -r scripts/requirements.txt
python scripts/validate-shacl.py
```

### O que e validado

- `geo:Poco` — `tipoPoco` de enum ANP canonico, `operador` e `bloco` com cardinalidade 1..1
- `geo:Bloco` — `regimeContratual` in {Concessao, Partilha, CessaoOnerosa}, `bacia` 1..1
- `geo:Reserva` — `categoriaSPEPRMS` in {1P,2P,3P,C1C,C2C,C3C}; disjunto de `ReservaAmbiental`
- `geo:osduKind` — padrao `opendes:osdu:master-data--TypeName:major.minor.patch`
- `geo:Acronym` — `sigla` obrigatorio, ao menos uma expansao PT/EN, `category` de lista canonica
- `geo:GSOClass` — `owlUri` com dominio `loop3d.org`
- `geo:geocoverage` — valores restritos a {layer1, layer1b, layer2, ..., layer7}
- `geo:OntopetroClass` — `classId` padrao `C000-C999`, ao menos um `source`
- Mais 8 shapes para classes de entidades, propriedades de objeto, links `owl:sameAs` e contratos E&P

Veja `docs/SHACL.md` para documentacao completa e instrucoes de como adicionar novas shapes.

---

## Como usar os dados

### Via raw GitHub

```
https://raw.githubusercontent.com/thiagoflc/geolytics-dictionary/main/data/glossary.json
https://raw.githubusercontent.com/thiagoflc/geolytics-dictionary/main/data/entity-graph.json
https://raw.githubusercontent.com/thiagoflc/geolytics-dictionary/main/ai/rag-corpus.jsonl
```

### Via GitHub Pages

```
https://thiagoflc.github.io/geolytics-dictionary/api/v1/index.json
https://thiagoflc.github.io/geolytics-dictionary/data/full.json
https://thiagoflc.github.io/geolytics-dictionary/ai/rag-corpus.jsonl
```

### Carregando o RAG corpus em LangChain (Python)

```python
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import urllib.request, json

URL = "https://thiagoflc.github.io/geolytics-dictionary/ai/rag-corpus.jsonl"
docs = []
with urllib.request.urlopen(URL) as f:
    for line in f:
        rec = json.loads(line)
        docs.append({"page_content": rec["text"], "metadata": rec["metadata"] | {"id": rec["id"], "type": rec["type"]}})

vs = FAISS.from_texts(
    [d["page_content"] for d in docs],
    OpenAIEmbeddings(),
    metadatas=[d["metadata"] for d in docs],
)
```

### Carregando em LlamaIndex (Python)

```python
from llama_index.core import Document, VectorStoreIndex
import urllib.request, json

URL = "https://thiagoflc.github.io/geolytics-dictionary/ai/rag-corpus.jsonl"
documents = []
with urllib.request.urlopen(URL) as f:
    for line in f:
        rec = json.loads(line)
        documents.append(Document(text=rec["text"], metadata={**rec["metadata"], "id": rec["id"], "type": rec["type"]}))

index = VectorStoreIndex.from_documents(documents)
```

### Usando o system prompt

Leia o conteúdo de `ai/system-prompt-ptbr.md` (ou `ai/system-prompt-en.md`) e use-o como mensagem de sistema do seu agente conversacional. Ele estabelece o contexto de domínio, define as entidades-chave e explicita os termos que tipicamente confundem modelos genéricos (PAD, UTS, Período Exploratório, Pré-sal, Concessão vs. Partilha).

### Text2Cypher / Text2SPARQL

O diretório `ai/` inclui arquivos de suporte para pipelines de perguntas em linguagem natural convertidas para Cypher (Neo4j) ou SPARQL (RDF/OWL).

| Arquivo | Conteúdo |
|---|---|
| `ai/graph-schema.md` | Fragmento de prompt com schema Neo4j: labels, propriedades, relações, cardinalidade e exemplos de tradução PT-BR → Cypher. Prepend ao system prompt ao usar Text2Cypher. |
| `ai/graph-schema-sparql.md` | Fragmento equivalente para SPARQL: prefixos reais do TTL, classes, propriedades OWL, triples de esquema e exemplos de queries. |
| `ai/text2cypher-fewshot.jsonl` | 45 exemplos few-shot (30+ obrigatórios) cobrindo todos os 7 tipos de entidade e os principais tipos de relação. |
| `ai/text2sparql-fewshot.jsonl` | 25 exemplos few-shot SPARQL equivalentes, usando os prefixos reais de `data/geolytics.ttl`. |

#### Formato dos exemplos few-shot

Cada linha dos arquivos `.jsonl` segue o schema:

```json
{
  "question_pt": "Qual é a cadeia completa de um poço até o campo que ele pode originar?",
  "question_en": "What is the full chain from a well to the field it can originate?",
  "cypher": "MATCH path = (p:Operational {id: 'poco'})-[:may_register]->(nd:Instrument {id: 'notificacao-descoberta'}), (b:Contractual {id: 'pad'})-[:may_yield]->(dc:Contractual {id: 'declaracao-comercialidade'})-[:originates]->(campo:Operational {id: 'campo'}) RETURN p.label AS poco, nd.label AS notificacao, dc.label AS declaracao, campo.label AS campo",
  "expected_columns": ["poco", "notificacao", "declaracao", "campo"],
  "difficulty": "multi-hop",
  "tags": ["operational", "contractual", "chain", "discovery", "campo"]
}
```

Para o arquivo SPARQL, o campo `cypher` é substituído por `sparql`:

```json
{
  "question_pt": "Quantas classes existem por tipo de entidade (geo:entityType)?",
  "question_en": "How many classes exist per entity type (geo:entityType)?",
  "sparql": "PREFIX geo: <https://geolytics.petrobras.com.br/dict/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nSELECT ?entityType (COUNT(?classe) AS ?total)\nWHERE {\n  ?classe a owl:Class ;\n          geo:entityType ?entityType .\n}\nGROUP BY ?entityType\nORDER BY DESC(?total)",
  "expected_columns": ["entityType", "total"],
  "difficulty": "aggregation",
  "tags": ["aggregation", "entity-type", "count"]
}
```

#### Casos difíceis cobertos

- Distinguir `geo:reserva` (SPE-PRMS 1P/2P/3P) de Reserva Ambiental (REBIO/RPPN).
- Distinguir regime Concessão vs Partilha de Produção.
- Siglas com múltiplos sentidos: `PAD` (Plano de Avaliação ≠ drilling pad), `UTS` (Unidades de Trabalho ≠ Unidade Territorial).
- Cadeias multi-hop: poço → bloco → bacia → regime contratual (4 saltos).
- Cadeias multi-hop: rodada de licitação → bloco → PAD → Declaração de Comercialidade → Primeiro Óleo.
- Campo Tensional (geomecânica) vs Campo de petróleo (ANP).
- Formação (unidade litoestratigráfica) vs Litologia (tipo petrográfico).

---

## Semantic Validator

A deterministic, side-effect-free validator that checks claims (free text or structured objects) against the canonical enumerations in `data/taxonomies.json`, `data/entity-graph.json`, and related files. Mirrors the Python validator at `examples/langgraph-agent/nodes/validator.py` and shares the same rule IDs.

### Rules enforced

| Rule ID | Severity | Description |
|---|---|---|
| `SPE_PRMS_INVALID_CATEGORY` | error | Only 1P/2P/3P (Reservas) and C1C/C2C/C3C (Recursos Contingentes) are valid |
| `RESERVA_AMBIGUITY` | warning | Flags "Reserva" near REBIO/RPPN/APA terms — distinguish SPE-PRMS vs ambiental |
| `REGIME_CONTRATUAL_INVALID` | error | Must be Concessão, Partilha de Produção, or Cessão Onerosa |
| `TIPO_POCO_INVALID` | error | ANP well code prefix must be 1, 2, 3, 4, 6, or 7 |
| `LITOLOGIA_INVALID` | warning | Lithology must be in canonical CGI/GeoSciML enumeration |
| `JANELA_GERACAO_INVALID` | warning | Generation window must match Ro% scale enumeration |
| `ACRONYM_AMBIGUOUS` | warning | Ambiguous siglas (PAD, UTS, API…) must include disambiguation context |
| `OSDU_KIND_FORMAT` | error | Must match `opendes:osdu:<domain>--<Type>:<major>.<minor>.<patch>` |
| `LAYER_COVERAGE_MISMATCH` | warning | Entity asserted in layer X but geocoverage does not include X |

The full machine-readable manifest is at `api/v1/validate-rules.json`.

### CLI usage

```bash
# Validate free text — exit code 0 = valid, 1 = violations
node scripts/validate-cli.js "Reserva 4P do Campo de Búzios"

# Valid claim
node scripts/validate-cli.js "Bloco BS-500 em regime de Concessão"

# Invalid regime
node scripts/validate-cli.js "Bloco BS-500 em regime de Privatização"

# Human-readable output
node scripts/validate-cli.js --format text "Reserva 4P do pré-sal"

# Validate a JSON file containing an array of claims
node scripts/validate-cli.js --file claims.json --format json
```

### JavaScript API

```js
const { validate } = require('./scripts/semantic-validator');

// Free-text claim
const result = validate('Reserva 4P do Campo de Búzios');
// { valid: false, violations: [{rule: 'SPE_PRMS_INVALID_CATEGORY', ...}], warnings: [] }

// Structured claim with layer-coverage check
const structured = validate({
  type: 'entity',
  value: 'poco referenciado em layer9',
  context: { entity_id: 'poco', layer: 'layer9' }
});
// { valid: true, violations: [], warnings: [{rule: 'LAYER_COVERAGE_MISMATCH', ...}] }

console.log(result.valid);          // false
console.log(result.violations[0].rule);        // 'SPE_PRMS_INVALID_CATEGORY'
console.log(result.violations[0].suggested_fix);
```

### Running the test suite

```bash
node --test tests/validator.test.js
```

---

## Modelo de entidades

| Tipo | Cor | Entidades |
|---|---|---|
| **operational** | `#378ADD` | Poço, Bloco, Campo, Bacia Sedimentar |
| **contractual** | `#7F77DD` | Contrato E&P, PAD, Rodada de Licitação, Declaração de Comercialidade |
| **actor** | `#D85A30` | Operador, ANP, IBAMA, CONAMA, ANA, IBP, BNDES |
| **instrument** | `#888780` | SIGEP, SEP, UTS, Regime Contratual, Período Exploratório, Processo Sancionador, Notificação Descoberta, Área de Desenvolvimento, EIA, RIMA, AFE, JOA, EPC |
| **geological** | `#639922` | Pré-sal, Bacias Agrupadas, Ambiente |
| **equipment** | `#C77B30` | BOP, FPSO, ANM, Riser, ROV, DHSV, BHA, ESP/BCS, MWD, LWD, Manifold Submarino |

Relações entre entidades são tipadas (`drilled_in`, `governed_by`, `evaluates`, `originates`, etc.) e classificadas como `solid` (sempre presente) ou `dashed` (condicional).

---

## Siglário O&G

O arquivo `data/acronyms.json` traz 1.102 siglas curadas do domínio óleo e gás (PT/EN), parseadas e categorizadas a partir de fonte comunitária. Cada entrada tem:

```json
{
  "id": "bop",
  "sigla": "BOP",
  "expansion_pt": "Preventor de Erupção, Obturador de Segurança",
  "expansion_en": "Blowout Preventer",
  "category": "equipment",
  "it_generic": false
}
```

**Categorias**: `equipment` (180), `measurement` (122), `fluid` (113), `process` (74), `environmental` (53), `standard_body` (51), `contract` (47), `unit` (40), `lithology` (39), `geophysics` (33), `well_state` (14), `regulator` (14), `it_generic` (23), `general` (294), `organization` (5).

**Múltiplos sentidos**: a mesma sigla pode ter várias entradas (ex.: BO = "Barrels of Oil" e "Bottom Oil"; BT = "Total Formation Volume Factor" + "Bathythermograph" + "Build and Transfer"). O campo `id` distingue cada sentido; `sigla` é compartilhada.

**Filtragem para RAG**: siglas com `it_generic: true` (CMOS, RAM, FFT, OSI…) são excluídas do `rag-corpus.jsonl` para não competir com o sinal de domínio, mas continuam no JSON para referência.

**Regenerar**: `node scripts/build-acronyms.js` reprocessa `scripts/acronyms-source.txt` → `data/acronyms.json`.

---

## Arquitetura semântica em 6 camadas

O domínio de O&G brasileiro se organiza em 6 camadas independentes e complementares. Cada termo do dicionário tem o campo `geocoverage` listando em quais camadas ele tem cobertura formal.

| Layer | Nome | Mantenedor | Tipo | Cobertura no dicionário |
|---|---|---|---|---|
| **layer1** | BFO + GeoCore | UFRGS/BDI + Geosiris | ontologia formal (OWL/BFO) | Bacia, Pré-sal, Formação, Reservatório, Litologia, Processo Geológico |
| **layer2** | O3PO + GeoReservoir | UFRGS/BDI | ontologia de domínio | Poço, Reservatório, Sistema Deposicional, Completação, Lâmina d'Água, Acumulação |
| **layer3** | Petro KGraph | PUC-Rio / Petroles | knowledge graph PT-BR (539 conceitos) | Bacia, Poço, Bloco, Operador, Pré-sal, Reservatório, Formação |
| **layer4** | OSDU | The Open Group (Petrobras membro) | schema de dados (Apache 2.0) | Poço, Bacia, Campo, Operador, Reservatório, Completação |
| **layer5** | ANP / SIGEP / Lei 9478/1997 | ANP | marco regulatório brasileiro | Todos os 23 termos do glossário |
| **layer6** | Geolytics / Petrobras Internal | Petrobras / Geolytics | ontologia corporativa interna | Módulos M7/M8/M9/M10 — sistemas corporativos (GEOQWIN, SIRR, GDA, GEOMECBR…) |

**Regra de deduplicação:**
- **Petro KGraph é construído sobre GeoCore** — não são duplicatas. Use `petrokgraph_uri` como referência primária para RAG em português.
- **OSDU é schema de dados IT**, não ontologia filosófica. Complementar a todos os outros. Use `osdu_kind` para interoperabilidade com sistemas Petrobras.
- **Camada ANP é única** e não sobrepõe nenhuma ontologia internacional.
- **Camada 6 (Petrobras Internal) é o ativo técnico mais valioso** — namespace `https://petrobras.com.br/geolytics/ontology/`. Apenas definições conceituais públicas; dados Sigilo=Interno NÃO são publicados.

Veja `ai/ontology-map.json` para a documentação completa de cada camada com URLs OWL, GitHub e regras de uso.

## Conceitos exclusivamente brasileiros (camada 5)

Os 11 conceitos abaixo **não existem em nenhuma ontologia internacional** de geologia ou petróleo (GeoCore, Petro KGraph, OSDU, IFC, BFO). São exclusivos do framework regulatório da ANP / Lei nº 9.478/1997 / Lei nº 12.351/2010:

- **Bloco** (não é "lease" ou "license" americano)
- **PAD — Plano de Avaliação de Descobertas** (não é "appraisal" genérico)
- **Contrato de E&P** (estrutura jurídica brasileira específica)
- **Rodada de Licitação** (numeradas desde 1999)
- **UTS — Unidades de Trabalho** (métrica brasileira para o PEM)
- **Regime Contratual** (Concessão vs. Partilha de Produção)
- **Período Exploratório** (1º, 2º, 3º PE — fase contratual com prazo)
- **Etapa Prorrogada** (resolução ANP específica)
- **Processo Sancionador** (procedimento ANP/SEP)
- **Notificação de Descoberta** (registro ANP por poço)
- **Declaração de Comercialidade** (marco regulatório que origina o Campo)

Por isso este dicionário existe — para preencher esta lacuna ontológica.

## Sobre o Petro KGraph

O **Petro KGraph** é uma ontologia formal de Óleo & Gás em português desenvolvida pela **PUC-Rio / PetroNLP** com **539 conceitos formais** populados com instâncias ANP públicas e relações extraídas de documentos técnicos por NLP. **É construído sobre GeoCore** (UFRGS/BDI). Inclui corpora anotados: PetroGold (NER), PetroNER, PetroRE (extração de relações). É a camada mais adequada para RAG em português. Repositório: https://github.com/Petroles/PetroNLP

## Sobre PPDM e SPE-PRMS

**PPDM (Professional Petroleum Data Management Association)** é o padrão internacional clássico de modelagem de dados de E&P, originário da Society of Petroleum Engineers nos anos 1990. Define entidades canônicas como Well, Wellbore, Field, Reservoir, Trap, Play, Prospect, Resource, Reserve. O ontopetro deste dicionário (`data/ontopetro.json`) usa PPDM como uma das fontes principais (junto com GeoCore) — ver coluna `sources` em cada classe (C001-C020).

**SPE-PRMS (Society of Petroleum Engineers — Petroleum Resources Management System)** é o sistema canônico de classificação de recursos e reservas de hidrocarbonetos. Define a hierarquia Reservas (1P/2P/3P, com graus de certeza) vs. Recursos Contingentes (C1C/C2C/C3C). A taxonomia SPE-PRMS está modelada em `data/taxonomies.json` com alerta RAG explícito de que "Reserva (SPE-PRMS) ≠ Reserva Ambiental (REBIO/RPPN)".

## Sobre OSDU

**OSDU — Open Subsurface Data Universe** é o padrão global de dados de subsuperfície da indústria petrolífera, mantido pelo The Open Group. Petrobras é membro ativo. Cobre schemas para Well, Wellbore, Field, Basin, SeismicAcquisition, Trajectory, WellLog. Não é ontologia formal — é schema de dados para interoperabilidade IT. Licença Apache 2.0. Os campos `osdu_kind` no dicionário usam o formato `opendes:osdu:master-data--[Type]:1.0.0`.

---

## Fontes

- **Lei nº 9.478/1997** (Lei do Petróleo) — instituiu a ANP e o atual marco regulatório de E&P no Brasil.
- **ANP — Agência Nacional do Petróleo, Gás Natural e Biocombustíveis** — autarquia federal regulatória.
- **SEP — Superintendência de Exploração** da ANP.
- **SIGEP — Sistema de Informações Gerenciais de Exploração e Produção**.
- Resoluções ANP nº 708/2017 e nº 815/2020.
- Contato dos datasets: `sigep_sep@anp.gov.br`.

---

## Graph database

O dicionário pode ser carregado em um Neo4j 5 local para consultas Cypher multi-hop, análise de caminhos e exploração interativa do grafo.

### Quickstart

```bash
node scripts/build-neo4j.js
docker compose up
```

O primeiro comando gera `build/neo4j/nodes.cypher` e `build/neo4j/relationships.cypher`. O `docker compose up` sobe o Neo4j 5 Community com APOC e executa o `loader` que importa os dois arquivos automaticamente (aguarda o Neo4j ficar saudável antes de iniciar).

Browser: http://localhost:7474 — login `neo4j` / senha `geolytics123`.

### Exemplo rápido

```cypher
// Todas as entidades operacionais sem URI no Petro KGraph
MATCH (e:Operational)
WHERE e.petrokgraph_uri IS NULL
RETURN e.id, e.label, e.geocoverage
ORDER BY e.label
```

### Consultas de exemplo

O diretório `docs/queries/` contém 6 consultas comentadas em PT-BR:

| Arquivo | Pergunta |
|---|---|
| `01-poco-bloco-bacia-regime.cypher` | Caminho multi-hop poço → bloco → bacia → regime contratual |
| `02-gso-falha-osdu-crosswalk.cypher` | Classes GSO de falhas com mapeamento OSDU |
| `03-entidades-sem-petrokgraph.cypher` | Entidades sem URI no Petro KGraph (lacunas ontológicas) |
| `04-caminho-mais-curto.cypher` | Menor caminho entre quaisquer dois nós (com e sem APOC) |
| `05-cascata-regulatoria.cypher` | Cascata regulatória Lei 9.478 → ANP → SIGEP |
| `06-desambiguacao-siglas.cypher` | Siglas com múltiplos sentidos no domínio O&G |

---

## MCP server

The `mcp/geolytics-mcp/` directory contains a TypeScript MCP server that exposes the dictionary as 9 AI tools over stdio transport. Any MCP-compatible agent (Claude Desktop, Claude Code, Cursor, LangGraph) can use it offline without an API key or embedding provider.

### Install and build

```bash
cd mcp/geolytics-mcp
npm install
npm run build
```

### Configuration

**Claude Desktop** — add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/path/to/geolytics-dictionary/mcp/geolytics-mcp/dist/index.js"]
    }
  }
}
```

**Claude Code** — add to your project's `.claude/settings.json` or globally to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/path/to/geolytics-dictionary/mcp/geolytics-mcp/dist/index.js"]
    }
  }
}
```

**Cursor** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "geolytics": {
      "command": "node",
      "args": ["/path/to/geolytics-dictionary/mcp/geolytics-mcp/dist/index.js"]
    }
  }
}
```

### Available tools

| Tool | Description |
|---|---|
| `lookup_term` | Search glossary + extended-terms + ontopetro by name (PT/EN), with fuzzy option |
| `expand_acronym` | Expand an O&G sigla; returns all senses with disambiguation hint |
| `get_entity` | Fetch entity node with all outgoing/incoming relations resolved |
| `get_entity_neighbors` | Multi-hop BFS traversal (1-3 hops), optional edge type filter |
| `validate_claim` | Validate natural-language claim against the ontology (requires P1.4) |
| `cypher_query` | Run Cypher against Neo4j — only active when `NEO4J_URI` is set |
| `search_rag` | BM25 full-text search over `ai/rag-corpus.jsonl` (no embedding provider) |
| `list_layers` | List all semantic layers with metadata |
| `crosswalk_lookup` | Find equivalent terms across layers by URI, OSDU kind or entity id |

See `mcp/geolytics-mcp/README.md` for full documentation, sample call/response shapes, and Neo4j setup.

---

## Regenerando os dados

```bash
node scripts/generate.js
```

O script regrava todos os arquivos em `/data`, `/api/v1` e `/ai`. Os dados-fonte (GLOSSARIO, CONJUNTOS, ONTOLOGY, DOMAINS, ENTITY_NODES, EDGES) ficam embedados no próprio script — para sincronizar com o Geolytics, copie os exports de `src/config/dicionario.js` e `src/config/ontology.js`.

---

## Continuous Integration

Every pull request and push to `main` runs a suite of automated checks via GitHub Actions.

### Workflows

| Workflow | File | Trigger |
|---|---|---|
| CI | `.github/workflows/ci.yml` | push / pull_request |
| Release | `.github/workflows/release.yml` | tag `v*` |

### CI jobs (`.github/workflows/ci.yml`)

| Job | What it checks |
|---|---|
| `lint` | Node syntax (`node --check`) over all `scripts/*.js`; Python syntax (`python -m py_compile`) over all `.py` files |
| `node-tests` | Runs `node --test tests/validator.test.js`; then verifies that `node scripts/generate.js` produces no diff in `data/full.json` or `api/v1/` |
| `shacl` | Installs pyshacl + rdflib in an isolated venv and runs `python scripts/validate-shacl.py` |
| `python-tests` | Installs the Python package and runs `pytest python/tests/ -q` |
| `langgraph-tests` | Installs LangGraph agent deps (CPU-only) and runs `pytest examples/langgraph-agent/tests/ -q` |
| `eval` | Runs the offline eval harness (`--runner vector_only` and `--runner graphrag_validator`, `--offline --limit 30`), generates the report, and fails if the composite score regresses more than 5% below `eval/baseline.json`. On `main`, updates `eval/baseline.json` automatically. |
| `mcp-build` | Installs `mcp/geolytics-mcp` deps and runs `npx tsc --noEmit` to verify TypeScript compiles without errors |
| `graph-diff` | Posts a Markdown comment on the PR summarising added/removed nodes and edges in `data/entity-graph.json` |

All jobs run on `ubuntu-latest` with Node 20 and Python 3.11 in parallel (no inter-job dependencies). The only secret required for releases is the PyPI OIDC environment (`pypi`); all CI jobs run without secrets from a fresh clone.

### Verifying regen locally

```bash
bash scripts/check-regen.sh
```

This runs `node scripts/generate.js` and exits non-zero if any tracked file changes. Run this before every commit that touches `data/` sources inside `scripts/generate.js`.

### Release workflow (`.github/workflows/release.yml`)

Push a tag matching `v*` to trigger a PyPI publish. The workflow builds the wheel from `python/` using `python -m build` and publishes via OIDC (no long-lived token needed — configure the `pypi` GitHub environment with the Trusted Publisher on PyPI).

---

## Licença

- **Codigo** (`scripts/`, `index.html`): MIT.
- **Dados** (`data/`, `api/`, `ai/`): derivados de informacoes publicas da ANP/SEP. Uso livre para fins educacionais, de pesquisa e desenvolvimento, mantendo a atribuicao a fonte original.
