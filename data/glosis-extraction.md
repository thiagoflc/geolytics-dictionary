# GLOSIS — Análise profunda e oportunidades de enriquecimento

**Fonte:** https://glosis-ld.github.io/glosis/ — repo: https://github.com/glosis-ld/glosis

**Versão analisada:** 1.5.1 (release 1.5.0 — 2025-03-12) · **Licença:** CC BY-NC-SA 3.0 IGO (módulo `unit` é CC BY 4.0)
**FAIRsharing:** https://doi.org/10.25504/FAIRsharing.af87a1
**Origem:** SIEUSOIL (China-EU) + EJP SOIL · ISRIC, PSNC, Masaryk Univ., Ghent Univ., Datacove
**Geração de docs:** WiDoco

---

## 1. Arquitetura — 11 módulos (relevante como template)

Padrão é diretamente reusável para a GeoBrain: ontologia mestre que faz `owl:imports` de módulos por escopo, codelists separados como SKOS, módulo de unidades QUDT.

| Módulo | IRI base | Conteúdo | Tamanho |
|---|---|---|---|
| `main` | `w3id.org/glosis/model/main/` | Master profile, imports tudo | 0 classes — só metadados |
| `common` | `w3id.org/glosis/model/common/` | Tipos de valor compartilhados (depth, color, rock-size…) | 27 classes |
| `siteplot` | `w3id.org/glosis/model/siteplot/` | Características de sítio/parcela (slope, lithology, landform, climate, vegetation, erosion, flood…) | 52 classes, 5 oprop, 9 dprop |
| `profile` | `w3id.org/glosis/model/profile/` | Classificação de perfis de solo (FAO/USDA/WRB) | 6 classes |
| `layerhorizon` | `w3id.org/glosis/model/layerhorizon/` | **Geoquímica/mineralogia/granulometria/estrutura por camada** | **212 classes** |
| `surface` | `w3id.org/glosis/model/surface/` | Salinidade superficial, selamento | 7 classes |
| `observation` | `w3id.org/glosis/model/observation/` | `GL_Observation` ⊑ `OM_Observation` | 1 classe |
| `procedure` | `w3id.org/glosis/model/procedure/` | **27 codelists de procedimento analítico** (pH, CEC, BD, PSA…) | 27 schemes |
| `codelists` | `w3id.org/glosis/model/codelists/` | **95 codelists SKOS** (litologia, landform, textura…) | 95 schemes |
| `unit` | `w3id.org/glosis/model/unit/` | Unidades QUDT extras (ex.: `cmol/L`, `g/100g`, `m3/100m3`) | extensão QUDT |
| `iso28258` | `w3id.org/glosis/model/iso28258/2013/` | **Backbone estrutural ISO 28258** | 7 classes, 16 oprop |

### Backbone ISO 28258 (lições para o E&P)
Hierarquia geral `Site → Plot → Profile → ProfileElement(Layer|Horizon) → Surface`. Equivalente conceitual no E&P:
- `Site` ↔ Bloco/Campo
- `Plot` ↔ Locação de poço
- `Profile` ↔ Coluna estratigráfica/log do poço
- `ProfileElement` ↔ Intervalo (com `lowerDepth`/`upperDepth`/`order`)
- `Layer` ↔ camada sedimentar; `Horizon` ↔ unidade pedogênica/diagenética

**Object properties ISO 28258** (16, todas reusáveis como padrão):
`Site.samplingPlot`, `Site.typicalProfile`, `Plot.plotInSite`, `Plot.profile`, `Profile.profileSite`, `Profile.samplingPlot`, `Profile.element`, `ProfileElement.elementOfProfile`, `ProfileElement.upperDepth`, `ProfileElement.lowerDepth`, `ProfileElement.order`, `Layer.developedHorizon`, `Horizon.horizonInLayer` etc.
→ `Site` e `Profile` são `rdfs:subClassOf iso19156_GFI:GFI_Feature` (reuso direto de OGC O&M).

