# Geolytics Graph Schema — Cypher Reference

Prepend this fragment to the system prompt when generating Cypher queries against the Geolytics Neo4j graph.

---

## Node Labels and Properties

Each node carries the following core properties:

| Property | Type | Description |
|---|---|---|
| `id` | String | Unique slug (e.g. `poco`, `bloco`, `contrato-ep`) |
| `label` | String | Canonical PT-BR label |
| `label_en` | String | Canonical English label |
| `type` | String | Entity category (mirrors the Neo4j label below) |
| `definition` | String | PT-BR definition |
| `legal_source` | String | Regulatory source (e.g. `Lei nº 9478/1997`, `ANP/SEP`) |
| `datasets` | List[String] | ANP/SIGEP dataset slugs |
| `petrokgraph_uri` | String | Petro KGraph OWL URI |
| `osdu_kind` | String | OSDU data kind string |
| `geocoverage` | List[String] | Semantic layers covered (`layer1`–`layer6`) |
| `synonyms_pt` | List[String] | Portuguese synonyms |
| `synonyms_en` | List[String] | English synonyms |
| `examples` | List[String] | Real-world instance examples |

### :Operational

Nodes representing operational petroleum entities.

Instances: `poco`, `bloco`, `campo`, `bacia-sedimentar`, `reservatorio`, `acumulacao`, `play`, `prospecto`, `primeiro-oleo`, `wellbore`, `completacao`, `drilling-activity`, `activity-plan`, `well-activity-program`, `well-activity-phase-type`, `drilling-reason-type`

Key examples:
- `poco` — Well (e.g. `1-RJS-702-RJ`, `3-BRSA-944-RJS`)
- `bloco` — Block (e.g. `BM-S-11`, `BCAM-40`, `BS-4`)
- `campo` — Field (e.g. Búzios, Lula, Atlanta)
- `bacia-sedimentar` — Sedimentary Basin (e.g. Bacia de Campos, Bacia de Santos)

### :Contractual

Nodes representing regulatory and contractual instruments.

Instances: `contrato-ep`, `pad`, `rodada-licitacao`, `declaracao-comercialidade`, `area-desenvolvimento`, `plano-desenvolvimento`, `recurso`, `reserva`, `document-type`, `acl`

Key examples:
- `contrato-ep` — E&P Contract (Concessao or Partilha)
- `pad` — Plano de Avaliacao de Descobertas (NOT a drilling pad)
- `declaracao-comercialidade` — Commerciality Declaration (originates a Campo)
- `reserva` — Reserve (SPE-PRMS 1P/2P/3P — NOT an environmental reserve)

### :Actor

Nodes representing institutional actors.

Instances: `operador`, `anp`, `ibama`, `conama`, `ana-agencia`, `ibp`, `bndes`, `geo-political-entity`

Key examples:
- `anp` — Agencia Nacional do Petroleo (regulator)
- `operador` — Petroleum Operator (e.g. Petrobras, Shell)
- `ibama` — Environmental licensing authority

### :Instrument

Nodes representing regulatory instruments, metrics, and information systems.

Instances: `sigep`, `sep`, `uts`, `regime-contratual`, `periodo-exploratorio`, `processo-sancionador`, `notificacao-descoberta`, `eia`, `rima`, `afe`, `joa`, `epc`, `unidade-medida`, `seismic-acquisition-survey`, `seismic-processing-project`, `wellbore-trajectory`, `log-curve-type`

Key examples:
- `uts` — Unidades de Trabalho (PEM metric — NOT Unidade Territorial)
- `regime-contratual` — Contractual Regime (Concessao or Partilha de Producao)
- `periodo-exploratorio` — Exploratory Period (1st/2nd/3rd PE — NOT generic exploration)
- `sigep` — SIGEP information system (ANP/SEP)

### :Geological

Nodes representing geological concepts.

Instances: `formacao`, `sistema-deposicional`, `presal`, `bacias-agrupadas`, `ambiente`, `rocha-geradora`, `rocha-capacitante`, `trapa`, `sistema-petrolifero`, `falha`, `idade-geologica`, `intervalo-estratigrafico`, `basin-type`, `seismic-horizon`, `wellbore-marker-set`

