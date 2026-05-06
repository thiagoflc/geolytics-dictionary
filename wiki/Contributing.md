# Contributing

Como contribuir com termos, entidades, relações, shapes ou código. O fluxo é o mesmo de qualquer projeto open-source GitHub, com algumas convenções específicas pela natureza ontológica.

📁 Documento técnico complementar: [docs/CONTRIBUTING.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/docs/CONTRIBUTING.md)
📁 Código de conduta: [CODE_OF_CONDUCT.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/CODE_OF_CONDUCT.md)

---

## Antes de começar

1. **Issue primeiro** — abra issue descrevendo a contribuição. Discutimos escopo antes de você gastar tempo.
2. **Fork** o repositório.
3. **Branch** descritivo: `feat/anp-pad-enrichment`, `fix/spe-prms-validator`, `docs/wiki-tour`.

---

## Setup local

```bash
git clone https://github.com/SEU_USUARIO/geolytics-dictionary.git
cd geolytics-dictionary

# Pre-commit hooks (Prettier, eslint, Black, markdownlint)
pip install pre-commit && pre-commit install

# Node deps (para ETL)
node --version  # ≥ 18

# Python deps (para SHACL + tests)
pip install -r scripts/requirements.txt
pip install -e python/[graph,rag]
```

---

## Princípio: edite a fonte, não o gerado

Quase tudo em `data/`, `api/v1/`, `ai/` é **gerado**. Não edite à mão.

| Quero adicionar…             | Edite                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Um termo ANP                  | constante `GLOSSARY` em [`scripts/generate.js`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/scripts/generate.js) |
| Uma entidade no grafo         | constantes `ENTITY_NODES` e `EDGES` em `scripts/generate.js`                                    |
| Uma classe ontopetro          | [`scripts/ontopetro-data.js`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/scripts/ontopetro-data.js) |
| Uma sigla                     | [`scripts/acronyms-source.txt`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/scripts/acronyms-source.txt) |
| Um alinhamento SWEET           | [`data/sweet-alignment.json`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/sweet-alignment.json) (excepcional — JSON editado direto) |
| Uma SHACL shape               | adicionada via geração declarativa em `generate.js`; ver [docs/SHACL.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/docs/SHACL.md) |
| Uma regra do Validator        | [`scripts/semantic-validator.js`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/scripts/semantic-validator.js) |

Após editar, **sempre** rode:
```bash
node scripts/generate.js
node scripts/build-ontology-doc.js
```

---

## Adicionando um termo ANP

```js
// scripts/generate.js — constante GLOSSARY
{
  id: 'meu-termo',
  label: 'Meu Termo (ANP)',
  description: 'Definição completa, com referência normativa.',
  layer: 'L5',
  geocoverage: ['L5'],
  anp_normative: ['Lei 9.478/1997 art. 26', 'Portaria ANP 115/1999'],
  synonyms: ['my-term (en)'],
  petrokgraph_uri: null,
  osdu_kind: null,
}
```

Checklist:
- [ ] `id` em kebab-case e único.
- [ ] `description` em PT-BR, com referência normativa.
- [ ] `geocoverage: ['L5']` se exclusivamente brasileiro.
- [ ] Cross-URIs preenchidas se houver equivalente em outras camadas.
- [ ] `synonyms` para variações PT/EN.

---

## Adicionando uma entidade ao grafo

```js
// scripts/generate.js — constante ENTITY_NODES
{
  id: 'minha-entidade',
  label: 'Minha Entidade',
  type: 'Operational',  // ou Geological/Contractual/Actor/Equipment/Instrument/Analytical
  description: 'O que é e por que existe.',
  geocoverage: ['L4', 'L5'],
  petrokgraph_uri: 'https://petrokgraph.puc-rio.br/ontology#MinhaEntidade',
  osdu_kind: 'osdu:reference-data--MinhaEntidade:1.0.0',
}
```

Adicione relações em `EDGES`:

```js
{ from: 'minha-entidade', to: 'anp', rel: 'governed_by' },
{ from: 'minha-entidade', to: 'bacia-sedimentar', rel: 'located_in' },
```

Checklist:
- [ ] `type` correto (importante para SHACL).
- [ ] `relations[].to` resolve para algum nó existente.
- [ ] `geocoverage` honesto.
- [ ] Sem duplicação semântica (verifique sinônimos).

---

## Adicionando uma sigla

```
# scripts/acronyms-source.txt
PAD;Plano de Avaliação de Descoberta;L5;Instrumento contratual ANP
PAD;Drilling Pad;L4;Plataforma física de perfuração
PAD;Pulsed Amplitude Detector;L4;Instrumento físico
```

Formato: `sigla;expansão;layer;contexto`

Após:
```bash
node scripts/build-acronyms.js
node scripts/generate.js
```

---

## Adicionando uma regra do Validator

Edite [`scripts/semantic-validator.js`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/scripts/semantic-validator.js):

```js
function checkMyRule(text, context) {
  if (/regra que dispara X/.test(text)) {
    return {
      rule: 'MY_NEW_RULE',
      severity: 'warning',  // ou 'error', 'info'
      evidence: 'trecho extraído',
      suggested_fix: 'O que sugerir',
      source_layer: 'L4-MY-STANDARD',
    };
  }
  return null;
}

const RULES = [checkSpePrms, /* ... */, checkMyRule];
```

