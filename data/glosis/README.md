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
| `geolytics-glosis-ext.ttl` | **Ontologia OWL+SKOS** — 416 triples: 4 `owl:imports` (codelists, ISO 28258, procedures, units), 98 mappings SKOS (22 exact + 48 close + 22 broad + 6 related), backbone E&P (Bloco/Locação/PerfilPoço/Intervalo/Camada) sobre ISO 28258, e par `*Property`/`*Value` para 18 campos PVT | gerado |
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
| CGI Simple Lithology | 69/88 mapeados (19 exact + 35 close + 14 broad + 1 related), **19 noMatch** |
| INSPIRE Geomorphology + EventEnvironment | **16/19** dos noMatch acima cobertos (2 exact + 9 close + 5 broad em 29 links 1:N) |
| **Total cobertura final** | **85/88 (96,6%)** — 3 sem match em qualquer vocabulário: `IB3 dolerite` (litotipo, precisa CGI Geologic Unit Type), `UU` (unspecified deposits), `UU2` (loam and silt — mistura genérica) |

## Próximos passos sugeridos

1. **3 conceitos remanescentes:** `IB3 dolerite` deve ser mapeado contra **CGI Geologic Unit Type** ou **OneGeology Lithology** (vocabulários litológicos mais finos que CGI Simple Lithology). `UU` e `UU2` são agregadores genéricos sem equivalente — manter como noMatch.
2. **1:N nas closeMatch agregadas** (ex.: `MA2 gneiss, migmatite`, `SO1 limestone, other carbonate rock`): converter para múltiplos targets como já feito no crosswalk INSPIRE Geomorph.
3. **Emitir TTL** com `owl:imports` para `<http://w3id.org/glosis/model/codelists>`, `<http://w3id.org/glosis/model/iso28258/2013>`, `<http://inspire.ec.europa.eu/codelist/NaturalGeomorphologicFeatureTypeValue>` e `<http://inspire.ec.europa.eu/codelist/EventEnvironmentValue>`.
4. **Registrar PURL** em w3id.org (ver `data/glosis/w3id-registration-draft.md`).
