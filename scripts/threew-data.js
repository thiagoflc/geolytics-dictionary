/* Petrobras 3W v2.0.0 — entity-graph nodes, edges, taxonomies, and
   supplementary data for the GeoBrain knowledge graph.

   Source: https://github.com/petrobras/3W (CC-BY 4.0)
   DOI: 10.1016/j.petrol.2019.106223
   Authors: Vargas et al. (2019)

   This module exports semantic metadata derived from dataset.ini and enums.py.
   No Parquet instances are included. Merged into the build pipeline by
   scripts/generate.js, following the pattern of operacoes-geologicas-nodes.js.

   Mnemônico disciplinar: TW. Codes TW001–TW051.
     TW001–TW027  sensor/instrument nodes (27 variáveis 3W)
     TW028–TW040  Xmas-tree equipment nodes (13 new)
     TW041        ANM — Subsea Xmas-tree assembly wrapper
     TW042–TW051  operational event nodes (10 classes 3W)
*/

const TW_SRC = "Petrobras 3W v2.0.0";
const TW_DS = ["dataset-3w"];
const TW_LAYERS = ["layer4", "layer6"];

// ---------------------------------------------------------------------------
// Helper: build a full SKOS + bilingual sensor node
// ---------------------------------------------------------------------------
function sensor(
  id,
  tag,
  labelEn,
  unit,
  quantityKind,
  signalRole,
  measuredAt,
  definition,
  definitionEn,
  synonymsPt,
  synonymsEn,
  examples,
  module
) {
  return {
    id,
    label: tag,
    label_en: labelEn,
    type: "instrument",
    color: "#888780",
    size: 18,
    definition,
    definition_en_canonical: definitionEn,
    legal_source: TW_SRC,
    datasets: TW_DS,
    petrokgraph_uri: null,
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    geosciml_uri: null,
    owl_uri: `https://github.com/petrobras/3W#${tag}`,
    geocoverage: TW_LAYERS,
    synonyms_pt: synonymsPt,
    synonyms_en: synonymsEn,
    examples,
    glossary_id: null,
    extended_id: null,
    module,
    threew_tag: tag,
    threew_unit: unit,
    threew_quantity_kind: quantityKind,
    threew_signal_role: signalRole,
    threew_measured_at: measuredAt,
    skos_prefLabel: { "@pt": tag, "@en": labelEn },
    skos_altLabel: { "@pt": synonymsPt, "@en": synonymsEn },
    skos_definition: { "@pt": definition, "@en": definitionEn },
    skos_example: examples,
  };
}

// Helper: full equipment node
function equip(
  id,
  label,
  labelEn,
  subtype,
  osduType,
  definition,
  definitionEn,
  synonymsPt,
  synonymsEn,
  examples,
  module
) {
  return {
    id,
    label,
    label_en: labelEn,
    type: "equipment",
    color: "#C77B30",
    size: 20,
    definition,
    definition_en_canonical: definitionEn,
    legal_source: TW_SRC,
    datasets: TW_DS,
    petrokgraph_uri: null,
    osdu_kind: `opendes:osdu:reference-data--EquipmentType:${osduType}:1.0.0`,
    geosciml_uri: null,
    owl_uri: `https://github.com/petrobras/3W#${id.toUpperCase()}`,
    geocoverage: TW_LAYERS,
    synonyms_pt: synonymsPt,
    synonyms_en: synonymsEn,
    examples,
    glossary_id: null,
    extended_id: null,
    module,
    threew_equipment_subtype: subtype,
    skos_prefLabel: { "@pt": label, "@en": labelEn },
    skos_altLabel: { "@pt": synonymsPt, "@en": synonymsEn },
    skos_definition: { "@pt": definition, "@en": definitionEn },
    skos_example: examples,
  };
}

// Helper: full event node
function event(
  id,
  label,
  labelEn,
  tw_label,
  transient,
  window_,
  step,
  sigTags,
  eventClass,
  definition,
  definitionEn,
  synonymsPt,
  synonymsEn,
  examples,
  module
) {
  return {
    id,
    label,
    label_en: labelEn,
    type: "operational",
    subtype: "event",
    color: "#378ADD",
    size: 22,
    definition,
    definition_en_canonical: definitionEn,
    legal_source: TW_SRC,
    datasets: TW_DS,
    petrokgraph_uri: null,
    osdu_kind: null,
    geosciml_uri: null,
    owl_uri: `https://github.com/petrobras/3W#${id.toUpperCase()}`,
    geocoverage: TW_LAYERS,
    synonyms_pt: synonymsPt,
    synonyms_en: synonymsEn,
    examples,
    glossary_id: null,
    extended_id: null,
    module,
    threew_label: tw_label,
    threew_transient: transient,
    threew_transient_label: transient ? tw_label + 100 : null,
    threew_window: window_,
    threew_step: step,
    threew_signature_tags: sigTags,
    threew_event_class: eventClass,
    skos_prefLabel: { "@pt": label, "@en": labelEn },
    skos_altLabel: { "@pt": synonymsPt, "@en": synonymsEn },
    skos_definition: { "@pt": definition, "@en": definitionEn },
    skos_example: examples,
  };
}

// ===========================================================================
// SENSOR NODES — TW001–TW027
// ===========================================================================

