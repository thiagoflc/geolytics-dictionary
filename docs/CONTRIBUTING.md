# Guia de contribuicao — adicionando conceitos novos

Este guia descreve, passo a passo, como contribuidores podem **adicionar conceitos novos** ao dicionario: termos do glossario ANP, entidades do grafo, termos geologicos estendidos, alinhamentos com camadas externas (Petro KGraph, OSDU, WITSML/PRODML, GSO, SWEET) e shapes SHACL.

A regra de ouro do projeto: **dados entram em arquivos-fonte versionados em codigo (`scripts/*.js`) e os artefatos publicos em `data/`, `api/v1/`, `ai/` sao sempre gerados pela pipeline ETL** — nunca edite os JSON em `data/` diretamente.

---

## 1. Antes de comecar — escolha a categoria certa

Cada conceito novo cai em uma (ou mais) das categorias abaixo. Escolha a errada e o conceito nao aparecera nos artefatos certos (TTL, RAG, MCP, validador).

| Categoria | Quando usar | Onde editar |
|---|---|---|
| **Termo do glossario ANP** | Conceito definido por norma ANP/Lei 9.478 com fonte oficial | `GLOSSARIO` em [scripts/generate.js](../scripts/generate.js) |
| **Entidade do grafo** (no) | Conceito que se relaciona com outros nos via `EDGES` | `ENTITY_NODES` em [scripts/generate.js](../scripts/generate.js) |
| **Aresta do grafo** (relacao) | Liga duas entidades ja existentes | `EDGES` em [scripts/generate.js](../scripts/generate.js) |
| **Termo geologico estendido** | Conceito geologico generico (formacao, reservatorio, sistema deposicional) que extrapola ANP | `EXTENDED_TERMS` em [scripts/ontology-alignment.js](../scripts/ontology-alignment.js) |
| **Alinhamento de camadas** | Mapear termo existente para Petro KGraph / OSDU / camadas L1–L7 | `TERM_ALIGNMENT` ou `ENTITY_ALIGNMENT` em [scripts/ontology-alignment.js](../scripts/ontology-alignment.js) |
| **Modulo ontologico** (classes/propriedades formais) | Modulo OntoPetro novo (geomecanica, sismica, PVT...) | [scripts/ontopetro-data.js](../scripts/ontopetro-data.js) |
| **Crosswalk OSDU extra** | Tipo OSDU sem termo ANP equivalente | [scripts/osdu-extra-nodes.js](../scripts/osdu-extra-nodes.js) |
| **Crosswalk WITSML/PRODML** | Mapear classe XML para `geo:` | [scripts/witsml-to-rdf.js](../scripts/witsml-to-rdf.js) |
| **Sigla** | Acronimo O&G PT/EN | [scripts/acronyms-source.txt](../scripts/acronyms-source.txt) (depois rodar `build-acronyms.js`) |
| **Shape SHACL** | Regra de validacao formal | [data/geolytics-shapes.ttl](../data/geolytics-shapes.ttl) — ver [SHACL.md](SHACL.md) |
| **Regra do validador deterministico** | Restricao sem RDF (ex: SPE-PRMS rejeita "4P") | `RULES` em [scripts/semantic-validator.js](../scripts/semantic-validator.js) |

Em duvida: comece pelo glossario + entidade. Os demais sao especializacoes.

---

## 2. Receita 1 — adicionar termo ANP ao glossario

**Arquivo:** [scripts/generate.js](../scripts/generate.js), constante `GLOSSARIO` (linha ~296).

**Campos obrigatorios:**

```js
{
  id: 'kebab-case-unico',           // estavel, usado como chave em todos os artefatos
  termo: 'Nome em PT-BR',
  categoria: 'geologia' | 'contratos' | 'operacoes' | 'regulatorio' | 'sistemas',
  definicao: 'Texto canonico em PT-BR. Cite a fonte normativa no final da definicao quando relevante.',
  fonte: 'Lei nº 9478/1997' | 'ANP/SEP' | 'ANP/SEP — SIGEP' | 'Resolução ANP nº XXX/AAAA',
  apareceEm: ['pocos-exploratorios', 'blocos-contrato', ...]  // ids de CONJUNTOS onde o termo aparece como coluna
}
```

