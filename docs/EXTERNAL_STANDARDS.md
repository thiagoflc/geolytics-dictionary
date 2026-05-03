# Padroes externos — Petro KGraph, PPDM, SPE-PRMS, OSDU

Documentacao dos padroes externos referenciados pelo GeoBrain, com indicacoes de como cada um e usado e onde encontrar os mapeamentos.

---

## Petro KGraph

**Petro KGraph** e uma ontologia formal de Oleo & Gas em portugues desenvolvida pela **PUC-Rio / PetroNLP** com 539 conceitos formais populados com instancias ANP publicas e relacoes extraidas de documentos tecnicos por NLP.

**Caracteristicas**:
- Construido sobre GeoCore (UFRGS/BDI) — nao sao duplicatas
- Cobre o dominio de E&P em portugues com foco no contexto brasileiro
- Inclui corpora anotados: PetroGold (NER), PetroNER, PetroRE (extracao de relacoes)
- E a camada mais adequada para RAG em portugues

**No Geolytics**: o campo `petrokgraph_uri` em cada entidade aponta para o URI correspondente no Petro KGraph. Entidades sem esse campo representam conceitos exclusivamente brasileiros (camada 5) que nao existem no Petro KGraph.

**Repositorio**: https://github.com/Petroles/PetroNLP

**Uso no agente**: o MCP tool `crosswalk_lookup` e o GraphQuery usam `petrokgraph_uri` como referencia primaria para resolucao de entidades em portugues.

---

## PPDM

**PPDM (Professional Petroleum Data Management Association)** e o padrao internacional classico de modelagem de dados de E&P, originado na Society of Petroleum Engineers nos anos 1990.

Define entidades canonicas:

| Entidade PPDM | Equivalente Geolytics | Observacao |
|---|---|---|
| Well | geo:Poco | geocoverage layer2, layer4, layer5 |
| Wellbore | geo:Poco (sub-entidade) | distinção Poco/Poco_Filho depende do contexto |
| Field | geo:Campo | |
| Reservoir | geo:Reservatorio | |
| Trap | geo:Armadilha | |
| Play | sem equivalente direto | conceito exploratório probabilístico |
| Prospect | sem equivalente direto | area prospectiva pre-descoberta |
| Resource | geo:Recurso | |
| Reserve | geo:Reserva | restrito ao contexto SPE-PRMS (nao ambiental) |

**No Geolytics**: a coluna `sources` em cada classe da `data/ontopetro.json` identifica quais classes derivam de PPDM. Classes C001-C020 usam PPDM como uma das fontes principais (junto com GeoCore).

---

## SPE-PRMS

**SPE-PRMS (Society of Petroleum Engineers — Petroleum Resources Management System)** e o sistema canonico de classificacao de recursos e reservas de hidrocarbonetos, adotado globalmente (incluindo pela ANP para relatorios de reservas).

### Hierarquia SPE-PRMS

```
Hidrocarbonetos In Situ
  Recursos Prospectivos (nao descobertos)
  Recursos Contingentes (descobertos, nao comercializaveis)
    C1C — Desenvolvimento Contemplado (maior certeza)
    C2C — Desenvolvimento em Espera
    C3C — Desenvolvimento Improvavel (menor certeza)
  Reservas (descobertos, comercializaveis)
    1P — Provadas
    2P — Prováveis (1P + probabilidade media)
    3P — Possíveis (2P + possíveis)
```

### Erro mais comum

A categoria "4P" **nao existe** no SPE-PRMS. E o erro mais frequente detectado pelo validador semantico (`SPE_PRMS_INVALID_CATEGORY`). Origina-se de confusao com analogias como "the 4 Ps of marketing" ou de leitura descuidada de relatorios.

### Disambiguacao critica

"Reserva" no contexto SPE-PRMS (volume de hidrocarbonetos) **nao tem nenhuma relacao** com "Reserva Ambiental" (REBIO, RPPN, APA — areas de protecao ambiental reguladas pelo SNUC, Lei 9.985/2000). O validador emite `RESERVA_AMBIENTAL_CONFUSION` quando detecta essa mistura.

**No Geolytics**: a taxonomia SPE-PRMS esta modelada em `data/taxonomies.json` com alerta RAG explicito. A SHACL shape `geo:ReservaShape` valida que `categoriaSPEPRMS` deve ser um dos 6 valores canonicos.

---

## OSDU

**OSDU — Open Subsurface Data Universe** e o padrao global de dados de subsuperficie da industria petrolífera, mantido pelo The Open Group. Petrobras e membro ativo do OSDU Forum.

**Caracteristicas**:
- Nao e ontologia formal — e schema de dados para interoperabilidade IT
- Licenca Apache 2.0
- Cobre schemas para Well, Wellbore, Field, Basin, SeismicAcquisition, Trajectory, WellLog
- Os campos `osdu_kind` no dicionario usam o formato `opendes:osdu:master-data--[Type]:1.0.0`