---

## 2. Stack de padrões (reusar no projeto)

```
@prefix sosa: <http://www.w3.org/ns/sosa/>          # observação/sensor
@prefix ssn:  <http://www.w3.org/ns/ssn/>           # rede de sensores
@prefix gsp:  <http://www.opengis.net/ont/geosparql#>
@prefix iso19156_*: <http://def.isotc211.org/iso19156/2011/...>  # O&M, SF, SSF
@prefix iso19115_DQI: <...>                          # qualidade
@prefix qudt: <http://qudt.org/schema/qudt/>         # unidades
@prefix quantitykind: <http://qudt.org/vocab/quantitykind/>
@prefix skos: <http://www.w3.org/2004/02/skos/core#>
@prefix dct, dcat, foaf, schema, owl, rdfs
```

**Padrão idiomático observado** — toda propriedade física vira:
1. uma classe-feature (`*Property`, ex. `BulkDensityFineEarth`),
2. uma classe-valor (`*Value`, ex. `BulkDensityFineEarthValue`) com restrição QUDT (`qudt:unit`, `qudt:numericValue`),
3. ligação SOSA `hasResult` / `observedProperty` via OWL Restriction.

Esse pattern é exatamente o que falta na camada O3PO/PetroKGraph e no PVT-Dictionary do Geolytics — recomendado adotar.

---

## 3. Codelists SKOS — 95 schemes (alta reusabilidade)

**Diretamente alinháveis com layers existentes do Geolytics:**

| GLOSIS scheme | Cardinalidade | Onde encaixa no Geolytics |
|---|---|---|
| `lithologyValueCode` | 88 conceitos (FAO/SOTER hierárquica: I-igneous, M-metamorphic, S-sedimentary, U-unconsolidated) | **Layer 1b GeoSciML/CGI Lithology** — adicionar `skos:exactMatch`/`closeMatch` |
| `cementationDegreeValueCode` | Cemented, Indurated, Moderately/Weakly cemented, Compacted but non-cemented, Non-cemented… | **Reservoir characterization** — diagênese |
| `cementationNatureValueCode` | Clay, Iron, Iron–manganese, Iron–organic, Clay–sesquioxides… | Diagênese / qualidade reservatório |
| `cementationFabricValueCode` | Nodular, Pisolithic, Platy, Vesicular | Petrografia |
| `weatheringValueCode` | Fresh / Slightly / Weathered / Strongly weathered | Alteração de basamento |
| `porosityClassValueCode` | Very low / Low / Medium / High / Very high | Reservatório (alinhar com SPE-PRMS) |
| `structureGradeValueCode` + `structureSizeValueCode` | Weak/Moderate/Strong + Fine/Medium/Coarse/Very coarse… | Petrografia / fácies |
| `rockSizeValueCode` + `rockShapeValueCode` | Boulders/Stones/Gravel… + Angular/Subrounded/Rounded/Flat | Sedimentologia (clastos) |
| `textureUnconsolidatedValueCode` | Texturas USDA | Sedimentos não-consolidados |
| `plasticityValueCode` / `stickinessValueCode` | Non-plastic…Very plastic / Non-sticky…Very sticky | Geomecânica de argilas (selo) |
| `majorLandFormValueCode` | 16 formas (plateau, valley floor, escarpment, hill, mountain…) | Mapeamento superficial |
| `physiographyValueCode` | — | Mapeamento superficial |
| `slopeFormValueCode` / `slopeGradientClassValueCode` | — | Topografia para risco geomecânico |
| `fragmentsClassValueCode` / `fragmentsSizeValueCode` | — | Análise de cuttings |

