# Arquitetura do GeoBrain

Documentacao da arquitetura semantica, pipeline ETL e topologia do agente GraphRAG.

---

## Visao geral das camadas semanticas

O GeoBrain organiza o conhecimento de E&P em 8 camadas semânticas independentes e complementares. Cada termo carrega o campo `geocoverage` indicando em quais camadas possui cobertura formal.

```mermaid
graph TD
    L1["Layer 1 — BFO + GeoCore<br/>(UFRGS/BDI + Geosiris)<br/>ontologia formal OWL/BFO"]
    L1B["Layer 1b — GeoSciML / CGI<br/>Simple Lithology<br/>437 conceitos CGI Simple Lithology"]
    L2["Layer 2 — O3PO + GeoReservoir<br/>(UFRGS/BDI)<br/>ontologia de dominio"]
    L3["Layer 3 — Petro KGraph<br/>(PUC-Rio / PetroNLP)<br/>539 conceitos PT-BR"]
    L4["Layer 4 — OSDU<br/>(The Open Group)<br/>schema de dados IT"]
    L5["Layer 5 — ANP / SIGEP<br/>marco regulatorio brasileiro<br/>Lei 9.478/1997"]
    L6["Layer 6 — Geolytics / Petrobras<br/>ontologia corporativa interna<br/>modulos M7-M10"]
    L7["Layer 7 — GSO / Loop3D<br/>(ARDC / GeoScience Australia)<br/>213 classes estruturais"]

    L1 --> KG["Knowledge Graph<br/>data/entity-graph.json<br/>170 nos + 259 relacoes"]
    L1B --> KG
    L2 --> KG
    L3 --> KG
    L4 --> KG
    L5 --> KG
    L6 --> KG
    L7 --> KG

    KG --> API["API REST estatica<br/>api/v1/<br/>23 endpoints"]
    KG --> RAG["RAG Corpus<br/>ai/rag-corpus.jsonl<br/>2.674 chunks"]
    KG --> NEO["Neo4j 5<br/>Cypher multi-hop"]
    KG --> TTL["RDF / SHACL<br/>data/geolytics.ttl<br/>data/geolytics-shapes.ttl"]

    API --> MCP["MCP Server<br/>mcp/geobrain-mcp/<br/>11 ferramentas AI"]
    RAG --> AGENT["LangGraph Agent<br/>examples/langgraph-agent/"]
    NEO --> AGENT
    TTL --> SHACL["Validador SHACL<br/>scripts/validate-shacl.py"]
    SHACL --> AGENT
    AGENT --> MCP
```

---

## Pipeline ETL semantico

O script `scripts/generate.js` executa o pipeline de transformacao completo:

```mermaid
graph LR
    subgraph Extracao["Extracao multi-fonte"]
        S1["GLOSSARIO<br/>(23 termos ANP)"]
        S2["ENTITY_NODES<br/>(170 nos tipados)"]
        S3["EDGES<br/>(259 relacoes)"]
        S4["ONTOLOGY<br/>(ontopetro + SWEET)"]
        S5["Modulos sismicos<br/>P2.8 acquisition/<br/>processing/inversion"]
        S6["Modulos geomecanicos<br/>P2.7 MEM + fraturas"]
        S7["GSO L7<br/>(scripts/gso-extract.js)"]
        S8["WITSML/PRODML<br/>crosswalks RDF"]
    end

    subgraph Harmonizacao["Harmonizacao"]
        H1["Merge + dedup<br/>(data/full.json)"]
        H2["SKOS alignment<br/>(SWEET, OSDU, GSO)"]
        H3["SHACL generation<br/>(22 NodeShapes)"]
        H4["Turtle serializer<br/>(scripts/ttl-serializer.js)"]
    end

    subgraph Carga["Carga"]
        C1["data/ — JSON canonico"]
        C2["api/v1/ — endpoints publicos"]
        C3["ai/ — corpus RAG + prompts"]
        C4["build/neo4j/ — Cypher loader"]
    end

    S1 & S2 & S3 & S4 & S5 & S6 & S7 & S8 --> H1
    H1 --> H2 --> H3 --> H4
    H4 --> C1
    C1 --> C2
    C1 --> C3
    C1 --> C4
```

