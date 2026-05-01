/**
 * ontopetro-data.js — Dados estruturados das ontologias de domínio:
 *
 * - ONTOPETRO: 6 módulos (Classes, Properties, Relations, Instances, Taxonomies, Metadata)
 * - TAXONOMIES: 9 enumerações canônicas (litologia, trapa, tipo_poco, SPE-PRMS, ...)
 * - MODULES_EXTENDED: M7 Geoquímica, M8 Rocha, M9 Geomecânica, M10 Fluidos
 * - PVT_DICTIONARY: 35 campos do sistema SIRR Petrobras com completude real
 * - SYSTEMS: 8 sistemas corporativos Petrobras
 * - REGIS_NER: mapeamento PetroGold ↔ entity-graph
 * - LAYER6_DEF: definição da camada 6 (Petrobras Internal)
 * - ONTOPETRO_NODES / ONTOPETRO_EDGES: extensão do entity-graph
 */

/* ─────────────────────────────────────────────────────────────
 * SPEC 15 — ontopetro.json
 * ───────────────────────────────────────────────────────────── */

export const ONTOPETRO_CLASSES = [
  { id: 'C001', name: 'BaciaSedimentar',     name_en: 'Sedimentary Basin',  superclass: 'GeologicalObject',     description: 'Depressão crustal onde sedimentos se acumulam ao longo do tempo geológico',                              domain: 'Geologia Estrutural',   sources: ['GeoCore'],          entity_graph_id: 'bacia-sedimentar' },
  { id: 'C002', name: 'FormacaoGeologica',   name_en: 'Geological Formation',superclass: 'GeologicalObject',    description: 'Unidade litoestratigráfica nomeada e mapeável',                                                          domain: 'Estratigrafia',         sources: ['PPDM','GeoCore'],   entity_graph_id: 'formacao' },
  { id: 'C003', name: 'RochaReservatorio',   name_en: 'Reservoir Rock',      superclass: 'FormacaoGeologica',    description: 'Rocha porosa e permeável capaz de armazenar hidrocarbonetos',                                            domain: 'Reservatório',          sources: ['GDGEO','GeoCore'],  entity_graph_id: 'reservatorio' },
  { id: 'C004', name: 'RochaCapacitante',    name_en: 'Cap Rock',            superclass: 'FormacaoGeologica',    description: 'Rocha de baixa permeabilidade que sela o reservatório (cap rock)',                                       domain: 'Reservatório',          sources: ['GeoCore'],          entity_graph_id: 'rocha-capacitante' },
  { id: 'C005', name: 'RochaGeneradora',     name_en: 'Source Rock',         superclass: 'FormacaoGeologica',    description: 'Rocha rica em matéria orgânica geradora de HC (source rock)',                                            domain: 'Geoquímica',            sources: ['GeoCore'],          entity_graph_id: 'rocha-geradora' },
  { id: 'C006', name: 'TrapaPetrolifera',    name_en: 'Petroleum Trap',      superclass: 'GeologicalObject',     description: 'Configuração geológica que permite acúmulo de HC',                                                       domain: 'Sistemas Petrolíferos', sources: ['PPDM'],             entity_graph_id: 'trapa' },
  { id: 'C007', name: 'SistemaPetrolifero',  name_en: 'Petroleum System',    superclass: 'GeologicalSystem',     description: 'Conjunto rocha-geradora, migração, reservatório, capa e trapa',                                          domain: 'Sistemas Petrolíferos', sources: ['PPDM','GeoCore'],   entity_graph_id: 'sistema-petrolifero' },
  { id: 'C008', name: 'Acumulacao',          name_en: 'Hydrocarbon Accumulation', superclass: 'GeologicalObject',description: 'Volume de HC contido em armadilha com dimensões definidas',                                              domain: 'Reservatório',          sources: ['PPDM'],             entity_graph_id: 'acumulacao' },
  { id: 'C009', name: 'Campo',               name_en: 'Field',               superclass: 'GeologicalObject',     description: 'Área geográfica delimitada contendo uma ou mais acumulações',                                            domain: 'Produção',              sources: ['ANP','PPDM'],       entity_graph_id: 'campo' },
  { id: 'C010', name: 'Bloco',               name_en: 'Exploration Block',   superclass: 'AdministrativeObject', description: 'Área definida em concessão ou partilha para atividade E&P',                                              domain: 'Regulatório',           sources: ['ANP'],              entity_graph_id: 'bloco' },
  { id: 'C011', name: 'Poco',                name_en: 'Well',                superclass: 'WellObject',           description: 'Perfuração realizada para exploração, avaliação ou produção',                                            domain: 'Poços',                 sources: ['PPDM','OSDU'],      entity_graph_id: 'poco' },
  { id: 'C012', name: 'Testemunho',          name_en: 'Core Sample',         superclass: 'SampleObject',         description: 'Amostra cilíndrica de rocha extraída durante perfuração',                                                domain: 'Amostragem',            sources: ['GDGEO'],            entity_graph_id: 'testemunho' },
  { id: 'C013', name: 'PerfilDePoco',        name_en: 'Well Log',            superclass: 'WellLog',              description: 'Medição contínua de propriedades físicas ao longo do poço',                                              domain: 'Petrofísica',           sources: ['PPDM'],             entity_graph_id: 'perfil-poco' },
  { id: 'C014', name: 'SismoEstratigrafia',  name_en: 'Seismic Stratigraphy',superclass: 'InterpretationObject', description: 'Análise estratigráfica baseada em dados sísmicos',                                                       domain: 'Geofísica',             sources: ['Petrolês','GeoCore'], entity_graph_id: null },
  { id: 'C015', name: 'Horizonte',           name_en: 'Seismic Horizon',     superclass: 'SeismicObject',        description: 'Superfície refletora identificada em dados sísmicos',                                                    domain: 'Geofísica',             sources: ['PPDM'],             entity_graph_id: null },
  { id: 'C016', name: 'FalhaGeologica',      name_en: 'Geological Fault',    superclass: 'StructuralObject',     description: 'Descontinuidade tectônica com deslocamento relativo das camadas',                                        domain: 'Geologia Estrutural',   sources: ['GeoCore'],          entity_graph_id: 'falha' },
  { id: 'C017', name: 'Play',                name_en: 'Play',                superclass: 'ExplorationObject',    description: 'Combinação de elementos petrolíferos com potencial exploratório',                                        domain: 'Exploração',            sources: ['PPDM'],             entity_graph_id: 'play' },
  { id: 'C018', name: 'Prospecto',           name_en: 'Prospect',            superclass: 'ExplorationObject',    description: 'Área estrutural/estratigráfica com potencial para acumulação',                                           domain: 'Exploração',            sources: ['PPDM'],             entity_graph_id: 'prospecto' },
  { id: 'C019', name: 'Recurso',             name_en: 'Resource',            superclass: 'EconomicObject',       description: 'Volume de HC com grau variável de certeza geológica',                                                    domain: 'Reservas/Recursos',     sources: ['ANP','SPE-PRMS'],   entity_graph_id: 'recurso' },
  { id: 'C020', name: 'Reserva',             name_en: 'Reserve',             superclass: 'EconomicObject',       description: 'Volume de HC tecnicamente recuperável e economicamente viável',                                          domain: 'Reservas/Recursos',     sources: ['ANP','SPE-PRMS'],   entity_graph_id: 'reserva' },
];

export const ONTOPETRO_PROPERTIES = [
  { id: 'P001', name: 'nomeFormacao',              name_en: 'formationName',            type: 'DatatypeProperty', domain_class: 'FormacaoGeologica',   range: 'xsd:string', unit: null,           description: 'Nome oficial da formação',                              rag_priority: 'medium' },
  { id: 'P002', name: 'idadeCronoestratigrafica',  name_en: 'chronostratigraphicAge',   type: 'DatatypeProperty', domain_class: 'FormacaoGeologica',   range: 'xsd:string', unit: 'Ma',           description: 'Período geológico (Cretáceo, Aptiano, Albiano…)',        rag_priority: 'medium' },
  { id: 'P003', name: 'litologia',                 name_en: 'lithology',                type: 'DatatypeProperty', domain_class: 'FormacaoGeologica',   range: 'xsd:string', unit: null,           description: 'Tipo de rocha predominante',                            rag_priority: 'medium' },
  { id: 'P004', name: 'porosidade',                name_en: 'porosity',                 type: 'DatatypeProperty', domain_class: 'RochaReservatorio',   range: 'xsd:float',  unit: '%',            description: 'Fração do volume total da rocha ocupado por poros',     rag_priority: 'high' },
  { id: 'P005', name: 'permeabilidade',            name_en: 'permeability',             type: 'DatatypeProperty', domain_class: 'RochaReservatorio',   range: 'xsd:float',  unit: 'mD',           description: 'Capacidade de transmitir fluidos',                      rag_priority: 'high' },
  { id: 'P006', name: 'saturacaoDeOleo',           name_en: 'oilSaturation',            type: 'DatatypeProperty', domain_class: 'RochaReservatorio',   range: 'xsd:float',  unit: '%',            description: 'Fração do espaço poroso ocupado por óleo',              rag_priority: 'high' },
  { id: 'P007', name: 'profundidadeTopReservatorio', name_en: 'reservoirTopDepth',      type: 'DatatypeProperty', domain_class: 'RochaReservatorio',   range: 'xsd:float',  unit: 'm',            description: 'Profundidade do topo do reservatório',                  rag_priority: 'high' },
  { id: 'P008', name: 'contatoOleoAgua',           name_en: 'oilWaterContact',          type: 'DatatypeProperty', domain_class: 'Acumulacao',          range: 'xsd:float',  unit: 'm',            description: 'Profundidade do contato óleo-água (OWC)',               rag_priority: 'high' },
  { id: 'P009', name: 'volumeOriginalOleo',        name_en: 'originalOilInPlace',       type: 'DatatypeProperty', domain_class: 'Acumulacao',          range: 'xsd:float',  unit: 'Mm³/MMbbl',    description: 'VOIP/STOIIP — volume original de óleo in place',         rag_priority: 'high' },
  { id: 'P010', name: 'fatorDeRecuperacao',        name_en: 'recoveryFactor',           type: 'DatatypeProperty', domain_class: 'Acumulacao',          range: 'xsd:float',  unit: '%',            description: 'Estimativa de recuperação de HC',                       rag_priority: 'high' },
  { id: 'P011', name: 'coordenadaX',               name_en: 'longitude',                type: 'DatatypeProperty', domain_class: 'GeospatialObject',    range: 'xsd:float',  unit: 'graus',        description: 'Longitude WGS84/SIRGAS2000',                            rag_priority: 'medium' },
  { id: 'P012', name: 'coordenadaY',               name_en: 'latitude',                 type: 'DatatypeProperty', domain_class: 'GeospatialObject',    range: 'xsd:float',  unit: 'graus',        description: 'Latitude WGS84/SIRGAS2000',                             rag_priority: 'medium' },
  { id: 'P013', name: 'datumGeodetico',            name_en: 'geodeticDatum',            type: 'DatatypeProperty', domain_class: 'GeospatialObject',    range: 'xsd:string', unit: null,           description: 'CRS de referência: SIRGAS2000 ou WGS84',                rag_priority: 'medium' },
  { id: 'P014', name: 'grauAPI',                   name_en: 'apiGravity',               type: 'DatatypeProperty', domain_class: 'Hidrocarboneto',      range: 'xsd:float',  unit: '°API',         description: 'Densidade do óleo em graus API',                        rag_priority: 'high' },
  { id: 'P015', name: 'teorDeCarbono',             name_en: 'totalOrganicCarbon',       type: 'DatatypeProperty', domain_class: 'RochaGeneradora',     range: 'xsd:float',  unit: '% peso',       description: 'COT/TOC — teor de carbono orgânico total',              rag_priority: 'high' },
  { id: 'P016', name: 'janelaDeOleo',              name_en: 'oilWindow',                type: 'DatatypeProperty', domain_class: 'SistemaPetrolifero',  range: 'xsd:string', unit: null,           description: 'Faixa de maturidade termal',                            rag_priority: 'high' },
  { id: 'P017', name: 'tipoDeTrapa',               name_en: 'trapType',                 type: 'DatatypeProperty', domain_class: 'TrapaPetrolifera',    range: 'xsd:string', unit: null,           description: 'Estrutural / Estratigráfica / Combinada',               rag_priority: 'medium' },
  { id: 'P018', name: 'amplitudeSismica',          name_en: 'seismicAmplitude',         type: 'DatatypeProperty', domain_class: 'Horizonte',           range: 'xsd:float',  unit: 'ms',           description: 'Tempo de reflexão sísmica',                             rag_priority: 'medium' },
  { id: 'P019', name: 'nomePoco',                  name_en: 'wellName',                 type: 'DatatypeProperty', domain_class: 'Poco',                range: 'xsd:string', unit: null,           description: 'Nome oficial ANP do poço',                              rag_priority: 'medium' },
  { id: 'P020', name: 'tipoPoco',                  name_en: 'wellType',                 type: 'DatatypeProperty', domain_class: 'Poco',                range: 'xsd:string', unit: null,           description: 'Exploratório / Avaliação / Desenvolvimento / Injetor',  rag_priority: 'medium' },
];