export const THREEW_VARIABLES = [
  sensor(
    "sensor_aber_ckgl",
    "ABER-CKGL",
    "Gas-Lift Choke Opening",
    "%",
    "ValveOpening",
    "valve_opening",
    "glck",
    "Abertura do GLCK (gas-lift choke), variável 3W em percentual. Indica o grau de abertura da válvula de estrangulamento da linha de gas-lift.",
    "Opening percentage of the GLCK (gas-lift choke). 3W variable [%].",
    ["abertura GLCK", "abertura choke gas-lift"],
    ["GLCK opening", "gas-lift choke opening"],
    ["ABER-CKGL=0 indica GLCK fechado", "ABER-CKGL=100 indica GLCK totalmente aberto"],
    "data/threew.json#TW001"
  ),

  sensor(
    "sensor_aber_ckp",
    "ABER-CKP",
    "Production Choke Opening",
    "%",
    "ValveOpening",
    "valve_opening",
    "pck",
    "Abertura do PCK (production choke), variável 3W em percentual. Queda brusca de ABER-CKP pode indicar restrição rápida (classe 6) ou incrustação (classe 7).",
    "Opening percentage of the PCK (production choke). 3W variable [%]. Sudden drop can indicate quick restriction (class 6) or scaling (class 7).",
    ["abertura PCK", "abertura choke produção"],
    ["PCK opening", "production choke opening"],
    ["ABER-CKP caindo rapidamente indica classe 6 ou 7"],
    "data/threew.json#TW002"
  ),

  sensor(
    "sensor_estado_dhsv",
    "ESTADO-DHSV",
    "DHSV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "dhsv",
    "Estado da DHSV (válvula de segurança de subsuperfície): 0=fechada, 0.5=parcial, 1=aberta. Fechamento espúrio (classe 2) é detectado por queda abrupta de ESTADO-DHSV.",
    "State of the DHSV (downhole safety valve): 0=closed, 0.5=partial, 1=open. Spurious closure (class 2) is detected by an abrupt drop in ESTADO-DHSV.",
    ["estado DHSV", "estado válvula de segurança"],
    ["DHSV state", "safety valve state"],
    ["ESTADO-DHSV=0 confirma fechamento da DHSV"],
    "data/threew.json#TW003"
  ),

  sensor(
    "sensor_estado_m1",
    "ESTADO-M1",
    "PMV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "pmv",
    "Estado da PMV (production master valve / válvula mestra de produção): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the PMV (production master valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado PMV", "estado válvula mestra produção"],
    ["PMV state", "production master valve state"],
    [],
    "data/threew.json#TW004"
  ),

  sensor(
    "sensor_estado_m2",
    "ESTADO-M2",
    "AMV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "amv",
    "Estado da AMV (annulus master valve / válvula mestra de anular): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the AMV (annulus master valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado AMV", "estado válvula mestra anular"],
    ["AMV state", "annulus master valve state"],
    [],
    "data/threew.json#TW005"
  ),

  sensor(
    "sensor_estado_pxo",
    "ESTADO-PXO",
    "PXO Valve State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "pxo",
    "Estado da PXO (pig-crossover valve): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the PXO (pig-crossover valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado PXO", "estado válvula pig-crossover"],
    ["PXO state", "pig-crossover valve state"],
    [],
    "data/threew.json#TW006"
  ),

  sensor(
    "sensor_estado_sdv_gl",
    "ESTADO-SDV-GL",
    "Gas-Lift SDV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "sdv_gl",
    "Estado da SDV-GL (válvula de bloqueio de gas-lift): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the gas-lift SDV (shutdown valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado SDV-GL", "estado válvula bloqueio gas-lift"],
    ["SDV-GL state", "gas-lift shutdown valve state"],
    [],
    "data/threew.json#TW007"
  ),

  sensor(
    "sensor_estado_sdv_p",
    "ESTADO-SDV-P",
    "Production SDV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "sdv_p",
    "Estado da SDV-P (válvula de bloqueio de produção): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the production SDV (shutdown valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado SDV-P", "estado válvula bloqueio produção"],
    ["SDV-P state", "production shutdown valve state"],
    [],
    "data/threew.json#TW008"
  ),

  sensor(
    "sensor_estado_w1",
    "ESTADO-W1",
    "PWV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "pwv",
    "Estado da PWV (production wing valve / válvula asa de produção): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the PWV (production wing valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado PWV", "estado válvula asa produção"],
    ["PWV state", "production wing valve state"],
    [],
    "data/threew.json#TW009"
  ),

  sensor(
    "sensor_estado_w2",
    "ESTADO-W2",
    "AWV State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "awv",
    "Estado da AWV (annulus wing valve / válvula asa de anular): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the AWV (annulus wing valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado AWV", "estado válvula asa anular"],
    ["AWV state", "annulus wing valve state"],
    [],
    "data/threew.json#TW010"
  ),

  sensor(
    "sensor_estado_xo",
    "ESTADO-XO",
    "XO Valve State",
    "0/0.5/1",
    "ValveState",
    "valve_state",
    "xo",
    "Estado da XO (crossover valve): 0=fechada, 0.5=parcial, 1=aberta. Variável 3W.",
    "State of the XO (crossover valve): 0=closed, 0.5=partial, 1=open. 3W variable.",
    ["estado XO", "estado válvula crossover"],
    ["XO state", "crossover valve state"],
    [],
    "data/threew.json#TW011"
  ),

  sensor(
    "sensor_p_anular",
    "P-ANULAR",
    "Annulus Pressure",
    "Pa",
    "Pressure",
    "pressure_annulus",
    "poco",
    "Pressão no anular do poço [Pa]. Variável 3W. Monitorada para detectar vazamentos de válvulas e comunicação de pressão entre anular e coluna de produção.",
    "Pressure in the well annulus [Pa]. 3W variable. Monitored for valve leaks and pressure communication between annulus and tubing.",
    ["pressão anular", "pressão do anular"],
    ["annulus pressure", "casing-tubing annulus pressure"],
    ["P-ANULAR elevado pode indicar comunicação entre anular e coluna"],
    "data/threew.json#TW012"
  ),

  sensor(
    "sensor_p_jus_bs",
    "P-JUS-BS",
    "Service Pump Downstream Pressure",
    "Pa",
    "Pressure",
    "pressure_service",
    "sp_pump",
    "Pressão a jusante da SP (bomba de serviço) [Pa]. Variável 3W. Relevante para detecção de hidrato em linha de serviço (classe 9).",
    "Downstream pressure of the SP (service pump) [Pa]. 3W variable. Key for hydrate detection in service line (class 9).",
    ["pressão jusante bomba serviço", "P-JUS-BS"],
    ["service pump downstream pressure", "BS downstream pressure"],
    ["P-JUS-BS cai em caso de hidrato na linha de serviço"],
    "data/threew.json#TW013"
  ),

  sensor(
    "sensor_p_jus_ckgl",
    "P-JUS-CKGL",
    "Gas-Lift Choke Downstream Pressure",
    "Pa",
    "Pressure",
    "pressure_choke_down",
    "glck",
    "Pressão a jusante do GLCK (gas-lift choke) [Pa]. Variável 3W. Representa a pressão de injeção de gas-lift após o estrangulamento.",
    "Downstream pressure of the GLCK (gas-lift choke) [Pa]. 3W variable. Represents gas-lift injection pressure after the choke.",
    ["pressão jusante GLCK", "pressão jusante choke gas-lift"],
    ["GLCK downstream pressure", "gas-lift choke downstream pressure"],
    [],
    "data/threew.json#TW014"
  ),

  sensor(
    "sensor_p_jus_ckp",
    "P-JUS-CKP",
    "Production Choke Downstream Pressure",
    "Pa",
    "Pressure",
    "pressure_choke_down",
    "pck",
    "Pressão a jusante do PCK (production choke) [Pa]. Variável 3W. Junto com P-MON-CKP e ABER-CKP, caracteriza o diferencial de pressão no choke de produção.",
    "Downstream pressure of the PCK (production choke) [Pa]. 3W variable. Together with P-MON-CKP and ABER-CKP characterizes the choke differential pressure.",
    ["pressão jusante PCK", "pressão jusante choke produção"],
    ["PCK downstream pressure", "production choke downstream pressure"],
    ["Diferencial P-MON-CKP - P-JUS-CKP indica grau de restrição do choke"],
    "data/threew.json#TW015"
  ),

  sensor(
    "sensor_p_mon_ckgl",
    "P-MON-CKGL",
    "Gas-Lift Choke Upstream Pressure",
    "Pa",
    "Pressure",
    "pressure_choke_up",
    "glck",
    "Pressão a montante do GLCK (gas-lift choke) [Pa]. Variável 3W. Representa a pressão de entrada de gas-lift antes do estrangulamento.",
    "Upstream pressure of the GLCK (gas-lift choke) [Pa]. 3W variable.",
    ["pressão montante GLCK", "pressão montante choke gas-lift"],
    ["GLCK upstream pressure", "gas-lift choke upstream pressure"],
    [],
    "data/threew.json#TW016"
  ),

  sensor(
    "sensor_p_mon_ckp",
    "P-MON-CKP",
    "Production Choke Upstream Pressure",
    "Pa",
    "Pressure",
    "pressure_choke_up",
    "pck",
    "Pressão a montante do PCK (production choke) [Pa]. Variável 3W. Usada em conjunto com P-JUS-CKP para calcular diferencial de pressão no choke.",
    "Upstream pressure of the PCK (production choke) [Pa]. 3W variable.",
    ["pressão montante PCK", "pressão montante choke produção"],
    ["PCK upstream pressure", "production choke upstream pressure"],
    ["P-MON-CKP crescente com ABER-CKP constante pode indicar incrustação"],
    "data/threew.json#TW017"
  ),

  sensor(
    "sensor_p_mon_sdv_p",
    "P-MON-SDV-P",
    "Production SDV Upstream Pressure",
    "Pa",
    "Pressure",
    "pressure_choke_up",
    "sdv_p",
    "Pressão a montante da SDV-P (válvula de bloqueio de produção) [Pa]. Variável 3W.",
    "Upstream pressure of the production SDV (shutdown valve) [Pa]. 3W variable.",
    ["pressão montante SDV-P"],
    ["SDV-P upstream pressure", "production SDV upstream pressure"],
    [],
    "data/threew.json#TW018"
  ),

  sensor(
    "sensor_p_pdg",
    "P-PDG",
    "PDG Downhole Pressure",
    "Pa",
    "Pressure",
    "pressure_downhole",
    "pdg",
    "Pressão downhole medida pelo PDG (Permanent Downhole Gauge) [Pa]. Variável 3W fundamental para detectar golfadas severas (classe 3), instabilidade de fluxo (classe 4) e perda de produtividade (classe 5).",
    "Downhole pressure measured at the PDG (Permanent Downhole Gauge) [Pa]. 3W key variable for severe slugging (class 3), flow instability (class 4), and rapid productivity loss (class 5).",
    ["pressão downhole", "pressão PDG", "pressão de fundo"],
    ["downhole pressure", "PDG pressure", "bottomhole pressure"],
    [
      "P-PDG oscilante é assinatura de severe slugging",
      "P-PDG declinando rapidamente indica perda de produtividade",
    ],
    "data/threew.json#TW019"
  ),

  sensor(
    "sensor_pt_p",
    "PT-P",
    "Xmas-Tree Production Line Pressure",
    "Pa",
    "Pressure",
    "pressure_subsea_xt",
    "anm",
    "Pressão na linha de produção da ANM (árvore de natal subsea), a jusante da PWV [Pa]. Variável 3W.",
    "Subsea Xmas-tree pressure downstream of the PWV in the production line [Pa]. 3W variable.",
    ["pressão ANM linha produção", "pressão jusante PWV"],
    ["Xmas-tree production pressure", "subsea tree production line pressure"],
    [],
    "data/threew.json#TW020"
  ),

  sensor(
    "sensor_p_tpt",
    "P-TPT",
    "TPT Pressure",
    "Pa",
    "Pressure",
    "pressure_subsea_xt",
    "tpt",
    "Pressão medida pelo TPT (Temperature and Pressure Transducer) na ANM [Pa]. Variável 3W. Principal sensor de superfície do poço subsea para detecção de golfadas severas.",
    "Pressure at the TPT (Temperature and Pressure Transducer) on the subsea Xmas-tree [Pa]. 3W variable. Primary subsea wellhead sensor for severe slugging detection.",
    ["pressão TPT", "pressão transdutor ANM"],
    ["TPT pressure", "subsea tree pressure transducer pressure"],
    ["P-TPT oscilando em ciclos indica severe slugging"],
    "data/threew.json#TW021"
  ),

  sensor(
    "sensor_qbs",
    "QBS",
    "Service Pump Flow Rate",
    "m³/s",
    "VolumeRate",
    "flow_rate",
    "sp_pump",
    "Vazão na bomba de serviço (SP) [m³/s]. Variável 3W. Usada para detectar hidrato em linha de serviço (classe 9).",
    "Flow rate at the SP (service pump) [m³/s]. 3W variable. Used to detect hydrate in service line (class 9).",
    ["vazão bomba serviço", "QBS"],
    ["service pump flow rate", "BS flow"],
    ["QBS reduzindo junto com P-JUS-BS indica hidrato na linha de serviço"],
    "data/threew.json#TW022"
  ),

  sensor(
    "sensor_qgl",
    "QGL",
    "Gas-Lift Flow Rate",
    "m³/s",
    "VolumeRate",
    "flow_rate",
    "poco",
    "Vazão de injeção de gas-lift [m³/s]. Variável 3W. Queda abrupta de QGL pode indicar instabilidade de fluxo ou perda de produtividade.",
    "Gas-lift injection flow rate [m³/s]. 3W variable. Sudden drop may indicate flow instability or productivity loss.",
    ["vazão gas-lift", "QGL", "injeção gas-lift"],
    ["gas-lift flow rate", "GL injection rate"],
    ["QGL reduzindo rapidamente pode indicar classe 5 ou problema no compressor"],
    "data/threew.json#TW023"
  ),

  sensor(
    "sensor_t_jus_ckp",
    "T-JUS-CKP",
    "Production Choke Downstream Temperature",
    "°C",
    "Temperature",
    "temperature_choke",
    "pck",
    "Temperatura a jusante do PCK (production choke) [°C]. Variável 3W. Efeito Joule-Thomson causa queda de temperatura no estrangulamento; anomalia pode indicar hidrato.",
    "Downstream temperature of the PCK (production choke) [°C]. 3W variable. Joule-Thomson effect causes temperature drop; anomaly may indicate hydrate.",
    ["temperatura jusante PCK", "temperatura choke produção"],
    ["PCK downstream temperature", "production choke downstream temperature"],
    ["T-JUS-CKP muito baixa pode indicar formação de hidrato no choke"],
    "data/threew.json#TW024"
  ),

  sensor(
    "sensor_t_mon_ckp",
    "T-MON-CKP",
    "Production Choke Upstream Temperature",
    "°C",
    "Temperature",
    "temperature_choke",
    "pck",
    "Temperatura a montante do PCK (production choke) [°C]. Variável 3W. Usada em conjunto com T-JUS-CKP para monitorar diferencial de temperatura no choke.",
    "Upstream temperature of the PCK (production choke) [°C]. 3W variable.",
    ["temperatura montante PCK"],
    ["PCK upstream temperature", "production choke upstream temperature"],
    ["Diferencial T-MON-CKP - T-JUS-CKP indica severidade de expansão no choke"],
    "data/threew.json#TW025"
  ),

  sensor(
    "sensor_t_pdg",
    "T-PDG",
    "PDG Downhole Temperature",
    "°C",
    "Temperature",
    "temperature_downhole",
    "pdg",
    "Temperatura downhole medida pelo PDG (Permanent Downhole Gauge) [°C]. Variável 3W. Queda persistente pode indicar hidrato ou redução de fluxo.",
    "Downhole temperature measured at the PDG (Permanent Downhole Gauge) [°C]. 3W variable.",
    ["temperatura downhole", "temperatura PDG", "temperatura de fundo"],
    ["downhole temperature", "PDG temperature", "bottomhole temperature"],
    [
      "T-PDG declinando progressivamente em poço com gas-lift pode indicar hidrato na linha de produção",
    ],
    "data/threew.json#TW026"
  ),

  sensor(
    "sensor_t_tpt",
    "T-TPT",
    "TPT Temperature",
    "°C",
    "Temperature",
    "temperature_subsea_xt",
    "tpt",
    "Temperatura medida pelo TPT (Temperature and Pressure Transducer) na ANM [°C]. Variável 3W.",
    "Temperature at the TPT on the subsea Xmas-tree [°C]. 3W variable.",
    ["temperatura TPT", "temperatura transdutor ANM"],
    ["TPT temperature", "subsea tree temperature"],
    [],
    "data/threew.json#TW027"
  ),
];

