#!/usr/bin/env python3
"""Extend data/anp-osdu-wellstatus-map.json with the 19 statuses from
Resolução ANP nº 699/2017 (Tabela 2).

The current file maps Resolução ANP 25/2015 codes (older taxonomy of well
type/situation). The 699/2017 introduces a different status set focused on
operational state in the well lifecycle. Both coexist in regulatory practice.

To keep both sources distinguishable, a new field `anp_source` is added to
each mapping ("ANP-25/2015" for legacy entries, "ANP-699/2017" for new). The
meta block is extended with a `sources` list and total_mappings is recounted.

Idempotent — re-running on a patched JSON is a no-op.
Usage: python3 scripts/migrations/2026-05-03/extend-anp-osdu-wellstatus-map.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "data" / "anp-osdu-wellstatus-map.json"

ANP_699_MAPPINGS = [
    {
        "anp_code": "ABANDONADO_PERMANENTE",
        "anp_label_pt": "Abandonado permanentemente",
        "anp_label_en": "Permanently abandoned",
        "osdu_value": "Plugged and Abandoned",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "exactMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well with no future re-entry interest; permanent barrier envelopes established (NCSB).",
    },
    {
        "anp_code": "ABANDONADO_TEMP_MONITORADO",
        "anp_label_pt": "Abandonado temporariamente com monitoramento",
        "anp_label_en": "Temporarily abandoned with monitoring",
        "osdu_value": "Temporarily Abandoned",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "exactMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Re-entry intended; barrier envelopes periodically monitored. Reason for temp abandonment must be in observations.",
    },
    {
        "anp_code": "ABANDONADO_TEMP_NAO_MONITORADO",
        "anp_label_pt": "Abandonado temporariamente sem monitoramento",
        "anp_label_en": "Temporarily abandoned without monitoring",
        "osdu_value": "Temporarily Abandoned",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Re-entry intended; barriers in place but not actively monitored. Reason must be in observations.",
    },
    {
        "anp_code": "ARRASADO",
        "anp_label_pt": "Arrasado",
        "anp_label_en": "Razed (wellhead removed and capped)",
        "osdu_value": "Plugged and Abandoned",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Permanent abandonment with full wellhead removal and conductor cut to ground level (terrestre) or per regulation depth (marítimo).",
    },
    {
        "anp_code": "PRODUZINDO",
        "anp_label_pt": "Produzindo",
        "anp_label_en": "Producing",
        "osdu_value": "Producing",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "exactMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well operating as hydrocarbon producer. Losses must be reported in observations.",
    },
    {
        "anp_code": "INJETANDO",
        "anp_label_pt": "Injetando",
        "anp_label_en": "Injecting",
        "osdu_value": "Injection",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "exactMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well operating as fluid injector for improved hydrocarbon recovery.",
    },
    {
        "anp_code": "PRODUZINDO_INJETANDO",
        "anp_label_pt": "Produzindo e injetando",
        "anp_label_en": "Producing and injecting (dual completion or auto-injection)",
        "osdu_value": "Producing",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Simultaneous production and injection in distinct intervals (dual completion or auto-injection). OSDU has no dedicated dual-mode value; closest is Producing.",
    },
    {
        "anp_code": "RETIRANDO_GAS_ESTOCAGEM",
        "anp_label_pt": "Retirando gás natural estocado",
        "anp_label_en": "Withdrawing stored natural gas",
        "osdu_value": "Producing",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Underground gas storage withdrawal. ANP categoria 10 (Poço de Estocagem). OSDU lacks a storage-specific value.",
    },
    {
        "anp_code": "INJETANDO_ESTOCAGEM",
        "anp_label_pt": "Injetando para estocagem",
        "anp_label_en": "Injecting for storage",
        "osdu_value": "Injection",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Underground gas storage injection. ANP categoria 10 (Poço de Estocagem).",
    },
    {
        "anp_code": "EQUIPADO_AGUARDANDO",
        "anp_label_pt": "Equipado aguardando início de operação",
        "anp_label_en": "Equipped, awaiting start of operation",
        "osdu_value": "Suspended",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Completed well awaiting external triggers (authorization, surface facilities, pipeline) before producing or injecting. Includes Sistema de Produção Antecipada and TLD.",
    },
    {
        "anp_code": "FECHADO",
        "anp_label_pt": "Fechado",
        "anp_label_en": "Shut-in (already operated)",
        "osdu_value": "Shut-In",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "exactMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Completed well that already entered production/injection but is currently shut waiting for surface normalization, decision study, or intervention. Must meet temporary abandonment conditions.",
    },
    {
        "anp_code": "EM_OBSERVACAO_699",
        "anp_label_pt": "Em observação",
        "anp_label_en": "Under observation (instrumented for pressure monitoring)",
        "osdu_value": "Temporarily Abandoned",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well instrumented for pressure monitoring of producing reservoir or gas storage. Distinct from EM_OBSERVACAO (ANP-25/2015) which has same label but legacy code.",
    },
    {
        "anp_code": "EM_PERFURACAO_699",
        "anp_label_pt": "Em perfuração",
        "anp_label_en": "Drilling in progress",
        "osdu_value": "Active",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Drilling-related operations: casing run/cementing, logging, open-hole formation testing, fishing.",
    },
    {
        "anp_code": "EM_AVALIACAO",
        "anp_label_pt": "Em avaliação",
        "anp_label_en": "Under evaluation (formation/productivity testing)",
        "osdu_value": "Active",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Formation testing after Drilling Termination, TLD, or other productivity evaluation (e.g., post-fracture).",
    },
    {
        "anp_code": "EM_COMPLETACAO_699",
        "anp_label_pt": "Em completação",
        "anp_label_en": "Completion in progress",
        "osdu_value": "Active",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Operations to bring well to production/injection after drilling.",
    },
    {
        "anp_code": "EM_INTERVENCAO",
        "anp_label_pt": "Em intervenção",
        "anp_label_en": "Workover in progress",
        "osdu_value": "Active",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Completed well undergoing evaluation during production stage, restoration, recompletion, or abandonment.",
    },
    {
        "anp_code": "OPERANDO_CAPTACAO_AGUA",
        "anp_label_pt": "Operando para captação de água",
        "anp_label_en": "Operating for water capture (source well)",
        "osdu_value": "Producing",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well operating to capture water for re-injection in another well or other E&P purposes. Specific finality must be in observations.",
    },
    {
        "anp_code": "CEDIDO_CAPTACAO_AGUA",
        "anp_label_pt": "Cedido para captação de água",
        "anp_label_en": "Transferred for water capture (out of E&P scope)",
        "osdu_value": "Plugged and Abandoned",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "relatedMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well transferred (alienated) after decision of non-use in petroleum industry, for water production. No exact OSDU equivalent — out of E&P scope.",
    },
    {
        "anp_code": "OPERANDO_DESCARTE",
        "anp_label_pt": "Operando para descarte",
        "anp_label_en": "Operating for disposal (produced fluids / effluents)",
        "osdu_value": "Injection",
        "osdu_kind": "reference-data--WellStatus:osdu:reference-data--WellStatus:1.0.0",
        "match_kind": "closeMatch",
        "anp_source": "ANP-699/2017",
        "notes": "Well operating for disposal of produced fluids from other wells or various effluents from E&P. Discarded fluid must be in observations. Closest OSDU value is Injection (disposal-injection).",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    existing_codes = {m["anp_code"] for m in data["mappings"]}
    to_add = [m for m in ANP_699_MAPPINGS if m["anp_code"] not in existing_codes]

    print(f"Existing mappings: {len(data['mappings'])}")
    print(f"Proposed ANP-699/2017 mappings: {len(ANP_699_MAPPINGS)}; truly new: {len(to_add)}")

    for m in to_add:
        print(f"  + {m['anp_code']:<35} → {m['osdu_value']:<25} ({m['match_kind']})")
    skipped = [m for m in ANP_699_MAPPINGS if m["anp_code"] in existing_codes]
    for m in skipped:
        print(f"  SKIP {m['anp_code']} (already present)")

    if args.dry_run:
        print("--dry-run; not writing.")
        return 0

    # Backfill anp_source on legacy entries
    for m in data["mappings"]:
        m.setdefault("anp_source", "ANP-25/2015")

    data["mappings"].extend(to_add)

    # Update meta
    data["meta"]["sources"] = sorted(
        {m.get("anp_source", "ANP-25/2015") for m in data["mappings"]}
    )
    data["meta"]["total_mappings"] = len(data["mappings"])
    data["meta"]["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data["meta"]["coverage_note"] = (
        "Covers ANP Situação/Tipo per Resolução ANP nº 25/2015 plus the 19 "
        "operational statuses from Resolução ANP nº 699/2017 (Tabela 2). "
        "Each mapping carries `anp_source` to distinguish provenance."
    )
    data["meta"]["description"] = (
        "Crosswalk between ANP well status/classification (Resoluções 25/2015 "
        "and 699/2017) and OSDU WellStatus reference data."
    )
    # source_anp single-string is now legacy; keep for backward compat
    data["meta"]["source_anp"] = (
        "Resolução ANP 25/2015; Resolução ANP 699/2017"
    )

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {TARGET.relative_to(ROOT)} — total mappings: {data['meta']['total_mappings']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