export const ONTOPETRO_RELATIONS = [
  { id: 'R001', name: 'pertenceA',         name_en: 'belongsTo',          domain: 'FormacaoGeologica',   range: 'BaciaSedimentar',       inverse: 'contemFormacao',     cardinality: 'N:1', description: 'Formação pertence a uma bacia sedimentar' },
  { id: 'R002', name: 'compostoPor',       name_en: 'composedOf',         domain: 'BaciaSedimentar',     range: 'FormacaoGeologica',     inverse: 'pertenceA',          cardinality: '1:N', description: 'Bacia é composta por múltiplas formações' },
  { id: 'R003', name: 'constitui',         name_en: 'constitutes',        domain: 'RochaReservatorio',   range: 'TrapaPetrolifera',      inverse: 'eConstituidaPor',    cardinality: 'N:M', description: 'Rocha reservatório constitui parte da trapa' },
  { id: 'R004', name: 'selaReservatorio',  name_en: 'sealsReservoir',     domain: 'RochaCapacitante',    range: 'RochaReservatorio',     inverse: 'eSeladaPor',         cardinality: 'N:M', description: 'Rocha capacitante sela o reservatório' },
  { id: 'R005', name: 'geraHidrocarbonetos', name_en: 'generatesHydrocarbons', domain: 'RochaGeneradora', range: 'Hidrocarboneto',     inverse: 'eGeradoPor',         cardinality: '1:N', description: 'Rocha geradora gera hidrocarbonetos' },
  { id: 'R006', name: 'contem',            name_en: 'contains',           domain: 'TrapaPetrolifera',    range: 'Acumulacao',            inverse: 'eContidaEm',         cardinality: '1:N', description: 'Trapa contém acumulações' },
  { id: 'R007', name: 'fazParteDe',        name_en: 'isPartOf',           domain: 'Acumulacao',          range: 'Campo',                 inverse: 'contemAcumulacao',   cardinality: 'N:1', description: 'Acumulação faz parte de um campo' },
  { id: 'R008', name: 'localizadoEm',      name_en: 'locatedIn',          domain: 'Campo',               range: 'BaciaSedimentar',       inverse: 'contemCampo',        cardinality: 'N:1', description: 'Campo localizado em bacia' },
  { id: 'R009', name: 'associadoA',        name_en: 'associatedWith',     domain: 'Prospecto',           range: 'Play',                  inverse: 'contemProspecto',    cardinality: 'N:1', description: 'Prospecto associado a play' },
  { id: 'R010', name: 'perfuradoEm',       name_en: 'drilledIn',          domain: 'Poco',                range: 'Campo',                 inverse: 'contemPoco',         cardinality: 'N:1', description: 'Poço perfurado em campo' },
  { id: 'R011', name: 'intercepta',        name_en: 'intersects',         domain: 'Poco',                range: 'FormacaoGeologica',     inverse: 'eInterceptadaPor',   cardinality: 'N:M', description: 'Poço intercepta formações' },
  { id: 'R012', name: 'amostradoPor',      name_en: 'sampledBy',          domain: 'FormacaoGeologica',   range: 'Testemunho',            inverse: 'amostrou',           cardinality: '1:N', description: 'Formação amostrada por testemunhos' },
  { id: 'R013', name: 'medidoPor',         name_en: 'measuredBy',         domain: 'FormacaoGeologica',   range: 'PerfilDePoco',          inverse: 'mediu',              cardinality: '1:N', description: 'Formação medida por perfis de poço' },
  { id: 'R014', name: 'integraA',          name_en: 'integratesTo',       domain: 'SistemaPetrolifero',  range: 'BaciaSedimentar',       inverse: 'possui',             cardinality: 'N:1', description: 'Sistema petrolífero integra-se à bacia' },
  { id: 'R015', name: 'localizadoEmGeo',   name_en: 'locatedInGeo',       domain: 'Poco',                range: 'Bloco',                 inverse: 'contemPoco',         cardinality: 'N:1', description: 'Poço localizado geograficamente em bloco' },
  { id: 'R016', name: 'categorizadoEm',    name_en: 'categorizedAs',      domain: 'Recurso',             range: 'SPE_PRMS_Categoria',    inverse: null,                 cardinality: 'N:1', description: 'Recurso categorizado por SPE-PRMS' },
  { id: 'R017', name: 'derivaDe',          name_en: 'derivedFrom',        domain: 'Reserva',             range: 'Recurso',               inverse: 'originaReserva',     cardinality: '1:1', description: 'Reserva deriva de recurso' },
  { id: 'R018', name: 'imageadoPor',       name_en: 'imagedBy',           domain: 'Horizonte',           range: 'LevantamentoSismico',   inverse: 'imageia',            cardinality: 'N:1', description: 'Horizonte imageado por levantamento sísmico' },
  { id: 'R019', name: 'caracterizadoPor',  name_en: 'characterizedBy',    domain: 'Acumulacao',          range: 'FluidoDeReservatorio',  inverse: 'caracteriza',        cardinality: '1:N', description: 'Acumulação caracterizada por fluido' },
  { id: 'R020', name: 'reguladoPor',       name_en: 'regulatedBy',        domain: 'Bloco',               range: 'ANP',                   inverse: 'regula',             cardinality: 'N:1', description: 'Bloco regulado pela ANP' },
];

export const ONTOPETRO_INSTANCES = [
  { id: 'I001', class: 'BaciaSedimentar',    name: 'Bacia de Santos',          attributes: { area_km2: 352000 },                                            source: 'ANP' },
  { id: 'I002', class: 'BaciaSedimentar',    name: 'Bacia de Campos',          attributes: { area_km2: 115000 },                                            source: 'ANP' },
  { id: 'I003', class: 'BaciaSedimentar',    name: 'Bacia do Solimões',        attributes: { area_km2: 590000 },                                            source: 'ANP' },
  { id: 'I004', class: 'FormacaoGeologica',  name: 'Formação Barra Velha',     attributes: { bacia: 'Bacia de Santos', age: 'Aptiano' },                    source: 'Petrobras' },
  { id: 'I005', class: 'FormacaoGeologica',  name: 'Formação Macabu',          attributes: { bacia: 'Bacia de Campos', age: 'Aptiano' },                    source: 'Petrobras' },
  { id: 'I006', class: 'Campo',              name: 'Campo de Búzios',          attributes: { bacia: 'Bacia de Santos' },                                    source: 'ANP' },
  { id: 'I007', class: 'Campo',              name: 'Campo de Tupi',            attributes: { bacia: 'Bacia de Santos' },                                    source: 'ANP' },
  { id: 'I008', class: 'TrapaPetrolifera',   name: 'Pré-sal da Bacia de Santos', attributes: { tipo: 'Estratigráfico-Estrutural' },                         source: 'Petrobras' },
  { id: 'I009', class: 'Play',               name: 'Play Carbonatos Pré-sal',  attributes: { tipo: 'Estratigráfico' },                                      source: 'SINTEX/Petrobras' },
  { id: 'I010', class: 'SistemaPetrolifero', name: 'SP Lagoa Feia-Macabu',     attributes: { bacia: 'Bacia de Campos' },                                    source: 'GDGEO' },
];

/* ─────────────────────────────────────────────────────────────
 * SPEC 16 — taxonomies.json
 * ───────────────────────────────────────────────────────────── */

export const TAXONOMIES = {
  tipo_litologia: {
    label: 'Tipo de Litologia', label_en: 'Lithology Type',
    values: {
      siliciclastico: { label: 'Siliciclástico', children: ['arenito','conglomerado','folhelho','argilito'] },
      carbonatico:    { label: 'Carbonático',    children: ['calcario','dolomito','marga'] },
    },
  },
  tipo_trapa: {
    label: 'Tipo de Trapa Petrolífera', label_en: 'Petroleum Trap Type',
    values: {
      estrutural:     { label: 'Estrutural',     children: ['anticlinal','falha','domo_sal'] },
      estratigrafico: { label: 'Estratigráfico', children: ['pinch_out','discordancia'] },
      combinado:      { label: 'Combinado',      children: [] },
    },
  },
  tipo_poco: {
    label: 'Tipo de Poço ANP', label_en: 'ANP Well Type',
    description: 'Convenção de nomenclatura ANP: o prefixo numérico indica a categoria',
    values: {
      exploratorio:    { label: 'Exploratório',    prefix: '1-xxx',           examples: ['1-RJS-702-RJ','1-BRSA-944-RJS'] },
      avaliacao:       { label: 'Avaliação',       prefix: '2-xxx',           examples: ['2-ANP-1-RJ'] },
      desenvolvimento: { label: 'Desenvolvimento', prefix: '3-xxx ou 7-xxx',  examples: ['7-BUZ-5-RJS','3-NA-0001-RN'] },
      especial:        { label: 'Especial',        prefix: '4-xxx ou 6-xxx',  examples: [] },
    },
  },
  categoria_recurso_spe_prms: {
    label: 'Categoria de Recurso (SPE-PRMS)', label_en: 'SPE-PRMS Resource Category',
    description: 'Society of Petroleum Engineers — Petroleum Resources Management System',
    rag_alert: "Reserva (SPE-PRMS) ≠ Reserva Ambiental (REBIO/RPPN). Sempre desambiguar.",
    values: {
      reservas: {
        label: 'Reservas',
        children: {
          '1P': { label: 'Provadas (1P)', certainty: 'alta' },
          '2P': { label: 'Prováveis (2P)', certainty: 'média' },
          '3P': { label: 'Possíveis (3P)', certainty: 'baixa' },
        },
      },
      contingentes: {
        label: 'Recursos Contingentes',
        children: { 'C1C': { label: 'C1C' }, 'C2C': { label: 'C2C' }, 'C3C': { label: 'C3C' } },
      },
    },
  },
  tipo_fluido_reservatorio: {
    label: 'Tipo de Fluido de Reservatório', label_en: 'Reservoir Fluid Type',
    values: ['oleo_volatil','oleo_negro','gas_condensado','gas_umido','gas_seco'],
  },
  tipo_querogeno: {
    label: 'Tipo de Querogênio', label_en: 'Kerogen Type',
    values: {
      tipo_I:   { label: 'Tipo I',   origem: 'Lacustre / algas',     produto: 'óleo' },
      tipo_II:  { label: 'Tipo II',  origem: 'Marinho',              produto: 'óleo + gás' },
      tipo_IIS: { label: 'Tipo IIS', origem: 'Marinho com enxofre',  produto: 'óleo rico em S' },
      tipo_III: { label: 'Tipo III', origem: 'Terrígeno / vegetal',  produto: 'gás' },
      tipo_IV:  { label: 'Tipo IV',  origem: 'Inertinita',           produto: 'sem potencial gerador' },
    },
  },
  janela_geracao: {
    label: 'Janela de Geração de Hidrocarbonetos', label_en: 'Hydrocarbon Generation Window',
    description: 'Baseada na reflectância da vitrinita (Ro%)',
    rag_alert: "Janela de Geração ≠ Janela de Lama. A primeira é uma faixa de maturação Ro%; a segunda é o intervalo seguro de peso de lama na perfuração.",
    values: [
      { id: 'imaturo',     label: 'Imaturo',             ro_min: null, ro_max: 0.5,  produto: null },
      { id: 'janela_oleo', label: 'Janela de Óleo',      ro_min: 0.5,  ro_max: 1.0,  produto: 'óleo' },
      { id: 'gas_umido',   label: 'Janela de Gás Úmido', ro_min: 1.0,  ro_max: 1.3,  produto: 'gás úmido' },
      { id: 'gas_seco',    label: 'Janela de Gás Seco',  ro_min: 1.3,  ro_max: 2.0,  produto: 'gás seco' },
      { id: 'sobrematuro', label: 'Sobrematuro',         ro_min: 2.0,  ro_max: null, produto: null },
    ],
  },
  status_qualidade_dado: {
    label: 'Status de Qualidade do Dado', label_en: 'Data Quality Status',
    description: 'Modelo de proveniência do ontopetro Módulo 6',
    values: ['Raso','Verificado','Certificado'],
  },
  confidencialidade: {
    label: 'Confidencialidade', label_en: 'Confidentiality Level',
    values: ['Público','Restrito','Confidencial','Secreto'],
  },
};

