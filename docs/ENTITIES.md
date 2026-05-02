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
