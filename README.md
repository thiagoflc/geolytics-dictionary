# Geolytics Dictionary

Ontologia semântica do domínio de **Exploração & Produção (E&P) de petróleo e gás natural no Brasil**, derivada do módulo Dicionário da plataforma Geolytics. Dados oficiais da **ANP/SEP — SIGEP**, organizados como JSON estático, grafo de entidades e corpus pronto para RAG.

**Visualização interativa:** https://thiagoflc.github.io/geolytics-dictionary

---

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `data/glossary.json` | 23 termos ANP enriquecidos (alinhamento ontológico, sinônimos PT/EN, exemplos) |
| `data/extended-terms.json` | 8 termos geológicos derivados de GeoCore/O3PO/GeoReservoir |
| `data/datasets.json` | 8 datasets ANP/SEP-SIGEP com metadados de colunas |
| `data/entity-graph.json` | Grafo de 75 entidades + 80 relações com `petrokgraph_uri`, `osdu_kind`, `geocoverage` |
| `data/ontology-types.json` | Tipologia geoquímica (7) + níveis de processamento (3) + 4 domínios |
| `data/ontopetro.json` | Ontologia de domínio formal — 6 módulos (20 classes, 20 properties, 20 relations, 10 instances) |
| `data/taxonomies.json` | 9 enumerações canônicas (litologia, trapa, tipo poço ANP, SPE-PRMS, querogênio, janela de geração…) |
| `data/modules-extended.json` | Módulos M7 Geoquímica, M8 Rocha, M9 Geomecânica, M10 Fluidos (camada 6 — Petrobras) |
| `data/pvt-dictionary.json` | 34 campos PVT do sistema SIRR Petrobras com completude real |
| `data/systems.json` | 8 sistemas corporativos (GEOQWIN, SIRR, LIMS, AIDA, GDA, GEOMECBR, GERESIM, TrapTester) |
| `data/regis-ner-schema.json` | Mapeamento PetroGold (PUC-Rio) ↔ entity-graph para pipelines NER |
| `data/acronyms.json` | 1.102 siglas O&G PT/EN categorizadas (equipment, regulator, contract, env etc.) |
| `data/full.json` | Merge de tudo acima |
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

## Regenerando os dados

```bash
node scripts/generate.js
```

O script regrava todos os arquivos em `/data`, `/api/v1` e `/ai`. Os dados-fonte (GLOSSARIO, CONJUNTOS, ONTOLOGY, DOMAINS, ENTITY_NODES, EDGES) ficam embedados no próprio script — para sincronizar com o Geolytics, copie os exports de `src/config/dicionario.js` e `src/config/ontology.js`.

---

## Licença

- **Código** (`scripts/`, `index.html`): MIT.
- **Dados** (`data/`, `api/`, `ai/`): derivados de informações públicas da ANP/SEP. Uso livre para fins educacionais, de pesquisa e desenvolvimento, mantendo a atribuição à fonte original.