**Boas praticas:**
- `id` em **kebab-case sem acentos** — e usado em URLs, IRIs RDF e ids do grafo.
- `definicao` deve ser **autocontida** (1–4 frases). Vai virar chunk RAG e card HTML.
- `fonte` deve ser **rastreavel** (lei, resolucao, manual ANP). Sem fonte → nao entra.
- Reuse `categoria` existente; se for criar nova, atualize tambem [docs/ENTITIES.md](ENTITIES.md).

**Se o termo tiver alinhamento com camadas externas**, adicione tambem entrada em `TERM_ALIGNMENT` em [scripts/ontology-alignment.js](../scripts/ontology-alignment.js):

```js
'meu-termo': {
  kg:    '#PetroKGraphFragment',                                  // ou null
  osdu:  'opendes:osdu:master-data--XYZ:1.0.0',                   // ou null
  layers: ['layer1','layer2','layer3','layer4','layer5'],         // sempre obrigatorio
}
```

Se o termo aparece em datasets ANP, adicione-o tambem ao `colunas[]` do dataset relevante em `CONJUNTOS`.

---

## 3. Receita 2 — adicionar entidade ao grafo (no + arestas)

**Arquivos:** `ENTITY_NODES` (linha ~601) e `EDGES` (linha ~699) em [scripts/generate.js](../scripts/generate.js).

### 3.1 No

```js
{
  id: 'meu-conceito',
  label: 'Meu Conceito',
  label_en: 'My Concept',
  type: 'operational' | 'contractual' | 'actor' | 'instrument'
       | 'geological' | 'equipment' | 'analytical',
  glossId: 'meu-conceito',          // id em GLOSSARIO, se houver. Use null se for sigla pura.
  extendedId: null,                 // id em EXTENDED_TERMS, se houver
  // Use APENAS quando glossId === null (no sem termo de glossario):
  definicaoOverride: 'Definicao curta (1–3 frases).',
  fonte: 'Siglário O&G / API'
}
```

Regras:
- Se `glossId` aponta para `GLOSSARIO`, **nao** preencha `definicaoOverride` — a definicao sai do glossario.
- `type` controla cor, tamanho do no e categorizacao no MCP/RAG. Nao invente novos `type` sem antes atualizar `ONTOLOGY_TYPES`, `COLORS` e `SIZES` (linha ~553–598).
- Para conceito **sem fonte ANP** (siglas O&G, equipamentos, atores ambientais), use `glossId: null` + `definicaoOverride` + `fonte` rastreavel.

### 3.2 Arestas (relacoes)

```js
{
  source: 'meu-conceito',
  target: 'entidade-existente',
  relation: 'verb_in_snake_case',         // ex: drilled_in, governed_by, requires_report
  relation_label: 'verbo em PT-BR',       // ex: 'perfurado em'
  style: 'solid' | 'dashed'               // solid = obrigatorio/forte, dashed = opcional/fraco
}
```

Padroes do projeto:
- **`relation`** — verbo passivo em ingles, snake_case. Reuse vocabulario existente (`located_in`, `operated_by`, `governed_by`, `evaluates`, `may_yield`, `originates`, `installed_on`...) antes de criar verbo novo.
- **`style: 'solid'`** para relacoes obrigatorias por norma ou estruturais. **`'dashed'`** para condicionais (ex: `pad → declaracao-comercialidade` e `may_yield`, dashed).
- Modele em **ambas direcoes** so se for semanticamente assimetrico — caso contrario, uma aresta basta.

---

## 4. Receita 3 — termo geologico estendido (fora do escopo ANP)

**Arquivo:** [scripts/ontology-alignment.js](../scripts/ontology-alignment.js), constante `EXTENDED_TERMS` (linha ~118).

