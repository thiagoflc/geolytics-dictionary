# Geolytics Graph Schema — SPARQL Reference

Prepend this fragment to the system prompt when generating SPARQL queries against `data/geolytics.ttl`.

---

## Namespace Prefixes

```sparql
PREFIX geo:  <https://geolytics.petrobras.com.br/dict/>
PREFIX osdu: <https://w3id.org/osdu#>
PREFIX kg:   <https://raw.githubusercontent.com/Petroles/PetroNLP/main/Petro%20KGraph%20public.owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
```

Always declare these prefixes at the top of every SPARQL query.

---

## OWL Classes (geo: namespace)

All entity classes are declared as `owl:Class` instances in the `geo:` namespace. They carry `skos:` vocabulary annotations and `geo:entityType` / `geo:geocoverage` data properties.

### Operational entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:poco` | Poco | Well |
| `geo:bloco` | Bloco | Block |
| `geo:campo` | Campo | Field |
| `geo:bacia-sedimentar` | Bacia Sedimentar | Sedimentary Basin |
| `geo:reservatorio` | Reservatorio | Reservoir |
| `geo:acumulacao` | Acumulacao | Accumulation |
| `geo:play` | Play | Play |
| `geo:prospecto` | Prospecto | Prospect |
| `geo:primeiro-oleo` | Primeiro Oleo | First Oil |
| `geo:wellbore` | Wellbore | Wellbore |
| `geo:completacao` | Completacao | Completion |
| `geo:drilling-activity` | Atividade de Perfuracao | Drilling Activity |

### Contractual entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:contrato-ep` | Contrato E&P | E&P Contract |
| `geo:pad` | PAD | Discovery Evaluation Plan |
| `geo:rodada-licitacao` | Rodada de Licitacao | Bidding Round |
| `geo:declaracao-comercialidade` | Declaracao de Comercialidade | Commerciality Declaration |
| `geo:area-desenvolvimento` | Area de Desenvolvimento | Development Area |
| `geo:plano-desenvolvimento` | Plano de Desenvolvimento | Development Plan |
| `geo:recurso` | Recurso | Resource |
| `geo:reserva` | Reserva | Reserve |

### Actor entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:operador` | Operador | Operator |
| `geo:anp` | ANP | ANP |
| `geo:ibama` | IBAMA | IBAMA |
| `geo:conama` | CONAMA | CONAMA |
| `geo:ana-agencia` | ANA | ANA |
| `geo:ibp` | IBP | IBP |
| `geo:bndes` | BNDES | BNDES |

### Instrument entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:sigep` | SIGEP | SIGEP |
| `geo:sep` | SEP | SEP |
| `geo:uts` | UTS | Work Units |
| `geo:regime-contratual` | Regime Contratual | Contractual Regime |
| `geo:periodo-exploratorio` | Periodo Exploratorio | Exploratory Period |
| `geo:processo-sancionador` | Processo Sancionador | Enforcement Process |
| `geo:notificacao-descoberta` | Notificacao de Descoberta | Discovery Notification |
| `geo:eia` | EIA | EIA |
| `geo:rima` | RIMA | RIMA |
| `geo:afe` | AFE | AFE |
| `geo:joa` | JOA | JOA |

### Geological entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:formacao` | Formacao | Geological Formation |
| `geo:sistema-deposicional` | Sistema Deposicional | Depositional System |
| `geo:presal` | Pre-sal | Pre-salt |
| `geo:bacias-agrupadas` | Bacias Agrupadas | Basin Groups |
| `geo:ambiente` | Ambiente | Operational Environment |
| `geo:rocha-geradora` | Rocha Geradora | Source Rock |
| `geo:rocha-capacitante` | Rocha Capacitante | Seal Rock |
| `geo:trapa` | Trapa | Trap |
| `geo:sistema-petrolifero` | Sistema Petrolifero | Petroleum System |
| `geo:falha` | Falha | Fault |
| `geo:idade-geologica` | Idade Geologica | Geological Age |
| `geo:intervalo-estratigrafico` | Intervalo Estratigrafico | Stratigraphic Interval |