Key examples:
- `formacao` — Geological Formation (e.g. Formacao Barra Velha — a named lithostratigraphic unit, NOT a lithology type)
- `presal` — Pre-salt layer (geological concept with contractual consequences)
- `trapa` — Trap (structural or stratigraphic)

### :Equipment

Nodes representing physical equipment used in E&P operations.

Instances: `bop`, `fpso`, `anm-eq`, `riser`, `rov`, `dhsv`, `bha`, `esp-eq`, `mwd`, `lwd`, `manifold-submarino`, `casing-design`, `wellbore-architecture`, `mud-pump`, `facility-type`

Key examples:
- `fpso` — Floating Production, Storage and Offloading vessel
- `bop` — Blowout Preventer
- `anm-eq` — Arvore de Natal Molhada (Wet Christmas Tree)
- `dhsv` — Downhole Safety Valve

### :Analytical

Nodes representing analytical data types and geoscience measurements.

Instances: `testemunho`, `perfil-poco`, `materia-organica`, `maturidade-termal`, `biomarcador`, `correlacao-oleo-rocha`, `litologia`, `facies-sedimentar`, `modelo-petrofisico`, `campo-tensional`, `janela-lama`, `ocorrencia-geomec`, `potencial-selante`, `amostra-fluido`, `pvt`, `classe-fluido`, `gc-ms`, `sara`, `topo-formacional`, `trajetoria-poco`, `drilling-parameters`, `core-sample`, `cementing-fluid`, `bottom-hole-pressure-type`, `annular-fluid-type`

Key examples:
- `pvt` — Pressure-Volume-Temperature fluid analysis
- `janela-lama` — Mud Weight Window (geomechanics — NOT the hydrocarbon generation window)
- `campo-tensional` — In-situ Stress Field (Sv, SHmax, Shmin)

### :OntologyClass

Nodes imported from external ontologies (O3PO, GeoCore, BFO). Used in cross-ontology queries.

### :GSOClass

Nodes representing the 213 GSO/Loop3D structural geology classes (Layer 7, CC BY 4.0).

---

## Relationship Types

The graph uses directed typed relationships. Format: `(source_label)-[:RELATION]->(target_label)`.

### Core E&P Chain

| Relationship | Source | Target | Label PT | Notes |
|---|---|---|---|---|
| `drilled_in` | :Operational (poco) | :Operational (bloco) | perfurado em | |
| `delimited_in` | :Operational (bloco) | :Operational (bacia-sedimentar) | delimitado em | |
| `governed_by` | :Operational (bloco) | :Contractual (contrato-ep) | regido por | |
| `defines` | :Contractual (contrato-ep) | :Instrument (regime-contratual) | define | Concessao or Partilha |
| `organized_in` | :Contractual (contrato-ep) | :Instrument (periodo-exploratorio) | organizado em | |
| `measured_via` | :Contractual (contrato-ep) | :Instrument (uts) | mede via | |
| `may_have` | :Operational (bloco) | :Contractual (pad) | pode ter | conditional |
| `may_yield` | :Contractual (pad) | :Contractual (declaracao-comercialidade) | pode gerar | conditional |
| `originates` | :Contractual (declaracao-comercialidade) | :Operational (campo) | origina | |
| `initiates` | :Contractual (declaracao-comercialidade) | :Contractual (area-desenvolvimento) | da inicio a | |
| `ends_with` | :Contractual (area-desenvolvimento) | :Operational (primeiro-oleo) | encerrada pelo | |
| `inaugurates` | :Operational (primeiro-oleo) | :Operational (campo) | inaugura | |
| `originated_in` | :Operational (bloco) | :Contractual (rodada-licitacao) | originado em | |

### Geological Chain

| Relationship | Source | Target | Label PT |
|---|---|---|---|
| `traverses` | :Operational (poco) | :Geological (formacao) | atravessa |
| `hosted_in` | :Operational (reservatorio) | :Geological (formacao) | hospedado em |
| `sustained_by` | :Operational (campo) | :Operational (reservatorio) | sustentado por |
| `contained_in` | :Operational (reservatorio) | :Operational (bacia-sedimentar) | contido em |
| `feeds` | :Geological (rocha-geradora) | :Geological (sistema-petrolifero) | alimenta |
| `forms` | :Geological (falha) | :Geological (trapa) | compoe |
| `comprises` | :Geological (trapa) | :Operational (reservatorio) | comporta |
| `contains` | :Geological (trapa) | :Operational (acumulacao) | contem |
| `becomes` | :Operational (acumulacao) | :Operational (campo) | origina |
| `spawns` | :Operational (play) | :Operational (prospecto) | gera |
| `integrates_to` | :Geological (sistema-petrolifero) | :Operational (bacia-sedimentar) | integra-se a |
| `has_age` | :Geological (formacao) | :Geological (idade-geologica) | tem idade |