// ===========================================================================
// EQUIPMENT — Xmas-tree components (TW028–TW041)
// ===========================================================================

export const THREEW_EQUIPMENT = [
  equip(
    "pmv",
    "PMV",
    "Production Master Valve",
    "production_master_valve",
    "ProductionMasterValve",
    "Válvula mestra de produção (Production Master Valve, M1) da ANM subsea. Controla o fluxo na linha principal de produção do poço. Parte da árvore de natal (ANM).",
    "Production master valve (M1) of the subsea Xmas-tree. Controls flow in the main production line. Part of the ANM assembly.",
    ["válvula mestra produção", "M1"],
    ["production master valve", "PMV", "M1"],
    ["PMV fechada indica shutdown do poço pelo lado de produção"],
    "data/threew.json#TW028"
  ),

  equip(
    "amv",
    "AMV",
    "Annulus Master Valve",
    "annulus_master_valve",
    "AnnulusMasterValve",
    "Válvula mestra de anular (Annulus Master Valve, M2) da ANM subsea. Controla o acesso ao espaço anular do poço. Parte da árvore de natal (ANM).",
    "Annulus master valve (M2) of the subsea Xmas-tree. Controls access to the well annulus. Part of the ANM assembly.",
    ["válvula mestra anular", "M2"],
    ["annulus master valve", "AMV", "M2"],
    [],
    "data/threew.json#TW029"
  ),

  equip(
    "pwv",
    "PWV",
    "Production Wing Valve",
    "production_wing_valve",
    "ProductionWingValve",
    "Válvula asa de produção (Production Wing Valve, W1) da ANM subsea. Válvula de isolamento da linha de produção. Parte da árvore de natal (ANM).",
    "Production wing valve (W1) of the subsea Xmas-tree. Isolation valve for the production flowline. Part of the ANM assembly.",
    ["válvula asa produção", "W1"],
    ["production wing valve", "PWV", "W1"],
    ["PWV fechada isola o poço da linha de produção"],
    "data/threew.json#TW030"
  ),

  equip(
    "awv",
    "AWV",
    "Annulus Wing Valve",
    "annulus_wing_valve",
    "AnnulusWingValve",
    "Válvula asa de anular (Annulus Wing Valve, W2) da ANM subsea. Válvula de isolamento da linha de anular. Parte da árvore de natal (ANM).",
    "Annulus wing valve (W2) of the subsea Xmas-tree. Isolation valve for the annulus flowline. Part of the ANM assembly.",
    ["válvula asa anular", "W2"],
    ["annulus wing valve", "AWV", "W2"],
    [],
    "data/threew.json#TW031"
  ),

  equip(
    "pxo",
    "PXO",
    "Pig-Crossover Valve",
    "pig_crossover_valve",
    "PigCrossoverValve",
    "Válvula de pig-crossover da ANM subsea. Permite desvio de linha para passagem de pig de limpeza. Parte da árvore de natal (ANM).",
    "Pig-crossover valve of the subsea Xmas-tree. Allows line bypass for pig launching/receiving. Part of the ANM assembly.",
    ["válvula pig-crossover", "PXO"],
    ["pig-crossover valve", "PXO"],
    [],
    "data/threew.json#TW032"
  ),

  equip(
    "xo",
    "XO",
    "Crossover Valve",
    "crossover_valve",
    "CrossoverValve",
    "Válvula crossover da ANM subsea. Permite comunicação entre linhas de produção e anular no leito marinho. Parte da árvore de natal (ANM).",
    "Crossover valve of the subsea Xmas-tree. Enables communication between production and annulus lines on the seabed. Part of the ANM assembly.",
    ["válvula crossover", "XO"],
    ["crossover valve", "XO"],
    [],
    "data/threew.json#TW033"
  ),

  equip(
    "sdv_p",
    "SDV-P",
    "Production Shutdown Valve",
    "production_shutdown_valve",
    "ProductionShutdownValve",
    "Válvula de bloqueio da linha de produção (Production Shutdown Valve) da ANM subsea. Actua como elemento de segurança em caso de ESD. Parte da árvore de natal (ANM).",
    "Production shutdown valve of the subsea Xmas-tree. Acts as a safety element in case of ESD. Part of the ANM assembly.",
    ["válvula bloqueio produção", "SDV-P", "válvula de shutdown produção"],
    ["production shutdown valve", "SDV-P"],
    ["SDV-P fecha automaticamente em caso de ESD ou alta pressão"],
    "data/threew.json#TW034"
  ),

  equip(
    "sdv_gl",
    "SDV-GL",
    "Gas-Lift Shutdown Valve",
    "gas_lift_shutdown_valve",
    "GasLiftShutdownValve",
    "Válvula de bloqueio da linha de gas-lift (Gas-Lift Shutdown Valve) da ANM subsea. Actua como elemento de segurança. Parte da árvore de natal (ANM).",
    "Gas-lift shutdown valve of the subsea Xmas-tree. Acts as a safety element for gas-lift injection line. Part of the ANM assembly.",
    ["válvula bloqueio gas-lift", "SDV-GL", "válvula shutdown gas-lift"],
    ["gas-lift shutdown valve", "SDV-GL"],
    [],
    "data/threew.json#TW035"
  ),

  equip(
    "glck",
    "GLCK",
    "Gas-Lift Choke",
    "gas_lift_choke",
    "GasLiftChoke",
    "Choke (estrangulador) da linha de gas-lift (GLCK) da ANM subsea. Controla a taxa de injeção de gas-lift no poço. Parte da árvore de natal (ANM).",
    "Gas-lift choke (GLCK) of the subsea Xmas-tree. Controls gas-lift injection rate into the well. Part of the ANM assembly.",
    ["choke gas-lift", "GLCK", "estrangulador gas-lift"],
    ["gas-lift choke", "GLCK"],
    ["ABER-CKGL e pressões P-MON-CKGL/P-JUS-CKGL monitoram o GLCK"],
    "data/threew.json#TW036"
  ),

  equip(
    "pck",
    "PCK",
    "Production Choke",
    "production_choke",
    "ProductionChoke",
    'Choke de produção (PCK) da ANM subsea. Controla a vazão da linha de produção do poço; principal ponto de incrustação (scaling, classe 7) e restrição rápida (classe 6). Parte da árvore de natal (ANM). ATENÇÃO: PCK no contexto 3W é o Production Choke — não confundir com "pilot-operated check valve" em contextos genéricos de tubulação.',
    'Production choke (PCK) of the subsea Xmas-tree. Controls production flowline rate; main point of scaling (class 7) and quick restriction (class 6). Part of the ANM assembly. NOTE: PCK in 3W context is the Production Choke — do not confuse with "pilot-operated check valve" in generic piping contexts.',
    ["choke produção", "PCK", "estrangulador produção"],
    ["production choke", "PCK"],
    ["Incrustação no PCK detectada por queda de ABER-CKP com diferencial crescente de pressão"],
    "data/threew.json#TW037"
  ),

  equip(
    "tpt",
    "TPT",
    "Temperature and Pressure Transducer",
    "temperature_pressure_transducer",
    "TemperaturePressureTransducer",
    "Transdutor de temperatura e pressão (TPT) instalado na ANM subsea. Fornece as variáveis P-TPT e T-TPT. Parte da árvore de natal (ANM).",
    "Temperature and Pressure Transducer (TPT) installed on the subsea Xmas-tree. Provides P-TPT and T-TPT variables. Part of the ANM assembly.",
    ["transdutor temperatura pressão", "TPT", "transdutor ANM"],
    ["temperature pressure transducer", "TPT"],
    [],
    "data/threew.json#TW038"
  ),

  equip(
    "pdg",
    "PDG",
    "Permanent Downhole Gauge",
    "permanent_downhole_gauge",
    "PermanentDownholeGauge",
    "Medidor permanente de fundo de poço (Permanent Downhole Gauge, PDG). Instalado na coluna de produção dentro do poço (downhole). Fornece P-PDG e T-PDG. Sensor crítico para detecção de golfadas severas e perda de produtividade.",
    "Permanent downhole gauge (PDG) installed in the production tubing inside the well. Provides P-PDG and T-PDG. Critical sensor for severe slugging and productivity loss detection.",
    ["medidor downhole", "PDG", "medidor permanente fundo"],
    ["permanent downhole gauge", "PDG", "downhole gauge"],
    ["PDG mede pressão e temperatura na coluna de produção em profundidade"],
    "data/threew.json#TW039"
  ),

  equip(
    "sp_pump",
    "SP",
    "Service Pump",
    "service_pump",
    "ServicePump",
    "Bomba de serviço (SP) usada em operações de intervenção ou injeção de fluidos no poço. Fornece as variáveis QBS (vazão) e P-JUS-BS (pressão a jusante). Relevante para detecção de hidrato em linha de serviço (classe 9).",
    "Service pump (SP) used for well intervention or fluid injection operations. Provides QBS (flow rate) and P-JUS-BS (downstream pressure). Relevant for hydrate in service line (class 9) detection.",
    ["bomba serviço", "SP"],
    ["service pump", "SP"],
    ["QBS + P-JUS-BS monitoram hidrato na linha de serviço"],
    "data/threew.json#TW040"
  ),

  equip(
    "anm",
    "ANM",
    "Subsea Xmas-Tree",
    "subsea_xmas_tree",
    "SubseaXmasTree",
    "Árvore de natal molhada (ANM) — conjunto de válvulas e equipamentos instalado no leito marinho no topo do poço offshore. Inclui PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK e TPT. Componente central da completação subsea.",
    "Subsea Xmas-tree (ANM) — assembly of valves and equipment installed on the seabed at the top of an offshore well. Includes PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK and TPT. Central component of subsea completion.",
    ["árvore de natal molhada", "ANM", "árvore de natal subsea", "Christmas tree subsea"],
    ["subsea Xmas-tree", "ANM", "wet Christmas tree", "subsea tree"],
    ["A ANM é o principal conjunto de controle de fluxo em poços offshore"],
    "data/threew.json#TW041"
  ),
];