```js
{
  id: 'kebab-case',
  termo: 'Nome PT',
  termo_en: 'Name EN',
  categoria: 'geologia',
  definicao: 'Definicao alinhada a GeoCore/GeoReservoir/SWEET.',
  legal_source: 'GeoCore (UFRGS/Geosiris)' | 'GeoReservoir (UFRGS)' | 'SWEET (NASA/ESIPFed)',
  apareceEm: [],
  petrokgraph_uri: `${PETROKGRAPH_BASE}#FragmentName` | null,
  osdu_kind: 'opendes:osdu:master-data--XXX:1.0.0' | null,
  geocoverage: ['layer1','layer2','layer3','layer4'],
  synonyms_pt: ['sinonimo 1', 'sinonimo 2'],
  synonyms_en: ['synonym 1'],
  examples: ['Exemplo concreto brasileiro 1', 'Exemplo 2'],
}
```

Termos estendidos viram nos do grafo se voce adicionar tambem entrada em `ENTITY_NODES` com `extendedId: 'meu-id'`. Veja `reservatorio`, `formacao`, `sistema-deposicional` como exemplos.

---

## 5. Receita 4 — sigla nova

**Arquivo:** [scripts/acronyms-source.txt](../scripts/acronyms-source.txt). Formato linha a linha:

```
SIGLA | Expansao em PT (en: English Expansion) | categoria | fonte
```

Categorias canonicas: `equipamento`, `operacional`, `geologia`, `regulatorio`, `petrofisica`, `geomecanica`, `sismica`, `quimica`, `seguranca`, `producao`. Veja o arquivo para o conjunto completo.

Apos editar, regere o JSON:

```bash
node scripts/build-acronyms.js
```

Isto atualiza [data/acronyms.json](../data/acronyms.json). Em seguida rode o pipeline principal.

---

## 6. Receita 5 — shape SHACL

Veja [SHACL.md](SHACL.md) para o esquema completo. Resumo do fluxo:

1. Edite [data/geolytics-shapes.ttl](../data/geolytics-shapes.ttl) — adicione `sh:NodeShape` para a classe-alvo.
2. Adicione caso de teste em [tests/](../tests/) ou `eval/` para a propriedade que deve falhar.
3. Rode `python scripts/validate-shacl.py` localmente.
4. Atualize [data/geolytics-vocab.ttl](../data/geolytics-vocab.ttl) se a shape introduzir vocabulario novo (`geo:` IRI).

---

## 7. Receita 6 — regra do validador deterministico

Para validar afirmacoes em texto livre (ex: "Reserva 4P do Campo de Buzios" → SPE-PRMS so reconhece 1P/2P/3P), adicione regra em `RULES` em [scripts/semantic-validator.js](../scripts/semantic-validator.js).

```js
{
  id: 'SPE_PRMS_INVALID_CATEGORY',
  pattern: /\b4P\b/i,
  severity: 'error',
  message: 'SPE-PRMS reconhece apenas 1P, 2P, 3P. "4P" nao existe na hierarquia formal.',
  source: 'SPE-PRMS 2018'
}
```

Adicione caso de teste em [tests/validator.test.js](../tests/validator.test.js).

---

## 8. Pipeline de geracao — gerando os artefatos

Apos qualquer edicao em `scripts/`, regere os artefatos:

```bash
# Pipeline principal — regenera data/, api/v1/, ai/
node scripts/generate.js

# Doc de classes/propriedades formais (so se mexeu em ontopetro-data.js)
node scripts/build-ontology-doc.js

