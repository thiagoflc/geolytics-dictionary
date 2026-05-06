# Glossary

Glossário interno usado nesta Wiki e na documentação. Para o **glossário de domínio** (termos ANP completos), veja [`data/glossary.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/glossary.json) ou [docs/INDEX.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/docs/INDEX.md).

---

## Conceitos GeoBrain

### **Camada (Layer, L1..L7)**
Unidade de organização do conhecimento. As 8 camadas do GeoBrain (L1, L1b, L2-L7) representam públicos e perspectivas distintas. Detalhes em [[Semantic Layers]].

### **Cross-URI**
Identificador equivalente em outra camada. Ex.: `petrokgraph_uri`, `osdu_kind`, `geosciml_uri`, `bfo_iri`, `gso_uri`. Aparece como atributo em entidades do grafo.

### **Crosswalk**
Mapeamento bilateral entre conceitos de duas camadas. Ex.: [`data/cgi-osdu-lithology-map.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/cgi-osdu-lithology-map.json) é um crosswalk CGI ↔ OSDU.

### **Determinismo**
Propriedade onde a mesma entrada produz exatamente a mesma saída. ETL e Validator são determinísticos. Synthesizer (LLM) **não** é.

### **Entity Graph**
O grafo principal do projeto: 221 nós tipados + 370 relações. Vive em [`data/entity-graph.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/entity-graph.json).

### **`geocoverage`**
Atributo presente em todo termo/entidade. Lista de camadas onde o conceito existe formalmente. Ex.: `["L4", "L5"]`.

### **Guardrail**
Validação determinística que envolve a saída do LLM antes de chegar ao usuário. No GeoBrain, o Semantic Validator e SHACL atuam como guardrails.

### **Knowledge Graph (KG)**
Sinônimo de Entity Graph neste projeto. Veja [[Knowledge Graph]].

### **NodeShape (SHACL)**
Restrição em RDF que define o que uma instância de uma classe deve ter (propriedades obrigatórias, tipos, cardinalidades). Veja [[SHACL Validation]].

### **RAG Corpus**
Conjunto de chunks textuais (~2.683) pré-processados para alimentar buscas BM25 ou embeddings densos. Vive em [`ai/rag-corpus.jsonl`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/ai/rag-corpus.jsonl). Veja [[RAG Corpus]].

### **Semantic Validator**
Validador determinístico (sem LLM) que checa claims em texto contra regras de domínio (SPE-PRMS, regime contratual, etc.). Veja [[Semantic Validator]].

### **SKOS**
Simple Knowledge Organization System. Padrão W3C para alinhamentos entre vocabulários (`exactMatch`, `closeMatch`, `relatedMatch`). Usado nos crosswalks.

### **TTL / Turtle**
Formato de serialização RDF (`.ttl`). Usado em [`data/geolytics.ttl`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/geolytics.ttl) e nas SHACL shapes.

---

## Domínio O&G

> Definições enxutas. Para detalhes completos, consulte o glossário canônico em `data/glossary.json` (descrições com referência normativa).

### **ANP**
Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (Brasil). Regulador setorial criado pela Lei 9.478/1997.

### **AVO**
Amplitude Variation with Offset. Análise sísmica que correlaciona amplitude refletida com offset fonte-receptor. Classes I-IV (não 4P, 5P!) — ver [[Semantic Validator]].

### **Bacia Sedimentar**
Depressão geológica com sedimentos acumulados. Catálogo oficial ANP em [`data/anp-bacia-sedimentar.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/anp-bacia-sedimentar.json).

### **BFO**
Basic Formal Ontology. Ontologia de alto nível usada como camada L1 (raiz formal).

### **BHA**
Bottom-Hole Assembly. Conjunto de equipamentos no fundo do poço durante perfuração.

### **BOP**
1) Blowout Preventer (equipamento de segurança) — L4
2) Bandeira de Operação Padrão (Petrobras) — L6

### **Bloco**
Unidade administrativa de exploração ANP, instituída pela Lei 9.478/1997. Conceito brasileiro sem equivalente OSDU direto.

### **Cessão Onerosa**
Regime contratual brasileiro instituído pela Lei 12.276/2010, com volume máximo de 5 bilhões de boe. Um dos três regimes válidos no Brasil.

### **CGI**
Commission for the Management and Application of Geoscience Information (IUGS). Mantém vocabulários internacionais (Simple Lithology, Geologic Time, Fault Type, etc.). Camada L1b.

### **Concessão**
Regime contratual brasileiro tradicional (Lei 9.478/1997). Operador assume risco e direito sobre produção, paga royalties + participações ANP.

### **CGS**
Common Gas Standard. Termo técnico de operação.

### **Contrato E&P**
Instrumento contratual entre ANP e operador. Tipos: Concessão, Partilha, Cessão Onerosa.

### **GSO**
Geological Structures Ontology. Mantida pelo ARDC / GeoScience Australia. Camada L7 (213 classes estruturais).

### **GeoSciML**
Geoscience Markup Language. Padrão ISO/CGI para descrição de dados geocientíficos. Camada L1b.

### **MEM**
Mechanical Earth Model. Modelo geomecânico do subsolo (pore pressure, stress, fracture gradient). MEM 1D = perfil vertical num poço.

### **MD / TVD**
Measured Depth / True Vertical Depth. Em poços direcionais, MD ≥ TVD. Mapeados a `geo:depth_MD` e `geo:depth_TVD` em WITSML crosswalk.

