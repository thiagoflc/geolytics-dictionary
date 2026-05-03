# Indice de documentacao — GeoBrain

Mapa de navegacao para toda a documentacao do projeto.

---

## Documentos principais

| Arquivo | Descricao |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arquitetura do sistema: diagrama das 8 camadas semanticas, pipeline ETL multi-fonte → grafo → consumo downstream, sequencia de uma pergunta atravessando o agente GraphRAG |
| [GRAPHRAG.md](GRAPHRAG.md) | Receita completa do agente LangGraph: topologia do DAG, descricao de cada no, validador como guardrail com exemplo trabalhado, tabela de decisao "quando usar o que" |
| [ONTOLOGY.md](ONTOLOGY.md) | Referencia de classes e propriedades: tabelas geradas automaticamente de `data/ontopetro.json`, `data/geomechanics.json` e modulos sismicos P2.8. Regenerar com `node scripts/build-ontology-doc.js` |
| [USE_CASES.md](USE_CASES.md) | Seis casos de uso concretos com perguntas, caminho no DAG e resposta esperada: regime ANP, WITSML TVD/MD, AVO Classe 4, janela mud weight MEM, disambiguacao SPE-PRMS vs ambiental, crosswalk OSDU |

---

## Modulos tecnicos

| Arquivo | Descricao |
|---|---|
| [GEOMECHANICS.md](GEOMECHANICS.md) | Modulo MEM P2.7: conceito, quatro pilares do MEM 1D, mapeamento JSON, diagrama Mermaid, Circulo de Mohr, SHACL shapes, crosswalk fraturas-GSO. **Inclui modulo L6 Corporate Petrobras** (47 entidades GEOMEC*, crosswalk L2↔L6, SHACL shapes 23-30, integracao com Validator do LangGraph). |
| [SEISMIC.md](SEISMIC.md) | Modulo sismico P2.8: aquisicao, processamento, inversao e atributos. Diagrama Mermaid, mapeamento OSDU, classes AVO |
| [SHACL.md](SHACL.md) | Documentacao do sistema SHACL: 65 NodeShapes, como validar, como adicionar novas shapes |
| [SWEET.md](SWEET.md) | Alinhamento SWEET (NASA/ESIPFed): 66 alinhamentos SKOS, expansao semantica via `sweet-expand.js`, uso em agentes |
| [WITSML.md](WITSML.md) | Mapeamento WITSML/PRODML → RDF: argumento linear→grafo, schema do crosswalk, exemplos SPARQL/Cypher |

---

## Referencia de dados e dominio

| Arquivo | Descricao |
|---|---|
| [ENTITIES.md](ENTITIES.md) | Modelo de entidades: 6 tipos, relacoes tipadas, campos por no, API e MCP tools, queries Cypher de exemplo |
| [ENTITIES.md#operações-geológicas--aquisição-de-dados-geoquímicos](ENTITIES.md#operações-geológicas--aquisição-de-dados-geoquímicos) | Operacoes Geologicas DRX/FRX: mnemonicos minerais, elementos maiores/traco e razoes elementares Petrobras EXP/OGP/AQG |
| [ACRONYMS.md](ACRONYMS.md) | Siglario O&G: 1.102 siglas categorizadas, estrutura JSON, siglas com multiplos sentidos, filtragem RAG |
| [BRAZIL_SPECIFIC.md](BRAZIL_SPECIFIC.md) | Os 11 conceitos exclusivamente brasileiros (camada 5 — ANP): Bloco, PAD, Contrato E&P, Rodada de Licitacao, UTS, Regime Contratual, Periodos Exploratorios, Processo Sancionador, Notificacao de Descoberta, Declaracao de Comercialidade |
| [CGI.md](CGI.md) | CGI vocabularies (Layer 1b — GeoSciML): 7 vocabulary files, JSON schema, cross-links via geosciml_uri, OSDU crosswalk, Python/API/MCP usage, reference Cypher queries 07 and 08 |
| [GWML2.md](GWML2.md) | GWML2 WellConstruction (9 classes) e propriedades gsmlbh do poço (boreholeDiameter, dateOfDrilling, drillingMethod, inclinationType) |
| [EXTERNAL_STANDARDS.md](EXTERNAL_STANDARDS.md) | Padroes externos: Petro KGraph (PUC-Rio), PPDM, SPE-PRMS (hierarquia de reservas), OSDU (crosswalks e formato osdu_kind) |

---

## Consultas de exemplo

O diretorio `queries/` contem 10 consultas Cypher comentadas em PT-BR:

| Arquivo | Pergunta |
|---|---|
| [queries/01-poco-bloco-bacia-regime.cypher](queries/01-poco-bloco-bacia-regime.cypher) | Caminho multi-hop poco → bloco → bacia → regime contratual |
| [queries/02-gso-falha-osdu-crosswalk.cypher](queries/02-gso-falha-osdu-crosswalk.cypher) | Classes GSO de falhas com mapeamento OSDU |
| [queries/03-entidades-sem-petrokgraph.cypher](queries/03-entidades-sem-petrokgraph.cypher) | Entidades sem URI no Petro KGraph |
| [queries/04-caminho-mais-curto.cypher](queries/04-caminho-mais-curto.cypher) | Menor caminho entre quaisquer dois nos |
| [queries/05-cascata-regulatoria.cypher](queries/05-cascata-regulatoria.cypher) | Cascata regulatoria Lei 9.478 → ANP → SIGEP |
| [queries/06-desambiguacao-siglas.cypher](queries/06-desambiguacao-siglas.cypher) | Siglas com multiplos sentidos |
| [queries/07-litologia-cgi-osdu-crosswalk.cypher](queries/07-litologia-cgi-osdu-crosswalk.cypher) | Litologias CGI com mapeamento OSDU LithologyType (crosswalk bilateral) |
| [queries/08-escala-tempo-geologico-presal.cypher](queries/08-escala-tempo-geologico-presal.cypher) | Escala de tempo geológico e períodos com notas sobre Pré-sal brasileiro |
| [queries/09-componentes-poco-gwml2.cypher](queries/09-componentes-poco-gwml2.cypher) | Componentes de construção de poço (GWML2 WellConstruction) |
| [queries/10-sosa-observacoes-perfis.cypher](queries/10-sosa-observacoes-perfis.cypher) | Observações SOSA/SSN mapeadas a perfis de poço e mnemonicos QUDT |

---

## Guias de inicio rapido

- **Carregar o dicionario em Python**: ver raiz `README.md` → secao "Como usar os dados"
- **Instalar o pacote Python**: `pip install geobrain` — ver `python/README.md`
- **Subir o grafo em Neo4j**: `node scripts/build-neo4j.js && docker compose up`
- **Instalar o MCP Server**: ver `mcp/geobrain-mcp/README.md`
- **Rodar o agente LangGraph**: `cd examples/langgraph-agent && python run_demo.py`
- **Validar com SHACL**: `pip install pyshacl && python scripts/validate-shacl.py`
- **Regenerar todos os dados**: `node scripts/generate.js`
- **Regenerar referencia de ontologia**: `node scripts/build-ontology-doc.js`
