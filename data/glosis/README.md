# GLOSIS reuse layer

Reaproveitamento da **GloSIS v1.5.1** (Global Soil Information System ontology — SIEUSOIL/EJP SOIL/ISRIC) para enriquecer o Geolytics Dictionary.
Análise completa: `../glosis-extraction.md`.

## Arquivos

| Arquivo | Conteúdo | Origem |
|---|---|---|
| `lithology.json` | 88 conceitos da hierarquia FAO/SOTER (`lithologyValueCode`) com `prefLabel`, `definition`, `notation`, `broader`, `iri` | `glosis_cl.ttl` |
| `lithology-crosswalk-cgi.json` | **88/88 conceitos GLOSIS classificados** (19 exactMatch, 35 closeMatch, 14 broadMatch, 1 relatedMatch, 19 noMatch). Cada linha tem `review`: `auto` (33) ou `manual` (50 + SC3 refinado). | join automático + revisão manual |
| `petrography-codelists.json` | 22 codelists (cementação, weathering, porosidade, estrutura, granulometria, plasticidade, landform) — 166 conceitos | `glosis_cl.ttl` |
| `inspire-geomorph-codelists.json` | 4 codelists INSPIRE Geomorphology/EventEnvironment — 227 conceitos (38 + 16 + 166 + 7) | INSPIRE Registry RDF |
| `lithology-crosswalk-inspire-geomorph.json` | **Crosswalk dos 19 GLOSIS noMatch** contra INSPIRE Geomorph (1:N, 29 links totais — 2 exactMatch, 9 closeMatch, 5 broadMatch, 3 ainda noMatch) | manual |
| `lithology-crosswalk-inspire-litho.json` | Crosswalk transitivo GLOSIS → CGI 2016.01 → INSPIRE **LithologyValue** (mínimo: 1 mapeamento IB3, documenta o pattern) | derivado |
| `geolytics-glosis-ext.ttl` | **Ontologia OWL+SKOS** — 417 triples: 4 `owl:imports` (codelists, ISO 28258, procedures, units), 99 mappings SKOS, backbone E&P, par `*Property`/`*Value` para 18 campos PVT | gerado |
| `geolytics-modules.ttl` | M7/M8/M9/M10 modules serialization — 463 triples | gerado |
| `geolytics-units.ttl` | Unidades petroleiras (BBL/D, MCF/D, SCF/STB, RB/STB, °API, psia, cP, mD…) — 123 triples, 13 unidades, 5 quantity kinds | manual |
| `pvt-procedures.ttl` | 8 procedures PVT (flash/differential liberation, CCE, swelling, separator, viscosity, slim-tube, multi-contact) — 116 triples | manual |
| `geolytics-ep-backbone.ttl` | ISO 28258 alias completo: 16 object properties + cardinalidades + SOSA bridge — 136 triples | manual |
| `geolytics-shapes.ttl` | 6 SHACL shapes (qudt:Quantity, ISO depth invariant, SOSA Observation, lithology IRI source, PVT row, crosswalk symmetry) — 107 triples | manual |
| `cgi-version-strategy.json` | Estratégia de fallback CGI 201211 ↔ 2016.01 | doc |
| `source-ttl/` | Cache local dos 11 módulos GLOSIS v1.5.1 (~1,2 MB) | upstream |
| `README.md` | Este arquivo | — |

## Onde foi integrado no projeto

- **`data/osdu-gso-crosswalk.json`** — nova seção `glosis_reuse` listando componentes reutilizáveis (ISO 28258 backbone, 95 codelists SKOS, 27 procedure codelists, padrão SOSA Property/Value, módulo QUDT-unit).
- **`data/pvt-dictionary.json`** — 18 campos numéricos receberam bloco `qudt` (com `unit` e `hasQuantityKind` IRIs) + bloco `sosa_pattern` (par `*Property`/`*Value` estilo GLOSIS).
- **`data/modules-extended.json`** — módulos M7/M8/M9/M10 recebem bloco `qudt_pattern` com defaults de quantidade e instruções de aplicação; 11 classes quantitativas anotadas com `sosa_pattern`.

## Licença

GLOSIS é **CC BY-NC-SA 3.0 IGO** (uso não-comercial, com atribuição e share-alike). O módulo `glosis_unit` é **CC BY 4.0**.
**Atribuição obrigatória:** Palma R., Janiak B., Reznik T., Schleidt K. e equipe SIEUSOIL/ISRIC (2020) — http://w3id.org/glosis/model/

## Insight da revisão

Os **19 `noMatch`** se concentram nos códigos `U*` da GLOSIS (colluvial, eolian, fluvial, glacial, kryogenic, lacustrine, marine, organic, anthropogenic-mistos) — esses **não são litologias**, são **classes de material parental por gênese** (geomorfológicas/sedimentológicas). CGI Simple Lithology é vocabulário litológico-petrográfico, então a falta de mapeamento não é um gap a corrigir lá; é gap **de vocabulário**: para esses conceitos o alvo correto é **INSPIRE Geomorphology** ou **GeoSciML Geomorphology**, não CGI.

Os **14 `broadMatch`** revelam o padrão "GLOSIS é mais específico" em três frentes: (a) categorias químicas em metamórficas (`acid/basic/ultrabasic metamorphic` → CGI `metamorphic rock`), (b) minerais individuais em evaporitos (`halite` → CGI `evaporite`), (c) variantes genéticas de areias/cascalhos (`glacio-fluvial sand` → CGI `sand`). Útil para queries hierárquicas SKOS via `skos:broader`.

## Cobertura final dos 88 conceitos GLOSIS lithology

| Vocabulário-alvo | Match coverage |
|---|---|
| CGI Simple Lithology 201211 | 70/88 mapeados (19 exact + 36 close + 14 broad + 1 related), **18 noMatch** |
| CGI Simple Lithology 2016.01 (fallback) | 1 (IB3 dolerite → doleritic_rock) |
| INSPIRE Geomorphology + EventEnvironment | **16/18** dos noMatch cobertos (2 exact + 9 close + 5 broad em 29 links 1:N) |
| **Total cobertura final** | **86/88 (97,7%)** — 2 sem match em qualquer vocabulário: `UU` (unspecified deposits), `UU2` (loam and silt — mistura genérica) |

### Aggregadores 1:N

13 conceitos GLOSIS que agregam múltiplos litotipos (II1, MA2, MA3, MB1, MU1, SC1, SC2, SE1, SO1, UF2, UR1, UU5, IU) usam `cgi_targets[]` para enumerar todos os alvos CGI. Total de 81 links CGI (acima dos 69 de mapeamento 1:1).

## Validação

```bash
python3 scripts/validate.py --self-check       # parse all TTLs + JSONs
python3 scripts/validate.py --crosswalk-audit  # check crosswalk integrity
python3 scripts/validate.py <data.ttl>         # SHACL validate instance data
```

Self-check status: 6 TTL files (1361 triples) + 6 JSON files — todos OK.

## Próximos passos sugeridos

1. **2 conceitos remanescentes:** `UU` e `UU2` são agregadores genéricos sem equivalente — manter como noMatch.
2. **Tradução PT/ES** dos labels (atualmente só EN no GLOSIS upstream).
3. **Registrar PURL** em w3id.org (ver `w3id-registration-draft.md`).
4. **WiDoco generation** para gerar HTML pyLODE-style automático dos TTLs.
5. **FAIRsharing registration** do Geolytics Dictionary (espelhar `doi.org/10.25504/FAIRsharing.af87a1`).
