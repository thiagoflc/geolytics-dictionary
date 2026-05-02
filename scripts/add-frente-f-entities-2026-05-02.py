#!/usr/bin/env python3
"""Add Frente F skeleton entities to corporate module — 2026-05-02.

Adds 8 new low-confidence entity skeletons (GEOMEC046..GEOMEC053) plus the
inbound canonical relationships from existing entities that referenced these
concepts as bare strings or evidence gaps. Team will backfill definitions,
sources, owner_department, official_datastore, internal_tools and
internal_standards in a follow-up pass.

Idempotent:
- If a target entity ID already exists, the entity-add is skipped.
- If a relationship being added already exists on the source entity
  (matching relation_type + target_id), it is skipped.

Usage: python scripts/add-frente-f-entities-2026-05-02.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

# ─────────────────────────────────────────────────────────────────────────────
# 8 new entities — minimal skeleton conforming to Shapes 23-33:
#   - id matches /GEOMEC\d{3}[A-Z]?/
#   - category in enum {Classifier, Document, Formula, GovernanceKPI,
#                       Measurement, Model, Process, Property, Risk, Tool}
#   - confidence = "low"  → evidence_gaps must be non-empty
#   - sources = []  (team to fill)
#   - relationships = []  (inbound links added separately to the SOURCE entity)
# ─────────────────────────────────────────────────────────────────────────────
NEW_ENTITIES = [
    {
        "id": "GEOMEC046",
        "label_pt": "Subsidência — Faixas de Risco",
        "label_en": "Subsidence Risk Ranges",
        "category": "Classifier",
        "confidence": "low",
        "definition_pt": (
            "Classificador corporativo de severidade de subsidência baseado "
            "em deslocamento vertical acumulado: <40 cm moderada, 40-100 cm "
            "elevada, >100 cm extrema (faixas citadas em PP-2E&P-00322)."
        ),
        "definition_en": (
            "Corporate severity classifier for subsidence based on cumulative "
            "vertical displacement: <40 cm moderate, 40-100 cm high, "
            ">100 cm extreme (ranges cited in PP-2E&P-00322)."
        ),
        "evidence_gaps": [
            "Faixas (<40 cm, 40-100 cm, >100 cm) citadas como referência de PP-2E&P-00322 mas sem reprodução literal do trecho normativo.",
            "Documento-fonte PP-2E&P-00322 não anexado ao corpus; sources=[] aguardando backfill.",
            "Falta confirmar se as faixas são absolutas ou condicionadas a horizonte temporal / profundidade do reservatório.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC047",
        "label_pt": "SIMCARR",
        "label_en": "SIMCARR — Hydraulic Modeling System",
        "acronym": ["SIMCARR"],
        "category": "Tool",
        "confidence": "low",
        "definition_pt": (
            "Sistema corporativo Petrobras de modelagem hidráulica usado para "
            "simulação de pressões de circulação e suporte à análise de ECD. "
            "Citado em GEOMEC019 (ECD) e GEOMEC036 (Fórmula de ECD)."
        ),
        "definition_en": (
            "Petrobras corporate hydraulic modeling system used to simulate "
            "circulation pressures and support ECD analysis. Referenced by "
            "GEOMEC019 (ECD) and GEOMEC036 (ECD Formula)."
        ),
        "evidence_gaps": [
            "Sistema citado nominalmente em GEOMEC019/GEOMEC036 sem documentação de escopo, módulos ou interfaces.",
            "Falta referência a manual/owner_department do sistema (sources=[] e owner_department a backfill).",
            "Não está claro se SIMCARR é o sistema oficial de produção ou ferramenta de pesquisa interna.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC048",
        "label_pt": "PWDa",
        "label_en": "PWDa — Pressure While Drilling Annular",
        "acronym": ["PWDa"],
        "category": "Tool",
        "confidence": "low",
        "definition_pt": (
            "Sistema/sensor de monitoramento em tempo real da pressão anular "
            "durante a perfuração (Pressure While Drilling — Annular). Citado "
            "em GEOMEC019 (ECD) e GEOMEC037 (ESD) como fonte primária de leitura."
        ),
        "definition_en": (
            "Real-time annular pressure-while-drilling monitoring sensor/system. "
            "Referenced by GEOMEC019 (ECD) and GEOMEC037 (ESD) as the primary "
            "downhole reading source."
        ),
        "evidence_gaps": [
            "Citado como sensor/sistema sem distinção clara entre o hardware downhole e o sistema de superfície que registra os dados.",
            "Falta especificar fornecedor, taxa de amostragem e datastore oficial onde os dados PWDa são persistidos.",
            "Vínculo com BDIEP/OpenWells não documentado.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC049",
        "label_pt": "BDIEP",
        "label_en": "BDIEP — Banco de Dados de Informações de Engenharia de Poço",
        "acronym": ["BDIEP"],
        "category": "Tool",
        "confidence": "low",
        "definition_pt": (
            "Datastore corporativo Petrobras para informações de engenharia de "
            "poço, incluindo eventos operacionais relevantes para análise de "
            "riscos como prisão de coluna (referenciado em GEOMEC045)."
        ),
        "definition_en": (
            "Petrobras corporate datastore for well engineering information, "
            "including operational events relevant to risk analysis such as "
            "stuck pipe (referenced by GEOMEC045)."
        ),
        "evidence_gaps": [
            "Citado como datastore corporativo sem schema, owner_department ou política de retenção documentados.",
            "Fronteira de responsabilidade entre BDIEP e OpenWells (GEOMEC051) não esclarecida.",
            "Não há lista de tabelas/eventos canônicos persistidos no BDIEP.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC050",
        "label_pt": "BDP — Boletim Diário da Perfuração",
        "label_en": "BDP — Daily Drilling Report",
        "acronym": ["BDP"],
        "category": "Document",
        "confidence": "low",
        "definition_pt": (
            "Documento operacional emitido diariamente durante a perfuração, "
            "registrando eventos, anomalias e parâmetros relevantes da sonda. "
            "Citado em GEOMEC025 (CSD) como insumo de monitoramento."
        ),
        "definition_en": (
            "Operational document issued daily during drilling, recording rig "
            "events, anomalies and relevant parameters. Referenced by "
            "GEOMEC025 (CSD) as a monitoring input."
        ),
        "evidence_gaps": [
            "Documento citado sem template/seções canônicas documentadas.",
            "Falta indicar se o BDP é estruturado (campos fixos) ou texto-livre.",
            "Sem mapeamento de quais campos do BDP alimentam BDIEP/OpenWells.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC051",
        "label_pt": "OpenWells",
        "label_en": "OpenWells — Well Operations Datastore",
        "acronym": ["OpenWells"],
        "category": "Tool",
        "confidence": "low",
        "definition_pt": (
            "Datastore de operações de poço usado pela Petrobras para "
            "registro de eventos e parâmetros operacionais. Citado em "
            "GEOMEC045 (Prisão de Coluna) como fonte de eventos correlatos."
        ),
        "definition_en": (
            "Well operations datastore used at Petrobras to record events and "
            "operational parameters. Referenced by GEOMEC045 (Stuck Pipe) as "
            "a source of correlated events."
        ),
        "evidence_gaps": [
            "Sistema de origem comercial (Halliburton/Landmark) mencionado nominalmente sem versão ou owner_department interno.",
            "Limites entre OpenWells e BDIEP não documentados — provável sobreposição parcial de eventos.",
            "Falta confirmar se OpenWells é fonte primária ou réplica downstream.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC052",
        "label_pt": "PRV — Pressure Relief Valve / Setpoint MPD",
        "label_en": "PRV / MPD Setpoint",
        "acronym": ["PRV"],
        "category": "Property",
        "confidence": "low",
        "definition_pt": (
            "Limite de contrapressão (setpoint da válvula de alívio) imposto "
            "em operações Managed Pressure Drilling (MPD). Gap explícito "
            "registrado em GEOMEC041 (Contrapressão de Superfície)."
        ),
        "definition_en": (
            "Backpressure limit (relief valve setpoint) enforced during "
            "Managed Pressure Drilling (MPD) operations. Explicit gap noted "
            "on GEOMEC041 (Surface Backpressure)."
        ),
        "evidence_gaps": [
            "Conceito citado em gap de GEOMEC041 sem valor numérico canônico nem norma interna de referência.",
            "Falta distinguir PRV mecânica (válvula física) vs setpoint lógico no sistema MPD.",
            "Faixa de operação típica (psi) e standard_unit a confirmar com Engenharia de Poço.",
        ],
        "relationships": [],
        "sources": [],
    },
    {
        "id": "GEOMEC053",
        "label_pt": "Pressão de Reabertura / Propagação de Fratura",
        "label_en": "Fracture Reopening / Propagation Pressure",
        "category": "Measurement",
        "confidence": "low",
        "definition_pt": (
            "Pressão associada à reabertura ou propagação de fratura em "
            "ensaios de injetividade. Citada no gap de GEOMEC043 (Pc/ISIP) "
            "como conceito sobreposto que requer desambiguação formal."
        ),
        "definition_en": (
            "Pressure associated with fracture reopening or propagation in "
            "injectivity tests. Referenced in the GEOMEC043 (Pc/ISIP) gap as "
            "an overlapping concept requiring formal disambiguation."
        ),
        "evidence_gaps": [
            "Sobreposição com Pc (Pressão de Fechamento) e ISIP registrada como gap em GEOMEC043 sem definição operacional separada.",
            "Falta procedimento canônico para extração da pressão de reabertura a partir do registro de pressão do leak-off/XLOT.",
            "Standard_unit e variantes observadas (psi, MPa, lb/gal equivalente) a confirmar.",
        ],
        "relationships": [],
        "sources": [],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Inbound relationships — added to the SOURCE entity that already references
# the new concept. Verbs from the canonical vocabulary
# (proposal-relation-vocabulary-2026-05-02.md):
#   - REQUIRES   : Process/Measurement/Formula → Tool (process requires tool)
#   - MENTIONED_IN / RELATED_TO are NOT canonical → use REQUIRES, MONITORS,
#     IS_RISK_FOR, RELATED_TO with edge_note when no closer fit
# ─────────────────────────────────────────────────────────────────────────────
INBOUND_RELATIONSHIPS = [
    # GEOMEC019 (ECD, Measurement) requires SIMCARR (Tool) for hydraulic modeling
    ("GEOMEC019", "REQUIRES", "GEOMEC047", "SIMCARR",
     "ECD analysis depends on SIMCARR hydraulic modeling outputs."),
    # GEOMEC036 (Fórmula de ECD, Formula) requires SIMCARR (Tool)
    ("GEOMEC036", "REQUIRES", "GEOMEC047", "SIMCARR",
     "Fórmula de ECD operacionalizada via SIMCARR."),
    # GEOMEC019 (ECD) requires PWDa (Tool) — primary downhole reading
    ("GEOMEC019", "REQUIRES", "GEOMEC048", "PWDa — Pressure While Drilling Annular",
     "ECD lê pressão anular em tempo real via PWDa."),
    # GEOMEC037 (ESD) requires PWDa (Tool)
    ("GEOMEC037", "REQUIRES", "GEOMEC048", "PWDa — Pressure While Drilling Annular",
     "ESD derivada da leitura PWDa em condição sem circulação."),
    # GEOMEC045 (Prisão de Coluna, Risk) — eventos correlatos persistidos em BDIEP/OpenWells
    ("GEOMEC045", "RELATED_TO", "GEOMEC049", "BDIEP — Banco de Dados de Informações de Engenharia de Poço",
     "Eventos correlatos de prisão de coluna são persistidos no BDIEP."),
    ("GEOMEC045", "RELATED_TO", "GEOMEC051", "OpenWells — Well Operations Datastore",
     "Eventos correlatos de prisão de coluna também são registrados no OpenWells."),
    # GEOMEC025 (CSD, Process) monitors the BDP daily report
    ("GEOMEC025", "MONITORS", "GEOMEC050", "BDP — Boletim Diário da Perfuração",
     "CSD consome o BDP diariamente para vigilância operacional."),
    # GEOMEC041 (Contrapressão de Superfície, Property) constrained by PRV setpoint
    ("GEOMEC041", "CONSTRAINS", "GEOMEC052", "PRV / MPD Setpoint",
     "Setpoint de PRV impõe limite superior de contrapressão em MPD."),
    # GEOMEC043 (Pressão de Fechamento de Fratura) related to reopening/propagation
    ("GEOMEC043", "RELATED_TO", "GEOMEC053", "Fracture Reopening / Propagation Pressure",
     "Sobreposição conceitual entre Pc/ISIP e pressão de reabertura/propagação."),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}

    log: list[str] = []
    added_entities = 0
    skipped_entities = 0
    added_rels = 0
    skipped_rels = 0

    # ── 1. Add new entities idempotently ──
    for new_ent in NEW_ENTITIES:
        eid = new_ent["id"]
        if eid in by_id:
            log.append(f"  ENT {eid}: already exists — SKIP")
            skipped_entities += 1
            continue
        data["entities"].append(new_ent)
        by_id[eid] = new_ent
        log.append(f"  ENT {eid} ADD  ({new_ent['category']}, conf={new_ent['confidence']})")
        added_entities += 1

    # ── 2. Add inbound relationships idempotently ──
    for src, rt, tgt, tgt_label, edge_note in INBOUND_RELATIONSHIPS:
        ent = by_id.get(src)
        if not ent:
            log.append(f"  REL {src} {rt}→{tgt}: source NOT FOUND — SKIP")
            skipped_rels += 1
            continue
        rels = ent.setdefault("relationships", [])
        if any(r.get("relation_type") == rt and r.get("target_id") == tgt for r in rels):
            log.append(f"  REL {src} {rt}→{tgt}: already exists — SKIP")
            skipped_rels += 1
            continue
        rec: dict = {
            "target_id": tgt,
            "relation_type": rt,
            "target_label": tgt_label,
        }
        if edge_note:
            rec["edge_note"] = edge_note
        rels.append(rec)
        log.append(f"  REL {src} {rt}→{tgt}  ADD")
        added_rels += 1

    # ── 3. architecture_notes breadcrumb ──
    notes = data["meta"].setdefault("architecture_notes", [])
    note_str = (
        "Frente F 2026-05-02 — adicionados 8 esqueletos low-confidence "
        "(GEOMEC046..GEOMEC053: Subsidence Risk Ranges, SIMCARR, PWDa, "
        "BDIEP, BDP, OpenWells, PRV/MPD Setpoint, Fracture Reopening Pressure) "
        "com inbound relationships canônicas a partir de GEOMEC019, "
        "GEOMEC025, GEOMEC036, GEOMEC037, GEOMEC041, GEOMEC043 e GEOMEC045. "
        "Definições, sources, owner_department, official_datastore, "
        "internal_tools e internal_standards a backfillar pelo time."
    )
    if note_str not in notes:
        notes.append(note_str)

    print("\n".join(log) if log else "(no changes)")
    print(
        f"\nEntities — added: {added_entities}  skipped: {skipped_entities}\n"
        f"Relations — added: {added_rels}  skipped: {skipped_rels}"
    )

    if args.dry_run:
        print("[dry-run] master JSON NÃO foi modificado.")
        return 0

    TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"✓ Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
