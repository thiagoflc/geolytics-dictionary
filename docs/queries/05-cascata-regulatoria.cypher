// Pergunta: Como a cascata regulatória da Lei 9.478 flui até o SIGEP via ANP?
// Mostra a cadeia de autoridade: Lei 9478 → ANP → SIGEP e entidades que cada um governa

MATCH (anp:Actor {id: 'anp'})
OPTIONAL MATCH (anp)-[:OVERSEES_VIA]->(sigep:Instrument {id: 'sigep'})
OPTIONAL MATCH (anp)-[:GOVERNS|DEFINES|REGULATES|CONTROLS]->(regulados)
OPTIONAL MATCH (sigep)-[:MANAGES_VIA|INTEGRATES_TO]->(downstream)
WITH anp, sigep, collect(DISTINCT regulados.label) AS entidades_anp,
     collect(DISTINCT downstream.label) AS sistemas_sigep
RETURN
  anp.label                          AS orgao_regulador,
  'Lei nº 9.478/1997'                AS base_legal,
  sigep.label                        AS sistema_gestao,
  entidades_anp                      AS entidades_reguladas_pela_anp,
  sistemas_sigep                     AS sistemas_vinculados_ao_sigep
