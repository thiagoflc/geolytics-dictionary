# Geolytics Dictionary

Ontologia semântica do domínio de **Exploração & Produção (E&P) de petróleo e gás natural no Brasil**, derivada do módulo Dicionário da plataforma Geolytics. Dados oficiais da **ANP/SEP — SIGEP**, organizados como JSON estático, grafo de entidades e corpus pronto para RAG.

**Visualização interativa:** https://ORG_OR_USER.github.io/geolytics-dictionary

---

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `data/glossary.json` | 23 termos ANP (definição, fonte legal, categoria, datasets onde aparece) |
| `data/datasets.json` | 8 datasets ANP/SEP-SIGEP com metadados de colunas |
| `data/entity-graph.json` | Grafo de 21 entidades + 21 relações (nodes/edges) |
| `data/ontology-types.json` | Tipologia geoquímica (7) + níveis de processamento (3) + 4 domínios |
| `data/full.json` | Merge de tudo acima |
| `api/v1/index.json` | Manifesto da API com URLs de todos os endpoints |
| `api/v1/terms.json` | Lista plana de termos |
| `api/v1/entities.json` | Entidades com relações outgoing/incoming pré-computadas |
| `api/v1/datasets.json` | Datasets com lista de termos referenciados |
| `api/v1/search-index.json` | Índice de busca client-side (id, text, type, tokens) |
| `ai/rag-corpus.jsonl` | 145 chunks para embedding (term, column, entity, domain, type) |
| `ai/system-prompt-ptbr.md` | System prompt PT-BR (~800 tokens) |
| `ai/system-prompt-en.md` | System prompt EN (~800 tokens) |
| `index.html` | Visualização D3 interativa (GitHub Pages) |
| `scripts/generate.js` | Regenera `/data`, `/api` e `/ai` |

---

## Como usar os dados

### Via raw GitHub

```
https://raw.githubusercontent.com/ORG_OR_USER/geolytics-dictionary/main/data/glossary.json
https://raw.githubusercontent.com/ORG_OR_USER/geolytics-dictionary/main/data/entity-graph.json
https://raw.githubusercontent.com/ORG_OR_USER/geolytics-dictionary/main/ai/rag-corpus.jsonl
```

### Via GitHub Pages

```
https://ORG_OR_USER.github.io/geolytics-dictionary/api/v1/index.json
https://ORG_OR_USER.github.io/geolytics-dictionary/data/full.json
https://ORG_OR_USER.github.io/geolytics-dictionary/ai/rag-corpus.jsonl
```

### Carregando o RAG corpus em LangChain (Python)

```python
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import urllib.request, json

URL = "https://ORG_OR_USER.github.io/geolytics-dictionary/ai/rag-corpus.jsonl"
docs = []
with urllib.request.urlopen(URL) as f:
    for line in f:
        rec = json.loads(line)
        docs.append({"page_content": rec["text"], "metadata": rec["metadata"] | {"id": rec["id"], "type": rec["type"]}})

vs = FAISS.from_texts(
    [d["page_content"] for d in docs],
    OpenAIEmbeddings(),
    metadatas=[d["metadata"] for d in docs],
)
```

### Carregando em LlamaIndex (Python)

```python
from llama_index.core import Document, VectorStoreIndex
import urllib.request, json

URL = "https://ORG_OR_USER.github.io/geolytics-dictionary/ai/rag-corpus.jsonl"
documents = []
with urllib.request.urlopen(URL) as f:
    for line in f:
        rec = json.loads(line)
        documents.append(Document(text=rec["text"], metadata={**rec["metadata"], "id": rec["id"], "type": rec["type"]}))

index = VectorStoreIndex.from_documents(documents)
```

### Usando o system prompt

Leia o conteúdo de `ai/system-prompt-ptbr.md` (ou `ai/system-prompt-en.md`) e use-o como mensagem de sistema do seu agente conversacional. Ele estabelece o contexto de domínio, define as entidades-chave e explicita os termos que tipicamente confundem modelos genéricos (PAD, UTS, Período Exploratório, Pré-sal, Concessão vs. Partilha).

---

## Modelo de entidades

| Tipo | Cor | Entidades |
|---|---|---|
| **operational** | `#378ADD` | Poço, Bloco, Campo, Bacia Sedimentar |
| **contractual** | `#7F77DD` | Contrato E&P, PAD, Rodada de Licitação, Declaração de Comercialidade |
| **actor** | `#D85A30` | Operador, ANP |
| **instrument** | `#888780` | SIGEP, SEP, UTS, Regime Contratual, Período Exploratório, Processo Sancionador, Notificação Descoberta, Área de Desenvolvimento |
| **geological** | `#639922` | Pré-sal, Bacias Agrupadas, Ambiente |

Relações entre entidades são tipadas (`drilled_in`, `governed_by`, `evaluates`, `originates`, etc.) e classificadas como `solid` (sempre presente) ou `dashed` (condicional).

---

## Sobre o Petro KGraph

Os campos `kgraph_uri`, `kgraph_label_pt`, `kgraph_label_en` referenciam o **Petro KGraph** — ontologia formal do domínio Óleo & Gás em português desenvolvida pela **PUC-Rio / PetroNLP** com **539 conceitos formais**. No estado atual deste repositório esses campos são `null` para todas as entidades; o enriquecimento via Petro KGraph é feito sob demanda no app Geolytics e pode ser portado aqui em release futura.

---

## Fontes

- **Lei nº 9.478/1997** (Lei do Petróleo) — instituiu a ANP e o atual marco regulatório de E&P no Brasil.
- **ANP — Agência Nacional do Petróleo, Gás Natural e Biocombustíveis** — autarquia federal regulatória.
- **SEP — Superintendência de Exploração** da ANP.
- **SIGEP — Sistema de Informações Gerenciais de Exploração e Produção**.
- Resoluções ANP nº 708/2017 e nº 815/2020.
- Contato dos datasets: `sigep_sep@anp.gov.br`.

---

## Regenerando os dados

```bash
node scripts/generate.js
```

O script regrava todos os arquivos em `/data`, `/api/v1` e `/ai`. Os dados-fonte (GLOSSARIO, CONJUNTOS, ONTOLOGY, DOMAINS, ENTITY_NODES, EDGES) ficam embedados no próprio script — para sincronizar com o Geolytics, copie os exports de `src/config/dicionario.js` e `src/config/ontology.js`.

---

## Licença

- **Código** (`scripts/`, `index.html`): MIT.
- **Dados** (`data/`, `api/`, `ai/`): derivados de informações públicas da ANP/SEP. Uso livre para fins educacionais, de pesquisa e desenvolvimento, mantendo a atribuição à fonte original.
