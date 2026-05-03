// Pergunta: Quais são os componentes de construção de um poço segundo o padrão GWML2 (OGC)?
// Navega: poco → gsmlbh:Borehole → GWML2 WellConstruction classes

MATCH (poco {id: 'poco'})
WHERE 'layer1b' IN poco.geocoverage
RETURN
  poco.id             AS id_entidade,
  poco.label          AS nome_pt,
  poco.geosciml_uri   AS gsmlbh_uri,
  'WellConstruction'  AS gwml2_parent_class,
  [
    'CasingComponent',
    'Screen',
    'SealingComponent',
    'FiltrationComponent',
    'BoreCollar',
    'BoreInterval',
    'WellPump',
    'CasingString'
  ]                   AS gwml2_classes

// Para verificar propriedades gsmlbh do poço:
MATCH (poco {id: 'poco'})
RETURN
  poco.id,
  'boreholeDiameter'   AS propriedade_1,
  'dateOfDrilling'     AS propriedade_2,
  'drillingMethod'     AS propriedade_3,
  'inclinationType'    AS propriedade_4

// Valores de inclinationType: 'vertical', 'deviated', 'horizontal'
