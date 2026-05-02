# Proposta — Enum Corporativo de Verbos de Relação

**Módulo:** `geomechanics-corporate` (Layer 6)
**Data:** 2026-05-02
**Para:** Gestão e Governança de Dados — Geomecânica E&P
**Origem:** Continuação da revisão "Frente C" do backlog pós-ingestão.

---

## Sumário executivo

O dicionário corporativo hoje opera com **66 verbos distintos** em 167 relações ativas — média de 2,5 relações por verbo. Há famílias claras de quase-sinônimos que diluem a semântica e dificultam queries do GraphRAG (ex.: 5 verbos diferentes para "medir/determinar grandeza"). A proposta abaixo consolida em **31 verbos canônicos** organizados em 13 famílias, mantendo todas as nuances que vocês já decidiram (`CO_MEASURED_WITH`, `ESTIMATES`, `MONITORS`).

**Impacto em 167 arestas atuais:**

| Ação | Quantas arestas | O que muda no banco |
|---|---:|---|
| Mantidas exatamente como estão | 118 | Zero impacto |
| Mescladas em verbo canônico (mesmo sentido) | 26 | `relation_type` renomeado |
| Direção invertida (canonical = inverso atual) | 23 | Origem e alvo trocam, verbo passa para a forma ativa |
| **Total alterado** | **49 / 167 (29%)** | |

**Convenção proposta:** armazenar **uma única direção por par** no JSON. O reasoner OWL e os consumidores (RAG, Cypher) inferem a inversa. Isso reduz redundância e elimina ambiguidade quando os dois sentidos são gravados manualmente com nuances diferentes.

---

## Os 31 verbos canônicos por família

Cada linha lista o verbo canônico, sua simetria/transitividade, e o uso pretendido. A coluna **Atual** mostra quantas arestas existem hoje convergindo para esse canônico.

### Família 1 — Composição (3 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `IS_PART_OF` | — | Sim | Qualquer→Process/Property | Meronimia hierárquica formal: A é parte estrutural de B | 18 |
| `CONTAINS` | — | Não | Document→{Property,Process} | Documento contém dado, forecast, ou seção (não confundir com `IS_PART_OF`) | 4 |
| `RELATED_TO` | Sim | Não | Qualquer→Qualquer | **Associação genérica fraca** — preferir verbo específico; usar com `edge_note` quando inevitável | 3 |

### Família 2 — Cálculo / Derivação (4 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `IS_CALCULATED_FROM` | — | Não | Property→Property | A = f(B), derivação **matemática** formal | 14 |
| `COMPUTES` | — | Não | Tool→Property | Ferramenta computa um valor (Tool→Output) | 4 |
| `ESTIMATES` | — | Não | Measurement→Property | Inferência **observacional não-matemática** (ex.: ISIP estima Shmin) | 5 |
| `DERIVED_FROM` | — | Não | Qualquer→Qualquer | Derivação geral, não estritamente matemática (ex.: ECD derivado de operação MPD) | 3 |

### Família 3 — Medição / Observação (4 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `MEASURES` | — | Não | {Process,Tool,Measurement}→Property | Origem é o método/teste/sistema; alvo é a grandeza física quantificada | 5 |
| `CO_MEASURED_WITH` | **Sim** | Não | Property↔Property | Co-derivação no mesmo ensaio (E ↔ ν, UCS ↔ E) — já aprovado em commit `dc1a0fc` | 2 |
| `MONITORS` | — | Não | Process→{Process,Risk,Measurement} | Sistema/processo observa evento, estado ou grandeza ao longo do tempo | 4 |
| `CALIBRATES` | — | Não | Process→{Property,Tool} | Dado de campo calibra modelo/ferramenta (≠ `MEASURES`, ≠ `ESTIMATES`) | 2 |

### Família 4 — Restrição (3 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `CONSTRAINS` | — | Não | Qualquer→Qualquer | Restrição operacional (ex.: ECD restringe Pp e Shmin) | 14 |
| `DEFINES_UPPER_BOUND` | — | Não | Property→Process | Define o teto operacional de uma janela | 1 |
| `DEFINES_LOWER_BOUND` | — | Não | Property→Process | Define o piso operacional de uma janela | 3 |

### Família 5 — Influência causal (3 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `INFLUENCES` | — | Não | Qualquer→Qualquer | Causalidade não estritamente matemática (ex.: Pp influencia tensões totais) | 29 |
| `INFLUENCED_BY` | — | Não | Qualquer→Qualquer | **Inverso de `INFLUENCES`** — usado quando a direção física é "X é afetado por Y" e a inversão geraria perda de leitura natural | 4 |
| `MAY_TRIGGER` | — | Não | Process→Process | Causalidade epistemicamente incerta — preserva incerteza no grafo (≠ `INFLUENCES`) | 2 |