### **OSDU**
Open Subsurface Data Universe. Padrão The Open Group para schema de dados subsuperficiais. Camada L4.

### **PAD**
1) Plano de Avaliação de Descoberta (instrumento contratual ANP) — L5
2) Drilling Pad (plataforma física) — L4
3) Pulsed Amplitude Detector — L4

> Sigla com 3+ sentidos. Validator dispara `ACRONYM_AMBIGUOUS` se sem contexto.

### **Partilha de Produção**
Regime contratual brasileiro instituído pela Lei 12.351/2010 para áreas estratégicas (Pré-sal). Operador divide produção com União após cost recovery.

### **PE-1, PE-2, PE-3**
Períodos Exploratórios definidos no contrato ANP (fases temporais com obrigações). Ordem: PE-1 → PE-2 → PE-3.

### **Petro KGraph**
Knowledge Graph de E&P em PT-BR mantido pela PUC-Rio (PetroNLP). Camada L3 (539 conceitos).

### **Pré-sal**
Província petrolífera offshore brasileira (Bacia de Santos + Campos), abaixo da camada de sal. Reservatórios carbonáticos do Aptiano.

### **PRODML**
Production Markup Language. Padrão Energistics para dados de produção. 15 classes mapeadas em [`data/prodml-rdf-crosswalk.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/prodml-rdf-crosswalk.json).

### **Reserva (SPE-PRMS)**
Categoria de hidrocarbonetos com critérios de probabilidade:
- **1P** = Proved (≥90%)
- **2P** = Proved + Probable (≥50%)
- **3P** = Proved + Probable + Possible (≥10%)
- **C1C/C2C/C3C** = Contingent (sub-comercial)

> "4P" e superiores **não existem**. Validator captura.

### **Reserva (ambiental)**
Unidade de Conservação SNUC. Tipos:
- **REBIO** — Reserva Biológica
- **RPPN** — Reserva Particular do Patrimônio Natural
- **APA** — Área de Proteção Ambiental
- **REC** — Refúgio Ecológico

> Validator dispara `RESERVA_AMBIGUITY` quando há mistura de contextos.

### **Rodada de Licitação**
Leilão público ANP de áreas de E&P. Brasil teve R1 (1999) a R17 (2024).

### **SIGEP**
Sistema de Gestão de Exploração e Produção. Sistema interno ANP.

### **SOSA**
Sensor, Observation, Sample, and Actuator. Padrão W3C para descrever observações sensoriais. 17 mnemônicos de logs alinhados em [`data/sosa-qudt-alignment.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/sosa-qudt-alignment.json).

### **SWEET**
Semantic Web for Earth and Environmental Technology. Ontologia NASA/ESIPFed. 66 alinhamentos SKOS no GeoBrain.

### **Trabalho Mínimo (UTS)**
Unidade de Trabalho Sísmico. Métrica contratual ANP que define obrigação mínima de aquisição/processamento sísmico no contrato E&P.

### **WITSML**
Wellsite Information Transfer Standard Markup Language. Padrão Energistics para dados de poço. 25 classes WITSML 2.0 mapeadas em [`data/witsml-rdf-crosswalk.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/witsml-rdf-crosswalk.json).

### **Xmas-tree (Árvore de Natal Molhada)**
Conjunto de válvulas instalado na cabeça do poço submarino. 14 equipamentos modelados via Petrobras 3W v2.0.0.

### **3W (Petrobras)**
Dataset Petrobras de eventos críticos em poços (CC-BY 4.0). 27 sensores, 10 tipos de evento (kick, loss, twist-off…). Camada L6.

---

## Engenharia / Build

### **CI gate**
Workflow de CI que bloqueia o PR se condição não for satisfeita. Ex.: `validate.yml` bloqueia se `git diff` não-vazio após regenerar.

### **Idempotência**
Propriedade onde rodar uma operação múltiplas vezes produz o mesmo resultado da primeira. ETL e Neo4j loaders são idempotentes (uso de MERGE em vez de CREATE).

### **JSON canônico**
Versão dev-friendly de um dado, em `data/`. Serve de fonte para gerar TTL, JSON otimizado para API, e RAG corpus.

### **MCP**
Model Context Protocol. Spec da Anthropic para servers de ferramentas conectados a Claude/clientes compatíveis.

### **NodeShape**
Termo técnico SHACL. Veja entrada acima.

### **Single source of truth**
Cada informação tem **uma e apenas uma** fonte autoritativa. Em GeoBrain: constantes em `scripts/*.js`. Tudo em `data/` é gerado.

---

## Acrônimos do projeto

| Sigla   | Significado                                        |
| ------- | -------------------------------------------------- |
| ETL     | Extract, Transform, Load                            |
| KG      | Knowledge Graph                                     |
| MCP     | Model Context Protocol                              |
| OWL     | Web Ontology Language                               |
| PR      | Pull Request                                        |
| RAG     | Retrieval-Augmented Generation                      |
| RDF     | Resource Description Framework                      |
| SDK     | Software Development Kit                            |
| SHACL   | Shapes Constraint Language                          |
| SKOS    | Simple Knowledge Organization System                 |
| SPARQL  | SPARQL Protocol and RDF Query Language              |
| SVG     | Scalable Vector Graphics                            |
| TTL     | Turtle (RDF serialization)                           |
| URI     | Uniform Resource Identifier                          |

---

> **Voltar:** [[Home]] · **Próximo:** [[FAQ]]
