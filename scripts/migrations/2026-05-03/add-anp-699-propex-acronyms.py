#!/usr/bin/env python3
"""Add ANP-699/2017 + PROPEX/GPP acronyms to data/acronyms.json.

Source documents:
  - Resolução ANP nº 699/2017 (codificação de poços, definição de Resultado e
    Status, envio de relatórios). 18 documentos com prazos legais.
  - Material corporativo PROPEX (Programa Exploratório Petrobras): governança,
    portões decisórios PEXP, PGP, TEP, ISA, fóruns COMEXP/GRBLOC/GRT.
  - Conceitos regulatórios derivados do Bloco: PEM, PAD, DC, PD/PDP.

Collisions: several siglas (CRP, DC, FP, ISA, PD, PVT, SOP, TEP) already exist
in acronyms.json with different domain meanings (geophysics, drilling,
finance). New entries get a domain-suffixed id (e.g. `fp-anp`, `dc-anp`) so
both meanings coexist — same sigla, different ids, different categories.

Adds the new boolean field `corporate_internal` to flag Petrobras-internal
governance terminology vs. ANP-public regulatory terminology. Existing
entries are NOT modified (absence of the field is implicitly false).

Idempotent — re-running on a patched JSON is a no-op.
Usage: python3 scripts/migrations/2026-05-03/add-anp-699-propex-acronyms.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "data" / "acronyms.json"

# ---------------------------------------------------------------------------
# New entries
# ---------------------------------------------------------------------------
# Convention:
#   - Each entry gets a unique `id` (lowercased; collisions get `-anp` / `-corp`
#     suffix to avoid clashing with existing entries).
#   - `category`: best fit from existing taxonomy (regulator, process,
#     it_generic). No new categories introduced.
#   - `corporate_internal`: true for Petrobras-internal governance (PROPEX,
#     PEXP, PGP, TEP, ISA, COMEXP, GRBLOC, GRT). False for ANP-public.
#   - `domain`: free-text routing hint (matches existing convention).
#   - `evidence_refs`: pointer to source document(s).

NEW_ENTRIES = [
    # === ANP-699/2017 documents (regulator, public) ===
    {
        "id": "npp-anp",
        "sigla": "NPP",
        "expansion_pt": "Notificação de Perfuração de Poço",
        "expansion_en": "Well Drilling Notification",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "cipp-anp",
        "sigla": "CIPP",
        "expansion_pt": "Comunicação de Início de Perfuração de Poço",
        "expansion_en": "Well Spud Notice",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "cuepp-anp",
        "sigla": "CUEPP",
        "expansion_pt": "Comunicação de Utilização de Equipamento de Pequeno Porte",
        "expansion_en": "Small-Scale Equipment Use Notice",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "crp-anp",
        "sigla": "CRP",
        "expansion_pt": "Comunicação de Reentrada em Poço",
        "expansion_en": "Well Re-entry Notice",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
        "collision_note": "Collides with sigla CRP (geophysics: Common Reflection Point).",
    },
    {
        "id": "ncrp-anp",
        "sigla": "NCRP",
        "expansion_pt": "Notificação de Conclusão de Reentrada em Poço",
        "expansion_en": "Well Re-entry Conclusion Notification",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "nd-anp",
        "sigla": "ND",
        "expansion_pt": "Notificação de Descoberta",
        "expansion_en": "Discovery Notification",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "npr-anp",
        "sigla": "NPR",
        "expansion_pt": "Notificação de Perfilagens Realizadas",
        "expansion_en": "Logging Operations Notification",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "ncsb-anp",
        "sigla": "NCSB",
        "expansion_pt": "Notificação de Conjuntos Solidários de Barreira",
        "expansion_en": "Well Barrier Envelope Notification",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017", "ANP-46/2016"],
    },
    {
        "id": "laep-anp",
        "sigla": "LAEP",
        "expansion_pt": "Licença Ambiental para atividades de Exploração e Produção",
        "expansion_en": "Environmental License (Exploration & Production)",
        "category": "environmental",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp_ibama",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "sop-anp",
        "sigla": "SOP",
        "expansion_pt": "Situação Operacional de Poços",
        "expansion_en": "Daily Well Operational Status Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
        "collision_note": "Collides with sigla SOP (Standard Operating Procedure / Sistema Operacional).",
    },
    {
        "id": "fp-anp",
        "sigla": "FP",
        "expansion_pt": "Relatório Final de Perfuração",
        "expansion_en": "Final Drilling Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
        "collision_note": "Collides with sigla FP (Flowing Pressure / Pressão de Fluxo).",
    },
    {
        "id": "rfap-anp",
        "sigla": "RFAP",
        "expansion_pt": "Relatório Final de Abandono de Poço",
        "expansion_en": "Final Well Abandonment Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "rcp-anp",
        "sigla": "RCP",
        "expansion_pt": "Relatório de Completação de Poço",
        "expansion_en": "Well Completion Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "rfp-anp",
        "sigla": "RFP",
        "expansion_pt": "Relatório Final de Poço Exploratório",
        "expansion_en": "Final Exploratory Well Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "rfp-prod-anp",
        "sigla": "RFP-PROD",
        "expansion_pt": "Relatório Final de Poço Explotatório",
        "expansion_en": "Final Production Well Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "rpf-anp",
        "sigla": "RPF",
        "expansion_pt": "Relatório de Ensaios Petrofísicos",
        "expansion_en": "Petrophysical Tests Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "pvt-rep-anp",
        "sigla": "PVT",
        "expansion_pt": "Relatório de Ensaios de PVT (Pressão-Volume-Temperatura)",
        "expansion_en": "PVT Tests Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
        "collision_note": "Distinct from existing PVT acronym (Pressure-Volume-Temperature property/concept). This entry refers specifically to the regulatory report deliverable.",
    },
    {
        "id": "rgp-anp",
        "sigla": "RGP",
        "expansion_pt": "Relatório de Geoquímica de Poço",
        "expansion_en": "Well Geochemistry Report",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "i-sigep",
        "sigla": "i-SIGEP",
        "expansion_pt": "Sistema integrado de gestão de exploração e produção da ANP",
        "expansion_en": "ANP Integrated E&P Management System",
        "category": "it_generic",
        "it_generic": True,
        "corporate_internal": False,
        "domain": "sistemas_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    {
        "id": "i-engine",
        "sigla": "i-ENGINE",
        "expansion_pt": "Sistema ANP de envio de SOP/TLD/relatórios diários",
        "expansion_en": "ANP daily-reporting system",
        "category": "it_generic",
        "it_generic": True,
        "corporate_internal": False,
        "domain": "sistemas_anp",
        "evidence_refs": ["ANP-699/2017"],
    },
    # === Regulatórios derivados do Bloco (ANP-public) ===
    {
        "id": "pem",
        "sigla": "PEM",
        "expansion_pt": "Programa Exploratório Mínimo",
        "expansion_en": "Minimum Exploratory Program",
        "category": "contract",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "contrato_anp",
        "evidence_refs": ["Lei 9.478/1997", "Contratos de Concessão ANP"],
    },
    {
        "id": "pad",
        "sigla": "PAD",
        "expansion_pt": "Plano de Avaliação de Descoberta",
        "expansion_en": "Discovery Evaluation Plan",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["Lei 9.478/1997", "Resolução ANP 47/2014"],
    },
    {
        "id": "dc-anp",
        "sigla": "DC",
        "expansion_pt": "Declaração de Comercialidade",
        "expansion_en": "Commerciality Declaration",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["Lei 9.478/1997", "Contratos de Concessão ANP"],
        "collision_note": "Collides with sigla DC (Drill Collar / Comando de Perfuração).",
    },
    {
        "id": "pd-anp",
        "sigla": "PD",
        "expansion_pt": "Plano de Desenvolvimento",
        "expansion_en": "Development Plan",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["Lei 9.478/1997", "Resolução ANP 17/2015"],
        "collision_note": "Collides with sigla PD (Positive Displacement).",
    },
    {
        "id": "pdp",
        "sigla": "PDP",
        "expansion_pt": "Plano de Desenvolvimento da Produção",
        "expansion_en": "Production Development Plan",
        "category": "regulator",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "regulatorio_anp",
        "evidence_refs": ["Resolução ANP 17/2015"],
    },
    # === PROPEX governance (Petrobras-internal) ===
    {
        "id": "propex",
        "sigla": "PROPEX",
        "expansion_pt": "Programa Exploratório (governança Petrobras de projetos exploratórios)",
        "expansion_en": "Exploratory Program (Petrobras governance program)",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025", "PE-2EXP-PROPEX"],
    },
    {
        "id": "pexp",
        "sigla": "PEXP",
        "expansion_pt": "Portões Decisórios do PROPEX (eventos de aprovação)",
        "expansion_en": "PROPEX Decision Gates",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "pexp1",
        "sigla": "PEXP1",
        "expansion_pt": "PEXP fase 1 — aprovação da estratégia do Bloco",
        "expansion_en": "PROPEX Gate 1 — Block strategy approval",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "pexp2",
        "sigla": "PEXP2",
        "expansion_pt": "PEXP fase 2 — aprovação do PAD ou devolução total",
        "expansion_en": "PROPEX Gate 2 — PAD approval or full relinquishment",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "pexp2a",
        "sigla": "PEXP2A",
        "expansion_pt": "PEXP fase 2A — revisão do PEM ou devolução parcial",
        "expansion_en": "PROPEX Gate 2A — PEM review or partial relinquishment",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "pexp3",
        "sigla": "PEXP3",
        "expansion_pt": "PEXP fase 3 — declaração de comercialidade ou devolução",
        "expansion_en": "PROPEX Gate 3 — commerciality declaration or relinquishment",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "pexp3a",
        "sigla": "PEXP3A",
        "expansion_pt": "PEXP fase 3A — revisão do PAD",
        "expansion_en": "PROPEX Gate 3A — PAD review",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "pgp",
        "sigla": "PGP",
        "expansion_pt": "Plano de Gerenciamento de Projetos (escopo, cronograma, custo, riscos)",
        "expansion_en": "Project Management Plan",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "tep-anp",
        "sigla": "TEP",
        "expansion_pt": "Termo de Encerramento do Projeto (PROPEX)",
        "expansion_en": "Project Closure Term",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
        "collision_note": "Collides with sigla TEP (Tonne of Oil Equivalent).",
    },
    {
        "id": "isa-corp",
        "sigla": "ISA",
        "expansion_pt": "Instrumento de Situação do Ativo (transição Exp→Prod)",
        "expansion_en": "Asset Status Instrument",
        "category": "process",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
        "collision_note": "Collides with sigla ISA (International Society of Automation).",
    },
    {
        "id": "comexp",
        "sigla": "COMEXP",
        "expansion_pt": "Comitê de Gestão da Exploração",
        "expansion_en": "Exploration Management Committee",
        "category": "organization",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025", "PROPEX wiki"],
    },
    {
        "id": "grbloc",
        "sigla": "GRBLOC",
        "expansion_pt": "Grupo Técnico de Blocos (revisão pré-COMEXP)",
        "expansion_en": "Block Technical Review Group",
        "category": "organization",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    {
        "id": "grt",
        "sigla": "GRT",
        "expansion_pt": "Grupo de Revisão Técnica (apoio aos PEXPs)",
        "expansion_en": "Technical Review Group",
        "category": "organization",
        "it_generic": False,
        "corporate_internal": True,
        "domain": "governanca_exploratoria",
        "evidence_refs": ["Curso PROPEX 2024/2025"],
    },
    # === Gestão de portfólio (mixed corporate/industry-standard) ===
    {
        "id": "wi",
        "sigla": "WI",
        "expansion_pt": "Participação (Working Interest)",
        "expansion_en": "Working Interest",
        "category": "contract",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "gestao_portfolio",
        "evidence_refs": ["SPE Reserves Definitions"],
    },
    {
        "id": "vme",
        "sigla": "VME",
        "expansion_pt": "Valor Monetário Esperado",
        "expansion_en": "Expected Monetary Value",
        "category": "general",
        "it_generic": False,
        "corporate_internal": False,
        "domain": "avaliacao_economica",
        "evidence_refs": ["SPE/AAPG decision-analysis literature"],
    },
]


# ---------------------------------------------------------------------------
# Migration logic
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print summary, do not write")
    args = parser.parse_args()

    if not TARGET.exists():
        print(f"ERROR: target file not found: {TARGET}", file=sys.stderr)
        return 2

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    existing_ids = {a["id"] for a in data["acronyms"]}
    to_add = [e for e in NEW_ENTRIES if e["id"] not in existing_ids]
    skipped = [e for e in NEW_ENTRIES if e["id"] in existing_ids]

    print(f"Found {len(data['acronyms'])} existing acronyms")
    print(f"Proposed {len(NEW_ENTRIES)} new entries; {len(to_add)} truly new, {len(skipped)} already present")
    if skipped:
        for s in skipped:
            print(f"  SKIP (id already exists): {s['id']} = {s['sigla']}")

    if not to_add:
        print("Nothing to do.")
        return 0

    print("\nAdding:")
    for e in to_add:
        flag = " [corp]" if e.get("corporate_internal") else ""
        print(f"  + {e['id']:<14} {e['sigla']:<10} {e['expansion_pt']}{flag}")

    if args.dry_run:
        print("\n--dry-run set; not writing.")
        return 0

    data["acronyms"].extend(to_add)

    # Refresh meta counters
    data["meta"]["total"] = len(data["acronyms"])
    data["meta"]["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    data["meta"]["by_category"] = dict(
        sorted(Counter(a["category"] for a in data["acronyms"]).items())
    )

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {TARGET.relative_to(ROOT)} — new total: {data['meta']['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