### Família 6 — Produção (2 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `PRODUCES` | — | Não | {Process,Tool,Model}→{Document,Property} | Processo/sistema gera artefato (laudo, curva, valor) | 11 |
| `STORAGE_FOR` | — | Não | Tool→{Property,Document} | Sistema é repositório autoritativo do dado (≠ `PRODUCES` — quem armazena ≠ quem produz) | 1 |

### Família 7 — Especialização (1 verbo)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `IS_SPECIALIZATION_OF` | — | Sim | Qualquer→Qualquer | Taxonomia is-a (ex.: XLOT é especialização de Testes de Absorção) | 3 |

### Família 8 — Dependência (2 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `REQUIRES` | — | Não | Process→{Property,Process} | Dependência genérica para que o processo ocorra (use `edge_note` para tipo: validação/análise/conhecimento) | 11 |
| `REQUIRES_INPUT` | — | Não | Document/Process→Document/Property | Dependência computacional específica (insumo de entrada) | 2 |

### Família 9 — Governança (1 verbo)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `GOVERNED_BY` | — | Não | Qualquer→{Document,Process} | Governança formal — qual padrão PE-XXX, política ou comitê rege a entidade | 4 |

### Família 10 — Suporte / Uso (3 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `SUPPORTS` | — | Não | Qualquer→Qualquer | Suporte não-bloqueante (mais fraco que `ENABLES`) | 1 |
| `ENABLES` | — | Não | Qualquer→Qualquer | Viabilização — sem X, Y não pode acontecer | 2 |
| `USED_WITH` | **Sim** | Não | Tool↔Tool | Ferramentas companheiras (ex.: SIGEO ↔ SEST TR) | 4 |

### Família 11 — Fluxo de processo (2 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `PRECEDED_BY` | — | Sim | Process→Process | Sequência temporal — Y deve ocorrer antes de X | 1 |
| `PERFORMED_BY` | — | Não | Process→{Tool,Department} | Processo é executado por agente/ferramenta | 2 |

### Família 12 — Documento / Conformidade (2 verbos)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `IS_INPUT_FOR` | — | Não | Document→Process | Documento alimenta processo (ex.: QPG é input para Laudo Geomecânico) | 5 |
| `FORMALIZES` | — | Não | Document→{Process,Property} | Documento formaliza conceito ou política (use `edge_note='conformidade'` para `SATISFIES`) | 2 |

### Família 13 — Risco (1 verbo)

| Canônico | Sim. | Trans. | Domínio→Alcance | Definição | Atual |
|---|:---:|:---:|---|---|---:|
| `IS_RISK_FOR` | — | Não | Risk→Process | Risco operacional para um processo | 1 |

---

## Tabela de migração — 66 verbos atuais → 31 canônicos

### Mantidos sem mudança (16 verbos · 118 arestas)

`IS_PART_OF`, `CONTAINS`, `RELATED_TO`, `IS_CALCULATED_FROM`, `COMPUTES`, `ESTIMATES`, `DERIVED_FROM`, `MEASURES`, `CO_MEASURED_WITH`, `MONITORS`, `CALIBRATES`, `CONSTRAINS`, `DEFINES_UPPER_BOUND`, `DEFINES_LOWER_BOUND`, `INFLUENCES`, `MAY_TRIGGER`, `PRODUCES`, `STORAGE_FOR`, `IS_SPECIALIZATION_OF`, `REQUIRES`, `REQUIRES_INPUT`, `GOVERNED_BY`, `SUPPORTS`, `ENABLES`, `USED_WITH`, `PRECEDED_BY`, `PERFORMED_BY`, `IS_INPUT_FOR`, `FORMALIZES`, `IS_RISK_FOR`.

### Mesclados em verbo canônico (15 verbos · 26 arestas — sem mudar direção)

