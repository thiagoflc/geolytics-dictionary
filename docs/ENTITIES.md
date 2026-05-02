# Modelo de Entidades

O grafo de entidades (`data/entity-graph.json`) contem 75 nos e 80 relacoes tipadas, organizados em 6 tipos de entidade.

---

## Tipos de entidade

| Tipo | Cor visual | Entidades principais |
|---|---|---|
| **operational** | `#378ADD` | Poco, Bloco, Campo, Bacia Sedimentar |
| **contractual** | `#7F77DD` | Contrato E&P, PAD, Rodada de Licitacao, Declaracao de Comercialidade |
| **actor** | `#D85A30` | Operador, ANP, IBAMA, CONAMA, ANA, IBP, BNDES |
| **instrument** | `#888780` | SIGEP, SEP, UTS, Regime Contratual, Periodo Exploratorio, Processo Sancionador, Notificacao Descoberta, Area de Desenvolvimento, EIA, RIMA, AFE, JOA, EPC |
| **geological** | `#639922` | Pre-sal, Bacias Agrupadas, Ambiente |
| **equipment** | `#C77B30` | BOP, FPSO, ANM, Riser, ROV, DHSV, BHA, ESP/BCS, MWD, LWD, Manifold Submarino |

---

## Relacoes tipadas

As relacoes entre entidades sao tipadas e classificadas em `solid` (sempre presente) ou `dashed` (condicional/opcional).

Exemplos de relacoes:

| Relacao | Origem | Destino | Tipo |
|---|---|---|---|
| `drilled_in` | Poco | Bloco | solid |
| `governed_by` | Bloco | Regime Contratual | solid |
| `evaluates` | PAD | Notificacao Descoberta | solid |
| `originates` | Declaracao de Comercialidade | Campo | solid |
| `may_register` | Poco | Notificacao Descoberta | dashed |
| `may_yield` | PAD | Declaracao de Comercialidade | dashed |
| `operates_in` | Operador | Bloco | solid |
| `regulates` | ANP | Bloco | solid |
| `licenses` | ANP | Contrato E&P | solid |
| `auctioned_in` | Bloco | Rodada de Licitacao | solid |

---

## Campos por no

Cada entidade no grafo tem os seguintes campos:

```json
{
  "id": "poco",
  "label": "Poco",
  "label_en": "Well",
  "type": "operational",
  "geocoverage": ["layer2", "layer3", "layer4", "layer5"],
  "petrokgraph_uri": "http://www.petroles.petro.br/ontology/Poco",
  "osdu_kind": "opendes:osdu:master-data--Well:1.0.0",
  "description": "...",
  "outgoing": [...],
  "incoming": [...]
}
```

### geocoverage

O campo `geocoverage` indica em quais camadas semanticas a entidade possui cobertura formal. Valores possiveis: `layer1`, `layer1b`, `layer2`, `layer3`, `layer4`, `layer5`, `layer6`, `layer7`.

Entidades sem `petrokgraph_uri` representam conceitos exclusivamente brasileiros (camada 5 — ANP) que nao existem em ontologias internacionais. Ver `docs/BRAZIL_SPECIFIC.md`.

---

## API REST

As entidades pre-computadas (com relacoes outgoing/incoming resolvidas) estao disponiveis em:

```
api/v1/entities.json         — todos os nos
api/v1/search-index.json     — indice de busca client-side
```

---

## MCP: ferramenta get_entity

```javascript
// Via MCP Server
get_entity({ entity_id: "poco" })
get_entity_neighbors({ entity_id: "bloco", hops: 2, edge_type: "governed_by" })
```

---

## Consultas Cypher de exemplo

Ver `docs/queries/` para 6 consultas comentadas:

| Arquivo | Pergunta |
|---|---|
| `01-poco-bloco-bacia-regime.cypher` | Caminho multi-hop poco → bloco → bacia → regime contratual |
| `02-gso-falha-osdu-crosswalk.cypher` | Classes GSO de falhas com mapeamento OSDU |
| `03-entidades-sem-petrokgraph.cypher` | Entidades sem URI no Petro KGraph (lacunas ontologicas) |
| `04-caminho-mais-curto.cypher` | Menor caminho entre quaisquer dois nos |
| `05-cascata-regulatoria.cypher` | Cascata regulatoria Lei 9.478 → ANP → SIGEP |
| `06-desambiguacao-siglas.cypher` | Siglas com multiplos sentidos no dominio O&G |

---

## Operações Geológicas — Aquisição de Dados Geoquímicos