# Manifest de regras de validacao
node scripts/build-validate-manifest.js
```

A pipeline grava (entre outros): `data/glossary.json`, `data/entity-graph.json`, `data/full.json`, `data/geolytics.ttl`, `data/ontopetro.json`, `api/v1/*.json`, `ai/rag-corpus.jsonl`, `ai/system-prompt-*.md`, `ai/ontology-map.json`. Todos derivados — **nunca edite a mao**.

### 8.1 Dry-run

```bash
node scripts/generate.js --dry-run
```

Mostra o que seria escrito sem tocar no disco. Util para revisar tamanho dos artefatos antes de commitar.

### 8.2 Validacao do diff

```bash
bash scripts/check-regen.sh
```

Verifica se um `git diff` aparece apos rodar a pipeline — se sim, voce esqueceu de commitar artefatos regenerados, ou alguem editou `data/` a mao.

---

## 9. Validacao — antes de abrir o PR

```bash
# 1. SHACL formal (requer Python)
pip install -r scripts/requirements.txt
python scripts/validate-shacl.py

# 2. Validador deterministico
node scripts/validate-cli.js "frase de teste mencionando seu conceito"

# 3. Testes unitarios
node --test tests/

# 4. Confere se o grafo nao quebrou (Neo4j opcional)
node scripts/build-neo4j.js
docker compose up -d
# abra http://localhost:7474 e rode uma query do docs/queries/
```

PRs com SHACL vermelho ou testes falhando nao serao aceitos.

---

## 10. Checklist final

Antes do commit:

- [ ] `id` em kebab-case sem acentos, unico em todo o repositorio
- [ ] `fonte` rastreavel a norma/manual/paper
- [ ] `categoria` reusa valor existente (ou justifica novo na descricao do PR)
- [ ] Se virou no do grafo: tem ao menos uma aresta entrando ou saindo
- [ ] Se mapeou camadas: `layers` correto e `petrokgraph_uri`/`osdu_kind` validados
- [ ] `node scripts/generate.js` rodou limpo, artefatos regenerados commitados
- [ ] `bash scripts/check-regen.sh` nao acusa diff sujo
- [ ] `python scripts/validate-shacl.py` passa
- [ ] `node --test tests/` passa
- [ ] Atualizou doc relevante em `docs/` quando o conceito merece prosa (ex: novo modulo P2.x → `ARCHITECTURE.md`, `INDEX.md`)

---

## 11. Convencoes de PR

- **Titulo**: `feat(glossary): adiciona termo X` / `feat(graph): adiciona aresta Y → Z` / `feat(crosswalk): mapeia OSDU W para geo:V`
- **Descricao**: cite a fonte normativa, justifique escolha de `type`/`categoria`, anexe trecho do grafo afetado se relevante.
- **Tamanho**: prefira PRs pequenos — 1 conceito ou 1 modulo por PR. Pacotes grandes sao mais dificeis de revisar por especialistas de dominio.

---

## 12. Quando nao adicionar

- **Conceitos genericos sem fonte**. Se nao ha lei, resolucao, norma tecnica, paper revisado por pares ou manual ANP — nao entra. O dicionario e regulatorio, nao opinativo.
- **Sinonimos puros de termos existentes**. Use `synonyms_pt`/`synonyms_en` em `EXTENDED_TERMS` ou no enriquecimento, nao crie um termo novo.
- **Tags de produto Petrobras internas**. O dicionario e publico; conceitos corporativos vao em [systems.json](../data/systems.json) com escopo claramente proprietario.
- **Conceitos OSDU/WITSML que ja existem nos crosswalks**. Confira [data/osdu-mapping.json](../data/osdu-mapping.json) e [data/witsml-rdf-crosswalk.json](../data/witsml-rdf-crosswalk.json) antes de propor.

---

## Referencias

- Arquitetura geral: [ARCHITECTURE.md](ARCHITECTURE.md)
- Modelo de entidades: [ENTITIES.md](ENTITIES.md)
- Padroes externos: [EXTERNAL_STANDARDS.md](EXTERNAL_STANDARDS.md)
- SHACL: [SHACL.md](SHACL.md)
- Conceitos brasileiros: [BRAZIL_SPECIFIC.md](BRAZIL_SPECIFIC.md)
- Indice completo: [INDEX.md](INDEX.md)
