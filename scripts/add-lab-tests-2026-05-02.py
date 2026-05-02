#!/usr/bin/env python3
"""Add 7 new LabTest entities (GEOMEC061–GEOMEC067) to the corporate ontology.

Adds standard ISRM rock-mechanics laboratory tests as a new category "LabTest":

  GEOMEC061  Ensaio Triaxial            (medium)
  GEOMEC062  Ensaio UCS                 (medium)
  GEOMEC063  Ensaio Hidrostático        (medium)
  GEOMEC064  Ensaio Brasileiro          (medium)
  GEOMEC065  Ensaio Oedométrico         (medium)
  GEOMEC066  Ensaio TWC                 (low)
  GEOMEC067  Ensaio de Volume Poroso    (medium)

Each entity is wired with:
  - IS_PART_OF → GEOMEC022 (Scratch Test e Ensaios Mecânicos — umbrella)
  - MEASURES   → property entities where applicable
  - evidence_gaps explicitly flagging missing target entities or PE-XXX links

NOTE: After running this script the SHACL category enum on
data/geolytics-shapes.ttl (geo:GeomechCorporateEntityShape) MUST be
extended with "LabTest", or validation will fail. That update is owned
by a parallel agent and is intentionally NOT touched here.

Idempotent — re-running on a patched JSON is a no-op.
Usage: python3 scripts/add-lab-tests-2026-05-02.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"

UMBRELLA_ID = "GEOMEC022"
UMBRELLA_LABEL_PT = "Scratch Test e Ensaios Mecânicos de Rocha em Laboratório"

# Common evidence_gap shared by all entities (no ISRM/PE-XXX sources curated yet)
COMMON_SOURCES_GAP = (
    "Procedimento ainda não vinculado a uma norma ISRM específica nem a um PE-XXX "
    "Petrobras-interno; sources=[] até curadoria pelo time de laboratório."
)
COMMON_CALIB_GAP = (
    "Constantes de calibração e procedimentos Petrobras-internos (parâmetros de "
    "ensaio, geometria de corpo de prova, tolerâncias) não documentados nesta entity."
)


# ─────────────────────────────────────────────────────────────────────────
# 7 new lab-test entities
# ─────────────────────────────────────────────────────────────────────────
NEW_ENTITIES: list[dict] = [
    {
        "id": "GEOMEC061",
        "label_pt": "Ensaio Triaxial",
        "label_en": "Triaxial Test",
        "category": "LabTest",
        "confidence": "medium",
        "acronym": ["Triaxial"],
        "standard_unit": None,
        "definition_pt": (
            "Ensaio de compressão axial sob confinamento radial constante, executado em "
            "corpo de prova cilíndrico de rocha intacta. Permite obter resistência à "
            "compressão sob tensão de confinamento (UCS confinada), módulo de Young, "
            "coeficiente de Poisson e envoltória de ruptura (Mohr–Coulomb / Hoek–Brown). "
            "Aplicado em caracterização geomecânica de reservatório e capeadora para "
            "modelos 1D/3D MEM."
        ),
        "definition_en": (
            "Axial compression test under constant radial confining pressure on a "
            "cylindrical intact rock specimen. Yields confined strength, Young's modulus, "
            "Poisson's ratio, and the Mohr–Coulomb/Hoek–Brown failure envelope. Standard "
            "input for reservoir/cap-rock geomechanical characterization (1D/3D MEM)."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
            "Faixas típicas de tensão de confinamento usadas pela Petrobras (single-stage "
            "vs. multi-stage) não capturadas.",
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF",  "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
            {"relation_type": "MEASURES",    "target_id": "GEOMEC010", "target_label": "Resistência à Compressão Uniaxial (UCS)"},
            {"relation_type": "MEASURES",    "target_id": "GEOMEC011", "target_label": "Módulo de Young"},
            {"relation_type": "MEASURES",    "target_id": "GEOMEC012", "target_label": "Coeficiente de Poisson"},
            {"relation_type": "MEASURES",    "target_id": "GEOMEC005", "target_label": "Tensão Efetiva"},
        ],
    },
    {
        "id": "GEOMEC062",
        "label_pt": "Ensaio UCS (Uniaxial sem Confinamento)",
        "label_en": "Unconfined Compression Test",
        "category": "LabTest",
        "confidence": "medium",
        "acronym": ["UCS test", "UCS"],
        "standard_unit": None,
        "definition_pt": (
            "Compressão axial em corpo de prova cilíndrico de rocha sem aplicação de "
            "tensão de confinamento (σ3 = 0). Fornece a resistência à compressão "
            "uniaxial (UCS) — propriedade primária de resistência da rocha. Quando "
            "instrumentado com strain-gauges, permite estimar também módulo de Young e "
            "coeficiente de Poisson estáticos."
        ),
        "definition_en": (
            "Axial compression test on a cylindrical rock specimen with zero confining "
            "pressure (σ3 = 0). Yields the Unconfined Compressive Strength (UCS) — the "
            "primary rock-strength descriptor. Optional strain-gauge instrumentation "
            "also provides static Young's modulus and Poisson's ratio."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF", "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
            {"relation_type": "MEASURES",   "target_id": "GEOMEC010", "target_label": "Resistência à Compressão Uniaxial (UCS)"},
        ],
    },
    {
        "id": "GEOMEC063",
        "label_pt": "Ensaio Hidrostático",
        "label_en": "Hydrostatic Compression Test",
        "category": "LabTest",
        "confidence": "medium",
        "acronym": ["Hydrostat"],
        "standard_unit": None,
        "definition_pt": (
            "Ensaio em que o corpo de prova é submetido a tensão isotrópica crescente "
            "(σ1 = σ2 = σ3) com medição da deformação volumétrica. Caracteriza a "
            "compressibilidade da rocha e dos poros, fornecendo Cbc e Cpc usadas em "
            "modelos de compactação/subsidência e em correções de porosidade in-situ."
        ),
        "definition_en": (
            "Test under increasing isotropic stress (σ1 = σ2 = σ3) with volumetric "
            "strain measurement. Characterizes rock and pore compressibility, providing "
            "Cbc/Cpc used in compaction/subsidence modeling and in-situ porosity "
            "corrections."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
            "Distinção entre Cpc (drenado) e outros tipos de compressibilidade reportada "
            "no ensaio precisa ser explicitada por entidade alvo.",
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF", "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
            {"relation_type": "MEASURES",   "target_id": "GEOMEC014", "target_label": "Compressibilidade de Poros"},
        ],
    },
    {
        "id": "GEOMEC064",
        "label_pt": "Ensaio Brasileiro (Tração)",
        "label_en": "Brazilian Tensile Test",
        "category": "LabTest",
        "confidence": "medium",
        "acronym": ["BR", "Brazilian"],
        "standard_unit": None,
        "definition_pt": (
            "Ensaio de tração indireta no qual um disco de rocha é comprimido entre dois "
            "pratos diametralmente opostos, induzindo tração no plano central. A "
            "resistência à tração σt é calculada a partir da carga de ruptura e da "
            "geometria do corpo de prova (norma ISRM). Fornece dado primário para "
            "calibração de envoltórias de ruptura e cálculo de pressão de quebra em "
            "fraturamento."
        ),
        "definition_en": (
            "Indirect tensile test in which a rock disc is compressed between two "
            "diametrically opposed platens, inducing tension on the central plane. "
            "Tensile strength σt is computed from the failure load and specimen "
            "geometry (ISRM). Primary input for failure-envelope calibration and "
            "fracture breakdown-pressure calculations."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
            "Não há entidade alvo para 'Resistência à Tração σt' no dicionário corporativo "
            "atual — criar GEOMEC para σt e religar este ensaio com MEASURES.",
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF", "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
        ],
    },
    {
        "id": "GEOMEC065",
        "label_pt": "Ensaio Oedométrico",
        "label_en": "Oedometric Test",
        "category": "LabTest",
        "confidence": "medium",
        "acronym": ["Oedo"],
        "standard_unit": None,
        "definition_pt": (
            "Compressão uniaxial sob deformação lateral nula (condição K0): o corpo de "
            "prova é confinado em um anel rígido e tensionado axialmente em estágios. "
            "Fornece a compressibilidade de poros uniaxial (Cpu/Cm), parâmetro chave para "
            "modelagem de compactação de reservatório e subsidência em campos clásticos."
        ),
        "definition_en": (
            "Uniaxial compression under zero lateral strain (K0 condition): the specimen "
            "is confined in a rigid ring and axially loaded in stages. Yields the "
            "uniaxial pore compressibility (Cpu/Cm), a key input for reservoir compaction "
            "and subsidence modeling in clastic fields."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF", "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
            {"relation_type": "MEASURES",   "target_id": "GEOMEC024", "target_label": "Compressibilidade de Poros Uniaxial"},
        ],
    },
    {
        "id": "GEOMEC066",
        "label_pt": "Ensaio TWC (Thick-Walled Cylinder)",
        "label_en": "Thick-Walled Cylinder Test",
        "category": "LabTest",
        "confidence": "low",
        "acronym": ["TWC"],
        "standard_unit": None,
        "definition_pt": (
            "Ensaio em corpo de prova cilíndrico oco submetido simultaneamente a "
            "pressão externa e (opcionalmente) interna, simulando o estado de tensões "
            "no entorno de um poço aberto. Mede a pressão crítica de colapso da parede "
            "interna e é o ensaio padrão de laboratório para avaliação de risco de "
            "produção de areia (sanding) em arenitos pouco consolidados."
        ),
        "definition_en": (
            "Test on a hollow cylindrical specimen under external (and optionally "
            "internal) pressure, simulating the near-wellbore stress state. Measures the "
            "critical inner-wall collapse pressure and is the standard laboratory "
            "method for sand-production risk assessment in poorly consolidated "
            "sandstones."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
            "Não há entidade alvo para 'Sand Production Risk' no dicionário corporativo "
            "atual — criar GEOMEC para risco de produção de areia e religar este ensaio "
            "com MEASURES.",
            "Confidence=low: dependência forte de geometria do CP e calibração específica "
            "Petrobras ainda não inventariada.",
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF",    "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
            {"relation_type": "IS_INPUT_FOR", "target_id": "GEOMEC015", "target_label": "Estabilidade de Poço / Análise de Geohazards"},
        ],
    },
    {
        "id": "GEOMEC067",
        "label_pt": "Ensaio de Volume Poroso",
        "label_en": "Pore Volume Analysis",
        "category": "LabTest",
        "confidence": "medium",
        "acronym": ["PVA"],
        "standard_unit": None,
        "definition_pt": (
            "Conjunto de ensaios laboratoriais para determinação do volume de poros e "
            "porosidade efetiva de plug de rocha — tipicamente por porosimetria a hélio "
            "ou método de saturação. Fornece o volume poroso de referência usado em "
            "ensaios de compressibilidade, permeabilidade e correções petrofísicas. "
            "Escopo formal pertence à Petrofísica; mantido aqui pelo acoplamento direto "
            "com ensaios geomecânicos (Hidrostático, Oedométrico)."
        ),
        "definition_en": (
            "Set of laboratory measurements determining pore volume and effective "
            "porosity of a rock plug — typically by helium porosimetry or saturation "
            "methods. Supplies the reference pore volume used in compressibility, "
            "permeability and petrophysical-correction calculations. Formal scope is "
            "Petrophysics; retained here for direct coupling with geomechanical tests "
            "(Hydrostatic, Oedometric)."
        ),
        "evidence_gaps": [
            COMMON_SOURCES_GAP,
            COMMON_CALIB_GAP,
            "Não há entidades alvo para 'Porosidade efetiva' nem 'Permeabilidade absoluta' "
            "no dicionário corporativo atual — escopo Petrofísica; criar entidades e "
            "religar este ensaio com MEASURES quando elas existirem.",
        ],
        "sources": [],
        "relationships": [
            {"relation_type": "IS_PART_OF", "target_id": UMBRELLA_ID, "target_label": UMBRELLA_LABEL_PT},
        ],
    },
]


def add_entity(by_id: dict, entity: dict, log: list[str]) -> None:
    """Add a new lab-test entity. Skip if id already present (idempotent)."""
    eid = entity["id"]
    if eid in by_id:
        log.append(f"  SKIP {eid}: already present")
        return
    by_id[eid] = entity
    n_rels = len(entity.get("relationships") or [])
    log.append(
        f"  ADD  {eid} ({entity['label_pt']}) — "
        f"category={entity['category']}, confidence={entity['confidence']}, "
        f"relationships={n_rels}, evidence_gaps={len(entity.get('evidence_gaps') or [])}"
    )


def ensure_relations(by_id: dict, entity: dict, log: list[str]) -> None:
    """Ensure each declared relationship exists exactly once on the entity.

    Re-runs are no-ops because we de-dupe by (relation_type, target_id).
    """
    cur = by_id.get(entity["id"])
    if cur is None:
        return
    rels = cur.setdefault("relationships", [])
    existing = {(r.get("relation_type"), r.get("target_id")) for r in rels}
    for r in entity.get("relationships") or []:
        key = (r.get("relation_type"), r.get("target_id"))
        if key not in existing:
            rels.append(r)
            existing.add(key)
            log.append(
                f"  RELATE {entity['id']} {r['relation_type']}→{r['target_id']}"
            )


def sort_key(eid: str) -> tuple:
    m = re.match(r"GEOMEC(\d+)([A-Z]?)$", eid)
    return (int(m.group(1)), m.group(2)) if m else (9999, eid)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}
    log: list[str] = []

    # Verify umbrella exists; warn but continue if not
    if UMBRELLA_ID not in by_id:
        log.append(f"  WARN umbrella {UMBRELLA_ID} not found — IS_PART_OF edges will dangle")

    # Verify MEASURES targets exist; warn for any missing
    referenced_targets: set[str] = set()
    for ent in NEW_ENTITIES:
        for r in ent.get("relationships") or []:
            referenced_targets.add(r["target_id"])
    for tid in sorted(referenced_targets):
        if tid not in by_id:
            log.append(f"  WARN relationship target {tid} missing in master JSON")

    # Add new entities (idempotent)
    for ent in NEW_ENTITIES:
        add_entity(by_id, ent, log)
        # If entity was added or already present, ensure declared relations are in place
        ensure_relations(by_id, ent, log)

    # Rebuild entity list in sorted order
    data["entities"] = [by_id[k] for k in sorted(by_id.keys(), key=sort_key)]

    # Append architecture note
    notes = data.setdefault("meta", {}).setdefault("architecture_notes", [])
    note_str = (
        "Lab-tests batch 2026-05-02 — adicionadas 7 entidades de ensaios de "
        "laboratório (GEOMEC061–GEOMEC067) sob nova categoria 'LabTest', "
        "todas IS_PART_OF GEOMEC022 (Scratch Test e Ensaios Mecânicos). "
        "Definições baseadas em prática-padrão ISRM; sources=[] e "
        "evidence_gaps explicitando ausência de PE-XXX vinculado e calibração "
        "Petrobras-interna. SHACL: enum de categoria deve ser estendida com "
        "'LabTest' em geo:GeomechCorporateEntityShape (parallel agent)."
    )
    if note_str not in notes:
        notes.append(note_str)

    print("\n".join(log))
    print(f"\nTotal log lines: {len(log)}")
    print(f"Entities now: {len(data['entities'])}")

    if args.dry_run:
        print("\n[dry-run] master JSON NÃO foi modificado.")
        return 0

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n✓ Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
