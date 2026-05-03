# Modelo de Entidades

O grafo de entidades (`data/entity-graph.json`) contem 221 nos e 370 relacoes tipadas, organizados em 6 tipos de entidade.

---

## Tipos de entidade

| Tipo | Cor visual | Entidades principais |
|---|---|---|
| **operational** | `#378ADD` | Poco, Bloco, Campo, Bacia Sedimentar |
| **contractual** | `#7F77DD` | Contrato E&P, PAD, Rodada de Licitacao, Declaracao de Comercialidade |
| **actor** | `#D85A30` | Operador, ANP, IBAMA, CONAMA, ANA, IBP, BNDES |
| **instrument** | `#888780` | SIGEP, SEP, UTS, Regime Contratual, Periodo Exploratorio, Processo Sancionador, Notificacao Descoberta, Area de Desenvolvimento, EIA, RIMA, AFE, JOA, EPC; **+ 27 sensores 3W** (P-PDG, T-PDG, P-TPT, T-TPT, QGL, ABER-CKGL, ABER-CKP, ESTADO-*, …) |
| **geological** | `#639922` | Pre-sal, Bacias Agrupadas, Ambiente |
| **equipment** | `#C77B30` | BOP, FPSO, ANM, Riser, ROV, DHSV, BHA, ESP/BCS, MWD, LWD, Manifold Submarino; **+ 14 equipamentos Xmas-tree 3W** (PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK, TPT, PDG, SP, ANM) |
| **operational** (subtype=event) | `#378ADD` | **10 eventos operacionais 3W**: Normal, BSW Increase, Spurious DHSV Closure, Severe Slugging, Flow Instability, Rapid Production Loss, Quick PCK Restriction, PCK Scaling, Production Line Hydrate, Service Line Hydrate |

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

## Petrobras 3W v2.0.0 — Subgrafo Operacional de Producao

O modulo 3W (CC-BY 4.0, Vargas et al. 2019, DOI 10.1016/j.petrol.2019.106223) acrescenta 51 entidades ao grafo (TW001–TW051).

### Sensores (27 nos, type=instrument, TW001–TW027)

| ID | Label 3W | Funcao / Quantidade |
|---|---|---|
| `sensor_p_pdg` | P-PDG | Pressao downhole (PDG) — Pa |
| `sensor_t_pdg` | T-PDG | Temperatura downhole (PDG) — °C |
| `sensor_p_tpt` | P-TPT | Pressao no TPT — Pa |
| `sensor_t_tpt` | T-TPT | Temperatura no TPT — °C |
| `sensor_p_anular` | P-ANULAR | Pressao anular — Pa |
| `sensor_p_jus_ckgl` | P-JUS-CKGL | Pressao jusante GLCK — Pa |
| `sensor_p_jus_ckp` | P-JUS-CKP | Pressao jusante PCK — Pa |
| `sensor_p_jus_bs` | P-JUS-BS | Pressao jusante bomba SP — Pa |
| `sensor_p_mon_ckgl` | P-MON-CKGL | Pressao montante GLCK — Pa |
| `sensor_p_mon_ckp` | P-MON-CKP | Pressao montante PCK — Pa |
| `sensor_p_mon_sdv_p` | P-MON-SDV-P | Pressao montante SDV-P — Pa |
| `sensor_p_pt_p` | PT-P | Pressao transducer PWV — Pa |
| `sensor_t_jus_ckp` | T-JUS-CKP | Temperatura jusante PCK — °C |
| `sensor_t_mon_ckp` | T-MON-CKP | Temperatura montante PCK — °C |
| `sensor_qbs` | QBS | Vazao de liquido SP — m³/s |
| `sensor_qgl` | QGL | Vazao de gas lift — m³/s |
| `sensor_aber_ckgl` | ABER-CKGL | Abertura GLCK — % |
| `sensor_aber_ckp` | ABER-CKP | Abertura PCK — % |
| `sensor_estado_dhsv` | ESTADO-DHSV | Estado valvula DHSV — {0, 0.5, 1} |
| `sensor_estado_m1` | ESTADO-M1 | Estado valvula PMV — {0, 0.5, 1} |
| `sensor_estado_m2` | ESTADO-M2 | Estado valvula AMV — {0, 0.5, 1} |
| `sensor_estado_w1` | ESTADO-W1 | Estado valvula PWV — {0, 0.5, 1} |
| `sensor_estado_w2` | ESTADO-W2 | Estado valvula AWV — {0, 0.5, 1} |
| `sensor_estado_pxo` | ESTADO-PXO | Estado valvula PXO — {0, 0.5, 1} |
| `sensor_estado_xo` | ESTADO-XO | Estado valvula XO — {0, 0.5, 1} |
| `sensor_estado_sdv_gl` | ESTADO-SDV-GL | Estado valvula SDV-GL — {0, 0.5, 1} |
| `sensor_estado_sdv_p` | ESTADO-SDV-P | Estado valvula SDV-P — {0, 0.5, 1} |