| Verbo atual | Canônico | Justificativa | Arestas |
|---|---|---|---:|
| `IS_COMPONENT_OF` | `IS_PART_OF` | quase-sinônimo de meronimia | 4 (já zero pós-norm) |
| `CONTAINS_FORECAST` | `CONTAINS` | + `edge_note: "forecast"` | 2 |
| `IS_DETERMINED_FROM` | `IS_CALCULATED_FROM` | quase-sinônimo | 1 |
| `COMPUTES_1D` | `COMPUTES` | + `edge_note: "1D"` (dimensão herdada do alvo MEM 1D) | 1 |
| `ALLOWS_ESTIMATION` | `ESTIMATES` | active form | 1 |
| `DETERMINES` | `INFLUENCES` | uso atual é causal genérico | 2 |
| `DETERMINES_DIRECTION` | `INFLUENCES` | + `edge_note: "direção/azimute"` | 2 |
| `CONTROLS` | `INFLUENCES` | uso atual é causal, não governança formal | 1 |
| `MANIPULATES` | `INFLUENCES` | causal genérico | 1 |
| `EXPLOITS` | `INFLUENCES` | causal genérico | 1 |
| `IS_RELATED_TO` | `RELATED_TO` | normalização de grafia | 1 |
| `GENERATES` | `PRODUCES` | quase-sinônimo | 1 |
| `OUTPUTS` | `PRODUCES` | quase-sinônimo | 3 |
| `MANAGED_BY` | `GOVERNED_BY` | quase-sinônimo | 1 |
| `IMPLEMENTED_BY` | `PERFORMED_BY` | quase-sinônimo | 1 |
| `INTERFACES_WITH` | `USED_WITH` | quase-sinônimo | 1 |
| `ANALYZES` | `MONITORS` | quase-sinônimo no contexto operacional | 1 |
| `SATISFIES` | `FORMALIZES` | + `edge_note: "conformidade"` | 1 |
| `REQUIRES_VALIDATION` | `REQUIRES` | + `edge_note: "validação"` | 1 |
| `REQUIRES_KNOWLEDGE` | `REQUIRES` | + `edge_note: "conhecimento prévio"` | 1 |
| `REQUIRES_ANALYSIS` | `REQUIRES` | + `edge_note: "análise"` | 2 |
| `ENABLES_DESIGN` | `ENABLES` | + `edge_note: "design"` | 1 |
| `GOVERNS_UPDATE` | `GOVERNED_BY` (inverso) | + `edge_note: "ciclo de atualização"` | 1 |

### Direção invertida (15 verbos · 23 arestas — origem e alvo trocam)

| Verbo atual | Canônico | Direção | Arestas |
|---|---|---|---:|
| `MEASURED_BY` | `MEASURES` | grandeza→método ⇒ método→grandeza | 1 |
| `OBTAINED_BY` | `MEASURES` | grandeza→método ⇒ método→grandeza | 1 |
| `IS_DETERMINED_BY` | `MEASURES` | grandeza→método ⇒ método→grandeza | 1 |
| `IS_CALIBRATED_BY` | `CALIBRATES` | objeto→agente ⇒ agente→objeto | 1 |
| `INCLUDES` | `IS_PART_OF` | todo→parte ⇒ parte→todo | 5 |
| `IS_USED_TO_CALCULATE` | `IS_CALCULATED_FROM` | insumo→saída ⇒ saída→insumo | 8 |
| `LIMITED_BY` | `CONSTRAINS` | restrito→restritor ⇒ restritor→restrito | 1 |
| `MUST_STAY_IN` | `CONSTRAINS` | restrito→restritor ⇒ restritor→restrito | 1 |
| `UPPER_BOUND_DEFINED_BY` | `DEFINES_UPPER_BOUND` | janela→limite ⇒ limite→janela | 1 |
| `LOWER_BOUND_DEFINED_BY` | `DEFINES_LOWER_BOUND` | janela→limite ⇒ limite→janela | 2 |
| `OPERATES_ABOVE` | `DEFINES_LOWER_BOUND` | "X opera acima de Y" ⟺ "Y define piso de X" | 1 |
| `TRIGGERED_BY` | `INFLUENCES` | efeito→causa ⇒ causa→efeito | 2 |
| `CONTROLLED_BY` | `INFLUENCES` | controlado→controlador ⇒ controlador→controlado | 1 |
| `DEPENDS_ON` | `INFLUENCED_BY` | dependente→dependência (mantém leitura) | 1 |
| `DETERMINED_BY` | `INFLUENCED_BY` | determinado→determinador (mantém leitura) | 3 |
| `PRODUCED_BY` | `PRODUCES` | produto→produtor ⇒ produtor→produto | 1 |
| `OUTPUT_OF` | `PRODUCES` | saída→fonte ⇒ fonte→saída | 1 |
| `IS_CLASSIFICATION_OF` | `IS_SPECIALIZATION_OF` | inverso | 1 |
| `IS_REQUIRED_BY` | `REQUIRES` | dependência→dependente ⇒ dependente→dependência | 1 |
| `IS_REQUIRED_FOR` | `REQUIRES` | dependência→dependente ⇒ dependente→dependência | 1 |
| `USED_BY` | `REQUIRES` | ferramenta→processo ⇒ processo→ferramenta (process REQUIRES tool) | 1 |
| `COMPLEMENTED_BY` | `USED_WITH` | um→outro ⇒ simétrico (uma direção apenas) | 2 |