/* ─────────────────────────────────────────────────────────────
 * SPEC 17 — modules-extended.json (M7-M10)
 * ───────────────────────────────────────────────────────────── */

export const MODULES_EXTENDED = {
  M7_geochem: {
    label: 'Geoquímica Orgânica e Inorgânica', label_en: 'Organic & Inorganic Geochemistry',
    system_origin: 'GEOQWIN, Rock-Eval, GC',
    classes: [
      { id: 'C101', name: 'AnaliseGeoquimica',   superclass: 'AnalyticalObject',     description: 'Conjunto de análises sobre amostras para caracterização geoquímica' },
      { id: 'C102', name: 'RochaGeneradora',     superclass: 'FormacaoGeologica',    description: 'Rocha rica em matéria orgânica capaz de gerar HC (source rock)' },
      { id: 'C103', name: 'MateriaOrganica',     superclass: 'GeochemicalObject',    description: 'Substância orgânica preservada na rocha com potencial gerador' },
      { id: 'C104', name: 'MaturidadeTermal',    superclass: 'GeochemicalProperty',  description: 'Estado de evolução termal da matéria orgânica (Ro% e Tmax)' },
      { id: 'C105', name: 'CromatografiaDeGas',  superclass: 'AnalyticalMethod',     description: 'GC-FID, GC-TCD, GC-MS — análise da composição dos gases' },
      { id: 'C106', name: 'BioMarcador',         superclass: 'GeochemicalObject',    description: 'Hopanos, esteranos, pristano, fitano para correlação óleo-rocha' },
      { id: 'C107', name: 'CorrelacaoOleoRocha', superclass: 'InterpretationObject', description: 'Análise que associa óleo produzido à rocha geradora via biomarcadores' },
      { id: 'C108', name: 'JanelaDeGeracao',     superclass: 'GeochemicalProperty',  description: 'Faixa de Ro% em que ocorre geração de HC (0.5–2.0%)' },
    ],
    key_properties: [
      { id: 'PG01', name: 'COT',  name_en: 'TOC',  unit: '% peso',        description: 'Carbono Orgânico Total — fundamental para potencial gerador. COT > 2% = excelente' },
      { id: 'PG02', name: 'S1',   unit: 'mg HC/g rocha',                  description: 'HC livres — Rock-Eval, primeiro pico' },
      { id: 'PG03', name: 'S2',   unit: 'mg HC/g rocha',                  description: 'Potencial gerador residual (Rock-Eval) — HC ainda gerável' },
      { id: 'PG04', name: 'S3',   unit: 'mg CO2/g rocha',                 description: 'CO2 liberado durante craqueamento (Rock-Eval)' },
      { id: 'PG05', name: 'IH',   name_en: 'HI', unit: 'mg HC/g COT',     description: 'Índice de Hidrogênio (S2/COT×100) — tipo de querogênio e qualidade do óleo' },
      { id: 'PG06', name: 'IO',   name_en: 'OI', unit: 'mg CO2/g COT',    description: 'Índice de Oxigênio (S3/COT×100)' },
      { id: 'PG07', name: 'Tmax', unit: '°C',                             description: 'Temperatura máxima de craqueamento — proxy de maturidade. Tmax~435°C = janela óleo' },
      { id: 'PG08', name: 'Ro',   unit: '%',                              description: 'Reflectância da Vitrinita — indicador direto de maturidade. Janela óleo: 0.5–1.0%' },
      { id: 'PG09', name: 'tipoQuerogeno',                                description: 'Tipo I/II/IIS/III/IV (ver taxonomia tipo_querogeno)' },
      { id: 'PG10', name: 'razaoC1_C5', unit: '—',                        description: 'Razão metano/pentanos — separa gases secos de úmidos' },
    ],
  },
  M8_rock: {
    label: 'Rocha e Petrofísica', label_en: 'Rock & Petrophysics',
    system_origin: 'GDA, Mineral Solver, RockFinder',
    classes: [
      { id: 'C201', name: 'Litologia',         superclass: 'RockProperty',         description: 'Classificação composicional da rocha (mineralógica e textural)' },
      { id: 'C202', name: 'Mineralogia',       superclass: 'RockProperty',         description: 'Composição mineral identificada (FRX, XRD, Mineral Solver)' },
      { id: 'C203', name: 'FaciesSedimentar',  superclass: 'GeologicalObject',     description: 'Unidade rochosa com características distintas — base de classificação de reservatório' },
      { id: 'C204', name: 'TipoPorosidade',    superclass: 'ReservoirProperty',    description: 'Primária (intergranular), secundária (dissolução/fratura), vugular' },
      { id: 'C205', name: 'SistemaFratura',    superclass: 'RockStructure',        description: 'Conjunto de fraturas naturais que afetam permeabilidade' },
      { id: 'C206', name: 'AnaliseRocha',      superclass: 'AnalyticalObject',     description: 'Análises laboratoriais de rocha (porosimetria, permeametria, MICP)' },
      { id: 'C207', name: 'Dolomitizacao',     superclass: 'DiageneticProcess',    description: 'Substituição de calcita por dolomita — afeta permeabilidade no pré-sal (Castagna)' },
      { id: 'C208', name: 'ModeloPetrofisico', superclass: 'InterpretationObject', description: 'Integra perfis (Den, Neu, Son, NMR) para calcular φ, k, Sw' },
      { id: 'C209', name: 'FaciesDePerfuracao', superclass: 'OperationalObject',   description: 'Classificação litológica em tempo real durante perfuração' },
      { id: 'C210', name: 'RockFinder',        superclass: 'AIObject',             description: 'IA Petrobras (GDA/ML) para sugestão automática de litologia a partir de perfis' },
    ],
    key_properties: [
      { id: 'PR01', name: 'porosidadeTotal_NMR',     unit: '%',  description: 'Porosidade por Ressonância Magnética Nuclear — mais precisa para carbonatos pré-sal' },
      { id: 'PR02', name: 'porosidadeTotal_Den',     unit: '%',  description: 'Porosidade derivada do perfil de densidade (Den)' },
      { id: 'PR03', name: 'porosidadeTotal_Neu',     unit: '%',  description: 'Porosidade derivada do perfil de neutron (Neu)' },
      { id: 'PR04', name: 'porosidadeTotal_Son',     unit: '%',  description: 'Porosidade derivada do perfil sônico (Son)' },
      { id: 'PR05', name: 'permeabilidadeHorizontal', unit: 'mD', description: 'kH — fluxo lateral (direção do acamamento)' },
      { id: 'PR06', name: 'permeabilidadeVertical',  unit: 'mD', description: 'kV — fluxo cruzando camadas. Razão kV/kH crítica para avaliação' },
      { id: 'PR07', name: 'saturacaoAgua_Sw',        unit: '%',  description: 'Saturação de água — equação de Archie (parâmetros m e n)' },
      { id: 'PR08', name: 'fatorArchie_m',           unit: '—',  description: 'Expoente de cementação na equação de Archie' },
      { id: 'PR09', name: 'fatorArchie_n',           unit: '—',  description: 'Expoente de saturação na equação de Archie' },
      { id: 'PR10', name: 'densidadeMatriz',         unit: 'g/cm³', description: 'Densidade da matriz mineral (calcita=2.71, dolomita=2.87, quartzo=2.65)' },
      { id: 'PR15', name: 'classificacaoLitol_IA',   unit: '—',  description: 'Litologia inferida por ML (RockFinder/GDA) — Petrobras' },
    ],
  },
  M9_geomec: {
    label: 'Geomecânica de Reservatório', label_en: 'Reservoir Geomechanics',
    system_origin: 'GEOMECBR, GERESIM, TrapTester, GDA',
    hierarchy_ref: 'GeomechanicsObject.md (arquivo na pasta /dados)',
    classes: [
      { id: 'C301', name: 'ModeloGeomecanico1D',   superclass: 'GeomechanicsObject', description: 'Modelo geomecânico ao longo de um poço (GEOMECBR)' },
      { id: 'C302', name: 'ModeloGeomecanico3D',   superclass: 'GeomechanicsObject', description: 'Modelo volumétrico integrado ao modelo geológico (GERESIM)' },
      { id: 'C303', name: 'CampoTensionalInSitu',  superclass: 'GeomechanicsObject', description: 'Tensores Sv (vertical), SHmax (horiz. max), Shmin (horiz. min)' },
      { id: 'C304', name: 'TensaoVertical',        superclass: 'CampoTensionalInSitu', description: 'Sv — sobrecarga calculada por integração da densidade' },
      { id: 'C305', name: 'TensaoHorizontalMinima', superclass: 'CampoTensionalInSitu', description: 'Shmin — calibrada por LOT/XLOT/Mini-frac' },
      { id: 'C306', name: 'TensaoHorizontalMaxima', superclass: 'CampoTensionalInSitu', description: 'SHmax — orientada por breakouts e fraturas induzidas' },
      { id: 'C307', name: 'PressaoDePoros',        superclass: 'GeomechanicsObject', description: 'Pp — fundamental para tensão efetiva e janela de lama' },
      { id: 'C308', name: 'PropriedadeMecanicaRocha', superclass: 'RockMechanicalProperty', description: 'UCS, E (Young), ν (Poisson), K (bulk), G (shear)' },
      { id: 'C309', name: 'JanelaDeLama',          superclass: 'DrillingObject',     description: 'Intervalo seguro: limInf=colapso, limSup=fratura/perda circulação' },
      { id: 'C310', name: 'Breakout',              superclass: 'OcorrenciaGeomecanica', description: 'Colapso compressivo na direção Shmin — caliper 4 braços ou FMI/UBI' },
      { id: 'C311', name: 'FraturaInduzida',       superclass: 'OcorrenciaGeomecanica', description: 'Fratura criada por perfuração — orientada por SHmax' },
      { id: 'C312', name: 'FraturaNatural',        superclass: 'RockStructure',      description: 'Aberta, mineralizada ou induzida' },
      { id: 'C313', name: 'PotencialSelanteFalha', superclass: 'FaultProperty',      description: 'Capacidade de selo — SGR, CSP, SSF (TrapTester/BEM)' },
      { id: 'C314', name: 'ZonaDeDanoDeFalha',     superclass: 'FaultProperty',      description: 'Volume rochoso adjacente à falha com permeabilidade alterada' },
      { id: 'C315', name: 'CompactacaoReservatorio', superclass: 'DeformationModel', description: 'Compactação por queda de Pp durante produção — afeta φ/k' },
      { id: 'C316', name: 'SubsidenciaSuperficial', superclass: 'DeformationModel', description: 'Afundamento superficial por compactação subterrânea' },
      { id: 'C317', name: 'OcorrenciaGeomecanica', superclass: 'OperationalEvent',   description: 'Breakouts, kick zones, lost circulation, stuck pipe' },
      { id: 'C318', name: 'AnaliseImagemPocoGeomec', superclass: 'AnalyticalObject', description: 'Análise de imagens FMI/UBI para identificar breakouts e fraturas' },
    ],
    key_properties: [
      { id: 'PGM01', name: 'gradienteSv',         unit: 'g/cm³ ou ppg', description: 'Gradiente de tensão vertical' },
      { id: 'PGM02', name: 'gradienteShmin',      unit: 'g/cm³ ou ppg', description: 'Gradiente de Shmin — calibrado por LOT/XLOT' },
      { id: 'PGM03', name: 'gradienteSHmax',      unit: 'g/cm³ ou ppg', description: 'Gradiente de SHmax — calibrado por breakout/fratura induzida' },
      { id: 'PGM04', name: 'orientacaoSHmax',     unit: '°',            description: 'Azimute de SHmax (regional ou local)' },
      { id: 'PGM05', name: 'gradientePressaoPoros', unit: 'g/cm³ ou ppg', description: 'Gradiente de Pp — Eaton, RFT/MDT, sísmica ou Bowers' },
      { id: 'PGM06', name: 'metodoPP',            unit: '—',             description: 'Eaton / RFT / MDT / sísmica / Bowers' },
      { id: 'PGM07', name: 'UCS_estat',           unit: 'MPa',           description: 'UCS estático (lab) — verdadeiro' },
      { id: 'PGM08', name: 'UCS_dinam',           unit: 'MPa',           description: 'UCS dinâmico (DTC/DTS) — correlação interna GDA. Diferença 20–40%' },
      { id: 'PGM10', name: 'E_estat',             unit: 'GPa',           description: 'Módulo de Young estático' },
      { id: 'PGM11', name: 'E_dinam',             unit: 'GPa',           description: 'Módulo de Young dinâmico (DTC/DTS)' },
      { id: 'PGM17', name: 'limiteInferiorLama',  unit: 'g/cm³ ou ppg',  description: 'Peso mínimo de lama para evitar colapso (piso da JanelaDeLama)' },
      { id: 'PGM18', name: 'limiteSuperiorLama',  unit: 'g/cm³ ou ppg',  description: 'Peso máximo de lama para evitar fratura (teto da JanelaDeLama)' },
      { id: 'PGM22', name: 'SGR',                 unit: '%',             description: 'Shale Gouge Ratio — proxy selante. SGR > 18–20% = potencial selante' },
      { id: 'PGM23', name: 'CSP',                 unit: '—',             description: 'Column Sealing Potential (TrapTester)' },
      { id: 'PGM24', name: 'SSF',                 unit: '—',             description: 'Shale Smear Factor (TrapTester)' },
    ],
    cross_module_connections: [
      { from: 'M9', to: 'Poços',         connection: 'JanelaDeLama guia o peso de lama durante a perfuração' },
      { from: 'M9', to: 'M8_rock',       connection: 'DTC/DTS → módulos dinâmicos (E, ν); porosidade → compressibilidade' },
      { from: 'M9', to: 'Reservatório',  connection: 'CompactacaoReservatorio impacta φ/k; PressaoDePoros = input de avaliação' },
      { from: 'M9', to: 'M7_geochem',    connection: 'Falhas extensionais controlam migração de HC e composição das águas de formação' },
    ],
  },
  M10_fluidos: {
    label: 'Fluidos — Geoquímica e PVT', label_en: 'Fluids — Geochemistry & PVT',
    version: 'v0.1', namespace: 'https://petrobras.com.br/geolytics/ontology/',
    system_origin: 'GEOQWIN, SIRR, LIMS Sample Manager, AIDA',
    classes: [
      { id: 'CL_AMOSTRA',       name: 'Amostra',                description: 'Amostra de fluido/óleo/gás/água coletada para análise' },
      { id: 'CL_OLEO',          name: 'Amostra de Óleo',        description: 'Subclasse de Amostra — fluido oleoso' },
      { id: 'CL_GAS',           name: 'Amostra de Gás',         description: 'Subclasse de Amostra — fluido gasoso' },
      { id: 'CL_AGUA',          name: 'Amostra de Água',        description: 'Subclasse de Amostra — água de formação' },
      { id: 'CL_GC_FID',        name: 'Cromatografia Gasosa GC-FID', description: 'Whole Oil quantitativo C6–C35 — base da fingerprint geoquímica' },
      { id: 'CL_GC_MS',         name: 'GC-MS SIM',              description: 'GC + espectrometria de massas — biomarcadores (Pr/Ph, hopanos, esteranos)' },
      { id: 'CL_SARA',          name: 'SARA',                   description: 'Saturados/Aromáticos/Resinas/Asfaltenos — viscosidade e risco de deposição' },
      { id: 'CL_PVT',           name: 'PVT',                    description: 'Flash, ECC, Liberação Diferencial, Viscosidade. Sistema SIRR' },
      { id: 'CL_CARBURANE',     name: 'Carburane',              description: 'Análise de carbon-isotope individual em compostos (CSIA)' },
      { id: 'CL_CLASS_FLUIDO',  name: 'Classe de Fluido',       description: 'Classificação operacional: black oil, óleo volátil, condensado, gás úmido, gás seco. Critérios: API e RGO' },
      { id: 'CL_ANALISE',       name: 'Análise de Fluido',      description: 'Conjunto genérico de análises sobre uma amostra' },
      { id: 'CL_ARTEFATO',      name: 'Artefato Analítico',     description: 'Documento, relatório ou dataset gerado pelas análises' },
    ],
    key_properties: [
      { id: 'PR_API',  name: '°API',         name_en: 'API gravity',  unit: '°API',         description: 'Densidade do óleo. >40=leve, 20–40=médio, <20=pesado. SIRR: Grau API Tanque' },
      { id: 'PR_RGO',  name: 'RGO',          name_en: 'GOR',          unit: 'scf/stb ou m³/m³', description: 'Razão Gás-Óleo. <2000 scf/stb=óleo; >2000=condensado. Completude SIRR: 61.2%' },
      { id: 'PR_PSAT', name: 'Psat',         name_en: 'Saturation Pressure', unit: 'psi',   description: 'Pressão de saturação (bolha p/ óleo, orvalho p/ gás). Completude SIRR: 73.9%' },
      { id: 'PR_PRPH', name: 'Pr/Ph',        unit: '—',                                     description: 'Razão Pristano/Fitano — ambiente deposicional. >3=terrígeno; <1=marinho anóxico' },
      { id: 'PR_TSTM', name: 'Ts/(Ts+Tm)',   unit: '—',                                     description: 'Razão de hopanos — proxy de maturidade' },
      { id: 'PR_SAT',  name: 'Saturados SARA', unit: '%',                                  description: 'Fração de saturados em SARA — alta = óleo leve' },
      { id: 'PR_ASF',  name: 'Asfaltenos SARA', unit: '%',                                 description: 'Fração de asfaltenos — risco de deposição/floculação' },
      { id: 'PR_d13C', name: 'δ13C',         unit: '‰ (IRMS/CSIA)',                        description: 'Isótopo de carbono — correlação óleo-óleo e óleo-rocha' },
    ],
    business_rules_public: [
      { id: 'RN_GQ03', description: 'RGO e API são obrigatórios para classificar tipo de fluido. Se ausentes, marcar como "Não classificado".' },
    ],
    lens_mappings_public: [
      { journey: 'Descobrir',     question: 'O que existe aqui, onde está e qual a cobertura/qualidade?' },
      { journey: 'Classificar',   question: 'Que tipo de fluido é este?' },
      { journey: 'Correlacionar', question: 'O que se relaciona com o quê (óleo-óleo, óleo-rocha)?' },
    ],
  },
};

