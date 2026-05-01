// Pergunta: Qual o caminho completo de um poço até o regime contratual que governa seu bloco?
// Navega a cadeia multi-hop: poço → bloco → bacia → regime contratual

MATCH path = (poco:Operational {id: 'poco'})
             -[:DRILLED_IN]->(bloco:Operational {id: 'bloco'})
             -[:LOCATED_IN]->(bacia:Operational)
             -[:GOVERNED_BY]->(regime:Instrument)
WHERE regime.type = 'instrument'
RETURN
  poco.label   AS poco,
  bloco.label  AS bloco,
  bacia.label  AS bacia,
  regime.label AS regime_contratual,
  length(path) AS hops
