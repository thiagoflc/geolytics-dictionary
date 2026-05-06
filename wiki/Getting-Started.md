# Getting Started

Cinco caminhos rápidos, escolha um conforme seu objetivo. Cada um leva ~5 minutos.

---

## 🐍 Caminho 1 — Pacote Python (mais simples)

> Para: notebooks, exploração rápida, scripts de validação.

```bash
pip install "geobrain[graph,rag]"
```

```python
from geolytics_dictionary import Dictionary, KnowledgeGraph, Validator

# Buscar termos
d = Dictionary()
print(d.lookup("Pré-sal")[0].description)

# Explorar grafo
kg = KnowledgeGraph.from_local()
print(kg.shortest_path("poco", "regime-contratual"))

# Validar claim
v = Validator()
report = v.validate("Reserva 4P do Campo de Buzios")
print(report.violations[0].rule)  # SPE_PRMS_INVALID_CATEGORY
```

→ Mais detalhes em [[Python Package]].

---

## 🤖 Caminho 2 — MCP Server em Claude Desktop

> Para: usar o GeoBrain via prompts em Claude Desktop, Cursor, ou Claude Code.

```bash
# 1. Clone e build
git clone https://github.com/thiagoflc/geolytics-dictionary.git
cd geolytics-dictionary/mcp/geobrain-mcp
npm install && npm run build

# 2. Configurar Claude Desktop
# Edite ~/Library/Application Support/Claude/claude_desktop_config.json:
```

```json
{
  "mcpServers": {
    "geobrain": {
      "command": "node",
      "args": ["/CAMINHO/ABSOLUTO/mcp/geobrain-mcp/dist/index.js"]
    }
  }
}
```

```bash
# 3. Reinicie o Claude Desktop. Pronto.
```

Em qualquer chat: `@geobrain.lookup_term "Pré-sal"`. → Mais em [[MCP Server]].

---

## 🕸️ Caminho 3 — Neo4j local (queries multi-hop)

> Para: análises ad-hoc, exploração visual, prototipagem de agentes.

```bash
git clone https://github.com/thiagoflc/geolytics-dictionary.git
cd geolytics-dictionary

# 1. Gerar Cypher loader
node scripts/build-neo4j.js

# 2. Subir Neo4j em Docker
docker compose up -d

# 3. Acessar Browser
open http://localhost:7474
# login: neo4j / senha: geobrain123
```

Cole no Browser:
```cypher
MATCH path = shortestPath(
  (p:Operational {id:'poco'})-[*]-
  (r:Contractual {id:'regime-contratual'})
)
RETURN path
```

→ Mais em [[Neo4j Setup]].

---

## 🧠 Caminho 4 — Agente LangGraph completo

> Para: construir agente próprio com guardrail Validator + GraphQuery.

```bash
git clone https://github.com/thiagoflc/geolytics-dictionary.git
cd geolytics-dictionary/examples/langgraph-agent

# 1. Setup
pip install -r requirements.txt

# 2. Configure LLM (Anthropic recomendado)
export ANTHROPIC_API_KEY=sk-ant-...

# 3. (Opcional) Neo4j para Cypher real
cd ../.. && docker compose up -d
export NEO4J_URI=bolt://localhost:7687
cd examples/langgraph-agent

# 4. Rode demo
python run_demo.py
```

→ Mais em [[LangGraph Agent]].

---

## 📒 Caminho 5 — Notebooks didáticos

> Para: aprender o projeto interativamente.

```bash
git clone https://github.com/thiagoflc/geolytics-dictionary.git
cd geolytics-dictionary

pip install -r notebooks/requirements.txt
jupyter lab notebooks/
```

Quatro notebooks:

| Notebook                          | Aprende                                                          |
| --------------------------------- | ---------------------------------------------------------------- |
| `01_explore_graph.ipynb`          | Carregar `entity-graph.json`, visualizar com NetworkX, BFS       |
| `02_rag_with_validator.ipynb`     | Tour pelo RAG corpus + demonstração de regras do Validator       |
| `03_langgraph_multiagent.ipynb`   | Walkthrough do agente (Router → Decomposer → Validator pipeline) |
| `04_geomec_qa.ipynb`              | Q&A em domínio geomecânico (Petrobras corporate)                  |

---

## 🌐 Caminho 6 (sem clonar) — direto via HTTP

> Para: apps web, prototipagem rápida sem instalar nada.

```javascript
// index.html
const manifest = await fetch('https://thiagoflc.github.io/geobrain/api/v1/index.json').then(r => r.json());
const terms = await fetch(`https://thiagoflc.github.io/geobrain${manifest.endpoints.terms}`).then(r => r.json());
console.log(terms.find(t => t.id === 'bloco'));
```

→ Mais em [[REST API]].

---

## Pré-requisitos por caminho

| Caminho            | Node.js | Python  | Docker  | LLM Key  |
| ------------------ | ------- | ------- | ------- | -------- |
| Python Package     |         | ≥ 3.10  |         |          |
| MCP Server         | ≥ 18    |         |         | (LLM via Claude Desktop) |
| Neo4j              |         |         | ≥ 20.10 |          |
| LangGraph          | ≥ 18    | ≥ 3.10  | (opt.)  | ✅       |
| Notebooks          |         | ≥ 3.10  |         | (opt.)   |
| REST API           |         |         |         |          |

---

## Verificar tudo funcionando

Após qualquer caminho, este teste sanity confirma:

```bash
# Python
python -c "from geolytics_dictionary import Dictionary; print(len(Dictionary().lookup('petróleo')))"

# Node
node -e "const g = require('./data/entity-graph.json'); console.log('Nodes:', g.nodes.length)"

# Neo4j
docker exec geobrain-neo4j cypher-shell -u neo4j -p geobrain123 \
  "MATCH (n) RETURN count(n)"
```

Espere algo como:
- Python: `lookup` retorna ≥ 1 termo
- Node: `Nodes: 221`
- Neo4j: `count(n) = 221`

---

## O que fazer depois

Conforme seu objetivo:

| Quero…                                                | Vá para                                |
| ----------------------------------------------------- | -------------------------------------- |
| Entender as 8 camadas semânticas                      | [[Semantic Layers]]                    |
| Ver casos de uso reais                                | [[Use Cases]]                          |
| Adicionar uma entidade nova                            | [[Contributing]]                       |
| Validar afirmações automaticamente                     | [[Semantic Validator]]                 |
| Exportar SHACL para outro triplestore                  | [[SHACL Validation]]                   |
| Integrar dados Volve enriquecidos                      | [[SPE Volve Integration]]              |
| Resolver dúvidas comuns                                | [[FAQ]]                                |

---

## Onde pedir ajuda

- 🐛 **Bugs** → [GitHub Issues](https://github.com/thiagoflc/geolytics-dictionary/issues)
- 💬 **Dúvidas conceituais** → [Discussions](https://github.com/thiagoflc/geolytics-dictionary/discussions)
- 📧 **Pesquisa / colaboração acadêmica** → email do mantenedor (perfil GitHub)

---

> Próximo: aprender o **vocabulário** do projeto em [[Semantic Layers]] ou ver exemplos em [[Use Cases]].