---

## Consumo downstream

```mermaid
graph TD
    KG["Knowledge Graph"]

    KG --> MCP["MCP Server<br/>(stdio transport)<br/>Claude Desktop / Cursor / Claude Code"]
    KG --> LG["LangGraph Agent<br/>(Router-Decomposer-GraphQuery-RAG-Validator-Synthesizer)"]
    KG --> NB["Notebooks Jupyter<br/>(notebooks/01-04)"]
    KG --> PY["Python Package<br/>geobrain<br/>(Dictionary, KnowledgeGraph, Validator, SweetExpander)"]
    KG --> SHACL["SHACL Validator<br/>(pyshacl)<br/>22 NodeShapes"]
    KG --> T2C["Text2Cypher / Text2SPARQL<br/>(ai/text2cypher-fewshot.jsonl<br/>ai/text2sparql-fewshot.jsonl)"]

    MCP --> CLAUDE["Agentes Claude"]
    LG --> EVAL["Harness de avaliacao<br/>(eval/run.py)"]
    PY --> CLAUDE
```

---

## Fluxo de uma pergunta no agente GraphRAG

Diagrama de sequencia para a pergunta: "Qual o regime contratual do Bloco BS-500 e quais obrigacoes de trabalho minimo se aplicam?"

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Router
    participant D as Decomposer
    participant G as GraphQuery
    participant RAG as RAGRetrieve
    participant V as Validator
    participant S as Synthesizer

    U->>R: pergunta em linguagem natural
    R->>R: classifica (lookup / multi_hop / validation)
    R->>D: classification = multi_hop

    D->>D: decompoe em sub-questoes:<br/>1. Qual o regime do BS-500?<br/>2. Quais UTS se aplicam ao regime?
    D->>G: sub-questoes + contexto

    G->>G: converte para Cypher<br/>MATCH (b:Contractual)-[:governed_by]->(a:ANP)<br/>RETURN b.regimeContratual
    G->>RAG: resultados do grafo + sub-questoes

    RAG->>RAG: BM25 sobre rag-corpus.jsonl<br/>recupera chunks sobre regime contratual,<br/>UTS, PAD, periodo exploratorio
    RAG->>V: contexto grafo + chunks RAG

    V->>V: verifica REGIME_CONTRATUAL_INVALID<br/>verifica SPE_PRMS_INVALID_CATEGORY<br/>verifica ACRONYM_AMBIGUOUS (UTS)
    V->>S: validation={valid:true, violations:[], warnings:[]}

    S->>S: sintetiza resposta final<br/>com fontes e layer coverage
    S->>U: resposta estruturada com<br/>regime contratual + obrigacoes UTS
```

---

## Arquivos-chave

| Componente | Arquivo |
|---|---|
| Grafo de entidades | `data/entity-graph.json` |
| Ontologia formal | `data/ontopetro.json` |
| Mapa de camadas | `ai/ontology-map.json` |
| Pipeline ETL | `scripts/generate.js` |
| Agente LangGraph | `examples/langgraph-agent/agent.py` |
| MCP Server | `mcp/geobrain-mcp/src/index.ts` |
| SHACL shapes | `data/geolytics-shapes.ttl` |
| Vocabulario OWL | `data/geolytics-vocab.ttl` |

Veja tambem: [GRAPHRAG.md](GRAPHRAG.md) — receita completa do agente GraphRAG.

---

## Notas de extensao recentes

**GWML2 WellConstruction (layer1b)**: o modulo `gwml2` adiciona 9 classes para componentes fisicos de pocos (Casing, Screen, Sealing, Filtration, BoreCollar, BoreInterval, WellPump, CasingString, WellConstruction). Arquivo `data/gwml2.json`.

**SOSA/QUDT alignment**: 17 mnemonics de perfis de poco (GR, RHOB, NPHI, DT, UCS, etc.) mapeados a `sosa:Observation` com unidades QUDT em `data/sosa-qudt-alignment.json`. Triples emitidos em `data/geobrain.ttl`.