### Crosswalks disponíveis

| Arquivo | Conteudo |
|---|---|
| `data/witsml-rdf-crosswalk.json` | 25 classes WITSML 2.0 mapeadas para `geo:` + OSDU kind + GeoCore alignment |
| `data/prodml-rdf-crosswalk.json` | 15 classes PRODML 2.x mapeadas para `geo:` — inclui DTS, DAS, FiberOpticPath |
| `data/osdu-gso-crosswalk.json` | 14 mapeamentos SKOS OSDU↔GSO (Layer 7) |
| `data/osdu-mapping.json` | Mapeamento geral OSDU kinds para entidades do grafo |

### Formato osdu_kind

```
opendes:osdu:master-data--[TypeName]:[major].[minor].[patch]
```

Exemplos:
- `opendes:osdu:master-data--Well:1.0.0`
- `opendes:osdu:master-data--SeismicAcquisitionSurvey:1.0.0`
- `opendes:osdu:master-data--Field:1.0.0`

O validador semantico emite `OSDU_KIND_FORMAT` quando um `osdu_kind` nao segue este padrao. A SHACL shape `geo:OsduKindShape` valida o formato via regex.

### Diferenca OSDU vs ontologia formal

OSDU define schemas de dados (como os campos de um registro JSON devem ser estruturados). Uma ontologia formal (GeoCore, Petro KGraph) define o significado dos conceitos, suas relacoes logicas e restrições axiomaticas. Os dois sao complementares — OSDU para interoperabilidade IT, ontologia para raciocinio semantico.

---

## GeoSciML e CGI Simple Lithology (layer1b)

**GeoSciML** é o padrão OGC para intercâmbio de dados geociêntificos. **CGI Simple Lithology** é um vocabulário OWL/SKOS do IUGS/CGI com 437 conceitos litológicos.

**Módulos GeoSciML usados**:
- `gsmlb` — geologia básica (GeologicUnit, Contact, Fold, Foliation, ShearDisplacementStructure)
- `gsmlbh` — sondagens/poços (Borehole, boreholeDiameter, dateOfDrilling, inclinationType)
- `gwml2` — construção de poços (9 classes: Casing, Screen, Sealing, Filtration, BoreCollar...)
- `CGI Simple Lithology` — 437 conceitos com tradução PT-BR e mapeamento OSDU LithologyType

**No Geolytics**: campo `geosciml_uri` em 50+ nós do entity-graph. Arquivo `data/cgi-lithology.json` com 437 conceitos; `data/cgi-osdu-lithology-map.json` com 152 mapeamentos CGI↔OSDU.

**Referências**:
- http://geosciml.org/
- http://resource.geosciml.org/classifier/cgi/lithology/

---

## GWML2 — GroundWaterML2

**GWML2** é o padrão OGC para modelagem de dados de poços/aquíferos. O módulo WellConstruction define 9 classes para componentes físicos de poços.

**Classes no Geolytics** (`data/gwml2.json`): WellConstruction, CasingComponent, Screen, SealingComponent, FiltrationComponent, BoreCollar, BoreInterval, WellPump, CasingString.

**Módulo**: M-WellIntegrity. **Referência**: http://www.opengis.net/gwml-well/2.2/

---

## W3C SOSA/SSN e QUDT

**SOSA** (Sensor, Observation, Sample, Actuator) e **SSN** (Semantic Sensor Network) são ontologias W3C para modelagem de observações e sensores.

**No Geolytics** (`data/sosa-qudt-alignment.json`): 17 mnemonics de perfis de poço (GR, RHOB, NPHI, DT, UCS, etc.) mapeados a `sosa:Observation` + unidades QUDT. 7 entidades do entity-graph alinhadas a `sosa:FeatureOfInterest`, `sosa:Sampling`, `ssn:Sample`.

**Triples emitidos** em `data/geobrain.ttl`: `geo:WellLog rdfs:subClassOf sosa:ObservationCollection`, `geo:poco rdfs:subClassOf sosa:FeatureOfInterest`, etc.

**Referências**: https://www.w3.org/TR/vocab-ssn/ | https://qudt.org/

---

## Regras de deduplicacao entre padroes

- **Petro KGraph e construido sobre GeoCore** — nao sao duplicatas. Use `petrokgraph_uri` como referencia primaria para RAG em portugues.
- **OSDU e schema de dados IT**, nao ontologia filosofica. Complementar a todos os outros. Use `osdu_kind` para interoperabilidade com sistemas Petrobras.
- **Camada ANP e unica** e nao sobrep nenhuma ontologia internacional. Ver `docs/BRAZIL_SPECIFIC.md`.
- **Camada 6 (Petrobras Internal) e o ativo tecnico mais valioso** — namespace `https://petrobras.com.br/geolytics/ontology/`. Apenas definicoes conceituais publicas sao publicadas.

Ver `ai/ontology-map.json` para a documentacao completa de cada camada com URLs OWL, GitHub e regras de uso.
