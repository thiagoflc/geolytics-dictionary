# Siglario O&G

O arquivo `data/acronyms.json` contem 1.102 siglas curadas do dominio oleo e gas (PT/EN), categorizadas a partir de fonte comunitaria.

---

## Estrutura de cada entrada

```json
{
  "id": "bop",
  "sigla": "BOP",
  "expansion_pt": "Preventor de Erupcao, Obturador de Seguranca",
  "expansion_en": "Blowout Preventer",
  "category": "equipment",
  "it_generic": false
}
```

| Campo | Descricao |
|---|---|
| `id` | Identificador unico (lowercase, slugificado) |
| `sigla` | Sigla em maiusculas |
| `expansion_pt` | Expansao em portugues |
| `expansion_en` | Expansao em ingles |
| `category` | Categoria tematica (ver abaixo) |
| `it_generic` | `true` se a sigla e generica de TI (excluida do RAG corpus) |

---

## Categorias e contagens

| Categoria | Count | Exemplos |
|---|---|---|
| `equipment` | 180 | BOP, FPSO, ANM, ROV, BHA, ESP |
| `measurement` | 122 | TVD, MD, WOB, ROP, GOR |
| `fluid` | 113 | OBM, WBM, PVT, GOR, CGR |
| `process` | 74 | EIA, RIMA, AFE, JOA, EPC |
| `environmental` | 53 | APA, REBIO, RPPN, CONAMA, IBAMA |
| `standard_body` | 51 | ANP, SPE, OSDU, IOGP, API |
| `contract` | 47 | PAD, UTS, PE, DC, CE |
| `unit` | 40 | MMboe, bcf, psi, ppg, SG |
| `lithology` | 39 | ETR, REG, CAL, CRB |
| `geophysics` | 33 | AVO, DHI, NMO, CDP, VSP |
| `well_state` | 14 | TAS, TAP, TCO, TSS |
| `regulator` | 14 | ANP, ANEEL, ANVISA, INEA |
| `it_generic` | 23 | CMOS, RAM, FFT, OSI |
| `general` | 294 | diversos |
| `organization` | 5 | IBP, BNDES, ABNT |

---

## Siglas com multiplos sentidos

A mesma sigla pode ter varias entradas. O campo `id` distingue cada sentido:

| Sigla | Sentido 1 | Sentido 2 | Sentido 3 |
|---|---|---|---|
| `PAD` | Plano de Avaliacao de Descobertas (contrato ANP) | Drilling Pad (pad de perfuracao) | — |
| `UTS` | Unidades de Trabalho Sismico (metrica PEM) | Ultimate Tensile Strength (resistencia a tracao) | — |
| `BO` | Barrels of Oil | Bottom Oil | — |
| `BT` | Total Formation Volume Factor | Bathythermograph | Build and Transfer |
| `API` | American Petroleum Institute | Grau API (densidade) | — |

Siglas ambigas devem incluir contexto de desambiguacao. O validador semantico emite `ACRONYM_AMBIGUOUS` quando detecta uso de PAD ou UTS sem contexto suficiente.

---

## Filtragem para RAG

Siglas com `it_generic: true` (CMOS, RAM, FFT, OSI, etc.) sao excluidas do `ai/rag-corpus.jsonl` para nao competir com o sinal de dominio O&G. Continuam no JSON para referencia completa.

---

## Regenerando

```bash
node scripts/build-acronyms.js
```

Reprocessa `scripts/acronyms-source.txt` → `data/acronyms.json`.

---

## Via API e MCP

```
# API REST estatica
api/v1/acronyms.json         — siglas com counts por categoria

# MCP Server
expand_acronym({ sigla: "BOP" })
expand_acronym({ sigla: "PAD" })  # retorna todas as expansoes com hint de desambiguacao
```
