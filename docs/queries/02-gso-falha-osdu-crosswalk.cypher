// Pergunta: Quais classes GSO de falhas têm mapeamento OSDU equivalente (exactMatch ou closeMatch)?
// Navega o crosswalk entre camada GSO (Layer 7) e entidades OSDU do grafo principal

MATCH (entity:Entity)-[r:EXACTMATCH|CLOSEMATCH]->(gso:GSOClass)
WHERE gso.gso_module = 'gso-faults'
RETURN
  entity.id            AS entidade_osdu,
  entity.osdu_kind     AS osdu_kind,
  type(r)              AS tipo_mapeamento,
  gso.gso_class        AS classe_gso,
  gso.owl_uri          AS gso_uri,
  gso.definition_en_canonical AS definicao_gso

UNION

MATCH (gso:GSOClass)
WHERE gso.gso_module = 'gso-faults'
  AND gso.osdu_crosswalk_match IS NOT NULL
RETURN
  null                          AS entidade_osdu,
  gso.osdu_crosswalk_class      AS osdu_kind,
  gso.osdu_crosswalk_match      AS tipo_mapeamento,
  gso.gso_class                 AS classe_gso,
  gso.owl_uri                   AS gso_uri,
  gso.definition_en_canonical   AS definicao_gso
ORDER BY tipo_mapeamento, classe_gso
