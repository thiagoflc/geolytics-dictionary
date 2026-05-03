// Pergunta: Quais reservatórios têm litologia mapeada no vocabulário CGI e qual é o equivalente OSDU?
// Navega: reservatório → litologia → CGI concept → OSDU LithologyType

// Versão simplificada (entity-graph)
MATCH (res:Operational {id: 'reservatorio'})
      -[:HAS_PROPERTY]->(lith:Scientific {id: 'litologia'})
WHERE 'layer1b' IN lith.geocoverage
RETURN
  res.label          AS reservatorio,
  lith.label         AS litologia_pt,
  lith.geosciml_uri  AS cgi_uri,
  lith.geocoverage   AS camadas_semanticas

// Versão com OSDU crosswalk (quando disponível)
MATCH (n)
WHERE 'layer1b' IN n.geocoverage
  AND n.geosciml_uri IS NOT NULL
RETURN
  n.id              AS entidade,
  n.label           AS nome_pt,
  n.geosciml_uri    AS uri_geosciml,
  n.osdu_kind       AS osdu_kind,
  n.geocoverage     AS camadas
ORDER BY n.type, n.id
LIMIT 20
