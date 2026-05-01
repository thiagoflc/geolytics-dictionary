# Casos de Uso — Exemplos com perguntas e comportamento esperado do agente

Este documento apresenta seis cenarios concretos que ilustram como o agente Geolytics responde a perguntas reais de E&P. Cada cenario inclui a pergunta de entrada, o caminho interno pelo DAG LangGraph e a resposta esperada.

---

## UC-01: Deteccao de incompatibilidade regulatoria — Regime ANP

**Contexto**: Um analista recebe um contrato descrevendo o Bloco BM-CAL-4 como operando sob "regime de Privatizacao". Precisa verificar se o regime e valido no framework regulatorio brasileiro.

**Pergunta**:
> "O contrato do Bloco BM-CAL-4 menciona regime de Privatizacao. Isso e compativel com o marco regulatorio da ANP?"

**Caminho no DAG**: Router classifica como `validation` -> Validator -> Synthesizer

**O que o Validator detecta**:

```
Regra: REGIME_CONTRATUAL_INVALID
Evidence: "Regime contratual mencionado: 'privatizacao'."
SuggestedFix: "Regimes contratuais validos no Brasil:
  Concessao (Lei 9.478/1997),
  Partilha de Producao (Lei 12.351/2010),
  Cessao Onerosa (Lei 12.276/2010)."
```

**Resposta esperada do agente**:
O agente identifica a violacao e explica: "Privatizacao" nao e um regime contratual reconhecido pela ANP. Os tres regimes validos sao Concessao, Partilha de Producao e Cessao Onerosa. O contrato contem um erro terminologico que pode invalidar clausulas especificas.

---

## UC-02: Validacao de relatório WITSML — Restricao geometrica TVD <= MD

**Contexto**: Um engenheiro de perfuracao recebeu um arquivo WITSML 2.0 com dados de trajetoria de poco e suspeita de erro: a Profundidade Vertical Real (TVD) esta maior que a Profundidade Medida (MD) em uma das estacoes.

**Pergunta**:
> "Este arquivo WITSML tem uma estacao com TVD de 3200m e MD de 3150m. Ha algum problema?"

**Caminho no DAG**: Router classifica como `validation` -> RAGRetrieve (chunks sobre WITSML, geometria de poco) -> Validator -> Synthesizer

**Regra violada**: `TVD <= MD` e uma restricao geometrica fundamental (o caminho medido ao longo da trajetoria nunca pode ser menor que a profundidade vertical projetada para um poco nao vertical).

**Validacao SHACL relevante** (`data/geolytics-shapes.ttl`):
```turtle
geo:TrajectoryStationShape a sh:NodeShape ;
    sh:targetClass geo:TrajectoryStation ;
    sh:sparql [
        sh:message "TVD must be <= MD" ;
        sh:select """SELECT $this WHERE {
            $this geo:tvd ?tvd ;
                  geo:md  ?md .
            FILTER (?tvd > ?md)
        }""" ;
    ] .
```

**Resposta esperada do agente**: O agente confirma o erro: TVD (3200m) > MD (3150m) e fisicamente impossivel para um poco inclinado ou horizontal. O resultado medido ao longo da trajetoria (MD) e sempre maior ou igual ao deslocamento vertical (TVD). Sugere verificar a estacao no indice correspondente do arquivo WITSML.

---

## UC-03: QA de inversao sismica — Classe AVO 4 como candidato DHI

**Contexto**: Um geofisico interpretando um levantamento sismico identifica uma anomalia de amplitude negativa e declara "Esta resposta AVO Classe IV confirma um DHI (Direct Hydrocarbon Indicator)".

**Pergunta**:
> "A anomalia AVO Classe 4 no topo da camada X e um DHI para gas em arenito raso. Isso e correto?"

**Caminho no DAG**: Router classifica como `validation` -> RAGRetrieve (chunks de AVO, DHI, taxonomia sismica) -> Validator -> Synthesizer

**O que o corpus RAG contem** (de `data/seismic-inversion-attributes.json`):
- AVO Classe 4: anomalia de amplitude negativa com offset (intercept negativo, gradiente positivo). Ocorre em arenitos de alta impedancia encaixados em folhelhos de baixa impedancia.
- DHI: um DHI verdadeiro requer que a anomalia seja causada por fluido (gas/oleo), nao apenas por contraste de impedancia litologica.

**Nuance critica**: AVO Classe 4 pode ser resultado de litologia (nao fluido) e e o mais ambiguo dos quatro. Nao confirma DHI sem analise de inversao e calibracao com poco.

**Resposta esperada do agente**: O agente nao confirma a afirmacao. AVO Classe 4 e um indicador sugestivo mas nao confirmatório de DHI. A alta razao Vp/Vs do gas tenderia a mover a resposta para as Classes 2 ou 3. Para Classe 4, a analise de inversao simultanea (Zp x Zs) ou crossplot de Lambda-Rho e necessaria antes de classificar como DHI.

---

## UC-04: Janela de mud weight via MEM 1D

**Contexto**: Um engenheiro de geomecânica precisa calcular os limites de peso de lama para perfurar um intervalo em arenito de 3500m de profundidade na Bacia de Campos.

**Pergunta**:
> "Para o intervalo de 3500m na Bacia de Campos com pressao de poros de 0.45 psi/ft e resistencia a compressao UCS de 8000 psi, qual a janela de mud weight?"

**Caminho no DAG**: Router classifica como `multi_hop` -> Decomposer -> GraphQuery -> RAGRetrieve -> Validator -> Synthesizer

