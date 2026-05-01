// Geolytics Dictionary — Neo4j relationship import
// Generated: 2026-05-01T12:08:19.625Z
// Run AFTER nodes.cypher
// Run with: cypher-shell -u neo4j -p <password> --file build/neo4j/relationships.cypher
MATCH (n_poco {id: 'poco'}), (n_bloco {id: 'bloco'})
MERGE (n_poco)-[:DRILLED_IN {label_pt: 'perfurado em', label_en: 'drilled in', style: 'solid'}]->(n_bloco)

MATCH (n_poco {id: 'poco'}), (n_ambiente {id: 'ambiente'})
MERGE (n_poco)-[:CLASSIFIED_BY {label_pt: 'classificado por', label_en: 'classified by', style: 'dashed'}]->(n_ambiente)

MATCH (n_poco {id: 'poco'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_poco)-[:LOCATED_IN {label_pt: 'localizado em', label_en: 'located in', style: 'solid'}]->(n_bacia_sedimentar)

MATCH (n_poco {id: 'poco'}), (n_operador {id: 'operador'})
MERGE (n_poco)-[:OPERATED_BY {label_pt: 'operado por', label_en: 'operated by', style: 'solid'}]->(n_operador)

MATCH (n_poco {id: 'poco'}), (n_notificacao_descoberta {id: 'notificacao-descoberta'})
MERGE (n_poco)-[:MAY_REGISTER {label_pt: 'pode registrar', label_en: 'may register', style: 'dashed'}]->(n_notificacao_descoberta)

MATCH (n_poco {id: 'poco'}), (n_presal {id: 'presal'})
MERGE (n_poco)-[:MAY_REACH {label_pt: 'pode atingir', label_en: 'may reach', style: 'dashed'}]->(n_presal)

MATCH (n_poco {id: 'poco'}), (n_formacao {id: 'formacao'})
MERGE (n_poco)-[:TRAVERSES {label_pt: 'atravessa', label_en: 'traverses', style: 'dashed'}]->(n_formacao)

MATCH (n_bloco {id: 'bloco'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_bloco)-[:DELIMITED_IN {label_pt: 'delimitado em', label_en: 'delimited in', style: 'solid'}]->(n_bacia_sedimentar)

MATCH (n_bloco {id: 'bloco'}), (n_contrato_ep {id: 'contrato-ep'})
MERGE (n_bloco)-[:GOVERNED_BY {label_pt: 'regido por', label_en: 'governed by', style: 'solid'}]->(n_contrato_ep)

MATCH (n_bloco {id: 'bloco'}), (n_operador {id: 'operador'})
MERGE (n_bloco)-[:OPERATED_BY {label_pt: 'operado por', label_en: 'operated by', style: 'solid'}]->(n_operador)

MATCH (n_bloco {id: 'bloco'}), (n_pad {id: 'pad'})
MERGE (n_bloco)-[:MAY_HAVE {label_pt: 'pode ter', label_en: 'may have', style: 'dashed'}]->(n_pad)

MATCH (n_bloco {id: 'bloco'}), (n_rodada_licitacao {id: 'rodada-licitacao'})
MERGE (n_bloco)-[:ORIGINATED_IN {label_pt: 'originado em', label_en: 'originated in', style: 'solid'}]->(n_rodada_licitacao)

MATCH (n_bloco {id: 'bloco'}), (n_ambiente {id: 'ambiente'})
MERGE (n_bloco)-[:CLASSIFIED_BY {label_pt: 'classificado por', label_en: 'classified by', style: 'dashed'}]->(n_ambiente)

MATCH (n_contrato_ep {id: 'contrato-ep'}), (n_anp {id: 'anp'})
MERGE (n_contrato_ep)-[:SIGNED_WITH {label_pt: 'celebrado com', label_en: 'signed with', style: 'solid'}]->(n_anp)

MATCH (n_contrato_ep {id: 'contrato-ep'}), (n_regime_contratual {id: 'regime-contratual'})
MERGE (n_contrato_ep)-[:DEFINES {label_pt: 'define', label_en: 'defines', style: 'solid'}]->(n_regime_contratual)

MATCH (n_contrato_ep {id: 'contrato-ep'}), (n_periodo_exploratorio {id: 'periodo-exploratorio'})
MERGE (n_contrato_ep)-[:ORGANIZED_IN {label_pt: 'organizado em', label_en: 'organized in', style: 'solid'}]->(n_periodo_exploratorio)

MATCH (n_contrato_ep {id: 'contrato-ep'}), (n_uts {id: 'uts'})
MERGE (n_contrato_ep)-[:MEASURED_VIA {label_pt: 'mede via', label_en: 'measured via', style: 'solid'}]->(n_uts)

MATCH (n_pad {id: 'pad'}), (n_bloco {id: 'bloco'})
MERGE (n_pad)-[:EVALUATES {label_pt: 'avalia', label_en: 'evaluates', style: 'solid'}]->(n_bloco)

MATCH (n_pad {id: 'pad'}), (n_declaracao_comercialidade {id: 'declaracao-comercialidade'})
MERGE (n_pad)-[:MAY_YIELD {label_pt: 'pode gerar', label_en: 'may yield', style: 'dashed'}]->(n_declaracao_comercialidade)

MATCH (n_declaracao_comercialidade {id: 'declaracao-comercialidade'}), (n_area_desenvolvimento {id: 'area-desenvolvimento'})
MERGE (n_declaracao_comercialidade)-[:INITIATES {label_pt: 'dá início a', label_en: 'initiates', style: 'solid'}]->(n_area_desenvolvimento)

MATCH (n_area_desenvolvimento {id: 'area-desenvolvimento'}), (n_plano_desenvolvimento {id: 'plano-desenvolvimento'})
MERGE (n_area_desenvolvimento)-[:REQUIRES {label_pt: 'exige', label_en: 'requires', style: 'solid'}]->(n_plano_desenvolvimento)

MATCH (n_area_desenvolvimento {id: 'area-desenvolvimento'}), (n_primeiro_oleo {id: 'primeiro-oleo'})
MERGE (n_area_desenvolvimento)-[:ENDS_WITH {label_pt: 'encerrada pelo', label_en: 'ends with', style: 'dashed'}]->(n_primeiro_oleo)

MATCH (n_primeiro_oleo {id: 'primeiro-oleo'}), (n_campo {id: 'campo'})
MERGE (n_primeiro_oleo)-[:INAUGURATES {label_pt: 'inaugura', label_en: 'inaugurates', style: 'solid'}]->(n_campo)

MATCH (n_declaracao_comercialidade {id: 'declaracao-comercialidade'}), (n_campo {id: 'campo'})
MERGE (n_declaracao_comercialidade)-[:ORIGINATES {label_pt: 'origina', label_en: 'originates', style: 'solid'}]->(n_campo)

MATCH (n_campo {id: 'campo'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_campo)-[:LOCATED_IN {label_pt: 'localizado em', label_en: 'located in', style: 'solid'}]->(n_bacia_sedimentar)

MATCH (n_campo {id: 'campo'}), (n_ambiente {id: 'ambiente'})
MERGE (n_campo)-[:CLASSIFIED_BY {label_pt: 'classificado por', label_en: 'classified by', style: 'dashed'}]->(n_ambiente)

MATCH (n_campo {id: 'campo'}), (n_reservatorio {id: 'reservatorio'})
MERGE (n_campo)-[:SUSTAINED_BY {label_pt: 'sustentado por', label_en: 'sustained by', style: 'solid'}]->(n_reservatorio)

MATCH (n_reservatorio {id: 'reservatorio'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_reservatorio)-[:CONTAINED_IN {label_pt: 'contido em', label_en: 'contained in', style: 'solid'}]->(n_bacia_sedimentar)

MATCH (n_reservatorio {id: 'reservatorio'}), (n_sistema_deposicional {id: 'sistema-deposicional'})
MERGE (n_reservatorio)-[:CHARACTERIZED_BY {label_pt: 'caracterizado por', label_en: 'characterized by', style: 'solid'}]->(n_sistema_deposicional)

MATCH (n_reservatorio {id: 'reservatorio'}), (n_formacao {id: 'formacao'})
MERGE (n_reservatorio)-[:HOSTED_IN {label_pt: 'hospedado em', label_en: 'hosted in', style: 'solid'}]->(n_formacao)

MATCH (n_operador {id: 'operador'}), (n_processo_sancionador {id: 'processo-sancionador'})
MERGE (n_operador)-[:MAY_HAVE {label_pt: 'pode ter', label_en: 'may have', style: 'dashed'}]->(n_processo_sancionador)

MATCH (n_anp {id: 'anp'}), (n_sigep {id: 'sigep'})
MERGE (n_anp)-[:MANAGES_VIA {label_pt: 'gerencia via', label_en: 'manages via', style: 'solid'}]->(n_sigep)

MATCH (n_anp {id: 'anp'}), (n_sep {id: 'sep'})
MERGE (n_anp)-[:OVERSEES_VIA {label_pt: 'fiscaliza via', label_en: 'oversees via', style: 'solid'}]->(n_sep)

MATCH (n_bacias_agrupadas {id: 'bacias-agrupadas'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_bacias_agrupadas)-[:CLASSIFIES {label_pt: 'classifica (ANP)', label_en: 'classifies', style: 'dashed'}]->(n_bacia_sedimentar)

MATCH (n_bop {id: 'bop'}), (n_poco {id: 'poco'})
MERGE (n_bop)-[:INSTALLED_ON {label_pt: 'instalado em', label_en: 'installed on', style: 'solid'}]->(n_poco)

MATCH (n_dhsv {id: 'dhsv'}), (n_poco {id: 'poco'})
MERGE (n_dhsv)-[:INSTALLED_IN {label_pt: 'instalado em', label_en: 'installed in', style: 'solid'}]->(n_poco)

MATCH (n_anm_eq {id: 'anm-eq'}), (n_poco {id: 'poco'})
MERGE (n_anm_eq)-[:CONTROLS {label_pt: 'controla', label_en: 'controls', style: 'solid'}]->(n_poco)

MATCH (n_bha {id: 'bha'}), (n_poco {id: 'poco'})
MERGE (n_bha)-[:COMPOSES {label_pt: 'compõe coluna', label_en: 'composes', style: 'dashed'}]->(n_poco)

MATCH (n_esp_eq {id: 'esp-eq'}), (n_poco {id: 'poco'})
MERGE (n_esp_eq)-[:LIFTS_FROM {label_pt: 'eleva fluido em', label_en: 'lifts from', style: 'dashed'}]->(n_poco)

MATCH (n_mwd {id: 'mwd'}), (n_poco {id: 'poco'})
MERGE (n_mwd)-[:MEASURES {label_pt: 'mede em', label_en: 'measures', style: 'dashed'}]->(n_poco)

MATCH (n_lwd {id: 'lwd'}), (n_poco {id: 'poco'})
MERGE (n_lwd)-[:LOGS {label_pt: 'perfila', label_en: 'logs', style: 'dashed'}]->(n_poco)

MATCH (n_fpso {id: 'fpso'}), (n_campo {id: 'campo'})
MERGE (n_fpso)-[:PRODUCES_AT {label_pt: 'produz em', label_en: 'produces at', style: 'solid'}]->(n_campo)

MATCH (n_riser {id: 'riser'}), (n_anm_eq {id: 'anm-eq'})
MERGE (n_riser)-[:CONNECTS {label_pt: 'conecta', label_en: 'connects', style: 'solid'}]->(n_anm_eq)

MATCH (n_riser {id: 'riser'}), (n_fpso {id: 'fpso'})
MERGE (n_riser)-[:CONNECTS {label_pt: 'conecta', label_en: 'connects', style: 'solid'}]->(n_fpso)

MATCH (n_rov {id: 'rov'}), (n_anm_eq {id: 'anm-eq'})
MERGE (n_rov)-[:OPERATES {label_pt: 'opera', label_en: 'operates', style: 'dashed'}]->(n_anm_eq)

MATCH (n_manifold_submarino {id: 'manifold-submarino'}), (n_poco {id: 'poco'})
MERGE (n_manifold_submarino)-[:GATHERS_FROM {label_pt: 'agrega fluxo de', label_en: 'gathers from', style: 'dashed'}]->(n_poco)

MATCH (n_manifold_submarino {id: 'manifold-submarino'}), (n_fpso {id: 'fpso'})
MERGE (n_manifold_submarino)-[:FEEDS {label_pt: 'alimenta', label_en: 'feeds', style: 'solid'}]->(n_fpso)

MATCH (n_ibama {id: 'ibama'}), (n_operador {id: 'operador'})
MERGE (n_ibama)-[:OVERSEES_ENVIRONMENT_OF {label_pt: 'fiscaliza ambientalmente', label_en: 'oversees environment of', style: 'solid'}]->(n_operador)

MATCH (n_ibama {id: 'ibama'}), (n_eia {id: 'eia'})
MERGE (n_ibama)-[:REQUIRES {label_pt: 'exige', label_en: 'requires', style: 'solid'}]->(n_eia)

MATCH (n_ibama {id: 'ibama'}), (n_rima {id: 'rima'})
MERGE (n_ibama)-[:REQUIRES {label_pt: 'exige', label_en: 'requires', style: 'solid'}]->(n_rima)

MATCH (n_conama {id: 'conama'}), (n_ibama {id: 'ibama'})
MERGE (n_conama)-[:GUIDES {label_pt: 'orienta normativamente', label_en: 'guides', style: 'solid'}]->(n_ibama)

MATCH (n_ana_agencia {id: 'ana-agencia'}), (n_operador {id: 'operador'})
MERGE (n_ana_agencia)-[:REGULATES_WATER_USE_OF {label_pt: 'regula uso de água', label_en: 'regulates water use of', style: 'dashed'}]->(n_operador)

MATCH (n_ibp {id: 'ibp'}), (n_operador {id: 'operador'})
MERGE (n_ibp)-[:REPRESENTS {label_pt: 'representa', label_en: 'represents', style: 'solid'}]->(n_operador)

MATCH (n_bndes {id: 'bndes'}), (n_bloco {id: 'bloco'})
MERGE (n_bndes)-[:FINANCES {label_pt: 'financia', label_en: 'finances', style: 'dashed'}]->(n_bloco)

MATCH (n_afe {id: 'afe'}), (n_poco {id: 'poco'})
MERGE (n_afe)-[:AUTHORIZES_SPENDING_FOR {label_pt: 'autoriza gasto em', label_en: 'authorizes spending for', style: 'solid'}]->(n_poco)

MATCH (n_joa {id: 'joa'}), (n_contrato_ep {id: 'contrato-ep'})
MERGE (n_joa)-[:COMPLEMENTS {label_pt: 'complementa', label_en: 'complements', style: 'solid'}]->(n_contrato_ep)

MATCH (n_epc {id: 'epc'}), (n_fpso {id: 'fpso'})
MERGE (n_epc)-[:DELIVERS {label_pt: 'entrega', label_en: 'delivers', style: 'dashed'}]->(n_fpso)

MATCH (n_rocha_geradora {id: 'rocha-geradora'}), (n_materia_organica {id: 'materia-organica'})
MERGE (n_rocha_geradora)-[:CONTAINS {label_pt: 'contém', label_en: 'contains', style: 'solid'}]->(n_materia_organica)

MATCH (n_rocha_geradora {id: 'rocha-geradora'}), (n_sistema_petrolifero {id: 'sistema-petrolifero'})
MERGE (n_rocha_geradora)-[:FEEDS {label_pt: 'alimenta', label_en: 'feeds', style: 'solid'}]->(n_sistema_petrolifero)

MATCH (n_maturidade_termal {id: 'maturidade-termal'}), (n_rocha_geradora {id: 'rocha-geradora'})
MERGE (n_maturidade_termal)-[:CHARACTERIZES {label_pt: 'caracteriza', label_en: 'characterizes', style: 'solid'}]->(n_rocha_geradora)

MATCH (n_rocha_capacitante {id: 'rocha-capacitante'}), (n_reservatorio {id: 'reservatorio'})
MERGE (n_rocha_capacitante)-[:SEALS {label_pt: 'sela', label_en: 'seals', style: 'solid'}]->(n_reservatorio)

MATCH (n_trapa {id: 'trapa'}), (n_reservatorio {id: 'reservatorio'})
MERGE (n_trapa)-[:COMPRISES {label_pt: 'comporta', label_en: 'comprises', style: 'solid'}]->(n_reservatorio)

MATCH (n_trapa {id: 'trapa'}), (n_acumulacao {id: 'acumulacao'})
MERGE (n_trapa)-[:CONTAINS {label_pt: 'contém', label_en: 'contains', style: 'solid'}]->(n_acumulacao)

MATCH (n_sistema_petrolifero {id: 'sistema-petrolifero'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_sistema_petrolifero)-[:INTEGRATES_TO {label_pt: 'integra-se a', label_en: 'integrates to', style: 'solid'}]->(n_bacia_sedimentar)

MATCH (n_acumulacao {id: 'acumulacao'}), (n_campo {id: 'campo'})
MERGE (n_acumulacao)-[:BECOMES {label_pt: 'origina', label_en: 'becomes', style: 'solid'}]->(n_campo)

MATCH (n_campo {id: 'campo'}), (n_reserva {id: 'reserva'})
MERGE (n_campo)-[:DECLARES {label_pt: 'declara', label_en: 'declares', style: 'dashed'}]->(n_reserva)

MATCH (n_reserva {id: 'reserva'}), (n_recurso {id: 'recurso'})
MERGE (n_reserva)-[:DERIVED_FROM {label_pt: 'deriva de', label_en: 'derived from', style: 'solid'}]->(n_recurso)

MATCH (n_play {id: 'play'}), (n_prospecto {id: 'prospecto'})
MERGE (n_play)-[:SPAWNS {label_pt: 'gera', label_en: 'spawns', style: 'dashed'}]->(n_prospecto)

MATCH (n_prospecto {id: 'prospecto'}), (n_acumulacao {id: 'acumulacao'})
MERGE (n_prospecto)-[:BECOMES {label_pt: 'pode tornar-se', label_en: 'becomes', style: 'dashed'}]->(n_acumulacao)

MATCH (n_falha {id: 'falha'}), (n_trapa {id: 'trapa'})
MERGE (n_falha)-[:FORMS {label_pt: 'compõe', label_en: 'forms', style: 'dashed'}]->(n_trapa)

MATCH (n_falha {id: 'falha'}), (n_potencial_selante {id: 'potencial-selante'})
MERGE (n_falha)-[:HAS_PROPERTY {label_pt: 'tem propriedade', label_en: 'has property', style: 'solid'}]->(n_potencial_selante)

MATCH (n_formacao {id: 'formacao'}), (n_idade_geologica {id: 'idade-geologica'})
MERGE (n_formacao)-[:HAS_AGE {label_pt: 'tem idade', label_en: 'has age', style: 'solid'}]->(n_idade_geologica)

MATCH (n_poco {id: 'poco'}), (n_intervalo_estratigrafico {id: 'intervalo-estratigrafico'})
MERGE (n_poco)-[:SAMPLES {label_pt: 'amostra', label_en: 'samples', style: 'dashed'}]->(n_intervalo_estratigrafico)

MATCH (n_testemunho {id: 'testemunho'}), (n_formacao {id: 'formacao'})
MERGE (n_testemunho)-[:SAMPLES {label_pt: 'amostra', label_en: 'samples', style: 'solid'}]->(n_formacao)

MATCH (n_perfil_poco {id: 'perfil-poco'}), (n_poco {id: 'poco'})
MERGE (n_perfil_poco)-[:MEASURES {label_pt: 'mede', label_en: 'measures', style: 'solid'}]->(n_poco)

MATCH (n_perfil_poco {id: 'perfil-poco'}), (n_litologia {id: 'litologia'})
MERGE (n_perfil_poco)-[:INFERS {label_pt: 'infere', label_en: 'infers', style: 'dashed'}]->(n_litologia)

MATCH (n_biomarcador {id: 'biomarcador'}), (n_correlacao_oleo_rocha {id: 'correlacao-oleo-rocha'})
MERGE (n_biomarcador)-[:ENABLES {label_pt: 'permite', label_en: 'enables', style: 'solid'}]->(n_correlacao_oleo_rocha)

MATCH (n_gc_ms {id: 'gc-ms'}), (n_biomarcador {id: 'biomarcador'})
MERGE (n_gc_ms)-[:DETECTS {label_pt: 'detecta', label_en: 'detects', style: 'solid'}]->(n_biomarcador)

MATCH (n_amostra_fluido {id: 'amostra-fluido'}), (n_pvt {id: 'pvt'})
MERGE (n_amostra_fluido)-[:UNDERGOES {label_pt: 'submetida a', label_en: 'undergoes', style: 'dashed'}]->(n_pvt)

MATCH (n_amostra_fluido {id: 'amostra-fluido'}), (n_sara {id: 'sara'})
MERGE (n_amostra_fluido)-[:UNDERGOES {label_pt: 'submetida a', label_en: 'undergoes', style: 'dashed'}]->(n_sara)

MATCH (n_pvt {id: 'pvt'}), (n_classe_fluido {id: 'classe-fluido'})
MERGE (n_pvt)-[:CLASSIFIES {label_pt: 'classifica', label_en: 'classifies', style: 'solid'}]->(n_classe_fluido)

MATCH (n_modelo_petrofisico {id: 'modelo-petrofisico'}), (n_reservatorio {id: 'reservatorio'})
MERGE (n_modelo_petrofisico)-[:CHARACTERIZES {label_pt: 'caracteriza', label_en: 'characterizes', style: 'solid'}]->(n_reservatorio)

MATCH (n_facies_sedimentar {id: 'facies-sedimentar'}), (n_reservatorio {id: 'reservatorio'})
MERGE (n_facies_sedimentar)-[:COMPOSES {label_pt: 'compõe', label_en: 'composes', style: 'solid'}]->(n_reservatorio)

MATCH (n_campo_tensional {id: 'campo-tensional'}), (n_janela_lama {id: 'janela-lama'})
MERGE (n_campo_tensional)-[:DEFINES {label_pt: 'define', label_en: 'defines', style: 'solid'}]->(n_janela_lama)

MATCH (n_janela_lama {id: 'janela-lama'}), (n_poco {id: 'poco'})
MERGE (n_janela_lama)-[:GUIDES_DRILLING_OF {label_pt: 'guia perfuração de', label_en: 'guides drilling of', style: 'solid'}]->(n_poco)

MATCH (n_ocorrencia_geomec {id: 'ocorrencia-geomec'}), (n_poco {id: 'poco'})
MERGE (n_ocorrencia_geomec)-[:OCCURS_IN {label_pt: 'ocorre em', label_en: 'occurs in', style: 'dashed'}]->(n_poco)

MATCH (n_recurso {id: 'recurso'}), (n_bloco {id: 'bloco'})
MERGE (n_recurso)-[:ALLOCATED_TO {label_pt: 'alocado em', label_en: 'allocated to', style: 'dashed'}]->(n_bloco)

MATCH (n_operador {id: 'operador'}), (n_recurso {id: 'recurso'})
MERGE (n_operador)-[:REPORTS {label_pt: 'reporta', label_en: 'reports', style: 'solid'}]->(n_recurso)

MATCH (n_poco {id: 'poco'}), (n_wellbore {id: 'wellbore'})
MERGE (n_poco)-[:HAS_WELLBORE {label_pt: 'tem wellbore', label_en: 'has wellbore', style: 'solid'}]->(n_wellbore)

MATCH (n_wellbore {id: 'wellbore'}), (n_poco {id: 'poco'})
MERGE (n_wellbore)-[:BELONGS_TO {label_pt: 'pertence a', label_en: 'belongs to', style: 'solid'}]->(n_poco)

MATCH (n_wellbore {id: 'wellbore'}), (n_completacao {id: 'completacao'})
MERGE (n_wellbore)-[:HAS_COMPLETION {label_pt: 'tem completação', label_en: 'has completion', style: 'solid'}]->(n_completacao)

MATCH (n_completacao {id: 'completacao'}), (n_dhsv {id: 'dhsv'})
MERGE (n_completacao)-[:CONTAINS {label_pt: 'contém', label_en: 'contains', style: 'dashed'}]->(n_dhsv)

MATCH (n_completacao {id: 'completacao'}), (n_campo {id: 'campo'})
MERGE (n_completacao)-[:ENABLES {label_pt: 'viabiliza', label_en: 'enables', style: 'dashed'}]->(n_campo)

MATCH (n_wellbore {id: 'wellbore'}), (n_formacao {id: 'formacao'})
MERGE (n_wellbore)-[:PENETRATES {label_pt: 'penetra', label_en: 'penetrates', style: 'dashed'}]->(n_formacao)

MATCH (n_wellbore {id: 'wellbore'}), (n_trajetoria_poco {id: 'trajetoria-poco'})
MERGE (n_wellbore)-[:HAS_TRAJECTORY {label_pt: 'tem trajetória', label_en: 'has trajectory', style: 'dashed'}]->(n_trajetoria_poco)

MATCH (n_wellbore {id: 'wellbore'}), (n_topo_formacional {id: 'topo-formacional'})
MERGE (n_wellbore)-[:HAS_MARKER {label_pt: 'tem marker', label_en: 'has marker', style: 'dashed'}]->(n_topo_formacional)

MATCH (n_formacao {id: 'formacao'}), (n_topo_formacional {id: 'topo-formacional'})
MERGE (n_formacao)-[:HAS_TOP_AT {label_pt: 'tem topo em', label_en: 'has top at', style: 'solid'}]->(n_topo_formacional)

MATCH (n_perfil_poco {id: 'perfil-poco'}), (n_wellbore {id: 'wellbore'})
MERGE (n_perfil_poco)-[:MEASURED_IN {label_pt: 'medida em', label_en: 'measured in', style: 'solid'}]->(n_wellbore)

MATCH (n_activity_plan {id: 'activity-plan'}), (n_poco {id: 'poco'})
MERGE (n_activity_plan)-[:PLANS_ACTIVITY_FOR {label_pt: 'planeja atividade em', label_en: 'plans activity for', style: 'dashed'}]->(n_poco)

MATCH (n_activity_plan {id: 'activity-plan'}), (n_activity_template {id: 'activity-template'})
MERGE (n_activity_plan)-[:COMPOSED_OF {label_pt: 'composto por', label_en: 'composed of', style: 'solid'}]->(n_activity_template)

MATCH (n_well_activity_program {id: 'well-activity-program'}), (n_poco {id: 'poco'})
MERGE (n_well_activity_program)-[:GOVERNS {label_pt: 'governa programa de', label_en: 'governs', style: 'solid'}]->(n_poco)

MATCH (n_well_activity_program {id: 'well-activity-program'}), (n_well_activity_phase_type {id: 'well-activity-phase-type'})
MERGE (n_well_activity_program)-[:HAS_PHASE {label_pt: 'tem fase', label_en: 'has phase', style: 'dashed'}]->(n_well_activity_phase_type)

MATCH (n_well_activity_program {id: 'well-activity-program'}), (n_drilling_activity {id: 'drilling-activity'})
MERGE (n_well_activity_program)-[:REALIZED_BY {label_pt: 'realizado por', label_en: 'realized by', style: 'solid'}]->(n_drilling_activity)

MATCH (n_drilling_activity {id: 'drilling-activity'}), (n_poco {id: 'poco'})
MERGE (n_drilling_activity)-[:PERFORMED_ON {label_pt: 'executada em', label_en: 'performed on', style: 'solid'}]->(n_poco)

MATCH (n_drilling_activity {id: 'drilling-activity'}), (n_drilling_reason_type {id: 'drilling-reason-type'})
MERGE (n_drilling_activity)-[:CLASSIFIED_BY {label_pt: 'classificada por', label_en: 'classified by', style: 'dashed'}]->(n_drilling_reason_type)

MATCH (n_drilling_parameters {id: 'drilling-parameters'}), (n_bha {id: 'bha'})
MERGE (n_drilling_parameters)-[:MEASURED_FOR {label_pt: 'medido para', label_en: 'measured for', style: 'solid'}]->(n_bha)

MATCH (n_mud_pump {id: 'mud-pump'}), (n_drilling_activity {id: 'drilling-activity'})
MERGE (n_mud_pump)-[:USED_IN {label_pt: 'usado em', label_en: 'used in', style: 'dashed'}]->(n_drilling_activity)

MATCH (n_wellbore_architecture {id: 'wellbore-architecture'}), (n_wellbore {id: 'wellbore'})
MERGE (n_wellbore_architecture)-[:DESCRIBES_STRUCTURE_OF {label_pt: 'descreve estrutura de', label_en: 'describes structure of', style: 'solid'}]->(n_wellbore)

MATCH (n_casing_design {id: 'casing-design'}), (n_wellbore_architecture {id: 'wellbore-architecture'})
MERGE (n_casing_design)-[:PART_OF {label_pt: 'parte de', label_en: 'part of', style: 'solid'}]->(n_wellbore_architecture)

MATCH (n_cementing_fluid {id: 'cementing-fluid'}), (n_casing_design {id: 'casing-design'})
MERGE (n_cementing_fluid)-[:USED_IN {label_pt: 'usado em', label_en: 'used in', style: 'dashed'}]->(n_casing_design)

MATCH (n_wellbore_trajectory {id: 'wellbore-trajectory'}), (n_wellbore {id: 'wellbore'})
MERGE (n_wellbore_trajectory)-[:POSITIONS {label_pt: 'posiciona', label_en: 'positions', style: 'solid'}]->(n_wellbore)

MATCH (n_wellbore_marker_set {id: 'wellbore-marker-set'}), (n_wellbore {id: 'wellbore'})
MERGE (n_wellbore_marker_set)-[:IDENTIFIES_IN {label_pt: 'identifica em', label_en: 'identifies in', style: 'solid'}]->(n_wellbore)

MATCH (n_wellbore_marker_set {id: 'wellbore-marker-set'}), (n_topo_formacional {id: 'topo-formacional'})
MERGE (n_wellbore_marker_set)-[:SPECIALIZES {label_pt: 'especializa', label_en: 'specializes', style: 'dashed'}]->(n_topo_formacional)

MATCH (n_wellbore_marker_set {id: 'wellbore-marker-set'}), (n_intervalo_estratigrafico {id: 'intervalo-estratigrafico'})
MERGE (n_wellbore_marker_set)-[:MAPS_TO {label_pt: 'mapeia para', label_en: 'maps to', style: 'dashed'}]->(n_intervalo_estratigrafico)

MATCH (n_core_sample {id: 'core-sample'}), (n_testemunho {id: 'testemunho'})
MERGE (n_core_sample)-[:ALIGNS_WITH {label_pt: 'alinha-se com', label_en: 'aligns with', style: 'dashed'}]->(n_testemunho)

MATCH (n_log_curve_type {id: 'log-curve-type'}), (n_perfil_poco {id: 'perfil-poco'})
MERGE (n_log_curve_type)-[:CLASSIFIES_CURVE_IN {label_pt: 'classifica curva de', label_en: 'classifies curve in', style: 'dashed'}]->(n_perfil_poco)

MATCH (n_seismic_acquisition_survey {id: 'seismic-acquisition-survey'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_seismic_acquisition_survey)-[:COVERS {label_pt: 'cobre', label_en: 'covers', style: 'dashed'}]->(n_bacia_sedimentar)

MATCH (n_seismic_processing_project {id: 'seismic-processing-project'}), (n_seismic_acquisition_survey {id: 'seismic-acquisition-survey'})
MERGE (n_seismic_processing_project)-[:PROCESSES {label_pt: 'processa dados de', label_en: 'processes', style: 'solid'}]->(n_seismic_acquisition_survey)

MATCH (n_seismic_horizon {id: 'seismic-horizon'}), (n_seismic_processing_project {id: 'seismic-processing-project'})
MERGE (n_seismic_horizon)-[:OUTPUT_OF {label_pt: 'saída de', label_en: 'output of', style: 'solid'}]->(n_seismic_processing_project)

MATCH (n_seismic_horizon {id: 'seismic-horizon'}), (n_topo_formacional {id: 'topo-formacional'})
MERGE (n_seismic_horizon)-[:CORRELATES_WITH {label_pt: 'correlaciona com', label_en: 'correlates with', style: 'dashed'}]->(n_topo_formacional)

MATCH (n_basin_type {id: 'basin-type'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_basin_type)-[:CLASSIFIES {label_pt: 'classifica', label_en: 'classifies', style: 'dashed'}]->(n_bacia_sedimentar)

MATCH (n_bottom_hole_pressure_type {id: 'bottom-hole-pressure-type'}), (n_pvt {id: 'pvt'})
MERGE (n_bottom_hole_pressure_type)-[:MEASUREMENT_FOR {label_pt: 'medição para', label_en: 'measurement for', style: 'dashed'}]->(n_pvt)

MATCH (n_annular_fluid_type {id: 'annular-fluid-type'}), (n_janela_lama {id: 'janela-lama'})
MERGE (n_annular_fluid_type)-[:RELATED_TO {label_pt: 'relacionado a', label_en: 'related to', style: 'dashed'}]->(n_janela_lama)

MATCH (n_document_type {id: 'document-type'}), (n_eia {id: 'eia'})
MERGE (n_document_type)-[:CLASSIFIES {label_pt: 'classifica documento de', label_en: 'classifies', style: 'dashed'}]->(n_eia)

MATCH (n_facility_type {id: 'facility-type'}), (n_fpso {id: 'fpso'})
MERGE (n_facility_type)-[:CLASSIFIES {label_pt: 'classifica', label_en: 'classifies', style: 'dashed'}]->(n_fpso)

MATCH (n_geo_political_entity {id: 'geo-political-entity'}), (n_anp {id: 'anp'})
MERGE (n_geo_political_entity)-[:JURISDICTION_OF {label_pt: 'jurisdição de', label_en: 'jurisdiction of', style: 'dashed'}]->(n_anp)

MATCH (n_acl {id: 'acl'}), (n_operador {id: 'operador'})
MERGE (n_acl)-[:RESTRICTS_ACCESS_FOR {label_pt: 'restringe acesso para', label_en: 'restricts access for', style: 'dashed'}]->(n_operador)

MATCH (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'}), (n_bacia_sedimentar {id: 'bacia-sedimentar'})
MERGE (n_ontopetro_class_C001)-[:MAPS_TO_ENTITY]->(n_bacia_sedimentar)

MATCH (n_bacia_sedimentar {id: 'bacia-sedimentar'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_bacia_sedimentar)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'}), (n_formacao {id: 'formacao'})
MERGE (n_ontopetro_class_C002)-[:MAPS_TO_ENTITY]->(n_formacao)

MATCH (n_formacao {id: 'formacao'}), (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'})
MERGE (n_formacao)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C002)

MATCH (n_ontopetro_class_C003 {id: 'ontopetro_class_C003'}), (n_reservatorio {id: 'reservatorio'})
MERGE (n_ontopetro_class_C003)-[:MAPS_TO_ENTITY]->(n_reservatorio)

MATCH (n_reservatorio {id: 'reservatorio'}), (n_ontopetro_class_C003 {id: 'ontopetro_class_C003'})
MERGE (n_reservatorio)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C003)

MATCH (n_ontopetro_class_C004 {id: 'ontopetro_class_C004'}), (n_rocha_capacitante {id: 'rocha-capacitante'})
MERGE (n_ontopetro_class_C004)-[:MAPS_TO_ENTITY]->(n_rocha_capacitante)

MATCH (n_rocha_capacitante {id: 'rocha-capacitante'}), (n_ontopetro_class_C004 {id: 'ontopetro_class_C004'})
MERGE (n_rocha_capacitante)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C004)

MATCH (n_ontopetro_class_C005 {id: 'ontopetro_class_C005'}), (n_rocha_geradora {id: 'rocha-geradora'})
MERGE (n_ontopetro_class_C005)-[:MAPS_TO_ENTITY]->(n_rocha_geradora)

MATCH (n_rocha_geradora {id: 'rocha-geradora'}), (n_ontopetro_class_C005 {id: 'ontopetro_class_C005'})
MERGE (n_rocha_geradora)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C005)

MATCH (n_ontopetro_class_C006 {id: 'ontopetro_class_C006'}), (n_trapa {id: 'trapa'})
MERGE (n_ontopetro_class_C006)-[:MAPS_TO_ENTITY]->(n_trapa)

MATCH (n_trapa {id: 'trapa'}), (n_ontopetro_class_C006 {id: 'ontopetro_class_C006'})
MERGE (n_trapa)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C006)

MATCH (n_ontopetro_class_C007 {id: 'ontopetro_class_C007'}), (n_sistema_petrolifero {id: 'sistema-petrolifero'})
MERGE (n_ontopetro_class_C007)-[:MAPS_TO_ENTITY]->(n_sistema_petrolifero)

MATCH (n_sistema_petrolifero {id: 'sistema-petrolifero'}), (n_ontopetro_class_C007 {id: 'ontopetro_class_C007'})
MERGE (n_sistema_petrolifero)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C007)

MATCH (n_ontopetro_class_C008 {id: 'ontopetro_class_C008'}), (n_acumulacao {id: 'acumulacao'})
MERGE (n_ontopetro_class_C008)-[:MAPS_TO_ENTITY]->(n_acumulacao)

MATCH (n_acumulacao {id: 'acumulacao'}), (n_ontopetro_class_C008 {id: 'ontopetro_class_C008'})
MERGE (n_acumulacao)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C008)

MATCH (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'}), (n_campo {id: 'campo'})
MERGE (n_ontopetro_class_C009)-[:MAPS_TO_ENTITY]->(n_campo)

MATCH (n_campo {id: 'campo'}), (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'})
MERGE (n_campo)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C009)

MATCH (n_ontopetro_class_C010 {id: 'ontopetro_class_C010'}), (n_bloco {id: 'bloco'})
MERGE (n_ontopetro_class_C010)-[:MAPS_TO_ENTITY]->(n_bloco)

MATCH (n_bloco {id: 'bloco'}), (n_ontopetro_class_C010 {id: 'ontopetro_class_C010'})
MERGE (n_bloco)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C010)

MATCH (n_ontopetro_class_C011 {id: 'ontopetro_class_C011'}), (n_poco {id: 'poco'})
MERGE (n_ontopetro_class_C011)-[:MAPS_TO_ENTITY]->(n_poco)

MATCH (n_poco {id: 'poco'}), (n_ontopetro_class_C011 {id: 'ontopetro_class_C011'})
MERGE (n_poco)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C011)

MATCH (n_ontopetro_class_C012 {id: 'ontopetro_class_C012'}), (n_testemunho {id: 'testemunho'})
MERGE (n_ontopetro_class_C012)-[:MAPS_TO_ENTITY]->(n_testemunho)

MATCH (n_testemunho {id: 'testemunho'}), (n_ontopetro_class_C012 {id: 'ontopetro_class_C012'})
MERGE (n_testemunho)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C012)

MATCH (n_ontopetro_class_C013 {id: 'ontopetro_class_C013'}), (n_perfil_poco {id: 'perfil-poco'})
MERGE (n_ontopetro_class_C013)-[:MAPS_TO_ENTITY]->(n_perfil_poco)

MATCH (n_perfil_poco {id: 'perfil-poco'}), (n_ontopetro_class_C013 {id: 'ontopetro_class_C013'})
MERGE (n_perfil_poco)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C013)

MATCH (n_ontopetro_class_C016 {id: 'ontopetro_class_C016'}), (n_falha {id: 'falha'})
MERGE (n_ontopetro_class_C016)-[:MAPS_TO_ENTITY]->(n_falha)

MATCH (n_falha {id: 'falha'}), (n_ontopetro_class_C016 {id: 'ontopetro_class_C016'})
MERGE (n_falha)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C016)