// Enrichment patches for existing entity-graph nodes (merged in generate.js)
export const THREEW_EQUIPMENT_PATCHES = [
  {
    id: "dhsv",
    definition_en_canonical:
      "Downhole Safety Valve (DHSV / SSSV / SCSSV). Installed in the production tubing inside the well; closes automatically in case of catastrophic surface failure. 3W event class 2 (Spurious Closure of DHSV) involves this valve.",
    legal_source: TW_SRC,
    datasets: TW_DS,
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:DownholeSafetyValve:1.0.0",
    geocoverage: TW_LAYERS,
    synonyms_pt: ["válvula de segurança de subsuperfície", "SSSV", "SCSSV"],
    synonyms_en: [
      "downhole safety valve",
      "subsurface safety valve",
      "surface-controlled subsurface safety valve",
      "SSSV",
      "SCSSV",
    ],
    examples: [
      "DHSV fecha automaticamente quando a pressão de controle hidráulico cai",
      "Fechamento espúrio da DHSV (classe 2 do 3W) causa queda de P-PDG",
    ],
    threew_equipment_subtype: "safety_valve",
    threew_failure_modes: ["spurious_closure", "failure_to_close", "seal_leak"],
    threew_monitored_by: ["sensor_estado_dhsv", "sensor_p_pdg"],
  },
];

// ===========================================================================
// EVENT NODES — TW042–TW051
// ===========================================================================

export const THREEW_EVENTS = [
  event(
    "event_normal",
    "Operação Normal",
    "Normal Operation",
    0,
    false,
    null,
    null,
    [],
    "normal",
    "Estado de referência do poço: produção estável, todas as variáveis dentro da faixa operacional nominal. Rótulo 3W classe 0.",
    "Well reference state: stable production, all variables within nominal operating range. 3W label class 0.",
    ["operação normal", "estado normal"],
    ["normal operation", "normal state"],
    ["Classe 0 é o baseline para treinamento de modelos de detecção de anomalias"],
    "data/threew.json#TW042"
  ),

  event(
    "event_bsw_increase",
    "Aumento Abrupto de BSW",
    "Abrupt Increase of BSW",
    1,
    true,
    null,
    null,
    ["sensor_qbs", "sensor_qgl", "sensor_p_pdg"],
    "fluid_property_change",
    "Aumento súbito do BSW (Basic Sediment and Water — fração de água e sedimentos na produção). Indica influxo de água de formação ou quebra de barreira de óleo/água. Rótulo 3W classe 1 (transiente: 101).",
    "Sudden increase in BSW (Basic Sediment and Water fraction in production). Indicates formation water influx or oil/water barrier breakthrough. 3W label class 1 (transient: 101).",
    ["aumento BSW", "surgência de água", "irrupção de água"],
    ["BSW increase", "water breakthrough", "water influx"],
    ["BSW abrupto indica comunicação com aquífero ou falha de barreira"],
    "data/threew.json#TW043"
  ),

  event(
    "event_spurious_dhsv",
    "Fechamento Espúrio de DHSV",
    "Spurious Closure of DHSV",
    2,
    true,
    180,
    15,
    ["sensor_estado_dhsv", "sensor_p_pdg", "sensor_p_tpt"],
    "safety_event",
    "Fechamento não-intencional da DHSV (válvula de segurança de subsuperfície) sem causa operacional justificada. Causa queda abrupta de P-PDG e P-TPT. Rótulo 3W classe 2 (transiente: 102). Janela de análise: 180 s, passo: 15 s.",
    "Unintentional closure of the DHSV (downhole safety valve) without justified operational cause. Causes abrupt drop in P-PDG and P-TPT. 3W label class 2 (transient: 102). Analysis window: 180 s, step: 15 s.",
    ["fechamento espúrio DHSV", "fechamento não-intencional DHSV"],
    ["spurious DHSV closure", "unintended DHSV closure"],
    ["ESTADO-DHSV=0 com queda de P-PDG confirma fechamento espúrio"],
    "data/threew.json#TW044"
  ),

  event(
    "event_severe_slugging",
    "Golfadas Severas",
    "Severe Slugging",
    3,
    false,
    null,
    null,
    ["sensor_p_tpt", "sensor_p_pdg", "sensor_qgl"],
    "flow_regime",
    "Padrão de fluxo bifásico instável caracterizado por golfadas longas de líquido alternadas com bolsões de gás na linha de produção riser. Causa oscilações cíclicas em P-TPT e P-PDG. Rótulo 3W classe 3 (sem transiente).",
    "Unstable two-phase flow regime characterized by long liquid slugs alternating with gas pockets in the production riser. Causes cyclic oscillations in P-TPT and P-PDG. 3W label class 3 (no transient).",
    ["golfadas severas", "slugging severo", "padrão de golfadas"],
    ["severe slugging", "riser slugging", "terrain slugging"],
    [
      "Ciclo de golfada severa: bloqueio de gás → acúmulo de líquido → irrupção → blow-out",
      "P-TPT e P-PDG oscilatórios são assinatura de severe slugging",
    ],
    "data/threew.json#TW045"
  ),

  event(
    "event_flow_instability",
    "Instabilidade de Fluxo",
    "Flow Instability",
    4,
    false,
    null,
    null,
    ["sensor_p_tpt", "sensor_p_pdg", "sensor_qgl"],
    "flow_regime",
    "Instabilidade de fluxo multifásico no poço, com oscilações irregulares de pressão e vazão. Diferencia-se de golfadas severas por padrão menos periódico. Rótulo 3W classe 4 (sem transiente).",
    "Multiphase flow instability in the well with irregular oscillations of pressure and flow rate. Differs from severe slugging by a less periodic pattern. 3W label class 4 (no transient).",
    ["instabilidade de fluxo", "fluxo instável", "oscilação de fluxo"],
    ["flow instability", "flow oscillation", "unstable flow"],
    ["Instabilidade de fluxo pode anteceder golfadas severas"],
    "data/threew.json#TW046"
  ),

  event(
    "event_rapid_prod_loss",
    "Perda Rápida de Produtividade",
    "Rapid Productivity Loss",
    5,
    true,
    null,
    null,
    ["sensor_p_pdg", "sensor_p_tpt", "sensor_qgl"],
    "productivity_event",
    "Queda rápida e persistente da produtividade do poço, indicada por redução de P-PDG e QGL sem ação operacional. Pode ser causada por dano à formação, incrustação de fundo ou mudança na permeabilidade efetiva. Rótulo 3W classe 5 (transiente: 105).",
    "Rapid and persistent decline in well productivity indicated by reduction in P-PDG and QGL without operational intervention. May be caused by formation damage, downhole scaling, or effective permeability change. 3W label class 5 (transient: 105).",
    ["perda produtividade", "declínio rápido", "queda de produção"],
    ["rapid productivity loss", "productivity decline", "production drop"],
    ["P-PDG declining faster than expected pode indicar skin damage"],
    "data/threew.json#TW047"
  ),

  event(
    "event_quick_pck_restriction",
    "Restrição Rápida no PCK",
    "Quick Restriction in PCK",
    6,
    true,
    null,
    null,
    ["sensor_aber_ckp", "sensor_p_mon_ckp", "sensor_p_jus_ckp"],
    "choke_anomaly",
    "Redução rápida e abrupta da abertura do PCK (production choke) ou da seção de passagem, causando aumento do diferencial de pressão. Pode ser causada por objeto sólido, wax ou hidrato parcial. Rótulo 3W classe 6 (transiente: 106).",
    "Rapid and abrupt reduction in PCK (production choke) opening or flow section, causing increased differential pressure. May be caused by a solid object, wax, or partial hydrate. 3W label class 6 (transient: 106).",
    ["restrição rápida PCK", "obstrução rápida choke"],
    ["quick PCK restriction", "rapid choke restriction", "choke obstruction"],
    ["ABER-CKP caindo abruptamente com diferencial de pressão crescente é assinatura de classe 6"],
    "data/threew.json#TW048"
  ),

  event(
    "event_scaling_pck",
    "Incrustação no PCK",
    "Scaling in PCK",
    7,
    true,
    null,
    null,
    ["sensor_aber_ckp", "sensor_p_mon_ckp", "sensor_p_jus_ckp", "sensor_t_mon_ckp"],
    "choke_anomaly",
    "Deposição progressiva de incrustações minerais (carbonato de cálcio, barita, etc.) no PCK (production choke), causando redução gradual da abertura efetiva. Distingue-se de restrição rápida pelo ritmo de crescimento do diferencial de pressão. Rótulo 3W classe 7 (transiente: 107).",
    "Progressive deposition of mineral scale (calcium carbonate, barium sulfate, etc.) in the PCK (production choke), causing gradual reduction of effective opening. Distinguished from quick restriction by the rate of differential pressure growth. 3W label class 7 (transient: 107).",
    ["incrustação PCK", "scaling choke", "deposição mineral choke"],
    ["PCK scaling", "choke scaling", "mineral deposition in choke"],
    ["T-MON-CKP elevada com diferencial crescente ao longo do tempo é assinatura de scaling"],
    "data/threew.json#TW049"
  ),

  event(
    "event_hydrate_production",
    "Hidrato na Linha de Produção",
    "Hydrate in Production Line",
    8,
    true,
    null,
    null,
    ["sensor_p_pdg", "sensor_p_tpt", "sensor_qgl", "sensor_t_pdg"],
    "flow_assurance",
    "Formação de hidrato de gás na linha de produção subsea, causando obstrução parcial ou total. Ocorre em condições de alta pressão e baixa temperatura. Detectado por queda de P-PDG, P-TPT e QGL com T-PDG decrescente. Rótulo 3W classe 8 (transiente: 108).",
    "Gas hydrate formation in the subsea production line, causing partial or total blockage. Occurs under high pressure and low temperature conditions. Detected by drops in P-PDG, P-TPT, and QGL with decreasing T-PDG. 3W label class 8 (transient: 108).",
    ["hidrato linha produção", "obstrução por hidrato", "plug de hidrato produção"],
    ["production line hydrate", "hydrate plug in production", "gas hydrate blockage"],
    ["Queda simultânea de P-PDG + T-PDG + QGL indica hidrato na linha de produção"],
    "data/threew.json#TW050"
  ),

  event(
    "event_hydrate_service",
    "Hidrato na Linha de Serviço",
    "Hydrate in Service Line",
    9,
    true,
    null,
    null,
    ["sensor_p_jus_bs", "sensor_qbs", "sensor_t_jus_ckp"],
    "flow_assurance",
    "Formação de hidrato de gás na linha de serviço (injeção de inibidor ou fluido de intervenção) subsea. Detectado por queda de P-JUS-BS e QBS. Rótulo 3W classe 9 (transiente: 109).",
    "Gas hydrate formation in the subsea service line (inhibitor injection or intervention fluid). Detected by drops in P-JUS-BS and QBS. 3W label class 9 (transient: 109).",
    ["hidrato linha serviço", "obstrução por hidrato serviço", "plug de hidrato serviço"],
    ["service line hydrate", "hydrate in service line", "intervention line hydrate"],
    ["QBS reduzindo com P-JUS-BS crescente indica obstrução por hidrato na linha de serviço"],
    "data/threew.json#TW051"
  ),
];

