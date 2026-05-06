"""inject_geolytics_rag.py — Inject the geolytics-dictionary RAG corpus into the SPE Volve Neo4j vector index.

Injects ontology terms from the geolytics-dictionary-v1.1 as ReportChunk nodes into
the SPE Volve Neo4j graph, enriching semantic search with O&G domain knowledge.

The corpus is embedded as a Python constant — no file I/O at runtime (standalone script).

Usage:
    python inject_geolytics_rag.py --stats
    python inject_geolytics_rag.py --verify
    python inject_geolytics_rag.py --dry-run
    python inject_geolytics_rag.py --categories geologia contratos
    python inject_geolytics_rag.py
"""

from __future__ import annotations

import argparse
import logging
import os
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Corpus constant — 78 ontology chunks from geolytics-dictionary-v1.1
# Source: ai/rag-corpus.jsonl (types: term, ontology_layer, domain, type)
# ---------------------------------------------------------------------------
GEOLYTICS_RAG_CORPUS: list[dict[str, Any]] = [
    {'chunk_id': 'geolytics_term_bloco', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Bloco (Exploration Block): Parte de uma bacia sedimentar, formada por um prisma vertical de profundidade indeterminada, com superfície poligonal definida pelas coordenadas geográficas de seus vértices, onde são desenvolvidas atividades de exploração ou produção de petróleo e gás natural. Sinônimos: bloco exploratório, área concedida, block, exploration block, lease block, concession block. Exemplos: BM-S-11 (Lula); BCAM-40 (Búzios); BS-4 (Atlanta); BM-C-33. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos, Declarações de Comercialidade, Resolução ANP nº 708/2017, Resolução ANP nº 815/2020. Fonte: Lei nº 9478, de 06/08/1997.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_bacia-sedimentar', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Bacia Sedimentar (Sedimentary Basin): Depressão da crosta terrestre onde se acumulam rochas sedimentares que podem ser portadoras de petróleo ou gás, associados ou não. Sinônimos: bacia, bacia sedimentar, basin, sedimentary basin. Exemplos: Bacia de Campos; Bacia de Santos; Bacia de Sergipe-Alagoas; Bacia Potiguar; Bacia do Recôncavo. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos, Declarações de Comercialidade. Fonte: Lei nº 9478, de 06/08/1997.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_bacias-agrupadas', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Bacias Agrupadas: Agrupamento regional das bacias sedimentares em quatro grupos: Mar — Margem Equatorial (Foz do Amazonas, Pará-Maranhão, Barreirinhas, Ceará, Potiguar marítimo); Mar — Margem Leste (Pernambuco-Paraíba, Sergipe-Alagoas, Jacuípe, Camamu-Almada, Jequitinhonha, Cumuruxatiba, Mucuri, Espírito Santo, Campos, Santos, Pelotas); Terra — Bacias Maduras (Potiguar, Sergipe, Alagoas, Recôncavo, Espírito Santo terrestre); Terra — Bacias de Nova Fronteira (Amazonas, Paraná, Parnaíba, São Francisco, Solimões, Tucano Sul). Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_ambiente', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Ambiente: Localização por ambiente dos blocos exploratórios sob contrato: terra (onshore) ou mar (offshore). Distingue operações terrestres e marítimas para fins de classificação e monitoramento regulatório. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos, Declarações de Comercialidade. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_presal', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Pré-sal (Pre-salt): Camada geológica localizada abaixo de uma extensa camada de sal no subsolo marítimo e terrestre. Identificar se um poço atingiu o pré-sal é informação estratégica para avaliar o potencial exploratório e enquadrar o regime contratual aplicável. Sinônimos: pré-sal, camada do pré-sal, reservatórios do pré-sal, pre-salt, sub-salt, subsalt. Exemplos: Reservatórios de Tupi; Reservatórios de Búzios; Polígono do Pré-sal (Lei 12.351/2010). Aparece nos datasets: Poços Exploratórios em Blocos. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_operador', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Operador (Operator): Empresa legalmente designada pelos consorciados para conduzir e executar todas as operações e atividades na área sob contrato, de acordo com o estabelecido no contrato de E&P celebrado entre a contratante e o contratado. Sinônimos: operadora, concessionária, empresa operadora, operator, operating company, lead operator. Exemplos: Petrobras; Shell Brasil; Equinor; TotalEnergies; Repsol Sinopec; BP Brasil; Galp Energia. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos, Declarações de Comercialidade, Resolução ANP nº 708/2017, Resolução ANP nº 815/2020. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_contratados', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Contratados: Empresas contratadas e sua participação, em porcentagem, no contrato de E&P. Inclui o operador e eventuais parceiros do consórcio, com suas respectivas parcelas de participação. Aparece nos datasets: Blocos sob Contrato, PADs em Andamento. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_contrato-ep', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Contrato de E&P (E&P Contract): Contrato de Exploração e Produção assinado entre o agente econômico e a ANP. Estabelece os direitos e obrigações das partes para exploração de petróleo e gás natural em um bloco específico, incluindo o Programa Exploratório Mínimo (PEM) e as condições de produção. Sinônimos: contrato de E&P, contrato de concessão, contrato de partilha, E&P contract, exploration and production contract, upstream contract. Exemplos: Concessão BM-S-11; Partilha de Libra; Cessão Onerosa de Búzios. Aparece nos datasets: Blocos sob Contrato, Resolução ANP nº 708/2017, Resolução ANP nº 815/2020. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_pem', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'PEM — Programa Exploratório Mínimo: Conjunto mínimo de atividades exploratórias que o contratado se compromete a realizar como parte do contrato de concessão ou partilha de produção. A partir da 5ª Rodada (2003), o PEM do 1º período exploratório é expresso em Unidades de Trabalho (UTs) — parâmetro de oferta na licitação — e o do 2º período corresponde obrigatoriamente à perfuração de um poço exploratório. O cumprimento de cada período é garantido por garantia financeira prestada à ANP, devolvida após a entrega dos dados conforme padrões regulatórios. Aparece nos datasets: Blocos sob Contrato. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_pte', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'PTE — Plano de Trabalho Exploratório: Instrumento de acompanhamento e fiscalização das atividades exploratórias de cada bloco sob contrato de E&P, substituto do Programa Anual de Trabalho e Orçamento e do Plano de Exploração. Deve ser apresentado em até 90 dias da assinatura do contrato de concessão (ou 180 dias no caso de partilha de produção). Ao longo da vigência, o operador envia anualmente: o PTE previsto (outubro) e o PTE realizado (março). Revisões são permitidas conforme condições da Resolução ANP nº 876/2022. A ANP analisa e aprova cada remessa em até 30 dias. O envio é realizado pelo sistema DPP. Aparece nos datasets: Blocos sob Contrato. Fonte: Resolução ANP nº 876/2022.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_periodo-exploratorio', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Período Exploratório: Identificação do período exploratório dos blocos sob contrato: 1º, 2º ou 3º período exploratório, período único ou prorrogado por PAD. Cada período tem prazo definido e obrigações exploratórias mínimas que o contratado deve cumprir. Aparece nos datasets: Blocos sob Contrato. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_uts', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'UTS — Unidades de Trabalho: Unidade de conversão para diferentes trabalhos exploratórios, utilizada para fins de aferição da execução do Programa Exploratório Mínimo (PEM) de cada contrato. Permite comparar diferentes tipos de atividades exploratórias — como perfuração de poços, aquisição sísmica e estudos técnicos — em uma unidade comum. Aparece nos datasets: Blocos sob Contrato. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_fase-exploratoria', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Fase Exploratória: Período total da fase de exploração do bloco contratado. O vencimento da fase exploratória pode ser igual ao vencimento do último período exploratório ou ao vencimento do último PAD, quando a fase estiver prorrogada por plano de avaliação de descobertas. Aparece nos datasets: Blocos sob Contrato. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_etapa-prorrogada', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Etapa Prorrogada: Identifica a etapa do período exploratório que foi prorrogada com base em resolução específica da ANP. Pode ser: período único, 1º e 2º PE conjuntamente, ou apenas o 2º PE. Aparece nos datasets: Resolução ANP nº 708/2017, Resolução ANP nº 815/2020. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_regime-contratual', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Regime Contratual (Contract Regime): Modalidade contratual do bloco exploratório. Concessão: o concessionário assume todos os riscos e detém o petróleo produzido mediante pagamento de tributos. Partilha de produção: o petróleo produzido é dividido entre o contratado e a União, sendo a Petrobras operadora obrigatória nos blocos do pré-sal. Sinônimos: regime, modalidade contratual, regime de exploração, contract regime, contract model, fiscal regime. Exemplos: Concessão (Lei 9.478/1997); Partilha de Produção (Lei 12.351/2010); Cessão Onerosa. Aparece nos datasets: PADs em Andamento, PADs Concluídos, Declarações de Comercialidade. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'contratos', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_pad', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'PAD — Plano de Avaliação de Descobertas (Discovery Evaluation Plan): Instrumento pelo qual o concessionário avalia tecnicamente uma descoberta de hidrocarbonetos para determinar sua viabilidade comercial. Elaborado e entregue à ANP conforme a Resolução ANP nº 845/2021, descreve a descoberta e apresenta programa de trabalho com atividades, prazos e investimentos para avaliação. O código do PAD corresponde ao nome da acumulação principal da área avaliada. Após a conclusão, o PAD resulta em RFAD; se a descoberta for comercial, o RFAD fundamenta a Declaração de Comercialidade. Sinônimos: Plano de Avaliação de Descobertas, PAD, Discovery Evaluation Plan, Appraisal Plan, DEP. Exemplos: PAD Búzios; PAD Mero; PAD Sépia; PAD Atapu. Aparece nos datasets: PADs em Andamento, PADs Concluídos, Declarações de Comercialidade, Resolução ANP nº 815/2020. Fonte: ANP/SEP — SIGEP; Resolução ANP nº 845/2021.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_rfad', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'RFAD — Relatório Final de Avaliação de Descobertas: Documento de encerramento do PAD que consolida as atividades de avaliação realizadas e os resultados da interpretação dos dados. A aprovação do RFAD pela ANP é condição necessária para conferir efetividade a uma eventual Declaração de Comercialidade. Em caso de resultado negativo, encerra o PAD sem declaração. Aparece nos datasets: PADs Concluídos, Declarações de Comercialidade. Fonte: Resolução ANP nº 845/2021.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_poco-anp', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Poço ANP (Well (ANP)): Identificador padronizado atribuído a um poço de petróleo ou gás no Brasil, conforme as regras da Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP). Permite a identificação única em documentos técnicos, sistemas oficiais e comunicações regulatórias. Sinônimos: poço, poço exploratório, poço de petróleo, well, borehole, exploratory well, oil well. Exemplos: 1-RJS-702-RJ (Tupi); 1-BRSA-1135-RJS; 3-BRSA-944-RJS (Búzios); 1-ANP-2-AL. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_notificacao-descoberta', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Notificação de Descoberta: Registro que identifica se ocorreu ou não indícios de hidrocarbonetos durante a perfuração de um poço exploratório. A data da primeira descoberta registra quando foi notificada à ANP a primeira detecção de hidrocarbonetos no poço. Aparece nos datasets: Poços Exploratórios em Blocos. Fonte: ANP/SEP — SIGEP.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_declaracao-comercialidade', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Declaração de Comercialidade: Declaração formal do concessionário à ANP de que uma descoberta de hidrocarbonetos possui viabilidade econômica para produção. Encerra o PAD com resultado positivo e dá início ao planejamento da área de desenvolvimento. Aparece nos datasets: PADs Concluídos, Declarações de Comercialidade. Fonte: ANP/SEP — SIGEP.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_area-desenvolvimento', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Área de Desenvolvimento da Produção (Development Area): Fase intermediária do ciclo de E&P entre a Declaração de Comercialidade e o Primeiro Óleo. Durante essa etapa, o concessionário executa o Plano de Desenvolvimento (PD) aprovado pela ANP: contratação de plataformas, perfuração de poços produtores, instalação de sistemas submarinos e gasodutos. O campo é considerado "em desenvolvimento" enquanto a produção comercial ainda não se iniciou. Sinônimos: área de desenvolvimento, campo, development area, field, producing field. Exemplos: Tupi; Búzios; Mero; Sapinhoá; Lula; Sépia; Atapu. Aparece nos datasets: PADs Concluídos, Declarações de Comercialidade. Fonte: Lei nº 9.478/1997; RANP 810/2020.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_plano-desenvolvimento', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Plano de Desenvolvimento: Documento técnico-econômico obrigatório entregue pelo concessionário à ANP em até 180 dias após a Declaração de Comercialidade. Agrupa informações técnicas, operacionais, econômicas e ambientais da explotação do campo, incluindo abandono. A ANP analisa o PD em até 180 dias; se solicitar modificações, o contratado tem 60 dias para apresentar o PD modificado. Após aprovação, o PD passa a vincular a atuação do concessionário. Em casos de jazidas compartilhadas, deve ser acompanhado do AIP ou do CIP. Aparece nos datasets: Declarações de Comercialidade. Fonte: Resolução ANP nº 17/2015.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_aip', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'AIP — Acordo de Individualização da Produção: Acordo celebrado entre concessionários de blocos distintos que compartilham a mesma jazida de hidrocarbonetos, estabelecendo os termos para a produção individualizada de cada parte. Deve ser submetido à ANP juntamente com o Plano de Desenvolvimento quando houver descoberta em jazida compartilhada. Em situações em que o AIP ainda não está concluído, o CIP pode ser apresentado em substituição provisória. Aparece nos datasets: Declarações de Comercialidade. Fonte: Lei nº 9.478/1997; Resolução ANP nº 17/2015.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_cip', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'CIP — Compromisso de Individualização da Produção: Instrumento provisório apresentado pelos concessionários à ANP quando o Acordo de Individualização da Produção (AIP) ainda não foi concluído, comprometendo-se a celebrá-lo em prazo definido. Acompanha o Plano de Desenvolvimento em casos de jazida compartilhada nos quais o AIP definitivo não está disponível. Aparece nos datasets: Declarações de Comercialidade. Fonte: Lei nº 9.478/1997; Resolução ANP nº 17/2015.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_primeiro-oleo', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Primeiro Óleo: Marco que sinaliza o início da produção comercial em um campo. Para a ANP, é o evento que encerra formalmente a Fase de Desenvolvimento da Produção e inaugura o Campo de Produção. A partir desse ponto, o operador passa a submeter o Programa Anual de Produção (PAP) e a pagar royalties sobre a produção. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_teste-formacao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Teste de Formação: Teste realizado por tubulação com fluxo em superfície para avaliação do reservatório e coleta de amostras de fluido. Abrange os tipos: TIF (identificação de fluidos), TF (poço aberto), TFS (seletivo a poço aberto), TFR (poço revestido) e TFRE (TFR estendido > 72 h). Não exige autorização prévia da ANP, exceto quando realizado no âmbito de PAD ou PD ainda não aprovado. Exige envio do RFTP via DPP em até 60 dias após conclusão. Durante a execução, o operador reporta diariamente via SOP no i-Engine. Aparece nos datasets: PADs em Andamento, PADs Concluídos. Fonte: ANP — Norma de Testes de Poço; Resolução ANP nº 71/2014.', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_tld', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'TLD: Teste de Longa Duração. Realizado dentro de um PAD, com duração total superior a 72 horas de fluxo. Exige autorização prévia específica da ANP, mesmo em PAD aprovado. Sujeito ao pagamento de royalties e participações governamentais. Requer aprovação do sistema de medição fiscal e destino da produção. Documentação obrigatória: TLDI (em até 1 dia após abertura do poço), TLDS (semanal) e TLDF (em até 7 dias após conclusão), todos enviados via i-Engine; além do BMP mensal e RFTP. Internacionalmente corresponde ao Extended Well Test (EWT). Aparece nos datasets: PADs em Andamento, PADs Concluídos. Fonte: ANP — Norma de Testes de Poço (TLD).', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_rftp', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'RFTP: Relatório Final de Teste de Poço. Documento obrigatório enviado à ANP via DPP em até 60 dias após a conclusão de qualquer teste de formação (TIF, TF, TFS, TFR, TFRE, TLD). Contém: relatório operacional (sequência de eventos), planilhas de medições de superfície, relatório de estimulação, esquema de coluna de teste e dados de registradores de fundo. Fonte: ANP — Norma de Testes de Poço.', 'metadata': {'type': 'ontology_term', 'category': 'regulatorio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_i-engine', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'i-Engine: Sistema de webservices da ANP para envio e recebimento de dados técnicos de E&P. Utilizado para: SOP (Situação Operacional de Poços) durante testes de formação, TLDI/TLDS/TLDF durante TLD e BMP mensal na fase de produção. Utiliza formato XML padronizado com tags semânticas para amostra, fase e componente conforme Resolução ANP nº 880/2022. Aparece nos datasets: PADs em Andamento, PADs Concluídos, Declarações de Comercialidade. Fonte: ANP/SEP — Resolução nº 880/2022.', 'metadata': {'type': 'ontology_term', 'category': 'sistemas', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_dpp', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'DPP: Portal de Dados e Projetos da ANP. Sistema utilizado para envio do RFTP e respectivos anexos após a conclusão de testes de formação e TLD. Complementa o i-Engine no fluxo regulatório de entrega de dados técnicos de poço. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'sistemas', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_bmp', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'BMP: Boletim Mensal de Produção. Documento enviado mensalmente à ANP via i-Engine durante a realização de TLD e na fase de produção regular do campo. Informa volumes de óleo, gás e outros fluidos produzidos para efeito de cálculo de royalties e participações governamentais. Aparece nos datasets: Declarações de Comercialidade. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'regulatorio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_rodada-licitacao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Rodada de Licitação (Bidding Round): Ato pelo qual o governo leiloa áreas específicas do seu território para fins de exploração mineral. Identifica em qual rodada o bloco exploratório foi arrematado, permitindo rastrear o histórico de concessões e partilhas no Brasil. Sinônimos: rodada, leilão de blocos, rodada da ANP, bidding round, oil auction, licensing round. Exemplos: 1ª Rodada (1999); 17ª Rodada (2022); 1ª Rodada de Partilha (2013, Libra); Cessão Onerosa (2019). Aparece nos datasets: PADs em Andamento, PADs Concluídos, Declarações de Comercialidade. Fonte: Dicionário enciclopédico inglês-português de geofísica e geologia.', 'metadata': {'type': 'ontology_term', 'category': 'regulatorio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_processo-sancionador', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Processo Sancionador: Processo administrativo resultante da consolidação das autuações relativas à exploração de petróleo e gás natural em trâmite na Superintendência de Exploração (SEP). Registra o auto de infração, o motivo da autuação, a multa aplicada e a situação processual. Aparece nos datasets: Processos Sancionadores. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'regulatorio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_anp', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'ANP: Agência Nacional do Petróleo, Gás Natural e Biocombustíveis. Autarquia federal vinculada ao Ministério de Minas e Energia, responsável pela regulação, contratação e fiscalização das atividades da indústria de petróleo, gás natural e biocombustíveis no Brasil. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos, Declarações de Comercialidade, Processos Sancionadores, Resolução ANP nº 708/2017, Resolução ANP nº 815/2020. Fonte: Lei nº 9478/1997.', 'metadata': {'type': 'ontology_term', 'category': 'regulatorio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_sigep', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'SIGEP: Sistema de Informações Gerenciais de Exploração e Produção. Sistema oficial da ANP que concentra e disponibiliza dados sobre poços, PADs, blocos e contratos de exploração e produção de petróleo e gás natural no Brasil. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos. Fonte: ANP/SEP.', 'metadata': {'type': 'ontology_term', 'category': 'sistemas', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_sep', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'SEP: Superintendência de Exploração da ANP. Unidade organizacional responsável pelo gerenciamento e fiscalização das atividades exploratórias de petróleo e gás natural no Brasil, incluindo o acompanhamento de blocos, poços e PADs. Aparece nos datasets: Poços Exploratórios em Blocos, Blocos sob Contrato, PADs em Andamento, PADs Concluídos, Declarações de Comercialidade, Processos Sancionadores, Resolução ANP nº 708/2017, Resolução ANP nº 815/2020. Fonte: ANP.', 'metadata': {'type': 'ontology_term', 'category': 'sistemas', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_formacao-geologica', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Formação Geológica (Geological Formation): Unidade litoestratigráfica formal com características rochosas homogêneas, definida por suas propriedades litológicas e posição estratigráfica. É a unidade fundamental de mapeamento geológico e equivale ao conceito de GeologicalUnit do GeoCore. Sinônimos: formação, unidade litoestratigráfica, unidade geológica, formation, geological formation, lithostratigraphic unit. Exemplos: Formação Barra Velha (pré-sal); Formação Quissamã; Formação Carapebus; Formação Itapema. Fonte: GeoCore (UFRGS/Geosiris).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_reservatorio', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Reservatório (Reservoir): Corpo rochoso poroso e permeável capaz de armazenar e produzir hidrocarbonetos sob condições de pressão e temperatura adequadas. Equivale ao GeologicalBody do GeoCore com propriedades de porosidade e permeabilidade. O reservatório é a unidade econômica fundamental da exploração de petróleo. Sinônimos: reservatório, rocha-reservatório, corpo reservatório, reservoir, reservoir rock, pay zone. Exemplos: Reservatórios carbonáticos do pré-sal (Coquinas); Reservatórios turbidíticos de Campos; Reservatório Barra Velha. Fonte: GeoCore + GeoReservoir (UFRGS).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_sistema-deposicional', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Sistema Deposicional (Depositional System): Conjunto de ambientes deposicionais geneticamente relacionados que depositaram sedimentos durante um evento ou época geológica. É a base da classificação de reservatórios de águas profundas brasileiros, especialmente os turbidíticos da Bacia de Campos e os carbonáticos do pré-sal de Santos. Sinônimos: sistema deposicional, sistema sedimentar, ambiente deposicional, depositional system, sedimentary system. Exemplos: Sistema turbidítico de águas profundas; Sistema lacustre carbonático (pré-sal); Sistema deltaico. Fonte: GeoReservoir (UFRGS).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_litologia', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Litologia (Lithology): Descrição das características físicas de uma rocha, incluindo composição mineralógica, textura, cor, granulometria e estruturas sedimentares. Derivado do RockMaterial do GeoCore. Fundamental na descrição de testemunhos e cuttings. Sinônimos: litologia, tipo de rocha, descrição litológica, lithology, rock type, lithologic description. Exemplos: Folhelho (shale); Arenito (sandstone); Carbonato (limestone); Coquina; Estromatólito. Fonte: GeoCore (UFRGS/Geosiris).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_completacao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Completação de Poço (Well Completion): Conjunto de operações e equipamentos instalados no poço após a perfuração para viabilizar a produção segura de hidrocarbonetos. Inclui revestimento de produção, tubing (coluna de produção), packers, válvulas de subsuperfície (DHSV) e canhoneio (perforation) das zonas produtoras. Sinônimos: completação, acabamento de poço, well completion, completion. Exemplos: Completação seca (dry tree); Completação molhada (subsea com ANM); Completação inteligente (smart well). Fonte: O3PO (UFRGS).', 'metadata': {'type': 'ontology_term', 'category': 'operacoes', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_lamina-dagua', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': "Lâmina d'Água (Water Depth): Profundidade da coluna de água entre a superfície do mar e o fundo marinho no local do poço. Parâmetro crítico para classificação de poços offshore: águas rasas (< 300 m), águas profundas (300–1500 m), águas ultraprofundas (> 1500 m). Define complexidade tecnológica e custo das operações. Sinônimos: lâmina d'água, profundidade d'água, LDA, water depth, WD, sea depth. Exemplos: Bacia de Campos: ~1.000 m; Pré-sal de Santos: 1.900–2.400 m; Foz do Amazonas: 2.000–2.880 m. Fonte: O3PO (UFRGS).", 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_acumulacao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Acumulação de Hidrocarbonetos (Hydrocarbon Accumulation): Concentração de petróleo ou gás natural em uma armadilha geológica (estrutural, estratigráfica ou mista) com volume e qualidade suficientes para avaliação técnico-econômica. Precede e fundamenta a Declaração de Comercialidade. Distingue-se de "campo" por ainda não ter sido formalmente declarado comercial. Sinônimos: acumulação, descoberta de hidrocarbonetos, jazida, hydrocarbon accumulation, discovery, accumulation. Exemplos: Acumulação de Tupi (descoberta 2006); Acumulação de Búzios; Acumulação de Mero. Fonte: O3PO + GeoCore.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_processo-geologico', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Processo Geológico (Geological Process): Mecanismo natural (sedimentação, diagênese, tectônica, migração de fluidos, evaporação, magmatismo) que gera, modifica ou destrói feições e corpos geológicos ao longo do tempo geológico. Fundamental para entender a formação e preservação de reservatórios e a maturação de hidrocarbonetos. Sinônimos: processo geológico, evento geológico, geological process, geologic process. Exemplos: Sedimentação clástica; Diagênese; Halocinese (tectônica do sal); Migração secundária de hidrocarbonetos. Fonte: GeoCore (UFRGS/Geosiris).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_hidrocarboneto', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Hidrocarboneto (Hydrocarbon): Composto orgânico formado essencialmente por carbono e hidrogênio. No domínio E&P designa óleo, gás natural, condensado e seus derivados. Em PetroGold é o tipo NER PRP quando associado a propriedades; FLU quando designa o fluido. Sinônimos: HC, hidrocarboneto, óleo e gás, hydrocarbon, HC, oil and gas. Exemplos: metano; etano; óleo cru; gás natural úmido; condensado. Fonte: GeoCore / IUPAC.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_querogenio', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Querogênio (Kerogen): Fração da matéria orgânica preservada em rochas sedimentares insolúvel em solventes orgânicos. Classificado em quatro tipos com base em origem e potencial gerador: Tipo I (lacustre, óleo), Tipo II (marinho, óleo+gás), Tipo III (terrígeno, gás), Tipo IV (inertinita, sem potencial). Determina o produto da rocha geradora ao atingir maturação termal. Sinônimos: querogênio, matéria orgânica insolúvel, kerogen. Exemplos: Querogênio Tipo I (lacustre — Lagoa Feia); Querogênio Tipo II (marinho — Cretáceo); Querogênio Tipo III (deltaico). Fonte: GeoCore / Tissot & Welte 1984.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_migracao-hidrocarbonetos', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Migração de Hidrocarbonetos (Hydrocarbon Migration): Processo de deslocamento de hidrocarbonetos da rocha geradora (onde foram formados) até a rocha reservatório, e sua acumulação em armadilha selada por rocha capa. Distingue-se em migração primária (saída do querogênio na rocha geradora) e migração secundária (deslocamento por carrier beds, falhas e descontinuidades estratigráficas). Falhas selantes vs. condutivas controlam fortemente a eficácia da migração. Sinônimos: migração de HC, migração primária, migração secundária, hydrocarbon migration, primary migration, secondary migration. Exemplos: Migração através do Sistema Petrolífero Lagoa Feia-Macabu; Falhas extensionais como conduto de migração no pré-sal. Fonte: GeoCore / PPDM.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_discordancia', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Discordância (Unconformity): Superfície estratigráfica que separa rochas mais novas de rochas mais antigas e representa um hiato deposicional ou erosivo significativo. Pode ser angular, paralela (paraconformidade), erosiva ou de não-deposição. Frequentemente atua como armadilha estratigráfica ou marco regional de correlação sísmica. Sinônimos: discordância, discordância angular, paraconformidade, unconformity, angular unconformity, paraconformity, disconformity. Exemplos: Discordância pré-Aptiana (separa pré-sal de rifte); Discordância intra-Albiana. Fonte: GeoCore / ICS GTS.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_diagenese', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Diagênese (Diagenesis): Conjunto de processos físicos, químicos e biológicos que afetam os sedimentos após a deposição e antes do metamorfismo. Inclui compactação, cimentação, dissolução, dolomitização, recristalização e formação/preenchimento de porosidade secundária. É determinante na qualidade final do reservatório — a permeabilidade dos carbonatos pré-sal é fortemente controlada por diagênese (especialmente dolomitização e dissolução). Sinônimos: diagênese, processo diagenético, diagenesis, diagenetic process. Exemplos: Dolomitização nos carbonatos do pré-sal; Cimentação calcítica; Dissolução geradora de porosidade vugular. Fonte: GeoCore.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_evento-tectonico', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Evento Tectônico (Tectonic Event): Episódio geológico de deformação crustal — rifteamento, abertura oceânica, inversão tectônica, halocinese (movimentação do sal) ou compressão — que altera a geometria das bacias e cria/destrói armadilhas estruturais. No Brasil, o rifteamento Mesozoico abriu as bacias da margem leste e a halocinese pós-Aptiana esculpiu as armadilhas do pré-sal. Sinônimos: evento tectônico, fase tectônica, episódio deformacional, tectonic event, tectonic phase. Exemplos: Rifteamento mesozoico (abertura do Atlântico Sul); Halocinese pós-Aptiana (sal de Santos); Inversão andina. Fonte: GeoCore.', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_contato-geologico', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Contato Geológico (Geological Contact): Superfície ou zona estreita que separa duas unidades geológicas distintas. Pode ser deposicional (concordante), erosivo (discordância), intrusivo ou tectônico (falha). Contatos são o esqueleto de mapas geológicos e de modelos 3D de subsuperfície usados em E&P. Sinônimos: contato geológico, limite estratigráfico, superfície de contato, geological contact, geologic contact, stratigraphic boundary. Exemplos: Contato Aptiano/Albiano (sal sobre carbonatos do pré-sal); Discordância pré-rifte; Contato intrusivo entre soleira de diabásio e folhelho. Fonte: GeoSciML Basic (gsmlb:Contact).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_dobra', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Dobra (Fold): Estrutura geológica formada pela deformação dúctil de camadas rochosas, gerando flexuras (anticlinais e sinclinais). Dobras anticlinais são armadilhas estruturais clássicas em E&P — concentram hidrocarbonetos no topo da flexura. Sinônimos: dobra, flexura, anticlinal, sinclinal, fold, anticline, syncline, flexure. Exemplos: Anticlinal de Carmópolis (Bacia Sergipe-Alagoas); Estrutura dobrada de Quiriri; Dobras sinrifte na Bacia do Recôncavo. Fonte: GeoSciML Basic (gsmlb:Fold).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_foliacao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Foliação (Foliation): Estrutura planar penetrativa em rochas — bandamento, xistosidade, clivagem ardosiana, estratificação. Define anisotropia mecânica e hidráulica em reservatórios fraturados e em rochas-selante. Sinônimos: foliação, xistosidade, clivagem, bandamento, foliation, schistosity, cleavage, banding. Exemplos: Xistosidade nos embasamentos cristalinos; Bandamento gnáissico; Estratificação cruzada em arenitos eólicos. Fonte: GeoSciML Basic (gsmlb:Foliation).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_falha-cisalhante', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Falha de Cisalhamento (Shear Displacement Structure): Estrutura de fratura com deslocamento relativo entre blocos — falhas normais, inversas, transcorrentes. No pré-sal e em Campos, falhas controlam compartimentação de reservatórios e atuam como caminhos ou barreiras para migração de hidrocarbonetos. Sinônimos: falha, estrutura de cisalhamento, falha geológica, plano de falha, fault, shear displacement structure, fault zone. Exemplos: Falhas de borda do rifte de Campos; Falhas transcorrentes da Bacia Potiguar; Falhamentos lístricos sinrifte. Fonte: GeoSciML Basic (gsmlb:ShearDisplacementStructure).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_feature-mapeada', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Feição Mapeada (Mapped Feature): Representação espacial concreta (polígono, linha ou ponto) de uma feição geológica em um mapa ou modelo. Distingue a entidade geológica conceitual (ex: Formação Barra Velha) de sua manifestação cartográfica em uma escala/projeção específica. Sinônimos: feição mapeada, feature cartográfica, ocorrência mapeada, mapped feature, cartographic occurrence. Exemplos: Polígono da Formação Quissamã no mapa geológico 1:250.000; Traço de falha em mapa estrutural. Fonte: GeoSciML Basic (gsmlb:MappedFeature).', 'metadata': {'type': 'ontology_term', 'category': 'geologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_term_metodo-perfuracao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Método de Perfuração (Drilling Method): Técnica empregada para perfuração de poço — rotativa convencional, rotativa direcional, percussão, sondagem por testemunho, hidráulica. Determina diâmetro, taxa de avanço e qualidade do testemunho recuperado. Sinônimos: método de perfuração, técnica de perfuração, drilling method, drilling technique. Exemplos: Perfuração rotativa direcional (poços horizontais do pré-sal); Sondagem com testemunho contínuo; Slimhole drilling. Fonte: GeoSciML Borehole (gsmlbh:drillingMethod).', 'metadata': {'type': 'ontology_term', 'category': 'operacional', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer1', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'BFO + GeoCore (layer1, mantida por UFRGS/BDI + Geosiris (França)): Ontologia formal de geologia com 11 classes baseadas em BFO (Basic Formal Ontology). Define o que entidades geológicas SÃO em termos ontológicos formais. Cobre: GeologicalObject, GeologicalBody, GeologicalUnit, RockMaterial, GeologicalProcess, GeologicalBoundary, GeologicalStructure, GeologicalQuality, GeologicalAge. Cobertura no GeoBrain: bacia-sedimentar, presal, formacao-geologica, reservatorio, litologia, processo-geologico, sistema-deposicional.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer1b', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'GeoSciML + CGI Simple Lithology (layer1b, mantida por OGC + CGI/IUGS (Commission for the Management and Application of Geoscience Information)): Padrão internacional OGC para troca de dados geológicos. Complementa GeoCore com modelo detalhado de Borehole (gsmlbh) e vocabulário canônico de litologias (CGI Simple Lithology, ~437 conceitos). Usado como referência por serviços geológicos nacionais (USGS, BGS, Geoscience Australia, CPRM-BR). Adotado como vocabulário-base por OSDU para LithologyType. Cobertura no GeoBrain: poco, wellbore, bacia-sedimentar, formacao-geologica, reservatorio, litologia, contato-geologico, dobra, foliacao, falha-cisalhante, feature-mapeada.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer2', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'O3PO + GeoReservoir (layer2, mantida por UFRGS/BDI): Ontologias de domínio para produção offshore e reservatórios. O3PO cobre plataformas, poços, tubing, flowlines, manifolds — validado em campo offshore brasileiro real. GeoReservoir cobre sistemas deposicionais de mar profundo. Ambas estendem GeoCore. Cobertura no GeoBrain: poco-anp, reservatorio, sistema-deposicional, completacao, lamina-dagua, acumulacao.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer3', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Petro KGraph (layer3, mantida por PUC-Rio / Petroles): Knowledge graph de O&G em português construído SOBRE GeoCore. Contém 539 conceitos populados com instâncias ANP públicas e relações extraídas de documentos técnicos por NLP. Inclui corpora anotados: PetroGold (NER), PetroNER, PetroRE (extração de relações). É a camada mais adequada para RAG em português — combina formalidade ontológica de GeoCore com praticidade de NLP. Relação com GeoCore: BUILT_ON — Petro KGraph extends GeoCore with Brazilian petroleum instances and NLP annotations. Cobertura no GeoBrain: bacia-sedimentar, poco-anp, bloco, operador, presal, ambiente, bacias-agrupadas, reservatorio, formacao-geologica.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer4', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'OSDU — Open Subsurface Data Universe (layer4, mantida por undefined): Padrão de dados de subsuperfície da indústria petrolífera global. Tripartição Master/Reference/WPC. Não é ontologia formal — é schema de dados para interoperabilidade IT. Essencial para alinhar o dicionário com sistemas de dados que a Petrobras está construindo. Cobertura no GeoBrain: poco, wellbore, campo, bacia-sedimentar, operador, formacao, reservatorio, litologia, classe-fluido, unidade-medida, perfil-poco, topo-formacional, trajetoria-poco, pvt.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer5', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'ANP / SIGEP / Lei 9478/1997 (layer5, mantida por Agência Nacional do Petróleo, Gás Natural e Biocombustíveis): Marco legal e regulatório brasileiro de E&P. ÚNICA camada com cobertura de conceitos jurídico-contratuais brasileiros: Bloco, PAD, Contrato E&P, Rodada de Licitação, UTS, Regime Contratual, Período Exploratório, Etapa Prorrogada, Processo Sancionador. Estes conceitos NÃO existem em nenhuma outra ontologia internacional. Cobertura no GeoBrain: all_23_glossario_terms.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer6', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Geolytics / Petrobras Internal (layer6, mantida por Petrobras / Geolytics): Ontologia operacional interna da Petrobras para o Geolytics. Namespace próprio + ligação a sistemas corporativos. Inclui APENAS definições conceituais públicas — dados Sigilo=Interno NÃO são publicados aqui. Cobertura no GeoBrain: all_modules_extended (M7+M8+M9+M10).', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_ontology_layer_layer7', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'GSO — Geoscience Ontology (Loop3D) (layer7, mantida por Brodaric & Richard — Natural Resources Canada / Geological Survey of Canada): Ontologia de geociência estrutural e materiais rochosos do projeto Loop3D (GSC, Canadá). Cobre falhas, dobras, foliação, lineação, contatos, tempo geológico ICC, e padrão GSOC quality/role/value alinhado a BFO. Domínio adjacente a E&P: complementa OSDU/ontopetro com geologia estrutural rigorosa que era gap no geolytics. 213 classes importadas via scripts/gso-extract.js. Cobertura no GeoBrain: estrutural completo (213 classes); materiais/tempo/processo pendentes.', 'metadata': {'type': 'ontology_term', 'category': 'ontologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_domain_ativos', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Domínio Geolytics "Ativos": Blocos, campos, concessões, PADs, regulatório ANP. Os domínios organizam os termos do dicionário ANP em quatro grupos primários: Ativos (ciclo contratual e regulatório), Fluidos (produção e injeção), Rocha (geologia sedimentar) e Geomecânica (estrutura física dos poços).', 'metadata': {'type': 'ontology_term', 'category': 'dominio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_domain_fluidos', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Domínio Geolytics "Fluidos": Produção e injeção — óleo, gás, água, condensado, CO2, vapor. Os domínios organizam os termos do dicionário ANP em quatro grupos primários: Ativos (ciclo contratual e regulatório), Fluidos (produção e injeção), Rocha (geologia sedimentar) e Geomecânica (estrutura física dos poços).', 'metadata': {'type': 'ontology_term', 'category': 'dominio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_domain_rocha', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Domínio Geolytics "Rocha": Bacias sedimentares, formações, estratigrafia, ambiente deposicional. Os domínios organizam os termos do dicionário ANP em quatro grupos primários: Ativos (ciclo contratual e regulatório), Fluidos (produção e injeção), Rocha (geologia sedimentar) e Geomecânica (estrutura física dos poços).', 'metadata': {'type': 'ontology_term', 'category': 'dominio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_domain_geomecanica', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Domínio Geolytics "Geomecânica": Profundidade, estratificação, stress in-situ (em roadmap). Os domínios organizam os termos do dicionário ANP em quatro grupos primários: Ativos (ciclo contratual e regulatório), Fluidos (produção e injeção), Rocha (geologia sedimentar) e Geomecânica (estrutura física dos poços).', 'metadata': {'type': 'ontology_term', 'category': 'dominio', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_geo_org', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "Geoquímica Orgânica": TOC, pirólise, biomarcadores, maturidade. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_geo_inorg', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "Geoquímica Inorgânica": Isótopos, traços inorgânicos. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_geo_hidro', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "Hidrogeoquímica": Análise de água de formação. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_pvt', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "PVT": Propriedades pressão-volume-temperatura. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_show', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "Show de Fluido": Observação visual em perfuração. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_teste', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "Teste de Formação": DST, teste de produção. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_typology_composicao', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Tipologia geoquímica "Composição Molecular": GC, GC-MS, espectrometria. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.', 'metadata': {'type': 'ontology_term', 'category': 'tipologia', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_processing_primario', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Nível de processamento "Dado Primário": Medida direta de amostra ou análise laboratorial. Indica o grau de transformação do dado bruto até o produto analítico final.', 'metadata': {'type': 'ontology_term', 'category': 'nivel_processamento', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_processing_interpretado', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Nível de processamento "Dado Interpretado": Classificação, mapa ou modelo derivado das medidas. Indica o grau de transformação do dado bruto até o produto analítico final.', 'metadata': {'type': 'ontology_term', 'category': 'nivel_processamento', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
    {'chunk_id': 'geolytics_type_processing_curado', 'source_pdf': 'geolytics-dictionary-v1.1', 'text': 'Nível de processamento "Produto Curado": Dataset validado, harmonizado e versionado. Indica o grau de transformação do dado bruto até o produto analítico final.', 'metadata': {'type': 'ontology_term', 'category': 'nivel_processamento', 'language': 'pt-br+en', 'domain': 'petroleum_exploration'}},
]

# ---------------------------------------------------------------------------
# CHUNK_CATEGORIES — chunk_ids grouped by semantic category for selective injection
# ---------------------------------------------------------------------------
CHUNK_CATEGORIES: dict[str, list[str]] = {
    'contratos': ['geolytics_term_operador', 'geolytics_term_contratados', 'geolytics_term_contrato-ep', 'geolytics_term_pem', 'geolytics_term_pte', 'geolytics_term_periodo-exploratorio', 'geolytics_term_uts', 'geolytics_term_fase-exploratoria', 'geolytics_term_etapa-prorrogada', 'geolytics_term_regime-contratual'],
    'dominio': ['geolytics_domain_ativos', 'geolytics_domain_fluidos', 'geolytics_domain_rocha', 'geolytics_domain_geomecanica'],
    'geologia': ['geolytics_term_bloco', 'geolytics_term_bacia-sedimentar', 'geolytics_term_bacias-agrupadas', 'geolytics_term_ambiente', 'geolytics_term_presal', 'geolytics_term_formacao-geologica', 'geolytics_term_reservatorio', 'geolytics_term_sistema-deposicional', 'geolytics_term_litologia', 'geolytics_term_lamina-dagua', 'geolytics_term_acumulacao', 'geolytics_term_processo-geologico', 'geolytics_term_hidrocarboneto', 'geolytics_term_querogenio', 'geolytics_term_migracao-hidrocarbonetos', 'geolytics_term_discordancia', 'geolytics_term_diagenese', 'geolytics_term_evento-tectonico', 'geolytics_term_contato-geologico', 'geolytics_term_dobra', 'geolytics_term_foliacao', 'geolytics_term_falha-cisalhante', 'geolytics_term_feature-mapeada'],
    'nivel_processamento': ['geolytics_type_processing_primario', 'geolytics_type_processing_interpretado', 'geolytics_type_processing_curado'],
    'ontologia': ['geolytics_ontology_layer_layer1', 'geolytics_ontology_layer_layer1b', 'geolytics_ontology_layer_layer2', 'geolytics_ontology_layer_layer3', 'geolytics_ontology_layer_layer4', 'geolytics_ontology_layer_layer5', 'geolytics_ontology_layer_layer6', 'geolytics_ontology_layer_layer7'],
    'operacional': ['geolytics_term_metodo-perfuracao'],
    'operacoes': ['geolytics_term_pad', 'geolytics_term_rfad', 'geolytics_term_poco-anp', 'geolytics_term_notificacao-descoberta', 'geolytics_term_declaracao-comercialidade', 'geolytics_term_area-desenvolvimento', 'geolytics_term_plano-desenvolvimento', 'geolytics_term_aip', 'geolytics_term_cip', 'geolytics_term_primeiro-oleo', 'geolytics_term_teste-formacao', 'geolytics_term_tld', 'geolytics_term_completacao'],
    'regulatorio': ['geolytics_term_rftp', 'geolytics_term_bmp', 'geolytics_term_rodada-licitacao', 'geolytics_term_processo-sancionador', 'geolytics_term_anp'],
    'sistemas': ['geolytics_term_i-engine', 'geolytics_term_dpp', 'geolytics_term_sigep', 'geolytics_term_sep'],
    'tipologia': ['geolytics_type_typology_geo_org', 'geolytics_type_typology_geo_inorg', 'geolytics_type_typology_geo_hidro', 'geolytics_type_typology_pvt', 'geolytics_type_typology_show', 'geolytics_type_typology_teste', 'geolytics_type_typology_composicao'],
}

# ---------------------------------------------------------------------------
# Cypher
# ---------------------------------------------------------------------------
_MERGE_CYPHER = """
MERGE (c:ReportChunk {chunk_id: $chunk_id})
SET c.source_pdf = $source_pdf,
    c.text = $text,
    c.embedding = $embedding,
    c.metadata_type = $metadata_type,
    c.metadata_category = $metadata_category,
    c.metadata_domain = $metadata_domain
""".strip()

_EXISTS_CYPHER = """
MATCH (c:ReportChunk {chunk_id: $chunk_id}) RETURN count(c) AS n
""".strip()

_COUNT_GEOLYTICS_CYPHER = """
MATCH (c:ReportChunk)
WHERE c.chunk_id STARTS WITH 'geolytics_'
RETURN count(c) AS total,
       collect(DISTINCT c.metadata_category) AS categories
""".strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def inject_corpus(
    driver: Any,
    embedder: Any,
    batch_size: int = 10,
    dry_run: bool = False,
    categories: list[str] | None = None,
) -> dict[str, Any]:
    """Inject GEOLYTICS_RAG_CORPUS chunks into Neo4j as ReportChunk nodes.

    Args:
        driver: A neo4j.Driver instance (neo4j package).
        embedder: Object with an ``embed_documents(texts: list[str]) -> list[list[float]]``
                  method — e.g. ``langchain_openai.OpenAIEmbeddings`` with
                  ``model="text-embedding-3-large"`` and ``dimensions=3072``.
        batch_size: Number of chunks to embed per OpenAI API call.
        dry_run: If True, log actions but do not write to Neo4j or call embedder.
        categories: Optional list of category names (e.g. ["geologia", "contratos"]).
                    When provided only chunks matching these categories are injected.

    Returns:
        dict with keys: injected (int), skipped (int), errors (list[str])
    """
    stats: dict[str, Any] = {"injected": 0, "skipped": 0, "errors": []}

    # Filter corpus by category if requested
    corpus = GEOLYTICS_RAG_CORPUS
    if categories:
        allowed = set(categories)
        corpus = [c for c in corpus if c["metadata"]["category"] in allowed]
        log.info("Category filter active — %d chunks selected from %d total", len(corpus), len(GEOLYTICS_RAG_CORPUS))

    if dry_run:
        log.info("[DRY-RUN] Would inject %d chunks (no writes)", len(corpus))
        for chunk in corpus:
            log.info("[DRY-RUN] chunk_id=%s category=%s len=%d",
                     chunk["chunk_id"], chunk["metadata"]["category"], len(chunk["text"]))
        stats["injected"] = len(corpus)
        return stats

    # Process in batches
    for batch_start in range(0, len(corpus), batch_size):
        batch = corpus[batch_start:batch_start + batch_size]

        # Check which chunk_ids already exist
        to_embed: list[dict[str, Any]] = []
        with driver.session() as session:
            for chunk in batch:
                result = session.run(_EXISTS_CYPHER, chunk_id=chunk["chunk_id"])
                record = result.single()
                if record and record["n"] > 0:
                    log.debug("Skipping existing chunk: %s", chunk["chunk_id"])
                    stats["skipped"] += 1
                else:
                    to_embed.append(chunk)

        if not to_embed:
            continue

        # Generate embeddings for new chunks
        texts = [c["text"] for c in to_embed]
        try:
            embeddings = embedder.embed_documents(texts)
        except Exception as exc:
            err_msg = f"Embedding error for batch starting at index {batch_start}: {exc}"
            log.error(err_msg)
            stats["errors"].append(err_msg)
            continue

        # Write to Neo4j
        with driver.session() as session:
            for chunk, embedding in zip(to_embed, embeddings):
                try:
                    session.run(
                        _MERGE_CYPHER,
                        chunk_id=chunk["chunk_id"],
                        source_pdf=chunk["source_pdf"],
                        text=chunk["text"],
                        embedding=embedding,
                        metadata_type=chunk["metadata"]["type"],
                        metadata_category=chunk["metadata"]["category"],
                        metadata_domain=chunk["metadata"]["domain"],
                    )
                    log.info("Injected: %s (%s)", chunk["chunk_id"], chunk["metadata"]["category"])
                    stats["injected"] += 1
                except Exception as exc:
                    err_msg = f"Neo4j write error for {chunk['chunk_id']}: {exc}"
                    log.error(err_msg)
                    stats["errors"].append(err_msg)

    return stats


def get_corpus_stats() -> dict[str, Any]:
    """Return statistics about the embedded corpus (no external calls).

    Returns:
        dict with keys: total_chunks, by_category (dict), avg_text_length (float),
        min_text_length (int), max_text_length (int)
    """
    by_category: dict[str, int] = {}
    text_lengths: list[int] = []

    for chunk in GEOLYTICS_RAG_CORPUS:
        cat = chunk["metadata"]["category"]
        by_category[cat] = by_category.get(cat, 0) + 1
        text_lengths.append(len(chunk["text"]))

    return {
        "total_chunks": len(GEOLYTICS_RAG_CORPUS),
        "by_category": by_category,
        "avg_text_length": round(sum(text_lengths) / len(text_lengths), 1) if text_lengths else 0.0,
        "min_text_length": min(text_lengths) if text_lengths else 0,
        "max_text_length": max(text_lengths) if text_lengths else 0,
    }


def verify_injection(driver: Any) -> dict[str, Any]:
    """Query Neo4j to check how many geolytics chunks are already indexed.

    Args:
        driver: A neo4j.Driver instance.

    Returns:
        dict with keys: indexed_count (int), categories (list[str]),
        total_in_corpus (int), missing_count (int)
    """
    with driver.session() as session:
        result = session.run(_COUNT_GEOLYTICS_CYPHER)
        record = result.single()
        indexed_count = record["total"] if record else 0
        categories = record["categories"] if record else []

    return {
        "indexed_count": indexed_count,
        "categories": sorted(categories),
        "total_in_corpus": len(GEOLYTICS_RAG_CORPUS),
        "missing_count": max(0, len(GEOLYTICS_RAG_CORPUS) - indexed_count),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_driver() -> Any:
    """Build a Neo4j driver from environment variables."""
    import neo4j  # type: ignore[import]

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    return neo4j.GraphDatabase.driver(uri, auth=(user, password))


def _build_embedder() -> Any:
    """Build an OpenAI embedder using LangChain."""
    from langchain_openai import OpenAIEmbeddings  # type: ignore[import]

    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=3072,
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inject geolytics-dictionary RAG corpus into SPE Volve Neo4j index."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without writing to Neo4j or calling the embedder.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print corpus statistics and exit (no Neo4j connection needed).",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Check how many geolytics chunks are already indexed in Neo4j.",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        metavar="CATEGORY",
        help=(
            "Inject only chunks from these categories. "
            f"Available: {', '.join(sorted(CHUNK_CATEGORIES))}."
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of chunks per embedding API call (default: 10).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if args.stats:
        import pprint
        pprint.pprint(get_corpus_stats())
        return

    if args.dry_run:
        result = inject_corpus(
            driver=None,
            embedder=None,
            batch_size=args.batch_size,
            dry_run=True,
            categories=args.categories,
        )
        print(f"[DRY-RUN] injected={result['injected']} skipped={result['skipped']} errors={len(result['errors'])}")
        return

    driver = _build_driver()
    try:
        if args.verify:
            import pprint
            pprint.pprint(verify_injection(driver))
            return

        embedder = _build_embedder()

        result = inject_corpus(
            driver=driver,
            embedder=embedder,
            batch_size=args.batch_size,
            dry_run=False,
            categories=args.categories,
        )
        print(f"Done — injected={result['injected']} skipped={result['skipped']} errors={len(result['errors'])}")
        if result["errors"]:
            for err in result["errors"]:
                print(f"  ERROR: {err}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