DRX (Difração de Raios X) e FRX (Fluorescência de Raios X) são analises complementares executadas sobre amostras de calha (cuttings) ao longo da perfuração. Ambas sao geridas por **EXP/OGP/AQG**, armazenadas no **SIGEO** e tem schemas brutos definidos em [data/operacoes-geologicas.json](../data/operacoes-geologicas.json). DRX entrega composicao mineralogica semi-quantitativa; FRX entrega composicao elementar (maiores e traco) — juntas sustentam classificacao litologica, correlacao estratigrafica, decisoes de estabilidade de poco e a construcao do DNA Geoquimico.

### DRX — Difração de Raios X

Análise por difração de raios X em amostras de calha ou testemunho, fornecendo composição mineralógica qualitativa e semi-quantitativa. Insumo crítico para classificação litológica, correlação estratigráfica e decisões de estabilidade de poço (identificação de argilominerais reativos).

**Equipamento e metadados de servico**

| Campo | Valor padrao |
|---|---|
| Prestadora | GEOSERVICES |
| Equipamento | OLYMPUS BTX-III |
| Tipo de tubo | Cobre |
| Temperatura de secagem | 90 °C |
| Metodo de quantificacao | RIR (Reference Intensity Ratio) |

**Mnemonicos minerais (12)**

| Mnemonico | Mineral (PT) | Mineral (EN) | Unidade |
|---|---|---|---|
| QTZ | Quartzo | Quartz | % |
| CAL | Calcita | Calcite | % |
| DOL | Dolomita | Dolomite | % |
| A_M | Argilominerais | Clay Minerals | % |
| AND | Anidrita | Anhydrite | % |
| HAL | Halita | Halite | % |
| PLG | Plagioclasio | Plagioclase | % |
| KFD | K-Feldspato | K-Feldspar | % |
| PIR | Pirita | Pyrite | % |
| PRX | Piroxenio | Pyroxene | % |
| ANF | Anfibolio | Amphibole | % |
| OLI | Olivina | Olivine | % |

> Nota: o mnemonico `A_M` agrega esmectita, ilita, caulinita e clorita. Argilominerais reativos identificados via DRX alimentam decisoes de janela de fluido / estabilidade de poco — relacao `OGR11 supports_decision: DRX → GM005 (MudWindow)` no modulo de geomecanica.

### FRX — Fluorescência de Raios X

Análise por fluorescência de raios X em amostras de calha, fornecendo composição elementar (elementos maiores e traço). Permite classificação litológica via razões elementares, correlação geoquímica entre poços e construção de assinaturas geoquímicas de formações (DNA Geoquímico).

**Equipamento e metadados de servico**

| Campo | Valor padrao |
|---|---|
| Prestadora | GEOSERVICES |
| Equipamento | SPECTRO XEPOS STANDARD |
| Tipo de tubo | Paladio |
| Atmosfera | Vacuo (alternativa: Helio) |
| Tipo de amostra | PRENSADA (alternativa: POEIRA) |

**Elementos maiores (11, em %)**

| Mnemonico | Unidade |
|---|---|
| Na | % |
| Mg | % |
| Al | % |
| Si | % |
| P  | % |
| S  | % |
| K  | % |
| Ca | % |
| Ti | % |
| Mn | % |
| Fe | % |

**Elementos traco (37, em ppm)**

Cl, V, Cr, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Rb, Sr, Y, Zr, Nb, Mo, Ag, Cd, Sn, Sb, Te, I, Cs, Ba, La, Ce, Hf, Ta, W, Hg, Tl, Pb, Bi, Th, U.

**Razoes elementares padronizadas (5)**

| Crossplot | Eixos | Finalidade |
|---|---|---|
| FeBa | Fe x Ba | Discriminacao de formacoes |
| CaK | Ca/K | Indicador carbonato vs siliciclastico |
| RbSr | Rb/Sr | Proxy de intemperismo e proveniencia |
| ZrFe | Zr/Fe | Indicador de aporte detritico |
| PearceNbY | Nb/Y x Zr/Ti | Pearce — classificacao de rochas igneas/vulcanoclasticas |

### Lacunas de evidencia

- Pipeline de ingestao DRX SIGEO/BDIEP → AIDA/Databricks nao documentado.
- Pipeline de ingestao FRX SIGEO → AIDA/Databricks nao documentado.
- Padronizacao de mnemonicos DRX no SIGEO nao documentada na ontologia.
- Padroes de rocha de referencia no modulo SIGEO de QC (FRX) nao documentados na ontologia.
- Integracao DRX e FRX ao pipeline text-to-SQL do GeoDO ausente.
