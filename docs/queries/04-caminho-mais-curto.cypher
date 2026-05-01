// Pergunta: Qual é o caminho mais curto entre duas entidades quaisquer do grafo?
// Exemplo: de 'poco' até 'anp' — quantos saltos e por quais relações?

MATCH (origem {id: 'poco'}), (destino {id: 'anp'})
CALL apoc.algo.dijkstra(origem, destino, '', 'weight') YIELD path, weight
RETURN
  [n IN nodes(path) | coalesce(n.label, n.name, n.id)] AS nos_do_caminho,
  [r IN relationships(path) | type(r)]                 AS relacoes,
  length(path)                                          AS num_hops

UNION

// Alternativa sem APOC (BFS nativo, sem peso):
MATCH path = shortestPath(
  (origem {id: 'poco'})-[*]-(destino {id: 'anp'})
)
RETURN
  [n IN nodes(path) | coalesce(n.label, n.name, n.id)] AS nos_do_caminho,
  [r IN relationships(path) | type(r)]                 AS relacoes,
  length(path)                                          AS num_hops
LIMIT 1