/* ─────────────────────────────────────────────────────────────
 * SPEC 18 — pvt-dictionary.json (do CSV real do SIRR)
 * ───────────────────────────────────────────────────────────── */

export const PVT_FIELDS = [
  { name: 'Poço',                          type: 'text',  completeness_pct: 100.0, description: 'Identificador do poço ANP' },
  { name: 'Campo',                         type: 'text',  completeness_pct: 92.9,  description: 'Nome do campo de produção' },
  { name: 'Bacia',                         type: 'text',  completeness_pct: 100.0, description: 'Bacia sedimentar' },
  { name: 'Data Amostragem',               type: 'date',  completeness_pct: 100.0, description: 'Data da coleta da amostra' },
  { name: 'Topo(m)',                       type: 'float', completeness_pct: 100.0, unit: 'm', description: 'Topo do intervalo amostrado' },
  { name: 'Base(m)',                       type: 'float', completeness_pct: 95.7,  unit: 'm', description: 'Base do intervalo amostrado' },
  { name: 'Temperatura(°C)',               type: 'float', completeness_pct: 88.8,  unit: '°C', description: 'Temperatura de reservatório' },
  { name: 'Tipo Amostragem',               type: 'text',  completeness_pct: 100.0, description: 'Método de amostragem (fundo/superfície)' },
  { name: 'Data Análise',                  type: 'date',  completeness_pct: 80.5,  description: 'Data do ensaio laboratorial' },
  { name: 'Análise PVT',                   type: 'text',  completeness_pct: 100.0, description: 'Tipo de análise PVT realizada' },
  { name: 'Documento da Análise',          type: 'text',  completeness_pct: 85.3,  description: 'Referência ao certificado/documento' },
  { name: 'Nº Solicitação',                type: 'float', completeness_pct: 100.0, description: 'Identificador da solicitação' },
  { name: 'Dt Operação Estabiliz Poço',    type: 'date',  completeness_pct: 100.0, description: 'Data de estabilização operacional do poço' },
  { name: 'Autoria',                       type: 'text',  completeness_pct: 95.2,  description: 'Laboratório/responsável pela análise' },
  { name: 'Fa Tanque',                     type: 'float', completeness_pct: 1.95,  description: 'Fator de encolhimento em tanque — campo raríssimo (<2%)' },
  { name: 'Dens. Liq Tanque',              type: 'float', completeness_pct: 8.19,  description: 'Densidade do líquido em tanque' },
  { name: 'RGL Tanque',                    type: 'float', completeness_pct: 1.89,  description: 'Razão Gás-Líquido em tanque' },
  { name: 'Dg liberado Tanque',            type: 'float', completeness_pct: 63.1,  description: 'Densidade do gás liberado em tanque' },
  { name: 'Grau API Tanque',               type: 'float', completeness_pct: 63.2,  unit: '°API', description: 'Grau API medido em condições de tanque (superfície)' },
  { name: 'RGO Tanque',                    type: 'float', completeness_pct: 61.2,  unit: 'scf/stb', description: 'Razão Gás-Óleo em condições de tanque' },
  { name: 'Coef Exp Term Tanque',          type: 'float', completeness_pct: 56.6,  description: 'Coeficiente de expansão térmica do tanque' },
  { name: 'Dg Lab',                        type: 'float', completeness_pct: 1.98,  description: 'Densidade do gás em laboratório — campo raríssimo' },
  { name: 'Z Lab',                         type: 'float', completeness_pct: 1.98,  description: 'Fator Z (compressibilidade) em laboratório — raríssimo' },
  { name: 'RGL Lab',                       type: 'float', completeness_pct: 1.98,  description: 'Razão Gás-Líquido em laboratório — raríssimo' },
  { name: 'Dg Média Lib. Dif',             type: 'float', completeness_pct: 58.2,  description: 'Densidade do gás média na liberação diferencial' },
  { name: 'Grau API Óleo Lib. Dif',        type: 'float', completeness_pct: 77.4,  unit: '°API', description: 'Grau API do óleo residual na liberação diferencial' },
  { name: 'Temperatura ºC Lib. Dif',       type: 'float', completeness_pct: 58.2,  unit: '°C', description: 'Temperatura da liberação diferencial' },
  { name: 'Coef. Exp. Term. Lib. Dif',     type: 'float', completeness_pct: 55.2,  description: 'Coef. expansão térmica na liberação diferencial' },
  { name: 'Press. do C.Exp.Term.Lib.Dif',  type: 'float', completeness_pct: 73.9,  unit: 'psi', description: 'Pressão do coef. expansão térmica — proxy Psat' },
  { name: 'Observação',                    type: 'text',  completeness_pct: 14.4,  description: 'Notas livres do analista' },
  { name: 'Data Ult. Atualização',         type: 'date',  completeness_pct: 100.0, description: 'Última atualização do registro' },
  { name: 'Chave Usuário',                 type: 'text',  completeness_pct: 100.0, description: 'Identificador do usuário/operador' },
  { name: 'Fluido Amostra',                type: 'text',  completeness_pct: 100.0, description: 'Tipo de fluido (óleo/gás/água)' },
  { name: 'Experimento',                   type: 'text',  completeness_pct: 100.0, description: 'Tipo de ensaio PVT' },
];

/* ─────────────────────────────────────────────────────────────
 * SPEC 19 — systems.json
 * ───────────────────────────────────────────────────────────── */

