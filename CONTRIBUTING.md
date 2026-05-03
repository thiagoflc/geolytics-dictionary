# Contributing to GeoBrain

Obrigado por considerar contribuir! Este documento explica o fluxo de trabalho.

## Code of Conduct

Este projeto adota o [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Ao participar, você concorda em segui-lo.

## Como contribuir

### Reportando bugs

Use o template de issue **Bug report**. Inclua:

- Versão / commit do GeoBrain.
- Passos para reproduzir.
- Comportamento esperado vs. observado.
- Logs ou trechos de código relevantes.

### Propondo features

Use o template **Feature request**. Para mudanças grandes (novas camadas ontológicas, novos validadores SHACL, breaking changes na API), abra uma issue de discussão **antes** de codar.

### Pull Requests

1. Faça fork e crie uma branch a partir de `main`:
   ```
   git checkout -b feat/minha-feature
   ```
2. Siga as convenções de código (ver abaixo).
3. Adicione/atualize testes em `python/tests/` ou `tests/`.
4. Rode localmente:
   ```
   pre-commit run --all-files
   pytest python/tests
   node --test tests/validator.test.js
   node scripts/generate.js  # regen deve ser reproduzível
   ```
5. Commits seguem [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` nova funcionalidade
   - `fix:` correção de bug
   - `docs:` documentação
   - `chore:` tarefas de manutenção
   - `refactor:` refatoração sem mudança de comportamento
   - `test:` adição/correção de testes
   - `ci:` mudanças em CI/CD
6. Abra o PR usando o template. Descreva **o quê** e **por quê** (não só o como).

### Setup local

**Python (SDK em `python/`):**

```
cd python
pip install -e ".[graph,rag,validator,dev]"
```

**Node (scripts + MCP):**

```
cd mcp/geobrain-mcp && npm ci
```

**Pre-commit hooks:**

```
pip install pre-commit
pre-commit install
```

## Convenções de código

- **Python**: formatado com `ruff format`, lint com `ruff check`. Type hints obrigatórios em funções públicas.
- **JavaScript**: formatado com `prettier`. Sem `var`, preferir `const`/`let`.
- **Markdown**: linhas até ~120 colunas, formatado com `prettier`.
- **Commits**: imperativo, < 72 chars no título.

## Adicionando uma nova entidade ao grafo

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Em resumo:

1. Adicione o termo em `data/<categoria>.json`.
2. Atualize relações em `data/relations.json` se necessário.
3. Rode `node scripts/generate.js`.
4. Verifique o snapshot em `api/v1/`.
5. Adicione validador SHACL se o termo tem invariantes estruturais.

## Migrações de dados

Scripts one-shot vão em `scripts/migrations/<YYYY-MM-DD>/` com README explicativo. Após aplicados em todos os ambientes, podem ser removidos em PR dedicado.

## Reportando vulnerabilidades

**Não abra issues públicas para falhas de segurança.** Ver [SECURITY.md](SECURITY.md).
