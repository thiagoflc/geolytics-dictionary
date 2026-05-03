#!/usr/bin/env python3
"""Extend data/operacoes-geologicas.json with ANP-699/2017 document classes,
the Poço class with ANP-699 attributes, and an ANP regulatory document
lineage instance.

Source: Resolução ANP nº 699/2017 — Capítulos II–V + Anexo III.

Adds:
  18 new classes (subClassOf GeologicalOperationsDocument):
    NPP, CIPP, CUEPP, LAEP, SOP_ANP, ND, NPR, FP_ANP, RFAP, RCP, RFP,
    RFP_PROD, CRP_ANP, NCRP, RPF, PVT_Report, RGP, NCSB
  1 new class:
    Poco (ANP-699 attributes: cadastro_anp, categoria_anp, tipo_anp, etc.)
  1 new instance:
    OG_DOC_LINEAGE_ANP (regulatory document chain)

Each new doc class carries:
  - prazo_envio: deadline string from Anexo III
  - gatilho: trigger event
  - conteudo_resumido: summary of required content
  - forma_envio: typically "via sistema (i-SIGEP / i-ENGINE)" or "físico"
  - corporate_internal: false (all are public regulatory)
  - evidence_refs: ANP-699/2017 + specific article

Idempotent — re-running on a patched JSON is a no-op.
Usage: python3 scripts/migrations/2026-05-03/extend-og-with-anp-699-docs.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "data" / "operacoes-geologicas.json"

# ---------------------------------------------------------------------------
# 18 ANP-699 document classes
# ---------------------------------------------------------------------------
# Convention: id = OG-ANP-NNN. All subClassOf GeologicalOperationsDocument.
# Names follow the sigla; for collisions with existing OG classes we keep the
# regulator-side id distinct (e.g., "FP_ANP" because FP is also Pressão de Fluxo).

ANP_DOC_CLASSES = [
    {
        "id": "OG-ANP-001",
        "name": "NPP",
        "name_pt": "NotificacaoPerfuracaoPoco",
        "label_pt": "NPP — Notificação de Perfuração de Poço",
        "label_en": "Well Drilling Notification (NPP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted to ANP at least 20 days before the planned start of drilling, or before use of Small-Scale Equipment for the first well phases. Composed of 6 sections: i) basic well data; ii) planned spud date, rig, base/target coordinates, final depth/stratigraphic unit; iii) prospect data with petroleum-system probabilities and statistical volumetric properties; iv) prospect images (stratigraphy, seismic lines, location and geological maps/sections); v) formations to be crossed; vi) planned phases with casing/cementing characteristics.",
        "description_pt": "Documento enviado à ANP em no mínimo 20 dias antes do Início de Perfuração, ou do início da utilização de Equipamentos de Pequeno Porte. 6 seções: i) dados básicos do poço; ii) data prevista, sonda, coordenadas, profundidade/unidade estratigráfica finais; iii) prospecto com probabilidades do sistema petrolífero e volumétrica; iv) imagens (estratigrafia, sísmica, mapas/seções); v) formações a atravessar; vi) fases previstas com revestimentos/cimentações.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "no mínimo 20 dias antes da data prevista para o Início de Perfuração",
        "gatilho": "antes do Início de Perfuração",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §1"],
        "synonyms": ["NPP", "Notificação de Perfuração de Poço"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-002",
        "name": "CIPP",
        "name_pt": "ComunicacaoInicioPerfuracaoPoco",
        "label_pt": "CIPP — Comunicação de Início de Perfuração de Poço",
        "label_en": "Well Spud Notice (CIPP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted to ANP within 6 hours after the well Spud (Início de Perfuração). Contains base coordinates, rig identification, and the environmental authorization for the activity (including post-issuance amendments such as inclusion of drilling units in the license). Triggers ANP cadastro emission within 5 business days.",
        "description_pt": "Documento enviado à ANP em até 6 horas após o Início de Perfuração. Contém coordenadas da base, sonda e autorização ambiental para execução da atividade (incluindo eventuais anuências posteriores). A partir desse cadastro o poço recebe seu Cadastro e Nome oficiais em até 5 dias úteis.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "até 6 horas após o Início de Perfuração",
        "gatilho": "Início de Perfuração",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §2"],
        "synonyms": ["CIPP", "Comunicação de Início de Perfuração"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-003",
        "name": "CUEPP",
        "name_pt": "ComunicacaoUtilizacaoEquipamentoPequenoPorte",
        "label_pt": "CUEPP — Comunicação de Utilização de Equipamento de Pequeno Porte",
        "label_en": "Small-Scale Equipment Use Notice (CUEPP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted to ANP within 6 hours of formation cutting using Small-Scale Equipment for the first phases of an onshore well, up to surface casing setting depth.",
        "description_pt": "Documento enviado à ANP em até 6 horas após início do corte de formação com Equipamentos de Pequeno Porte (EPP) para as primeiras fases de poço terrestre, até no máximo a descida do revestimento de superfície.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "até 6 horas após o início do corte de formação",
        "gatilho": "início do corte de formação com EPP em poço terrestre",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §3"],
        "synonyms": ["CUEPP", "Comunicação de Utilização de Equipamento de Pequeno Porte"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-004",
        "name": "LAEP",
        "name_pt": "LicencaAmbientalEP",
        "label_pt": "LAEP — Licença Ambiental para E&P",
        "label_en": "Environmental License (E&P)",
        "superclass": "GeologicalOperationsDocument",
        "description": "IBAMA/state environmental license for drilling, completion, evaluation, intervention or abandonment activities. Must be submitted to ANP before or together with NPP (already obtained) or before/together with CIPP (otherwise). For re-entry, before/together with CRP.",
        "description_pt": "Licença ambiental (IBAMA/estadual) para perfuração, completação, avaliação, intervenção ou abandono. Deve ser enviada antes ou concomitantemente à NPP (caso já obtida) ou antes/concomitante à CIPP. Para reentradas, antes/concomitante à CRP.",
        "format": "document",
        "structured": "no",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "antes ou concomitante à NPP/CIPP/CRP conforme caso",
        "gatilho": "obtenção da licença ambiental",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §4"],
        "synonyms": ["LAEP", "Licença Ambiental"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-005",
        "name": "SOP_ANP",
        "name_pt": "SituacaoOperacionalPocos",
        "label_pt": "SOP — Situação Operacional de Poços",
        "label_en": "Daily Well Operational Status Report (SOP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Daily report submitted to ANP between 6h and 12h, covering operations performed the previous day. Includes basic well info, current depth, stratigraphic unit, and main operations (kicks, losses, stuck pipe, etc.). Required during drilling (incl. Small-Scale Equipment), evaluation (incl. TLD), completion, restoration, abandonment and any well intervention. Sent through i-Engine.",
        "description_pt": "Boletim diário enviado à ANP entre 6h e 12h, sobre operações do dia anterior. Inclui dados básicos do poço, profundidade, unidade estratigráfica atual e principais operações (kicks, perdas de circulação, prisões de coluna). Devido durante perfuração (incl. EPP), avaliação (incl. TLD), completação, restauração, abandono e qualquer intervenção. Enviado via i-Engine.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-Engine",
        "prazo_envio": "diariamente entre 6h e 12h",
        "gatilho": "operações em poço (todo dia útil)",
        "forma_envio": "via sistema (i-Engine)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §5"],
        "synonyms": ["SOP", "Situação Operacional de Poços"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-006",
        "name": "ND",
        "name_pt": "NotificacaoDescoberta",
        "label_pt": "ND — Notificação de Descoberta",
        "label_en": "Discovery Notification (ND)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted to ANP within 72 hours after characterization of a discovery, per Concession/Production-Sharing/Onerous-Assignment contracts. 3 sections matching detection methods: i) rock/mud-gas drilling-time indications; ii) zones of interest from log interpretation with petrophysical properties; iii) hydrocarbon recovery in formation tests (DST or wireline). ND identified by fewer than 2 methods may be justified in observation fields.",
        "description_pt": "Documento enviado à ANP em até 72 horas após caracterização da descoberta. 3 seções por método de detecção: i) indícios em amostras de rocha/detector de gás; ii) zonas de interesse por perfis com propriedades petrofísicas; iii) recuperação em testes de formação (tubulação ou cabo).",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "até 72 horas após a caracterização da ocorrência",
        "gatilho": "caracterização da descoberta (≥2 métodos)",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §6"],
        "synonyms": ["ND", "Notificação de Descoberta"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-007",
        "name": "NPR",
        "name_pt": "NotificacaoPerfilagensRealizadas",
        "label_pt": "NPR — Notificação de Perfilagens Realizadas",
        "label_en": "Logging Operations Notification (NPR)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted within 10 days after final logging or well conclusion (whichever is applicable). 4 sections: i) basic operation data; ii) drilling-time logs; iii) conventional logs run; iv) special logs (seismic, sidewall, cable tests, perforation, production logs).",
        "description_pt": "Documento enviado em até 10 dias após perfilagem final ou Conclusão do Poço. 4 seções: i) dados básicos; ii) perfis corridos durante perfuração; iii) perfis convencionais; iv) perfis especiais (sísmicos, amostragem lateral, testes a cabo, canhoneio, perfis de produção).",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "10 dias após a perfilagem final do poço",
        "gatilho": "perfilagem final ou Conclusão do Poço (sem perfilagem)",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §7"],
        "synonyms": ["NPR", "Notificação de Perfilagens Realizadas"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-008",
        "name": "FP_ANP",
        "name_pt": "RelatorioFinalPerfuracao",
        "label_pt": "FP — Relatório Final de Perfuração",
        "label_en": "Final Drilling Report (FP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Final drilling report due within 60 days after end of drilling activities. 8 sections: i) basic well data; ii) phase data (diameters, depths, dates, rig, absorption tests); iii) casing details (weight, metallurgy, connections, accessories like centralizers); iv) drilling fluid types and properties per phase; v) bit data with classification, wear indicator, drilling parameters; vi) BHA composition and objective per phase; vii) cementing data (depths, slurry/auxiliary fluid characteristics); viii) drilling non-conformities causing lost time.",
        "description_pt": "Relatório final de perfuração em até 60 dias após término das atividades. 8 seções: i) dados básicos; ii) dados das fases (diâmetros, profundidades, datas, sonda, testes de absorção); iii) revestimentos descidos (peso, metalurgia, conexões, centralizadores); iv) fluidos de perfuração; v) brocas (classificação, desgaste, parâmetros); vi) BHA por fase; vii) cimentações; viii) não-conformidades.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após o término das atividades de perfuração",
        "gatilho": "término das atividades de perfuração",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §8"],
        "synonyms": ["FP", "Relatório Final de Perfuração"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-009",
        "name": "RFAP",
        "name_pt": "RelatorioFinalAbandonoPoco",
        "label_pt": "RFAP — Relatório Final de Abandono de Poço",
        "label_en": "Final Well Abandonment Report (RFAP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 30 days after the abandonment intervention. 8 sections: i) basic abandonment data, unit, type, motivation; ii) barrier-envelope description; iii) cement plug characteristics and depths; iv) casings and column components remaining post-abandonment; v) fish left in well due to recovery impossibility; vi) open-hole intervals, intervals covered by torn pipes, perforations; vii) mechanical plugs with nature; viii) re-cemented intervals (especially corrective). Includes well mechanical schematic post-abandonment.",
        "description_pt": "Relatório em até 30 dias após a conclusão da intervenção de abandono. 8 seções: i) dados básicos do abandono; ii) conjuntos solidários de barreiras; iii) tampões de cimento; iv) revestimentos pós-abandono; v) peixe no poço; vi) intervalos abertos/cobertos/canhoneados; vii) tampões mecânicos; viii) recimentações. Anexo: esquema mecânico pós-abandono.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "30 dias após a conclusão da intervenção de abandono",
        "gatilho": "conclusão da intervenção de abandono",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §9", "ANP-46/2016"],
        "synonyms": ["RFAP", "Relatório Final de Abandono de Poço"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-010",
        "name": "RCP",
        "name_pt": "RelatorioCompletacaoPoco",
        "label_pt": "RCP — Relatório de Completação de Poço",
        "label_en": "Well Completion Report (RCP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 60 days after completion. 8 sections: i) basic completion data; ii) production casings (incl. liners and torn pipes); iii) production intervals with petrophysical properties and perforation; iv) stimulation operations (fracturing, acidizing, solvent injection — materials, volumes, pressures); v) sand-control system; vi) production/injection column description; vii) basic data of formation tests by tubing during the workover/completion; viii) artificial-lift method. Includes mechanical schematic post-completion.",
        "description_pt": "Relatório em até 60 dias após o término da completação. 8 seções: i) dados básicos; ii) revestimentos de produção (liners, tubos rasgados); iii) intervalos de produção (petrofísica, canhoneio); iv) estimulação (fraturamento, acidificação, solvente); v) contenção de areia; vi) coluna de produção/injeção; vii) testes de formação por tubulação; viii) método de elevação artificial. Anexo: esquema mecânico pós-completação.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após a conclusão da completação",
        "gatilho": "conclusão da completação",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §10"],
        "synonyms": ["RCP", "Relatório de Completação de Poço"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-011",
        "name": "RFP",
        "name_pt": "RelatorioFinalPocoExploratorio",
        "label_pt": "RFP — Relatório Final de Poço Exploratório",
        "label_en": "Final Exploratory Well Report (RFP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 60 days after Conclusão do Poço (exploratório). 10 sections covering: definitive coordinates, final depths, predicted vs observed stratigraphic unit tops; hydrocarbon indications; lithological description of cores and sidewall samples; zones of interest with calculated petrophysical properties; formation tests; temperatures; calha sampling pattern; volumetric appropriation; conclusions on well result. Annexes: comments on well objectives; updated maps/sections; rock-sample description; geological accompaniment profile; petrophysical/petrographic/geochemical/biostratigraphic/fluid lab results; time-depth from seismic; pressure-depth from cable records.",
        "description_pt": "Relatório em até 60 dias após Conclusão do Poço (exploratório). 10 seções: coordenadas definitivas, profundidades finais, topos previstos x constatados; índices de HC; litologia de testemunhos/amostras laterais; zonas de interesse com petrofísica; testes de formação; temperaturas; padrão de amostragem de calha; apropriação volumétrica; conclusões sobre resultado. Anexos: comentários sobre objetivos; mapas/seções; descrição de amostras; perfil de acompanhamento geológico; ensaios laboratoriais; tabela tempo-profundidade; tabela pressão-profundidade.",
        "format": "structured + visualizations",
        "structured": "semi",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após a Conclusão do Poço",
        "gatilho": "Conclusão do Poço (exploratório)",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §11"],
        "synonyms": ["RFP", "Relatório Final de Poço Exploratório"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-012",
        "name": "RFP_PROD",
        "name_pt": "RelatorioFinalPocoExplotatorio",
        "label_pt": "RFP-PROD — Relatório Final de Poço Explotatório",
        "label_en": "Final Production Well Report (RFP-PROD)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 60 days after Conclusão do Poço (explotatório). 8 sections: basic data, well result, top/base depths of crossed reservoirs, predicted vs observed stratigraphic unit tops, lithological core description, zones of interest with petrophysics, formation tests, temperature table, calha sampling pattern.",
        "description_pt": "Relatório em até 60 dias após Conclusão do Poço (explotatório). 8 seções: dados básicos, resultados do poço, topos/base de reservatórios atravessados, topos estratigráficos previstos x constatados, descrição litológica de testemunhos, zonas de interesse com petrofísica, testes de formação, tabela de temperaturas, padrão de amostragem de calha.",
        "format": "structured + visualizations",
        "structured": "semi",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após a Conclusão do Poço",
        "gatilho": "Conclusão do Poço (explotatório)",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §12"],
        "synonyms": ["RFP-PROD", "Relatório Final de Poço Explotatório"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-013",
        "name": "CRP_ANP",
        "name_pt": "ComunicacaoReentradaPoco",
        "label_pt": "CRP — Comunicação de Reentrada em Poço",
        "label_en": "Well Re-entry Notice (CRP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted within 1 day after the start of re-entry, defined by BOP connection. In interventions without BOP, start is the moment of tool descent into the well. Contains basic data (start date, intervention unit), environmental authorization, motivation, objectives and planned operations.",
        "description_pt": "Documento enviado em até 1 dia após o início da reentrada (conexão do BOP). Em intervenções sem BOP, o início é a descida de ferramentas. Contém dados básicos (data, unidade), autorização ambiental, motivação, objetivos e operações previstas.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "1 dia após o início da reentrada",
        "gatilho": "conexão do BOP (ou descida de ferramenta) em reentrada",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §13"],
        "synonyms": ["CRP", "Comunicação de Reentrada em Poço"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-014",
        "name": "NCRP",
        "name_pt": "NotificacaoConclusaoReentradaPoco",
        "label_pt": "NCRP — Notificação de Conclusão de Reentrada em Poço",
        "label_en": "Well Re-entry Conclusion Notification (NCRP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document submitted within 10 days after conclusion of operations, marked by disconnection of the unit performing the re-entry. Contains basic data (conclusion date), well state after conclusion, operations performed and data acquired.",
        "description_pt": "Documento enviado em até 10 dias após conclusão das operações, marcada pela desvinculação da unidade que realizou a reentrada. Contém dados básicos (data de conclusão), estado do poço após, operações realizadas e dados adquiridos.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "10 dias após a conclusão das operações na reentrada",
        "gatilho": "desvinculação da unidade que realizou a reentrada",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §14"],
        "synonyms": ["NCRP", "Notificação de Conclusão de Reentrada em Poço"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-015",
        "name": "RPF",
        "name_pt": "RelatorioEnsaiosPetrofisicos",
        "label_pt": "RPF — Relatório de Ensaios Petrofísicos",
        "label_en": "Petrophysical Tests Report (RPF)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 60 days after laboratory tests are completed. 5 sections: i) basic data (start/end dates, lab); ii) listing of analyzed rock samples (type, depths, basic petrophysics); iii) compressibility test results (P × compressibility curve points); iv) capillary pressure test results (parameters and curves P × saturation); v) relative permeability test results (parameters and curves k × saturation).",
        "description_pt": "Relatório em até 60 dias após o término dos ensaios laboratoriais. 5 seções: i) dados básicos (datas, lab); ii) amostras de rocha (tipo, profundidades, petrofísica básica); iii) compressibilidade (curva P × compressibilidade); iv) pressão capilar (curvas P × saturação); v) permeabilidade relativa (curvas k_relativa × saturação).",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador / Laboratório",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após o término dos ensaios laboratoriais (semestral aceito para muitos poços)",
        "gatilho": "término de sequência de ensaios planejada para o poço",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §15"],
        "synonyms": ["RPF", "Relatório de Ensaios Petrofísicos"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-016",
        "name": "PVT_Report",
        "name_pt": "RelatorioEnsaiosPVT",
        "label_pt": "PVT — Relatório de Ensaios de PVT",
        "label_en": "PVT Tests Report",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 60 days after laboratory tests. 6 sections: i) basic data (dates, lab); ii) fluid samples (type, depths, flash data); iii) Constant Composition Expansion (CCE); iv) Differential Liberation; v) Separator Tests; vi) Constant Volume Depletion (CVD).",
        "description_pt": "Relatório em até 60 dias após o término dos ensaios. 6 seções: i) dados básicos; ii) amostras de fluido (tipo, profundidades, flash); iii) Expansão a Composição Constante (CCE); iv) Liberação Diferencial; v) Testes de Separador; vi) Depleção a Volume Constante (CVD).",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador / Laboratório",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após o término dos ensaios laboratoriais",
        "gatilho": "término de sequência de ensaios PVT",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §16"],
        "synonyms": ["PVT (relatório)", "Relatório de Ensaios de PVT"],
        "corporate_internal": False,
        "collision_note": "Distinct from existing PVT entity (Pressure-Volume-Temperature property concept). This class refers specifically to the regulatory report deliverable.",
    },
    {
        "id": "OG-ANP-017",
        "name": "RGP",
        "name_pt": "RelatorioGeoquimicaPoco",
        "label_pt": "RGP — Relatório de Geoquímica de Poço",
        "label_en": "Well Geochemistry Report (RGP)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document due within 60 days after laboratory tests. Sections include basic data (dates, lab) and test results, indicating samples (depth and stratigraphic unit) and TOC data, insoluble residue, pyrolysis parameters and other analyses for source-rock characterization.",
        "description_pt": "Relatório em até 60 dias após o término dos ensaios. Seções: dados básicos (datas, lab) e resultados — amostras (profundidade e unidade estratigráfica), COT, resíduo insolúvel, parâmetros de pirólise rock-eval e outras análises para caracterização de rocha geradora.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador / Laboratório",
        "stored_in": "i-SIGEP",
        "prazo_envio": "60 dias após o término dos ensaios laboratoriais",
        "gatilho": "término de sequência de ensaios geoquímicos",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §17"],
        "synonyms": ["RGP", "Relatório de Geoquímica de Poço"],
        "corporate_internal": False,
    },
    {
        "id": "OG-ANP-018",
        "name": "NCSB",
        "name_pt": "NotificacaoConjuntosSolidariosBarreira",
        "label_pt": "NCSB — Notificação de Conjuntos Solidários de Barreira",
        "label_en": "Well Barrier Envelope Notification (NCSB)",
        "superclass": "GeologicalOperationsDocument",
        "description": "Document tied to well lifecycle stage: Construção stage (within 10 days of any temporary abandonment >10 days); Produção stage (within 10 days of completion conclusion; new version within 10 days of any intervention); Permanent Abandonment stage (≥5 days before exploratory well permanent-barrier work; ≥20 days before explotatório well). Last submitted version must reflect current well condition.",
        "description_pt": "Documento amarrado ao ciclo de vida do poço: Construção (10 dias após abandono temporário >10 dias); Produção (10 dias após conclusão da completação; nova versão a cada intervenção); Abandono Permanente (≥5 dias antes em poços exploratórios; ≥20 dias antes em explotatórios). Última versão deve refletir condição atual do poço.",
        "format": "structured",
        "structured": "yes",
        "manager": "Operador",
        "stored_in": "i-SIGEP",
        "prazo_envio": "variado conforme etapa (Construção/Produção/Abandono Permanente)",
        "gatilho": "abandono temporário, completação, intervenção, ou pré-abandono permanente",
        "forma_envio": "via sistema (i-SIGEP)",
        "evidence_status": "documented",
        "evidence_refs": ["ANP-699/2017 Anexo III §18", "ANP-46/2016"],
        "synonyms": ["NCSB", "Notificação de Conjuntos Solidários de Barreira"],
        "corporate_internal": False,
    },
]

# ---------------------------------------------------------------------------
# Poço class — ANP-699 attributes
# ---------------------------------------------------------------------------
POCO_CLASS = {
    "id": "OG-ANP-POCO",
    "name": "Poco",
    "name_pt": "Poco",
    "label_pt": "Poço (entidade ANP-699)",
    "label_en": "Well (ANP-699 entity)",
    "superclass": None,
    "description": "Drilled hole for petroleum/natural-gas exploration, production, underground gas storage or correlated special purposes. Identified by an ANP Cadastro (11 digits: UF[2] + Bacia[3] + Sequencial[6]) and an ANP Name (Categoria-Sigla-Numeração+Tipo-RefGeográfica). Lifecycle covers Notificação de Perfuração (NPP) → Início de Perfuração → Término de Perfuração → Conclusão do Poço, with status reported daily via SOP.",
    "description_pt": "Furo perfurado para exploração/produção de hidrocarbonetos, estocagem subterrânea de gás ou objetivos especiais correlatos. Identificado por Cadastro ANP (11 dígitos: UF[2] + Bacia[3] + Sequencial[6]) e Nome ANP (Categoria-Sigla-Numeração+Tipo-RefGeográfica). Ciclo de vida: NPP → Início de Perfuração → Término de Perfuração → Conclusão do Poço, com status diário via SOP.",
    "evidence_status": "documented",
    "evidence_refs": ["ANP-699/2017"],
    "anp_attributes": {
        "nome_anp": {
            "type": "string",
            "regex": "^[1-9][0-9]?-[A-Z]+-[0-9]+[A-Z]?(-[A-Z]+)?$",
            "description": "Categoria-Sigla-Numeração(+Tipo opcional)-RefGeográfica. Ex: '1-RJS-685', '7-MLL-30D-RJS', '3-BRSA-944A-RJS'.",
            "evidence_refs": ["ANP-699/2017 art.4º"],
        },
        "cadastro_anp": {
            "type": "string",
            "regex": "^[0-9]{11}$",
            "description": "11 dígitos: UF(2) + Bacia(3) + Sequencial(6). Único e permanente.",
            "evidence_refs": ["ANP-699/2017 art.5º"],
        },
        "categoria_anp": {
            "type": "enum",
            "ref_codelist": "data/anp-poco-categoria.json",
            "values": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "description": "Finalidade principal original do poço (Tabela 1).",
        },
        "tipo_anp": {
            "type": "enum",
            "ref_codelist": "data/anp-poco-tipo.json",
            "values": ["", "D", "H", "P", "i", "A-Z (sequencial repetido)"],
            "description": "Trajetória / tipo do poço (art. 4º §4).",
        },
        "referencia_geografica": {
            "type": "string",
            "regex": "^[A-Z]{2}S?$",
            "description": "Sigla IBGE da UF (2 letras) + 'S' opcional para poços marítimos.",
            "ref_codelist": "data/anp-uf.json",
        },
        "bacia_anp_codigo": {
            "type": "string",
            "regex": "^[0-9]{2,3}$",
            "ref_codelist": "data/anp-bacia-sedimentar.json",
            "description": "Código numérico da bacia sedimentar (Anexo II).",
        },
        "uf_anp_codigo": {
            "type": "string",
            "regex": "^[0-9]{2}$",
            "ref_codelist": "data/anp-uf.json",
            "description": "Código numérico da UF (Anexo I).",
        },
        "operador": {
            "type": "string",
            "description": "Sigla do operador (até 4 letras maiúsculas) — para exploratórios e especiais.",
        },
        "campo": {
            "type": "string",
            "description": "Nome do campo (para explotatórios e estocagem).",
        },
        "resultado_anp": {
            "type": "enum",
            "ref_codelist": "data/anp-poco-resultado.json",
            "values": ["poco-com-hidrocarbonetos", "poco-seco", "poco-nao-qualificavel"],
            "description": "Resultado final (Cap. III). Enviado em até 60 dias após Conclusão do Poço.",
        },
        "status_anp": {
            "type": "enum",
            "ref_codelist": "data/anp-osdu-wellstatus-map.json",
            "values_source": "ANP-699/2017 Tabela 2 (19 valores)",
            "description": "Status operacional. Enviado mensalmente até dia 15.",
        },
        "data_inicio_perfuracao": {"type": "date", "description": "art. 3º XII"},
        "data_termino_perfuracao": {"type": "date", "description": "art. 3º XXXII"},
        "data_conclusao_poco": {"type": "date", "description": "art. 3º VII"},
        "is_reentrada": {
            "type": "boolean",
            "description": "True se houve CRP/NCRP (operação de reentrada).",
        },
        "is_partilhado_de": {
            "type": "ref",
            "ref_class": "Poco",
            "description": "Para Tipo P (Partilhado/Multilateral): poço de origem.",
        },
        "is_repetido_de": {
            "type": "ref",
            "ref_class": "Poco",
            "description": "Para Tipo A-Z (Repetido): poço original.",
        },
    },
    "synonyms": ["Poço", "Well", "Wellbore (ANP-699 nominal entity)"],
    "corporate_internal": False,
}

# ---------------------------------------------------------------------------
# OG_DOC_LINEAGE_ANP — regulatory document lineage instance
# ---------------------------------------------------------------------------
OG_DOC_LINEAGE_ANP = {
    "id": "OG_DOC_LINEAGE_ANP",
    "name": "ANP regulatory document lineage (canonical)",
    "name_pt": "Linhagem canônica de documentos regulatórios ANP-699",
    "class": "GeologicalOperations",
    "description": "Canonical regulatory document lineage per Resolução ANP nº 699/2017. Spans well lifecycle from pre-spud notification through final reports. Distinct from the Petrobras-internal OG_DOC_LINEAGE which covers wellsite-geology documents (QPG/IGP/RMG/etc). Both lineages coexist and are joined at the well identifier (nome_anp / cadastro_anp).",
    "description_pt": "Linhagem regulatória canônica conforme Resolução ANP nº 699/2017. Cobre o ciclo do poço desde a notificação pré-spud até relatórios finais. Distinta da OG_DOC_LINEAGE Petrobras-interna (QPG/IGP/RMG). Ambas convivem e se juntam pelo identificador do poço.",
    "is_canonical_lineage": True,
    "lineage_kind": "regulatory_anp",
    "use_in_queries": "Resolve 'qual o prazo de X?' / 'que documento ANP é exigido após Y?' / 'qual a sequência regulatória do poço?'",
    "edges": [
        {"order": 1, "source": "NPP", "target": None, "relation": "lineage_root", "evidence_status": "documented", "note": "Pre-spud — at least 20 days before drilling start."},
        {"order": 2, "source": "LAEP", "target": "NPP", "relation": "co_required", "evidence_status": "documented", "note": "Environmental license before/together with NPP."},
        {"order": 3, "source": "CIPP", "target": "NPP", "relation": "follows", "evidence_status": "documented", "note": "Within 6 hours of spud. Triggers official Cadastro/Nome assignment."},
        {"order": 4, "source": "CUEPP", "target": "CIPP", "relation": "alternative_of", "evidence_status": "documented", "note": "When using Small-Scale Equipment for first phases of land well."},
        {"order": 5, "source": "SOP_ANP", "target": "CIPP", "relation": "daily_during", "evidence_status": "documented", "note": "Daily report 6h-12h, every operational day until Conclusão."},
        {"order": 6, "source": "ND", "target": "SOP_ANP", "relation": "may_trigger", "evidence_status": "documented", "note": "Within 72 hours after discovery characterization."},
        {"order": 7, "source": "NPR", "target": "SOP_ANP", "relation": "follows", "evidence_status": "documented", "note": "Within 10 days after final logging."},
        {"order": 8, "source": "FP_ANP", "target": "NPR", "relation": "follows", "evidence_status": "documented", "note": "60 days after end of drilling activities."},
        {"order": 9, "source": "RCP", "target": "FP_ANP", "relation": "follows", "evidence_status": "documented", "note": "60 days after completion conclusion (when applicable)."},
        {"order": 10, "source": "RFAP", "target": "FP_ANP", "relation": "alternative_of_RCP", "evidence_status": "documented", "note": "30 days after abandonment — alternative outcome to completion."},
        {"order": 11, "source": "RFP", "target": "FP_ANP", "relation": "follows_for_exploratory", "evidence_status": "documented", "note": "60 days after Conclusão for exploratory wells."},
        {"order": 12, "source": "RFP_PROD", "target": "FP_ANP", "relation": "follows_for_production", "evidence_status": "documented", "note": "60 days after Conclusão for production wells."},
        {"order": 13, "source": "RPF", "target": "FP_ANP", "relation": "lab_result_of", "evidence_status": "documented", "note": "60 days after laboratory tests (petrophysics)."},
        {"order": 14, "source": "PVT_Report", "target": "FP_ANP", "relation": "lab_result_of", "evidence_status": "documented", "note": "60 days after laboratory tests (PVT)."},
        {"order": 15, "source": "RGP", "target": "FP_ANP", "relation": "lab_result_of", "evidence_status": "documented", "note": "60 days after laboratory tests (geochemistry)."},
        {"order": 16, "source": "NCSB", "target": "FP_ANP", "relation": "barrier_status_for", "evidence_status": "documented", "note": "Lifecycle-stage-dependent deadlines (Construção/Produção/Abandono Permanente)."},
        {"order": 17, "source": "CRP_ANP", "target": "FP_ANP", "relation": "re_entry_starts_from", "evidence_status": "documented", "note": "1 day after re-entry start (BOP connection)."},
        {"order": 18, "source": "NCRP", "target": "CRP_ANP", "relation": "concludes", "evidence_status": "documented", "note": "10 days after re-entry conclusion."},
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(TARGET.read_text(encoding="utf-8"))
    classes = data.setdefault("classes", {})
    instances = data.setdefault("instances", {})

    # Track changes
    new_docs = []
    skipped_docs = []
    for cls in ANP_DOC_CLASSES:
        if cls["name"] in classes:
            skipped_docs.append(cls["name"])
        else:
            classes[cls["name"]] = cls
            new_docs.append(cls["name"])

    poco_added = False
    if POCO_CLASS["name"] not in classes:
        classes[POCO_CLASS["name"]] = POCO_CLASS
        poco_added = True

    lineage_added = False
    if OG_DOC_LINEAGE_ANP["id"] not in instances:
        instances[OG_DOC_LINEAGE_ANP["id"]] = OG_DOC_LINEAGE_ANP
        lineage_added = True

    print(f"Existing classes: {len(classes)} (was {len(classes) - len(new_docs) - (1 if poco_added else 0)})")
    print(f"New ANP-699 doc classes added: {len(new_docs)}")
    for n in new_docs:
        print(f"  + {n}")
    if skipped_docs:
        print("Skipped (already present):")
        for n in skipped_docs:
            print(f"  SKIP {n}")
    print(f"Poco class added: {poco_added}")
    print(f"OG_DOC_LINEAGE_ANP added: {lineage_added}")

    # Update meta counts
    if "meta" in data:
        data["meta"]["class_count"] = len(classes)
        data["meta"]["instance_count"] = len(instances)
        sources = data["meta"].setdefault("sources", [])
        if "Resolução ANP nº 699/2017" not in sources:
            sources.append("Resolução ANP nº 699/2017")

    if args.dry_run:
        print("--dry-run; not writing.")
        return 0

    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
