# FAQ

Perguntas comuns sobre o GeoBrain. Se a sua não estiver aqui, abra uma issue/discussion.

---

## Conceito

### O GeoBrain substitui o RAG vetorial?

**Não.** Ele *complementa.* O agente de referência ([[LangGraph Agent]]) usa **GraphQuery + RAG vetorial + Validator** em conjunto. Cada um cobre falhas dos outros.

### Por que oito camadas? Não é demais?

Cada camada serve um público real:
- **L1 (BFO)** — pesquisadores ontológicos
- **L1b (CGI)** — geocientistas
- **L2 (O3PO)** — academia O&G
- **L3 (Petro KGraph)** — falantes PT-BR
- **L4 (OSDU)** — engenheiros de dados subsuperficiais
- **L5 (ANP)** — reguladores e advogados
- **L6 (Petrobras)** — operadores brasileiros
- **L7 (GSO)** — geólogos estruturais

Sem camadas, mistura tudo em um vocabulário que ninguém reconhece como "seu".

### O grafo precisa de Neo4j?

**Não.** Você pode:
1. Carregar `data/entity-graph.json` em **NetworkX** (Python).
2. Usar o pacote Python `geobrain` (NetworkX por baixo).
3. Subir Neo4j (recomendado para queries multi-hop frequentes).
4. Acessar via REST API estática (`api/v1/`).

### Posso usar para outros países (Argentina, México, Norway)?

**Estrutura sim, conteúdo não direto.** As camadas L1-L4 e L7 são internacionais. L5 (ANP) é específica do Brasil. Para outros reguladores, faria sentido criar:
- L5-AR (Secretaría de Energía)
- L5-MX (CNH)
- L5-NO (NPD)

PRs benvindos. Modelo é replicável.

### Por que PT-BR primeiro?

Porque é o único repositório aberto com cobertura ANP/SIGEP. Inglês é first-class via `synonyms` e `system-prompt-en.md`, mas a fonte de autoridade (ANP) é PT-BR.

---

## Uso prático

### Como faço lookup rápido sem instalar nada?

```bash
curl -s https://thiagoflc.github.io/geobrain/api/v1/terms.json \
  | jq '.[] | select(.id == "bloco")'
```

### O MCP Server funciona em Claude Code (CLI)?

