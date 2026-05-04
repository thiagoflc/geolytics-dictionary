# Vocabulário de Predicados — GeoBrain

Especificação normativa do vocabulário relacional do grafo [data/entity-graph.json](data/entity-graph.json). Define quais predicados são canônicos, quais devem ser deprecados, quais precisam ser introduzidos e como cada um se alinha às seis camadas descritas em [docs/ONTOLOGY_LAYERS.md](docs/ONTOLOGY_LAYERS.md).

---

## 1. Princípio

Predicados existentes no grafo são reutilizados sempre que houver equivalência semântica. **Não criar sinônimos** de predicado existente. Um novo predicado só é admissível quando:

1. Há gap conceitual claro (nenhum predicado em uso captura a semântica intencionada), e
2. O ganho expressivo justifica o custo de migração e treinamento de curadoria.

Quando um predicado existente é levemente impreciso, a preferência é refinar sua semântica documentada — e migrar instâncias quando necessário — em vez de cunhar um termo paralelo.

A perspectiva inversa de uma relação **não justifica** um novo predicado: inversos são gerados por inferência (regras SPARQL/SHACL ou views Cypher), não materializados como arestas.

---

## 2. Mapeamento canônico ↔ existente

Tabela cruzando predicados da proposta de seis camadas com o vocabulário em uso. Status:

- `keep` — já existe e é canônico; nenhuma ação.
- `alias` — variante existe; consolidar instâncias no canônico em fase futura.
- `new` — gap real; introduzir.
- `inferred` — inverso de outro canônico; **não materializar**, gerar por regra.

| Canônico (proposta) | Status | Existente em uso | Exemplo (source → target) | Inverso (não materializar) |
|---|---|---|---|---|
| `engaged_by` | new | — | `Well → engaged_by → WellOperation` (ex.: `poco → drilling-activity`) | `engages` (= `occurs_in`) |
| `occurs_in` | keep | `occurs_in` (11) | `WellOperation → occurs_in → Well` | `is_location_of` |
| `generates` | keep | `generates` (1), `produces` (20), `yields` (2) | `WellOperation → generates → Sample` (ex.: `coring → generates → core-sample`) | `generated_by` |
| `acquired_from` | new | parcial: `measured_at` (25), `acquired_during` (1) | `WellLog → acquired_from → Well` (ex.: `perfil-poco → acquired_from → poco`) | `is_log_source_of` (inferido) |
| `consumes` | alias | `is_input_for` (19), `requires_input` (9), `requires` (21), `uses` (2) | `InterpretationProcess → consumes → Sample` | `consumed_by` |
| `produces` | keep | `produces` (20), `yields` (2), `output_of` (1) | `InterpretationProcess → produces → GeologicalFeature` | `produced_by` |
| `interpreted_into` | new | parcial: `derived_from` (35), `infers` (1) | `Sample → interpreted_into → InterpretedDataset` | `derived_from` |
| `observed_in` | new | parcial: `detected_via` (29), `detects` (1), `measured_at` (25) | `GeologicalFeature → observed_in → Well` | `is_observation_context_of` (inferido) |
| `derived_from` | keep | `derived_from` (35) | `InterpretedDataset → derived_from → WellLog` | (já é inverso natural de `produces`) |
| `applies_to` | new | parcial: `performed_on` (3), `scoped_to` (1) | `WellEngineeringArtifact → applies_to → Well` (ex.: `casing-design → applies_to → poco`) | `has_engineering_artifact` |
| `supports` | keep | `supports` (2), `enables` (5) | `WellEngineeringArtifact → supports → WellOperation` | `supported_by` |
| `constrains` | keep | `constrains` (16) | `WellEngineeringArtifact → constrains → WellOperation` | `constrained_by` |
| `valid_for` | new | parcial: `applies_to` (proposto), `scoped_to` (1) | `Standard → valid_for → InterpretationProcess` | `governed_by` |
| `correlated_with` | alias | `correlates_with` (2), `co_measured_with` (2), `complements` (4) | `GeologicalFeature → correlated_with → GeologicalFeature` | simétrico |
| `intersects` | new | — | `GeologicalFeature → intersects → Wellbore` | simétrico |
| `assigns` / `assigned_to` | alias | `classifies` (5), `classified_by` (4), `qualified_by` (1) | `WellAttributeConcept → assigned_to → Well` | inverso simétrico |
| `based_on` | alias | `informed_by` (1), `references` (1) | `InterpretationProcess → based_on → Standard` | `is_basis_of` |
| `estimated_from` | alias | `estimates` (8), `is_calculated_from` (14), `computes` (11) | `Property → estimated_from → WellLog` | `estimates` (inverso) |
| `is_location_of` | inferred | — (deriva de `occurs_in`, `acquired_from`, `observed_in`) | inferido em SPARQL/Cypher, não escrito | — |
| `is_sample_source_of` | inferred | — (deriva de `generates` quando target é Sample) | inferido | — |
| `is_log_source_of` | inferred | — (deriva de `acquired_from`) | inferido | — |
| `is_test_location_of` | inferred | — (deriva de `occurs_in` quando subject é WellTest) | inferido | — |
| `is_observation_context_of` | inferred | — (deriva de `observed_in`) | inferido | — |

