// Pergunta: Quais unidades de tempo geológico são relevantes para o pré-sal brasileiro?
// Fonte: data/cgi-geologic-time.json (layer3), ICS 2023

// Buscar formações e sua posição na escala temporal
MATCH (f {id: 'formacao'})
WHERE 'layer3' IN f.geocoverage
RETURN
  f.id              AS formacao_id,
  f.label           AS nome_pt,
  f.geosciml_uri    AS geosciml_uri,
  'Aptiano-Albiano'  AS periodo_presal,
  '125-100.5 Ma'    AS intervalo_ma

// Nota: Para consultar a escala de tempo completa, use a API:
// GET api/v1/cgi-geologic-time.json
// Filtrar por brazil_notes IS NOT NULL para unidades com contexto pré-sal
