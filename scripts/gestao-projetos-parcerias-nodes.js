/* Gestão de Projetos e Parcerias (GPP) — entity-graph nodes, edges, glossary.
   Sourced from data/gestao-projetos-parcerias.json. Merged into the build
   pipeline by scripts/generate.js, mirroring how OG_NODES works.

   Covers: Bloco lifecycle states, PROPEX governance program, decision gates
   (PEXP), PGP/TEP documents, PAD/DC/PD regulatory chain, partnership
   management (Working Interest, Operator role), portfolio decisions.

   Naming: corporate_internal entries (PROPEX, PEXP, PGP, TEP, ISA, COMEXP,
   GRBLOC, GRT, ProjetoExploratorio, PortfolioExploratorio) are flagged with
   `corporate_internal: true` in metadata so RAG can filter by audience.
*/

/* Helper to compose a node with sensible defaults. Keeps NODES array readable. */
function gpp(node) {
  return {
    color: "#9B59B6",
    size: 18,
    legal_source: null,
    datasets: [],
    petrokgraph_uri: null,
    osdu_kind: null,
    geosciml_uri: null,
    owl_uri: null,
    geocoverage: ["layer4", "layer5"],
    synonyms_pt: [],
    synonyms_en: [],
    examples: [],
    glossary_id: null,
    extended_id: null,
    corporate_internal: false,
    evidence_status: "documented",
    ...node,
    skos_prefLabel: { "@pt": node.label_pt || node.label, "@en": node.label_en || node.label },
    skos_altLabel: {
      "@pt": node.synonyms_pt || [],
      "@en": node.synonyms_en || [],
    },
    skos_definition: {
      "@pt": node.definition_pt || node.definition,
      "@en": node.definition_en_canonical || node.definition,
    },
    skos_example: node.examples || [],
  };
}

