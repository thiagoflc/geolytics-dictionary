# Wiki source — `wiki/`

Esta pasta contém o **conteúdo-fonte** da Wiki do GeoBrain. Os arquivos `.md` aqui são publicados em https://github.com/thiagoflc/geolytics-dictionary/wiki via o script [`publish.sh`](publish.sh).

> **Por que vivem aqui (e não direto no Wiki repo)?**
> A Wiki do GitHub é um repositório separado (`<repo>.wiki.git`) que não tem PRs, code review, CI, ou histórico vinculado ao código. Mantendo as fontes aqui:
> - Mudanças passam por PR (review obrigatório)
> - Diff aparece junto com o código relacionado
> - Markdownlint via pre-commit
> - Possível bumpar Wiki simultaneamente ao changelog

---

## Estrutura

```
wiki/
├── Home.md                       # Landing page (https://github.com/.../wiki)
├── _Sidebar.md                   # Sidebar de navegação (esquerda)
├── _Footer.md                    # Footer global
├── Architecture.md               # /Architecture
├── Contributing.md
├── Data-Files.md
├── ETL-Pipeline.md
├── FAQ.md
├── Getting-Started.md
├── Glossary.md
├── Knowledge-Graph.md
├── LangGraph-Agent.md
├── MCP-Server.md
├── Neo4j-Setup.md
├── Python-Package.md
├── RAG-Corpus.md
├── REST-API.md
├── Semantic-Layers.md
├── Semantic-Validator.md
├── SHACL-Validation.md
├── SPE-Volve-Integration.md
├── Use-Cases.md
├── What-is-GeoBrain.md
├── publish.sh                    # Script de publicação
└── README.md                     # Este arquivo
```

### Convenções de nomeação

- **`Home.md`**, **`_Sidebar.md`**, **`_Footer.md`** — nomes especiais reconhecidos pelo GitHub Wiki.
- **Páginas regulares** usam `Title-With-Hyphens.md`. URL será `/wiki/Title-With-Hyphens`.
- **Wiki links** usam sintaxe `[[Page Name]]` ou `[[Display Text|Page Name]]`. GitHub resolve para o nome do arquivo (sem extensão).

---

## Como editar

1. **Abra um PR** alterando arquivos em `wiki/`.
2. Pre-commit roda markdownlint, Prettier, etc.
3. Após merge no `main`, rode (ou peça a alguém com acesso) `bash wiki/publish.sh`.
4. Verifique resultado em https://github.com/thiagoflc/geolytics-dictionary/wiki.

> 💡 Para preview local sem publicar:
> ```bash
> bash wiki/publish.sh --dry-run
> ```

---

## Publicação via script

### Pré-requisitos

A Wiki **deve existir** antes do script funcionar. GitHub não permite clone do `.wiki.git` se nenhuma página foi criada na UI ainda.

**Bootstrap da primeira vez:**
1. Acesse https://github.com/thiagoflc/geolytics-dictionary/wiki
2. Clique em **"Create the first page"**
3. Salve qualquer placeholder (ex.: "Initialized")
4. Agora rode `bash wiki/publish.sh` — vai sobrescrever com o conteúdo real

### Fluxo

```bash
bash wiki/publish.sh
```

O script:
1. Clona `<repo>.wiki.git` em diretório temporário
2. Copia todo `wiki/*.md` para lá
3. Faz commit e push se houver diff
4. Limpa diretório temporário

### Autenticação

- **HTTPS** (padrão): usa credenciais do `gh` CLI ou Git Credential Manager.
- **SSH**: edite `WIKI_REMOTE` em `publish.sh` para `git@github.com:thiagoflc/geolytics-dictionary.wiki.git`.

---

## Como adicionar uma nova página

1. Crie `wiki/Nova-Pagina.md`.
2. Edite [`_Sidebar.md`](_Sidebar.md) para incluir o link.
3. Atualize [`Home.md`](Home.md) se for página de alto nível.
4. PR + merge + `bash wiki/publish.sh`.

---

## Sintaxe Wiki especial

### Internal links (entre páginas Wiki)

```markdown
[[Architecture]]                 → linka para /Architecture
[[Ver arquitetura|Architecture]] → texto custom
```

### Imagens

GitHub Wiki suporta imagens em duas formas:

```markdown
![alt](https://github.com/thiagoflc/geolytics-dictionary/raw/main/docs/img/diagram.svg)
```

Mantenha imagens em `docs/img/` no repo principal — Wiki referencia via raw URL.

### Mermaid

Funciona nativamente:

```markdown
\`\`\`mermaid
graph TD
  A --> B
\`\`\`
```

### Code blocks com syntax highlight

Funciona como GitHub regular: ```\`\`\`python ... \`\`\````.

---

## Padrões de estilo

- **PT-BR** como idioma default (espelha o README e a comunidade-alvo do projeto).
- **Diagramas Mermaid** quando agregam valor (não para coisa simples).
- **Links para arquivos** sempre como `[arquivo.md](...)` apontando para `main`.
- **Linha numérica** em fontes-chave: `[scripts/generate.js:130](https://github.com/.../scripts/generate.js#L130)`.
- **Tabelas** preferíveis a listas longas para informação tabular.
- **TL;DR** no topo de páginas longas.

---

## Anti-padrões

- ❌ Não copiar conteúdo extenso de `docs/` — link, não duplique.
- ❌ Não criar "página todo" — coloque em issue.
- ❌ Não escrever em primeira pessoa ("eu acho que..."). Escreva impessoal.
- ❌ Não inserir snippets de código sem testá-los — refrigeram em runtime real.
- ❌ Não vincular a branches efêmeros — sempre `main`.

---

## Manutenção

Ao mexer em algo do código, **considere atualizar a Wiki** se:
- Mudou comando de instalação
- Renomeou ferramenta ou módulo
- Adicionou regra do Validator (atualize [[Semantic Validator]])
- Adicionou tool no MCP (atualize [[MCP Server]])
- Mudou estrutura de dados (atualize [[Data Files]] ou [[Knowledge Graph]])

PRs que mudam interface pública sem atualizar Wiki são rejeitados.

---

## Sincronização com `docs/`

Wiki e `docs/` têm escopos diferentes:

| Aspecto             | `wiki/` (esta pasta)                                           | `docs/` (no repo)                                |
| ------------------- | -------------------------------------------------------------- | ------------------------------------------------ |
| **Público**         | Visitantes navegando o GitHub Wiki                              | Devs/pesquisadores que clonaram o repo            |
| **Estilo**          | Didático, alto-nível, com TL;DR                                 | Técnico, denso, exhaustivo                       |
| **Renderização**    | GitHub Wiki (sidebar, footer)                                   | GitHub plain                                      |
| **Atualização**     | Manual via `publish.sh`                                         | Automática (parte do PR)                         |
| **Cross-linking**   | Wiki links `[[Page]]`                                           | Markdown links relativos                         |

Use a Wiki para **explicar conceitos**. Use `docs/` para **referência técnica completa**.

---

> Voltar para [[Home|Wiki Home]] · README do repo: [../README.md](../README.md)