**Sub-questoes decompostas**:
1. "Quais propriedades elasticas sao necessarias para o calculo MEM 1D?"
2. "Qual o limite inferior (colapso) e superior (fratura) do mud weight?"
3. "A UCS de 8000 psi e compativel com arenito na Bacia de Campos?"

**Resultado do GraphQuery**: entidade `ModelloTerrasMecanico` com relacoes para `PressaoPoros`, `GradienteFratura`, `TensaoInSitu`, `UCS`.

**Resposta esperada do agente**: O agente explica a janela de mud weight como o intervalo entre o equivalente de circulacao da pressao de poros (limite inferior de colapso) e o gradiente de fratura (limite superior). Com 0.45 psi/ft de pressao de poros, o ECD minimo deve exceder esse valor. O agente identifica que UCS de 8000 psi e compativel com arenito compactado e recomenda usar o criterio de Mohr-Coulomb para calcular a resistencia ao colapso.

---

## UC-05: Disambiguacao Reserva SPE-PRMS vs Reserva Ambiental

**Contexto**: Um texto de relatorio menciona "Reservas da APA Campos Gerais" em uma secao de recursos de hidrocarbonetos.

**Pergunta**:
> "O relatorio lista Reservas da APA Campos Gerais como parte do portfolio de recursos 2P da empresa. Isso faz sentido?"

**Caminho no DAG**: Router classifica como `validation` -> Validator -> Synthesizer

**O que o Validator detecta**:

```
Regra: RESERVA_AMBIENTAL_CONFUSION
Evidence: "O texto menciona 'reserva' em contexto de petroleo/gas
  mas tambem contem termos de reserva ambiental (APA)."
SuggestedFix: "Desambiguar: 'Reserva' no contexto SPE-PRMS refere-se
  a volumes de hidrocarbonetos tecnicamente recuperaveis e comercialmente
  viaveis (1P/2P/3P). 'Reserva Ambiental' (REBIO/RPPN/APA) e uma area
  de protecao ambiental regulada pelo SNUC (Lei 9.985/2000)."
```

**Resposta esperada do agente**: O agente identifica a confusao terminologica. APA (Area de Protecao Ambiental) e uma categoria de Unidade de Conservacao do SNUC — nao tem relacao com recursos petrolíferos. Se a empresa tem ativos proximos a uma APA, isso geraria restricoes ambientais, nao "Reservas 2P". O portfolio de recursos deve usar categorias SPE-PRMS (1P, 2P, 3P, C1C, C2C, C3C).

---

## UC-06: Crosswalk OSDU para Petro KGraph — Dados de um Poco

**Contexto**: Um time de dados precisa mapear dados de poco armazenados no schema OSDU para o grafo de conhecimento Geolytics (Petro KGraph).

**Pergunta**:
> "Tenho um registro OSDU kind 'opendes:osdu:master-data--Well:1.0.0'. Qual entidade equivalente no grafo Geolytics e quais propriedades sao compartilhadas?"

**Caminho no DAG**: Router classifica como `multi_hop` -> Decomposer -> GraphQuery (crosswalk lookup) -> RAGRetrieve -> Synthesizer

**Sub-questoes decompostas**:
1. "Qual entidade Geolytics corresponde ao OSDU kind Well?"
2. "Quais campos OSDU mapeiam para propriedades do grafo Geolytics?"
3. "Ha restricoes SHACL sobre a entidade equivalente?"

**Resultado do GraphQuery** (via `crosswalk_lookup` no MCP):
```json
{
  "osdu_kind": "opendes:osdu:master-data--Well:1.0.0",
  "geo_entity": "poco",
  "geo_uri": "https://geolytics.petrobras.com.br/dict/Poco",
  "petrokgraph_uri": "http://www.petroles.petro.br/ontology/Poco",
  "shared_properties": ["nome", "operador", "bacia", "coordenadas"],
  "shacl_shape": "geo:PocoShape"
}
```

**Resposta esperada do agente**: O agente retorna o mapeamento completo: o OSDU Well corresponde a `geo:Poco` no grafo Geolytics, com URI Petro KGraph disponivel. As propriedades `WellName`, `OperatorName`, `BasinName` do OSDU mapeiam para `geo:nome`, `geo:operador`, `geo:bacia` respectivamente. O agente tambem informa que `geo:PocoShape` (SHACL) valida que `tipoPoco` deve ser da enumeracao ANP canonica e que `operador` e `bloco` tem cardinalidade 1..1.

---

## Executando os casos de uso

```bash
cd examples/langgraph-agent
pip install -r requirements.txt

# UC-01: regime invalido
python run_demo.py --question "O contrato do Bloco BM-CAL-4 menciona regime de Privatizacao. Isso e compativel com o marco regulatorio da ANP?"

# UC-05: disambiguacao reserva
python run_demo.py --question "O relatorio lista Reservas da APA Campos Gerais como 2P. Isso faz sentido?"

# UC-06: crosswalk OSDU
python run_demo.py --question "Tenho um OSDU kind opendes:osdu:master-data--Well:1.0.0. Qual entidade equivalente no grafo Geolytics?"
```

Para os casos com WITSML (UC-02), use a ferramenta MCP:

```bash
node scripts/validate-cli.js --format text "TVD 3200m MD 3150m na estacao 5 do poco 1-RJS-702-RJ"
```

Para validacao SHACL completa de um arquivo RDF (UC-02, UC-04):

```bash
python scripts/validate-shacl.py
```