### Equipment entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:bop` | BOP | Blowout Preventer |
| `geo:fpso` | FPSO | FPSO |
| `geo:anm-eq` | ANM | Wet Christmas Tree |
| `geo:riser` | Riser | Riser |
| `geo:rov` | ROV | ROV |
| `geo:dhsv` | DHSV | Downhole Safety Valve |
| `geo:bha` | BHA | Bottom Hole Assembly |
| `geo:esp-eq` | ESP/BCS | Electric Submersible Pump |
| `geo:mwd` | MWD | Measurement While Drilling |
| `geo:lwd` | LWD | Logging While Drilling |
| `geo:manifold-submarino` | Manifold Submarino | Subsea Manifold |

### Analytical entities

| URI | prefLabel@pt | prefLabel@en |
|---|---|---|
| `geo:testemunho` | Testemunho | Core |
| `geo:perfil-poco` | Perfil de Poco | Well Log |
| `geo:materia-organica` | Materia Organica | Organic Matter |
| `geo:maturidade-termal` | Maturidade Termal | Thermal Maturity |
| `geo:biomarcador` | Biomarcador | Biomarker |
| `geo:correlacao-oleo-rocha` | Correlacao Oleo-Rocha | Oil-Source Correlation |
| `geo:litologia` | Litologia | Lithology |
| `geo:facies-sedimentar` | Facies Sedimentar | Sedimentary Facies |
| `geo:modelo-petrofisico` | Modelo Petrofisico | Petrophysical Model |
| `geo:campo-tensional` | Campo Tensional | Stress Field |
| `geo:janela-lama` | Janela de Lama | Mud Weight Window |
| `geo:amostra-fluido` | Amostra de Fluido | Fluid Sample |
| `geo:pvt` | PVT | PVT Analysis |
| `geo:classe-fluido` | Classe de Fluido | Fluid Class |
| `geo:gc-ms` | GC-MS | GC-MS |
| `geo:sara` | SARA | SARA |

---

## Data Properties

### SKOS annotation properties (on owl:Class instances)

| Property | Usage |
|---|---|
| `skos:prefLabel` | Preferred label. Always has `@pt` and `@en` language tags. |
| `skos:altLabel` | Alternative labels / synonyms. Language-tagged. |
| `skos:definition` | Definition text. Language-tagged (`@pt` and/or `@en`). |
| `skos:example` | Real-world example string (no language tag). |

### geo: custom data properties

| Property | Range | Description |
|---|---|---|
| `geo:entityType` | xsd:string | Entity category: `operational`, `contractual`, `actor`, `instrument`, `geological`, `equipment`, `analytical` |
| `geo:geocoverage` | xsd:string | Semantic layer slug: `layer1` through `layer6`. Multi-valued. |

---

## Object Properties (geo: namespace)

All relationships are declared as `owl:ObjectProperty` with `rdfs:domain`, `rdfs:range`, `rdfs:label@pt`, and `rdfs:label@en`. They also appear as RDF triples at the schema level (e.g. `geo:poco geo:drilled_in geo:bloco .`).

### Core E&P chain properties

