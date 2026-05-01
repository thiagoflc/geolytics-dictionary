// Pergunta: Quais entidades do grafo não têm URI no Petro KGraph (lacunas ontológicas)?
// Útil para identificar termos exclusivamente brasileiros sem equivalente no KG de PUC-Rio

MATCH (e:Entity)
WHERE e.petrokgraph_uri IS NULL
RETURN
  e.id          AS id,
  e.label       AS label_pt,
  e.label_en    AS label_en,
  e.type        AS tipo,
  e.osdu_kind   AS osdu_kind,
  e.geocoverage AS camadas
ORDER BY e.type, e.label