// ===========================================================================
// EDGES — sensor→equipment, equipment→anm/well, event→sensor, event→equipment
// ===========================================================================

export const THREEW_EDGES = [
  // --- Sensors measured_at their instruments ---
  {
    source: "sensor_aber_ckgl",
    target: "glck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_aber_ckp",
    target: "pck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_dhsv",
    target: "dhsv",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_m1",
    target: "pmv",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_m2",
    target: "amv",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_pxo",
    target: "pxo",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_sdv_gl",
    target: "sdv_gl",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_sdv_p",
    target: "sdv_p",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_w1",
    target: "pwv",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_w2",
    target: "awv",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_estado_xo",
    target: "xo",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_anular",
    target: "poco",
    relation: "measured_in",
    relation_label: "medido em",
    relation_label_en: "measured in",
    style: "solid",
  },
  {
    source: "sensor_p_jus_bs",
    target: "sp_pump",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_jus_ckgl",
    target: "glck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_jus_ckp",
    target: "pck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_mon_ckgl",
    target: "glck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_mon_ckp",
    target: "pck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_mon_sdv_p",
    target: "sdv_p",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_pdg",
    target: "pdg",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_pt_p",
    target: "anm",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_p_tpt",
    target: "tpt",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_qbs",
    target: "sp_pump",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_qgl",
    target: "poco",
    relation: "measured_in",
    relation_label: "medido em",
    relation_label_en: "measured in",
    style: "solid",
  },
  {
    source: "sensor_t_jus_ckp",
    target: "pck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_t_mon_ckp",
    target: "pck",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_t_pdg",
    target: "pdg",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },
  {
    source: "sensor_t_tpt",
    target: "tpt",
    relation: "measured_at",
    relation_label: "medido em",
    relation_label_en: "measured at",
    style: "solid",
  },

  // --- Sensors located_in well ---
  ...[
    "sensor_aber_ckgl",
    "sensor_aber_ckp",
    "sensor_estado_dhsv",
    "sensor_estado_m1",
    "sensor_estado_m2",
    "sensor_estado_pxo",
    "sensor_estado_sdv_gl",
    "sensor_estado_sdv_p",
    "sensor_estado_w1",
    "sensor_estado_w2",
    "sensor_estado_xo",
    "sensor_p_jus_bs",
    "sensor_p_jus_ckgl",
    "sensor_p_jus_ckp",
    "sensor_p_mon_ckgl",
    "sensor_p_mon_ckp",
    "sensor_p_mon_sdv_p",
    "sensor_p_pdg",
    "sensor_pt_p",
    "sensor_p_tpt",
    "sensor_qbs",
    "sensor_t_jus_ckp",
    "sensor_t_mon_ckp",
    "sensor_t_pdg",
    "sensor_t_tpt",
  ].map((s) => ({
    source: s,
    target: "poco",
    relation: "located_in",
    relation_label: "localizado em",
    relation_label_en: "located in",
    style: "dashed",
  })),

  // --- Equipment part_of ANM (subsea components) ---
  ...["pmv", "amv", "pwv", "awv", "pxo", "xo", "sdv_p", "sdv_gl", "glck", "pck", "tpt"].map(
    (e) => ({
      source: e,
      target: "anm",
      relation: "part_of",
      relation_label: "parte de",
      relation_label_en: "part of",
      style: "solid",
    })
  ),

  // --- ANM and downhole equipment connected to well ---
  {
    source: "anm",
    target: "poco",
    relation: "part_of",
    relation_label: "parte de",
    relation_label_en: "part of",
    style: "solid",
  },
  {
    source: "dhsv",
    target: "poco",
    relation: "installed_in",
    relation_label: "instalado em",
    relation_label_en: "installed in",
    style: "solid",
  },
  {
    source: "pdg",
    target: "poco",
    relation: "installed_in",
    relation_label: "instalado em",
    relation_label_en: "installed in",
    style: "solid",
  },
  {
    source: "sp_pump",
    target: "poco",
    relation: "connects",
    relation_label: "conectado a",
    relation_label_en: "connects to",
    style: "dashed",
  },

  // --- Events detected_via signature sensors ---
  // Event 1: BSW increase
  {
    source: "event_bsw_increase",
    target: "sensor_qbs",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_bsw_increase",
    target: "sensor_qgl",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_bsw_increase",
    target: "sensor_p_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  // Event 2: spurious DHSV
  {
    source: "event_spurious_dhsv",
    target: "sensor_estado_dhsv",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_spurious_dhsv",
    target: "sensor_p_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_spurious_dhsv",
    target: "sensor_p_tpt",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_spurious_dhsv",
    target: "dhsv",
    relation: "involves_equipment",
    relation_label: "envolve equipamento",
    relation_label_en: "involves equipment",
    style: "dashed",
  },
  // Event 3: severe slugging
  {
    source: "event_severe_slugging",
    target: "sensor_p_tpt",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_severe_slugging",
    target: "sensor_p_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_severe_slugging",
    target: "sensor_qgl",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  // Event 4: flow instability
  {
    source: "event_flow_instability",
    target: "sensor_p_tpt",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_flow_instability",
    target: "sensor_p_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_flow_instability",
    target: "sensor_qgl",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  // Event 5: rapid productivity loss
  {
    source: "event_rapid_prod_loss",
    target: "sensor_p_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_rapid_prod_loss",
    target: "sensor_p_tpt",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_rapid_prod_loss",
    target: "sensor_qgl",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  // Event 6: quick PCK restriction
  {
    source: "event_quick_pck_restriction",
    target: "sensor_aber_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_quick_pck_restriction",
    target: "sensor_p_mon_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_quick_pck_restriction",
    target: "sensor_p_jus_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_quick_pck_restriction",
    target: "pck",
    relation: "involves_equipment",
    relation_label: "envolve equipamento",
    relation_label_en: "involves equipment",
    style: "dashed",
  },
  // Event 7: scaling PCK
  {
    source: "event_scaling_pck",
    target: "sensor_aber_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_scaling_pck",
    target: "sensor_p_mon_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_scaling_pck",
    target: "sensor_p_jus_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_scaling_pck",
    target: "sensor_t_mon_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_scaling_pck",
    target: "pck",
    relation: "involves_equipment",
    relation_label: "envolve equipamento",
    relation_label_en: "involves equipment",
    style: "dashed",
  },
  // Event 8: hydrate production line
  {
    source: "event_hydrate_production",
    target: "sensor_p_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_hydrate_production",
    target: "sensor_p_tpt",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_hydrate_production",
    target: "sensor_qgl",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_hydrate_production",
    target: "sensor_t_pdg",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  // Event 9: hydrate service line
  {
    source: "event_hydrate_service",
    target: "sensor_p_jus_bs",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_hydrate_service",
    target: "sensor_qbs",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },
  {
    source: "event_hydrate_service",
    target: "sensor_t_jus_ckp",
    relation: "detected_via",
    relation_label: "detectado via",
    relation_label_en: "detected via",
    style: "dashed",
  },

  // --- All events occur_in well ---
  ...[
    "event_normal",
    "event_bsw_increase",
    "event_spurious_dhsv",
    "event_severe_slugging",
    "event_flow_instability",
    "event_rapid_prod_loss",
    "event_quick_pck_restriction",
    "event_scaling_pck",
    "event_hydrate_production",
    "event_hydrate_service",
  ].map((e) => ({
    source: e,
    target: "poco",
    relation: "occurs_in",
    relation_label: "ocorre em",
    relation_label_en: "occurs in",
    style: "dashed",
  })),

  // --- Flow-assurance events also involve completacao ---
  {
    source: "event_hydrate_production",
    target: "anm",
    relation: "involves_equipment",
    relation_label: "envolve equipamento",
    relation_label_en: "involves equipment",
    style: "dashed",
  },
  {
    source: "event_hydrate_service",
    target: "sp_pump",
    relation: "involves_equipment",
    relation_label: "envolve equipamento",
    relation_label_en: "involves equipment",
    style: "dashed",
  },
];

// ===========================================================================
// TAXONOMIES — 4 new entries merged into TAXONOMIES object
// ===========================================================================

export const THREEW_TAXONOMIES = {
  operational_event_class_3w: {
    label: "Classe de Evento Operacional (3W)",
    label_en: "Operational Event Class (3W)",
    description:
      "Enumeração canônica das 10 classes de evento do dataset Petrobras 3W v2.0.0. Rótulos transientes = base + 100.",
    rag_alert:
      "Não confundir com ROA (Registro de Ocorrência Anormal, documento ANP). Os rótulos 3W são para modelos de ML, não documentos regulatórios.",
    source: TW_SRC,
    values: {
      0: { label: "Normal", transient: false, transient_label: null },
      1: { label: "Abrupt Increase of BSW", transient: true, transient_label: 101 },
      2: {
        label: "Spurious Closure of DHSV",
        transient: true,
        transient_label: 102,
        window: 180,
        step: 15,
      },
      3: { label: "Severe Slugging", transient: false, transient_label: null },
      4: { label: "Flow Instability", transient: false, transient_label: null },
      5: { label: "Rapid Productivity Loss", transient: true, transient_label: 105 },
      6: { label: "Quick Restriction in PCK", transient: true, transient_label: 106 },
      7: { label: "Scaling in PCK", transient: true, transient_label: 107 },
      8: { label: "Hydrate in Production Line", transient: true, transient_label: 108 },
      9: { label: "Hydrate in Service Line", transient: true, transient_label: 109 },
    },
  },
  instance_origin_3w: {
    label: "Origem da Instância (3W)",
    label_en: "Instance Origin (3W)",
    description:
      "Tipo de origem das instâncias do dataset 3W: REAL (poços reais, prefixo WELL_), SIMULATED (simuladas), DRAWN (manuais).",
    source: TW_SRC,
    values: {
      real: { prefix: "WELL_", description: "Série temporal de poço real Petrobras" },
      simulated: {
        prefix: "SIMULATED_",
        description: "Série temporal simulada com modelo de poço",
      },
      drawn: { prefix: "DRAWN_", description: "Série temporal construída manualmente" },
    },
  },
  event_phase_3w: {
    label: "Fase de Rótulo (3W)",
    label_en: "Event Label Phase (3W)",
    description:
      "Indicador de fase transiente/estacionário. TRANSIENT_OFFSET=100: rótulo transiente = rótulo base + 100. Classes 3 e 4 não possuem transiente.",
    source: TW_SRC,
    values: {
      steady: { offset: 0, description: "Estado estacionário ou normal" },
      transient: {
        offset: 100,
        description: "Fase inicial do evento (onset), antes de atingir estado estacionário anormal",
      },
    },
  },
  valve_state_3w: {
    label: "Estado de Válvula (3W)",
    label_en: "Valve State (3W)",
    description:
      "Valores canônicos para variáveis ESTADO-* do dataset 3W. Valores fora de {0, 0.5, 1} são inválidos.",
    source: TW_SRC,
    values: {
      0: { label: "Fechada", label_en: "Closed" },
      0.5: { label: "Parcial", label_en: "Partial" },
      1: { label: "Aberta", label_en: "Open" },
    },
  },
};

// ===========================================================================
// DATASET REGISTRY ENTRY
// ===========================================================================

export const THREEW_DATASET = {
  id: "dataset-3w",
  titulo: "3W Dataset v2.0.0 — Eventos Indesejáveis em Poços Offshore",
  descricao:
    "Primeiro dataset público realista com eventos raros e indesejáveis em poços de petróleo offshore. 1798 instâncias (922 reais, 878 simuladas/manuais), 10 classes de evento, 27 variáveis de sensores. Referência: DOI 10.1016/j.petrol.2019.106223.",
  fonte: "Petrobras / petrobras/3W (GitHub, CC-BY 4.0)",
  licenca: "CC-BY 4.0",
  doi: "10.1016/j.petrol.2019.106223",
  formato: "Parquet (PyArrow + Brotli)",
  frequencia: "snapshot por release (atual: 2.0.0, 2024-07-25)",
  url: "https://github.com/petrobras/3W",
  contato: "https://github.com/petrobras/3W/issues",
  colunas: [
    { nome: "timestamp", descricao: "Instante da observação", tipo: "DATETIME" },
    { nome: "ABER-CKGL", descricao: "Abertura do GLCK (gas-lift choke) [%]", tipo: "FLOAT" },
    { nome: "ABER-CKP", descricao: "Abertura do PCK (production choke) [%]", tipo: "FLOAT" },
    {
      nome: "ESTADO-DHSV",
      descricao: "Estado da DHSV (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-M1",
      descricao: "Estado da PMV (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-M2",
      descricao: "Estado da AMV (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-PXO",
      descricao: "Estado da PXO (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-SDV-GL",
      descricao: "Estado da SDV-GL (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-SDV-P",
      descricao: "Estado da SDV-P (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-W1",
      descricao: "Estado da PWV (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-W2",
      descricao: "Estado da AWV (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    {
      nome: "ESTADO-XO",
      descricao: "Estado da XO (0=fechada, 0.5=parcial, 1=aberta)",
      tipo: "FLOAT",
    },
    { nome: "P-ANULAR", descricao: "Pressão no anular do poço [Pa]", tipo: "FLOAT" },
    { nome: "P-JUS-BS", descricao: "Pressão a jusante da bomba de serviço [Pa]", tipo: "FLOAT" },
    { nome: "P-JUS-CKGL", descricao: "Pressão a jusante do GLCK [Pa]", tipo: "FLOAT" },
    { nome: "P-JUS-CKP", descricao: "Pressão a jusante do PCK [Pa]", tipo: "FLOAT" },
    { nome: "P-MON-CKGL", descricao: "Pressão a montante do GLCK [Pa]", tipo: "FLOAT" },
    { nome: "P-MON-CKP", descricao: "Pressão a montante do PCK [Pa]", tipo: "FLOAT" },
    { nome: "P-MON-SDV-P", descricao: "Pressão a montante da SDV-P [Pa]", tipo: "FLOAT" },
    { nome: "P-PDG", descricao: "Pressão downhole PDG [Pa]", tipo: "FLOAT" },
    { nome: "PT-P", descricao: "Pressão ANM linha produção [Pa]", tipo: "FLOAT" },
    { nome: "P-TPT", descricao: "Pressão no TPT [Pa]", tipo: "FLOAT" },
    { nome: "QBS", descricao: "Vazão bomba de serviço [m³/s]", tipo: "FLOAT" },
    { nome: "QGL", descricao: "Vazão de injeção de gas-lift [m³/s]", tipo: "FLOAT" },
    { nome: "T-JUS-CKP", descricao: "Temperatura a jusante do PCK [°C]", tipo: "FLOAT" },
    { nome: "T-MON-CKP", descricao: "Temperatura a montante do PCK [°C]", tipo: "FLOAT" },
    { nome: "T-PDG", descricao: "Temperatura downhole PDG [°C]", tipo: "FLOAT" },
    { nome: "T-TPT", descricao: "Temperatura no TPT [°C]", tipo: "FLOAT" },
    {
      nome: "class",
      descricao: "Rótulo da observação (0–9 estacionário, 101–109 transiente)",
      tipo: "INTEGER",
    },
    { nome: "state", descricao: "Status operacional do poço (3W interno)", tipo: "INTEGER" },
  ],
};

// ===========================================================================
// GLOSSARY — 1 entry per event + ANM
// ===========================================================================

export const THREEW_GLOSSARY = []; // Events are in entity-graph; glossary enrichment deferred.

// ===========================================================================
// ACRONYM PATCHES — add linked_entity_id + threew_role to existing entries
// ===========================================================================

export const THREEW_ACRONYM_LINKS = [
  { sigla: "BSW", linked_entity_id: "event_bsw_increase", threew_role: "fluid_property" },
  { sigla: "DHSV", linked_entity_id: "dhsv", threew_role: "valve" },
  { sigla: "PMV", linked_entity_id: "pmv", threew_role: "valve" },
  { sigla: "SDV", linked_entity_id: "sdv_p", threew_role: "valve" },
  { sigla: "TPT", linked_entity_id: "tpt", threew_role: "transducer" },
  { sigla: "PDG", linked_entity_id: "pdg", threew_role: "gauge" },
  { sigla: "PCK", linked_entity_id: "pck", threew_role: "valve" },
  { sigla: "ANM", linked_entity_id: "anm", threew_role: "assembly" },
];

// ===========================================================================
// RAG CORPUS CHUNKS — 1 per event class, bilingual, with DOI
// ===========================================================================

export const THREEW_RAG_CHUNKS = [
  {
    id: "threew_event_0_normal",
    type: "threew_event",
    text: "Classe 3W 0 — Operação Normal (Normal Operation): Estado de referência do poço com produção estável. Todas as 27 variáveis de sensores dentro da faixa operacional nominal. Rótulo base=0; sem transiente. Fonte: Petrobras 3W v2.0.0, DOI 10.1016/j.petrol.2019.106223.",
    metadata: {
      threew_label: 0,
      transient: false,
      entity_id: "event_normal",
      event_class: "normal",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_1_bsw",
    type: "threew_event",
    text: "Classe 3W 1 — Aumento Abrupto de BSW (Abrupt Increase of BSW): Influxo súbito de água de formação causando aumento do BSW. Assinatura: QGL, QBS e P-PDG alterados. Rótulo base=1, transiente=101. Entidade: event_bsw_increase. Atenção: BSW como propriedade de fluido ≠ BSW como evento 3W. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 1,
      transient: true,
      transient_label: 101,
      entity_id: "event_bsw_increase",
      event_class: "fluid_property_change",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_2_dhsv",
    type: "threew_event",
    text: "Classe 3W 2 — Fechamento Espúrio de DHSV (Spurious Closure of DHSV): Fechamento não-intencional da válvula de segurança de subsuperfície (DHSV). Assinatura: ESTADO-DHSV cai para 0, P-PDG e P-TPT caem abruptamente. Janela de análise: 180 s, passo: 15 s. Rótulo base=2, transiente=102. Entidade: event_spurious_dhsv. Equipamento envolvido: dhsv. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 2,
      transient: true,
      transient_label: 102,
      entity_id: "event_spurious_dhsv",
      event_class: "safety_event",
      source: TW_SRC,
      window: 180,
      step: 15,
    },
  },
  {
    id: "threew_event_3_severe_slugging",
    type: "threew_event",
    text: "Classe 3W 3 — Golfadas Severas (Severe Slugging): Instabilidade de fluxo bifásico no riser com golfadas longas de líquido. Assinatura: oscilações cíclicas em P-TPT e P-PDG, QGL variável. Rótulo base=3, SEM transiente (classes 3 e 4 não têm variante transiente). Entidade: event_severe_slugging. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 3,
      transient: false,
      entity_id: "event_severe_slugging",
      event_class: "flow_regime",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_4_flow_instability",
    type: "threew_event",
    text: "Classe 3W 4 — Instabilidade de Fluxo (Flow Instability): Oscilações irregulares de pressão e vazão no poço. Distingue-se de golfadas severas (classe 3) pelo padrão menos periódico. Assinatura: P-TPT, P-PDG e QGL oscilatórios. Rótulo base=4, SEM transiente. Entidade: event_flow_instability. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 4,
      transient: false,
      entity_id: "event_flow_instability",
      event_class: "flow_regime",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_5_rapid_prod_loss",
    type: "threew_event",
    text: "Classe 3W 5 — Perda Rápida de Produtividade (Rapid Productivity Loss): Queda persistente de P-PDG e QGL sem ação operacional. Causas: dano à formação, incrustação downhole. Rótulo base=5, transiente=105. Entidade: event_rapid_prod_loss. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 5,
      transient: true,
      transient_label: 105,
      entity_id: "event_rapid_prod_loss",
      event_class: "productivity_event",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_6_quick_pck",
    type: "threew_event",
    text: "Classe 3W 6 — Restrição Rápida no PCK (Quick Restriction in PCK): Redução abrupta da abertura do production choke (PCK). Assinatura: ABER-CKP cai abruptamente, diferencial P-MON-CKP - P-JUS-CKP cresce. Equipamento: pck. Rótulo base=6, transiente=106. Entidade: event_quick_pck_restriction. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 6,
      transient: true,
      transient_label: 106,
      entity_id: "event_quick_pck_restriction",
      event_class: "choke_anomaly",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_7_scaling_pck",
    type: "threew_event",
    text: "Classe 3W 7 — Incrustação no PCK (Scaling in PCK): Deposição progressiva de mineral no production choke. Assinatura: ABER-CKP decresce lentamente, diferencial de pressão e T-MON-CKP aumentam gradualmente. Distingue-se da classe 6 pelo ritmo gradual. Equipamento: pck. Rótulo base=7, transiente=107. Entidade: event_scaling_pck. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 7,
      transient: true,
      transient_label: 107,
      entity_id: "event_scaling_pck",
      event_class: "choke_anomaly",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_8_hydrate_prod",
    type: "threew_event",
    text: "Classe 3W 8 — Hidrato na Linha de Produção (Hydrate in Production Line): Formação de hidrato de gás obstaculizando a linha de produção subsea. Assinatura: P-PDG, P-TPT e QGL caem; T-PDG decresce. Alta pressão + baixa temperatura = risco de hidrato. Rótulo base=8, transiente=108. Entidade: event_hydrate_production. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 8,
      transient: true,
      transient_label: 108,
      entity_id: "event_hydrate_production",
      event_class: "flow_assurance",
      source: TW_SRC,
    },
  },
  {
    id: "threew_event_9_hydrate_svc",
    type: "threew_event",
    text: "Classe 3W 9 — Hidrato na Linha de Serviço (Hydrate in Service Line): Formação de hidrato na linha de injeção de inibidor/fluido de intervenção. Assinatura: QBS e P-JUS-BS caem; T-JUS-CKP indicativa. Rótulo base=9, transiente=109. Entidade: event_hydrate_service. Fonte: Petrobras 3W v2.0.0.",
    metadata: {
      threew_label: 9,
      transient: true,
      transient_label: 109,
      entity_id: "event_hydrate_service",
      event_class: "flow_assurance",
      source: TW_SRC,
    },
  },
];

// ===========================================================================
// TEXT2CYPHER FEW-SHOTS
// ===========================================================================

export const THREEW_FEW_SHOTS_CYPHER = [
  {
    question_pt: "Quais sensores monitoram hidrato na linha de produção?",
    question_en: "Which sensors detect hydrate in the production line?",
    cypher: `MATCH (e:OperationalEvent {id:'event_hydrate_production'})-[:DETECTED_VIA]->(s:Instrument) RETURN s.id AS sensor, s.label AS tag, s.threew_unit AS unit`,
    expected_columns: ["sensor", "tag", "unit"],
    difficulty: "medium",
    tags: ["3w", "hydrate", "sensor"],
  },
  {
    question_pt: "Liste todos os eventos transientes do dataset 3W.",
    question_en: "List all transient events from the 3W dataset.",
    cypher: `MATCH (e:OperationalEvent) WHERE e.threew_transient = true RETURN e.id, e.label, e.threew_label AS base_label, e.threew_transient_label AS transient_label ORDER BY e.threew_label`,
    expected_columns: ["e.id", "e.label", "base_label", "transient_label"],
    difficulty: "easy",
    tags: ["3w", "transient", "event"],
  },
  {
    question_pt: "Qual a diferença entre SDV-P e SDV-GL?",
    question_en: "What is the difference between SDV-P and SDV-GL?",
    cypher: `MATCH (s) WHERE s.id IN ['sdv_p','sdv_gl'] RETURN s.id, s.label, s.definition, s.threew_equipment_subtype`,
    expected_columns: ["s.id", "s.label", "s.definition", "s.threew_equipment_subtype"],
    difficulty: "easy",
    tags: ["3w", "equipment", "valve"],
  },
  {
    question_pt: "Em qual válvula ocorrem scaling e restrição rápida?",
    question_en: "In which valve do scaling and quick restriction occur?",
    cypher: `MATCH (e:OperationalEvent)-[:INVOLVES_EQUIPMENT]->(eq) WHERE e.id IN ['event_scaling_pck','event_quick_pck_restriction'] RETURN DISTINCT eq.id, eq.label`,
    expected_columns: ["eq.id", "eq.label"],
    difficulty: "medium",
    tags: ["3w", "choke", "pck"],
  },
  {
    question_pt: "Quais classes 3W têm o sensor PDG na assinatura?",
    question_en: "Which 3W event classes have the PDG sensor in their signature?",
    cypher: `MATCH (e:OperationalEvent)-[:DETECTED_VIA]->(s:Instrument {id:'sensor_p_pdg'}) RETURN e.id, e.label, e.threew_label ORDER BY e.threew_label`,
    expected_columns: ["e.id", "e.label", "e.threew_label"],
    difficulty: "medium",
    tags: ["3w", "pdg", "sensor", "multi-hop"],
  },
];

// ===========================================================================
// TEXT2SPARQL FEW-SHOTS
// ===========================================================================

export const THREEW_FEW_SHOTS_SPARQL = [
  {
    question_pt: "Quais sensores 3W medem pressão downhole?",
    question_en: "Which 3W sensors measure downhole pressure?",
    sparql: `PREFIX geo: <https://geolytics.petrobras.com.br/dict/>\nSELECT ?sensor ?tag WHERE {\n  ?sensor a geo:Instrument ;\n    geo:threewSignalRole "pressure_downhole" ;\n    geo:threewTag ?tag .\n}`,
    expected_vars: ["sensor", "tag"],
    tags: ["3w", "pressure", "sparql"],
  },
  {
    question_pt: "Quais equipamentos da ANM são monitorados por sensores de estado de válvula?",
    question_en: "Which ANM equipment items are monitored by valve state sensors?",
    sparql: `PREFIX geo: <https://geolytics.petrobras.com.br/dict/>\nSELECT ?sensor ?equip WHERE {\n  ?sensor a geo:Instrument ;\n    geo:threewQuantityKind "ValveState" ;\n    geo:measuredAt ?equip .\n  ?equip geo:partOf geo:anm .\n}`,
    expected_vars: ["sensor", "equip"],
    tags: ["3w", "valve", "anm", "sparql"],
  },
  {
    question_pt: "Quais eventos de flow assurance envolvem o poço?",
    question_en: "Which flow assurance events involve the well?",
    sparql: `PREFIX geo: <https://geolytics.petrobras.com.br/dict/>\nSELECT ?event ?label WHERE {\n  ?event a geo:OperationalEvent ;\n    geo:threewEventClass "flow_assurance" ;\n    geo:label ?label .\n}`,
    expected_vars: ["event", "label"],
    tags: ["3w", "hydrate", "flow_assurance", "sparql"],
  },
];

// ===========================================================================
// WITSML CROSSWALK — 3W sensor variables mapped to WITSML 2.0 concepts
// These entries extend data/witsml-rdf-crosswalk.json (applied via generate.js)
// ===========================================================================

export const THREEW_WITSML_CROSSWALK = [
  {
    witsml_class: "ChannelSet/Channel[P-PDG]",
    witsml_uri: "http://www.energistics.org/energyml/data/witsmlv2/2.0#Channel",
    rdf_class: "geo:Sensor3W",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/sensor_p_pdg",
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    layer: "layer4",
    description_pt:
      "Canal de pressão downhole PDG no WITSML 2.0 (ChannelSet). Equivalente 3W: P-PDG [Pa].",
    description_en: "WITSML 2.0 Channel for downhole PDG pressure. 3W equivalent: P-PDG [Pa].",
  },
  {
    witsml_class: "ChannelSet/Channel[T-PDG]",
    witsml_uri: "http://www.energistics.org/energyml/data/witsmlv2/2.0#Channel",
    rdf_class: "geo:Sensor3W",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/sensor_t_pdg",
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    layer: "layer4",
    description_pt: "Canal de temperatura downhole PDG no WITSML 2.0.",
    description_en: "WITSML 2.0 Channel for downhole PDG temperature.",
  },
  {
    witsml_class: "ChannelSet/Channel[CHOKE_POSITION]",
    witsml_uri: "http://www.energistics.org/energyml/data/witsmlv2/2.0#Channel",
    rdf_class: "geo:Sensor3W",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/sensor_aber_ckp",
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    layer: "layer4",
    description_pt: "Posição do choke de produção. Equivalente 3W: ABER-CKP [%].",
    description_en: "Production choke position. 3W equivalent: ABER-CKP [%].",
  },
  {
    witsml_class: "DownholeComponent[SafetyValve]",
    witsml_uri: "http://www.energistics.org/energyml/data/witsmlv2/2.0#DownholeComponent",
    rdf_class: "geo:Equipment",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/dhsv",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:DownholeSafetyValve:1.0.0",
    layer: "layer4",
    description_pt: "Válvula de segurança de subsuperfície (DHSV/SSSV).",
    description_en: "Downhole safety valve (DHSV/SSSV).",
  },
  {
    witsml_class: "DownholeComponent[Gauge]",
    witsml_uri: "http://www.energistics.org/energyml/data/witsmlv2/2.0#DownholeComponent",
    rdf_class: "geo:Equipment",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/pdg",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:PermanentDownholeGauge:1.0.0",
    layer: "layer4",
    description_pt: "Medidor permanente de fundo (PDG).",
    description_en: "Permanent downhole gauge (PDG).",
  },
];

// ===========================================================================
// PRODML CROSSWALK — 3W events and sensors mapped to PRODML 2.x
// ===========================================================================

export const THREEW_PRODML_CROSSWALK = [
  {
    prodml_class: "ProductionOperation/Well",
    prodml_uri: "http://www.energistics.org/energyml/data/prodmlv2#ProductionOperation",
    rdf_class: "geo:OperationalEvent",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/event_normal",
    osdu_kind: null,
    layer: "layer4",
    description_pt: "Operação de produção normal no PRODML. Equivalente 3W: event_normal.",
    description_en: "Normal production operation in PRODML. 3W equivalent: event_normal.",
  },
  {
    prodml_class: "FlowMeasurement/GasLift",
    prodml_uri: "http://www.energistics.org/energyml/data/prodmlv2#FlowMeasurement",
    rdf_class: "geo:Sensor3W",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/sensor_qgl",
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    layer: "layer4",
    description_pt: "Medição de fluxo de gas-lift. Equivalente 3W: QGL [m³/s].",
    description_en: "Gas-lift flow measurement. 3W equivalent: QGL [m³/s].",
  },
  {
    prodml_class: "ProductionEvent/HydrateBlockage",
    prodml_uri: "http://www.energistics.org/energyml/data/prodmlv2#ProductionEvent",
    rdf_class: "geo:OperationalEvent",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/event_hydrate_production",
    osdu_kind: null,
    layer: "layer6",
    description_pt:
      "Evento de obstrução por hidrato na linha de produção. Equivalente 3W: event_hydrate_production (classe 8).",
    description_en:
      "Hydrate blockage event in production line. 3W equivalent: event_hydrate_production (class 8).",
  },
  {
    prodml_class: "WellTest/DownholePressure",
    prodml_uri: "http://www.energistics.org/energyml/data/prodmlv2#WellTest",
    rdf_class: "geo:Sensor3W",
    rdf_uri: "https://geolytics.petrobras.com.br/dict/sensor_p_pdg",
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    layer: "layer4",
    description_pt: "Pressão de fundo em teste de poço. Equivalente 3W: P-PDG [Pa].",
    description_en: "Downhole pressure in well test. 3W equivalent: P-PDG [Pa].",
  },
];

// ===========================================================================
// SWEET ALIGNMENT — 3W entities mapped to SWEET ontology URIs
// These entries extend data/sweet-alignment.json (applied via generate.js)
// ===========================================================================

export const THREEW_SWEET_ALIGNMENT = [
  // Sensors — pressure
  {
    geolytics_id: "sensor_p_pdg",
    sweet_uris: ["http://sweetontology.net/propPressure/Pressure"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propPressure",
    rationale_pt:
      "P-PDG mede pressão de fluido downhole, mapeando diretamente para propPressure/Pressure.",
  },
  {
    geolytics_id: "sensor_p_tpt",
    sweet_uris: ["http://sweetontology.net/propPressure/Pressure"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propPressure",
    rationale_pt: "P-TPT mede pressão na ANM.",
  },
  {
    geolytics_id: "sensor_p_anular",
    sweet_uris: ["http://sweetontology.net/propPressure/Pressure"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propPressure",
    rationale_pt: "P-ANULAR mede pressão no espaço anular do poço.",
  },
  {
    geolytics_id: "sensor_p_mon_ckp",
    sweet_uris: ["http://sweetontology.net/propPressure/Pressure"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propPressure",
    rationale_pt: "P-MON-CKP mede pressão a montante do choke.",
  },
  {
    geolytics_id: "sensor_p_jus_ckp",
    sweet_uris: ["http://sweetontology.net/propPressure/Pressure"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propPressure",
    rationale_pt: "P-JUS-CKP mede pressão a jusante do choke.",
  },
  // Sensors — temperature
  {
    geolytics_id: "sensor_t_pdg",
    sweet_uris: ["http://sweetontology.net/propTemperature/Temperature"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propTemperature",
    rationale_pt: "T-PDG mede temperatura downhole.",
  },
  {
    geolytics_id: "sensor_t_tpt",
    sweet_uris: ["http://sweetontology.net/propTemperature/Temperature"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propTemperature",
    rationale_pt: "T-TPT mede temperatura na ANM.",
  },
  {
    geolytics_id: "sensor_t_mon_ckp",
    sweet_uris: ["http://sweetontology.net/propTemperature/Temperature"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propTemperature",
    rationale_pt: "T-MON-CKP mede temperatura a montante do choke.",
  },
  // Sensors — flow
  {
    geolytics_id: "sensor_qgl",
    sweet_uris: ["http://sweetontology.net/propFluid/FlowRate"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propFluid",
    rationale_pt: "QGL mede vazão volumétrica de gas-lift.",
  },
  {
    geolytics_id: "sensor_qbs",
    sweet_uris: ["http://sweetontology.net/propFluid/FlowRate"],
    alignment_type: "skos:closeMatch",
    sweet_module: "propFluid",
    rationale_pt: "QBS mede vazão da bomba de serviço.",
  },
  // Events — flow regime
  {
    geolytics_id: "event_severe_slugging",
    sweet_uris: ["http://sweetontology.net/phenFluidDynamics/FlowInstability"],
    alignment_type: "skos:relatedMatch",
    sweet_module: "phenFluidDynamics",
    rationale_pt: "Golfadas severas são instabilidade de fluxo bifásico em riser.",
  },
  {
    geolytics_id: "event_flow_instability",
    sweet_uris: ["http://sweetontology.net/phenFluidDynamics/FlowInstability"],
    alignment_type: "skos:relatedMatch",
    sweet_module: "phenFluidDynamics",
    rationale_pt: "Instabilidade de fluxo multifásico no poço.",
  },
  // Events — hydrate (phase transition)
  {
    geolytics_id: "event_hydrate_production",
    sweet_uris: ["http://sweetontology.net/phenFluidInstability/HydrateFormation"],
    alignment_type: "skos:closeMatch",
    sweet_module: "phenFluidInstability",
    rationale_pt: "Formação de hidrato de gás na linha de produção subsea.",
  },
  {
    geolytics_id: "event_hydrate_service",
    sweet_uris: ["http://sweetontology.net/phenFluidInstability/HydrateFormation"],
    alignment_type: "skos:closeMatch",
    sweet_module: "phenFluidInstability",
    rationale_pt: "Formação de hidrato de gás na linha de serviço subsea.",
  },
];

// ===========================================================================
// OSDU MAPPING — 3W entities mapped to OSDU kinds
// ===========================================================================

export const THREEW_OSDU_MAPPING = [
  // Sensors → TimeSeriesData
  ...THREEW_VARIABLES.map((v) => ({
    geolytics_id: v.id,
    osdu_kind: "opendes:osdu:work-product-component--TimeSeriesData:1.0.0",
    osdu_layer: "layer4",
    note: `3W sensor ${v.threew_tag}`,
  })),
  // Equipment → EquipmentType
  {
    geolytics_id: "anm",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:SubseaXmasTree:1.0.0",
    osdu_layer: "layer4",
    note: "Subsea Xmas-tree assembly",
  },
  {
    geolytics_id: "pmv",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:ProductionMasterValve:1.0.0",
    osdu_layer: "layer4",
    note: "PMV — M1",
  },
  {
    geolytics_id: "amv",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:AnnulusMasterValve:1.0.0",
    osdu_layer: "layer4",
    note: "AMV — M2",
  },
  {
    geolytics_id: "pwv",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:ProductionWingValve:1.0.0",
    osdu_layer: "layer4",
    note: "PWV — W1",
  },
  {
    geolytics_id: "awv",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:AnnulusWingValve:1.0.0",
    osdu_layer: "layer4",
    note: "AWV — W2",
  },
  {
    geolytics_id: "pck",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:ProductionChoke:1.0.0",
    osdu_layer: "layer4",
    note: "PCK — production choke",
  },
  {
    geolytics_id: "glck",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:GasLiftChoke:1.0.0",
    osdu_layer: "layer4",
    note: "GLCK — gas-lift choke",
  },
  {
    geolytics_id: "sdv_p",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:ProductionShutdownValve:1.0.0",
    osdu_layer: "layer4",
    note: "SDV-P",
  },
  {
    geolytics_id: "sdv_gl",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:GasLiftShutdownValve:1.0.0",
    osdu_layer: "layer4",
    note: "SDV-GL",
  },
  {
    geolytics_id: "tpt",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:TemperaturePressureTransducer:1.0.0",
    osdu_layer: "layer4",
    note: "TPT",
  },
  {
    geolytics_id: "pdg",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:PermanentDownholeGauge:1.0.0",
    osdu_layer: "layer4",
    note: "PDG",
  },
  {
    geolytics_id: "sp_pump",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:ServicePump:1.0.0",
    osdu_layer: "layer4",
    note: "SP — service pump",
  },
  {
    geolytics_id: "dhsv",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:DownholeSafetyValve:1.0.0",
    osdu_layer: "layer4",
    note: "DHSV (patch to existing node)",
  },
  {
    geolytics_id: "pxo",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:PigCrossoverValve:1.0.0",
    osdu_layer: "layer4",
    note: "PXO",
  },
  {
    geolytics_id: "xo",
    osdu_kind: "opendes:osdu:reference-data--EquipmentType:CrossoverValve:1.0.0",
    osdu_layer: "layer4",
    note: "XO",
  },
];

// ===========================================================================
// POLYSEMY CARDS — 3 disambiguation cards
// ===========================================================================

export const THREEW_POLYSEMY_CARDS = [
  {
    id: "CARD_POLYSEMY_PCK_2026_05_03",
    term: "PCK",
    created: "2026-05-03",
    description:
      "PCK é ambíguo: no contexto 3W/ANM refere-se ao Production Choke (estrangulador de produção subsea); em contextos genéricos de tubulação pode significar Pilot-operated Check Valve.",
    senses: [
      {
        sense_id: "pck_production_choke",
        label: "PCK — Production Choke (3W/ANM)",
        entity_id: "pck",
        context_keywords: [
          "estrangulamento",
          "choke",
          "ABER-CKP",
          "P-MON-CKP",
          "P-JUS-CKP",
          "ANM",
          "subsea",
          "3W",
          "scaling",
          "restrição",
        ],
      },
      {
        sense_id: "pck_check_valve",
        label: "PCK — Pilot-operated Check Valve (genérico)",
        entity_id: null,
        context_keywords: ["check valve", "válvula de retenção", "piloto", "tubulação superfície"],
      },
    ],
    resolution_rules: [
      'Se contexto contém "ABER-CKP", "P-MON-CKP", "P-JUS-CKP", "scaling", "restrição", "ANM" ou "3W" → usar pck (production choke)',
      'Se contexto contém "check valve", "válvula de retenção" sem referência a ANM/3W → sentido genérico',
    ],
    default_sense: "pck_production_choke",
  },
  {
    id: "CARD_POLYSEMY_BSW_2026_05_03",
    term: "BSW",
    created: "2026-05-03",
    description:
      "BSW tem dois sentidos: (1) propriedade de fluido — Basic Sediment and Water, fração de água e sedimentos na amostra de óleo; (2) evento operacional 3W classe 1 — Abrupt Increase of BSW.",
    senses: [
      {
        sense_id: "bsw_fluid_property",
        label: "BSW — Basic Sediment and Water (propriedade)",
        entity_id: "bsw",
        context_keywords: [
          "fração",
          "sedimento",
          "propriedade",
          "amostra",
          "medição",
          "corte de água",
        ],
      },
      {
        sense_id: "bsw_event",
        label: "BSW — Evento 3W classe 1 (Aumento Abrupto)",
        entity_id: "event_bsw_increase",
        context_keywords: [
          "aumento",
          "abrupto",
          "classe 1",
          "label=1",
          "101",
          "3W",
          "evento",
          "irrupção",
        ],
      },
    ],
    resolution_rules: [
      'Se contexto contém "aumento", "abrupto", "classe 1", "3W" ou "label" → sentido evento (event_bsw_increase)',
      'Se contexto contém "fração", "medição", "corte", "propriedade" → sentido fluido (bsw)',
    ],
    default_sense: "bsw_fluid_property",
  },
  {
    id: "CARD_POLYSEMY_STATE_2026_05_03",
    term: "state",
    created: "2026-05-03",
    description:
      'O campo "state" tem dois significados distintos: (1) status operacional interno do poço no dataset 3W (coluna "state" no Parquet); (2) well_state — taxonomia ANP de situação cadastral do poço (ativo, abandonado, cancelado, etc.).',
    senses: [
      {
        sense_id: "state_3w",
        label: "state — Status Operacional 3W (Parquet)",
        entity_id: null,
        context_keywords: ["3W", "Parquet", "class", "timestamp", "WELL_", "SIMULATED_", "DRAWN_"],
      },
      {
        sense_id: "state_anp",
        label: "well_state — Situação Cadastral ANP",
        entity_id: "poco",
        context_keywords: [
          "ANP",
          "SIGEP",
          "cadastro",
          "ativo",
          "abandonado",
          "cancelado",
          "perfurado",
        ],
      },
    ],
    resolution_rules: [
      'Se contexto menciona "3W", "Parquet", "class", "WELL_" → sentido 3W (coluna operacional)',
      'Se contexto menciona "ANP", "SIGEP", "cadastro", "situação" → sentido well_state ANP',
    ],
    default_sense: "state_anp",
  },
];