| Property URI | rdfs:label@pt | rdfs:label@en | Domain | Range |
|---|---|---|---|---|
| `geo:drilled_in` | perfurado em | drilled in | `geo:poco` | `geo:bloco` |
| `geo:delimited_in` | delimitado em | delimited in | `geo:bloco` | `geo:bacia-sedimentar` |
| `geo:governed_by` | regido por | governed by | `geo:bloco` | `geo:contrato-ep` |
| `geo:defines` | define | defines | `geo:contrato-ep` | `geo:regime-contratual` |
| `geo:organized_in` | organizado em | organized in | `geo:contrato-ep` | `geo:periodo-exploratorio` |
| `geo:measured_via` | mede via | measured via | `geo:contrato-ep` | `geo:uts` |
| `geo:may_have` | pode ter | may have | `geo:bloco` | `geo:pad` |
| `geo:evaluates` | avalia | evaluates | `geo:pad` | `geo:bloco` |
| `geo:may_yield` | pode gerar | may yield | `geo:pad` | `geo:declaracao-comercialidade` |
| `geo:initiates` | da inicio a | initiates | `geo:declaracao-comercialidade` | `geo:area-desenvolvimento` |
| `geo:originates` | origina | originates | `geo:declaracao-comercialidade` | `geo:campo` |
| `geo:requires` | exige | requires | `geo:area-desenvolvimento` | `geo:plano-desenvolvimento` |
| `geo:ends_with` | encerrada pelo | ends with | `geo:area-desenvolvimento` | `geo:primeiro-oleo` |
| `geo:inaugurates` | inaugura | inaugurates | `geo:primeiro-oleo` | `geo:campo` |
| `geo:originated_in` | originado em | originated in | `geo:bloco` | `geo:rodada-licitacao` |
| `geo:signed_with` | celebrado com | signed with | `geo:contrato-ep` | `geo:anp` |
| `geo:operated_by` | operado por | operated by | union of (poco, bloco, campo) | `geo:operador` |

### Geological chain properties

| Property URI | rdfs:label@pt | Domain | Range |
|---|---|---|---|
| `geo:traverses` | atravessa | `geo:poco` | `geo:formacao` |
| `geo:hosted_in` | hospedado em | `geo:reservatorio` | `geo:formacao` |
| `geo:sustained_by` | sustentado por | `geo:campo` | `geo:reservatorio` |
| `geo:contained_in` | contido em | `geo:reservatorio` | `geo:bacia-sedimentar` |
| `geo:located_in` | localizado em | union of (poco, campo) | `geo:bacia-sedimentar` |
| `geo:feeds` | alimenta | `geo:rocha-geradora` | `geo:sistema-petrolifero` |
| `geo:forms` | compoe | `geo:falha` | `geo:trapa` |
| `geo:comprises` | comporta | `geo:trapa` | `geo:reservatorio` |
| `geo:contains` | contem | `geo:trapa` | `geo:acumulacao` |
| `geo:becomes` | origina | `geo:acumulacao` | `geo:campo` |
| `geo:spawns` | gera | `geo:play` | `geo:prospecto` |
| `geo:integrates_to` | integra-se a | `geo:sistema-petrolifero` | `geo:bacia-sedimentar` |
| `geo:has_age` | tem idade | `geo:formacao` | `geo:idade-geologica` |

### Resource/Reserve properties

| Property URI | rdfs:label@pt | Domain | Range |
|---|---|---|---|
| `geo:declares` | declara | `geo:campo` | `geo:reserva` |
| `geo:derived_from` | deriva de | `geo:reserva` | `geo:recurso` |
| `geo:allocated_to` | alocado em | `geo:recurso` | `geo:bloco` |
| `geo:reports` | reporta | `geo:operador` | `geo:recurso` |

### Analytical properties

| Property URI | rdfs:label@pt | Domain | Range |
|---|---|---|---|
| `geo:undergoes` | submetida a | `geo:amostra-fluido` | `geo:pvt` or `geo:sara` |
| `geo:classifies` | classifica | `geo:pvt` | `geo:classe-fluido` |
| `geo:detects` | detecta | `geo:gc-ms` | `geo:biomarcador` |
| `geo:enables` | permite | `geo:biomarcador` | `geo:correlacao-oleo-rocha` |
| `geo:defines` | define | `geo:campo-tensional` | `geo:janela-lama` |
| `geo:guides_drilling_of` | guia perfuracao de | `geo:janela-lama` | `geo:poco` |
| `geo:has_property` | tem propriedade | `geo:falha` | `geo:potencial-selante` |
| `geo:measures` | mede | `geo:perfil-poco` | `geo:poco` |
| `geo:infers` | infere | `geo:perfil-poco` | `geo:litologia` |

---

## Schema-Level Triple Assertions