### Resource/Reserve Chain

| Relationship | Source | Target | Label PT |
|---|---|---|---|
| `declares` | :Operational (campo) | :Contractual (reserva) | declara |
| `derived_from` | :Contractual (reserva) | :Contractual (recurso) | deriva de |
| `allocated_to` | :Contractual (recurso) | :Operational (bloco) | alocado em |
| `reports` | :Actor (operador) | :Contractual (recurso) | reporta |

### Actor/Regulatory Relations

| Relationship | Source | Target | Label PT |
|---|---|---|---|
| `signed_with` | :Contractual (contrato-ep) | :Actor (anp) | celebrado com |
| `operated_by` | :Operational | :Actor (operador) | operado por |
| `manages_via` | :Actor (anp) | :Instrument (sigep) | gerencia via |
| `oversees_via` | :Actor (anp) | :Instrument (sep) | fiscaliza via |
| `oversees_environment_of` | :Actor (ibama) | :Actor (operador) | fiscaliza ambientalmente |
| `may_have` | :Actor (operador) | :Instrument (processo-sancionador) | pode ter |

### Equipment/Subsea Relations

| Relationship | Source | Target | Label PT |
|---|---|---|---|
| `installed_on` | :Equipment (bop) | :Operational (poco) | instalado em |
| `installed_in` | :Equipment (dhsv) | :Operational (poco) | instalado em |
| `controls` | :Equipment (anm-eq) | :Operational (poco) | controla |
| `produces_at` | :Equipment (fpso) | :Operational (campo) | produz em |
| `connects` | :Equipment (riser) | :Equipment (anm-eq) | conecta |
| `connects` | :Equipment (riser) | :Equipment (fpso) | conecta |
| `gathers_from` | :Equipment (manifold-submarino) | :Operational (poco) | agrega fluxo de |
| `feeds` | :Equipment (manifold-submarino) | :Equipment (fpso) | alimenta |

### Wellbore Chain

| Relationship | Source | Target | Label PT |
|---|---|---|---|
| `has_wellbore` | :Operational (poco) | :Operational (wellbore) | tem wellbore |
| `belongs_to` | :Operational (wellbore) | :Operational (poco) | pertence a |
| `has_completion` | :Operational (wellbore) | :Operational (completacao) | tem completacao |
| `contains` | :Operational (completacao) | :Equipment (dhsv) | contem |
| `penetrates` | :Operational (wellbore) | :Geological (formacao) | penetra |

### Analytical Relations

| Relationship | Source | Target | Label PT |
|---|---|---|---|
| `undergoes` | :Analytical (amostra-fluido) | :Analytical (pvt) | submetida a |
| `undergoes` | :Analytical (amostra-fluido) | :Analytical (sara) | submetida a |
| `classifies` | :Analytical (pvt) | :Analytical (classe-fluido) | classifica |
| `measures` | :Analytical (perfil-poco) | :Operational (poco) | mede |
| `infers` | :Analytical (perfil-poco) | :Analytical (litologia) | infere |
| `detects` | :Analytical (gc-ms) | :Analytical (biomarcador) | detecta |
| `enables` | :Analytical (biomarcador) | :Analytical (correlacao-oleo-rocha) | permite |
| `defines` | :Analytical (campo-tensional) | :Analytical (janela-lama) | define |
| `guides_drilling_of` | :Analytical (janela-lama) | :Operational (poco) | guia perfuracao de |
| `has_property` | :Geological (falha) | :Analytical (potencial-selante) | tem propriedade |

---

## Cardinality Hints