export const SYSTEMS = [
  { id: 'GEOQWIN',   name: 'GEOQWIN',                                  type: 'Banco de dados analítico', domain: 'M7 Geoquímica + M10 Fluidos',
    description: 'Banco de dados da Geoquímica Petrobras. Cromatografia (GC-FID, GC-MS), Rock-Eval, SARA, biomarcadores, isótopos e controle de amostras/oleoteca.',
    data_objects: ['Amostras','Cromatogramas GC-FID','GC-MS SIM','Rock-Eval','SARA','δ13C IRMS'] },
  { id: 'SIRR',      name: 'SIRR — Sistema Integrado de Reservatórios', type: 'Base corporativa', domain: 'M10 Fluidos / PVT',
    description: 'Base corporativa Petrobras de dados PVT. Certificados Flash, ECC, liberação diferencial, viscosidade. 35 campos com completude real (ver pvt-dictionary.json).',
    data_objects: ['PVT Flash','ECC','Liberação Diferencial','Viscosidade','API','RGO','Psat'] },
  { id: 'LIMS',      name: 'LIMS Sample Manager',                      type: 'LIMS', domain: 'M7 + M10',
    description: 'Gerenciamento de amostras e resultados laboratoriais. Customizações LF→BDIEP. Interface entre laboratório externo e base corporativa.',
    data_objects: ['SAMPLE','RESULT','TEST','metadados de amostra'] },
  { id: 'AIDA',      name: 'AIDA',                                     type: 'Sistema de classificação', domain: 'M10 Fluidos',
    description: 'Sistema Petrobras para classificação automática do tipo de fluido. Usa API e RGO para classificar: black oil, óleo volátil, condensado, gás úmido, gás seco.',
    data_objects: ['CL_CLASS_FLUIDO','Classificação API+RGO'] },
  { id: 'GDA',       name: 'GDA — Gerenciamento de Dados e Análises',  type: 'Plataforma analítica', domain: 'M8 Rocha + M9 Geomecânica',
    description: 'Plataforma interna Petrobras para processamento de perfis, módulos elásticos dinâmicos (DTC/DTS → E, ν), Mineral Solver, RockFinder (ML litologia), modelagem geomecânica 1D.',
    data_objects: ['Perfis processados','UCS dinâmico','E dinâmico','ν dinâmico','DTC/DTS sintéticos','classificação litológica ML'] },
  { id: 'GEOMECBR',  name: 'GEOMECBR',                                 type: 'Software de modelagem', domain: 'M9 Geomecânica',
    description: 'Software Petrobras para modelagem geomecânica 1D de poços. Gera perfis de JanelaDeLama, UCS, tensões in situ calibrados.',
    data_objects: ['Modelo geomecânico 1D','JanelaDeLama','CampoTensional','UCS calibrado'] },
  { id: 'GERESIM',   name: 'GERESIM',                                  type: 'Software de simulação', domain: 'M9 Geomecânica',
    description: 'Solução Petrobras para modelagem geomecânica 3D volumétrica, integrada ao modelo geológico.',
    data_objects: ['Modelo geomecânico 3D','Subsidência','Compactação de reservatório'] },
  { id: 'TrapTester', name: 'TrapTester / Badley Geoscience',          type: 'Software externo', domain: 'M9 Geomecânica / Estrutural',
    description: 'Análise de potencial selante de falhas. Calcula SGR (Shale Gouge Ratio), CSP, SSF via método BEM.',
    data_objects: ['SGR','CSP','SSF','PotencialSelanteFalha','ZonaDeDanoDeFalha'] },
];

/* ─────────────────────────────────────────────────────────────
 * SPEC 20 — regis-ner-schema.json
 * ───────────────────────────────────────────────────────────── */

export const REGIS_NER_MAPPINGS = [
  { petrogold_type: 'ROC', petrogold_label: 'Rocha',
    geolytics_nodes: ['litologia','facies-sedimentar','rocha-geradora','rocha-capacitante','reservatorio'],
    disambiguation_note: 'ROC = tipo petrográfico (arenito, calcário). Distinguir de FOR (formação = nome de unidade litoestratigráfica). Erro mais comum em NER de O&G PT-BR.',
    example_entities: ['arenito turbidítico','calcário microbialítico','folhelho preto','dolomita'] },
  { petrogold_type: 'FOR', petrogold_label: 'Formação',
    geolytics_nodes: ['formacao'],
    disambiguation_note: 'FOR = nome formal de unidade estratigráfica (Fm. Barra Velha). ≠ ROC (litologia da formação).',
    example_entities: ['Formação Barra Velha','Formação Macabu','Formação Itajaí-Açu','Grupo Lagoa Feia'] },
  { petrogold_type: 'BAC', petrogold_label: 'Bacia Sedimentar',
    geolytics_nodes: ['bacia-sedimentar'],
    disambiguation_note: 'Bacias brasileiras: Santos, Campos, Espírito Santo, Potiguar, Solimões.',
    example_entities: ['Bacia de Santos','Bacia de Campos','Bacia do Espírito Santo'] },
  { petrogold_type: 'CAM', petrogold_label: 'Campo Produtor',
    geolytics_nodes: ['campo'],
    disambiguation_note: 'Campo = área declarada pela ANP. ≠ campo (geográfico) ≠ campo (atributo de dado). Polissemia crítica.',
    example_entities: ['Campo de Búzios','Campo de Tupi','Campo de Libra'] },
  { petrogold_type: 'POC', petrogold_label: 'Poço',
    geolytics_nodes: ['poco'],
    disambiguation_note: 'Identificador ANP. Formato: 1-XXXXX-XX. Tipos por prefixo: 1=exploratório, 3=desenvolvimento, 4=injeção, 7=monitoramento.',
    example_entities: ['1-RJS-0646-RJ','3-NA-0001-RN','7-AG-0001-AM'] },
  { petrogold_type: 'FLU', petrogold_label: 'Fluido de Reservatório',
    geolytics_nodes: ['classe-fluido','amostra-fluido','pvt'],
    disambiguation_note: 'FLU = tipo de fluido (óleo, gás, condensado, água) ou análise. Distinguir de FLU(químico) = fluido de completação.',
    example_entities: ['óleo negro','condensado de gás','gás úmido','água de formação'] },
  { petrogold_type: 'PRP', petrogold_label: 'Propriedade Petrofísica/Geoquímica',
    geolytics_nodes: ['permeabilidade','porosidade','pvt','sara','maturidade-termal'],
    disambiguation_note: 'PRP = atributo numérico com unidade. Inclui: porosidade (%), permeabilidade (mD), COT (%), API (°API), Psat (psi), Tmax (°C), Ro (%).',
    example_entities: ['porosidade de 18%','permeabilidade de 50 mD','COT de 3.2%','Ro = 0.8%'] },
  { petrogold_type: 'IDA', petrogold_label: 'Idade Geológica',
    geolytics_nodes: ['idade-geologica'],
    disambiguation_note: 'IDA = período/época formal (ICS GTS2020). ≠ INT (intervalo estratigráfico).',
    example_entities: ['Aptiano','Albiano','Cretáceo Superior','Paleoceno','Eoceno'] },
  { petrogold_type: 'INT', petrogold_label: 'Intervalo Estratigráfico',
    geolytics_nodes: ['intervalo-estratigrafico'],
    disambiguation_note: 'INT = seção delimitada por dois marcos (topo/base). ≠ IDA (idade). Usado em testagem, completação, avaliação.',
    example_entities: ['intervalo 2100-2450m','zona produtora BVE-110','intervalo de testagem RJS-646'] },
  { petrogold_type: 'ORG', petrogold_label: 'Organização',
    geolytics_nodes: ['operador','anp'],
    disambiguation_note: 'ORG = empresa operadora, parceiro de consórcio, agência reguladora. Mapeado a operador (privado) ou anp (regulador).',
    example_entities: ['Petrobras','Shell','TotalEnergies','ANP','PPSA'] },
];

export const REGIS_RELATION_TYPES = [
  'has_age', 'deposited_in', 'found_in', 'prod_from',
  'correlates_with', 'identified_by', 'has_property',
];

/* ─────────────────────────────────────────────────────────────
 * Layer 6 — Geolytics / Petrobras Internal
 * ───────────────────────────────────────────────────────────── */

export const LAYER6_DEFINITION = {
  id: 'layer6',
  name: 'Geolytics / Petrobras Internal',
  maintainer: 'Petrobras / Geolytics',
  type: 'corporate_internal_ontology',
  namespace: 'https://petrobras.com.br/geolytics/ontology/',
  prefix: 'geo:',
  modules: ['M7 Geoquímica','M8 Rocha','M9 Geomecânica','M10 Fluidos'],
  systems: ['GEOQWIN','SIRR','LIMS','BDIEP','AIDA','GDA','GEOMECBR','GERESIM','TrapTester'],
  internal_standards: ['PE-2E&P-00531','PE-2E&P-00463','PE-2P&D-00189'],
  description: 'Ontologia operacional interna da Petrobras para o Geolytics, com namespace próprio e ligação a sistemas corporativos. Inclui apenas definições conceituais públicas — dados Sigilo=Interno não são publicados aqui.',
  status: 'v0.1 Preliminar/Interno',
  publication_policy: 'Apenas definições conceituais + estrutura de classes/propriedades. NÃO incluir dados operacionais reais nem configurações de sistemas.',
  geolytics_coverage: 'all_modules_extended',
};

/* ─────────────────────────────────────────────────────────────
 * Extensão do entity-graph com nós ontopetro + M7-M10
 * (curado para preservar legibilidade do grafo)
 * ───────────────────────────────────────────────────────────── */