---

## Convenções operacionais (após aprovação)

1. **Uma direção por par**: arestas inversas são inferidas pelo SHACL/reasoner. Quem grava manualmente não precisa duplicar.
2. **`edge_note`** (já aprovado em commit `dc1a0fc`): preservar nuance que não cabe no verbo (`"validação"`, `"forecast"`, `"1D"`, `"design"`, etc.).
3. **Verbos simétricos** (`CO_MEASURED_WITH`, `RELATED_TO`, `USED_WITH`): grafar **uma vez** por par, em ordem alfabética dos IDs.
4. **`INFLUENCED_BY` vs `INFLUENCES`**: regra de redação — usar a direção que produz a frase em português mais natural. Quando ambíguo, preferir `INFLUENCES` (active voice).
5. **Validação**: a SHACL Shape 24 será atualizada para enum (`sh:in (...)`) — qualquer verbo fora do enum aprovado vira erro de conformidade.

---

## Plano de implementação após aprovação

| Etapa | Esforço | Saída |
|---|---|---|
| 1. Atualizar SHACL Shape 24 com `sh:in` (enum dos 31 verbos) | 5 min | `data/geolytics-shapes.ttl` |
| 2. Aplicar 49 patches automatizados via script `apply-vocabulary-canonicalization.py` | 10 min | `data/geomechanics-corporate.json` atualizado |
| 3. Re-rodar SHACL + 10 testes regressão | 1 min | `✓ CONFORME` |
| 4. Re-rodar `generate.js` + commit | 5 min | RAG corpus atualizado |
| 5. Adicionar `meta.schema_policy.canonical_relation_enum` com tabela completa | 5 min | Documentação inline para futuros backfills |
| **Total** | **~30 min** | 1 commit |

Idempotente — re-rodar o script com banco já canonicalizado é no-op.

---

## Formulário de aprovação

**Aprovação global da proposta:**
- ( ) Aprovo as 13 famílias e os 31 verbos canônicos como apresentado
- ( ) Aprovo com ressalvas (preencher abaixo)
- ( ) Não aprovo — propor alternativa

**Itens com possível controvérsia (marcar conforme decisão):**

1. **`MAY_TRIGGER` permanece distinto de `INFLUENCES`?**
   ( ) Sim, manter — preserva incerteza epistemológica
   ( ) Não, mesclar em `INFLUENCES` + `edge_note: "potencial"`

2. **`CONTAINS` permanece distinto de `IS_PART_OF`?**
   ( ) Sim, manter — Document↔Property é diferente de meronimia hierárquica
   ( ) Não, unificar tudo em `IS_PART_OF`

3. **`STORAGE_FOR` permanece distinto de `PRODUCES`?**
   ( ) Sim, manter — armazenar ≠ produzir
   ( ) Não, mesclar em `PRODUCES` + `edge_note: "armazenamento"`

4. **`SUPPORTS` vs `ENABLES` — manter distinção?**
   ( ) Sim, distintos — `SUPPORTS` é fraco, `ENABLES` é forte
   ( ) Não, unificar em `SUPPORTS`

5. **`INFLUENCED_BY` permanece como verbo separado, ou tudo gira para `INFLUENCES` (active voice)?**
   ( ) Manter os dois (legibilidade)
   ( ) Apenas `INFLUENCES`; consumidores invertem na query

**Verbos novos a considerar (não há no enum proposto):**
( ) Adicionar `OWNED_BY` (governança — quem é dono operacional, ≠ `GOVERNED_BY` que é regulatório)
( ) Adicionar `STORED_IN` (inverso explícito de `STORAGE_FOR`)
( ) Outro: _______________

**Comentários livres:**
```


```

---

## Próximos passos

Após aprovação, abro **um PR único** com:
- Atualização da SHACL Shape 24 (enum sh:in)
- Script `apply-vocabulary-canonicalization-2026-05-02.py` (idempotente)
- 49 arestas reescritas (118 mantidas, 26 mescladas, 23 invertidas)
- `meta.schema_policy.canonical_relation_enum` com a tabela completa
- Atualização de `docs/GEOMECHANICS.md` com a tabela
- Atualização do RAG corpus

Tempo estimado total: ~30 min após o "vai".
