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

## Regras de deduplicacao entre padroes

- **Petro KGraph e construido sobre GeoCore** — nao sao duplicatas. Use `petrokgraph_uri` como referencia primaria para RAG em portugues.
- **OSDU e schema de dados IT**, nao ontologia filosofica. Complementar a todos os outros. Use `osdu_kind` para interoperabilidade com sistemas Petrobras.
- **Camada ANP e unica** e nao sobrep nenhuma ontologia internacional. Ver `docs/BRAZIL_SPECIFIC.md`.
- **Camada 6 (Petrobras Internal) e o ativo tecnico mais valioso** — namespace `https://petrobras.com.br/geolytics/ontology/`. Apenas definicoes conceituais publicas sao publicadas.

Ver `ai/ontology-map.json` para a documentacao completa de cada camada com URLs OWL, GitHub e regras de uso.

---

## Petrobras 3W v2.0.0

**URL canônica**: https://github.com/petrobras/3W  
**DOI**: 10.1016/j.petrol.2019.106223  
**Licença**: Creative Commons Attribution 4.0 (CC-BY 4.0)  
**Versão absorvida**: 2.0.0 (capturada em 2026-05-03)

### Escopo

O dataset 3W (Three-W) é o primeiro dataset público realista com eventos raros e indesejáveis em poços offshore de petróleo. Contém 1798 instâncias em formato Parquet com 27 variáveis de sensores e 10 classes de eventos operacionais.

O GeoBrain absorve apenas o **schema semântico** — nenhuma instância `.parquet` é incluída.

### Itens absorvidos

| Categoria | Quantidade | Campo `legal_source` |
|---|---|---|
| Variáveis de sensores | 27 nós `type: "instrument"` | `"Petrobras 3W v2.0.0"` |
| Classes de evento | 10 nós `type: "operational"` | `"Petrobras 3W v2.0.0"` |
| Equipamentos Xmas-tree | 13 nós novos + 1 enriquecido (`dhsv`) | `"Petrobras 3W v2.0.0"` |
| Taxonomias | 4 novas em `data/taxonomies.json` | — |
| Dataset registry | 1 entry em `data/datasets.json` | — |

### Mnemônico disciplinar

`TW` (Three-W). Códigos `TW001..TW051` no campo `module`. IDs de entidades: snake_case natural sem prefixo (`event_severe_slugging`, `sensor_p_pdg`, `pck`).

### Namespace RDF

`threew:` → `https://github.com/petrobras/3W#`

### TRANSIENT_OFFSET

Conforme `dataset.ini`: rótulos transientes = rótulo base + 100. Classes 3 (Severe Slugging) e 4 (Flow Instability) não possuem variante transiente.

### Atribuição obrigatória

> Vargas et al. (2019). A realistic and public dataset with rare undesirable real events in oil wells. *Journal of Petroleum Science and Engineering*, 181, 106223.

### Arquivos de proveniência

`data/sources/threew/PROVENANCE.md` — SHA-256 dos arquivos-fonte, data de captura, autores.

### Regras de desambiguação

Três polissemias identificadas: **PCK** (choke 3W vs check valve genérico), **BSW** (propriedade de fluido vs evento classe 1), **state** (status operacional 3W vs `well_state` ANP). Ver `polysemy_cards` em `data/threew.json`.