### Equipamentos Xmas-tree (14 nos, type=equipment, TW028–TW041)

| ID | Sigla | Nome completo | Subtipo |
|---|---|---|---|
| `pmv` | PMV | Production Master Valve (M1) | master_valve |
| `amv` | AMV | Annulus Master Valve (M2) | master_valve |
| `pwv` | PWV | Production Wing Valve (W1) | wing_valve |
| `awv` | AWV | Annulus Wing Valve (W2) | wing_valve |
| `pxo` | PXO | Pig-Crossover Valve | crossover |
| `xo` | XO | Crossover Valve | crossover |
| `sdv_p` | SDV-P | Production Shutdown Valve | shutdown_valve |
| `sdv_gl` | SDV-GL | Gas-Lift Shutdown Valve | shutdown_valve |
| `glck` | GLCK | Gas-Lift Choke | choke |
| `pck` | PCK | Production Choke | choke |
| `tpt` | TPT | Temperature & Pressure Transducer | transducer |
| `pdg` | PDG | Permanent Downhole Gauge | gauge |
| `sp_pump` | SP | Service Pump | pump |
| `anm` | ANM | Subsea Xmas-Tree (assembly) | xmas_tree |

O no `dhsv` (DHSV — Downhole Safety Valve) foi enriquecido in-place com campos 3W: `failure_modes`, `monitored_by`, `osdu_kind`, `threew_equipment_subtype`.

### Eventos Operacionais (10 nos, type=operational/subtype=event, TW042–TW051)

| ID | Label | Codigo 3W | Transiente | Categoria |
|---|---|---|---|---|
| `event_normal` | Normal | 0 | — | normal |
| `event_bsw_increase` | BSW Increase | 1 (transient: 101) | sim | fluid_property_change |
| `event_spurious_dhsv` | Spurious DHSV Closure | 2 (transient: 102) | sim | safety_event |
| `event_severe_slugging` | Severe Slugging | 3 | nao | flow_regime |
| `event_flow_instability` | Flow Instability | 4 | nao | flow_regime |
| `event_rapid_prod_loss` | Rapid Production Loss | 5 (transient: 105) | sim | productivity_event |
| `event_quick_pck_restriction` | Quick PCK Restriction | 6 (transient: 106) | sim | choke_anomaly |
| `event_scaling_pck` | PCK Scaling | 7 (transient: 107) | sim | choke_anomaly |
| `event_hydrate_production` | Production Line Hydrate | 8 (transient: 108) | sim | flow_assurance |
| `event_hydrate_service` | Service Line Hydrate | 9 (transient: 109) | sim | flow_assurance |

Nota: `TRANSIENT_OFFSET=100`. Classes 3 e 4 (Severe Slugging, Flow Instability) nao tem variante transiente.

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
