# Conceitos exclusivamente brasileiros (camada 5 — ANP)

Os conceitos abaixo **nao existem em nenhuma ontologia internacional** de geologia ou petroleo (GeoCore, Petro KGraph, OSDU, IFC, BFO). Sao exclusivos do framework regulatorio brasileiro definido pela Lei no 9.478/1997 (Lei do Petroleo), Lei no 12.351/2010 e resolucoes da ANP.

Por isso este dicionario existe: para preencher esta lacuna ontologica.

---

## Os 11 conceitos exclusivos

### Bloco

Unidade geografica de exploracao definida pela ANP para fins de concessao ou partilha de producao. **Nao e equivalente a "lease" ou "license" do sistema americano ou britanico.** O bloco brasileiro tem limites rigidos definidos pela ANP, numero sequencial e regime contratual especifico.

- Campo `geocoverage`: `layer5`
- OSDU kind: `opendes:osdu:master-data--SeismicAcquisitionSurvey:1.0.0` (aproximacao — nao ha equivalente exato)
- Identificado por codigo alfanumerico: ex. `BS-500`, `BM-CAL-4`, `POT-M-857`

### PAD — Plano de Avaliacao de Descobertas

Plano obrigatorio apresentado pelo concessionario/contratado a ANP apos uma Notificacao de Descoberta, descrevendo o programa de avaliacao da potencial acumulacao. **Nao e "appraisal" generico.** O PAD tem conteudo minimo definido pela Resolucao ANP no 708/2017 e prazo contratual especifico.

- Campo `geocoverage`: `layer5`
- Relacao chave: `PAD -> may_yield -> DeclaracaoDeComercialidade`

### Contrato de E&P

O instrumento juridico bilateral entre ANP e empresa(s) que define direitos e obrigacoes de exploracao e producao. Pode ser de Concessao, Partilha de Producao ou Cessao Onerosa. **A estrutura juridica e especifica do direito brasileiro** — nao mapeia diretamente para contratos PSC, RSC ou "license" de outros sistemas.

- Campo `geocoverage`: `layer5`
- Relacao chave: `ContratoEP -> governs -> Bloco`

### Rodada de Licitacao

Processo competitivo conduzido pela ANP para outorga de blocos. Numeradas sequencialmente desde 1999 (1a Rodada). Cada rodada tem edital especifico, areas ofertadas e criterios de qualificacao.

- Campo `geocoverage`: `layer5`
- Exemplos: Rodada 1 (1999), Rodada 17 (2021), Rodada Pre-sal 7 (2022)
- Relacao chave: `Bloco -> auctioned_in -> RodadaDeLicitacao`

### UTS — Unidades de Trabalho Sismico

Metrica brasileira para quantificar o Programa de Trabalho Minimo (PTM/PEM) de um contrato de exploracao. Cada tipo de dado sismico (2D, 3D, reprocessamento) tem um fator de conversao para UTS. **Nao existe equivalente exato em sistemas internacionais.**

- Campo `geocoverage`: `layer5`
- Sigla ambigua: UTS tambem significa "Ultimate Tensile Strength" em geomecanica — sempre usar com contexto

### Regime Contratual

A modalidade juridica do contrato de E&P no Brasil. Ha exatamente tres opcoes validas:

1. **Concessao** (Lei 9.478/1997): empresa assume risco integral; hidrocarboneretos sao de propriedade da empresa apos pagamento de royalties/participacoes.
2. **Partilha de Producao** (Lei 12.351/2010): Petrobras e operadora obrigatoria; governo recebe parcela em oleo (profit oil) alem de royalties; pre-sal obrigatorio.
3. **Cessao Onerosa** (Lei 12.276/2010): modalidade especial para o pre-sal para a Petrobras.

Qualquer outro regime mencionado em documentos E&P brasileiros e um erro. O validador semantico detecta via regra `REGIME_CONTRATUAL_INVALID`.

### Periodo Exploratorio (PE)

Fase contratual com prazo definido dividida em subperiodos (1o PE, 2o PE, 3o PE), cada um com obrigacoes de trabalho minimo (UTS). Ao final do periodo, o concessionario deve perfurar ou devolver a area.

- Campo `geocoverage`: `layer5`
- Relacao chave: `ContratoEP -> has_phase -> PeriodoExploratorio`

### Etapa Prorrogada

Periodo de extensao apos o Periodo Exploratorio principal, regulado por resolucoes ANP especificas. Permite a continuacao da exploracao sob condicoes especificas de comprometimento de trabalho adicional.

- Campo `geocoverage`: `layer5`

### Processo Sancionador

Procedimento administrativo da ANP/SEP para apurar infrações contratuais ou regulatorias. Pode resultar em multa, suspensao ou cancelamento do contrato.

- Campo `geocoverage`: `layer5`
- Relacao chave: `ANP -> initiates -> ProcessoSancionador`

### Notificacao de Descoberta

Comunicacao formal obrigatoria do operador a ANP quando identifica uma potencial acumulacao comercial durante a fase exploratoria. Dispara o prazo para apresentacao do PAD.

- Campo `geocoverage`: `layer5`
- Relacao chave: `Poco -> may_register -> NotificacaoDeDescoberta`

### Declaracao de Comercialidade

Marco regulatorio formal que transforma uma descoberta em campo de petroleo/gas. Apos a DC, inicia-se a fase de desenvolvimento. E o ato juridico que "origina" o Campo no sistema ANP.

- Campo `geocoverage`: `layer5`
- Relacao chave: `DeclaracaoDeComercialidade -> originates -> Campo`

---

## Por que esses conceitos existem

O sistema regulatorio brasileiro de O&G evoluiu de forma independente a partir da Lei 9.478/1997, criando um framework unico que combina:

- Soberania estatal sobre recursos minerais (Constituicao Federal, Art. 20)
- Participacoes governamentais especificas (royalties, participacao especial, bonus de assinatura)
- Papel singular da Petrobras como operadora obrigatoria no pre-sal (Lei 12.351/2010)
- Sistema de controle e fiscalizacao pela ANP com procedimentos proprios

Nenhuma ontologia internacional cobria esse framework antes deste dicionario.

---

## Referencia legal

| Conceito | Base legal principal |
|---|---|
| Bloco, Concessao, Rodada de Licitacao | Lei 9.478/1997 (Lei do Petroleo) |
| Partilha de Producao | Lei 12.351/2010 |
| Cessao Onerosa | Lei 12.276/2010 |
| PAD, Processo Sancionador | Resolucao ANP no 708/2017 |
| Etapa Prorrogada | Resolucao ANP no 815/2020 |
| Notificacao de Descoberta, Declaracao de Comercialidade | Resolucao ANP no 708/2017 |