**Codelists de procedimento analítico (27)** — reusar formato:
`pHProcedure`, `cationExchangeCapacitySoilProcedure`, `effectiveCecProcedure`, `bulkDensityFineEarthProcedure`, `bulkDensityWholeSoilProcedure`, `carbonOrganicProcedure`, `carbonInorganicProcedure`, `carbonTotalProcedure`, `nitrogenTotalProcedure`, `pSAProcedure` (Particle Size Analysis), `electricalConductivityProcedure`, `hydraulicConductivityProcedure`, `porosityProcedure`, `moistureContentProcedure`, `availableWaterHoldingCapacityProcedure`, `phosphorusRetentionProcedure`, `gypsumProcedure`, `solubleSaltsProcedure`, `totalCarbonateEquivalentProcedure`, `acidityExchangeableProcedure`, `baseSaturationProcedure`, `exchangeableBasesProcedure`, `extractableElementsProcedure`, `totalElementsProcedure`, `coarseFragmentsProcedure`, `organicMatterProcedure`, `textureSumProcedure`.

> **Padrão**: cada `Procedure` é `skos:Concept` **e** `sosa:Procedure` simultaneamente — vinculação direta ao SOSA. **Replicar em `geobrain` para procedimentos PVT/geoquímica** (já existe `pvt-dictionary.json` com 34 campos do SIRR).

---

## 4. Layer/Horizon — 212 classes de propriedades quantitativas

Este é o módulo mais denso e o que tem **maior overlap com geoquímica de petróleo**. Famílias de classes (cada uma vem em par `X` + `XValue`):

- **pH**, **CEC** (3 variantes: `CationExchangeCapacity`, `Effective`, `cSoil`), **BaseSaturation**, **Acidity** (`Exchangeable`, `Total`), **CationsSum**
- **Carbon**: `CarbonOrganic`, `CarbonInorganic`, `CarbonTotal`, `OrganicMatter`
- **Nitrogen**, **Sulfur** (Total, Extractable)
- **Cátions trocáveis**: Ca, Mg, K, Na, Al (família `*ExchangeableBases`)
- **Elementos extraíveis** (40+): Al, As, B, Cd, Ca, Cr, Co, Cu, Fe, Pb, Mg, Mn, Hg, Mo, Ni, P, K, Se, Si, Ag, Na, Sr, Zn — cada um × `Extractable` + `Total`
- **Granulometria**: `Clay`, `Silt`, `Sand` + frações de textura + `ClayFractionTexture`, `ClayMineralogy`
- **Densidade**: `BulkDensityFineEarth`, `BulkDensityWholeSoil`, `BulkDensityMineral`, `BulkDensityPeat`
- **Hidráulica**: `HydraulicConductivity`, `MoistureContent`, `AvailableWaterHoldingCapacity`
- **Estrutura**: `Boundary*`, `Cementation*`, `Coating*`, `Cracks*`, `Mottles*`, `Pores*`, `Voids*`, `Roots*`
- **Carbonatos / gipso / sais**

**Mapeamentos imediatos para Geolytics M7 (Geoquímica) / M8 (Rocha) / M9 (Geomecânica) / M10 (Fluidos):**

- M7 Geoquímica: `CarbonOrganic`/`CarbonTotal`/`CarbonInorganic` ↔ COT/CarbonateContent na Rock-Eval
- M7: `nitrogenTotal`, `sulfurTotal` ↔ S/N de querogênio
- M8 Rocha: BulkDensity*, ClayMineralogy, Cementation*, Porosity ↔ propriedades petrofísicas
- M9 Geomecânica: stickiness/plasticity ↔ argila reativa em selo
- M10 Fluidos: ElectricalConductivity, MoistureContent ↔ análises de água de formação

---

## 5. Convenções e infra (replicar)

