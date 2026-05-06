# O que é o GeoBrain?

GeoBrain é uma **ontologia semântica de domínio** sobre Exploração & Produção (E&P) de petróleo e gás natural no Brasil, materializada como:

- 📚 Um **dicionário** de termos canônicos da ANP/SEP (regulador brasileiro)
- 🕸️ Um **grafo de conhecimento** tipado (entidades + relações nomeadas)
- 🔬 Uma **ontologia formal** em RDF/OWL alinhada a 8 camadas internacionais
- 🛡️ Um conjunto de **65 SHACL shapes** para validação automática
- 🤖 Um **conjunto de ferramentas de IA** (MCP server, agente LangGraph, pacote Python, RAG corpus)

## A pergunta de fundo

> **Por que RAG vetorial puro não basta para perguntas de O&G?**

Porque o domínio combina três tipos de conhecimento que embeddings densos resolvem mal:

1. **Multi-hop estrutural** — "Qual o regime contratual do Bloco BS-500?" exige caminhar **poço → bloco → bacia → contrato → lei** através de relações tipadas. Vetorial entrega chunks textuais soltos; relações se perdem.
2. **Desambiguação polissêmica** — "PAD" pode ser:
   - **PAD** = Plano de Avaliação de Descoberta (instrumento contratual ANP)
   - **PAD** = drilling pad (plataforma física de perfuração)
   - **PAD** = Pulsed Amplitude Detector (instrumento físico)
   Apenas contexto ontológico (camada **5** ANP vs. camada **6** Petrobras vs. instrumentação) decide.
3. **Conformidade regulatória** — "Reserva 4P do Campo X" é **inválido**: o padrão SPE-PRMS reconhece apenas 1P/2P/3P. Um agente sem validador determinístico aceita o erro silenciosamente.

GeoBrain ataca os três frentes de uma vez: **camadas + grafo + validador**.

---

## Quem se beneficia

| Persona                                            | Uso típico                                                                                                                         |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Engenheiro de IA aplicada a O&G**                | Plug-and-play do MCP server em Claude/Cursor; agente LangGraph com Validator como guardrail.                                       |
| **Pesquisador de ontologias**                      | Alinhamentos SKOS para BFO, GeoSciML, OSDU, SWEET, Petro KGraph, GSO; SHACL shapes prontas.                                        |
| **Engenheiro de dados Petrobras / OSDU**           | Crosswalks bilaterais ANP↔OSDU↔WITSML/PRODML; Petrobras 3W v2.0.0 (CC-BY 4.0) integrado.                                           |
| **Geólogo / Engenheiro de petróleo**               | Dicionário com 23 termos ANP enriquecidos, 437 conceitos CGI Lithology, 213 classes GSO/Loop3D, 1.102 siglas categorizadas.        |
| **Aluno (graduação / pós-graduação)**              | Notebooks didáticos, queries Cypher comentadas em PT-BR, casos de uso passo a passo.                                               |
| **Auditor regulatório / advogado de direito mineral** | Cascata Lei 9.478/1997 → ANP → SIGEP modelada explicitamente; regimes contratuais validados.                                  |

---

## O que ele **não** é

- ❌ **Não é um banco de dados de poços** — não armazena measurements, logs ou produção; ele descreve o **vocabulário** com que esses dados deveriam ser nomeados.
- ❌ **Não é uma plataforma OSDU completa** — fornece **alinhamento** ANP↔OSDU, não a stack OSDU end-to-end.
- ❌ **Não é um LLM** — fornece **contexto tipado** que LLMs consomem (via MCP, RAG, ou few-shot).
- ❌ **Não substitui o agente** — fornece o **guardrail determinístico** (validador + SHACL) sobre o qual agentes operam com segurança.

---

## Princípios de design

1. **Determinístico antes de probabilístico** — toda inferência crítica (regime contratual válido? sigla ambígua?) é regra-baseada. LLMs entram só para sintetizar resposta natural.
2. **Camada-aware** — todo termo carrega `geocoverage: ["L3","L4","L5"]` indicando em quais camadas existe. Saber em qual camada um conceito vive é metade do problema resolvido.
3. **Cross-walks bilaterais** — ida e volta. Um mapeamento ANP→OSDU sem o reverso vira beco sem saída em pipelines reais.
4. **JSON canônico, RDF derivado** — o JSON é a fonte amigável; o TTL/SHACL é gerado por `scripts/ttl-serializer.js`. Sem dupla manutenção.
5. **Reproduzibilidade byte-a-byte** — `scripts/generate.js` é determinístico. CI verifica ausência de diff (`scripts/check-regen.sh`).

---

## Linha do tempo (alta-nível)

- **F1–F6** Construção das camadas L1–L4 (BFO, GeoSciML, O3PO, OSDU)
- **F7–F9** Camada L5 (ANP brasileiro), L6 (Petrobras corporativo), siglas
- **F10** Camada L7 (GSO/Loop3D) + crosswalks WITSML/PRODML
- **F11** Petrobras 3W v2.0.0 (CC-BY 4.0)
- **F12** SPE Volve bridge + ancoragem 183 SHACL warnings → 0 (regressão fixa)

Histórico completo: [CHANGELOG.md](https://github.com/thiagoflc/geolytics-dictionary/blob/main/CHANGELOG.md).

---

> **Próximo:** entender as [[Semantic Layers|8 camadas semânticas]] — o conceito mais importante do projeto.