**Regra sobre inversos.** As linhas marcadas `inferred` representam o mesmo fato com sujeito invertido. Persistí-las dobra o número de arestas, força sincronização manual e abre porta a inconsistências. Materializa-se apenas o predicado **direto** (na coluna canônica); o inverso é exposto via consulta. Esta regra é normativa.

---

## 3. Recomendações de adição (mínimas)

Predicados realmente novos a introduzir no grafo, justificados por gap conceitual claro nas seis camadas:

| Predicado | Domínio → Contradomínio | Justificativa |
|---|---|---|
| `engaged_by` | `Well → WellOperation` | Conecta L1 a L2 explicitamente. Hoje não existe; sem ele, o Poço fica órfão das suas operações no grafo direto. |
| `acquired_from` | `WellLog → Well` (também `TestData → Well`) | Captura proveniência locacional do registro. `measured_at` é próximo mas não distingue artefato de medida pontual. |
| `interpreted_into` | `Sample | WellLog | TestData → InterpretedDataset` | Liga L3 ao produto interpretado quando a interpretação é cadeia (artefato → artefato derivado), distinto do processo cognitivo `consumes`/`produces`. |
| `observed_in` | `GeologicalFeature → Well` | Liga L4 a L1 sem passar pela operação (uma feature pode ser observada por múltiplas operações; o vínculo locacional é direto). |
| `applies_to` | `WellEngineeringArtifact → Well` | Estabelece a relação L6 ↔ L1 que hoje está ausente — causa raiz da ilha de 84 nós `geomec_corporate` desconectados (ver [docs/ONTOLOGY_LAYERS.md](docs/ONTOLOGY_LAYERS.md) §9). |
| `intersects` | `GeologicalFeature → Wellbore` | Geometria estrutural: a feature corta o trecho perfurado em uma profundidade ou intervalo. Necessário para image-log e interpretação geomecânica. |

`engaged_by` é o inverso semântico de `occurs_in` mas com perspectiva de Poço. Recomenda-se materializar **apenas um deles** — escolha: manter `occurs_in` (já em uso, 11 instâncias) e gerar `engaged_by` por inferência. Esta decisão merece confirmação do curador (ver §7).

---

## 4. Predicados a manter como estão

Os predicados a seguir são canônicos do dicionário e permanecem o vocabulário oficial. Cada um cobre um padrão semântico distinto, sem sobreposição.

| Predicado | Uso | Semântica preservada |
|---|---|---|
| `is_part_of` / `part_of` | 34 / 13 | Mereologia (BFO part-of). Consolidar em `is_part_of` em fase futura. |
| `is_calculated_from` | 14 | Cálculo determinístico, distinto de `derived_from` (interpretação ou transformação genérica). |
| `produces` | 20 | Saída de processo. Mantido junto a `generates` que cobre operação física L2; `produces` é mais geral. |
| `derived_from` | 35 | Derivação de artefato a partir de outro (interpretação, agregação, transformação). |
| `is_specialization_of` | 3 | Subsunção taxonômica. Necessário para os componentes isolados (`GEOMEC084` → esquema de qualidade pai, etc.). |
| `governed_by` | 5 | Sujeição a norma/regulação. Liga L2/L6 a `regulatory_anchor`. |
| `is_input_for` | 19 | Insumo de processo. Coexiste com `consumes` (proposto) — `is_input_for` permanece canônico no grafo atual; `consumes` é alias semântico. |
| `requires` | 21 | Requisito não-consumível (capacidade, contexto). Distinto de `requires_input` (9). |
| `constrains` | 16 | Restrição operacional (L6 → L2). |
| `measures` | 17 | Instrumento mede grandeza. |
| `monitors` | 5 | Acompanhamento contínuo no tempo (séries). |
| `influences` | 34 | Causalidade fraca, qualitativa. Mantido — vocabulário consolidado em geomecânica. |
| `detected_via` | 29 | Indica método de detecção; **revisão pendente** — em parte sobrepõe-se a `observed_in` proposto. Avaliar consolidação. |
| `located_in`, `contained_in`, `hosted_in` | 27 / 1 / 1 | Geografia/contenção física. Manter `located_in` como canônico, deprecar os demais em fase futura. |