**Sim.** Claude Code suporta MCP servers locais via [config](https://docs.anthropic.com/en/docs/claude-code/mcp). Mesmo JSON do Claude Desktop.

### O agente LangGraph precisa de OpenAI?

**Não.** Suporta:
- `ANTHROPIC_API_KEY` → Claude (Sonnet, Opus)
- `OPENAI_API_KEY` → GPT-4o, GPT-4-turbo
- `LLM_PROVIDER` env var seleciona

`_make_llm()` em `agent.py` é o ponto de troca.

### Posso rodar tudo offline?

Quase tudo:
- ✅ Pacote Python — totalmente offline
- ✅ MCP Server — totalmente offline
- ✅ Neo4j local — totalmente offline
- ❌ Synthesizer (LangGraph) — depende de LLM provider

Para offline LLM, configure `_make_llm()` para usar [Ollama](https://ollama.com).

### Qual o tamanho da base?

- `data/` total: ~6 MB
- `entity-graph.json`: ~1 MB
- `rag-corpus.jsonl`: ~1.7 MB
- 221 nós + 370 relações + 65 SHACL shapes

Cabe num único request HTTP. Cabe em qualquer LLM context > 32k tokens (com chunking).

---

## Validação & SHACL

### Quando usar Semantic Validator vs SHACL?

| Validar…                              | Use                          |
| ------------------------------------- | ---------------------------- |
| Texto natural ("Reserva 4P...")       | Semantic Validator           |
| Estrutura RDF (cardinalidade, types)  | SHACL                        |
| Em runtime (cada turno do agente)     | Semantic Validator           |
| Em CI (build-time)                    | SHACL                        |

### Por que SHACL e não OWL reasoner?

OWL reasoners (Pellet, HermiT) são poderosos mas **lentos** (segundos por query). SHACL é **declarativo** e otimizado para validação estrutural. Em prática, SHACL captura 95% dos erros que importam, com 1% do custo.

### Posso adicionar minha própria regra do Validator?

Sim. Edite `scripts/semantic-validator.js`. Detalhes em [[Semantic Validator]] e [[Contributing]].

---

## Engenharia

### Por que JSON e não banco de dados?

JSON em Git dá:
- Diff legível em PRs
- Reproduzibilidade byte-a-byte
- Sem migrations
- Sem servidor

Banco de dados seria over-engineering para 221 nós. Quando passar de 100k nós, reavaliamos.

### Por que Node.js para o ETL?

Histórico (origem do projeto era um app web). Stdlib Node tem JSON ergonômico. Sem dependências externas → sem `npm install` em CI. Performance suficiente.

### Por que TypeScript no MCP server e Python no LangGraph?

- MCP SDK oficial é TS first.
- LangGraph é Python.

Boundary between worlds: ambos consomem os **mesmos JSONs** em `data/` e o **mesmo corpus** em `ai/`. Schemas equivalentes em TS e Python (verificado em CI).

### Como adiciono uma nova fonte (e.g., COGRESEC, NPD)?

Veja [[ETL Pipeline]] → "Como adicionar uma nova fonte". Resumo: crie módulo `scripts/<minha-fonte>.js`, importe em `generate.js`, adicione `geocoverage`.

### CI quebra com "git diff não-vazio". O que fazer?

Você editou JSON gerado à mão. Reverta `data/`, edite a fonte (`scripts/generate.js`), rode `node scripts/generate.js`, commit ambos.

---

## Licença & uso comercial

### Posso usar comercialmente?

- **Código** (MIT): sim, sem restrição.
- **Dados** (derivados ANP/SEP): uso livre com **atribuição** à fonte original (ANP/SEP).
- **Petrobras 3W** (CC-BY 4.0): atribuir Petrobras + link para dataset original.

### Preciso pagar?

Não. Tudo é open-source.

### Posso embutir no meu produto SaaS?

Sim, contanto que respeite as licenças. Atribuição em rodapé / sobre / docs costuma satisfazer CC-BY.

### Posso publicar no Hugging Face?

Sim. Há intenção de publicar `rag-corpus.jsonl` como dataset público no HF. Veja issue tracker.

---

## Comparações

### GeoBrain vs Petro KGraph (PUC-Rio)?

- **Petro KGraph** (L3): 539 conceitos PT-BR, fortemente acadêmico, hierarquia rica.
- **GeoBrain**: integra Petro KGraph (camada L3) com ANP, OSDU, GSO etc. Foco em validação + agentes IA.

São complementares. GeoBrain referencia PetroKGraph via `petrokgraph_uri` em todo termo aplicável.

### GeoBrain vs OSDU?

- **OSDU**: schema de **dados IT** subsuperficiais (Wellbore.kind, etc.). Foco em integração de pipelines.
- **GeoBrain**: ontologia **conceitual** com agentes/validador. Crosswalks ANP↔OSDU.

GeoBrain ajuda quem precisa **descrever** dados OSDU em PT-BR, ou validar consistência.

### GeoBrain vs SWEET?

- **SWEET (NASA/ESIPFed)**: ontologia genérica de Earth Science.
- **GeoBrain**: específico de E&P brasileiro, com 66 alinhamentos SKOS para SWEET.

Use SWEET para abstração geral, GeoBrain para precisão de domínio.

---

## Performance & escala

### Quanto demora o ETL?

`node scripts/generate.js` em ~3-5 segundos em laptop moderno.

### O Validator é rápido o suficiente para runtime?

Sim. ~0.5 ms por claim típico (< 200 chars). Sem I/O. Sem flutuação.

### Quantos nós o Neo4j aguenta?

Trivial até 100k. O grafo atual (221) tem queries multi-hop em < 20 ms.

### O agente LangGraph aguenta produção?

Latência típica 2-4 segundos. Bottleneck = LLM provider. Validator + GraphQuery + RAG são todos < 100 ms.

---

## Roadmap (perguntas frequentes)

### Vai ter UI web?

[`index.html`](https://github.com/thiagoflc/geolytics-dictionary/blob/main/index.html) e https://thiagoflc.github.io/geobrain já existem. Roadmap inclui versão React com busca facetada.

### Vai ter API GraphQL?

Não há plano imediato. REST estática + Cypher cobrem a maioria dos casos.

### Vai integrar com WITSML 1.4?

Crosswalk WITSML 2.0 já existe. Versão 1.4 está no backlog (issue aberta).

### Vai ter modelo embeddings pré-computado?

Sim, no roadmap. Anthropic, OpenAI e BGE-M3 são os candidatos.

---

## Outras dúvidas

Não encontrou aqui? Tente:

- [docs/INDEX.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/docs/INDEX.md) — documentação técnica completa
- [GitHub Discussions](https://github.com/thiagoflc/geolytics-dictionary/discussions)
- [GitHub Issues](https://github.com/thiagoflc/geolytics-dictionary/issues)
- Email do mantenedor (perfil GitHub)

---

> **Próximo:** [[Glossary|glossário]] de termos do projeto ou voltar à [[Home]].