- **PURL via w3id.org**: `http://w3id.org/glosis/model/...` — todas as IRIs persistentes via redirecionamento perma.cc/w3id. → Geolytics deveria registrar `w3id.org/geolytics/dictionary/` ao invés de depender de `thiagoflc.github.io`.
- **owl:versionIRI separado de IRI** (`/model/1.5.1` ≠ `/model`). Boa prática SemVer.
- **dct:isReferencedBy** apontando para FAIRsharing — adicionar registro FAIRsharing ao Geolytics.
- **Documentação WiDoco** auto-gerada a partir de TTL (https://github.com/dgarijo/Widoco). Substitui o `gso-cards.html` artesanal por geração automática para todos os módulos.
- **Crosswalks como CSV** em `csv_codelists/` separados do TTL — facilita ETL.
- **`utils/transformer-tool` + `utils/version-updater`** — scripts Python para regerar IRIs em bulk e versionar TTLs.

---

## 6. Oportunidades concretas de enriquecimento (ranqueadas)

### P0 — alto valor, baixo custo
1. **Adotar pattern `*Property` + `*Value` com QUDT** em `data/pvt-dictionary.json` e `modules-extended.json`. Cada um dos 34 campos PVT vira par classe/valor com `qudt:unit` + `qudt:hasQuantityKind`.
2. **Adicionar GLOSIS lithology como crosswalk** ao `data/osdu-gso-crosswalk.json`. O scheme tem hierarquia FAO/SOTER de 88 termos com `skos:broader` — alinhamento direto com `gso-faults.json` parents e Layer 1b CGI.
3. **Reusar codelists de cementação/weathering/porosity** como `skos:Concept` em layer de petrografia/diagênese. Importar diretamente os schemes via `owl:imports` em vez de duplicar.
4. **Adotar w3id.org PURL** para o Geolytics (registro free via https://github.com/perma-id/w3id.org). Trocar `thiagoflc.github.io` por `w3id.org/geolytics/dictionary` em todas as IRIs canônicas.

### P1 — alto valor, custo médio
5. **Backbone ISO 28258 → backbone E&P**: criar módulo `geolytics:wellprofile` espelhando `Site/Plot/Profile/Element/Layer` para Bloco/Locação/Poço/Intervalo/Camada, com as mesmas 16 object properties. ISO 19156 já está implícito nas referências OSDU.
6. **27 procedures GLOSIS como template** para criar procedures de PVT (ex.: `flashLiberationProcedure`, `differentialLiberationProcedure`, `swellingTestProcedure`, `constantCompositionExpansionProcedure`) — todas como `skos:Concept` ∧ `sosa:Procedure`.
7. **Substituir `gso-cards.html` artesanal por WiDoco** rodado contra `ontopetro.txt` (e demais TTLs quando existirem). Saída HTML estática + `application/rdf+xml`/JSON-LD por content negotiation.
8. **Módulo `unit/` próprio** com unidades de petróleo ausentes em QUDT (ex.: `bbl/d`, `Mcf/d`, `psia`, `RB/STB`, `scf/STB`) seguindo o template GLOSIS-unit (CC BY 4.0, IRIs `geolytics:unit/...`).

### P2 — alto valor, custo alto
9. **Geração de RAG-corpus a partir de TTL** (não só do JSON): cada `skos:Concept` com `prefLabel`+`definition`+`broader` vira chunk; adiciona ~3.000 conceitos GLOSIS reusados.
10. **Validação SHACL** das instâncias contra os shapes implícitos do GLOSIS (`owl:Restriction` + `oneOf` em codelists). Gera contracts para o pipeline de ingestão ANP→Geolytics.
11. **Registro FAIRsharing** do Geolytics dictionary, espelhando o registro do GLOSIS.

---

## 7. Arquivos baixados (cache)

`/tmp/glosis-fetch/` — 11 TTLs, ~1,2 MB total:
`glosis_main`, `glosis_common`, `glosis_cl` (545 KB · maior), `glosis_observation`, `glosis_procedure` (269 KB), `glosis_profile`, `glosis_siteplot`, `glosis_layer_horizon` (211 KB), `glosis_surface`, `glosis_unit`, `iso28258`.

Para reutilizar permanentemente, mover para `data/glosis/` no repo.