MATCH (n_ontopetro_class_C017 {id: 'ontopetro_class_C017'}), (n_play {id: 'play'})
MERGE (n_ontopetro_class_C017)-[:MAPS_TO_ENTITY]->(n_play)

MATCH (n_play {id: 'play'}), (n_ontopetro_class_C017 {id: 'ontopetro_class_C017'})
MERGE (n_play)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C017)

MATCH (n_ontopetro_class_C018 {id: 'ontopetro_class_C018'}), (n_prospecto {id: 'prospecto'})
MERGE (n_ontopetro_class_C018)-[:MAPS_TO_ENTITY]->(n_prospecto)

MATCH (n_prospecto {id: 'prospecto'}), (n_ontopetro_class_C018 {id: 'ontopetro_class_C018'})
MERGE (n_prospecto)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C018)

MATCH (n_ontopetro_class_C019 {id: 'ontopetro_class_C019'}), (n_recurso {id: 'recurso'})
MERGE (n_ontopetro_class_C019)-[:MAPS_TO_ENTITY]->(n_recurso)

MATCH (n_recurso {id: 'recurso'}), (n_ontopetro_class_C019 {id: 'ontopetro_class_C019'})
MERGE (n_recurso)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C019)

MATCH (n_ontopetro_class_C020 {id: 'ontopetro_class_C020'}), (n_reserva {id: 'reserva'})
MERGE (n_ontopetro_class_C020)-[:MAPS_TO_ENTITY]->(n_reserva)