---

## 5. Predicados a evitar

Sinalizadores de uso problemático. **Não usar em novos dados**; instâncias existentes devem ser revisadas e migradas.

| Predicado | Instâncias | Problema | Alternativa |
|---|---|---|---|
| `related_to` | 26 | Vago demais; não preserva semântica. | Substituir por relação específica (`correlated_with`, `references`, `is_input_for`, `derived_from`, `governed_by` conforme contexto). |
| `used_with` | 13 | Ambíguo entre coocorrência operacional e dependência de insumo. | `co_measured_with` (se medição simultânea) ou `is_input_for` (se insumo). |
| `complements` | 4 | Sobrepõe-se a `correlated_with` e `co_measured_with`. | `correlated_with`. |
| `feeds` | 4 | Coloquial; equivalente a `is_input_for`. | `is_input_for`. |
| `connects` | 3 | Sem direção semântica clara. | Especializar em `is_part_of`, `composed_of` ou relação topológica explícita. |
| `may_*` (`may_have`, `may_trigger`, `may_yield`, `may_register`, `may_reach`, `may_include`, `may_contribute_to`, `may_reference`) | 8 total | Modalidade epistêmica colada ao predicado polui o vocabulário. | Predicado direto + propriedade `confidence`/`modality` na aresta. |

A deprecation é **declarativa** nesta especificação; nenhuma alteração em `data/` é proposta aqui. A migração ocorre em fase F4, com alvo `related_to → 0` e os demais reduzidos a casos legítimos auditados.

---

## 6. Apêndice — Alinhamento BFO/SOSA/IAO

Registro de intenção para fase OWL futura. Não emitir TTL agora; o objetivo é fixar a semântica para que o pipeline ETL e as views SHACL possam alinhar quando cobertura `layer1` (BFO+GeoCore) for ativada.

| Camada GeoBrain | BFO / SOSA / IAO equivalente |
|---|---|
| L1 `Well` | `bfo:material entity` (subclasse `bfo:object` ou `bfo:fiat object part` do subsolo); endurantete físico, perdura no tempo. |
| L2 `WellOperation` | `bfo:process` (perdurante, ocupa intervalo temporal); subclasses como `iao:planned process` quando há plano executivo. |
| L3 `Sample` | `bfo:material entity` (objeto físico extraído). |
| L3 `WellLog` | `sosa:Result` + `iao:information artifact` — agregado de observações (sosa:Observation) registrado em meio digital. |
| L3 `TestData` | análogo a `WellLog`: `sosa:Result` + `iao:information artifact` para séries de teste. |
| L4 `GeologicalFeature` | `bfo:fiat object part` ou `bfo:site`, projetado sobre `Well`/`Wellbore`. |
| L5 `InterpretationProcess` | `bfo:process` ⊓ `iao:planned process`; consome `iao:information artifact` e produz `iao:information content entity`. |
| L6 `WellEngineeringArtifact` | `iao:plan specification` ou `iao:directive information entity`. |
| Predicados | `engaged_by` ≈ `bfo:participates in` (com filtro de papel); `occurs_in` ≈ `bfo:occurs in`; `generates` ≈ `bfo:has output`; `consumes` ≈ `bfo:has input`; `applies_to` ≈ `iao:is about` (especializado para Poço). |

Esta tabela é orientativa; a tradução completa para OWL será proposta separadamente quando a cobertura `layer1` (UFRGS/BDI + Geosiris) for incorporada ao pipeline conforme [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 7. Referências cruzadas

- Camadas e regra de ouro: [docs/ONTOLOGY_LAYERS.md](docs/ONTOLOGY_LAYERS.md).
- Arquitetura geral: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- Vocabulários SKOS e SHACL: [data/geolytics-vocab.ttl](data/geolytics-vocab.ttl), [data/geolytics-shapes.ttl](data/geolytics-shapes.ttl), [docs/SHACL.md](docs/SHACL.md).
- Crosswalks externos (WITSML, OSDU, GSO, SWEET): [docs/EXTERNAL_STANDARDS.md](docs/EXTERNAL_STANDARDS.md).