export const ONTOPETRO_NODES = [
  /* operational/geological extensions */
  { id: 'rocha-geradora',     label: 'Rocha Geradora',     label_en: 'Source Rock',     type: 'geological',
    definition: 'Rocha rica em matéria orgânica (COT > 1%) capaz de gerar HC quando submetida à temperatura adequada. Equivale a C005 em ontopetro.',
    fonte: 'GeoCore / ontopetro C005' },
  { id: 'rocha-capacitante',  label: 'Rocha Capacitante',  label_en: 'Cap Rock',        type: 'geological',
    definition: 'Rocha de baixa permeabilidade que sela o reservatório, impedindo migração de HC para fora da trapa. Equivale a C004 em ontopetro.',
    fonte: 'GeoCore / ontopetro C004' },
  { id: 'trapa',              label: 'Trapa',              label_en: 'Petroleum Trap',  type: 'geological',
    definition: 'Configuração geológica (estrutural, estratigráfica ou combinada) que permite acúmulo de HC. C006 em ontopetro.',
    fonte: 'PPDM / ontopetro C006' },
  { id: 'sistema-petrolifero',label: 'Sistema Petrolífero',label_en: 'Petroleum System',type: 'geological',
    definition: 'Conjunto integrado de rocha geradora, migração, reservatório, capa e trapa. C007 em ontopetro.',
    fonte: 'PPDM / GeoCore' },
  { id: 'acumulacao',         label: 'Acumulação',         label_en: 'Hydrocarbon Accumulation', type: 'operational',
    definition: 'Volume de HC contido em armadilha com dimensões definidas. Precede a Declaração de Comercialidade. C008 em ontopetro.',
    fonte: 'PPDM / ontopetro C008' },
  { id: 'play',               label: 'Play',               label_en: 'Play',            type: 'operational',
    definition: 'Combinação de elementos petrolíferos com potencial exploratório regional. C017 em ontopetro.',
    fonte: 'PPDM / ontopetro C017' },
  { id: 'prospecto',          label: 'Prospecto',          label_en: 'Prospect',        type: 'operational',
    definition: 'Área específica com potencial para acumulação, dentro de um play. C018 em ontopetro.',
    fonte: 'PPDM / ontopetro C018' },
  { id: 'recurso',            label: 'Recurso',            label_en: 'Resource',        type: 'contractual',
    definition: 'Volume de HC com grau variável de certeza geológica. Categorizado por SPE-PRMS. C019 em ontopetro.',
    fonte: 'ANP / SPE-PRMS / ontopetro C019' },
  { id: 'reserva',            label: 'Reserva',            label_en: 'Reserve',         type: 'contractual',
    definition: 'Volume de HC tecnicamente recuperável e economicamente viável. Categorias 1P/2P/3P. C020 em ontopetro. NÃO confundir com Reserva Ambiental.',
    fonte: 'ANP / SPE-PRMS / ontopetro C020' },
  { id: 'falha',              label: 'Falha Geológica',    label_en: 'Geological Fault',type: 'geological',
    definition: 'Descontinuidade tectônica com deslocamento relativo das camadas. C016 em ontopetro.',
    fonte: 'GeoCore / ontopetro C016' },
  { id: 'idade-geologica',    label: 'Idade Geológica',    label_en: 'Geological Age',  type: 'geological',
    definition: 'Período/época formal segundo ICS GTS2020. Ex.: Aptiano, Albiano, Cretáceo Superior. Tipo NER PetroGold IDA.',
    fonte: 'ICS GTS2020 / PetroGold' },
  { id: 'intervalo-estratigrafico', label: 'Intervalo Estratigráfico', label_en: 'Stratigraphic Interval', type: 'geological',
    definition: 'Seção de poço delimitada por dois marcos (topo/base). Usado em testagem, completação e avaliação. NÃO confundir com Idade. Tipo NER PetroGold INT.',
    fonte: 'PetroGold / Petrobras' },
  { id: 'testemunho',         label: 'Testemunho',         label_en: 'Core Sample',     type: 'analytical',
    definition: 'Amostra cilíndrica de rocha extraída durante perfuração. C012 em ontopetro.',
    fonte: 'GDGEO / ontopetro C012' },
  { id: 'perfil-poco',        label: 'Perfil de Poço',     label_en: 'Well Log',        type: 'analytical',
    definition: 'Medição contínua de propriedades físicas ao longo do poço (gamma, densidade, sônico, neutron, NMR). C013 em ontopetro.',
    fonte: 'PPDM / ontopetro C013' },

  /* M7 Geoquímica */
  { id: 'materia-organica',   label: 'Matéria Orgânica',   label_en: 'Organic Matter',  type: 'analytical',
    definition: 'Substância orgânica preservada na rocha geradora com potencial de gerar HC. Caracterizada por Rock-Eval e tipo de querogênio (I/II/IIS/III/IV). M7 C103.',
    fonte: 'GEOQWIN / Rock-Eval' },
  { id: 'maturidade-termal',  label: 'Maturidade Termal',  label_en: 'Thermal Maturity',type: 'analytical',
    definition: 'Estado de evolução termal medido por Ro% (vitrinita) e Tmax (Rock-Eval). Janela óleo: Ro 0.5–1.0%, Tmax ~435°C. M7 C104.',
    fonte: 'GEOQWIN' },
  { id: 'biomarcador',        label: 'Biomarcador',        label_en: 'Biomarker',       type: 'analytical',
    definition: 'Composto orgânico preservado (hopanos, esteranos, pristano, fitano) usado para correlação óleo-rocha via GC-MS. M7 C106.',
    fonte: 'GEOQWIN / GC-MS SIM' },
  { id: 'correlacao-oleo-rocha', label: 'Correlação Óleo-Rocha', label_en: 'Oil-Source Correlation', type: 'analytical',
    definition: 'Análise que associa hidrocarbonetos produzidos à rocha geradora de origem via assinatura de biomarcadores e isótopos. M7 C107.',
    fonte: 'GEOQWIN' },

  /* M8 Rocha */
  { id: 'litologia',          label: 'Litologia',          label_en: 'Lithology',       type: 'analytical',
    definition: 'Classificação composicional da rocha. Pode ser inferida por ML (RockFinder/GDA). NÃO confundir com formação (FOR ≠ ROC em PetroGold). M8 C201.',
    fonte: 'GDA / RockFinder' },
  { id: 'facies-sedimentar',  label: 'Fácies Sedimentar',  label_en: 'Sedimentary Facies', type: 'analytical',
    definition: 'Unidade rochosa com características físicas e biológicas distintas — base de classificação de reservatório. M8 C203.',
    fonte: 'Petrobras / GeoCore' },
  { id: 'modelo-petrofisico', label: 'Modelo Petrofísico', label_en: 'Petrophysical Model', type: 'analytical',
    definition: 'Integra perfis (Den, Neu, Son, NMR) para calcular φ, k, Sw via equação de Archie. M8 C208.',
    fonte: 'GDA' },

  /* M9 Geomecânica */
  { id: 'campo-tensional',    label: 'Campo Tensional',    label_en: 'In-Situ Stress Field', type: 'analytical',
    definition: 'Conjunto Sv (vertical), SHmax (horizontal máximo), Shmin (horizontal mínimo). Base do modelo geomecânico. M9 C303.',
    fonte: 'GEOMECBR / GERESIM' },
  { id: 'janela-lama',        label: 'Janela de Lama',     label_en: 'Mud Weight Window',type: 'analytical',
    definition: 'Intervalo seguro de peso de lama: limite inferior=colapso (breakout), limite superior=fratura (perda circulação). NÃO confundir com Janela de Geração (Ro%). M9 C309.',
    fonte: 'GEOMECBR' },
  { id: 'ocorrencia-geomec',  label: 'Ocorrência Geomecânica', label_en: 'Geomechanical Event', type: 'analytical',
    definition: 'Eventos: breakouts, kick zones, lost circulation, stuck pipe. Indicadores de problemas operacionais. M9 C317.',
    fonte: 'GEOMECBR / Petrobras' },
  { id: 'potencial-selante',  label: 'Potencial Selante',  label_en: 'Fault Sealing Potential', type: 'analytical',
    definition: 'Capacidade de falha reter HC — calculado por SGR (Shale Gouge Ratio), CSP e SSF no TrapTester. SGR > 18–20% = potencial selante. M9 C313.',
    fonte: 'TrapTester / Badley' },

  /* M10 Fluidos */
  { id: 'amostra-fluido',     label: 'Amostra de Fluido',  label_en: 'Fluid Sample',    type: 'analytical',
    definition: 'Amostra de óleo/gás/água coletada para análise laboratorial. M10 CL_AMOSTRA.',
    fonte: 'LIMS Sample Manager' },
  { id: 'pvt',                label: 'PVT',                label_en: 'PVT Analysis',    type: 'analytical',
    definition: 'Ensaios pressão-volume-temperatura: Flash, ECC, Liberação Diferencial, Viscosidade. Sistema SIRR (35 campos com completude documentada). M10 CL_PVT.',
    fonte: 'SIRR' },
  { id: 'classe-fluido',      label: 'Classe de Fluido',   label_en: 'Fluid Class',     type: 'analytical',
    definition: 'Classificação operacional: black oil, óleo volátil, condensado, gás úmido, gás seco. Critérios: API e RGO. Sistema AIDA. M10 CL_CLASS_FLUIDO.',
    fonte: 'AIDA' },
  { id: 'gc-ms',              label: 'GC-MS',              label_en: 'GC-MS SIM',       type: 'analytical',
    definition: 'Cromatografia gasosa com espectrometria de massas para biomarcadores (Pr/Ph, hopanos, esteranos). M10 CL_GC_MS.',
    fonte: 'GEOQWIN' },
  { id: 'sara',               label: 'SARA',               label_en: 'SARA',            type: 'analytical',
    definition: 'Saturados/Aromáticos/Resinas/Asfaltenos — fracionamento do óleo bruto. Correlaciona com viscosidade e risco de deposição. M10 CL_SARA.',
    fonte: 'GEOQWIN' },
];

export const ONTOPETRO_EDGES = [
  /* Sistema petrolífero — relações fundamentais */
  { source: 'rocha-geradora',     target: 'materia-organica',   relation: 'contains',         relation_label: 'contém',                  style: 'solid' },
  { source: 'rocha-geradora',     target: 'sistema-petrolifero',relation: 'feeds',            relation_label: 'alimenta',                style: 'solid' },
  { source: 'maturidade-termal',  target: 'rocha-geradora',     relation: 'characterizes',    relation_label: 'caracteriza',             style: 'solid' },
  { source: 'rocha-capacitante',  target: 'reservatorio',       relation: 'seals',            relation_label: 'sela',                    style: 'solid' },
  { source: 'trapa',              target: 'reservatorio',       relation: 'comprises',        relation_label: 'comporta',                style: 'solid' },
  { source: 'trapa',              target: 'acumulacao',         relation: 'contains',         relation_label: 'contém',                  style: 'solid' },
  { source: 'sistema-petrolifero',target: 'bacia-sedimentar',   relation: 'integrates_to',    relation_label: 'integra-se a',            style: 'solid' },
  { source: 'acumulacao',         target: 'campo',              relation: 'becomes',          relation_label: 'origina',                 style: 'solid' },
  { source: 'campo',              target: 'reserva',            relation: 'declares',         relation_label: 'declara',                 style: 'dashed' },
  { source: 'reserva',            target: 'recurso',            relation: 'derived_from',     relation_label: 'deriva de',               style: 'solid' },
  { source: 'play',               target: 'prospecto',          relation: 'spawns',           relation_label: 'gera',                    style: 'dashed' },
  { source: 'prospecto',          target: 'acumulacao',         relation: 'becomes',          relation_label: 'pode tornar-se',          style: 'dashed' },
  { source: 'falha',              target: 'trapa',              relation: 'forms',            relation_label: 'compõe',                  style: 'dashed' },
  { source: 'falha',              target: 'potencial-selante',  relation: 'has_property',     relation_label: 'tem propriedade',         style: 'solid' },

  /* Estratigrafia / amostragem */
  { source: 'formacao',           target: 'idade-geologica',    relation: 'has_age',          relation_label: 'tem idade',               style: 'solid' },
  { source: 'poco',               target: 'intervalo-estratigrafico', relation: 'samples',    relation_label: 'amostra',                 style: 'dashed' },
  { source: 'testemunho',         target: 'formacao',           relation: 'samples',          relation_label: 'amostra',                 style: 'solid' },
  { source: 'perfil-poco',        target: 'poco',               relation: 'measures',         relation_label: 'mede',                    style: 'solid' },
  { source: 'perfil-poco',        target: 'litologia',          relation: 'infers',           relation_label: 'infere',                  style: 'dashed' },

  /* M7-M10 análises */
  { source: 'biomarcador',        target: 'correlacao-oleo-rocha', relation: 'enables',       relation_label: 'permite',                 style: 'solid' },
  { source: 'biomarcador',        target: 'amostra-fluido',     relation: 'derived_from',     relation_label: 'extraído de',             style: 'dashed' },
  { source: 'gc-ms',              target: 'biomarcador',        relation: 'detects',          relation_label: 'detecta',                 style: 'solid' },
  { source: 'amostra-fluido',     target: 'pvt',                relation: 'undergoes',        relation_label: 'submetida a',             style: 'dashed' },
  { source: 'amostra-fluido',     target: 'sara',               relation: 'undergoes',        relation_label: 'submetida a',             style: 'dashed' },
  { source: 'pvt',                target: 'classe-fluido',      relation: 'classifies',       relation_label: 'classifica',              style: 'solid' },
  { source: 'pvt',                target: 'reservatorio',       relation: 'characterizes',    relation_label: 'caracteriza fluido de',   style: 'solid' },
  { source: 'correlacao-oleo-rocha', target: 'rocha-geradora',  relation: 'links_to',         relation_label: 'traça origem em',         style: 'solid' },
  { source: 'classe-fluido',      target: 'reservatorio',       relation: 'characterizes',    relation_label: 'caracteriza',             style: 'dashed' },
  { source: 'modelo-petrofisico', target: 'reservatorio',       relation: 'characterizes',    relation_label: 'caracteriza',             style: 'solid' },
  { source: 'facies-sedimentar',  target: 'reservatorio',       relation: 'composes',         relation_label: 'compõe',                  style: 'solid' },
  { source: 'campo-tensional',    target: 'janela-lama',        relation: 'defines',          relation_label: 'define',                  style: 'solid' },
  { source: 'janela-lama',        target: 'poco',               relation: 'guides_drilling_of', relation_label: 'guia perfuração de',    style: 'solid' },
  { source: 'ocorrencia-geomec',  target: 'poco',               relation: 'occurs_in',        relation_label: 'ocorre em',               style: 'dashed' },

  /* Recurso/Reserva ↔ Bloco/Operador */
  { source: 'recurso',            target: 'bloco',              relation: 'allocated_to',     relation_label: 'alocado em',              style: 'dashed' },
  { source: 'operador',           target: 'recurso',            relation: 'reports',          relation_label: 'reporta',                 style: 'solid' },
];