export const GPP_NODES = [
  gpp({
    id: "bloco-anchor",
    label: "Bloco (entidade-âncora)",
    label_pt: "Bloco (entidade-âncora)",
    label_en: "Block (anchor entity)",
    type: "regulatory_anchor",
    color: "#378ADD",
    size: 28,
    definition_pt:
      "Unidade primária de concessão/partilha. Ancora simultaneamente conceitos regulatórios (contrato E&P), técnicos (poços, projetos exploratórios) e de decisão (portfólio, ranking, devolução). Detalhada em data/gestao-projetos-parcerias.json#GPP001.",
    definition_en_canonical:
      "Primary upstream concession/production-sharing unit. Anchors regulatory, technical and portfolio-decision concepts simultaneously. Detailed in data/gestao-projetos-parcerias.json#GPP001.",
    legal_source: "Lei 9.478/1997",
    geocoverage: ["layer4", "layer5"],
    synonyms_pt: ["Bloco", "Bloco Exploratório", "Área Concedida"],
    synonyms_en: ["Exploration Block", "Lease Block"],
    examples: ["BM-S-11 (Lula)", "BCAM-40 (Búzios)", "BS-4 (Atlanta)", "BM-C-33"],
    module: "data/gestao-projetos-parcerias.json#GPP001",
    evidence_refs: ["Lei 9.478/1997", "Curso PROPEX 2024/2025"],
  }),
  /* contrato-ep, pem already exist in base ENTITY_NODES with rich definitions —
     enriched in-place via GPP_NODE_PATCHES below. */
  gpp({
    id: "bloco-exploratorio-state",
    label: "Bloco Exploratório (estado)",
    label_pt: "Bloco Exploratório (estado)",
    label_en: "Exploratory Block (state)",
    type: "lifecycle_state",
    color: "#1ABC9C",
    definition_pt:
      "Estado do Bloco sob contrato ativo, sem descoberta comercial. Governança via PROPEX. Conecta a Poços Pioneiros/Estratigráficos, Avaliação de Risco, VME.",
    definition_en_canonical:
      "Block lifecycle state under active contract, no commercial discovery yet. PROPEX-governed.",
    module: "data/gestao-projetos-parcerias.json#GPP004",
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "bloco-em-avaliacao-state",
    label: "Bloco em Avaliação",
    label_pt: "Bloco em Avaliação",
    label_en: "Block under Evaluation",
    type: "lifecycle_state",
    color: "#1ABC9C",
    definition_pt:
      "Estado após descoberta no Bloco — fase de delimitação e estudos técnico-econômicos. Fase PEXP2 do PROPEX.",
    definition_en_canonical:
      "State following a discovery — delineation and techno-economic studies. PROPEX PEXP2 phase.",
    module: "data/gestao-projetos-parcerias.json#GPP005",
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "area-em-pad-state",
    label: "Área em PAD",
    label_pt: "Área em PAD",
    label_en: "Area under Discovery Evaluation Plan",
    type: "lifecycle_state",
    color: "#1ABC9C",
    definition_pt:
      "Subárea do Bloco formalmente submetida a Plano de Avaliação de Descoberta (PAD). Múltiplos PADs podem coexistir num Bloco.",
    definition_en_canonical:
      "Block subarea formally under a Discovery Evaluation Plan. Multiple PADs may coexist within a Block.",
    legal_source: "Resolução ANP 47/2014",
    module: "data/gestao-projetos-parcerias.json#GPP006",
    evidence_refs: ["Resolução ANP 47/2014"],
  }),
  gpp({
    id: "campo-em-desenvolvimento-state",
    label: "Campo em Desenvolvimento",
    label_pt: "Campo em Desenvolvimento",
    label_en: "Field under Development",
    type: "lifecycle_state",
    color: "#16A085",
    definition_pt:
      "Estado pós-DC: a área do Bloco vira Campo, e um PD/PDP é aprovado. CAPEX, perfuração de poços de desenvolvimento, infraestrutura.",
    definition_en_canonical:
      "Post-DC state: Block area becomes a Field, and a PD/PDP is approved. CAPEX, development drilling, infrastructure.",
    legal_source: "Resolução ANP 17/2015",
    module: "data/gestao-projetos-parcerias.json#GPP007",
    evidence_refs: ["Resolução ANP 17/2015"],
  }),
  gpp({
    id: "campo-producao-state",
    label: "Campo de Produção",
    label_pt: "Campo de Produção",
    label_en: "Production Field",
    type: "lifecycle_state",
    color: "#16A085",
    definition_pt:
      "Campo com produção iniciada. Marco regulatório: Notificação de Início de Produção (Primeiro Óleo). Conecta a Poços Produtores/Injetores, OPEX, Medição Fiscal, Reservas.",
    definition_en_canonical:
      "Field with active production. Regulatory milestone: Start-of-Production notice (First Oil).",
    module: "data/gestao-projetos-parcerias.json#GPP008",
    evidence_refs: ["ANP/SEP"],
  }),
  gpp({
    id: "propex",
    label: "PROPEX (Programa Exploratório)",
    label_pt: "PROPEX (Programa Exploratório)",
    label_en: "PROPEX — Exploratory Program",
    type: "governance_program",
    color: "#8E44AD",
    size: 22,
    definition_pt:
      "Programa corporativo Petrobras de governança de projetos exploratórios em Blocos. Estrutura PEXPs, PGPs, TEPs, fóruns COMEXP/GRBLOC. PROPEX é Programa, NÃO projeto.",
    definition_en_canonical:
      "Petrobras corporate program governing exploratory projects in Blocks. Structures PEXPs, PGPs, TEPs, forums COMEXP/GRBLOC. PROPEX is a Program, NOT a project.",
    module: "data/gestao-projetos-parcerias.json#GPP009",
    synonyms_pt: ["PROPEX", "Programa Exploratório"],
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "projeto-exploratorio",
    label: "Projeto Exploratório",
    label_pt: "Projeto Exploratório",
    label_en: "Exploratory Project",
    type: "project",
    color: "#9B59B6",
    definition_pt:
      "Conjunto delimitado de atividades técnicas/econômicas/operacionais em um Bloco, voltadas a verificar acumulações de hidrocarbonetos. Governado pelo PROPEX, distinto deste.",
    definition_en_canonical:
      "Delimited set of technical/economic/operational activities in a Block, aimed at verifying hydrocarbon accumulations. Governed by PROPEX, distinct from it.",
    module: "data/gestao-projetos-parcerias.json#GPP010",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "pexp",
    label: "PEXP — Portões Decisórios PROPEX",
    label_pt: "PEXP — Portões Decisórios PROPEX",
    label_en: "PEXP — PROPEX Decision Gates",
    type: "decision_event",
    color: "#E74C3C",
    definition_pt:
      "Eventos decisórios formais do PROPEX. Gates: PEXP1 (estratégia), PEXP2 (PAD/devolução), PEXP2A (revisão PEM), PEXP3 (DC/devolução), PEXP3A (revisão PAD).",
    definition_en_canonical:
      "Formal PROPEX decision events. Gates: PEXP1 (strategy), PEXP2 (PAD/relinquishment), PEXP2A (PEM review), PEXP3 (DC/relinquishment), PEXP3A (PAD review).",
    module: "data/gestao-projetos-parcerias.json#GPP011",
    synonyms_pt: ["PEXP", "PEXP1", "PEXP2", "PEXP2A", "PEXP3", "PEXP3A"],
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "pgp",
    label: "PGP — Plano de Gerenciamento de Projetos",
    label_pt: "PGP — Plano de Gerenciamento de Projetos",
    label_en: "PGP — Project Management Plan",
    type: "governance_doc",
    color: "#E67E22",
    definition_pt:
      "Documento de escopo/cronograma/custo/riscos/governança de projeto no PROPEX. Variantes: PGP do Bloco e PGP do PAD. Obrigatório nos PEXPs.",
    definition_en_canonical:
      "Project scope/schedule/cost/risk/governance document within PROPEX. Variants: Block-PGP, PAD-PGP. Mandatory at PEXPs.",
    module: "data/gestao-projetos-parcerias.json#GPP012",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  /* pad, declaracao-comercialidade already exist in base ENTITY_NODES with
     rich definitions — enriched in-place via GPP_NODE_PATCHES below. */
  gpp({
    id: "pd-pdp",
    label: "PD/PDP — Plano de Desenvolvimento (da Produção)",
    label_pt: "PD/PDP — Plano de Desenvolvimento (da Produção)",
    label_en: "PD/PDP — Production Development Plan",
    type: "regulatory_doc",
    color: "#F39C12",
    size: 22,
    definition_pt:
      "Documento técnico-regulatório, em até 180 dias após DC. Agrupa info técnica/operacional/econômica/ambiental da explotação, incluindo abandono. ANP analisa em 180 dias.",
    definition_en_canonical:
      "Technical-regulatory document, within 180 days of DC. Aggregates technical/operational/economic/environmental info, including abandonment. ANP review within 180 days.",
    legal_source: "Resolução ANP 17/2015",
    module: "data/gestao-projetos-parcerias.json#GPP015",
    synonyms_pt: ["PD", "PDP", "Plano de Desenvolvimento", "Plano de Desenvolvimento da Produção"],
    evidence_refs: ["Resolução ANP 17/2015"],
  }),
  gpp({
    id: "tep",
    label: "TEP — Termo de Encerramento do Projeto",
    label_pt: "TEP — Termo de Encerramento do Projeto",
    label_en: "TEP — Project Closure Term",
    type: "governance_doc",
    color: "#7F8C8D",
    definition_pt:
      "Documento que encerra um Projeto Exploratório. Registra decisão final (DC ou devolução) e lições aprendidas. Encerra Projeto, validado pelo Programa PROPEX.",
    definition_en_canonical:
      "Document closing an Exploratory Project. Records final decision (DC or relinquishment) and lessons learned. Closes Project, validated by PROPEX Program.",
    module: "data/gestao-projetos-parcerias.json#GPP016",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "isa",
    label: "ISA — Instrumento de Situação do Ativo",
    label_pt: "ISA — Instrumento de Situação do Ativo",
    label_en: "ISA — Asset Status Instrument",
    type: "governance_doc",
    color: "#7F8C8D",
    definition_pt:
      "Documento/ato interno que formaliza passagem da Fase de Exploração para Produção. Marco administrativo pós-DC.",
    definition_en_canonical:
      "Internal document/act formalizing transition from Exploration to Production phase. Administrative milestone post-DC.",
    module: "data/gestao-projetos-parcerias.json#GPP017",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "comexp",
    label: "COMEXP",
    label_pt: "COMEXP — Comitê de Gestão da Exploração",
    label_en: "COMEXP — Exploration Management Committee",
    type: "governance_committee",
    color: "#34495E",
    definition_pt:
      "Instância máxima de decisão do PROPEX. Delibera PEXPs, PAD, DC e devoluções de Bloco.",
    definition_en_canonical:
      "Highest PROPEX decision instance. Deliberates PEXPs, PAD, DC, Block relinquishments.",
    module: "data/gestao-projetos-parcerias.json#GPP018",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "grbloc",
    label: "GRBLOC",
    label_pt: "GRBLOC — Grupo Técnico de Blocos",
    label_en: "GRBLOC — Block Technical Review Group",
    type: "governance_committee",
    color: "#34495E",
    definition_pt:
      "Grupo técnico de pré-análise de decisões de Bloco antes do COMEXP. Garante due diligence técnica.",
    definition_en_canonical: "Technical pre-review group for Block decisions, feeding COMEXP.",
    module: "data/gestao-projetos-parcerias.json#GPP019",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "grt",
    label: "GRT — Grupo de Revisão Técnica",
    label_pt: "GRT — Grupo de Revisão Técnica",
    label_en: "GRT — Technical Review Group",
    type: "governance_committee",
    color: "#34495E",
    definition_pt:
      "Grupo técnico que apoia os PEXPs com revisão de aspectos geológicos, de engenharia e econômicos.",
    definition_en_canonical: "Technical group supporting PEXPs with subject-matter review.",
    module: "data/gestao-projetos-parcerias.json#GPP020",
    corporate_internal: true,
    evidence_refs: ["Curso PROPEX 2024/2025"],
  }),
  gpp({
    id: "working-interest",
    label: "Participação (Working Interest)",
    label_pt: "Participação (Working Interest — WI)",
    label_en: "Working Interest (WI)",
    type: "portfolio_concept",
    color: "#5D6D7E",
    definition_pt:
      "Percentual de um sócio nos custos e receitas de Bloco/Campo. Soma 100%. Determina peso decisório e alocação de CAPEX/OPEX.",
    definition_en_canonical:
      "Partner's percentage share of costs and revenues in a Block/Field. Sums to 100%. Determines decision weight and CAPEX/OPEX allocation.",
    module: "data/gestao-projetos-parcerias.json#GPP021",
    synonyms_pt: ["WI", "Working Interest", "Participação"],
    evidence_refs: ["SPE Reserves Definitions"],
  }),
  gpp({
    id: "operador-role",
    label: "Operador / Não-Operador",
    label_pt: "Papel de Operador / Não-Operador",
    label_en: "Operator / Non-Operator Role",
    type: "portfolio_concept",
    color: "#5D6D7E",
    definition_pt:
      "Designa o sócio responsável pela execução das operações. Petrobras é Operadora obrigatória nos blocos do pré-sal sob Partilha (Lei 12.351/2010).",
    definition_en_canonical:
      "Designates the partner responsible for executing operations. Petrobras is mandatory Operator in pre-salt Production-Sharing blocks.",
    module: "data/gestao-projetos-parcerias.json#GPP022",
    legal_source: "Lei 12.351/2010",
    evidence_refs: ["Lei 12.351/2010"],
  }),
  gpp({
    id: "rodada",
    label: "Rodada (Leilão de Blocos)",
    label_pt: "Rodada (Leilão de Blocos)",
    label_en: "Bidding Round",
    type: "regulatory_event",
    color: "#3498DB",
    definition_pt:
      "Processo licitatório público da ANP para oferta de Blocos exploratórios. Cada Rodada tem Edital, áreas e regras próprios.",
    definition_en_canonical:
      "ANP public bidding process for offering exploration Blocks. Each Round has its own notice, areas and rules.",
    module: "data/gestao-projetos-parcerias.json#GPP023",
    synonyms_pt: ["Rodada", "Leilão de Blocos"],
    evidence_refs: ["Lei 9.478/1997"],
  }),
  gpp({
    id: "area-retida",
    label: "Área Retida",
    label_pt: "Área Retida",
    label_en: "Retained Area",
    type: "lifecycle_outcome",
    color: "#A569BD",
    definition_pt:
      "Porção do Bloco mantida pelo operador ao fim de fase exploratória, tipicamente em razão de descoberta ativa ou PAD.",
    definition_en_canonical:
      "Block portion kept by operator after an exploratory phase, typically due to active discovery or PAD.",
    module: "data/gestao-projetos-parcerias.json#GPP024",
    evidence_refs: ["Contratos de Concessão ANP"],
  }),
  gpp({
    id: "area-devolvida",
    label: "Área Devolvida",
    label_pt: "Área Devolvida",
    label_en: "Relinquished Area",
    type: "lifecycle_outcome",
    color: "#A569BD",
    definition_pt:
      "Porção do Bloco devolvida à ANP — parcial ou total. Após devolução, a área retorna à ANP para nova licitação.",
    definition_en_canonical:
      "Block portion returned to ANP — partial or total. Once relinquished, returns to ANP for re-bidding.",
    module: "data/gestao-projetos-parcerias.json#GPP025",
    evidence_refs: ["Contratos de Concessão ANP"],
  }),
  gpp({
    id: "portfolio-exploratorio",
    label: "Portfólio Exploratório",
    label_pt: "Portfólio Exploratório",
    label_en: "Exploration Portfolio",
    type: "portfolio_concept",
    color: "#BB8FCE",
    definition_pt:
      "Conjunto agregado de Blocos sob gestão do operador. Decisões de portfólio consideram VME, risco geológico, PEM, cronograma e composição de sócios.",
    definition_en_canonical:
      "Aggregate Block set under operator management. Portfolio decisions consider EMV, geological risk, PEM, schedule and partnership.",
    module: "data/gestao-projetos-parcerias.json#GPP026",
    corporate_internal: true,
    evidence_status: "partial",
    evidence_refs: ["Material gestão E&P Petrobras"],
  }),
  gpp({
    id: "vme",
    label: "VME — Valor Monetário Esperado",
    label_pt: "VME — Valor Monetário Esperado",
    label_en: "VME — Expected Monetary Value (EMV)",
    type: "portfolio_concept",
    color: "#BB8FCE",
    definition_pt:
      "Soma sobre resultados de (VPL × probabilidade). Insumo padrão para ranqueamento de Blocos e PEXPs.",
    definition_en_canonical:
      "Sum over outcomes of (NPV × probability). Standard input to Block ranking and PEXP decisions.",
    module: "data/gestao-projetos-parcerias.json#GPP027",
    synonyms_pt: ["VME"],
    synonyms_en: ["EMV", "Expected Monetary Value"],
    evidence_refs: ["SPE/AAPG decision-analysis"],
  }),
  gpp({
    id: "obrigacao-exploratoria",
    label: "Obrigação Exploratória",
    label_pt: "Obrigação Exploratória",
    label_en: "Exploratory Obligation",
    type: "regulatory_obligation",
    color: "#5499C7",
    definition_pt:
      "Compromisso específico do PEM (ex.: poço exploratório no ano 3). Cada obrigação tem métrica, prazo e penalidade.",
    definition_en_canonical:
      "Specific PEM commitment (e.g., one exploratory well by year 3). Each has metric, deadline and penalty.",
    module: "data/gestao-projetos-parcerias.json#GPP028",
    evidence_refs: ["Contratos de Concessão ANP"],
  }),
];

/* Helper for edges: source, target, relation (snake_case), and PT label.
   EN label defaults to relation snake-case → space-case. Style defaults to solid. */
function edge(source, target, relation, label, label_en, style = "solid") {
  return {
    source,
    target,
    relation,
    relation_label: label,
    relation_label_en: label_en || relation.replace(/_/g, " "),
    style,
  };
}

export const GPP_EDGES = [
  edge(
    "bloco-anchor",
    "contrato-ep",
    "is_subject_to_contract",
    "está sob contrato",
    "is subject to contract"
  ),
  edge("contrato-ep", "pem", "has_minimum_program", "possui PEM", "has minimum program"),
  edge("pem", "obrigacao-exploratoria", "decomposes_into", "decompõe-se em", "decomposes into"),
  edge(
    "bloco-anchor",
    "bloco-exploratorio-state",
    "has_lifecycle_state",
    "tem estado",
    "has lifecycle state"
  ),
  edge(
    "bloco-anchor",
    "bloco-em-avaliacao-state",
    "has_lifecycle_state",
    "tem estado",
    "has lifecycle state"
  ),
  edge(
    "bloco-anchor",
    "area-em-pad-state",
    "has_lifecycle_state",
    "tem estado",
    "has lifecycle state"
  ),
  edge(
    "bloco-anchor",
    "campo-em-desenvolvimento-state",
    "has_lifecycle_state",
    "tem estado",
    "has lifecycle state"
  ),
  edge(
    "bloco-anchor",
    "campo-producao-state",
    "has_lifecycle_state",
    "tem estado",
    "has lifecycle state"
  ),
  edge(
    "bloco-exploratorio-state",
    "bloco-em-avaliacao-state",
    "transitions_to",
    "transita para",
    "transitions to",
    "dashed"
  ),
  edge(
    "bloco-em-avaliacao-state",
    "area-em-pad-state",
    "transitions_to",
    "transita para",
    "transitions to",
    "dashed"
  ),
  edge(
    "area-em-pad-state",
    "campo-em-desenvolvimento-state",
    "transitions_to",
    "transita para",
    "transitions to",
    "dashed"
  ),
  edge(
    "campo-em-desenvolvimento-state",
    "campo-producao-state",
    "transitions_to",
    "transita para",
    "transitions to",
    "dashed"
  ),
  edge(
    "projeto-exploratorio",
    "propex",
    "is_governed_by_program",
    "é governado pelo Programa",
    "is governed by program"
  ),
  edge("propex", "pexp", "has_decision_gate", "tem portões decisórios", "has decision gate"),
  edge("pexp", "projeto-exploratorio", "evaluates_project", "avalia projeto", "evaluates project"),
  edge(
    "pgp",
    "projeto-exploratorio",
    "documents_project",
    "documenta projeto",
    "documents project"
  ),
  edge("pgp", "pad", "documents_pad", "documenta PAD", "documents PAD"),
  edge("pad", "area-em-pad-state", "triggers_state", "dispara estado", "triggers state"),
  edge("pad", "declaracao-comercialidade", "leads_to", "leva à", "leads to"),
  edge("declaracao-comercialidade", "pd-pdp", "triggers_doc", "dispara documento", "triggers doc"),
  edge(
    "declaracao-comercialidade",
    "campo-em-desenvolvimento-state",
    "marks_field_transition",
    "marca transição para Campo",
    "marks field transition"
  ),
  edge("tep", "projeto-exploratorio", "closes_project", "encerra projeto", "closes project"),
  edge("isa", "campo-producao-state", "marks_transition", "marca transição", "marks transition"),
  edge("comexp", "pexp", "deliberates_at", "delibera em", "deliberates at"),
  edge("grbloc", "comexp", "feeds_committee", "alimenta comitê", "feeds committee"),
  edge("grt", "pexp", "supports_gate", "apoia portão", "supports gate"),
  edge("rodada", "contrato-ep", "produces_contract", "produz contrato", "produces contract"),
  edge(
    "bloco-anchor",
    "working-interest",
    "has_partnership_share",
    "tem participação societária",
    "has partnership share"
  ),
  edge("working-interest", "operador-role", "designates", "designa", "designates"),
  edge("portfolio-exploratorio", "bloco-anchor", "aggregates", "agrega", "aggregates"),
  edge("vme", "bloco-anchor", "scores", "pontua", "scores"),
  edge("area-retida", "bloco-anchor", "is_outcome_of", "é desfecho de", "is outcome of"),
  edge("area-devolvida", "bloco-anchor", "is_outcome_of", "é desfecho de", "is outcome of"),
];

/* In-place patches for nodes that already exist in base ENTITY_NODES.
   Same pattern as THREEW_EQUIPMENT_PATCHES — generate.js applies these via
   Object.assign after merging all node sources. Adds GPP-specific metadata
   (module ref, evidence_refs, corporate_internal flag) without overwriting
   the canonical definition or label. */
export const GPP_NODE_PATCHES = [
  {
    id: "contrato-ep",
    module: "data/gestao-projetos-parcerias.json#GPP002",
    evidence_refs: ["Lei 9.478/1997", "Lei 12.351/2010", "Lei 12.276/2010"],
    corporate_internal: false,
    gpp_role: "regulatory_anchor",
  },
  {
    id: "pem",
    module: "data/gestao-projetos-parcerias.json#GPP003",
    evidence_refs: ["Lei 9.478/1997", "Contratos de Concessão ANP"],
    corporate_internal: false,
    gpp_role: "regulatory_obligation",
  },
  {
    id: "pad",
    module: "data/gestao-projetos-parcerias.json#GPP013",
    evidence_refs: ["Resolução ANP 47/2014", "Resolução ANP 845/2021"],
    corporate_internal: false,
    gpp_role: "regulatory_doc",
    triggers_state: "area-em-pad-state",
  },
  {
    id: "declaracao-comercialidade",
    module: "data/gestao-projetos-parcerias.json#GPP014",
    evidence_refs: ["Lei 9.478/1997"],
    corporate_internal: false,
    gpp_role: "regulatory_event",
    triggers_state: "campo-em-desenvolvimento-state",
  },
];

export const GPP_GLOSSARY = [
  {
    id: "bloco-anchor",
    termo: "Bloco — entidade-âncora regulatória + técnica + decisória",
    categoria: "regulatorio",
    definicao:
      "Unidade primária de concessão/partilha. Ancora simultaneamente conceitos regulatórios (contrato E&P), técnicos (poços, projetos exploratórios) e decisórios (portfólio, ranking, devolução). É objeto regulatório, técnico e decisório simultaneamente — fonte de muitas ambiguidades quando o termo 'Bloco' é usado para significar estado, área, contrato ou campo.",
    fonte: "Lei nº 9.478/1997; Curso PROPEX 2024/2025",
    apareceEm: [
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
    ],
  },
  {
    id: "propex",
    termo: "PROPEX — Programa Exploratório (Petrobras)",
    categoria: "governanca_corporativa",
    definicao:
      "Programa corporativo Petrobras de governança de projetos exploratórios em Blocos. Estrutura PEXPs, PGPs, TEPs e fóruns COMEXP/GRBLOC. CRÍTICO: PROPEX é Programa, não projeto — Projetos Exploratórios são entidades distintas governadas por ele.",
    fonte: "Curso PROPEX 2024/2025; PE-2EXP-PROPEX",
    apareceEm: [],
  },
  {
    id: "pad-doc",
    termo: "PAD — Plano de Avaliação de Descoberta",
    categoria: "regulatorio",
    definicao:
      "Documento submetido à ANP para avaliar comercialidade de descoberta no Bloco. Disparado após Notificação de Descoberta. Tem PGP próprio. Pode incluir TLD. Base para decisão de Declaração de Comercialidade.",
    fonte: "Resolução ANP nº 47/2014",
    apareceEm: ["pads-andamento", "pads-concluidos"],
  },
  {
    id: "dc-anp",
    termo: "DC — Declaração de Comercialidade",
    categoria: "regulatorio",
    definicao:
      "Ato regulatório que declara descoberta como comercial. Encerra fase exploratória, transforma área do Bloco em Campo, dispara obrigação de PD em até 180 dias.",
    fonte: "Lei nº 9.478/1997",
    apareceEm: ["declaracoes-comercialidade"],
  },
  {
    id: "pd-pdp",
    termo: "PD/PDP — Plano de Desenvolvimento (da Produção)",
    categoria: "regulatorio",
    definicao:
      "Documento técnico-regulatório entregue em até 180 dias após DC. Agrupa info técnica/operacional/econômica/ambiental da explotação, incluindo abandono. ANP analisa em até 180 dias. Em jazidas compartilhadas, acompanha AIP ou CIP.",
    fonte: "Resolução ANP nº 17/2015",
    apareceEm: ["declaracoes-comercialidade"],
  },
  {
    id: "wi",
    termo: "WI — Working Interest (Participação)",
    categoria: "gestao_portfolio",
    definicao:
      "Percentual de sócio nos custos e receitas de Bloco/Campo. Soma 100% entre todos os sócios. Determina peso decisório em comitês operacionais e alocação de CAPEX/OPEX.",
    fonte: "SPE Reserves Definitions; Contratos de Concessão ANP",
    apareceEm: [],
  },
];
