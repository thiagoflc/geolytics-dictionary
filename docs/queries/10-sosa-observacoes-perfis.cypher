// Pergunta: Como os perfis de poço se mapeiam para o padrão W3C SOSA/SSN?
// Objetivo: encontrar entidades que são sosa:Observation ou sosa:FeatureOfInterest

MATCH (n)
WHERE 'layer1b' IN n.geocoverage
  OR 'layer4' IN n.geocoverage  // operações
RETURN
  n.id            AS entidade,
  n.label         AS nome_pt,
  n.type          AS tipo,
  n.geocoverage   AS camadas,
  CASE n.id
    WHEN 'perfil-poco'              THEN 'sosa:Observation'
    WHEN 'formation-pressure-point' THEN 'sosa:Observation'
    WHEN 'poco'                     THEN 'sosa:FeatureOfInterest'
    WHEN 'formacao'                 THEN 'sosa:FeatureOfInterest'
    WHEN 'lwd-run'                  THEN 'sosa:Sampling'
    WHEN 'wireline-run'             THEN 'sosa:Sampling'
    WHEN 'core-plug'                THEN 'ssn:Sample'
    ELSE null
  END AS sosa_class
ORDER BY sosa_class, n.id

// Mnemonics de perfis e suas unidades QUDT (ver api/v1/sosa-qudt-alignment.json):
// GR → qudt:API | RHOB → qudt:KiloGM-PER-M3 | DT → qudt:MicroSEC-PER-FT
// RT → qudt:OHM-M | UCS → qudt:MegaPascal | POROSITY → qudt:FRACTION