- One `poco` can be `drilled_in` exactly one `bloco`.
- One `bloco` is `delimited_in` exactly one `bacia-sedimentar`.
- One `bloco` is `governed_by` one `contrato-ep`.
- One `contrato-ep` `defines` one `regime-contratual`.
- One `bloco` may have zero or one `pad` (`may_have` is conditional, style=dashed).
- One `pad` may yield zero or one `declaracao-comercialidade` (`may_yield` is conditional).
- One `declaracao-comercialidade` `originates` exactly one `campo`.
- One `campo` `sustained_by` one or more `reservatorio`.
- One `fpso` `produces_at` one `campo`.
- One `poco` `has_wellbore` one or more `wellbore`.

---

## Critical Disambiguations

### PAD != drilling pad
`geo:pad` is the **Plano de Avaliacao de Descobertas** — a contractual instrument (ANP) that evaluates a discovery for commercial viability. It is NOT a physical well pad or drilling location. Always use `pad` when the question is about a discovery evaluation plan.

### UTS != Unidade Territorial
`geo:uts` represents **Unidades de Trabalho** — a metric used in the **Programa Exploratorio Minimo (PEM)** to measure exploration obligations. It is NOT a territorial unit or geographic subdivision.

### Periodo Exploratorio != generic exploration
`geo:periodo-exploratorio` is a specific contractual phase (1st, 2nd, or 3rd PE) with a fixed deadline within an E&P Contract. It is NOT a generic reference to the exploration phase of a project.

### Concessao vs Partilha de Producao
Both are values of `geo:regime-contratual`. In **Concessao** (Lei 9.478/1997), the concessionaire assumes all risks and owns the produced oil. In **Partilha de Producao** (Lei 12.351/2010, pre-salt polygon), the oil is shared between the contractor and the Union, and Petrobras is mandatory operator.

### Reserva vs Reservatorio vs Reserva Ambiental
- `geo:reserva` — Volume classification per **SPE-PRMS** (1P/2P/3P). Commercial reserves. NOT an environmental reserve.
- `geo:reservatorio` — Geological **reservoir rock** (porous/permeable body storing hydrocarbons).
- Reserva Ambiental (REBIO/RPPN) — Environmental conservation unit. This concept is NOT in the graph.

### Campo (polysemy)
- `geo:campo` = ANP production **Field** (e.g. Campo de Buzios, Campo de Lula). Declared via Declaracao de Comercialidade.
- `geo:campo-tensional` = In-situ **Stress Field** (geomechanics). Completely different concept.
- Never confuse these two nodes.

### Formacao vs Litologia
- `geo:formacao` = named **lithostratigraphic unit** (e.g. Formacao Barra Velha, Formacao Macae). A proper noun.
- `geo:litologia` = **petrographic type** inferred from well logs (e.g. calcario microbialítico, arenito). A rock class, not a formation name.

### Janela de Lama vs Janela de Geracao
- `geo:janela-lama` = **Mud Weight Window** — safe drilling fluid density interval (geomechanics, bounded by collapse and fracture pressure).
- Janela de Geracao = hydrocarbon generation window (vitrinite reflectance Ro% range, geochemistry). This is a property of `geo:maturidade-termal`, NOT a separate node.

---

## Translation Example

**Question (PT-BR):** Qual o regime contratual do bloco BCAM-40 e quem o opera?

**Step-by-step reasoning:**
1. Bloco -> contrato-ep (via `governed_by`)
2. contrato-ep -> regime-contratual (via `defines`)
3. bloco -> operador (via `operated_by`)

**Generated Cypher:**
```cypher
MATCH (b:Operational {id: 'bloco'})-[:governed_by]->(c:Contractual {id: 'contrato-ep'})-[:defines]->(rc:Instrument {id: 'regime-contratual'}),
      (b)-[:operated_by]->(op:Actor {id: 'operador'})
WHERE b.examples CONTAINS 'BCAM-40'
RETURN b.label AS bloco, rc.label AS regime, op.label AS operador
```

**Expected columns:** `bloco`, `regime`, `operador`

---

## Neo4j Label Mapping from Entity Type

| `type` value in JSON | Neo4j Label |
|---|---|
| `operational` | `:Operational` |
| `contractual` | `:Contractual` |
| `actor` | `:Actor` |
| `instrument` | `:Instrument` |
| `geological` | `:Geological` |
| `equipment` | `:Equipment` |
| `analytical` | `:Analytical` |

All nodes also carry the generic label `:Entity`.