Adicione teste em [`tests/validator.test.js`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/tests/validator.test.js):

```js
test('MY_NEW_RULE catches X', () => {
  const r = validate('texto que dispara X');
  assert.strictEqual(r.violations[0].rule, 'MY_NEW_RULE');
});
```

Rode:
```bash
node --test tests/validator.test.js
node scripts/generate.js  # atualiza api/v1/validate-rules.json
```

---

## Adicionando uma SHACL shape

Em geral, shapes são **geradas** declarativamente em `generate.js`. Para adicionar manualmente um caso especial:

1. Edite [`data/geolytics-shapes.ttl`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/data/geolytics-shapes.ttl).
2. Rode `python scripts/validate-shacl.py` localmente.
3. Atualize baseline em [`tests/test_shacl_warnings_baseline.py`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/tests/test_shacl_warnings_baseline.py) se mudar contagem de warnings.

Detalhes: [[SHACL Validation]] e [docs/SHACL.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/docs/SHACL.md).

---

## Antes de abrir o PR

```bash
# Regenerar todos os dados
node scripts/generate.js
node scripts/build-ontology-doc.js

# Verificar idempotência (CI fará o mesmo)
bash scripts/check-regen.sh

# Testes Node
node --test tests/

# Testes Python
pytest tests/ -v

# SHACL
python scripts/validate-shacl.py

# Lint
pre-commit run --all-files
```

Tudo verde → PR pronto.

---

## Estrutura do PR

Use o template:

```markdown
## Resumo
[1-3 frases sobre o que mudou e por quê]

## Tipo
- [ ] Termo / entidade nova
- [ ] Crosswalk
- [ ] Regra do Validator
- [ ] SHACL shape
- [ ] Documentação
- [ ] Refactor / build
- [ ] Outro: ...

## Checklist
- [ ] Editei a fonte (não o gerado)
- [ ] Rodei `node scripts/generate.js`
- [ ] Rodei testes (Node + Python)
- [ ] Atualizei `docs/` se necessário
- [ ] Atualizei a [[Wiki]] se necessário (`wiki/*.md`)
- [ ] Sem dangling references
- [ ] CI passou

## Test plan
[O que rodei manualmente para verificar]
```

---

## Convenções de commit

Seguimos [Conventional Commits](https://www.conventionalcommits.org):

```
feat(anp): adiciona termo "Cessão Onerosa" com normative Lei 12.276/2010
fix(validator): corrige falso-positivo de SPE_PRMS em "1Petropolis"
docs(wiki): cria página Use Cases
chore(deps): bump pyshacl 0.20 → 0.21
refactor(scripts): extrai ttl-serializer para módulo
```

Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `style`.

Escopo (entre parênteses) é opcional mas recomendado: `anp`, `osdu`, `geomec`, `wiki`, `mcp`, `python`, etc.

---

## Republicando a Wiki

A Wiki vive em **branch separado** (`<repo>.wiki.git`). Para republicar após edição em `wiki/`:

```bash
bash wiki/publish.sh
```

Veja [`wiki/README.md`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/wiki/README.md) para detalhes.

---

## Tipos de contribuição valorizados

- 🟢 **Termos ANP enriquecidos** com referência normativa precisa
- 🟢 **Crosswalks bilaterais** (especialmente CGI↔OSDU, ANP↔OSDU)
- 🟢 **Regras de validador** baseadas em casos reais de erro de LLM
- 🟢 **Queries Cypher** comentadas em PT-BR para `docs/queries/`
- 🟢 **Notebooks didáticos** para `notebooks/`
- 🟢 **Testes que falham hoje** (regression targets)
- 🟢 **Tradução** PT ↔ EN dos system prompts

---

## Tipos de contribuição **não** aceitos

- ❌ Editar JSON gerado em `data/`/`api/`/`ai/` à mão
- ❌ Adicionar dependências sem justificativa (ETL é Node stdlib only)
- ❌ Termos sem fonte autoritativa (ex.: "achei no LinkedIn")
- ❌ Quebra de retro-compatibilidade sem version bump
- ❌ PRs sem testes
- ❌ Conteúdo não-livre (pode contaminar licença CC-BY)

---

## Reconhecimento

Contribuidores aparecem automaticamente em [GitHub Contributors](https://github.com/thiagoflc/geolytics-dictionary/graphs/contributors). Para citação acadêmica formal, abra issue.

---

## Onde tirar dúvidas

- 💬 **GitHub Discussions** — dúvidas conceituais, RFC informais
- 🐛 **GitHub Issues** — bugs, propostas concretas
- 📧 **Email do mantenedor** (perfil GitHub) — colaborações acadêmicas

---

## Licença

Ao abrir um PR você concorda em licenciar suas contribuições sob:
- **MIT** (código)
- **CC-BY 4.0** (dados / documentação)

O código de conduta em [CODE_OF_CONDUCT.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/CODE_OF_CONDUCT.md) se aplica a toda interação.

---

> **Próximo:** ler [[Architecture|a arquitetura]] para entender onde sua contribuição vai morar, ou ver [[FAQ]].