The TTL also contains schema-level triple assertions that encode the class-to-class graph structure directly:

```turtle
geo:poco geo:drilled_in geo:bloco .
geo:bloco geo:delimited_in geo:bacia-sedimentar .
geo:bloco geo:governed_by geo:contrato-ep .
geo:contrato-ep geo:defines geo:regime-contratual .
geo:pad geo:may_yield geo:declaracao-comercialidade .
geo:declaracao-comercialidade geo:originates geo:campo .
geo:campo geo:located_in geo:bacia-sedimentar .
geo:campo geo:sustained_by geo:reservatorio .
geo:reservatorio geo:hosted_in geo:formacao .
geo:rocha-geradora geo:feeds geo:sistema-petrolifero .
geo:sistema-petrolifero geo:integrates_to geo:bacia-sedimentar .
geo:falha geo:forms geo:trapa .
geo:campo geo:declares geo:reserva .
geo:reserva geo:derived_from geo:recurso .
```

Use these triples to validate path queries before writing SPARQL property paths.

---

## External Alignment Properties

| Property | Usage |
|---|---|
| `owl:sameAs` | Maps `geo:` classes to OSDU URIs (`https://w3id.org/osdu#...`) |
| `rdfs:seeAlso` | Points to Petro KGraph URIs (`https://raw.githubusercontent.com/Petroles/PetroNLP/main/Petro%20KGraph%20public.owl#...`) |

---

## Critical Disambiguations (for SPARQL)

### PAD — query pattern
Use `geo:pad` when the question is about a Discovery Evaluation Plan. The English label is "Discovery Evaluation Plan", not "drilling pad".

```sparql
geo:pad skos:prefLabel "PAD"@pt ;
        skos:definition "..."@pt .
```

### Reserva vs Reservatorio
- `geo:reserva` has `geo:entityType "contractual"` — commercial reserves (SPE-PRMS).
- `geo:reservatorio` has `geo:entityType "operational"` — geological reservoir rock.

To distinguish them by entity type:
```sparql
?classe geo:entityType "contractual" .   # -> geo:reserva
?classe geo:entityType "operational" .   # -> geo:reservatorio
```

### Regime Contratual
The two Brazilian contractual regimes (Concessao, Partilha) are values/instances of `geo:regime-contratual`, not separate classes in the TTL. To retrieve the regime description:
```sparql
geo:regime-contratual skos:definition ?def .
FILTER(LANG(?def) = "pt")
```

### Formacao vs Litologia
- `geo:formacao` — lithostratigraphic unit name. `geo:entityType "geological"`.
- `geo:litologia` — petrographic rock type inferred from well logs. `geo:entityType "analytical"`.

To check type:
```sparql
geo:formacao  geo:entityType "geological" .
geo:litologia geo:entityType "analytical" .
```

---

## Example SPARQL Query

**Question:** Quais classes do tipo 'geological' sao alcancaveis a partir de geo:poco em um ou dois saltos de propriedades OWL?

```sparql
PREFIX geo:  <https://geolytics.petrobras.com.br/dict/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?alvo ?label_pt ?saltos
WHERE {
  {
    # 1 salto
    ?p1 a owl:ObjectProperty ;
        rdfs:domain geo:poco ;
        rdfs:range ?alvo .
    ?alvo geo:entityType "geological" ;
          skos:prefLabel ?label_pt .
    FILTER(LANG(?label_pt) = "pt")
    BIND(1 AS ?saltos)
  }
  UNION
  {
    # 2 saltos
    ?p1 a owl:ObjectProperty ;
        rdfs:domain geo:poco ;
        rdfs:range ?intermediario .
    ?p2 a owl:ObjectProperty ;
        rdfs:domain ?intermediario ;
        rdfs:range ?alvo .
    ?alvo geo:entityType "geological" ;
          skos:prefLabel ?label_pt .
    FILTER(LANG(?label_pt) = "pt")
    BIND(2 AS ?saltos)
  }
}
ORDER BY ?saltos ?label_pt
```
