#!/usr/bin/env python3
"""Apply Frente F — team response 2026-05-02.

Surgical updates to GEOMEC046–053 based on the data governance team's
SINPEP/CoI investigation:

  - 6 in-place enrichments: 046 (Subsidência), 047 (SIMCARR), 048 (PWDa),
    049 (BDIEP), 050 (BDP), 051 (OpenWells)

  - 2 splits (following the GEOMEC026 deprecation pattern):
      GEOMEC052 → 052A (PRV hardware, high) + 052B (Setpoint MPD/SBP, high)
      GEOMEC053 → 053A (Pressão de Reabertura, high) + 053B (Pressão de
                  Propagação, high)
    Original 052/053 are kept and marked deprecated for audit; active
    references are re-routed to the new IDs.

Idempotent — re-running on a patched JSON is a no-op.
Usage: python3 scripts/apply-frente-f-team-response-2026-05-02.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "geomechanics-corporate.json"


# ─────────────────────────────────────────────────────────────────────────
# In-place enrichments (6 entities)
# ─────────────────────────────────────────────────────────────────────────
ENRICHMENTS = {
    "GEOMEC046": {
        "label_pt": "Subsidência — Faixas de Risco",
        "label_en": "Subsidence Risk Ranges",
        "confidence": "high",
        "category": "Classifier",
        "definition_pt": (
            "Classificação do nível de subsidência de um campo de petróleo em três faixas "
            "de risco, conforme PP-2E&P-00322 §3.9.1.1: subsidência moderada (<40 cm, segura), "
            "elevada (40–100 cm, requer monitoramento por possíveis patologias estruturais) e "
            "extrema (>100 cm, danos estruturais frequentes, projeto deve evitar ou aplicar "
            "monitoramento obrigatório). Modelagem recomendada com cenário de depleção forçada "
            "(injeção mínima)."
        ),
        "definition_en": (
            "Three-level risk classification of subsidence in petroleum fields per PP-2E&P-00322 "
            "§3.9.1.1: moderate (<40 cm, safe), elevated (40–100 cm, monitoring required) and "
            "extreme (>100 cm, structural damage common, mandatory mitigation/monitoring)."
        ),
        "standard_unit": "cm",
        "units_observed": ["cm", "m"],
        "owner_department": "RES/TR/GMR",
        "internal_standards": ["PP-2E&P-00322", "PE-2AGP-00027"],
        "subsidence_ranges": [
            {"name": "moderada", "min_cm": 0,    "max_cm": 40,   "implication": "Segura — sem registro de problemas graves; operação normal."},
            {"name": "elevada",  "min_cm": 40,   "max_cm": 100,  "implication": "Requer monitoramento — patologias estruturais possíveis; risco de danos mecânicos em poços."},
            {"name": "extrema",  "min_cm": 100,  "max_cm": None, "implication": "Evitar / monitoramento obrigatório — danos estruturais frequentes; alternativas de projeto obrigatórias."},
        ],
        "evidence_gaps": [
            "Confirmar com RES/TR/GMR se há horizonte temporal (ex.: subsidência projetada em N anos de produção) associado às faixas na prática operacional.",
            "PE-2AGP-00027 define monitoramento de PMO mas não diferencia explicitamente por faixa de subsidência — confirmar triggers de ação por faixa.",
        ],
        "sources_append": [
            {
                "doc_id": "PP-2E&P-00322",
                "section": "§3.9.1.1 Análise de Subsidência",
                "citation": "Inferior a 40 cm classifica-se como subsidência moderada [...] Entre 40 cm e 100 cm classifica-se como subsidência elevada [...] Maior que 100 cm classifica-se como subsidência extrema.",
            },
        ],
    },

    "GEOMEC047": {
        "label_pt": "SIMCARR",
        "label_en": "SIMCARR — Cuttings Transport and Hydraulics Simulator",
        "confidence": "medium",
        "category": "Tool",
        "definition_pt": (
            "Simulador interno de carreamento e hidráulica da Petrobras, disponível a toda "
            "equipe própria e contratada via PETRONET (simcarr.ep.petrobras.com.br). Calcula "
            "perdas de carga, ECD, eficiência de limpeza de poço e parâmetros de bomba para "
            "projeto e acompanhamento de operações de perfuração."
        ),
        "definition_en": (
            "Petrobras internal hole-cleaning and hydraulics web simulator (PETRONET-hosted). "
            "Computes ECD, pressure losses, cuttings transport efficiency, and pump parameters "
            "for both drilling project and real-time monitoring."
        ),
        "owner_department": "POCOS",
        "official_datastore": ["PETRONET (simcarr.ep.petrobras.com.br)"],
        "internal_standards": ["PE-2POC-00453"],
        "observed_variants_union": ["SIMCARR", "Simcarr", "simulador de carreamento", "simulador de hidráulica"],
        "evidence_gaps": [
            "Lista canônica de módulos do SIMCARR (gel, alargador, MPD, swab/surge): confirmar com POCOS.",
            "Arquitetura técnica: software próprio Petrobras vs. licenciado e re-skin.",
            "Versão atualmente em produção e roadmap.",
        ],
        "sources_append": [
            {
                "doc_id": "PE-2POC-00453",
                "section": "§3.1 Definição do SIMCARR",
                "citation": "O SIMCARR é o simulador de carreamento e hidráulica disponível a toda equipe Petrobras e contratada através da PETRONET no endereço simcarr.ep.petrobras.com.br.",
            },
        ],
    },

    "GEOMEC048": {
        "label_pt": "PWDa — Pressure While Drilling (annular)",
        "label_en": "Pressure While Drilling — Annular",
        "confidence": "medium",
        "category": "Tool",
        "definition_pt": (
            "Ferramenta MWD downhole que mede continuamente a pressão no anular durante a "
            "perfuração, gerando as grandezas ECD e ESD em tempo real. O sufixo \"a\" "
            "(annular) especifica leitura no espaço anular. Os dados são gravados em memória "
            "da ferramenta e/ou transmitidos em tempo real via pulso de pressão (WITSML/WITS). "
            "Modelada como entidade única (hardware + measurement inseparáveis no contexto do "
            "dicionário); sistema de superfície de aquisição PWD pode ser entidade separada em "
            "iteração futura se necessário."
        ),
        "definition_en": (
            "Downhole MWD sensor measuring annular pressure continuously during drilling, "
            "enabling real-time ECD and ESD calculation. Data stored in tool memory and/or "
            "transmitted via mud-pulse telemetry (WITSML/WITS)."
        ),
        "owner_department": "POCOS",
        "official_datastore": ["EXATA", "BDIEP"],
        "internal_standards": ["PE-2POC-00453", "PE-2EXP-00061"],
        "observed_variants_union": ["PWD", "PWDa", "medição de pressão de fundo", "sensor de pressão anular"],
        "evidence_gaps": [
            "Sample-rate típica não publicada nos padrões — depende da contratada (SLB/BHI/HAL) e modo de transmissão (~1s memória, 10–30s RT).",
            "Profundidade máxima de operação é especificação da ferramenta da contratada, não Petrobras-interna.",
            "Owner formal do hardware: padrão indica gestão POCOS do processo, mas hardware é da contratada de MWD.",
        ],
        "sources_append": [
            {
                "doc_id": "PE-2POC-00453",
                "section": "§3.2.2 Gravação e Transmissão do PWD",
                "citation": "Os dados de pressão de fundo são continuamente gravados na memória da ferramenta que, após uma manobra, podem ser recuperados e então analisados na superfície.",
            },
        ],
    },

    "GEOMEC049": {
        "label_pt": "BDIEP — Base de Dados Integrada de E&P",
        "label_en": "BDIEP — Integrated E&P Database",
        "confidence": "medium",
        "category": "Tool",
        "definition_pt": (
            "Repositório unificado de armazenamento de informações estruturadas e não "
            "estruturadas obtidas ou produzidas durante os processos técnicos da atividade de "
            "E&P da Petrobras. Acessado pela interface VGE para consulta e cadastro de "
            "arquivos. Retenção permanente; acesso protegido por chave e senha. Posicionamento "
            "vs. correlatos: BDIEP é repositório técnico corporativo (golden source para dados "
            "de poços exploratórios e explotatórios), enquanto OpenWells é fonte primária de "
            "dados operacionais (BDP, LOT, XLOT) que migram para BDIEP, e SIGEO armazena dados "
            "geológicos (calha, paleontologia, geoquímica)."
        ),
        "definition_en": (
            "BDIEP (Integrated E&P Database): unified repository for structured and "
            "unstructured information generated during Petrobras E&P technical processes. "
            "Primary long-term datastore for well data, accessed via VGE."
        ),
        "owner_department": "TIC/US/EXP-RES-DC",
        "internal_standards": ["PE-2EXP-00065", "PE-2EXP-00059"],
        "observed_variants_union": ["BDIEP", "Base de Dados Integrada de E&P", "base integrada E&P"],
        "evidence_gaps": [
            "Owner formal do schema: confirmar TIC/US/EXP-RES-DC (evidência indireta via EXATA-WIKI).",
            "DDL nativo não publicado no SINPEP — solicitar ao TIC/US/EXP-RES-DC. Tabelas Oracle conhecidas: poco, log_perfuracao, curva_perfilagem, metadado_curva.",
            "Política de backup/DR e retenção operacional.",
        ],
        "sources_append": [
            {
                "doc_id": "PE-2EXP-00065",
                "section": "§3.1.2 Definições",
                "citation": "BDIEP (Base de Dados Integrada de E&P): repositório unificado de armazenamento das informações estruturadas e não estruturadas obtidas ou produzidas durante os processos técnicos da atividade de E&P.",
            },
        ],
    },

    "GEOMEC050": {
        "label_pt": "BDP — Boletim Diário da Perfuração",
        "label_en": "BDP — Daily Drilling Report",
        "confidence": "medium",
        "category": "Document",
        "definition_pt": (
            "Relatório diário que registra todas as operações executadas no poço ao longo de "
            "um turno/dia de perfuração: atividades, profundidades atingidas, parâmetros de "
            "fluido, tempos produtivos e não produtivos (NPT), ocorrências e consumo de "
            "materiais. Documento operacional primário de rastreabilidade da execução do poço. "
            "Estrutura mista — combina campos estruturados (profundidade, tempos, parâmetros) "
            "com narrativa textual (ocorrências, observações). Preenchido pelo Fiscal RPB na "
            "sonda via OpenWells/Atlas; armazenamento permanente no BDIEP. Cardinalidade: 1 "
            "BDP por dia-turno por poço."
        ),
        "definition_en": (
            "Daily Drilling Report — operational record of all activities, depths, fluid "
            "parameters, NPT, events, and material consumption per well per shift. Mixed "
            "structured/narrative format. Filled in OpenWells/Atlas by RPB Fiscal on the rig; "
            "permanently archived in BDIEP."
        ),
        "owner_department": "POCOS",
        "official_datastore": ["OpenWells", "BDIEP"],
        "internal_standards": ["PE-2POC-00106", "PE-2EXP-00065"],
        "observed_variants_union": ["BDP", "Boletim Diário de Perfuração", "Daily Drilling Report", "DDR"],
        "evidence_gaps": [
            "PE dedicado ao template do BDP não localizado no SINPEP — pode existir em POCOS fora do escopo EXP indexado. Confirmar.",
            "Schema preciso dos campos estruturados (pode ser próprio do OpenWells/Atlas e não auditado em padrão Petrobras).",
        ],
        "sources_append": [
            {
                "doc_id": "PE-2EXP-00065",
                "section": "§3.3.2 Eventos durante perfilagem",
                "citation": "Durante a perfilagem por coluna reportar no ROP eventos anormais que gerem atraso, interrupção, falha ou dúvida sobre a qualidade do dado adquirido, informando o horário da ocorrência conforme relatado no BDP.",
            },
        ],
    },

    "GEOMEC051": {
        "label_pt": "OpenWells / Atlas",
        "label_en": "OpenWells / Atlas — Well Operations Datastore",
        "confidence": "medium",
        "category": "Tool",
        "definition_pt": (
            "Sistema corporativo de registro e gestão de dados operacionais de poços "
            "(perfuração, avaliação e completação): entrada do BDP, LOT/XLOT/FIT, testes de "
            "formação e demais eventos de poço em tempo real ou pós-operação. Também "
            "referenciado como \"OpenWells/Atlas\" nos padrões mais recentes. Posicionamento: "
            "fonte primária para dados operacionais de execução; dados migram para BDIEP "
            "(repositório de destino permanente). Golden source via AUTHORITATIVE_FOR para: "
            "BDP, LOT/XLOT/FIT/MFRAC, NPT, eventos de poço em execução."
        ),
        "definition_en": (
            "Corporate operations datastore for well execution data (drilling, evaluation, "
            "completion): primary entry point for BDP, LOT/XLOT/FIT/MFRAC and well events. "
            "Authoritative source for operational records, with data migrating to BDIEP for "
            "long-term archival."
        ),
        "owner_department": "POCOS/TIC",
        "internal_standards": ["PE-2POC-00106"],
        "observed_variants_union": ["OpenWells", "OpenWells/Atlas", "Atlas", "sistema de acompanhamento de poços"],
        "evidence_gaps": [
            "Owner formal: confirmar split POCOS (negócio) vs. TIC (infraestrutura).",
            "Versão atual em produção e roadmap.",
            "Mecanismo técnico de integração com BDIEP — push automático ou ETL? Latência típica?",
        ],
        "sources_append": [
            {
                "doc_id": "PE-2POC-00106",
                "section": "Tabela 1 — Registro de Testes de Pressão",
                "citation": "LOT — Nome de registro no OpenWells/Atlas: LOT; Nome de registro no SIRR: LOT - LEAKOFF TEST.",
            },
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────
# Splits — GEOMEC052 → 052A + 052B; GEOMEC053 → 053A + 053B
# Pattern follows GEOMEC026 deprecation (kept for audit, refs re-routed)
# ─────────────────────────────────────────────────────────────────────────
SPLIT_DEFINITIONS = {
    "GEOMEC052A": {
        "id": "GEOMEC052A",
        "label_pt": "PRV — Pressure Relief Valve",
        "label_en": "Pressure Relief Valve (MPD hardware)",
        "category": "Tool",
        "confidence": "high",
        "acronym": ["PRV"],
        "observed_variants": ["PRV", "Pressure Relief Valve", "válvula de alívio MPD"],
        "definition_pt": (
            "Válvula de alívio de pressão física, instalada no manifold de superfície do "
            "sistema MPD. Pode ser mecânica (abre completamente e permanece aberta até "
            "fechamento manual) ou eletrônica (possui setpoints distintos de abertura e "
            "fechamento, com alarme visual e sonoro). Atua como dispositivo de proteção "
            "secundário contra sobrepressurização do poço. Ajuste de pressão de "
            "abertura/fechamento pode ser remoto."
        ),
        "definition_en": (
            "Physical pressure relief valve installed on the MPD surface manifold. Mechanical "
            "type opens fully and stays open until manual reset; electronic type has distinct "
            "opening/closing setpoints with visual/audible alarms. Secondary overpressure "
            "protection."
        ),
        "standard_unit": "psi",
        "units_observed": ["psi", "kPa"],
        "owner_department": "POCOS",
        "internal_standards": ["PE-2POC-01247"],
        "operational_ranges": {
            "PRV_PMCD_BufferToChoke_psi": 2400,
            "PRV_BufferManifold_returnLines_psi": 1700,
        },
        "relationships": [
            {"target_id": "GEOMEC020", "relation_type": "IS_PART_OF",
             "target_label": "Perfuração com Controle de Pressão (MPD)"},
            {"target_id": "GEOMEC052B", "relation_type": "USED_WITH",
             "target_label": "Setpoint MPD/SBP",
             "edge_note": "PRV é proteção secundária; o controle ativo é via setpoint do SBP (PE-2POC-01247 §3.3.4)."},
        ],
        "sources": [
            {
                "doc_id": "PE-2POC-01247",
                "section": "§3.3.4 Pressure Relief Valve",
                "citation": "PRVs: São válvulas de alívio com abertura total quando acionadas. Podem ser mecânicas ou eletrônicas. O ajuste de sua pressão de abertura/fechamento pode ser feito de forma remota.",
            },
        ],
    },
    "GEOMEC052B": {
        "id": "GEOMEC052B",
        "label_pt": "Setpoint MPD / SBP",
        "label_en": "MPD Surface Back Pressure Setpoint",
        "category": "Property",
        "confidence": "high",
        "acronym": ["SBP", "SPL", "Bias", "High Limit"],
        "observed_variants": ["Setpoint MPD", "Surface Back Pressure setpoint", "SPL (Halliburton)", "Bias (SLB)", "High Limit (Weatherford)"],
        "definition_pt": (
            "Valor lógico de pressão configurado no software do sistema MPD para controle "
            "ativo da contrapressão de superfície pelos chokes automatizados. É o alvo de "
            "controle do sistema (não a PRV física). Distintos por fornecedor: Secondary "
            "Pressure Limiter (Halliburton), Bias (SLB), High Limit (Weatherford). Limite "
            "operacional típico: 750 psi para perfuração; 900 psi para completação."
        ),
        "definition_en": (
            "Logical pressure value configured in the MPD software for active surface back "
            "pressure control via automated chokes. Vendor-specific naming: SPL (Halliburton), "
            "Bias (SLB), High Limit (Weatherford). Typical operational limits: 750 psi "
            "drilling; 900 psi completion."
        ),
        "standard_unit": "psi",
        "units_observed": ["psi", "kPa"],
        "owner_department": "POCOS",
        "internal_standards": ["PE-2POC-01247"],
        "operational_ranges": {
            "drilling_limit_psi": 750,
            "completion_limit_psi": 900,
        },
        "relationships": [
            {"target_id": "GEOMEC020", "relation_type": "IS_PART_OF",
             "target_label": "Perfuração com Controle de Pressão (MPD)"},
            {"target_id": "GEOMEC041", "relation_type": "INFLUENCES",
             "target_label": "Contrapressão de Superfície (SBP)"},
        ],
        "sources": [
            {
                "doc_id": "PE-2POC-01247",
                "section": "§3.3.4 Hierarquia de Controle MPD",
                "citation": "Em operações com os demais sistemas de contrapressão, deve-se ajustar o SPL ou Bias como recurso primário e a PRV como secundário.",
            },
        ],
    },
    "GEOMEC053A": {
        "id": "GEOMEC053A",
        "label_pt": "Pressão de Reabertura de Fratura",
        "label_en": "Fracture Reopening Pressure",
        "category": "Measurement",
        "confidence": "high",
        "acronym": ["FRP"],
        "observed_variants": ["FRP", "pressão de reabertura", "Fracture Reopening Pressure", "MFRAC ABS ULT C"],
        "definition_pt": (
            "Pressão na qual uma fratura preexistente reaberta durante um segundo ciclo de "
            "bombeio (XLOT ou microfraturamento) começa a se propagar novamente. Obtida no 2º "
            "ciclo do teste pelo ponto de desvio da linearidade. A diferença entre a Pressão "
            "de Quebra (1º ciclo) e a Pressão de Reabertura é igual à resistência à tração da "
            "rocha. Sequência cronológica do teste: Pressão de Quebra (1º ciclo) > Pressão de "
            "Propagação ≥ Pressão de Reabertura (2º ciclo) > ISIP > Pc."
        ),
        "definition_en": (
            "Pressure at which a pre-existing fracture re-opens during a second pumping cycle "
            "of XLOT or microfrac, picked at the deviation from linearity in the 2nd cycle. "
            "Difference between Breakdown Pressure (1st cycle) and Reopening Pressure equals "
            "the rock tensile strength."
        ),
        "standard_unit": "kPa",
        "units_observed": ["kPa", "psi", "kgf/cm²"],
        "owner_department": "POCOS / RES/TR/GMR",
        "official_datastore": ["OpenWells", "Atlas", "SIRR"],
        "internal_standards": ["PE-2POC-00106", "PE-2POC-01151", "PP-2E&P-00322"],
        "relationships": [
            {"target_id": "GEOMEC006", "relation_type": "IS_PART_OF",
             "target_label": "Testes de Absorção e Fraturamento (LOT/xLOT/FIT)"},
            {"target_id": "GEOMEC042", "relation_type": "PRECEDED_BY",
             "target_label": "ISIP — Pressão Instantânea de Fechamento",
             "edge_note": "Reabertura ocorre no 2º ciclo, ANTES do ISIP do mesmo ciclo."},
            {"target_id": "GEOMEC053B", "relation_type": "RELATED_TO",
             "target_label": "Pressão de Propagação de Fratura",
             "edge_note": "Reabertura e Propagação ocorrem em fases distintas do 2º ciclo."},
        ],
        "sources": [
            {
                "doc_id": "PE-2POC-00106",
                "section": "§3.3.1 Nota 3.3.1.2 — Resistência à tração",
                "citation": "Para obter a resistência à tração da rocha e a pressão de reabertura da fratura repetir o teste. A diferença entre a pressão de quebra e a pressão de reabertura é a resistência à tração da rocha.",
            },
        ],
    },
    "GEOMEC053B": {
        "id": "GEOMEC053B",
        "label_pt": "Pressão de Propagação de Fratura",
        "label_en": "Fracture Propagation Pressure",
        "category": "Measurement",
        "confidence": "high",
        "acronym": ["FPP"],
        "observed_variants": ["FPP", "pressão de propagação", "Fracture Propagation Pressure", "XLOT ABS ULT C", "MFRAC ABS ULT C"],
        "definition_pt": (
            "Patamar de pressão estabilizado durante bombeio contínuo no XLOT/microfraturamento, "
            "no qual a fratura já propagou e se mantém aberta. Registrada como `XLOT ABS ULT C` "
            "e `MFRAC ABS ULT C` no OpenWells/Atlas. Uso operacional: limite superior da janela "
            "operacional via XLOT (calibração de Shmin)."
        ),
        "definition_en": (
            "Stabilized pressure plateau during continuous pumping in XLOT/microfrac, at which "
            "the fracture has propagated and remains open. Operational use: upper bound of the "
            "drilling window via XLOT (Shmin calibration)."
        ),
        "standard_unit": "kPa",
        "units_observed": ["kPa", "psi", "kgf/cm²"],
        "owner_department": "POCOS / RES/TR/GMR",
        "official_datastore": ["OpenWells", "Atlas", "SIRR"],
        "internal_standards": ["PE-2POC-00106", "PE-2POC-01151", "PP-2E&P-00322"],
        "relationships": [
            {"target_id": "GEOMEC006", "relation_type": "IS_PART_OF",
             "target_label": "Testes de Absorção e Fraturamento (LOT/xLOT/FIT)"},
            {"target_id": "GEOMEC002", "relation_type": "ESTIMATES",
             "target_label": "Tensão Mínima Horizontal (Shmin)",
             "edge_note": "Pressão de Propagação é usada como estimativa de Shmin no XLOT."},
            {"target_id": "GEOMEC003", "relation_type": "DEFINES_UPPER_BOUND",
             "target_label": "Janela Operacional de Lama"},
        ],
        "sources": [
            {
                "doc_id": "PE-2POC-00106",
                "section": "Tabela 1 — Registro no OpenWells/Atlas",
                "citation": "MFRAC ABS ULT C — pressão de propagação registrada no patamar estabilizado durante bombeio contínuo do microfraturamento.",
            },
        ],
    },
}


# Relations to re-route after splits (active edges currently pointing to 052/053)
REROUTE_AFTER_SPLIT = [
    # GEOMEC041 (SBP) CONSTRAINS GEOMEC052 → GEOMEC052B (lógico, alvo do controle)
    {"source": "GEOMEC041", "old_target": "GEOMEC052", "new_target": "GEOMEC052B",
     "relation_type": "CONSTRAINS"},
    # GEOMEC043 (Pc) RELATED_TO GEOMEC053 → split em 2 arestas para 053A e 053B
    {"source": "GEOMEC043", "old_target": "GEOMEC053", "new_target": "GEOMEC053A",
     "relation_type": "RELATED_TO"},
    {"source": "GEOMEC043", "old_target": "GEOMEC053", "new_target": "GEOMEC053B",
     "relation_type": "RELATED_TO", "extra": True},  # extra = adicionar segunda aresta
]


def _norm_units_observed(entity: dict, new_units: list[str]) -> None:
    existing = entity.get("units_observed") or []
    seen = set(existing)
    for u in new_units:
        if u not in seen:
            existing.append(u)
            seen.add(u)
    entity["units_observed"] = existing


def _norm_acronym(entity: dict, additions: list[str]) -> None:
    existing = entity.get("acronym") or []
    seen = {a.lower() for a in existing}
    for a in additions:
        if a.lower() not in seen:
            existing.append(a)
            seen.add(a.lower())
    entity["acronym"] = existing


def apply_enrichment(by_id: dict, eid: str, payload: dict, log: list[str]) -> None:
    e = by_id.get(eid)
    if not e:
        log.append(f"  SKIP {eid}: entity not found")
        return
    legacy = e.setdefault("_legacy", {})
    for field, value in payload.items():
        if field.endswith("_union") or field.endswith("_append"):
            base_field = field.rsplit("_", 1)[0]
            if field.endswith("_union"):
                _norm_acronym(e, value) if base_field == "acronym" else None
                if base_field == "observed_variants":
                    existing = e.get("observed_variants") or []
                    seen = set(existing)
                    for v in value:
                        if v not in seen:
                            existing.append(v); seen.add(v)
                    e["observed_variants"] = existing
                elif base_field == "units_observed":
                    _norm_units_observed(e, value)
            elif field.endswith("_append"):
                # sources_append, evidence_gaps_append, etc.
                target = e.setdefault(base_field, [])
                if base_field == "sources":
                    seen = {(s.get("doc_id"), s.get("section"), (s.get("citation") or "")[:60])
                            for s in target if isinstance(s, dict)}
                    for s in value:
                        key = (s.get("doc_id"), s.get("section"), (s.get("citation") or "")[:60])
                        if key not in seen:
                            target.append(s); seen.add(key)
                else:
                    seen = set(target)
                    for v in value:
                        if v not in seen:
                            target.append(v); seen.add(v)
        elif field == "subsidence_ranges" or field == "operational_ranges":
            # structured field — set/replace
            old = e.get(field)
            if old != value:
                if old not in (None, []):
                    legacy.setdefault(field, old)
                e[field] = value
        elif field == "evidence_gaps":
            # full replace (team curated this list)
            old = e.get(field)
            if old not in (None, []) and old != value:
                legacy.setdefault(field, old)
            e[field] = value
        else:
            old = e.get(field)
            if old != value:
                if old not in (None, "", [], {}):
                    legacy.setdefault(field, old)
                e[field] = value
    log.append(f"  ENRICH {eid} ({e.get('label_pt')[:50]}): {len(payload)} field updates")


def split_entity(by_id: dict, original_id: str, new_entities: list[dict],
                 reroutes: list[dict], log: list[str]) -> None:
    orig = by_id.get(original_id)
    if not orig:
        log.append(f"  SKIP split {original_id}: not found")
        return
    # Skip if already split (idempotency)
    if all(ne["id"] in by_id for ne in new_entities):
        log.append(f"  SKIP split {original_id}: replacement entities already exist")
        return
    # Mark original as deprecated (preserves audit), archive original relations
    orig.setdefault("_legacy", {})["original_relationships"] = list(orig.get("relationships") or [])
    orig["relationships"] = []
    orig["deprecated"] = {
        "replaced_by": [ne["id"] for ne in new_entities],
        "reason": (
            f"Split decidido pela governança 2026-05-02 — substituído por "
            f"{', '.join(ne['id'] + ' (' + ne['label_pt'] + ')' for ne in new_entities)}."
        ),
    }
    log.append(f"  DEPRECATE {original_id}: replaced_by={[ne['id'] for ne in new_entities]}")

    # Add new entities
    parent_list = None
    # Find the parent list (entities) by reference
    for k, v in by_id.items():
        if v is orig:
            break
    # The actual entities list is held in the JSON outer structure — we'll rebuild after
    for ne in new_entities:
        if ne["id"] in by_id:
            log.append(f"  SKIP add {ne['id']}: already exists")
            continue
        by_id[ne["id"]] = ne
        log.append(f"  ADD {ne['id']} ({ne['label_pt']}) — confidence={ne.get('confidence')}")


def reroute_relations(by_id: dict, log: list[str]) -> None:
    for r in REROUTE_AFTER_SPLIT:
        ent = by_id.get(r["source"])
        if not ent:
            continue
        rels = ent.get("relationships") or []
        if r.get("extra"):
            # add an additional relation to the second target (don't touch the first)
            if any(x.get("relation_type") == r["relation_type"] and x.get("target_id") == r["new_target"] for x in rels):
                log.append(f"  SKIP reroute extra {r['source']} {r['relation_type']}→{r['new_target']}: exists")
                continue
            new_rec = {"target_id": r["new_target"], "relation_type": r["relation_type"],
                       "target_label": by_id[r["new_target"]].get("label_pt"),
                       "_split_from": r["old_target"]}
            rels.append(new_rec)
            ent["relationships"] = rels
            log.append(f"  REROUTE-ADD {r['source']} {r['relation_type']}→{r['new_target']}")
        else:
            mutated = False
            for x in rels:
                if x.get("relation_type") == r["relation_type"] and x.get("target_id") == r["old_target"]:
                    x["target_id"] = r["new_target"]
                    x["target_label"] = by_id[r["new_target"]].get("label_pt")
                    x["_repointed_from"] = r["old_target"]
                    mutated = True
                    log.append(f"  REROUTE   {r['source']} {r['relation_type']}: {r['old_target']}→{r['new_target']}")
            if not mutated:
                log.append(f"  SKIP reroute {r['source']} {r['relation_type']}→{r['old_target']}: not present (already done?)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entities"]}
    log: list[str] = []

    # 1. Apply enrichments to 6 entities
    for eid, payload in ENRICHMENTS.items():
        # Translate _union/_append-style fields appropriately
        translated = {}
        for k, v in payload.items():
            if k == "observed_variants_union":
                translated["observed_variants_union"] = v
            elif k == "sources_append":
                translated["sources_append"] = v
            elif k == "acronym_union":
                translated["acronym_union"] = v
            else:
                translated[k] = v
        apply_enrichment(by_id, eid, translated, log)

    # 2. Splits — 052 and 053
    split_entity(by_id, "GEOMEC052",
                 [SPLIT_DEFINITIONS["GEOMEC052A"], SPLIT_DEFINITIONS["GEOMEC052B"]],
                 REROUTE_AFTER_SPLIT, log)
    split_entity(by_id, "GEOMEC053",
                 [SPLIT_DEFINITIONS["GEOMEC053A"], SPLIT_DEFINITIONS["GEOMEC053B"]],
                 REROUTE_AFTER_SPLIT, log)

    # 3. Re-route active references to 052 and 053
    reroute_relations(by_id, log)

    # 4. Rebuild the entity list, sorted by id (with split children adjacent to parent)
    def sort_key(eid: str) -> tuple:
        import re
        m = re.match(r"GEOMEC(\d+)([A-Z]?)$", eid)
        return (int(m.group(1)), m.group(2)) if m else (9999, eid)
    data["entities"] = [by_id[k] for k in sorted(by_id.keys(), key=sort_key)]

    # 5. Update architecture_notes
    notes = data["meta"].setdefault("architecture_notes", [])
    note_str = (
        "Frente F response 2026-05-02 — Gestão e Governança de Dados aplicou "
        "evidências documentais SINPEP a 8 entidades skeleton: 6 enriquecidas "
        "in-place (GEOMEC046–051), 2 splits (GEOMEC052→052A+052B, "
        "GEOMEC053→053A+053B) seguindo o padrão de deprecação do GEOMEC026. "
        "4 entidades promovidas para confidence=high (046, 052A, 052B, 053A, 053B); "
        "5 promovidas para medium (047, 048, 049, 050, 051). Lacunas residuais "
        "documentadas em cada entity.evidence_gaps."
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
