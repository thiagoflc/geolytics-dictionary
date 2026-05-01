// Pergunta: Quais siglas do domínio O&G têm múltiplos sentidos (ambiguidade)?
// Identifica siglas que aparecem em mais de uma entrada do siglário,
// agrupando por sigla e listando todos os significados — útil para NER e RAG

MATCH (e:Entity)
WHERE e.type IS NOT NULL
WITH e.label AS sigla_candidata, collect(e) AS entidades
WHERE size(entidades) > 1
RETURN
  sigla_candidata                                        AS sigla,
  size(entidades)                                        AS num_sentidos,
  [en IN entidades | en.id]                              AS ids,
  [en IN entidades | coalesce(en.definition, en.label)]  AS definicoes

UNION

// Siglas do dicionário de acrônimos com múltiplas entradas (via propriedade)
MATCH (a:Entity)
WHERE a.sigla IS NOT NULL
WITH a.sigla AS sigla, collect(a) AS entradas
WHERE size(entradas) > 1
RETURN
  sigla                                                  AS sigla,
  size(entradas)                                         AS num_sentidos,
  [en IN entradas | en.id]                               AS ids,
  [en IN entradas | coalesce(en.expansion_pt, en.label)] AS definicoes
ORDER BY num_sentidos DESC, sigla