/* Alinhamento ontológico para os novos nós (subset) */
export const ONTOPETRO_ALIGNMENT = {
  'rocha-geradora':           { kg: '#SourceRock',        osdu: null, layers: ['layer1','layer2','layer3','layer6'] },
  'rocha-capacitante':        { kg: '#CapRock',           osdu: null, layers: ['layer1','layer2','layer3'] },
  'trapa':                    { kg: '#PetroleumTrap',     osdu: null, layers: ['layer1','layer3'] },
  'sistema-petrolifero':      { kg: '#PetroleumSystem',   osdu: null, layers: ['layer1','layer3'] },
  'acumulacao':               { kg: '#HydrocarbonAccumulation', osdu: null, layers: ['layer2','layer3','layer4'] },
  'play':                     { kg: '#Play',              osdu: null, layers: ['layer3'] },
  'prospecto':                { kg: '#Prospect',          osdu: null, layers: ['layer3'] },
  'recurso':                  { kg: '#Resource',          osdu: null, layers: ['layer3','layer5'] },
  'reserva':                  { kg: '#Reserve',           osdu: null, layers: ['layer3','layer5'] },
  'falha':                    { kg: '#GeologicalFault',   osdu: null, layers: ['layer1','layer3'] },
  'idade-geologica':          { kg: null,                 osdu: null, layers: ['layer1','layer3'] },
  'intervalo-estratigrafico': { kg: null,                 osdu: null, layers: ['layer4','layer6'] },
  'testemunho':               { kg: '#Core',              osdu: null, layers: ['layer4','layer6'] },
  'perfil-poco':              { kg: '#WellLog',           osdu: 'opendes:osdu:work-product-component--WellLog:1.0.0', layers: ['layer3','layer4','layer6'] },
  'materia-organica':         { kg: null, osdu: null, layers: ['layer3','layer6'] },
  'maturidade-termal':        { kg: null, osdu: null, layers: ['layer3','layer6'] },
  'biomarcador':              { kg: null, osdu: null, layers: ['layer6'] },
  'correlacao-oleo-rocha':    { kg: null, osdu: null, layers: ['layer6'] },
  'litologia':                { kg: '#Lithology',         osdu: null, layers: ['layer1','layer2','layer3','layer6'] },
  'facies-sedimentar':        { kg: null, osdu: null, layers: ['layer2','layer6'] },
  'modelo-petrofisico':       { kg: null, osdu: null, layers: ['layer6'] },
  'campo-tensional':          { kg: null, osdu: null, layers: ['layer6'] },
  'janela-lama':              { kg: null, osdu: null, layers: ['layer6'] },
  'ocorrencia-geomec':        { kg: null, osdu: null, layers: ['layer6'] },
  'potencial-selante':        { kg: null, osdu: null, layers: ['layer6'] },
  'amostra-fluido':           { kg: null, osdu: 'opendes:osdu:master-data--Sample:1.0.0', layers: ['layer4','layer6'] },
  'pvt':                      { kg: null, osdu: null, layers: ['layer6'] },
  'classe-fluido':            { kg: null, osdu: null, layers: ['layer6'] },
  'gc-ms':                    { kg: null, osdu: null, layers: ['layer6'] },
  'sara':                     { kg: null, osdu: null, layers: ['layer6'] },
};

/* ─────────────────────────────────────────────────────────────
 * Ambiguity alerts (chunks RAG críticos)
 * ───────────────────────────────────────────────────────────── */

export const AMBIGUITY_ALERTS = [
  { id: 'ambig_rgo_gor',                terms: ['RGO','GOR'],
    text: 'RGO (Razão Gás-Óleo, em PT-BR) ≡ GOR (Gas-Oil Ratio, em EN). São SINÔNIMOS, não conceitos diferentes. Unidade típica: scf/stb (EN) ou m³/m³ (PT/SI). Nas bases corporativas Petrobras (SIRR), o campo é "RGO Tanque" com 61.2% de completude. Use os dois termos como equivalentes em qualquer pipeline NLP.' },
  { id: 'ambig_janela_lama_geracao',    terms: ['Janela de Lama','Janela de Geração'],
    text: 'CONCEITOS DISTINTOS — não confundir. (a) Janela de Lama (Mud Weight Window): intervalo seguro de peso de lama durante perfuração; limite inferior = colapso/breakout, limite superior = fratura/perda de circulação. Domínio: M9 Geomecânica. (b) Janela de Geração de HC: faixa de maturidade termal (Ro%) em que ocorre geração de hidrocarbonetos: 0.5–1.0% janela óleo, 1.0–1.3% gás úmido, 1.3–2.0% gás seco. Domínio: M7 Geoquímica.' },
  { id: 'ambig_ucs_estatico_dinamico',  terms: ['UCS estático','UCS dinâmico'],
    text: 'UCS estático ≠ UCS dinâmico. (a) UCS estático: medido em laboratório (lab) — valor verdadeiro de resistência compressiva uniaxial. (b) UCS dinâmico: calculado a partir de perfis sônicos (DTC/DTS) por correlação interna GDA/Petrobras. Diferença típica entre os dois: 20–40%. Não usar dinâmico para projeto sem calibração com estático.' },
  { id: 'ambig_porosidade_perfis',      terms: ['NMR','Den','Neu','Son'],
    text: 'Porosidade NÃO é única — depende do perfil. (a) NMR (Ressonância Magnética Nuclear): mais precisa para carbonatos pré-sal. (b) Den (Densidade): assume densidade da matriz; erro alto em rochas heterogêneas. (c) Neu (Neutron): sensível ao hidrogênio (água + óleo). (d) Son (Sônico): subestima em carbonatos. Em datasets Petrobras a coluna é tipicamente porosidadeTotal_NMR/_Den/_Neu/_Son.' },
  { id: 'ambig_api_tanque_reservatorio',terms: ['API Tanque','API Reservatório'],
    text: 'Grau API "Tanque" ≠ "Reservatório". API Tanque: medido em condições de superfície (após gás ter saído). API Reservatório: in situ, com gás dissolvido. SIRR campo: "Grau API Tanque" (63.2% completude) é o mais comum em relatórios. Não confundir.' },
  { id: 'ambig_sv_shmin_shmax',         terms: ['Sv','Shmin','SHmax'],
    text: 'Os 3 tensores do CampoTensionalInSitu (M9 C303) são distintos: Sv (vertical, sobrecarga), Shmin (horizontal mínimo, calibrado por LOT/XLOT), SHmax (horizontal máximo, orientado por breakouts). Em regiões extensionais Sv > SHmax > Shmin (regime normal). Em compressionais SHmax > Sv. Cuidado com a ordem ao discutir regime tectônico.' },
  { id: 'ambig_sara_fractions',         terms: ['Saturados','Aromáticos','Resinas','Asfaltenos'],
    text: 'SARA = Saturados / Aromáticos / Resinas / Asfaltenos. Fracionamento do óleo bruto. Saturados altos = óleo leve, fluido. Asfaltenos altos = risco de deposição/floculação em produção (problema operacional). Resinas atuam como dispersantes naturais dos asfaltenos. Sistema-fonte: GEOQWIN.' },
  { id: 'ambig_reserva_polissemia',     terms: ['Reserva'],
    text: 'POLISSEMIA — "Reserva" tem múltiplos significados: (a) Reserva SPE-PRMS (econômico): volume de HC recuperável e viável (1P/2P/3P). (b) Reservatório (geológico): rocha porosa que armazena HC. (c) Reserva Ambiental (REBIO/RPPN): área de proteção ambiental. (d) Reservas Estratégicas (regulatório, EGREP em Portugal). Sempre desambiguar pelo contexto.' },
  { id: 'ambig_cot_toc',                terms: ['COT','TOC'],
    text: 'COT (Carbono Orgânico Total, PT-BR) ≡ TOC (Total Organic Carbon, EN). SINÔNIMOS. Unidade: % em peso da rocha. COT > 1% = potencial gerador; > 2% = excelente. M7 Geoquímica, parâmetro fundamental Rock-Eval.' },
  { id: 'ambig_kh_kv',                  terms: ['kH','kV'],
    text: 'Permeabilidade NÃO é escalar. kH (horizontal): fluxo na direção do acamamento. kV (vertical): fluxo cruzando camadas. Razão kV/kH varia de 0.001 (folhelhos) a 1.0 (rochas isotrópicas). Sempre crítico para avaliação de reservatório, especialmente em águas profundas.' },
  { id: 'ambig_campo_polissemia',       terms: ['campo'],
    text: 'POLISSEMIA crítica em PT-BR para LLMs: "campo" pode ser: (a) Campo (ANP/PPDM): área produtora declarada (Búzios, Tupi). (b) campo (atributo de dado): coluna de tabela/JSON. (c) campo (geográfico): área aberta. (d) Campo Tensional: domínio M9 Geomecânica. Em NER (PetroGold tipo CAM) só (a) é entidade. Sempre desambiguar pelo contexto.' },
  { id: 'ambig_formacao_vs_litologia',  terms: ['formação','litologia'],
    text: 'NER PetroGold distingue: FOR (Formação) ≠ ROC (Litologia). FOR = nome formal de unidade litoestratigráfica (Fm. Barra Velha, Fm. Macabu). ROC = tipo petrográfico (arenito, calcário microbialítico, folhelho). A formação tem uma litologia, mas não é a litologia. Erro mais comum em NER de O&G PT-BR.' },
  { id: 'ambig_intervalo_estratigrafico', terms: ['intervalo','idade'],
    text: 'PetroGold tipos INT (Intervalo) ≠ IDA (Idade). INT = seção delimitada por dois marcos (topo/base) — ex.: "intervalo 2100-2450m", "zona produtora BVE-110". IDA = período/época formal — ex.: "Aptiano", "Cretáceo Superior". Um intervalo TEM uma idade, mas não é a idade.' },
  { id: 'osdu_well_wellbore_disambiguation', terms: ['Well','Wellbore'],
    text: "ALERTA RAG — Well vs Wellbore (OSDU): São duas entidades distintas no OSDU que a ANP conflate em um registro único. WELL = registro de superfície e legal. O número POCO_NUM da ANP corresponde ao Well.WellID. WELLBORE = o trecho físico perfurado. Um Well pode ter múltiplos Wellbores (sidetrack: ST1, ST2…). Na prática para o Geolytics: 1 poço ANP sem sidetrack = 1 Well + 1 Wellbore. A entidade 'poco' do entity-graph corresponde ao Well OSDU. A entidade 'wellbore' é granularidade adicional para workflows de integração IT. NUNCA use 'poço' e 'wellbore' como sinônimos em contexto OSDU — eles são entidades com IDs diferentes e ciclos de vida diferentes." },
];

/* ─────────────────────────────────────────────────────────────
 * OSDU Layer 4 — increment v2
 *   4 novos nós, 7 edges, 4 chunks RAG (master/reference/wpc/lineage)
 *   O ambiguity_alert OSDU já está em AMBIGUITY_ALERTS acima.
 * ───────────────────────────────────────────────────────────── */

