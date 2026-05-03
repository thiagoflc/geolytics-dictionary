# Migrations — 2026-05-03

One-shot data-governance scripts applied on **2026-05-03** to enrich the
graph and RAG corpus with regulatory and corporate-governance vocabulary
extracted from:

- **Resolução ANP nº 699/2017** — codificação de poços, definição de
  Resultado e Status, envio de relatórios para acompanhamento.
- **Material PROPEX** (Petrobras Programa Exploratório) — governança,
  portões decisórios PEXP, PGP, TEP, ISA, fóruns COMEXP/GRBLOC/GRT.
- **Conceitos regulatórios derivados do Bloco** — PEM, PAD, DC, PD/PDP.

## Scripts (executar nesta ordem)

| Script | Purpose | Status |
|---|---|---|
| `add-anp-699-propex-acronyms.py` | Added 40 acronyms (18 ANP-699 documents + 5 derived regulatory + 13 PROPEX-internal + 4 portfolio). Introduced `corporate_internal` boolean field. Coexists with existing siglas via id-suffixing (e.g. `dc-anp` vs existing `dc`). | ✅ Applied |
| `extend-anp-osdu-wellstatus-map.py` | Added 18 new ANP-699 statuses to the well-status crosswalk. Backfilled `anp_source` field on the 18 legacy ANP-25/2015 entries. Updated meta with multi-source description. | ✅ Applied |
| `build-anp-codelists.py` | Generated `data/anp-uf.json` (27 UFs with IBGE acronyms + maritime suffix) and `data/anp-bacia-sedimentar.json` (79 sedimentary basins with TERRA/MAR pairs from Anexo II). | ✅ Applied |
| `extend-og-with-anp-699-docs.py` | Added 18 ANP-699 doc classes (NPP/CIPP/CUEPP/LAEP/SOP_ANP/ND/NPR/FP_ANP/RFAP/RCP/RFP/RFP_PROD/CRP_ANP/NCRP/RPF/PVT_Report/RGP/NCSB) to `data/operacoes-geologicas.json` as subclasses of `GeologicalOperationsDocument`. Added `Poco` class with full ANP attributes (cadastro_anp regex, categoria/tipo/resultado/status enums). Added `OG_DOC_LINEAGE_ANP` instance with the canonical regulatory document chain. | ✅ Applied |

## Companion source-of-truth files (manually authored, not migrations)

| File | Purpose |
|---|---|
| `data/anp-poco-categoria.json` | 10 Categorias ANP-699 (Tabela 1) — well finality codelist |
| `data/anp-poco-tipo.json` | 6 Tipos ANP-699 (art. 4º §4) — well trajectory codelist |
| `data/anp-poco-resultado.json` | 3 Resultados (Cap. III) + 4 atributos complementares (art. 7º) |
| `data/gestao-projetos-parcerias.json` | New domain module — 28 classes covering Bloco lifecycle states, PROPEX governance, PEXP gates, PAD/DC/PD chain, partnership management |
| `scripts/gestao-projetos-parcerias-nodes.js` | Entity-graph nodes/edges/glossary for the GPP module + 4 in-place patches for existing entries (pem/pad/contrato-ep/declaracao-comercialidade) |

## Re-running for audit

```bash
python3 scripts/migrations/2026-05-03/<script>.py --dry-run
```

Both scripts are idempotent; re-applying on patched JSON is a no-op.

## Adding a new migration

Follow the template in `scripts/migrations/2026-05-02/README.md`.