MATCH (n_reserva {id: 'reserva'}), (n_ontopetro_class_C020 {id: 'ontopetro_class_C020'})
MERGE (n_reserva)-[:HAS_ONTOLOGY_CLASS]->(n_ontopetro_class_C020)

MATCH (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_ontopetro_class_C002)-[:PERTENCEA {cardinality: 'N:1', description: 'Formação pertence a uma bacia sedimentar'}]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'}), (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'})
MERGE (n_ontopetro_class_C001)-[:COMPOSTOPOR {cardinality: '1:N', description: 'Bacia é composta por múltiplas formações'}]->(n_ontopetro_class_C002)

MATCH (n_ontopetro_class_C003 {id: 'ontopetro_class_C003'}), (n_ontopetro_class_C006 {id: 'ontopetro_class_C006'})
MERGE (n_ontopetro_class_C003)-[:CONSTITUI {cardinality: 'N:M', description: 'Rocha reservatório constitui parte da trapa'}]->(n_ontopetro_class_C006)

MATCH (n_ontopetro_class_C004 {id: 'ontopetro_class_C004'}), (n_ontopetro_class_C003 {id: 'ontopetro_class_C003'})
MERGE (n_ontopetro_class_C004)-[:SELARESERVATORIO {cardinality: 'N:M', description: 'Rocha capacitante sela o reservatório'}]->(n_ontopetro_class_C003)