export const OSDU_NODES = [
  { id: 'wellbore', label: 'Trecho Perfurado', label_en: 'Wellbore', type: 'operational',
    definition: "Trecho físico perfurado de um poço. Um poço ANP (registro superficial + legal) pode ter múltiplos wellbores em caso de sidetrack ou completação multilateral. Na prática, 1 poço ANP sem sidetrack = 1 wellbore. OSDU separa formalmente Well (registro de superfície) de Wellbore (trecho perfurado físico). O número ANP POCO_NUM corresponde ao Well.WellID no OSDU; o wellbore é gerado automaticamente.",
    fonte: 'ANP/BDP + OSDU master-data--Wellbore',
    datasets: ['pocos-exploratorios'],
    osdu_kind_override: 'opendes:osdu:master-data--Wellbore:1.0.0',
    layers_override: ['layer2','layer3','layer4'],
    synonyms_pt: ['trecho perfurado', 'furo', 'wellbore', 'poço físico'],
    synonyms_en: ['wellbore', 'borehole', 'drilled hole'],
    examples: ['1-RJS-702-RJ (wellbore único)', '3-NA-0001-RN-ST1 (sidetrack = segundo wellbore)'],
    size: 22 },

  { id: 'topo-formacional', label: 'Topo Formacional', label_en: 'Formation Top / Wellbore Marker', type: 'analytical',
    definition: "Pick da profundidade (em MD — Measured Depth — e TVD — True Vertical Depth) em que o wellbore intercepta o topo de uma formação geológica. Dado fundamental em correlações estratigráficas entre poços e na construção de modelos de reservatórios 3D. Exemplo: Topo da Formação Barra Velha no poço 1-RJS-702-RJ a MD=4220m / TVD=4105m.",
    fonte: 'Relatórios de completação / OSDU WellboreMarker',
    datasets: ['pocos-exploratorios'],
    osdu_kind_override: 'opendes:osdu:work-product-component--WellboreMarker:1.0.0',
    layers_override: ['layer2','layer3','layer4'],
    synonyms_pt: ['topo de formação', 'marco estratigráfico', 'pick estratigráfico', 'marker'],
    synonyms_en: ['formation top', 'wellbore marker', 'stratigraphic pick', 'formation pick'],
    examples: ['Topo Fm. Barra Velha a 4220m MD', 'Topo Fm. Macaé a 2890m MD', 'Base do Sal a 3410m TVD'],
    size: 18 },

  { id: 'trajetoria-poco', label: 'Trajetória do Poço', label_en: 'Wellbore Trajectory', type: 'analytical',
    definition: "Survey direcional do wellbore: sequência de medições de profundidade (MD), inclinação e azimute ao longo do trecho perfurado. Permite calcular a posição 3D real do poço (TVD, offsets Norte/Sul/Leste/Oeste). Diferencia poços verticais (inclinação ≈ 0°) de poços direcionais (inclinação > 30°) e poços horizontais (inclinação ≈ 90°). Essencial para visualização 3D de poços offshore e para o cálculo correto de pressão hidrostática.",
    fonte: 'Relatórios de completação / OSDU WellboreTrajectory',
    datasets: ['pocos-exploratorios'],
    osdu_kind_override: 'opendes:osdu:work-product-component--WellboreTrajectory:1.0.0',
    layers_override: ['layer3','layer4'],
    synonyms_pt: ['trajetória direcional', 'survey direcional', 'desvio do poço', 'perfil direcional'],
    synonyms_en: ['wellbore trajectory', 'directional survey', 'deviation survey', 'trajectory survey'],
    examples: ['Poço horizontal pré-sal: 60° inclinação em 2800m TVD', 'Poço vertical 1-RJS-702-RJ: inclinação < 3°'],
    size: 16 },

  { id: 'completacao', label: 'Completação', label_en: 'Well Completion', type: 'operational',
    definition: "Conjunto de operações e equipamentos instalados no poço após a perfuração para viabilizar a produção segura: revestimento de produção, tubing (coluna de produção), packers, válvulas de subsuperfície (DHSV), perforações (canhoneio) das zonas produtoras e árvore de natal. No OSDU corresponde a master-data--WellboreCompletion, vinculado ao Wellbore. Tipos: completação seca (dry tree, plataforma fixa), molhada (subsea com ANM) ou inteligente (smart well — múltiplas zonas controladas).",
    fonte: 'O3PO (UFRGS) / OSDU master-data--WellboreCompletion',
    datasets: [],
    osdu_kind_override: 'opendes:osdu:master-data--WellboreCompletion:1.0.0',
    layers_override: ['layer2','layer3','layer4'],
    synonyms_pt: ['completação', 'acabamento de poço', 'completion'],
    synonyms_en: ['well completion', 'completion'],
    examples: ['Completação seca (dry tree)', 'Completação molhada subsea com ANM', 'Completação inteligente (smart well)'],
    size: 18 },

  { id: 'unidade-medida', label: 'Unidade de Medida', label_en: 'Unit of Measure', type: 'instrument',
    definition: "Vocabulário controlado de unidades de medida usadas nos dados de subsuperfície. Crítico para interoperabilidade entre sistemas: ANP/Petrobras usa SI (metros, MPa, m³/d) enquanto dados legados e internacionais frequentemente usam sistema imperial (ft, psi, bbl/d). O mD (miliDarcy) é um caso especial — unidade do sistema CGS-Gaussian amplamente usada em petrofísica. A conversão de unidades sem referência ao vocabulário OSDU é fonte frequente de erros em integração de dados.",
    fonte: 'OSDU reference-data--UnitOfMeasure / BIPM SI / API standards',
    datasets: [],
    osdu_kind_override: 'opendes:osdu:reference-data--UnitOfMeasure:1.0.0',
    layers_override: ['layer2','layer3','layer4'],
    synonyms_pt: ['unidade', 'unidade SI', 'unidade imperial', 'UOM'],
    synonyms_en: ['unit of measure', 'UOM', 'unit', 'measurement unit'],
    examples: ['mD (miliDarcy) — permeabilidade', 'ºAPI (API gravity) — densidade óleo', 'GAPI (Gamma Ray API) — argilosidade'],
    size: 14 },
];

export const OSDU_EDGES = [
  { source: 'poco',         target: 'wellbore',         relation: 'has_wellbore',     relation_label: 'tem wellbore',     style: 'solid' },
  { source: 'wellbore',     target: 'poco',             relation: 'belongs_to',       relation_label: 'pertence a',       style: 'solid' },
  { source: 'wellbore',     target: 'completacao',      relation: 'has_completion',   relation_label: 'tem completação',  style: 'solid' },
  { source: 'completacao',  target: 'dhsv',             relation: 'contains',         relation_label: 'contém',           style: 'dashed' },
  { source: 'completacao',  target: 'campo',            relation: 'enables',          relation_label: 'viabiliza',        style: 'dashed' },
  { source: 'wellbore',     target: 'formacao',         relation: 'penetrates',       relation_label: 'penetra',          style: 'dashed' },
  { source: 'wellbore',     target: 'trajetoria-poco',  relation: 'has_trajectory',   relation_label: 'tem trajetória',   style: 'dashed' },
  { source: 'wellbore',     target: 'topo-formacional', relation: 'has_marker',       relation_label: 'tem marker',       style: 'dashed' },
  { source: 'formacao',     target: 'topo-formacional', relation: 'has_top_at',       relation_label: 'tem topo em',      style: 'solid' },
  { source: 'perfil-poco',  target: 'wellbore',         relation: 'measured_in',      relation_label: 'medida em',        style: 'solid' },

  /* unidade-medida — metadado mandatório ANP (Res. 880/2022 / i-Engine XML) */
  { source: 'amostra-fluido', target: 'unidade-medida', relation: 'qualified_by',     relation_label: 'qualificada por',  style: 'solid' },
  { source: 'pvt',            target: 'unidade-medida', relation: 'expressed_in',     relation_label: 'expresso em',      style: 'solid' },
  { source: 'i-engine',       target: 'unidade-medida', relation: 'enforces',         relation_label: 'valida e impõe',   style: 'solid' },
  { source: 'bmp',            target: 'unidade-medida', relation: 'standardized_by',  relation_label: 'padronizado em',   style: 'dashed' },
  { source: 'reservatorio',   target: 'unidade-medida', relation: 'characterized_with', relation_label: 'caracterizado em', style: 'dashed' },
];

/* Alinhamento OSDU para os nós novos + alguns existentes que ainda têm null */
export const OSDU_ALIGNMENT_ADDITIONS = {
  'wellbore':         { kg: null, osdu: 'opendes:osdu:master-data--Wellbore:1.0.0',                    layers: ['layer2','layer3','layer4'] },
  'topo-formacional': { kg: null, osdu: 'opendes:osdu:work-product-component--WellboreMarker:1.0.0',   layers: ['layer2','layer3','layer4'] },
  'trajetoria-poco':  { kg: null, osdu: 'opendes:osdu:work-product-component--WellboreTrajectory:1.0.0', layers: ['layer3','layer4'] },
  'unidade-medida':   { kg: null, osdu: 'opendes:osdu:reference-data--UnitOfMeasure:1.0.0',            layers: ['layer2','layer3','layer4'] },
  /* Atualiza nós analytical existentes que estavam com osdu null */
  'litologia':        { kg: '#Lithology', osdu: 'opendes:osdu:reference-data--LithologyType:1.0.0',    layers: ['layer1','layer2','layer3','layer4','layer6'] },
  'classe-fluido':    { kg: null, osdu: 'opendes:osdu:reference-data--FluidType:1.0.0',                layers: ['layer4','layer6'] },
  'pvt':              { kg: null, osdu: 'opendes:osdu:work-product-component--WellborePressure:1.0.0', layers: ['layer4','layer6'] },
  'perfil-poco':      { kg: '#WellLog', osdu: 'opendes:osdu:work-product-component--WellLog:1.0.0',    layers: ['layer3','layer4','layer6'] },
};

/* RAG chunks específicos do increment OSDU v2 (excluindo o ambiguity_alert
   já incluído em AMBIGUITY_ALERTS acima) */
export const OSDU_RAG_CHUNKS = [
  {
    id: 'osdu_tripartition_master',
    type: 'osdu_tripartition',
    text: 'OSDU Master Data — Entidades estáveis de negócio com ciclo de vida longo. No Geolytics, equivalem aos nós tipo "operational" e "actor". Exemplos e mapeamentos: Well (poco) — registro de superfície + legal do poço; Wellbore (wellbore) — trecho físico perfurado; Field (campo) — campo de produção; Basin (bacia) — bacia sedimentar; Organisation (operador) — empresa operadora ou parceira; GeologicalFormation (formacao) — formação geológica formal; Reservoir (reservatorio) — corpo reservatório. Kind format: opendes:osdu:master-data--{Type}:1.0.0. Master Data é o "backbone" da plataforma OSDU — todos os Work Product Components e Reference Data se relacionam a entidades Master Data.',
    metadata: { category: 'master_data', osdu_platform: 'https://osduforum.org', rag_priority: 'high' },
  },
  {
    id: 'osdu_tripartition_reference',
    type: 'osdu_tripartition',
    text: 'OSDU Reference Data — Vocabulários controlados e enumerações. No Geolytics, equivalem às taxonomias. Crítico para interoperabilidade: sistemas diferentes usam termos diferentes para o mesmo conceito. WellStatus: ativo, abandonado, P&A (plug and abandon), suspenso, injetando. WellType / DrillingReasonType: exploratório (1-xxx ANP), appraisal, desenvolvimento (3-xxx), injeção (4-xxx), monitoramento (7-xxx). LithologyType: sandstone/arenito, limestone/calcário, shale/folhelho, salt/sal, evaporite/evaporito. FluidType: black_oil/óleo negro, volatile_oil/óleo volátil, condensate/condensado, wet_gas/gás úmido, dry_gas/gás seco. UnitOfMeasure: m, ft, mD, ºAPI, GAPI, MPa, psi, m³/d, bbl/d. Kind: opendes:osdu:reference-data--{Type}:1.0.0.',
    metadata: { category: 'reference_data', osdu_platform: 'https://osduforum.org', rag_priority: 'high' },
  },
  {
    id: 'osdu_tripartition_wpc',
    type: 'osdu_tripartition',
    text: 'OSDU Work Product Components (WPC) — Dados interpretativos e derivados. Resultado de serviços de campo, análises laboratoriais e interpretações técnicas. No Geolytics, equivalem aos nós tipo "analytical". WellLog (perfilagem): perfil contínuo de propriedades físicas ao longo do wellbore — curvas GR (argilosidade), RHOB (densidade), NPHI (porosidade nêutron), DT (sônico), RT (resistividade). WellboreMarker (topo_formacional): pick de profundidade onde o wellbore intercepta o topo de uma formação. WellboreTrajectory (trajetoria_poco): survey direcional MD/inclinação/azimute/TVD. WellborePressure (pvt): dados de pressão DST/RFT/MDT. Cada WPC tem ancestry.parents[] ligando ao Wellbore pai. Kind: opendes:osdu:work-product-component--{Type}:1.0.0. WPCs são o dado derivado mais valioso — integrar com M7-M10 Geolytics é o próximo passo.',
    metadata: { category: 'work_product_components', osdu_platform: 'https://osduforum.org', rag_priority: 'high' },
  },
  {
    id: 'osdu_lineage_anp_mapping',
    type: 'osdu_kind_mapping',
    text: 'Mapeamento de campos ANP → OSDU para poços: POCO_NUM → Well.WellID (ExternalID); POCO_POCO_NOME → Well.WellName; POCO_OPERADORA_SIGLA → Well.OperatorID → Organisation; POCO_STATUS → Wellbore.StatusID → reference-data--WellStatus; POCO_TIPO → Wellbore.DrillingReasonID → reference-data--WellDrillingReasonType; POCO_CAMPO → Well.FieldID → Field; POCO_BACIA_SIGLA → Well.BasinID → Basin; POCO_LATITUDE_BASE_4C → Well.SpatialLocation.Coordinates.Latitude; POCO_LONGITUDE_BASE_4C → Well.SpatialLocation.Coordinates.Longitude. Cadeia de linhagem: L5 (ANP public registry) → L4 (OSDU master-data--Well) → L6 (Geolytics enrichment). Cada registro OSDU tem ancestry.parents[] rastreando a origem ANP. Legal tags: opendes-ANP-public-data + otherRelevantDataCountries: BR. Arquivo de referência completo: data/osdu-mapping.json.',
    metadata: { type: 'osdu_kind_mapping', file: 'data/osdu-mapping.json', rag_priority: 'medium' },
  },
];
