# REST API (estática via GitHub Pages)

A pasta [`api/v1/`](https://github.com/thiagoflc/geolytics-dictionary/tree/main/api/v1) contém **endpoints estáticos** servidos por GitHub Pages — versões otimizadas dos dados em `data/` para consumo HTTP.

Base URL pública: **https://thiagoflc.github.io/geobrain/api/v1/**

> Diferença entre `data/` e `api/v1/`:
> - `data/` é fonte canônica para devs (JSON cru, com campos internos).
> - `api/v1/` é otimizado para apps (campos filtrados, manifest, headers de cache).

---

## Manifest

```bash
curl https://thiagoflc.github.io/geobrain/api/v1/index.json
```

Resposta:
```json
{
  "version": "0.4.2",
  "generated_at": "2026-04-15T08:00:00Z",
  "endpoints": {
    "entities": "/api/v1/entities.json",
    "terms": "/api/v1/terms.json",
    "acronyms": "/api/v1/acronyms.json",
    "search_index": "/api/v1/search-index.json",
    ...
  },
  "datasets": {...}
}
```

`index.json` é o **ponto de entrada**. Todos os outros endpoints são listados aqui.

---

## Endpoints principais

### Entidades & glossário

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/entities.json`                       | Grafo completo (221 nós + 370 relações)                  |
| `GET /api/v1/terms.json`                          | Glossário enriquecido (23 termos ANP + estendidos)       |
| `GET /api/v1/acronyms.json`                       | 1.102 siglas categorizadas                               |
| `GET /api/v1/search-index.json`                   | Índice invertido (chave: token, valor: array de IDs)     |
| `GET /api/v1/datasets.json`                       | Manifesto: versões de 3W, GSO, OSDU, CGI                  |

### CGI / GeoSciML (L1b)

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/cgi-lithology.json`                  | 437 conceitos litológicos                                |
| `GET /api/v1/cgi-geologic-time.json`              | Escala cronoestratigráfica                               |
| `GET /api/v1/cgi-fault-type.json`                 | Tipos de falha                                           |
| `GET /api/v1/cgi-stratigraphic-rank.json`         | Hierarquia estratigráfica                                |
| `GET /api/v1/cgi-deformation-style.json`          | Estilos de deformação                                    |
| `GET /api/v1/cgi-contact-type.json`               | Tipos de contato                                         |
| `GET /api/v1/cgi-osdu-lithology-map.json`         | Crosswalk CGI ↔ OSDU                                     |
| `GET /api/v1/layer1-layer1b-equivalence.json`     | Equivalência BFO ↔ GeoSciML                              |

### ANP (L5)

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/anp-bacia-sedimentar.json`           | Bacias sedimentares brasileiras                          |
| `GET /api/v1/anp-poco-tipo.json`                  | Tipos de poço ANP                                       |
| `GET /api/v1/anp-poco-categoria.json`             | Categorias de poço                                       |
| `GET /api/v1/anp-poco-resultado.json`             | Resultados de poço                                       |
| `GET /api/v1/anp-uf.json`                         | UFs com produção O&G                                     |
| `GET /api/v1/anp-osdu-wellstatus-map.json`        | Crosswalk status ANP ↔ OSDU                              |
| `GET /api/v1/well-attributes.json`                | Atributos de poço (envelope completo)                    |

### Crosswalks WITSML/PRODML/GWML2/SOSA

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/witsml-rdf-crosswalk.json`           | WITSML 2.0 → `geo:`                                      |
| `GET /api/v1/prodml-rdf-crosswalk.json`           | PRODML 2.x → `geo:`                                      |
| `GET /api/v1/gsmlbh-properties.json`              | GWML2 borehole properties                                |
| `GET /api/v1/gwml2.json`                         | 9 classes GWML2 WellConstruction                          |
| `GET /api/v1/sosa-qudt-alignment.json`            | SOSA + QUDT mnemonics                                    |

### Petrobras corporativo

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/gestao-projetos-parcerias.json`      | Projetos e parcerias                                    |
| `GET /api/v1/axon-manifest.json`                  | Manifest do glossário Petrobras AXON                    |
| `GET /api/v1/axon-petrobras-glossary.json`        | Glossário AXON (definições)                              |

### Geomecânica & sísmica

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/geomechanics.json`                   | Módulo MEM P2.7 + corporativo                            |
| `GET /api/v1/seismic.json`                        | Módulos sísmicos P2.8                                    |

### RDF / SHACL

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/geolytics-shapes.ttl`                | 65 SHACL NodeShapes                                      |
| `GET /api/v1/geolytics-vocab.ttl`                 | OWL vocab                                                |
| `GET /api/v1/geobrain-shapes.ttl`                 | (alias) shapes                                           |
| `GET /api/v1/geobrain-vocab.ttl`                  | (alias) vocab                                            |
| `GET /api/v1/ontology-layers-shapes.ttl`          | Shapes específicas para validar layer coverage           |

### Validador

| Endpoint                                          | Conteúdo                                                |
| ------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/validate-rules.json`                 | Catálogo de regras (rule_id, severity, description)      |

---

## Headers & caching

GitHub Pages serve com:
```
Cache-Control: public, max-age=600
Access-Control-Allow-Origin: *
```

CORS permissivo → pode fetchar do browser. Cache de 10 min.

> Para cache mais longo, use `https://raw.githubusercontent.com/thiagoflc/geolytics-dictionary/<commit-sha>/api/v1/...` (cache eterno por SHA).

---

## Exemplos de uso

### JavaScript (browser)

```javascript
const res = await fetch('https://thiagoflc.github.io/geobrain/api/v1/entities.json');
const graph = await res.json();
const wellbores = graph.nodes.filter(n => n.type === 'Operational');
console.log(`${wellbores.length} entidades operacionais`);
```

### Python

```python
import requests

manifest = requests.get(
    'https://thiagoflc.github.io/geobrain/api/v1/index.json'
).json()

terms_url = manifest['endpoints']['terms']
terms = requests.get(f'https://thiagoflc.github.io/geobrain{terms_url}').json()
```

### cURL + jq (quick exploration)

```bash
# Quantas entidades por tipo?
curl -s https://thiagoflc.github.io/geobrain/api/v1/entities.json \
  | jq '.nodes | group_by(.type) | map({type: .[0].type, count: length})'

# Listar siglas com 3+ expansões (ambíguas)
curl -s https://thiagoflc.github.io/geobrain/api/v1/acronyms.json \
  | jq '.[] | select(.expansions | length >= 3) | .acronym'
```

---

## Versionamento

- **Path-based** (`/api/v1/`) — major version. Breaking changes vão para `/api/v2/`.
- **Manifest version** (`index.json:version`) — semver completo (`0.4.2`).
- **`generated_at` timestamp** — quando foi regenerado.

GitHub Pages publica automaticamente em cada push ao `main`. Para fixar versão, use commit-SHA via raw GitHub.

---

## Limitações

- **Estático** — não suporta query params, body POST, search server-side.
- **Tamanho** — `entities.json` ~1 MB. Use `search-index.json` para lookups rápidos client-side.
- **Latência** — GitHub Pages CDN (CloudFlare por trás), latência ~100 ms a partir do Brasil.
- **Sem auth** — totalmente público. Não use para dados sensíveis.

---

## Para apps que precisam de query server-side

Use o pacote Python `geobrain` localmente, ou o **MCP Server** com tools como `cypher_query` e `search_rag`. Veja [[MCP Server]] e [[Python Package]].

Para Cypher full multi-hop, suba o Neo4j local. Veja [[Neo4j Setup]].

---

## Padrões de design

### 🟢 Manifest-first

`index.json` lista **todos** os endpoints. Apps não hardcodeiam URLs.

### 🟢 Conteúdo otimizado

`api/v1/` exclui campos internos (`_debug`, `_temp`). Tamanhos ~30% menores que `data/`.

### 🟢 Cross-format

Para os mesmos conceitos, oferecemos JSON e TTL:
- `entities.json` (gráfico)
- `geobrain-vocab.ttl` (RDF)
- `geobrain-shapes.ttl` (SHACL)

Apps escolhem o formato que faz sentido.

### 🟢 Search-index pré-computado

`search-index.json` permite full-text search client-side sem backend.

---

> **Próximo:** explorar [[RAG Corpus]] (formato pré-otimizado para embeddings) ou [[Data Files]] (versão dev-friendly).
