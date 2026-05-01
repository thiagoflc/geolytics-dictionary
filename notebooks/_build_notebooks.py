"""Build the four Geolytics tutorial notebooks as valid .ipynb files.

Run once from the repo root (or notebooks/ directory):
    python notebooks/_build_notebooks.py

The output files are committed alongside this script for reproducibility.
"""

from __future__ import annotations

import json
import os

NOTEBOOKS_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def md(source: str) -> dict:
    """Return a markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source,
    }


def code(source: str, outputs: list | None = None) -> dict:
    """Return a code cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": outputs or [],
        "source": source,
    }


def nb(cells: list) -> dict:
    """Wrap cells in a valid nbformat v4 notebook."""
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def save(name: str, notebook: dict) -> None:
    path = os.path.join(NOTEBOOKS_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(notebook, fh, ensure_ascii=False, indent=1)
    print(f"  Wrote {path}  ({len(notebook['cells'])} cells)")


# ===========================================================================
# Notebook 1 — Exploracao do Grafo com NetworkX
# ===========================================================================

NB1_CELLS = [
    md(
        "# 01 — Exploracao do Grafo de Entidades com NetworkX\n\n"
        "Neste notebook exploramos o grafo de entidades do **Geolytics Dictionary** "
        "usando a biblioteca [NetworkX](https://networkx.org/). O grafo contem "
        "107 nos e 127 arestas representando conceitos do dominio de "
        "Exploracao & Producao (E&P) de petroleo e gas no Brasil.\n\n"
        "**Fonte de dados:** `entity-graph.json` publicado via GitHub Pages."
    ),
    md(
        "## Pre-requisitos\n\n"
        "```bash\n"
        "pip install networkx matplotlib requests\n"
        "```\n\n"
        "Nao e necessaria nenhuma chave de API."
    ),
    md(
        "## Objetivo\n\n"
        "Ao final deste notebook voce sera capaz de:\n\n"
        "1. Carregar o `entity-graph.json` diretamente do GitHub Pages.\n"
        "2. Construir um `MultiDiGraph` NetworkX com atributos de no e aresta.\n"
        "3. Calcular estatisticas basicas (nos, arestas, distribuicao de tipos).\n"
        "4. Visualizar um sub-grafo ao redor do no `poco`.\n"
        "5. Calcular o caminho mais curto entre `poco` e `anp`.\n"
        "6. Detectar comunidades com o algoritmo de modularidade gulosa.\n"
        "7. Exportar o grafo para GraphML (compativel com Gephi/yEd)."
    ),
    md("## 1. Importacoes"),
    code(
        "import json\n"
        "import requests\n"
        "import networkx as nx\n"
        "import matplotlib\n"
        "import matplotlib.pyplot as plt\n"
        "import collections\n\n"
        "print('networkx', nx.__version__)\n"
        "print('matplotlib', matplotlib.__version__)"
        # expected output:
        "\n# Saida esperada:\n"
        "# networkx 3.x\n"
        "# matplotlib 3.x"
    ),
    md("## 2. Carregamento dos dados"),
    code(
        "# URL publica via GitHub Pages\n"
        "GRAPH_URL = (\n"
        "    'https://thiagoflc.github.io/geolytics-dictionary/data/entity-graph.json'\n"
        ")\n\n"
        "# Fallback: arquivo local (util se estiver offline)\n"
        "import os\n"
        "LOCAL_PATH = os.path.join(\n"
        "    os.path.dirname(os.getcwd()), 'data', 'entity-graph.json'\n"
        ")\n\n"
        "try:\n"
        "    resp = requests.get(GRAPH_URL, timeout=10)\n"
        "    resp.raise_for_status()\n"
        "    graph_data = resp.json()\n"
        "    print('Dados carregados via HTTP')\n"
        "except Exception as exc:\n"
        "    print(f'HTTP falhou ({exc}), usando arquivo local...')\n"
        "    with open(LOCAL_PATH, encoding='utf-8') as fh:\n"
        "        graph_data = json.load(fh)\n"
        "    print('Dados carregados do disco')\n\n"
        "nodes = graph_data['nodes']\n"
        "edges = graph_data.get('edges', [])\n"
        "print(f'Nos: {len(nodes)}  Arestas: {len(edges)}')"
        "\n# Saida esperada:\n"
        "# Dados carregados via HTTP\n"
        "# Nos: 107  Arestas: 127"
    ),
    md("## 3. Construcao do MultiDiGraph"),
    code(
        "G = nx.MultiDiGraph()\n\n"
        "# Adiciona nos com atributos\n"
        "for n in nodes:\n"
        "    G.add_node(\n"
        "        n['id'],\n"
        "        label=n.get('label', n['id']),\n"
        "        label_en=n.get('label_en', ''),\n"
        "        node_type=n.get('type', 'unknown'),\n"
        "        color=n.get('color', '#888888'),\n"
        "        size=n.get('size', 10),\n"
        "    )\n\n"
        "# Adiciona arestas com atributos\n"
        "for e in edges:\n"
        "    G.add_edge(\n"
        "        e['source'],\n"
        "        e['target'],\n"
        "        relation=e.get('relation', ''),\n"
        "        label_pt=e.get('relation_label_pt', ''),\n"
        "        style=e.get('style', 'solid'),\n"
        "    )\n\n"
        "print(f'Nos no grafo  : {G.number_of_nodes()}')\n"
        "print(f'Arestas no grafo: {G.number_of_edges()}')\n"
        "print(f'E direcionado : {G.is_directed()}')\n"
        "print(f'E multi-aresta: {G.is_multigraph()}')"
        "\n# Saida esperada:\n"
        "# Nos no grafo  : 107\n"
        "# Arestas no grafo: 127\n"
        "# E direcionado : True\n"
        "# E multi-aresta: True"
    ),
    md("## 4. Estatisticas do grafo"),
    code(
        "# Distribuicao de tipos de nos\n"
        "type_counter = collections.Counter(\n"
        "    data['node_type'] for _, data in G.nodes(data=True)\n"
        ")\n"
        "print('Distribuicao de tipos:')\n"
        "for tipo, count in sorted(type_counter.items(), key=lambda x: -x[1]):\n"
        "    print(f'  {tipo:<20} {count}')\n\n"
        "# Grau medio\n"
        "avg_deg = sum(d for _, d in G.degree()) / G.number_of_nodes()\n"
        "print(f'\\nGrau medio (total)  : {avg_deg:.2f}')\n\n"
        "# Top-5 nos por grau de entrada (mais referenciados)\n"
        "in_degrees = sorted(G.in_degree(), key=lambda x: -x[1])\n"
        "print('\\nTop-5 nos por grau de entrada:')\n"
        "for node_id, deg in in_degrees[:5]:\n"
        "    label = G.nodes[node_id].get('label', node_id)\n"
        "    print(f'  {label:<30} {deg}')"
        "\n# Saida esperada (aprox.):\n"
        "# Distribuicao de tipos:\n"
        "#   analytical           25\n"
        "#   operational          17\n"
        "#   ...\n"
        "# Grau medio: ~2.38\n"
        "# Top-5 por entrada: poco, bloco, bacia-sedimentar..."
    ),
    md(
        "### Histograma de graus\n\n"
        "O histograma abaixo mostra quantos nos possuem cada valor de grau total "
        "(entrada + saida). Grafos de conhecimento tipicamente exibem distribuicao "
        "de lei de potencia."
    ),
    code(
        "degrees = [d for _, d in G.degree()]\n\n"
        "fig, ax = plt.subplots(figsize=(7, 3))\n"
        "ax.hist(degrees, bins=range(0, max(degrees) + 2), color='#378ADD', edgecolor='white')\n"
        "ax.set_xlabel('Grau total (entrada + saida)')\n"
        "ax.set_ylabel('Numero de nos')\n"
        "ax.set_title('Distribuicao de Graus — entity-graph.json')\n"
        "plt.tight_layout()\n"
        "plt.show()"
        "\n# Saida esperada: histograma com cauda longa a direita"
    ),
    md("## 5. Sub-grafo ao redor de `poco`"),
    code(
        "CENTER = 'poco'\n"
        "RADIUS = 2  # saltos ao redor do centro\n\n"
        "# Nos a distancia <= RADIUS (tanto predecessores quanto sucessores)\n"
        "neighbors = {CENTER}\n"
        "current = {CENTER}\n"
        "for _ in range(RADIUS):\n"
        "    nxt = set()\n"
        "    for n in current:\n"
        "        nxt.update(G.successors(n))\n"
        "        nxt.update(G.predecessors(n))\n"
        "    neighbors.update(nxt)\n"
        "    current = nxt\n\n"
        "sub = G.subgraph(neighbors).copy()\n"
        "print(f'Sub-grafo: {sub.number_of_nodes()} nos, {sub.number_of_edges()} arestas')"
        "\n# Saida esperada:\n"
        "# Sub-grafo: ~20 nos, ~25 arestas"
    ),
    code(
        "# Mapeamento tipo -> cor para visualizacao\n"
        "TYPE_COLORS = {\n"
        "    'operational': '#378ADD',\n"
        "    'geological':  '#4CAF50',\n"
        "    'contractual': '#F4A522',\n"
        "    'actor':       '#D85A30',\n"
        "    'instrument':  '#9C27B0',\n"
        "    'equipment':   '#00BCD4',\n"
        "    'analytical':  '#795548',\n"
        "    'unknown':     '#888888',\n"
        "}\n\n"
        "node_colors = [\n"
        "    TYPE_COLORS.get(sub.nodes[n].get('node_type', 'unknown'), '#888888')\n"
        "    for n in sub.nodes()\n"
        "]\n"
        "node_sizes = [\n"
        "    sub.nodes[n].get('size', 10) * 40 for n in sub.nodes()\n"
        "]\n"
        "labels = {n: sub.nodes[n].get('label', n) for n in sub.nodes()}\n\n"
        "fig, ax = plt.subplots(figsize=(12, 8))\n"
        "pos = nx.spring_layout(sub, seed=42, k=1.2)\n"
        "nx.draw_networkx(\n"
        "    sub, pos=pos,\n"
        "    labels=labels,\n"
        "    node_color=node_colors,\n"
        "    node_size=node_sizes,\n"
        "    edge_color='#cccccc',\n"
        "    font_size=8,\n"
        "    arrows=True,\n"
        "    arrowsize=12,\n"
        "    ax=ax,\n"
        ")\n"
        "ax.set_title(f'Sub-grafo raio {RADIUS} ao redor de \"{CENTER}\"', fontsize=13)\n"
        "ax.axis('off')\n"
        "plt.tight_layout()\n"
        "plt.show()"
        "\n# Saida esperada: grafo com poco no centro, nos vizinhos como bloco,\n"
        "# bacia-sedimentar, anp, operador, etc."
    ),
    md("## 6. Caminho mais curto entre `poco` e `anp`"),
    code(
        "SOURCE = 'poco'\n"
        "TARGET = 'anp'\n\n"
        "# NetworkX trabalha com MultiDiGraph; usamos o grafo subjacente nao-dirigido\n"
        "# para encontrar qualquer caminho semantico\n"
        "G_undirected = G.to_undirected()\n\n"
        "try:\n"
        "    path = nx.shortest_path(G_undirected, source=SOURCE, target=TARGET)\n"
        "    print(f'Caminho mais curto ({SOURCE} -> {TARGET}):')\n"
        "    for i, node_id in enumerate(path):\n"
        "        label = G.nodes[node_id].get('label', node_id)\n"
        "        prefix = '  ' + '  ' * i + ('-> ' if i > 0 else '   ')\n"
        "        print(f'{prefix}{label} ({node_id})')\n"
        "    print(f'\\nComprimento: {len(path) - 1} aresta(s)')\n"
        "except nx.NetworkXNoPath:\n"
        "    print(f'Nenhum caminho encontrado entre {SOURCE} e {TARGET}')"
        "\n# Saida esperada (aprox.):\n"
        "# Caminho mais curto (poco -> anp):\n"
        "#    Poco (poco)\n"
        "#    -> Bloco (bloco)\n"
        "#    -> ANP (anp)\n"
        "# Comprimento: 2 aresta(s)"
    ),
    md("## 7. Deteccao de comunidades (modularidade gulosa)"),
    code(
        "# Para modularidade gulosa o grafo precisa ser nao-dirigido e conectado.\n"
        "# Trabalhamos com o maior componente conectado.\n"
        "from networkx.algorithms.community import greedy_modularity_communities\n\n"
        "G_undi = G.to_undirected()\n"
        "largest_cc = G_undi.subgraph(\n"
        "    max(nx.connected_components(G_undi), key=len)\n"
        ").copy()\n\n"
        "communities = list(greedy_modularity_communities(largest_cc))\n"
        "print(f'Numero de comunidades detectadas: {len(communities)}')\n\n"
        "for i, comm in enumerate(communities):\n"
        "    labels = [G.nodes[n].get('label', n) for n in sorted(comm)]\n"
        "    print(f'\\nComunidade {i+1} ({len(comm)} nos):')\n"
        "    print('  ' + ', '.join(labels[:10]) + (f'  ... (+{len(labels)-10} mais)' if len(labels) > 10 else ''))"
        "\n# Saida esperada:\n"
        "# Numero de comunidades detectadas: ~5\n"
        "# Comunidade 1: nos do dominio operacional/contratual\n"
        "# Comunidade 2: nos geologicos/analiticos\n"
        "# ..."
    ),
    md("## 8. Exportacao para GraphML (Gephi / yEd)"),
    code(
        "# GraphML e o formato padrao para importar em Gephi, yEd, Cytoscape etc.\n"
        "# Exportamos o grafo completo (nao apenas o sub-grafo).\n"
        "import os\n\n"
        "OUTPUT_PATH = os.path.join(os.path.dirname(os.getcwd()), 'notebooks', 'entity-graph.graphml')\n\n"
        "# MultiDiGraph -> DiGraph para remover multi-arestas (GraphML nao as suporta bem)\n"
        "G_simple = nx.DiGraph(G)\n\n"
        "nx.write_graphml(G_simple, OUTPUT_PATH)\n"
        "print(f'Grafo exportado para: {OUTPUT_PATH}')\n"
        "print(f'  Nos  : {G_simple.number_of_nodes()}')\n"
        "print(f'  Arestas: {G_simple.number_of_edges()}')\n"
        "print('Abra o arquivo no Gephi (File > Open) para visualizacao interativa.')"
        "\n# Saida esperada:\n"
        "# Grafo exportado para: .../notebooks/entity-graph.graphml\n"
        "# Nos  : 107\n"
        "# Arestas: 127"
    ),
    md(
        "## Proximo passo\n\n"
        "Veja o notebook **02_rag_with_validator.ipynb** para aprender como "
        "construir um pipeline RAG sobre o corpus Geolytics e validar "
        "semanticamente as respostas."
    ),
]

# ===========================================================================
# Notebook 2 — RAG com Validacao Semantica
# ===========================================================================

NB2_CELLS = [
    md(
        "# 02 — RAG com Validacao Semantica\n\n"
        "Este notebook demonstra um pipeline de **Retrieval-Augmented Generation (RAG)** "
        "usando o `rag-corpus.jsonl` do Geolytics Dictionary. Para executar sem "
        "nenhuma chave de API usamos `rank_bm25` como mecanismo de recuperacao "
        "esparsa (BM25). Em producao substituiria pelo indice vetorial de sua escolha "
        "(FAISS, Chroma, Pinecone etc.).\n\n"
        "Tambem demonstramos como o **validador semantico** do Geolytics captura "
        "alucinacoes tipicas, como confundir categorias de reservas SPE-PRMS."
    ),
    md(
        "## Pre-requisitos\n\n"
        "```bash\n"
        "pip install rank-bm25 requests\n"
        "# Opcional para index vetorial:\n"
        "# pip install faiss-cpu sentence-transformers\n"
        "```"
    ),
    md(
        "## Objetivo\n\n"
        "1. Carregar e inspecionar o `rag-corpus.jsonl`.\n"
        "2. Construir um indice BM25 como alternativa zero-config.\n"
        "3. Demonstrar recuperacao correta: *'O que e Plano de Avaliacao de Descobertas?'*\n"
        "4. Mostrar como um RAG vetor-only erra 'Reserva 4P' e como o validador corrige.\n"
        "5. Visualizar pontuacoes dos candidatos de recuperacao.\n"
        "6. Demonstrar a integracao com `scripts/validate-cli.js` via subprocess."
    ),
    md("## 1. Importacoes"),
    code(
        "import json\n"
        "import math\n"
        "import os\n"
        "import re\n"
        "import subprocess\n"
        "import requests\n"
        "from rank_bm25 import BM25Okapi\n"
        "import matplotlib.pyplot as plt\n\n"
        "print('rank-bm25 importado com sucesso')"
        "\n# Saida esperada: rank-bm25 importado com sucesso"
    ),
    md("## 2. Carregamento do corpus"),
    code(
        "CORPUS_URL = (\n"
        "    'https://thiagoflc.github.io/geolytics-dictionary/ai/rag-corpus.jsonl'\n"
        ")\n"
        "LOCAL_CORPUS = os.path.join(\n"
        "    os.path.dirname(os.getcwd()), 'ai', 'rag-corpus.jsonl'\n"
        ")\n\n"
        "corpus_docs = []\n\n"
        "def _load_jsonl(text: str) -> list[dict]:\n"
        "    docs = []\n"
        "    for line in text.strip().splitlines():\n"
        "        line = line.strip()\n"
        "        if line:\n"
        "            docs.append(json.loads(line))\n"
        "    return docs\n\n"
        "try:\n"
        "    resp = requests.get(CORPUS_URL, timeout=15)\n"
        "    resp.raise_for_status()\n"
        "    corpus_docs = _load_jsonl(resp.text)\n"
        "    print('Corpus carregado via HTTP')\n"
        "except Exception as exc:\n"
        "    print(f'HTTP falhou ({exc}), usando arquivo local...')\n"
        "    with open(LOCAL_CORPUS, encoding='utf-8') as fh:\n"
        "        corpus_docs = _load_jsonl(fh.read())\n"
        "    print('Corpus carregado do disco')\n\n"
        "print(f'Total de chunks: {len(corpus_docs)}')\n"
        "# Inspeciona um chunk de exemplo\n"
        "print('\\nExemplo de chunk:')\n"
        "print(json.dumps(corpus_docs[13], ensure_ascii=False, indent=2)[:400])"
        "\n# Saida esperada:\n"
        "# Corpus carregado via HTTP\n"
        "# Total de chunks: 1245\n"
        "# Exemplo de chunk: {\"id\": \"term_pad\", \"type\": \"term\", \"text\": \"PAD..."
    ),
    md("## 3. Construcao do indice BM25"),
    code(
        "# Tokenizacao simples: lowercase + split em espacos/pontuacao\n"
        "def tokenize(text: str) -> list[str]:\n"
        "    return re.sub(r'[^a-zA-Zaaccedeiioouuaeiou\\s]', ' ', text.lower()).split()\n\n"
        "texts = [doc['text'] for doc in corpus_docs]\n"
        "tokenized_corpus = [tokenize(t) for t in texts]\n\n"
        "bm25 = BM25Okapi(tokenized_corpus)\n"
        "print(f'Indice BM25 construido com {len(tokenized_corpus)} documentos')"
        "\n# Saida esperada:\n"
        "# Indice BM25 construido com 1245 documentos"
    ),
    code(
        "def retrieve(query: str, top_k: int = 5) -> list[dict]:\n"
        "    \"\"\"Retorna os top_k chunks mais relevantes para a query.\"\"\"\n"
        "    tokens = tokenize(query)\n"
        "    scores = bm25.get_scores(tokens)\n"
        "    top_indices = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]\n"
        "    results = []\n"
        "    for idx in top_indices:\n"
        "        doc = corpus_docs[idx]\n"
        "        results.append({\n"
        "            'id':    doc.get('id', ''),\n"
        "            'type':  doc.get('type', ''),\n"
        "            'score': float(scores[idx]),\n"
        "            'text':  doc.get('text', '')[:200],\n"
        "        })\n"
        "    return results\n\n"
        "print('Funcao retrieve() definida')"
    ),
    md("## 4. Recuperacao correta: Plano de Avaliacao de Descobertas"),
    code(
        "QUERY_PAD = 'O que e Plano de Avaliacao de Descobertas'\n\n"
        "results_pad = retrieve(QUERY_PAD, top_k=5)\n\n"
        "print(f'Query: \"{QUERY_PAD}\"')\n"
        "print('=' * 60)\n"
        "for i, r in enumerate(results_pad, 1):\n"
        "    print(f'#{i}  score={r[\"score\"]:.4f}  id={r[\"id\"]}  tipo={r[\"type\"]}')\n"
        "    print(f'    {r[\"text\"][:120]}...')\n"
        "    print()"
        "\n# Saida esperada:\n"
        "# #1  score=...  id=term_pad  tipo=term\n"
        "#     PAD — Plano de Avaliacao de Descobertas: Instrumento pelo qual o\n"
        "# #2  score=...  id=term_declaracao-comercialidade  tipo=term\n"
        "# ..."
    ),
    md(
        "O resultado #1 e `term_pad`, que e exatamente o chunk correto. "
        "O BM25 acerta porque os tokens da query ('plano', 'avaliacao', "
        "'descobertas') aparecem verbatim no texto do chunk."
    ),
    md(
        "## 5. Caso confuso: 'Reserva 4P'\n\n"
        "Um RAG baseado apenas em similaridade vetorial pode confundir "
        "'Reserva 4P' com 'Reserva Ambiental' (4P = categoria ambiental "
        "no contexto fundiario brasileiro). O validador semantico captura "
        "essa confusao verificando o contexto do dominio O&G vs. ambiental."
    ),
    code(
        "QUERY_4P = 'O que e Reserva 4P'\n\n"
        "results_4p = retrieve(QUERY_4P, top_k=5)\n\n"
        "print(f'Query: \"{QUERY_4P}\"')\n"
        "print('=' * 60)\n"
        "for i, r in enumerate(results_4p, 1):\n"
        "    print(f'#{i}  score={r[\"score\"]:.4f}  id={r[\"id\"]}  tipo={r[\"type\"]}')\n"
        "    print(f'    {r[\"text\"][:160]}...')\n"
        "    print()"
        "\n# Saida esperada:\n"
        "# Os resultados podem incluir chunks sobre SPE-PRMS (reservas 1P/2P/3P)\n"
        "# mas dificilmente '4P' pois nao e uma categoria SPE-PRMS valida —\n"
        "# esse e exatamente o comportamento incorreto que o validador detecta."
    ),
    code(
        "# Simulacao de uma resposta errada que um LLM poderia gerar\n"
        "FAKE_ANSWER_4P = (\n"
        "    'Reserva 4P e a quarta categoria de reservas da classificacao SPE-PRMS, '\n"
        "    'correspondendo a recursos contingentes de menor probabilidade de '\n"
        "    'desenvolvimento comercial.'\n"
        ")\n\n"
        "print('Resposta hipotetica do LLM (sem validacao):')\n"
        "print(FAKE_ANSWER_4P)\n\n"
        "print()\n"
        "print('PROBLEMA: A classificacao SPE-PRMS nao possui categoria 4P.')\n"
        "print('As categorias sao: 1P (provadas), 2P (provadas+provaveis), 3P (provadas+provaveis+possiveis).')\n"
        "print('\"4P\" nao e um termo tecnico valido na industria de O&G.')"
    ),
    md("### 5.1 Validacao via subprocess (validate-cli.js)"),
    code(
        "# O validate-cli.js e o validador semantico do Geolytics (Node.js).\n"
        "# Podemos chama-lo via subprocess a partir do Python.\n\n"
        "VALIDATOR_PATH = os.path.join(\n"
        "    os.path.dirname(os.getcwd()), 'scripts', 'validate-cli.js'\n"
        ")\n\n"
        "claim_to_validate = {\n"
        "    'term': '4P',\n"
        "    'answer': FAKE_ANSWER_4P,\n"
        "    'context': 'SPE-PRMS reservas'\n"
        "}\n\n"
        "if os.path.exists(VALIDATOR_PATH):\n"
        "    try:\n"
        "        proc = subprocess.run(\n"
        "            ['node', VALIDATOR_PATH, json.dumps(claim_to_validate)],\n"
        "            capture_output=True,\n"
        "            text=True,\n"
        "            timeout=10,\n"
        "        )\n"
        "        print('Saida do validador:')\n"
        "        print(proc.stdout or proc.stderr)\n"
        "    except Exception as exc:\n"
        "        print(f'Nao foi possivel executar o validador: {exc}')\n"
        "else:\n"
        "    print(f'validate-cli.js nao encontrado em {VALIDATOR_PATH}')\n"
        "    print('Para validar, execute a partir do diretorio raiz do repositorio.')"
        "\n# Saida esperada (se node disponivel):\n"
        "# { valid: false, violations: [{ rule: 'spe-prms-categories', ... }] }"
    ),
    md("## 6. Visualizacao das pontuacoes de recuperacao"),
    code(
        "queries = {\n"
        "    'PAD (correto)': QUERY_PAD,\n"
        "    'Reserva 4P (ambiguo)': QUERY_4P,\n"
        "    'Regime contratual': 'O que e regime contratual de concessao',\n"
        "}\n\n"
        "fig, axes = plt.subplots(1, len(queries), figsize=(14, 4))\n\n"
        "for ax, (title, query) in zip(axes, queries.items()):\n"
        "    results = retrieve(query, top_k=8)\n"
        "    ids = [r['id'].replace('term_', '')[:18] for r in results]\n"
        "    scores = [r['score'] for r in results]\n"
        "    ax.barh(ids[::-1], scores[::-1], color='#378ADD')\n"
        "    ax.set_title(title, fontsize=9)\n"
        "    ax.set_xlabel('Score BM25')\n"
        "    ax.tick_params(labelsize=7)\n\n"
        "plt.suptitle('Pontuacoes BM25 por Query', fontsize=11)\n"
        "plt.tight_layout()\n"
        "plt.show()"
        "\n# Saida esperada: tres graficos de barras horizontais mostrando\n"
        "# os chunks recuperados e seus scores BM25 para cada query."
    ),
    md(
        "## 7. Substituicao por indice vetorial (opcional)\n\n"
        "Para usar FAISS com embeddings locais (sem API), instale:\n\n"
        "```bash\n"
        "pip install faiss-cpu sentence-transformers\n"
        "```\n\n"
        "E substitua `retrieve()` pela versao abaixo:"
    ),
    code(
        "# ---------------------------------------------------------------------------\n"
        "# CELULA OPCIONAL — nao e executada automaticamente\n"
        "# ---------------------------------------------------------------------------\n"
        "# from sentence_transformers import SentenceTransformer\n"
        "# import faiss\n"
        "# import numpy as np\n"
        "#\n"
        "# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')\n"
        "# embeddings = model.encode(texts, show_progress_bar=True)\n"
        "# embeddings = np.array(embeddings).astype('float32')\n"
        "# faiss.normalize_L2(embeddings)\n"
        "#\n"
        "# index = faiss.IndexFlatIP(embeddings.shape[1])\n"
        "# index.add(embeddings)\n"
        "#\n"
        "# def retrieve_vec(query: str, top_k: int = 5):\n"
        "#     q_emb = model.encode([query]).astype('float32')\n"
        "#     faiss.normalize_L2(q_emb)\n"
        "#     distances, indices = index.search(q_emb, top_k)\n"
        "#     return [{'id': corpus_docs[i]['id'], 'score': float(d)}\n"
        "#              for i, d in zip(indices[0], distances[0])]\n"
        "print('Celula opcional — descomente para usar FAISS com embeddings locais')"
    ),
    md(
        "## Proximo passo\n\n"
        "Veja o notebook **03_langgraph_multiagent.ipynb** para integrar o RAG "
        "ao agente LangGraph multi-no com roteamento semantico."
    ),
]

# ===========================================================================
# Notebook 3 — Agente LangGraph Multi-no
# ===========================================================================

NB3_CELLS = [
    md(
        "# 03 — Agente LangGraph Multi-no\n\n"
        "Este notebook demonstra o **agente de referencia Geolytics** implementado "
        "com [LangGraph](https://github.com/langchain-ai/langgraph). O grafo DAG "
        "possui nos especializados para roteamento, decomposicao de perguntas "
        "multi-hop, recuperacao RAG, validacao semantica e sintese de respostas.\n\n"
        "**Atencao:** para executar com LLM real e necessaria a variavel de "
        "ambiente `ANTHROPIC_API_KEY` (ou `OPENAI_API_KEY`). O notebook "
        "demonstra a estrutura do grafo mesmo sem chave configurada."
    ),
    md(
        "## Pre-requisitos\n\n"
        "```bash\n"
        "pip install langgraph langchain-anthropic langchain-core\n"
        "# OU para OpenAI:\n"
        "# pip install langchain-openai\n"
        "```\n\n"
        "Variavel de ambiente (opcional para execucao real):\n"
        "```bash\n"
        "export ANTHROPIC_API_KEY='sk-ant-...'\n"
        "# OU\n"
        "export OPENAI_API_KEY='sk-...'\n"
        "```"
    ),
    md(
        "## Objetivo\n\n"
        "1. Importar o modulo `examples/langgraph-agent` via `sys.path`.\n"
        "2. Construir e inspecionar o grafo compilado.\n"
        "3. Executar 4 perguntas demo com impressao das transicoes de estado.\n"
        "4. Renderizar o DAG com `get_graph().draw_mermaid()`.\n"
        "5. Mostrar como trocar o provedor de LLM via variavel de ambiente."
    ),
    md("## 1. Configuracao do ambiente"),
    code(
        "import sys\n"
        "import os\n\n"
        "# Adiciona o diretorio do agente ao sys.path\n"
        "AGENT_DIR = os.path.join(\n"
        "    os.path.dirname(os.getcwd()), 'examples', 'langgraph-agent'\n"
        ")\n"
        "if AGENT_DIR not in sys.path:\n"
        "    sys.path.insert(0, AGENT_DIR)\n\n"
        "# Diretorio raiz do repositorio (para carregar dados)\n"
        "REPO_ROOT = os.path.dirname(os.getcwd())\n"
        "os.environ.setdefault('GEOLYTICS_DATA_DIR', os.path.join(REPO_ROOT, 'data'))\n"
        "os.environ.setdefault('GEOLYTICS_AI_DIR',   os.path.join(REPO_ROOT, 'ai'))\n\n"
        "print('AGENT_DIR:', AGENT_DIR)\n"
        "print('GEOLYTICS_DATA_DIR:', os.environ['GEOLYTICS_DATA_DIR'])"
        "\n# Saida esperada:\n"
        "# AGENT_DIR: .../examples/langgraph-agent\n"
        "# GEOLYTICS_DATA_DIR: .../data"
    ),
    md("## 2. Importacao dos modulos do agente"),
    code(
        "try:\n"
        "    from state import AgentState, ValidationResult\n"
        "    print('state.py importado')\n"
        "except ImportError as exc:\n"
        "    print(f'Aviso: {exc}')\n"
        "    # Define stub para demonstracao\n"
        "    from typing import Any\n"
        "    from typing_extensions import TypedDict\n\n"
        "    class ValidationResult(TypedDict, total=False):\n"
        "        valid: bool\n"
        "        violations: list\n\n"
        "    class AgentState(TypedDict, total=False):\n"
        "        question: str\n"
        "        classification: str\n"
        "        decomposed: list\n"
        "        graph_results: list\n"
        "        rag_results: list\n"
        "        draft: str\n"
        "        validation: ValidationResult\n"
        "        iteration: int\n"
        "        final_answer: str\n\n"
        "    print('Usando stub local do AgentState')"
        "\n# Saida esperada:\n"
        "# state.py importado"
    ),
    code(
        "# Tenta importar o modulo agent.py\n"
        "try:\n"
        "    import agent as geolytics_agent\n"
        "    print('agent.py importado')\n"
        "    HAS_AGENT = True\n"
        "except ImportError as exc:\n"
        "    print(f'Dependencia ausente: {exc}')\n"
        "    print('Instale: pip install langgraph langchain-anthropic langchain-core')\n"
        "    HAS_AGENT = False"
        "\n# Saida esperada:\n"
        "# agent.py importado (se langgraph estiver instalado)\n"
        "# OU: Dependencia ausente: No module named 'langgraph'"
    ),
    md("## 3. Construcao do grafo compilado"),
    code(
        "if HAS_AGENT:\n"
        "    try:\n"
        "        compiled = geolytics_agent.build_graph()\n"
        "        print('Grafo compilado com sucesso')\n"
        "        print(f'Tipo: {type(compiled)}')\n"
        "    except Exception as exc:\n"
        "        print(f'Erro ao compilar grafo: {exc}')\n"
        "        compiled = None\n"
        "else:\n"
        "    compiled = None\n"
        "    print('Pule esta celula — langgraph nao disponivel')"
        "\n# Saida esperada (com langgraph instalado):\n"
        "# Grafo compilado com sucesso\n"
        "# Tipo: <class 'langgraph.graph.state.CompiledStateGraph'>"
    ),
    md("## 4. Visualizacao do DAG em Mermaid"),
    code(
        "if compiled is not None:\n"
        "    try:\n"
        "        mermaid_str = compiled.get_graph().draw_mermaid()\n"
        "        print('Diagrama Mermaid gerado:')\n"
        "        print(mermaid_str)\n"
        "    except Exception as exc:\n"
        "        print(f'draw_mermaid() nao disponivel: {exc}')\n"
        "        mermaid_str = None\n"
        "else:\n"
        "    mermaid_str = None\n"
        "    print('Mostrando topologia documentada do agente (ver agent.py):')"
        "\n# Saida esperada (com langgraph instalado):\n"
        "# graph TD\n"
        "#   __start__ --> Router\n"
        "#   Router --> RAGRetrieve\n"
        "#   Router --> Decomposer\n"
        "#   Router --> Validator\n"
        "#   ..."
    ),
    md(
        "### Topologia do agente (referencia estatica)\n\n"
        "Mesmo sem LangGraph instalado e possivel visualizar a topologia "
        "documentada no codigo-fonte:\n\n"
        "```mermaid\n"
        "graph TD\n"
        "    A([__start__]) --> Router\n"
        "    Router -->|lookup| RAGRetrieve\n"
        "    Router -->|multi_hop| Decomposer\n"
        "    Router -->|validation| Validator\n"
        "    Decomposer --> GraphQuery\n"
        "    GraphQuery --> RAGRetrieve\n"
        "    RAGRetrieve --> Validator\n"
        "    Validator -->|valid=True ou iter>=2| Synthesizer\n"
        "    Validator -->|valid=False e iter<2| Synthesizer\n"
        "    Synthesizer --> B([__end__])\n"
        "```"
    ),
    md("## 5. Execucao de 4 perguntas demo"),
    code(
        "DEMO_QUESTIONS = [\n"
        "    {\n"
        "        'id': 'Q1',\n"
        "        'descricao': 'Lookup simples',\n"
        "        'pergunta': 'O que e PAD (Plano de Avaliacao de Descobertas)?',\n"
        "        'rota_esperada': 'lookup',\n"
        "    },\n"
        "    {\n"
        "        'id': 'Q2',\n"
        "        'descricao': 'Multi-hop: relacionamento entre entidades',\n"
        "        'pergunta': 'Quais bacias sedimentares possuem blocos com regime de partilha de producao?',\n"
        "        'rota_esperada': 'multi_hop',\n"
        "    },\n"
        "    {\n"
        "        'id': 'Q3',\n"
        "        'descricao': 'Falha de validacao esperada (4P)',\n"
        "        'pergunta': 'O que e Reserva 4P na classificacao SPE-PRMS?',\n"
        "        'rota_esperada': 'validation',\n"
        "    },\n"
        "    {\n"
        "        'id': 'Q4',\n"
        "        'descricao': 'Geomecanica: modulo elastico',\n"
        "        'pergunta': 'O que e o Modulo de Young e como ele e medido em testemunho?',\n"
        "        'rota_esperada': 'lookup',\n"
        "    },\n"
        "]\n\n"
        "for q in DEMO_QUESTIONS:\n"
        "    print(f\"[{q['id']}] {q['descricao']}\")\n"
        "    print(f\"    Pergunta: {q['pergunta']}\")\n"
        "    print(f\"    Rota esperada: {q['rota_esperada']}\")\n"
        "    print()"
        "\n# Saida esperada: listagem das 4 perguntas com suas descricoes"
    ),
    code(
        "# Executa o agente se disponivel; caso contrario simula as transicoes de estado\n\n"
        "def simulate_state_transitions(question: str, route: str) -> dict:\n"
        "    \"\"\"Simula as transicoes de estado sem LLM real.\"\"\"\n"
        "    state = {'question': question, 'iteration': 0}\n"
        "    transitions = []\n\n"
        "    # Router\n"
        "    state['classification'] = route\n"
        "    transitions.append(f'Router -> classificacao: {route}')\n\n"
        "    # Nos intermediarios por rota\n"
        "    if route == 'multi_hop':\n"
        "        state['decomposed'] = ['subpergunta 1', 'subpergunta 2']\n"
        "        transitions.append('Decomposer -> ' + str(state['decomposed']))\n"
        "        state['graph_results'] = [{'id': 'resultado_grafo', 'rel': 'exemplo'}]\n"
        "        transitions.append('GraphQuery -> graph_results: 1 resultado')\n"
        "    elif route == 'validation':\n"
        "        transitions.append('Router -> Validator (sem recuperacao RAG)')\n\n"
        "    # RAG (para lookup e multi_hop)\n"
        "    if route != 'validation':\n"
        "        state['rag_results'] = [{'id': 'term_pad', 'score': 9.42}]\n"
        "        transitions.append('RAGRetrieve -> rag_results: 1 chunk')\n\n"
        "    # Validator\n"
        "    state['validation'] = {'valid': route != 'validation', 'violations': []}\n"
        "    transitions.append(f\"Validator -> valid={state['validation']['valid']}\")\n\n"
        "    # Synthesizer\n"
        "    state['final_answer'] = f'[Resposta simulada para: {question[:40]}...]'\n"
        "    transitions.append('Synthesizer -> final_answer')\n\n"
        "    state['_transitions'] = transitions\n"
        "    return state\n\n"
        "for q in DEMO_QUESTIONS:\n"
        "    print(f\"\\n{'='*60}\")\n"
        "    print(f\"[{q['id']}] {q['descricao']}\")\n"
        "    print(f\"Pergunta: {q['pergunta']}\")\n"
        "    print()\n\n"
        "    if compiled is not None and os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY'):\n"
        "        try:\n"
        "            result = compiled.invoke({'question': q['pergunta'], 'iteration': 0})\n"
        "        except Exception as exc:\n"
        "            print(f'  Erro na execucao real: {exc}')\n"
        "            result = simulate_state_transitions(q['pergunta'], q['rota_esperada'])\n"
        "    else:\n"
        "        result = simulate_state_transitions(q['pergunta'], q['rota_esperada'])\n\n"
        "    print('Transicoes de estado:')\n"
        "    for t in result.get('_transitions', []):\n"
        "        print(f'  {t}')\n"
        "    print()\n"
        "    print(f\"Resposta final: {result.get('final_answer', 'N/A')}\")"
        "\n# Saida esperada:\n"
        "# [Q1] Lookup simples\n"
        "# Transicoes: Router -> lookup | RAGRetrieve | Validator | Synthesizer\n"
        "# ..."
    ),
    md("## 6. Como trocar o provedor de LLM"),
    code(
        "# O agente usa a variavel de ambiente LLM_PROVIDER para selecionar o modelo.\n"
        "# Valores suportados: 'anthropic' (padrao), 'openai'\n\n"
        "print('Exemplos de configuracao:')\n"
        "print()\n"
        "print('  # Anthropic Claude (padrao):')\n"
        "print('  export ANTHROPIC_API_KEY=\"sk-ant-...\"')\n"
        "print('  export LLM_PROVIDER=\"anthropic\"')\n"
        "print('  export LLM_MODEL=\"claude-sonnet-4-6\"')\n"
        "print()\n"
        "print('  # OpenAI:')\n"
        "print('  export OPENAI_API_KEY=\"sk-...\"')\n"
        "print('  export LLM_PROVIDER=\"openai\"')\n"
        "print('  export LLM_MODEL=\"gpt-4o\"')\n"
        "print()\n"
        "print('  # Dentro do notebook:')\n"
        "print('  os.environ[\"LLM_PROVIDER\"] = \"openai\"')\n"
        "print('  os.environ[\"OPENAI_API_KEY\"] = \"sk-...\"')\n"
        "print('  compiled = geolytics_agent.build_graph()  # reconstroi com novo provider')"
        "\n# Esta celula e apenas informativa e nao executa nenhuma chamada de API"
    ),
    md(
        "## Proximo passo\n\n"
        "Veja o notebook **04_geomec_qa.ipynb** para um estudo de caso "
        "aprofundado em geomecanica: circulo de Mohr, validacao SHACL e "
        "mapeamento de fraturas para o GSO."
    ),
]

# ===========================================================================
# Notebook 4 — Estudo de Caso: Geomecanica QA
# ===========================================================================

NB4_CELLS = [
    md(
        "# 04 — Geomecanica QA: Modelo de Terra Mecanico (MEM)\n\n"
        "Este notebook e um estudo de caso aprofundado no modulo de "
        "**Geomecanica** do Geolytics Dictionary. Cobrimos:\n\n"
        "- Consulta a propriedades elasticas necessarias para um MEM 1D.\n"
        "- Visualizacao do **Circulo de Mohr** para um estado de tensao sintetico.\n"
        "- Validacao SHACL da restricao `StressTensorShape`.\n"
        "- Mapeamento de fraturas para classes GSO/Loop3D via crosswalk."
    ),
    md(
        "## Pre-requisitos\n\n"
        "```bash\n"
        "pip install requests matplotlib\n"
        "# Opcional para validacao SHACL completa:\n"
        "# pip install pyshacl rdflib\n"
        "```"
    ),
    md(
        "## Objetivo\n\n"
        "1. Carregar `geomechanics.json` e `geomechanics-fractures.json`.\n"
        "2. Consultar quais propriedades elasticas sao necessarias para um MEM 1D.\n"
        "3. Plotar um Circulo de Mohr com envelope de Mohr-Coulomb.\n"
        "4. Demonstrar a restricao SHACL `StressTensorShape` (um valido, um invalido).\n"
        "5. Realizar o crosswalk fratura -> GSO."
    ),
    md("## 1. Carregamento dos dados"),
    code(
        "import json\n"
        "import os\n"
        "import math\n"
        "import requests\n"
        "import matplotlib.pyplot as plt\n"
        "import matplotlib.patches as mpatches\n"
        "import numpy as np\n\n"
        "BASE_URL = 'https://thiagoflc.github.io/geolytics-dictionary'\n"
        "DATA_DIR = os.path.join(os.path.dirname(os.getcwd()), 'data')\n\n"
        "def fetch_json(url: str, local_path: str) -> dict:\n"
        "    \"\"\"Baixa JSON via HTTP com fallback para arquivo local.\"\"\"\n"
        "    try:\n"
        "        resp = requests.get(url, timeout=10)\n"
        "        resp.raise_for_status()\n"
        "        print(f'Carregado via HTTP: {url.split(\"/\")[-1]}')\n"
        "        return resp.json()\n"
        "    except Exception as exc:\n"
        "        print(f'HTTP falhou ({exc}), usando local: {local_path}')\n"
        "        with open(local_path, encoding='utf-8') as fh:\n"
        "            return json.load(fh)\n\n"
        "geomec = fetch_json(\n"
        "    f'{BASE_URL}/data/geomechanics.json',\n"
        "    os.path.join(DATA_DIR, 'geomechanics.json'),\n"
        ")\n"
        "geomec_frac = fetch_json(\n"
        "    f'{BASE_URL}/data/geomechanics-fractures.json',\n"
        "    os.path.join(DATA_DIR, 'geomechanics-fractures.json'),\n"
        ")\n"
        "frac_gso = fetch_json(\n"
        "    f'{BASE_URL}/data/fracture_to_gso.json',\n"
        "    os.path.join(DATA_DIR, 'fracture_to_gso.json'),\n"
        ")\n"
        "taxonomies = fetch_json(\n"
        "    f'{BASE_URL}/data/taxonomies.json',\n"
        "    os.path.join(DATA_DIR, 'taxonomies.json'),\n"
        ")\n\n"
        "print(f'\\ngeomechanics.json   : {geomec[\"meta\"][\"class_count\"]} classes, {geomec[\"meta\"][\"property_count\"]} propriedades')\n"
        "print(f'geomechanics-fractures: {len(geomec_frac[\"classes\"])} classes')\n"
        "print(f'fracture_to_gso     : {len(frac_gso)} mapeamentos')"
        "\n# Saida esperada:\n"
        "# geomechanics.json   : 26 classes, 22 propriedades\n"
        "# geomechanics-fractures: 17 classes\n"
        "# fracture_to_gso     : 8 mapeamentos"
    ),
    md("## 2. Consulta: propriedades elasticas para um MEM 1D"),
    code(
        "# Um MEM 1D requer quatro pilares: tensao in situ, pressao de poros,\n"
        "# modulos elasticos e geometria de contencao.\n"
        "# Aqui identificamos as propriedades elasticas (Pilar 3) a partir da ontologia.\n\n"
        "def query_properties_by_class(data: dict, class_name: str) -> list[dict]:\n"
        "    \"\"\"Retorna propriedades da ontologia associadas a uma dada classe.\"\"\"\n"
        "    props = data.get('properties', [])\n"
        "    return [p for p in props if class_name.lower() in p.get('domain', '').lower()]\n\n"
        "# Classes de modulos elasticos no geomechanics.json\n"
        "ELASTIC_CLASSES = ['ElasticModuli', 'YoungModulus', 'PoissonRatio', 'ShearModulus', 'BulkModulus']\n\n"
        "print('Propriedades elasticas para MEM 1D:')\n"
        "print('=' * 60)\n\n"
        "all_classes = {c['name']: c for c in geomec.get('classes', [])}\n"
        "elastic_classes_found = [\n"
        "    c for c in geomec.get('classes', [])\n"
        "    if any(ec.lower() in c['name'].lower() for ec in ELASTIC_CLASSES)\n"
        "]\n\n"
        "for cls in elastic_classes_found:\n"
        "    print(f\"\\nClasse: {cls['name']} (id={cls['id']})\")\n"
        "    print(f\"  PT   : {cls.get('name_pt', 'N/A')}\")\n"
        "    print(f\"  Descr: {cls['description'][:100]}...\")\n"
        "    props_for_cls = [p for p in geomec.get('properties', []) if cls['name'] in p.get('domain', '')]\n"
        "    if props_for_cls:\n"
        "        print(f\"  Propriedades: {', '.join(p['name'] for p in props_for_cls)}\")"
        "\n# Saida esperada:\n"
        "# Classe: ElasticModuli (id=GM006)\n"
        "#   PT   : ModulosElasticos\n"
        "#   Descr: Collection of elastic moduli...\n"
        "# Classe: YoungModulus (id=GM007)\n"
        "# Classe: PoissonRatio (id=GM008)\n"
        "# ..."
    ),
    code(
        "# Resumo dos modulos necessarios para MEM 1D\n"
        "print('Resumo — Pilar 3 (Modulos Elasticos) para MEM 1D:')\n"
        "print()\n"
        "mem_pillars = [\n"
        "    ('Pilar 1', 'Tensao in situ', 'StressTensor, PrincipalStress, HorizStressRatio'),\n"
        "    ('Pilar 2', 'Pressao de poros', 'PorePressure, EffectiveStress, BiotCoefficient'),\n"
        "    ('Pilar 3', 'Modulos elasticos', 'YoungModulus [GPa], PoissonRatio [-], ShearModulus [GPa], BulkModulus [GPa]'),\n"
        "    ('Pilar 4', 'Geometria de contencao', 'ContainmentGeometry, FracturePressure, CollapseGradient'),\n"
        "]\n\n"
        "for pilar, nome, props in mem_pillars:\n"
        "    print(f'{pilar}: {nome}')\n"
        "    print(f'  Propriedades: {props}')\n"
        "    print()"
        "\n# Saida esperada: tabela dos 4 pilares do MEM com propriedades"
    ),
    md("## 3. Circulo de Mohr"),
    code(
        "# Estado de tensao sintetico (rocha de reservatorio tipica pre-sal)\n"
        "# Convencao: sigma_1 >= sigma_2 >= sigma_3 (compressao positiva)\n\n"
        "sigma_1 = 60.0  # MPa — tensao principal maxima (litostática)\n"
        "sigma_2 = 45.0  # MPa — tensao principal intermediaria\n"
        "sigma_3 = 30.0  # MPa — tensao principal minima (horizontal minima)\n"
        "pore_p  = 25.0  # MPa — pressao de poros\n\n"
        "# Tensoes efetivas (principio de Terzaghi)\n"
        "s1_eff = sigma_1 - pore_p\n"
        "s3_eff = sigma_3 - pore_p\n\n"
        "# Parametros Mohr-Coulomb\n"
        "cohesion    = 5.0   # MPa\n"
        "friction_deg = 30.0  # graus\n"
        "friction_rad = math.radians(friction_deg)\n\n"
        "print(f'Tensoes totais : sigma_1={sigma_1}, sigma_2={sigma_2}, sigma_3={sigma_3} MPa')\n"
        "print(f'Pressao de poros: {pore_p} MPa')\n"
        "print(f'Tensoes efetivas: sigma_1_eff={s1_eff}, sigma_3_eff={s3_eff} MPa')\n"
        "print(f'Parametros MC  : c={cohesion} MPa, phi={friction_deg}°')"
        "\n# Saida esperada:\n"
        "# Tensoes totais : sigma_1=60.0, sigma_2=45.0, sigma_3=30.0 MPa\n"
        "# Pressao de poros: 25.0 MPa\n"
        "# Tensoes efetivas: sigma_1_eff=35.0, sigma_3_eff=5.0 MPa"
    ),
    code(
        "fig, ax = plt.subplots(figsize=(9, 6))\n\n"
        "# Circulo de Mohr (espaco sigma-tau)\n"
        "center = (s1_eff + s3_eff) / 2\n"
        "radius = (s1_eff - s3_eff) / 2\n"
        "theta = np.linspace(0, 2 * np.pi, 360)\n"
        "sigma_circ = center + radius * np.cos(theta)\n"
        "tau_circ   = radius * np.sin(theta)\n\n"
        "ax.plot(sigma_circ, tau_circ, 'b-', linewidth=2, label='Circulo de Mohr')\n"
        "ax.plot(center, 0, 'bo', markersize=4)\n\n"
        "# Envelope de Mohr-Coulomb: tau = c + sigma * tan(phi)\n"
        "sigma_env = np.linspace(-5, s1_eff + 5, 300)\n"
        "tau_env   = cohesion + sigma_env * math.tan(friction_rad)\n"
        "ax.plot(sigma_env, tau_env, 'r--', linewidth=1.5,\n"
        "        label=f'Envoltoria M-C (c={cohesion} MPa, phi={friction_deg}°)')\n\n"
        "# Pontos notaveis\n"
        "ax.plot([s3_eff, s1_eff], [0, 0], 'b^', markersize=8)\n"
        "ax.annotate(f'sigma_3_eff\\n{s3_eff} MPa', xy=(s3_eff, 0),\n"
        "            xytext=(s3_eff - 4, radius * 0.3),\n"
        "            fontsize=8, arrowprops=dict(arrowstyle='->'))\n"
        "ax.annotate(f'sigma_1_eff\\n{s1_eff} MPa', xy=(s1_eff, 0),\n"
        "            xytext=(s1_eff + 1, radius * 0.3),\n"
        "            fontsize=8, arrowprops=dict(arrowstyle='->'))\n\n"
        "ax.axhline(0, color='k', linewidth=0.5)\n"
        "ax.axvline(0, color='k', linewidth=0.5, linestyle=':')\n"
        "ax.set_xlabel('Tensao Normal Efetiva (MPa)', fontsize=11)\n"
        "ax.set_ylabel('Tensao Cisalhante (MPa)', fontsize=11)\n"
        "ax.set_title('Circulo de Mohr — Estado de Tensao Sintetico\\n'\n"
        "             f'sigma_1={sigma_1}, sigma_2={sigma_2}, sigma_3={sigma_3} MPa; Pp={pore_p} MPa',\n"
        "             fontsize=11)\n"
        "ax.legend(fontsize=9)\n"
        "ax.set_aspect('equal')\n"
        "ax.grid(True, alpha=0.3)\n"
        "plt.tight_layout()\n"
        "plt.show()\n\n"
        "# Verificacao de estabilidade\n"
        "tau_max = radius\n"
        "sigma_at_tau_max = center\n"
        "tau_mc_at_center = cohesion + sigma_at_tau_max * math.tan(friction_rad)\n"
        "stable = tau_max < tau_mc_at_center\n"
        "print(f'tau_max = {tau_max:.2f} MPa')\n"
        "print(f'Envoltoria M-C em sigma={sigma_at_tau_max:.2f}: tau={tau_mc_at_center:.2f} MPa')\n"
        "print(f'Estado de tensao ESTAVEL: {stable}')"
        "\n# Saida esperada:\n"
        "# Circulo de Mohr plotado — o circulo nao toca a envoltoria M-C\n"
        "# tau_max = 15.0 MPa\n"
        "# Estado de tensao ESTAVEL: True"
    ),
    md(
        "O circulo de Mohr representa o estado de tensao efetivo no espaco "
        "tensao-normal / tensao-cisalhante. Quando o circulo toca ou cruza "
        "a envoltoria de Mohr-Coulomb, ocorre ruptura da rocha."
    ),
    md("## 4. Validacao SHACL: StressTensorShape"),
    code(
        "# A restricao StressTensorShape exige: sigma_1 >= sigma_2 >= sigma_3.\n"
        "# Abaixo demonstramos a logica da restricao sem precisar do pyshacl.\n\n"
        "STRESS_SHAPE_RULE = 'StressTensorShape: sigma_1 >= sigma_2 >= sigma_3'\n\n"
        "def validate_stress_tensor(s1: float, s2: float, s3: float) -> dict:\n"
        "    \"\"\"Valida a restricao de ordenacao do tensor de tensao.\"\"\"\n"
        "    violations = []\n"
        "    if not (s1 >= s2):\n"
        "        violations.append(f'sigma_1 ({s1}) < sigma_2 ({s2}) — viola convencao')\n"
        "    if not (s2 >= s3):\n"
        "        violations.append(f'sigma_2 ({s2}) < sigma_3 ({s3}) — viola convencao')\n"
        "    return {'valid': len(violations) == 0, 'violations': violations}\n\n"
        "# Caso 1: valido\n"
        "v1 = validate_stress_tensor(sigma_1, sigma_2, sigma_3)\n"
        "print(f'Caso 1 (sigma_1={sigma_1}, sigma_2={sigma_2}, sigma_3={sigma_3}):')\n"
        "print(f'  Valido: {v1[\"valid\"]}')\n"
        "print(f'  Violacoes: {v1[\"violations\"] or \"nenhuma\"}')\n\n"
        "# Caso 2: invalido (ordem incorreta)\n"
        "v2 = validate_stress_tensor(30.0, 45.0, 60.0)  # ordem invertida\n"
        "print(f'\\nCaso 2 (sigma_1=30, sigma_2=45, sigma_3=60 — ordem invertida):')\n"
        "print(f'  Valido: {v2[\"valid\"]}')\n"
        "print(f'  Violacoes: {v2[\"violations\"]}')"
        "\n# Saida esperada:\n"
        "# Caso 1 (60, 45, 30): Valido: True  Violacoes: nenhuma\n"
        "# Caso 2 (30, 45, 60): Valido: False  Violacoes: ['sigma_1 (30) < sigma_2 (45)...']"
    ),
    code(
        "# Validacao completa via pyshacl (se disponivel)\n"
        "SHAPES_PATH = os.path.join(os.path.dirname(os.getcwd()), 'data', 'geolytics-shapes.ttl')\n"
        "VOCAB_PATH  = os.path.join(os.path.dirname(os.getcwd()), 'data', 'geolytics-vocab.ttl')\n\n"
        "try:\n"
        "    import pyshacl\n"
        "    from rdflib import Graph, Literal, Namespace, RDF\n"
        "    from rdflib.namespace import XSD\n\n"
        "    GEO = Namespace('https://geolytics.petrobras.com.br/dict/')\n\n"
        "    def make_stress_graph(s1: float, s2: float, s3: float) -> Graph:\n"
        "        g = Graph()\n"
        "        node = GEO.SyntheticTensor1\n"
        "        g.add((node, RDF.type, GEO.StressTensor))\n"
        "        g.add((node, GEO.sigma_1, Literal(s1, datatype=XSD.float)))\n"
        "        g.add((node, GEO.sigma_2, Literal(s2, datatype=XSD.float)))\n"
        "        g.add((node, GEO.sigma_3, Literal(s3, datatype=XSD.float)))\n"
        "        return g\n\n"
        "    shapes_graph = Graph().parse(SHAPES_PATH, format='turtle')\n"
        "    vocab_graph  = Graph().parse(VOCAB_PATH,  format='turtle')\n\n"
        "    for label, s1, s2, s3 in [('Valido', 60, 45, 30), ('Invalido', 30, 45, 60)]:\n"
        "        data_g = make_stress_graph(s1, s2, s3)\n"
        "        conforms, _, report_text = pyshacl.validate(\n"
        "            data_g,\n"
        "            shacl_graph=shapes_graph,\n"
        "            ont_graph=vocab_graph,\n"
        "            inference='rdfs',\n"
        "        )\n"
        "        print(f'[{label}] sigma_1={s1}, sigma_2={s2}, sigma_3={s3}')\n"
        "        print(f'  Conforms: {conforms}')\n"
        "        if not conforms:\n"
        "            for line in report_text.strip().splitlines()[:5]:\n"
        "                print(f'  {line}')\n"
        "        print()\n\n"
        "except ImportError:\n"
        "    print('pyshacl nao disponivel — usando validacao Python nativa (celula anterior)')\n"
        "    print('Para instalar: pip install pyshacl rdflib')"
        "\n# Saida esperada (com pyshacl):\n"
        "# [Valido]   Conforms: True\n"
        "# [Invalido] Conforms: False\n"
        "#   Violation of sh:constraint ... sigma_1 < sigma_2"
    ),
    md("## 5. Crosswalk fratura -> GSO/Loop3D"),
    code(
        "print('Mapeamentos Geolytics Fratura -> GSO/Loop3D:')\n"
        "print('=' * 60)\n\n"
        "for mapping in frac_gso:\n"
        "    geo_id  = mapping.get('geo_id', mapping.get('geolytics_id', '?'))\n"
        "    geo_nm  = mapping.get('geo_label', mapping.get('geolytics_label', '?'))\n"
        "    gso_uri = mapping.get('gso_uri', '?')\n"
        "    gso_nm  = mapping.get('gso_label', '?')\n"
        "    rel     = mapping.get('skos_relation', mapping.get('relation', '?'))\n"
        "    print(f'{geo_nm} ({geo_id})')\n"
        "    print(f'  --[{rel}]--> {gso_nm}')\n"
        "    print(f'  GSO URI: {gso_uri}')\n"
        "    print()"
        "\n# Saida esperada:\n"
        "# FaultZone (GF002)\n"
        "#   --[skos:exactMatch]--> gso:FaultZone\n"
        "#   GSO URI: https://w3id.org/gso/1.0/geology/FaultZone\n"
        "# ..."
    ),
    code(
        "# Visualizacao tabular dos mapeamentos\n"
        "import collections\n\n"
        "rel_types = collections.Counter(\n"
        "    m.get('skos_relation', m.get('relation', 'unknown')) for m in frac_gso\n"
        ")\n\n"
        "fig, ax = plt.subplots(figsize=(7, 3))\n"
        "ax.bar(rel_types.keys(), rel_types.values(), color=['#378ADD', '#4CAF50', '#F4A522'][:len(rel_types)])\n"
        "ax.set_title('Tipos de relacao SKOS no crosswalk Fratura -> GSO', fontsize=11)\n"
        "ax.set_xlabel('Tipo de relacao SKOS')\n"
        "ax.set_ylabel('Numero de mapeamentos')\n"
        "plt.tight_layout()\n"
        "plt.show()"
        "\n# Saida esperada: grafico de barras com exactMatch, closeMatch, broadMatch"
    ),
    md("## 6. Consulta textual nas classes de geomecanica"),
    code(
        "def search_geomec(query: str, top_k: int = 5) -> list[dict]:\n"
        "    \"\"\"Busca textual simples nas classes da ontologia geomecanica.\"\"\"\n"
        "    query_lower = query.lower()\n"
        "    all_classes = geomec.get('classes', []) + geomec_frac.get('classes', [])\n"
        "    results = []\n"
        "    for cls in all_classes:\n"
        "        score = 0\n"
        "        text = (cls.get('description', '') + ' ' + cls.get('description_pt', '')).lower()\n"
        "        for token in query_lower.split():\n"
        "            if token in text:\n"
        "                score += text.count(token)\n"
        "        if score > 0:\n"
        "            results.append({'class': cls['name'], 'id': cls['id'], 'score': score,\n"
        "                            'desc_pt': cls.get('description_pt', '')[:120]})\n"
        "    return sorted(results, key=lambda x: -x['score'])[:top_k]\n\n"
        "QUERY_MEM = 'propriedades elasticas modulo Young medidas testemunho'\n"
        "hits = search_geomec(QUERY_MEM)\n\n"
        "print(f'Query: \"{QUERY_MEM}\"')\n"
        "print('=' * 60)\n"
        "for h in hits:\n"
        "    print(f\"#{h['id']}  {h['class']}  (score={h['score']})\")\n"
        "    print(f\"  {h['desc_pt']}...\")\n"
        "    print()"
        "\n# Saida esperada:\n"
        "# #GM007 YoungModulus (score alto)\n"
        "#   Razao entre tensao axial e deformacao axial...\n"
        "# #GM008 PoissonRatio\n"
        "# ..."
    ),
    md(
        "## Resumo\n\n"
        "Neste notebook:\n\n"
        "- Identificamos os **4 pilares do MEM 1D** e suas propriedades na ontologia Geolytics.\n"
        "- Plotamos o **Circulo de Mohr** para um estado de tensao sintetico tipico do pre-sal.\n"
        "- Demonstramos a restricao SHACL `StressTensorShape` em datasets sinteticos.\n"
        "- Realizamos o crosswalk de 8 classes de fraturas para o vocabulario GSO/Loop3D.\n\n"
        "Para aprofundamento, veja `docs/GEOMECHANICS.md` e `docs/SHACL.md` "
        "no repositorio."
    ),
]

# ===========================================================================
# main
# ===========================================================================

def main() -> None:
    print("Gerando notebooks Geolytics...")
    print()
    save("01_explore_graph.ipynb",        nb(NB1_CELLS))
    save("02_rag_with_validator.ipynb",   nb(NB2_CELLS))
    save("03_langgraph_multiagent.ipynb", nb(NB3_CELLS))
    save("04_geomec_qa.ipynb",            nb(NB4_CELLS))
    print()
    print("Verificando JSON...")
    import glob
    for path in sorted(glob.glob(os.path.join(NOTEBOOKS_DIR, "*.ipynb"))):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        assert "cells" in data
        assert data["nbformat"] == 4
        print(f"  OK  {os.path.basename(path)}  ({len(data['cells'])} celulas)")
    print()
    print("Todos os notebooks gerados e validados.")


if __name__ == "__main__":
    main()
