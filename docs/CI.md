# CI architecture

The CI is split into focused workflows that run in parallel and use
`paths:` filters so they only fire when relevant files change.

## Workflows

| Workflow | Triggers on | What it does |
|---|---|---|
| `lint.yml` | `**/*.py`, `**/*.js`, `**/*.ts` | Syntax check (Node + Python) and Ruff lint+format. |
| `test-node.yml` | `scripts/`, `tests/`, `data/`, `api/`, `package*.json` | Runs `node --test tests/validator.test.js` and verifies regen reproducibility. |
| `test-python.yml` | `python/**` | Runs `pytest python/tests/` against Python 3.10/3.11/3.12 with Codecov upload. |
| `test-langgraph.yml` | `examples/langgraph-agent/**` | Runs the LangGraph agent test suite (offline, no embeddings). |
| `validate-ontology.yml` | `data/`, `scripts/validate-shacl*` | SHACL validation + entity-graph diff comment on PRs. |
| `eval.yml` | `eval/`, `data/` | Runs offline eval (vector_only + graphrag_validator) and checks regression vs. baseline. |
| `mcp.yml` | `mcp/geobrain-mcp/**` | TypeScript type-check for the MCP server. |
| `pre-commit.yml` | all PRs | Runs `pre-commit run --all-files` (ruff, prettier, hooks). |
| `release.yml` | tag push | Builds and publishes the Python package. |

All workflows use `concurrency` groups to cancel superseded runs.

## Required status checks (recommended ruleset)

Configure on `main` branch protection (Settings → Branches → Branch protection rules):

- `Lint / Syntax check`
- `Lint / Ruff (Python lint + format)`
- `Test (Python) / pytest (Python 3.11)`
- `Pre-commit / pre-commit run --all-files`

Plus, when relevant paths are touched:
- `Test (Node) / Node tests + regen`
- `Validate ontology / SHACL validation`
- `MCP build / TypeScript build`

## Adding a new workflow

1. One workflow per concern. Don't accrete jobs to existing files.
2. Always add a `concurrency:` group.
3. Use `paths:` filters on `pull_request` and `push` to skip irrelevant runs.
4. Cache pip with `cache-dependency-path` pointing at the manifest used.
5. Document the workflow in this file.

## Local mirror of CI

```bash
# Lint
ruff check . --config python/pyproject.toml
ruff format --check . --config python/pyproject.toml

# Python tests
pip install -e "python/[graph,rag,validator,dev]"
pytest python/tests/ --cov=geobrain

# Node tests
node --test tests/validator.test.js

# SHACL
pip install -e "python/[validator]"
python scripts/validate-shacl.py

# MCP
cd mcp/geobrain-mcp && npm ci && npx tsc --noEmit

# Pre-commit
pre-commit run --all-files
```