MATCH (n_ontopetro_class_C006 {id: 'ontopetro_class_C006'}), (n_ontopetro_class_C008 {id: 'ontopetro_class_C008'})
MERGE (n_ontopetro_class_C006)-[:CONTEM {cardinality: '1:N', description: 'Trapa contém acumulações'}]->(n_ontopetro_class_C008)

MATCH (n_ontopetro_class_C008 {id: 'ontopetro_class_C008'}), (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'})
MERGE (n_ontopetro_class_C008)-[:FAZPARTEDE {cardinality: 'N:1', description: 'Acumulação faz parte de um campo'}]->(n_ontopetro_class_C009)

MATCH (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_ontopetro_class_C009)-[:LOCALIZADOEM {cardinality: 'N:1', description: 'Campo localizado em bacia'}]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_class_C018 {id: 'ontopetro_class_C018'}), (n_ontopetro_class_C017 {id: 'ontopetro_class_C017'})
MERGE (n_ontopetro_class_C018)-[:ASSOCIADOA {cardinality: 'N:1', description: 'Prospecto associado a play'}]->(n_ontopetro_class_C017)

MATCH (n_ontopetro_class_C011 {id: 'ontopetro_class_C011'}), (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'})
MERGE (n_ontopetro_class_C011)-[:PERFURADOEM {cardinality: 'N:1', description: 'Poço perfurado em campo'}]->(n_ontopetro_class_C009)

MATCH (n_ontopetro_class_C011 {id: 'ontopetro_class_C011'}), (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'})
MERGE (n_ontopetro_class_C011)-[:INTERCEPTA {cardinality: 'N:M', description: 'Poço intercepta formações'}]->(n_ontopetro_class_C002)

MATCH (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'}), (n_ontopetro_class_C012 {id: 'ontopetro_class_C012'})
MERGE (n_ontopetro_class_C002)-[:AMOSTRADOPOR {cardinality: '1:N', description: 'Formação amostrada por testemunhos'}]->(n_ontopetro_class_C012)

MATCH (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'}), (n_ontopetro_class_C013 {id: 'ontopetro_class_C013'})
MERGE (n_ontopetro_class_C002)-[:MEDIDOPOR {cardinality: '1:N', description: 'Formação medida por perfis de poço'}]->(n_ontopetro_class_C013)

MATCH (n_ontopetro_class_C007 {id: 'ontopetro_class_C007'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_ontopetro_class_C007)-[:INTEGRAA {cardinality: 'N:1', description: 'Sistema petrolífero integra-se à bacia'}]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_class_C011 {id: 'ontopetro_class_C011'}), (n_ontopetro_class_C010 {id: 'ontopetro_class_C010'})
MERGE (n_ontopetro_class_C011)-[:LOCALIZADOEMGEO {cardinality: 'N:1', description: 'Poço localizado geograficamente em bloco'}]->(n_ontopetro_class_C010)

MATCH (n_ontopetro_class_C020 {id: 'ontopetro_class_C020'}), (n_ontopetro_class_C019 {id: 'ontopetro_class_C019'})
MERGE (n_ontopetro_class_C020)-[:DERIVADE {cardinality: '1:1', description: 'Reserva deriva de recurso'}]->(n_ontopetro_class_C019)

MATCH (n_ontopetro_inst_I001 {id: 'ontopetro_inst_I001'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_ontopetro_inst_I001)-[:INSTANCE_OF]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_inst_I002 {id: 'ontopetro_inst_I002'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_ontopetro_inst_I002)-[:INSTANCE_OF]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_inst_I003 {id: 'ontopetro_inst_I003'}), (n_ontopetro_class_C001 {id: 'ontopetro_class_C001'})
MERGE (n_ontopetro_inst_I003)-[:INSTANCE_OF]->(n_ontopetro_class_C001)

MATCH (n_ontopetro_inst_I004 {id: 'ontopetro_inst_I004'}), (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'})
MERGE (n_ontopetro_inst_I004)-[:INSTANCE_OF]->(n_ontopetro_class_C002)

MATCH (n_ontopetro_inst_I005 {id: 'ontopetro_inst_I005'}), (n_ontopetro_class_C002 {id: 'ontopetro_class_C002'})
MERGE (n_ontopetro_inst_I005)-[:INSTANCE_OF]->(n_ontopetro_class_C002)

MATCH (n_ontopetro_inst_I006 {id: 'ontopetro_inst_I006'}), (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'})
MERGE (n_ontopetro_inst_I006)-[:INSTANCE_OF]->(n_ontopetro_class_C009)

MATCH (n_ontopetro_inst_I007 {id: 'ontopetro_inst_I007'}), (n_ontopetro_class_C009 {id: 'ontopetro_class_C009'})
MERGE (n_ontopetro_inst_I007)-[:INSTANCE_OF]->(n_ontopetro_class_C009)

MATCH (n_ontopetro_inst_I008 {id: 'ontopetro_inst_I008'}), (n_ontopetro_class_C006 {id: 'ontopetro_class_C006'})
MERGE (n_ontopetro_inst_I008)-[:INSTANCE_OF]->(n_ontopetro_class_C006)

MATCH (n_ontopetro_inst_I009 {id: 'ontopetro_inst_I009'}), (n_ontopetro_class_C017 {id: 'ontopetro_class_C017'})
MERGE (n_ontopetro_inst_I009)-[:INSTANCE_OF]->(n_ontopetro_class_C017)

MATCH (n_ontopetro_inst_I010 {id: 'ontopetro_inst_I010'}), (n_ontopetro_class_C007 {id: 'ontopetro_class_C007'})
MERGE (n_ontopetro_inst_I010)-[:INSTANCE_OF]->(n_ontopetro_class_C007)

MATCH (n_gso_Detachment_Fault {id: 'gso_Detachment_Fault'}), (n_gso_Low_Angle_Normal_Fault {id: 'gso_Low_Angle_Normal_Fault'})
MERGE (n_gso_Detachment_Fault)-[:SUBCLASS_OF]->(n_gso_Low_Angle_Normal_Fault)

MATCH (n_gso_Dextral {id: 'gso_Dextral'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_Dextral)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Dextral_Strike_Slip_Fault {id: 'gso_Dextral_Strike_Slip_Fault'}), (n_gso_Strike_Slip_Fault {id: 'gso_Strike_Slip_Fault'})
MERGE (n_gso_Dextral_Strike_Slip_Fault)-[:SUBCLASS_OF]->(n_gso_Strike_Slip_Fault)

MATCH (n_gso_Dip_Separation {id: 'gso_Dip_Separation'}), (n_gso_Fault_Separation {id: 'gso_Fault_Separation'})
MERGE (n_gso_Dip_Separation)-[:SUBCLASS_OF]->(n_gso_Fault_Separation)

MATCH (n_gso_Dip_Slip {id: 'gso_Dip_Slip'}), (n_gso_Fault_Slip {id: 'gso_Fault_Slip'})
MERGE (n_gso_Dip_Slip)-[:SUBCLASS_OF]->(n_gso_Fault_Slip)

MATCH (n_gso_Ductile_Shear_Zone {id: 'gso_Ductile_Shear_Zone'}), (n_gso_Fault_Zone {id: 'gso_Fault_Zone'})
MERGE (n_gso_Ductile_Shear_Zone)-[:SUBCLASS_OF]->(n_gso_Fault_Zone)

MATCH (n_gso_Extraction {id: 'gso_Extraction'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_Extraction)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Extraction_Fault {id: 'gso_Extraction_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Extraction_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Fault {id: 'gso_Fault'}), (n_gso_Fracture {id: 'gso_Fracture'})
MERGE (n_gso_Fault)-[:SUBCLASS_OF]->(n_gso_Fracture)

MATCH (n_gso_Fault_Movement_Magnitude {id: 'gso_Fault_Movement_Magnitude'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fault_Movement_Magnitude)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fault_Movement_Sense)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fault_Movement_Vector {id: 'gso_Fault_Movement_Vector'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fault_Movement_Vector)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fault_Separation {id: 'gso_Fault_Separation'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fault_Separation)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fault_Slip {id: 'gso_Fault_Slip'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fault_Slip)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fault_Zone {id: 'gso_Fault_Zone'}), (n_gso_Material_Feature {id: 'gso_Material_Feature'})
MERGE (n_gso_Fault_Zone)-[:SUBCLASS_OF]->(n_gso_Material_Feature)

MATCH (n_gso_Generic_Decollement_Fault {id: 'gso_Generic_Decollement_Fault'}), (n_gso_Low_Angle_Fault {id: 'gso_Low_Angle_Fault'})
MERGE (n_gso_Generic_Decollement_Fault)-[:SUBCLASS_OF]->(n_gso_Low_Angle_Fault)

MATCH (n_gso_High_Angle_Fault {id: 'gso_High_Angle_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_High_Angle_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_High_Angle_Normal_Fault {id: 'gso_High_Angle_Normal_Fault'}), (n_gso_High_Angle_Fault {id: 'gso_High_Angle_Fault'})
MERGE (n_gso_High_Angle_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_High_Angle_Fault)

MATCH (n_gso_High_Angle_Normal_Fault {id: 'gso_High_Angle_Normal_Fault'}), (n_gso_Normal_Fault {id: 'gso_Normal_Fault'})
MERGE (n_gso_High_Angle_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_Normal_Fault)

MATCH (n_gso_High_Angle_Reverse_Fault {id: 'gso_High_Angle_Reverse_Fault'}), (n_gso_High_Angle_Fault {id: 'gso_High_Angle_Fault'})
MERGE (n_gso_High_Angle_Reverse_Fault)-[:SUBCLASS_OF]->(n_gso_High_Angle_Fault)

MATCH (n_gso_High_Angle_Reverse_Fault {id: 'gso_High_Angle_Reverse_Fault'}), (n_gso_Reverse_Fault {id: 'gso_Reverse_Fault'})
MERGE (n_gso_High_Angle_Reverse_Fault)-[:SUBCLASS_OF]->(n_gso_Reverse_Fault)

MATCH (n_gso_Horizontal_Fault {id: 'gso_Horizontal_Fault'}), (n_gso_Low_Angle_Fault {id: 'gso_Low_Angle_Fault'})
MERGE (n_gso_Horizontal_Fault)-[:SUBCLASS_OF]->(n_gso_Low_Angle_Fault)

MATCH (n_gso_Left_Normal_Fault {id: 'gso_Left_Normal_Fault'}), (n_gso_Oblique_Slip_Fault {id: 'gso_Oblique_Slip_Fault'})
MERGE (n_gso_Left_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_Oblique_Slip_Fault)

MATCH (n_gso_Left_Reverse_Fault {id: 'gso_Left_Reverse_Fault'}), (n_gso_Oblique_Slip_Fault {id: 'gso_Oblique_Slip_Fault'})
MERGE (n_gso_Left_Reverse_Fault)-[:SUBCLASS_OF]->(n_gso_Oblique_Slip_Fault)

MATCH (n_gso_Low_Angle_Fault {id: 'gso_Low_Angle_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Low_Angle_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Low_Angle_Normal_Fault {id: 'gso_Low_Angle_Normal_Fault'}), (n_gso_Low_Angle_Fault {id: 'gso_Low_Angle_Fault'})
MERGE (n_gso_Low_Angle_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_Low_Angle_Fault)

MATCH (n_gso_Low_Angle_Normal_Fault {id: 'gso_Low_Angle_Normal_Fault'}), (n_gso_Normal_Fault {id: 'gso_Normal_Fault'})
MERGE (n_gso_Low_Angle_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_Normal_Fault)

MATCH (n_gso_Mixed_Extraction_Fault {id: 'gso_Mixed_Extraction_Fault'}), (n_gso_Extraction_Fault {id: 'gso_Extraction_Fault'})
MERGE (n_gso_Mixed_Extraction_Fault)-[:SUBCLASS_OF]->(n_gso_Extraction_Fault)

MATCH (n_gso_No_Movement_Sense {id: 'gso_No_Movement_Sense'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_No_Movement_Sense)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Normal {id: 'gso_Normal'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_Normal)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Normal_Dextral {id: 'gso_Normal_Dextral'}), (n_gso_Dextral {id: 'gso_Dextral'})
MERGE (n_gso_Normal_Dextral)-[:SUBCLASS_OF]->(n_gso_Dextral)

MATCH (n_gso_Normal_Dextral {id: 'gso_Normal_Dextral'}), (n_gso_Normal {id: 'gso_Normal'})
MERGE (n_gso_Normal_Dextral)-[:SUBCLASS_OF]->(n_gso_Normal)

MATCH (n_gso_Normal_Fault {id: 'gso_Normal_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Normal_Sinistral {id: 'gso_Normal_Sinistral'}), (n_gso_Normal {id: 'gso_Normal'})
MERGE (n_gso_Normal_Sinistral)-[:SUBCLASS_OF]->(n_gso_Normal)

MATCH (n_gso_Normal_Sinistral {id: 'gso_Normal_Sinistral'}), (n_gso_Sinistral {id: 'gso_Sinistral'})
MERGE (n_gso_Normal_Sinistral)-[:SUBCLASS_OF]->(n_gso_Sinistral)

MATCH (n_gso_Oblique_Slip {id: 'gso_Oblique_Slip'}), (n_gso_Fault_Slip {id: 'gso_Fault_Slip'})
MERGE (n_gso_Oblique_Slip)-[:SUBCLASS_OF]->(n_gso_Fault_Slip)

MATCH (n_gso_Oblique_Slip_Fault {id: 'gso_Oblique_Slip_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Oblique_Slip_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Pure_Extraction_Fault {id: 'gso_Pure_Extraction_Fault'}), (n_gso_Extraction_Fault {id: 'gso_Extraction_Fault'})
MERGE (n_gso_Pure_Extraction_Fault)-[:SUBCLASS_OF]->(n_gso_Extraction_Fault)

MATCH (n_gso_Reverse {id: 'gso_Reverse'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_Reverse)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Reverse_Dextral {id: 'gso_Reverse_Dextral'}), (n_gso_Dextral {id: 'gso_Dextral'})
MERGE (n_gso_Reverse_Dextral)-[:SUBCLASS_OF]->(n_gso_Dextral)

MATCH (n_gso_Reverse_Dextral {id: 'gso_Reverse_Dextral'}), (n_gso_Reverse {id: 'gso_Reverse'})
MERGE (n_gso_Reverse_Dextral)-[:SUBCLASS_OF]->(n_gso_Reverse)

MATCH (n_gso_Reverse_Fault {id: 'gso_Reverse_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Reverse_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Reverse_Sinistral {id: 'gso_Reverse_Sinistral'}), (n_gso_Reverse {id: 'gso_Reverse'})
MERGE (n_gso_Reverse_Sinistral)-[:SUBCLASS_OF]->(n_gso_Reverse)

MATCH (n_gso_Reverse_Sinistral {id: 'gso_Reverse_Sinistral'}), (n_gso_Sinistral {id: 'gso_Sinistral'})
MERGE (n_gso_Reverse_Sinistral)-[:SUBCLASS_OF]->(n_gso_Sinistral)

MATCH (n_gso_Right_Normal_Fault {id: 'gso_Right_Normal_Fault'}), (n_gso_Oblique_Slip_Fault {id: 'gso_Oblique_Slip_Fault'})
MERGE (n_gso_Right_Normal_Fault)-[:SUBCLASS_OF]->(n_gso_Oblique_Slip_Fault)

MATCH (n_gso_Right_Reverse_Fault {id: 'gso_Right_Reverse_Fault'}), (n_gso_Oblique_Slip_Fault {id: 'gso_Oblique_Slip_Fault'})
MERGE (n_gso_Right_Reverse_Fault)-[:SUBCLASS_OF]->(n_gso_Oblique_Slip_Fault)

MATCH (n_gso_Scissor_Fault {id: 'gso_Scissor_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Scissor_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Scissor_Movement {id: 'gso_Scissor_Movement'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_Scissor_Movement)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Sinistral {id: 'gso_Sinistral'}), (n_gso_Fault_Movement_Sense {id: 'gso_Fault_Movement_Sense'})
MERGE (n_gso_Sinistral)-[:SUBCLASS_OF]->(n_gso_Fault_Movement_Sense)

MATCH (n_gso_Sinistral_Strike_Slip_Fault {id: 'gso_Sinistral_Strike_Slip_Fault'}), (n_gso_Strike_Slip_Fault {id: 'gso_Strike_Slip_Fault'})
MERGE (n_gso_Sinistral_Strike_Slip_Fault)-[:SUBCLASS_OF]->(n_gso_Strike_Slip_Fault)

MATCH (n_gso_Strike_Separation {id: 'gso_Strike_Separation'}), (n_gso_Fault_Separation {id: 'gso_Fault_Separation'})
MERGE (n_gso_Strike_Separation)-[:SUBCLASS_OF]->(n_gso_Fault_Separation)

MATCH (n_gso_Strike_Slip {id: 'gso_Strike_Slip'}), (n_gso_Fault_Slip {id: 'gso_Fault_Slip'})
MERGE (n_gso_Strike_Slip)-[:SUBCLASS_OF]->(n_gso_Fault_Slip)

MATCH (n_gso_Strike_Slip_Fault {id: 'gso_Strike_Slip_Fault'}), (n_gso_Fault {id: 'gso_Fault'})
MERGE (n_gso_Strike_Slip_Fault)-[:SUBCLASS_OF]->(n_gso_Fault)

MATCH (n_gso_Thrust_Decollement_Fault {id: 'gso_Thrust_Decollement_Fault'}), (n_gso_Thrust_Fault {id: 'gso_Thrust_Fault'})
MERGE (n_gso_Thrust_Decollement_Fault)-[:SUBCLASS_OF]->(n_gso_Thrust_Fault)

MATCH (n_gso_Thrust_Fault {id: 'gso_Thrust_Fault'}), (n_gso_Low_Angle_Fault {id: 'gso_Low_Angle_Fault'})
MERGE (n_gso_Thrust_Fault)-[:SUBCLASS_OF]->(n_gso_Low_Angle_Fault)

MATCH (n_gso_Thrust_Fault {id: 'gso_Thrust_Fault'}), (n_gso_Reverse_Fault {id: 'gso_Reverse_Fault'})
MERGE (n_gso_Thrust_Fault)-[:SUBCLASS_OF]->(n_gso_Reverse_Fault)

MATCH (n_gso_Transcurrent_Fault {id: 'gso_Transcurrent_Fault'}), (n_gso_High_Angle_Fault {id: 'gso_High_Angle_Fault'})
MERGE (n_gso_Transcurrent_Fault)-[:SUBCLASS_OF]->(n_gso_High_Angle_Fault)

MATCH (n_gso_Transcurrent_Fault {id: 'gso_Transcurrent_Fault'}), (n_gso_Strike_Slip_Fault {id: 'gso_Strike_Slip_Fault'})
MERGE (n_gso_Transcurrent_Fault)-[:SUBCLASS_OF]->(n_gso_Strike_Slip_Fault)

MATCH (n_gso_Transform_Fault {id: 'gso_Transform_Fault'}), (n_gso_Strike_Slip_Fault {id: 'gso_Strike_Slip_Fault'})
MERGE (n_gso_Transform_Fault)-[:SUBCLASS_OF]->(n_gso_Strike_Slip_Fault)

MATCH (n_gso_Wrench_Fault {id: 'gso_Wrench_Fault'}), (n_gso_High_Angle_Fault {id: 'gso_High_Angle_Fault'})
MERGE (n_gso_Wrench_Fault)-[:SUBCLASS_OF]->(n_gso_High_Angle_Fault)

MATCH (n_gso_Wrench_Fault {id: 'gso_Wrench_Fault'}), (n_gso_Strike_Slip_Fault {id: 'gso_Strike_Slip_Fault'})
MERGE (n_gso_Wrench_Fault)-[:SUBCLASS_OF]->(n_gso_Strike_Slip_Fault)

MATCH (n_gso_Fracture {id: 'gso_Fracture'}), (n_gso_Geologic_Structure {id: 'gso_Geologic_Structure'})
MERGE (n_gso_Fracture)-[:SUBCLASS_OF]->(n_gso_Geologic_Structure)

MATCH (n_gso_Anticline {id: 'gso_Anticline'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Anticline)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Antiform {id: 'gso_Antiform'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Antiform)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Chevron_Fold {id: 'gso_Chevron_Fold'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Chevron_Fold)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Fold {id: 'gso_Fold'}), (n_gso_Nonphysical_Morphologic_Feature {id: 'gso_Nonphysical_Morphologic_Feature'})
MERGE (n_gso_Fold)-[:SUBCLASS_OF]->(n_gso_Nonphysical_Morphologic_Feature)

MATCH (n_gso_Fold {id: 'gso_Fold'}), (n_gso_Geologic_Structure {id: 'gso_Geologic_Structure'})
MERGE (n_gso_Fold)-[:SUBCLASS_OF]->(n_gso_Geologic_Structure)

MATCH (n_gso_Fold_Amplitude {id: 'gso_Fold_Amplitude'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fold_Amplitude)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fold_Axial_Surface {id: 'gso_Fold_Axial_Surface'}), (n_gso_Low_Dimension_Feature {id: 'gso_Low_Dimension_Feature'})
MERGE (n_gso_Fold_Axial_Surface)-[:SUBCLASS_OF]->(n_gso_Low_Dimension_Feature)

MATCH (n_gso_Fold_Hinge {id: 'gso_Fold_Hinge'}), (n_gso_Low_Dimension_Feature {id: 'gso_Low_Dimension_Feature'})
MERGE (n_gso_Fold_Hinge)-[:SUBCLASS_OF]->(n_gso_Low_Dimension_Feature)

MATCH (n_gso_Fold_Hinge_Surface {id: 'gso_Fold_Hinge_Surface'}), (n_gso_Low_Dimension_Feature {id: 'gso_Low_Dimension_Feature'})
MERGE (n_gso_Fold_Hinge_Surface)-[:SUBCLASS_OF]->(n_gso_Low_Dimension_Feature)

MATCH (n_gso_Fold_InterLimb_Angle {id: 'gso_Fold_InterLimb_Angle'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fold_InterLimb_Angle)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fold_Limb {id: 'gso_Fold_Limb'}), (n_gso_Nonphysical_Morphologic_Feature {id: 'gso_Nonphysical_Morphologic_Feature'})
MERGE (n_gso_Fold_Limb)-[:SUBCLASS_OF]->(n_gso_Nonphysical_Morphologic_Feature)

MATCH (n_gso_Fold_Limb {id: 'gso_Fold_Limb'}), (n_gso_Geologic_Structure {id: 'gso_Geologic_Structure'})
MERGE (n_gso_Fold_Limb)-[:SUBCLASS_OF]->(n_gso_Geologic_Structure)

MATCH (n_gso_Fold_Limb_Shape {id: 'gso_Fold_Limb_Shape'}), (n_gso_Shape {id: 'gso_Shape'})
MERGE (n_gso_Fold_Limb_Shape)-[:SUBCLASS_OF]->(n_gso_Shape)

MATCH (n_gso_Fold_Span {id: 'gso_Fold_Span'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fold_Span)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fold_Symmetry {id: 'gso_Fold_Symmetry'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fold_Symmetry)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Fold_System {id: 'gso_Fold_System'}), (n_gso_Inherant_Feature {id: 'gso_Inherant_Feature'})
MERGE (n_gso_Fold_System)-[:SUBCLASS_OF]->(n_gso_Inherant_Feature)

MATCH (n_gso_Fold_System {id: 'gso_Fold_System'}), (n_gso_Geologic_Structure {id: 'gso_Geologic_Structure'})
MERGE (n_gso_Fold_System)-[:SUBCLASS_OF]->(n_gso_Geologic_Structure)

MATCH (n_gso_Fold_Wavelength {id: 'gso_Fold_Wavelength'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Fold_Wavelength)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Hinge_Line_Curvature {id: 'gso_Hinge_Line_Curvature'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Hinge_Line_Curvature)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Hinge_Shape {id: 'gso_Hinge_Shape'}), (n_gso_Shape {id: 'gso_Shape'})
MERGE (n_gso_Hinge_Shape)-[:SUBCLASS_OF]->(n_gso_Shape)

MATCH (n_gso_Is_Periodic {id: 'gso_Is_Periodic'}), (n_gso_Physical_Quality {id: 'gso_Physical_Quality'})
MERGE (n_gso_Is_Periodic)-[:SUBCLASS_OF]->(n_gso_Physical_Quality)

MATCH (n_gso_Monocline {id: 'gso_Monocline'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Monocline)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Neutral_Fold {id: 'gso_Neutral_Fold'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Neutral_Fold)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Ptygmatic_Fold {id: 'gso_Ptygmatic_Fold'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Ptygmatic_Fold)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Recumbent {id: 'gso_Recumbent'}), (n_gso_Plane_Orientation {id: 'gso_Plane_Orientation'})
MERGE (n_gso_Recumbent)-[:SUBCLASS_OF]->(n_gso_Plane_Orientation)

MATCH (n_gso_Recumbent_Fold {id: 'gso_Recumbent_Fold'}), (n_gso_Neutral_Fold {id: 'gso_Neutral_Fold'})
MERGE (n_gso_Recumbent_Fold)-[:SUBCLASS_OF]->(n_gso_Neutral_Fold)

MATCH (n_gso_Syncline {id: 'gso_Syncline'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Syncline)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Synform {id: 'gso_Synform'}), (n_gso_Fold {id: 'gso_Fold'})
MERGE (n_gso_Synform)-[:SUBCLASS_OF]->(n_gso_Fold)

MATCH (n_gso_Upright_Inclination {id: 'gso_Upright_Inclination'}), (n_gso_Plane_Orientation {id: 'gso_Plane_Orientation'})
MERGE (n_gso_Upright_Inclination)-[:SUBCLASS_OF]->(n_gso_Plane_Orientation)

MATCH (n_gso_Vertical_Fold {id: 'gso_Vertical_Fold'}), (n_gso_Neutral_Fold {id: 'gso_Neutral_Fold'})
MERGE (n_gso_Vertical_Fold)-[:SUBCLASS_OF]->(n_gso_Neutral_Fold)

MATCH (n_gso_anastomosing_spaced_cleavage {id: 'gso_anastomosing_spaced_cleavage'}), (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'})
MERGE (n_gso_anastomosing_spaced_cleavage)-[:SUBCLASS_OF]->(n_gso_spaced_cleavage)

MATCH (n_gso_bedding_fabric {id: 'gso_bedding_fabric'}), (n_gso_primary_foliation {id: 'gso_primary_foliation'})
MERGE (n_gso_bedding_fabric)-[:SUBCLASS_OF]->(n_gso_primary_foliation)

MATCH (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'}), (n_gso_bedding_fabric {id: 'gso_bedding_fabric'})
MERGE (n_gso_bedding_lamination_structure)-[:SUBCLASS_OF]->(n_gso_bedding_fabric)

MATCH (n_gso_c_fabric {id: 'gso_c_fabric'}), (n_gso_ductile_shear_banding_foliation {id: 'gso_ductile_shear_banding_foliation'})
MERGE (n_gso_c_fabric)-[:SUBCLASS_OF]->(n_gso_ductile_shear_banding_foliation)

MATCH (n_gso_cleavage {id: 'gso_cleavage'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_cleavage)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_cleavage_parallel_to_bedding {id: 'gso_cleavage_parallel_to_bedding'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_cleavage_parallel_to_bedding)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_cleavage_parallel_to_bedding {id: 'gso_cleavage_parallel_to_bedding'}), (n_gso_compound_foliation {id: 'gso_compound_foliation'})
MERGE (n_gso_cleavage_parallel_to_bedding)-[:SUBCLASS_OF]->(n_gso_compound_foliation)

MATCH (n_gso_close_joints {id: 'gso_close_joints'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_close_joints)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_close_joints {id: 'gso_close_joints'}), (n_gso_joint_fabric {id: 'gso_joint_fabric'})
MERGE (n_gso_close_joints)-[:SUBCLASS_OF]->(n_gso_joint_fabric)

MATCH (n_gso_comb_layering {id: 'gso_comb_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_comb_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_compositional_layering {id: 'gso_compositional_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_compositional_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_compound_foliation {id: 'gso_compound_foliation'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_compound_foliation)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_compound_metamorphic_foliation {id: 'gso_compound_metamorphic_foliation'}), (n_gso_compound_foliation {id: 'gso_compound_foliation'})
MERGE (n_gso_compound_metamorphic_foliation)-[:SUBCLASS_OF]->(n_gso_compound_foliation)

MATCH (n_gso_continuous_cleavage {id: 'gso_continuous_cleavage'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_continuous_cleavage)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_continuous_crenulation_cleavage {id: 'gso_continuous_crenulation_cleavage'}), (n_gso_continuous_cleavage {id: 'gso_continuous_cleavage'})
MERGE (n_gso_continuous_crenulation_cleavage)-[:SUBCLASS_OF]->(n_gso_continuous_cleavage)

MATCH (n_gso_continuous_crenulation_cleavage {id: 'gso_continuous_crenulation_cleavage'}), (n_gso_crenulation_cleavage {id: 'gso_crenulation_cleavage'})
MERGE (n_gso_continuous_crenulation_cleavage)-[:SUBCLASS_OF]->(n_gso_crenulation_cleavage)

MATCH (n_gso_crenulation_cleavage {id: 'gso_crenulation_cleavage'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_crenulation_cleavage)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_crude_or_indistinct_bedding {id: 'gso_crude_or_indistinct_bedding'}), (n_gso_bedding_fabric {id: 'gso_bedding_fabric'})
MERGE (n_gso_crude_or_indistinct_bedding)-[:SUBCLASS_OF]->(n_gso_bedding_fabric)

MATCH (n_gso_cryptomicrobial_lamination {id: 'gso_cryptomicrobial_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_cryptomicrobial_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_cumulate_layering {id: 'gso_cumulate_layering'}), (n_gso_igneous_layering {id: 'gso_igneous_layering'})
MERGE (n_gso_cumulate_layering)-[:SUBCLASS_OF]->(n_gso_igneous_layering)

MATCH (n_gso_discrete_cleavage {id: 'gso_discrete_cleavage'}), (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'})
MERGE (n_gso_discrete_cleavage)-[:SUBCLASS_OF]->(n_gso_spaced_cleavage)

MATCH (n_gso_discrete_crenulation_cleavage {id: 'gso_discrete_crenulation_cleavage'}), (n_gso_crenulation_cleavage {id: 'gso_crenulation_cleavage'})
MERGE (n_gso_discrete_crenulation_cleavage)-[:SUBCLASS_OF]->(n_gso_crenulation_cleavage)

MATCH (n_gso_discrete_crenulation_cleavage {id: 'gso_discrete_crenulation_cleavage'}), (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'})
MERGE (n_gso_discrete_crenulation_cleavage)-[:SUBCLASS_OF]->(n_gso_spaced_cleavage)

MATCH (n_gso_discrete_disjunct_spaced_cleavage {id: 'gso_discrete_disjunct_spaced_cleavage'}), (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'})
MERGE (n_gso_discrete_disjunct_spaced_cleavage)-[:SUBCLASS_OF]->(n_gso_spaced_cleavage)

MATCH (n_gso_disjunctive_cleavage {id: 'gso_disjunctive_cleavage'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_disjunctive_cleavage)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_domainal_cleavage {id: 'gso_domainal_cleavage'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_domainal_cleavage)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_ductile_shear_banding_foliation {id: 'gso_ductile_shear_banding_foliation'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_ductile_shear_banding_foliation)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_eutaxitic_foliation {id: 'gso_eutaxitic_foliation'}), (n_gso_primary_igneous_foliation {id: 'gso_primary_igneous_foliation'})
MERGE (n_gso_eutaxitic_foliation)-[:SUBCLASS_OF]->(n_gso_primary_igneous_foliation)

MATCH (n_gso_fissile_lamination {id: 'gso_fissile_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_fissile_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_flaser_structure {id: 'gso_flaser_structure'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_flaser_structure)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_flow_layering {id: 'gso_flow_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_flow_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_generic_mylonitic_foliation {id: 'gso_generic_mylonitic_foliation'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_generic_mylonitic_foliation)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_gneissic_layering {id: 'gso_gneissic_layering'}), (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'})
MERGE (n_gso_gneissic_layering)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering)

MATCH (n_gso_grain_shape_foliation {id: 'gso_grain_shape_foliation'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_grain_shape_foliation)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_igneous_flow_foliation {id: 'gso_igneous_flow_foliation'}), (n_gso_primary_igneous_foliation {id: 'gso_primary_igneous_foliation'})
MERGE (n_gso_igneous_flow_foliation)-[:SUBCLASS_OF]->(n_gso_primary_igneous_foliation)

MATCH (n_gso_igneous_lamination {id: 'gso_igneous_lamination'}), (n_gso_igneous_layering {id: 'gso_igneous_layering'})
MERGE (n_gso_igneous_lamination)-[:SUBCLASS_OF]->(n_gso_igneous_layering)

MATCH (n_gso_igneous_lamination {id: 'gso_igneous_lamination'}), (n_gso_primary_igneous_foliation {id: 'gso_primary_igneous_foliation'})
MERGE (n_gso_igneous_lamination)-[:SUBCLASS_OF]->(n_gso_primary_igneous_foliation)

MATCH (n_gso_igneous_layering {id: 'gso_igneous_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_igneous_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_igneous_layering {id: 'gso_igneous_layering'}), (n_gso_primary_igneous_foliation {id: 'gso_primary_igneous_foliation'})
MERGE (n_gso_igneous_layering)-[:SUBCLASS_OF]->(n_gso_primary_igneous_foliation)

MATCH (n_gso_igneous_textural_layering {id: 'gso_igneous_textural_layering'}), (n_gso_igneous_layering {id: 'gso_igneous_layering'})
MERGE (n_gso_igneous_textural_layering)-[:SUBCLASS_OF]->(n_gso_igneous_layering)

MATCH (n_gso_imbricated_clast_fabric {id: 'gso_imbricated_clast_fabric'}), (n_gso_grain_shape_foliation {id: 'gso_grain_shape_foliation'})
MERGE (n_gso_imbricated_clast_fabric)-[:SUBCLASS_OF]->(n_gso_grain_shape_foliation)

MATCH (n_gso_imbricated_clast_fabric {id: 'gso_imbricated_clast_fabric'}), (n_gso_primary_foliation {id: 'gso_primary_foliation'})
MERGE (n_gso_imbricated_clast_fabric)-[:SUBCLASS_OF]->(n_gso_primary_foliation)

MATCH (n_gso_impersistent_lamination {id: 'gso_impersistent_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_impersistent_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_irregular_lamination {id: 'gso_irregular_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_irregular_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_joint_fabric {id: 'gso_joint_fabric'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_joint_fabric)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_laminated_metamorphic_layering {id: 'gso_laminated_metamorphic_layering'}), (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'})
MERGE (n_gso_laminated_metamorphic_layering)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering)

MATCH (n_gso_lava_flow_banding {id: 'gso_lava_flow_banding'}), (n_gso_flow_layering {id: 'gso_flow_layering'})
MERGE (n_gso_lava_flow_banding)-[:SUBCLASS_OF]->(n_gso_flow_layering)

MATCH (n_gso_lava_flow_banding {id: 'gso_lava_flow_banding'}), (n_gso_igneous_layering {id: 'gso_igneous_layering'})
MERGE (n_gso_lava_flow_banding)-[:SUBCLASS_OF]->(n_gso_igneous_layering)

MATCH (n_gso_layered_mylonitic_foliation {id: 'gso_layered_mylonitic_foliation'}), (n_gso_compound_foliation {id: 'gso_compound_foliation'})
MERGE (n_gso_layered_mylonitic_foliation)-[:SUBCLASS_OF]->(n_gso_compound_foliation)

MATCH (n_gso_layered_mylonitic_foliation {id: 'gso_layered_mylonitic_foliation'}), (n_gso_generic_mylonitic_foliation {id: 'gso_generic_mylonitic_foliation'})
MERGE (n_gso_layered_mylonitic_foliation)-[:SUBCLASS_OF]->(n_gso_generic_mylonitic_foliation)

MATCH (n_gso_layered_mylonitic_foliation {id: 'gso_layered_mylonitic_foliation'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_layered_mylonitic_foliation)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_layering {id: 'gso_layering'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_layering)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_low_temperature_flow_foliation {id: 'gso_low_temperature_flow_foliation'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_low_temperature_flow_foliation)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_metamorphic_differentiation_layering {id: 'gso_metamorphic_differentiation_layering'}), (n_gso_compositional_layering {id: 'gso_compositional_layering'})
MERGE (n_gso_metamorphic_differentiation_layering)-[:SUBCLASS_OF]->(n_gso_compositional_layering)

MATCH (n_gso_metamorphic_differentiation_layering {id: 'gso_metamorphic_differentiation_layering'}), (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'})
MERGE (n_gso_metamorphic_differentiation_layering)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering)

MATCH (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_metamorphic_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_metamorphic_layering_inherited_from_protolith {id: 'gso_metamorphic_layering_inherited_from_protolith'}), (n_gso_compositional_layering {id: 'gso_compositional_layering'})
MERGE (n_gso_metamorphic_layering_inherited_from_protolith)-[:SUBCLASS_OF]->(n_gso_compositional_layering)

MATCH (n_gso_metamorphic_layering_inherited_from_protolith {id: 'gso_metamorphic_layering_inherited_from_protolith'}), (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'})
MERGE (n_gso_metamorphic_layering_inherited_from_protolith)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering)

MATCH (n_gso_mineralogical_layering {id: 'gso_mineralogical_layering'}), (n_gso_compositional_layering {id: 'gso_compositional_layering'})
MERGE (n_gso_mineralogical_layering)-[:SUBCLASS_OF]->(n_gso_compositional_layering)

MATCH (n_gso_mylonite_foliation {id: 'gso_mylonite_foliation'}), (n_gso_generic_mylonitic_foliation {id: 'gso_generic_mylonitic_foliation'})
MERGE (n_gso_mylonite_foliation)-[:SUBCLASS_OF]->(n_gso_generic_mylonitic_foliation)

MATCH (n_gso_parallel_bedding {id: 'gso_parallel_bedding'}), (n_gso_bedding_fabric {id: 'gso_bedding_fabric'})
MERGE (n_gso_parallel_bedding)-[:SUBCLASS_OF]->(n_gso_bedding_fabric)

MATCH (n_gso_parallel_bedding_lamination {id: 'gso_parallel_bedding_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_parallel_bedding_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_phyllitic_cleavage {id: 'gso_phyllitic_cleavage'}), (n_gso_continuous_cleavage {id: 'gso_continuous_cleavage'})
MERGE (n_gso_phyllitic_cleavage)-[:SUBCLASS_OF]->(n_gso_continuous_cleavage)

MATCH (n_gso_planar_lamination {id: 'gso_planar_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_planar_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_primary_foliation {id: 'gso_primary_foliation'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_primary_foliation)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_primary_igneous_foliation {id: 'gso_primary_igneous_foliation'}), (n_gso_primary_foliation {id: 'gso_primary_foliation'})
MERGE (n_gso_primary_igneous_foliation)-[:SUBCLASS_OF]->(n_gso_primary_foliation)

MATCH (n_gso_protomylonite_foliation {id: 'gso_protomylonite_foliation'}), (n_gso_generic_mylonitic_foliation {id: 'gso_generic_mylonitic_foliation'})
MERGE (n_gso_protomylonite_foliation)-[:SUBCLASS_OF]->(n_gso_generic_mylonitic_foliation)

MATCH (n_gso_rhythmic_layering {id: 'gso_rhythmic_layering'}), (n_gso_igneous_layering {id: 'gso_igneous_layering'})
MERGE (n_gso_rhythmic_layering)-[:SUBCLASS_OF]->(n_gso_igneous_layering)

MATCH (n_gso_rough_cleavage {id: 'gso_rough_cleavage'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_rough_cleavage)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_s_fabric {id: 'gso_s_fabric'}), (n_gso_grain_shape_foliation {id: 'gso_grain_shape_foliation'})
MERGE (n_gso_s_fabric)-[:SUBCLASS_OF]->(n_gso_grain_shape_foliation)

MATCH (n_gso_s_fabric {id: 'gso_s_fabric'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_s_fabric)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_scaly_cleavage {id: 'gso_scaly_cleavage'}), (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'})
MERGE (n_gso_scaly_cleavage)-[:SUBCLASS_OF]->(n_gso_spaced_cleavage)

MATCH (n_gso_schistosity {id: 'gso_schistosity'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_schistosity)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_sedimentary_layering {id: 'gso_sedimentary_layering'}), (n_gso_bedding_fabric {id: 'gso_bedding_fabric'})
MERGE (n_gso_sedimentary_layering)-[:SUBCLASS_OF]->(n_gso_bedding_fabric)

MATCH (n_gso_sedimentary_layering {id: 'gso_sedimentary_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_sedimentary_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_slaty_cleavage {id: 'gso_slaty_cleavage'}), (n_gso_continuous_cleavage {id: 'gso_continuous_cleavage'})
MERGE (n_gso_slaty_cleavage)-[:SUBCLASS_OF]->(n_gso_continuous_cleavage)

MATCH (n_gso_solution_cleavage {id: 'gso_solution_cleavage'}), (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'})
MERGE (n_gso_solution_cleavage)-[:SUBCLASS_OF]->(n_gso_spaced_cleavage)

MATCH (n_gso_spaced_cleavage {id: 'gso_spaced_cleavage'}), (n_gso_cleavage {id: 'gso_cleavage'})
MERGE (n_gso_spaced_cleavage)-[:SUBCLASS_OF]->(n_gso_cleavage)

MATCH (n_gso_stromatic_layering {id: 'gso_stromatic_layering'}), (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'})
MERGE (n_gso_stromatic_layering)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering)

MATCH (n_gso_stromatolitic_lamination {id: 'gso_stromatolitic_lamination'}), (n_gso_cryptomicrobial_lamination {id: 'gso_cryptomicrobial_lamination'})
MERGE (n_gso_stromatolitic_lamination)-[:SUBCLASS_OF]->(n_gso_cryptomicrobial_lamination)

MATCH (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'}), (n_gso_Foliation {id: 'gso_Foliation'})
MERGE (n_gso_tectonic_foliation)-[:SUBCLASS_OF]->(n_gso_Foliation)

MATCH (n_gso_tectonic_layering {id: 'gso_tectonic_layering'}), (n_gso_layering {id: 'gso_layering'})
MERGE (n_gso_tectonic_layering)-[:SUBCLASS_OF]->(n_gso_layering)

MATCH (n_gso_tectonic_layering {id: 'gso_tectonic_layering'}), (n_gso_tectonic_foliation {id: 'gso_tectonic_foliation'})
MERGE (n_gso_tectonic_layering)-[:SUBCLASS_OF]->(n_gso_tectonic_foliation)

MATCH (n_gso_transposed_bedding_layering {id: 'gso_transposed_bedding_layering'}), (n_gso_metamorphic_layering_inherited_from_protolith {id: 'gso_metamorphic_layering_inherited_from_protolith'})
MERGE (n_gso_transposed_bedding_layering)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering_inherited_from_protolith)

MATCH (n_gso_ultramylonite_foliation {id: 'gso_ultramylonite_foliation'}), (n_gso_generic_mylonitic_foliation {id: 'gso_generic_mylonitic_foliation'})
MERGE (n_gso_ultramylonite_foliation)-[:SUBCLASS_OF]->(n_gso_generic_mylonitic_foliation)

MATCH (n_gso_undulating_lamination {id: 'gso_undulating_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_undulating_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_vague_metamorphic_layering {id: 'gso_vague_metamorphic_layering'}), (n_gso_metamorphic_layering {id: 'gso_metamorphic_layering'})
MERGE (n_gso_vague_metamorphic_layering)-[:SUBCLASS_OF]->(n_gso_metamorphic_layering)

MATCH (n_gso_varve_lamination {id: 'gso_varve_lamination'}), (n_gso_bedding_lamination_structure {id: 'gso_bedding_lamination_structure'})
MERGE (n_gso_varve_lamination)-[:SUBCLASS_OF]->(n_gso_bedding_lamination_structure)

MATCH (n_gso_augen_lineation {id: 'gso_augen_lineation'}), (n_gso_particle_shape_lineation {id: 'gso_particle_shape_lineation'})
MERGE (n_gso_augen_lineation)-[:SUBCLASS_OF]->(n_gso_particle_shape_lineation)

MATCH (n_gso_augen_lineation {id: 'gso_augen_lineation'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_augen_lineation)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_bedding_cleavage_intersection_lineation {id: 'gso_bedding_cleavage_intersection_lineation'}), (n_gso_intersection_lineation {id: 'gso_intersection_lineation'})
MERGE (n_gso_bedding_cleavage_intersection_lineation)-[:SUBCLASS_OF]->(n_gso_intersection_lineation)

MATCH (n_gso_bedding_cleavage_intersection_lineation {id: 'gso_bedding_cleavage_intersection_lineation'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_bedding_cleavage_intersection_lineation)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_biotite_mineral_lineation {id: 'gso_biotite_mineral_lineation'}), (n_gso_mineral_lineation {id: 'gso_mineral_lineation'})
MERGE (n_gso_biotite_mineral_lineation)-[:SUBCLASS_OF]->(n_gso_mineral_lineation)

MATCH (n_gso_cleavage_intersection_lineation {id: 'gso_cleavage_intersection_lineation'}), (n_gso_intersection_lineation {id: 'gso_intersection_lineation'})
MERGE (n_gso_cleavage_intersection_lineation)-[:SUBCLASS_OF]->(n_gso_intersection_lineation)

MATCH (n_gso_cleavage_intersection_lineation {id: 'gso_cleavage_intersection_lineation'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_cleavage_intersection_lineation)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_crenulation_lineation {id: 'gso_crenulation_lineation'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_crenulation_lineation)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_flow_lineation {id: 'gso_flow_lineation'}), (n_gso_Lineation {id: 'gso_Lineation'})
MERGE (n_gso_flow_lineation)-[:SUBCLASS_OF]->(n_gso_Lineation)

MATCH (n_gso_hornblende_mineral_lineation {id: 'gso_hornblende_mineral_lineation'}), (n_gso_mineral_lineation {id: 'gso_mineral_lineation'})
MERGE (n_gso_hornblende_mineral_lineation)-[:SUBCLASS_OF]->(n_gso_mineral_lineation)

MATCH (n_gso_igneous_lineation {id: 'gso_igneous_lineation'}), (n_gso_Lineation {id: 'gso_Lineation'})
MERGE (n_gso_igneous_lineation)-[:SUBCLASS_OF]->(n_gso_Lineation)

MATCH (n_gso_igneous_mineral_lineation {id: 'gso_igneous_mineral_lineation'}), (n_gso_igneous_lineation {id: 'gso_igneous_lineation'})
MERGE (n_gso_igneous_mineral_lineation)-[:SUBCLASS_OF]->(n_gso_igneous_lineation)

MATCH (n_gso_igneous_mineral_lineation {id: 'gso_igneous_mineral_lineation'}), (n_gso_mineral_lineation {id: 'gso_mineral_lineation'})
MERGE (n_gso_igneous_mineral_lineation)-[:SUBCLASS_OF]->(n_gso_mineral_lineation)

MATCH (n_gso_igneous_particle_shape_lineation {id: 'gso_igneous_particle_shape_lineation'}), (n_gso_igneous_lineation {id: 'gso_igneous_lineation'})
MERGE (n_gso_igneous_particle_shape_lineation)-[:SUBCLASS_OF]->(n_gso_igneous_lineation)

MATCH (n_gso_igneous_particle_shape_lineation {id: 'gso_igneous_particle_shape_lineation'}), (n_gso_particle_shape_lineation {id: 'gso_particle_shape_lineation'})
MERGE (n_gso_igneous_particle_shape_lineation)-[:SUBCLASS_OF]->(n_gso_particle_shape_lineation)

MATCH (n_gso_igneous_vesicle_lineation {id: 'gso_igneous_vesicle_lineation'}), (n_gso_igneous_lineation {id: 'gso_igneous_lineation'})
MERGE (n_gso_igneous_vesicle_lineation)-[:SUBCLASS_OF]->(n_gso_igneous_lineation)

MATCH (n_gso_intersection_lineation {id: 'gso_intersection_lineation'}), (n_gso_Lineation {id: 'gso_Lineation'})
MERGE (n_gso_intersection_lineation)-[:SUBCLASS_OF]->(n_gso_Lineation)

MATCH (n_gso_mineral_lineation {id: 'gso_mineral_lineation'}), (n_gso_particle_shape_lineation {id: 'gso_particle_shape_lineation'})
MERGE (n_gso_mineral_lineation)-[:SUBCLASS_OF]->(n_gso_particle_shape_lineation)

MATCH (n_gso_particle_shape_lineation {id: 'gso_particle_shape_lineation'}), (n_gso_Lineation {id: 'gso_Lineation'})
MERGE (n_gso_particle_shape_lineation)-[:SUBCLASS_OF]->(n_gso_Lineation)

MATCH (n_gso_pencil_lineation {id: 'gso_pencil_lineation'}), (n_gso_Lineation {id: 'gso_Lineation'})
MERGE (n_gso_pencil_lineation)-[:SUBCLASS_OF]->(n_gso_Lineation)

MATCH (n_gso_quartz_fibre_lineation {id: 'gso_quartz_fibre_lineation'}), (n_gso_particle_shape_lineation {id: 'gso_particle_shape_lineation'})
MERGE (n_gso_quartz_fibre_lineation)-[:SUBCLASS_OF]->(n_gso_particle_shape_lineation)

MATCH (n_gso_rodding_lineation {id: 'gso_rodding_lineation'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_rodding_lineation)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_sillimanite_mineral_lineation {id: 'gso_sillimanite_mineral_lineation'}), (n_gso_mineral_lineation {id: 'gso_mineral_lineation'})
MERGE (n_gso_sillimanite_mineral_lineation)-[:SUBCLASS_OF]->(n_gso_mineral_lineation)

MATCH (n_gso_slickenline {id: 'gso_slickenline'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_slickenline)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_stretching_lineation {id: 'gso_stretching_lineation'}), (n_gso_particle_shape_lineation {id: 'gso_particle_shape_lineation'})
MERGE (n_gso_stretching_lineation)-[:SUBCLASS_OF]->(n_gso_particle_shape_lineation)

MATCH (n_gso_stretching_lineation {id: 'gso_stretching_lineation'}), (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'})
MERGE (n_gso_stretching_lineation)-[:SUBCLASS_OF]->(n_gso_tectonic_lineation)

MATCH (n_gso_tectonic_lineation {id: 'gso_tectonic_lineation'}), (n_gso_Lineation {id: 'gso_Lineation'})
MERGE (n_gso_tectonic_lineation)-[:SUBCLASS_OF]->(n_gso_Lineation)

MATCH (n_gso_Alteration_Facies_Contact {id: 'gso_Alteration_Facies_Contact'}), (n_gso_Metamorphic_Contact {id: 'gso_Metamorphic_Contact'})
MERGE (n_gso_Alteration_Facies_Contact)-[:SUBCLASS_OF]->(n_gso_Metamorphic_Contact)

MATCH (n_gso_Angular_Unconformable_Contact {id: 'gso_Angular_Unconformable_Contact'}), (n_gso_Unconformable_Contact {id: 'gso_Unconformable_Contact'})
MERGE (n_gso_Angular_Unconformable_Contact)-[:SUBCLASS_OF]->(n_gso_Unconformable_Contact)

MATCH (n_gso_Buttress_Unconformity {id: 'gso_Buttress_Unconformity'}), (n_gso_Unconformable_Contact {id: 'gso_Unconformable_Contact'})
MERGE (n_gso_Buttress_Unconformity)-[:SUBCLASS_OF]->(n_gso_Unconformable_Contact)

MATCH (n_gso_Chronostratigraphic_Contact {id: 'gso_Chronostratigraphic_Contact'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Chronostratigraphic_Contact)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_Conductivity_Contact {id: 'gso_Conductivity_Contact'}), (n_gso_Geophysical_Contact {id: 'gso_Geophysical_Contact'})
MERGE (n_gso_Conductivity_Contact)-[:SUBCLASS_OF]->(n_gso_Geophysical_Contact)

MATCH (n_gso_Conformable_Contact {id: 'gso_Conformable_Contact'}), (n_gso_Depositional_Contact {id: 'gso_Depositional_Contact'})
MERGE (n_gso_Conformable_Contact)-[:SUBCLASS_OF]->(n_gso_Depositional_Contact)

MATCH (n_gso_Contact {id: 'gso_Contact'}), (n_gso_Low_Dimension_Feature {id: 'gso_Low_Dimension_Feature'})
MERGE (n_gso_Contact)-[:SUBCLASS_OF]->(n_gso_Low_Dimension_Feature)

MATCH (n_gso_Contact {id: 'gso_Contact'}), (n_gso_Geologic_Structure {id: 'gso_Geologic_Structure'})
MERGE (n_gso_Contact)-[:SUBCLASS_OF]->(n_gso_Geologic_Structure)

MATCH (n_gso_Deformation_Zone_Contact {id: 'gso_Deformation_Zone_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Deformation_Zone_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Density_Contact {id: 'gso_Density_Contact'}), (n_gso_Geophysical_Contact {id: 'gso_Geophysical_Contact'})
MERGE (n_gso_Density_Contact)-[:SUBCLASS_OF]->(n_gso_Geophysical_Contact)

MATCH (n_gso_Depositional_Contact {id: 'gso_Depositional_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Depositional_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Disconformable_Contact {id: 'gso_Disconformable_Contact'}), (n_gso_Unconformable_Contact {id: 'gso_Unconformable_Contact'})
MERGE (n_gso_Disconformable_Contact)-[:SUBCLASS_OF]->(n_gso_Unconformable_Contact)

MATCH (n_gso_Faulted_Contact {id: 'gso_Faulted_Contact'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Faulted_Contact)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_GSSP {id: 'gso_GSSP'}), (n_gso_Stratigraphic_Point {id: 'gso_Stratigraphic_Point'})
MERGE (n_gso_GSSP)-[:SUBCLASS_OF]->(n_gso_Stratigraphic_Point)

MATCH (n_gso_Geologic_Province_Contact {id: 'gso_Geologic_Province_Contact'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Geologic_Province_Contact)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_Geophysical_Contact {id: 'gso_Geophysical_Contact'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Geophysical_Contact)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_Glacial_Stationary_Line {id: 'gso_Glacial_Stationary_Line'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Glacial_Stationary_Line)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_Gradational_Contact_Zone {id: 'gso_Gradational_Contact_Zone'}), (n_gso_Material_Feature {id: 'gso_Material_Feature'})
MERGE (n_gso_Gradational_Contact_Zone)-[:SUBCLASS_OF]->(n_gso_Material_Feature)

MATCH (n_gso_Igneous_Intrusive_Contact {id: 'gso_Igneous_Intrusive_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Igneous_Intrusive_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Igneous_Phase_Contact {id: 'gso_Igneous_Phase_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Igneous_Phase_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Impact_Structure_Boundary {id: 'gso_Impact_Structure_Boundary'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Impact_Structure_Boundary)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Lithogenetic_Contact)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_Magnetic_Contact {id: 'gso_Magnetic_Contact'}), (n_gso_Geophysical_Contact {id: 'gso_Geophysical_Contact'})
MERGE (n_gso_Magnetic_Contact)-[:SUBCLASS_OF]->(n_gso_Geophysical_Contact)

MATCH (n_gso_Magnetic_Polarity_Contact {id: 'gso_Magnetic_Polarity_Contact'}), (n_gso_Magnetic_Contact {id: 'gso_Magnetic_Contact'})
MERGE (n_gso_Magnetic_Polarity_Contact)-[:SUBCLASS_OF]->(n_gso_Magnetic_Contact)

MATCH (n_gso_Magnetic_Susceptiblity_Contact {id: 'gso_Magnetic_Susceptiblity_Contact'}), (n_gso_Magnetic_Contact {id: 'gso_Magnetic_Contact'})
MERGE (n_gso_Magnetic_Susceptiblity_Contact)-[:SUBCLASS_OF]->(n_gso_Magnetic_Contact)

MATCH (n_gso_Magnetization_Contact {id: 'gso_Magnetization_Contact'}), (n_gso_Magnetic_Contact {id: 'gso_Magnetic_Contact'})
MERGE (n_gso_Magnetization_Contact)-[:SUBCLASS_OF]->(n_gso_Magnetic_Contact)

MATCH (n_gso_Metamorphic_Contact {id: 'gso_Metamorphic_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Metamorphic_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Metamorphic_Facies_Contact {id: 'gso_Metamorphic_Facies_Contact'}), (n_gso_Metamorphic_Contact {id: 'gso_Metamorphic_Contact'})
MERGE (n_gso_Metamorphic_Facies_Contact)-[:SUBCLASS_OF]->(n_gso_Metamorphic_Contact)

MATCH (n_gso_Metasomatic_Facies_Contact {id: 'gso_Metasomatic_Facies_Contact'}), (n_gso_Metamorphic_Contact {id: 'gso_Metamorphic_Contact'})
MERGE (n_gso_Metasomatic_Facies_Contact)-[:SUBCLASS_OF]->(n_gso_Metamorphic_Contact)

MATCH (n_gso_Mineralisation_Assemblage_Contact {id: 'gso_Mineralisation_Assemblage_Contact'}), (n_gso_Metamorphic_Contact {id: 'gso_Metamorphic_Contact'})
MERGE (n_gso_Mineralisation_Assemblage_Contact)-[:SUBCLASS_OF]->(n_gso_Metamorphic_Contact)

MATCH (n_gso_Nonconformable_Contact {id: 'gso_Nonconformable_Contact'}), (n_gso_Unconformable_Contact {id: 'gso_Unconformable_Contact'})
MERGE (n_gso_Nonconformable_Contact)-[:SUBCLASS_OF]->(n_gso_Unconformable_Contact)

MATCH (n_gso_Paraconformable_Contact {id: 'gso_Paraconformable_Contact'}), (n_gso_Unconformable_Contact {id: 'gso_Unconformable_Contact'})
MERGE (n_gso_Paraconformable_Contact)-[:SUBCLASS_OF]->(n_gso_Unconformable_Contact)

MATCH (n_gso_Radiometric_Contact {id: 'gso_Radiometric_Contact'}), (n_gso_Geophysical_Contact {id: 'gso_Geophysical_Contact'})
MERGE (n_gso_Radiometric_Contact)-[:SUBCLASS_OF]->(n_gso_Geophysical_Contact)

MATCH (n_gso_Sedimentary_Facies_Contact {id: 'gso_Sedimentary_Facies_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Sedimentary_Facies_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Sedimentary_Intrusive_Contact {id: 'gso_Sedimentary_Intrusive_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Sedimentary_Intrusive_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Seismic_Contact {id: 'gso_Seismic_Contact'}), (n_gso_Geophysical_Contact {id: 'gso_Geophysical_Contact'})
MERGE (n_gso_Seismic_Contact)-[:SUBCLASS_OF]->(n_gso_Geophysical_Contact)

MATCH (n_gso_Stratigraphic_Point {id: 'gso_Stratigraphic_Point'}), (n_gso_Contact {id: 'gso_Contact'})
MERGE (n_gso_Stratigraphic_Point)-[:SUBCLASS_OF]->(n_gso_Contact)

MATCH (n_gso_Unconformable_Contact {id: 'gso_Unconformable_Contact'}), (n_gso_Depositional_Contact {id: 'gso_Depositional_Contact'})
MERGE (n_gso_Unconformable_Contact)-[:SUBCLASS_OF]->(n_gso_Depositional_Contact)

MATCH (n_gso_Volcanic_Subsidence_Zone_Boundary {id: 'gso_Volcanic_Subsidence_Zone_Boundary'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Volcanic_Subsidence_Zone_Boundary)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

MATCH (n_gso_Weathering_Contact {id: 'gso_Weathering_Contact'}), (n_gso_Lithogenetic_Contact {id: 'gso_Lithogenetic_Contact'})
MERGE (n_gso_Weathering_Contact)-[:SUBCLASS_OF]->(n_gso_Lithogenetic_Contact)

// OSDU-GSO crosswalk: Fault exactMatch Fault
MATCH (gso {id: 'gso_Fault'})
SET gso.osdu_crosswalk_class = 'Fault', gso.osdu_crosswalk_match = 'exactMatch'

// OSDU-GSO crosswalk: GeologicalFormation closeMatch Geologic_Unit
MATCH (entity {id: 'formacao'}), (gso {id: 'gso_Geologic_Unit'})
MERGE (entity)-[:CLOSEMATCH {note: 'OSDU GeologicalFormation é unidade litoestratigráfica nomeada; GSO Geologic_Unit é abstração mais ampla (inclui chrono-, bio-, lito-stratigráfico). Use closeMatch — não substituir 1:1.'}]->(gso)

// OSDU-GSO crosswalk: Basin broadMatch Geologic_Setting
MATCH (entity {id: 'bacia-sedimentar'}), (gso {id: 'gso_Geologic_Setting'})
MERGE (entity)-[:BROADMATCH {note: 'OSDU Basin (área geográfica de sistema deposicional) é caso particular do conceito mais amplo GSO Geologic_Setting (ambientes geológicos).'}]->(gso)

// OSDU-GSO crosswalk: RockSample narrowMatch Material_Feature
MATCH (gso {id: 'gso_Material_Feature'})
SET gso.osdu_crosswalk_class = 'RockSample', gso.osdu_crosswalk_match = 'narrowMatch'

// OSDU-GSO crosswalk: LithologyType closeMatch Geologic_Rock_Material
MATCH (entity {id: 'litologia'}), (gso {id: 'gso_Geologic_Rock_Material'})
MERGE (entity)-[:CLOSEMATCH {note: 'OSDU LithologyType é taxonomia enumerativa de litologias; GSO Geologic_Rock_Material é classe formal de materiais rochosos com sub-classes detalhadas.'}]->(gso)

// GSO-only: Anticline (gso_only) — no OSDU equivalent

// GSO-only: Syncline (gso_only) — no OSDU equivalent

// GSO-only: Normal_Fault (gso_only) — no OSDU equivalent

// GSO-only: Strike_Slip_Fault (gso_only) — no OSDU equivalent

// GSO-only: Reverse_Fault (gso_only) — no OSDU equivalent

// GSO-only: Unconformity (gso_only) — no OSDU equivalent

// GSO-only: Conformable_Contact (gso_only) — no OSDU equivalent

// GSO-only: bedding_fabric (gso_only) — no OSDU equivalent

MATCH (op {id: 'ontopetro_class_C002'}), (gso {id: 'gso_Geologic_Unit'})
MERGE (op)-[:CLOSEMATCH]->(gso)

MATCH (op {id: 'ontopetro_class_C001'}), (gso {id: 'gso_Geologic_Setting'})
MERGE (op)-[:BROADMATCH]->(gso)
