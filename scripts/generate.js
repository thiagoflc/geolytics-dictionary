#!/usr/bin/env node
/**
 * generate.js — Regenera /data, /api e /ai a partir dos arquivos-fonte do Geolytics.
 *
 * Os dados (GLOSSARIO, CONJUNTOS, ONTOLOGY) ficam embedados aqui para tornar o
 * script standalone. Se quiser sincronizar com o Geolytics, copie os exports
 * de:
 *   src/config/dicionario.js  → GLOSSARIO, CONJUNTOS
 *   src/config/ontology.js    → ONTOLOGY
 *
 * Uso: node scripts/generate.js
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

/* ─────────────────────────────────────────────────────────────
 * SOURCE DATA — copiado de Geolytics src/config/dicionario.js
 * ───────────────────────────────────────────────────────────── */

const GLOSSARIO = [
  { id: 'bloco', termo: 'Bloco', categoria: 'geologia',
    definicao: 'Parte de uma bacia sedimentar, formada por um prisma vertical de profundidade indeterminada, com superfície poligonal definida pelas coordenadas geográficas de seus vértices, onde são desenvolvidas atividades de exploração ou produção de petróleo e gás natural.',
    fonte: 'Lei nº 9478, de 06/08/1997',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade', 'ranp-708', 'ranp-815'] },
  { id: 'bacia-sedimentar', termo: 'Bacia Sedimentar', categoria: 'geologia',
    definicao: 'Depressão da crosta terrestre onde se acumulam rochas sedimentares que podem ser portadoras de petróleo ou gás, associados ou não.',
    fonte: 'Lei nº 9478, de 06/08/1997',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade'] },
  { id: 'bacias-agrupadas', termo: 'Bacias Agrupadas', categoria: 'geologia',
    definicao: 'Agrupamento regional das bacias sedimentares em quatro grupos: Mar — Margem Equatorial (Foz do Amazonas, Pará-Maranhão, Barreirinhas, Ceará, Potiguar marítimo); Mar — Margem Leste (Pernambuco-Paraíba, Sergipe-Alagoas, Jacuípe, Camamu-Almada, Jequitinhonha, Cumuruxatiba, Mucuri, Espírito Santo, Campos, Santos, Pelotas); Terra — Bacias Maduras (Potiguar, Sergipe, Alagoas, Recôncavo, Espírito Santo terrestre); Terra — Bacias de Nova Fronteira (Amazonas, Paraná, Parnaíba, São Francisco, Solimões, Tucano Sul).',
    fonte: 'ANP/SEP',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos'] },
  { id: 'ambiente', termo: 'Ambiente', categoria: 'geologia',
    definicao: 'Localização por ambiente dos blocos exploratórios sob contrato: terra (onshore) ou mar (offshore). Distingue operações terrestres e marítimas para fins de classificação e monitoramento regulatório.',
    fonte: 'ANP/SEP',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade'] },
  { id: 'presal', termo: 'Pré-sal', categoria: 'geologia',
    definicao: 'Camada geológica localizada abaixo de uma extensa camada de sal no subsolo marítimo e terrestre. Identificar se um poço atingiu o pré-sal é informação estratégica para avaliar o potencial exploratório e enquadrar o regime contratual aplicável.',
    fonte: 'ANP/SEP',
    apareceEm: ['pocos-exploratorios'] },
  { id: 'operador', termo: 'Operador', categoria: 'contratos',
    definicao: 'Empresa legalmente designada pelos consorciados para conduzir e executar todas as operações e atividades na área sob contrato, de acordo com o estabelecido no contrato de E&P celebrado entre a contratante e o contratado.',
    fonte: 'ANP/SEP',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade', 'ranp-708', 'ranp-815'] },
  { id: 'contratados', termo: 'Contratados', categoria: 'contratos',
    definicao: 'Empresas contratadas e sua participação, em porcentagem, no contrato de E&P. Inclui o operador e eventuais parceiros do consórcio, com suas respectivas parcelas de participação.',
    fonte: 'ANP/SEP',
    apareceEm: ['blocos-contrato', 'pads-andamento'] },
  { id: 'contrato-ep', termo: 'Contrato de E&P', categoria: 'contratos',
    definicao: 'Contrato de Exploração e Produção assinado entre o agente econômico e a ANP. Estabelece os direitos e obrigações das partes para exploração de petróleo e gás natural em um bloco específico, incluindo o Programa Exploratório Mínimo (PEM) e as condições de produção.',
    fonte: 'ANP/SEP',
    apareceEm: ['blocos-contrato', 'ranp-708', 'ranp-815'] },
  { id: 'periodo-exploratorio', termo: 'Período Exploratório', categoria: 'contratos',
    definicao: 'Identificação do período exploratório dos blocos sob contrato: 1º, 2º ou 3º período exploratório, período único ou prorrogado por PAD. Cada período tem prazo definido e obrigações exploratórias mínimas que o contratado deve cumprir.',
    fonte: 'ANP/SEP',
    apareceEm: ['blocos-contrato'] },
  { id: 'uts', termo: 'UTS — Unidades de Trabalho', categoria: 'contratos',
    definicao: 'Unidade de conversão para diferentes trabalhos exploratórios, utilizada para fins de aferição da execução do Programa Exploratório Mínimo (PEM) de cada contrato. Permite comparar diferentes tipos de atividades exploratórias — como perfuração de poços, aquisição sísmica e estudos técnicos — em uma unidade comum.',
    fonte: 'ANP/SEP',
    apareceEm: ['blocos-contrato'] },
  { id: 'fase-exploratoria', termo: 'Fase Exploratória', categoria: 'contratos',
    definicao: 'Período total da fase de exploração do bloco contratado. O vencimento da fase exploratória pode ser igual ao vencimento do último período exploratório ou ao vencimento do último PAD, quando a fase estiver prorrogada por plano de avaliação de descobertas.',
    fonte: 'ANP/SEP',
    apareceEm: ['blocos-contrato'] },
  { id: 'etapa-prorrogada', termo: 'Etapa Prorrogada', categoria: 'contratos',
    definicao: 'Identifica a etapa do período exploratório que foi prorrogada com base em resolução específica da ANP. Pode ser: período único, 1º e 2º PE conjuntamente, ou apenas o 2º PE.',
    fonte: 'ANP/SEP',
    apareceEm: ['ranp-708', 'ranp-815'] },
  { id: 'regime-contratual', termo: 'Regime Contratual', categoria: 'contratos',
    definicao: 'Modalidade contratual do bloco exploratório. Concessão: o concessionário assume todos os riscos e detém o petróleo produzido mediante pagamento de tributos. Partilha de produção: o petróleo produzido é dividido entre o contratado e a União, sendo a Petrobras operadora obrigatória nos blocos do pré-sal.',
    fonte: 'ANP/SEP',
    apareceEm: ['pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade'] },
  { id: 'pad', termo: 'PAD — Plano de Avaliação de Descobertas', categoria: 'operacoes',
    definicao: 'Instrumento pelo qual o concessionário avalia tecnicamente uma descoberta de hidrocarbonetos para determinar sua viabilidade comercial. O código do PAD corresponde ao nome da acumulação principal da área avaliada. Após a conclusão, o PAD resulta em declaração de comercialidade ou encerramento sem sucesso.',
    fonte: 'ANP/SEP — SIGEP',
    apareceEm: ['pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade', 'ranp-815'] },
  { id: 'poco-anp', termo: 'Poço ANP', categoria: 'operacoes',
    definicao: 'Identificador padronizado atribuído a um poço de petróleo ou gás no Brasil, conforme as regras da Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP). Permite a identificação única em documentos técnicos, sistemas oficiais e comunicações regulatórias.',
    fonte: 'ANP/SEP',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato'] },
  { id: 'notificacao-descoberta', termo: 'Notificação de Descoberta', categoria: 'operacoes',
    definicao: 'Registro que identifica se ocorreu ou não indícios de hidrocarbonetos durante a perfuração de um poço exploratório. A data da primeira descoberta registra quando foi notificada à ANP a primeira detecção de hidrocarbonetos no poço.',
    fonte: 'ANP/SEP — SIGEP',
    apareceEm: ['pocos-exploratorios'] },
  { id: 'declaracao-comercialidade', termo: 'Declaração de Comercialidade', categoria: 'operacoes',
    definicao: 'Declaração formal do concessionário à ANP de que uma descoberta de hidrocarbonetos possui viabilidade econômica para produção. Encerra o PAD com resultado positivo e dá início ao planejamento da área de desenvolvimento.',
    fonte: 'ANP/SEP — SIGEP',
    apareceEm: ['pads-concluidos', 'declaracoes-comercialidade'] },
  { id: 'area-desenvolvimento', termo: 'Área de Desenvolvimento', categoria: 'operacoes',
    definicao: 'Área produtora de petróleo ou gás natural, a partir de um reservatório contínuo ou de mais de um reservatório, a profundidades variáveis. Resulta da declaração de comercialidade após avaliação técnica positiva de uma descoberta.',
    fonte: 'ANP/SEP',
    apareceEm: ['pads-concluidos', 'declaracoes-comercialidade'] },
  { id: 'rodada-licitacao', termo: 'Rodada de Licitação', categoria: 'regulatorio',
    definicao: 'Ato pelo qual o governo leiloa áreas específicas do seu território para fins de exploração mineral. Identifica em qual rodada o bloco exploratório foi arrematado, permitindo rastrear o histórico de concessões e partilhas no Brasil.',
    fonte: 'Dicionário enciclopédico inglês-português de geofísica e geologia',
    apareceEm: ['pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade'] },
  { id: 'processo-sancionador', termo: 'Processo Sancionador', categoria: 'regulatorio',
    definicao: 'Processo administrativo resultante da consolidação das autuações relativas à exploração de petróleo e gás natural em trâmite na Superintendência de Exploração (SEP). Registra o auto de infração, o motivo da autuação, a multa aplicada e a situação processual.',
    fonte: 'ANP/SEP',
    apareceEm: ['processos-sancionadores'] },
  { id: 'anp', termo: 'ANP', categoria: 'regulatorio',
    definicao: 'Agência Nacional do Petróleo, Gás Natural e Biocombustíveis. Autarquia federal vinculada ao Ministério de Minas e Energia, responsável pela regulação, contratação e fiscalização das atividades da indústria de petróleo, gás natural e biocombustíveis no Brasil.',
    fonte: 'Lei nº 9478/1997',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade', 'processos-sancionadores', 'ranp-708', 'ranp-815'] },
  { id: 'sigep', termo: 'SIGEP', categoria: 'sistemas',
    definicao: 'Sistema de Informações Gerenciais de Exploração e Produção. Sistema oficial da ANP que concentra e disponibiliza dados sobre poços, PADs, blocos e contratos de exploração e produção de petróleo e gás natural no Brasil.',
    fonte: 'ANP/SEP',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos'] },
  { id: 'sep', termo: 'SEP', categoria: 'sistemas',
    definicao: 'Superintendência de Exploração da ANP. Unidade organizacional responsável pelo gerenciamento e fiscalização das atividades exploratórias de petróleo e gás natural no Brasil, incluindo o acompanhamento de blocos, poços e PADs.',
    fonte: 'ANP',
    apareceEm: ['pocos-exploratorios', 'blocos-contrato', 'pads-andamento', 'pads-concluidos', 'declaracoes-comercialidade', 'processos-sancionadores', 'ranp-708', 'ranp-815'] },
];

const CONJUNTOS = [
  { id: 'pocos-exploratorios', titulo: 'Poços Exploratórios em Blocos',
    descricao: 'Dados gerais sobre os poços exploratórios que tiveram a perfuração iniciada a partir do ano de 1998.',
    fonte: 'ANP/SEP — SIGEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'POÇO ANP', descricao: 'Identificador padronizado do poço conforme regras da ANP', tipo: 'TEXT' },
      { nome: 'BLOCO', descricao: 'Nome do bloco onde o poço foi perfurado', tipo: 'TEXT' },
      { nome: 'BACIA', descricao: 'Nome da bacia sedimentar', tipo: 'TEXT' },
      { nome: 'BACIAS AGRUPADAS', descricao: 'Agrupamento regional das bacias sedimentares', tipo: 'TEXT' },
      { nome: 'ESTADO', descricao: 'Unidade da Federação', tipo: 'TEXT' },
      { nome: 'AMBIENTE', descricao: 'Localização por ambiente: terra ou mar', tipo: 'TEXT' },
      { nome: 'OPERADOR', descricao: 'Empresa operadora do contrato de E&P', tipo: 'TEXT' },
      { nome: 'INÍCIO DA PERFURAÇÃO', descricao: 'Data em que a perfuração do poço teve início', tipo: 'DATE' },
      { nome: 'CONCLUSÃO DA PERFURAÇÃO', descricao: 'Data em que foi concluída a perfuração', tipo: 'DATE' },
      { nome: 'PROFUNDIDADE FINAL (m)', descricao: 'Profundidade final alcançada pelo poço, em metros', tipo: 'INTEGER' },
      { nome: 'ATINGIU PRÉ-SAL?', descricao: 'Identifica se o poço atingiu o pré-sal', tipo: 'TEXT' },
      { nome: 'NOTIFICAÇÃO DE DESCOBERTA?', descricao: 'Identifica se ocorreu indícios de hidrocarbonetos durante a perfuração', tipo: 'TEXT' },
      { nome: 'DATA DA 1ª DESCOBERTA', descricao: 'Data da primeira descoberta de hidrocarbonetos notificada à ANP', tipo: 'DATE' },
      { nome: 'FLUIDO NOTIFICAÇÃO DE DESCOBERTA', descricao: 'Hidrocarboneto que foi notificada a descoberta à ANP', tipo: 'TEXT' },
    ] },
  { id: 'blocos-contrato', titulo: 'Blocos sob Contrato',
    descricao: 'Dados gerais sobre os blocos exploratórios sob contrato: operador, contratados, bacia, período exploratório, prazos de vencimento e dados técnicos sobre poços e UTS.',
    fonte: 'ANP/SEP — SIGEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'BLOCO', descricao: 'Nome do bloco exploratório', tipo: 'TEXT' },
      { nome: 'CONTRATO', descricao: 'Código do contrato de E&P assinado com a ANP', tipo: 'INTEGER' },
      { nome: 'OPERADOR', descricao: 'Concessionário designado para conduzir as operações', tipo: 'TEXT' },
      { nome: 'CONTRATADOS', descricao: 'Empresas contratadas e sua participação percentual', tipo: 'TEXT' },
      { nome: 'AMBIENTE', descricao: 'Localização por ambiente: terra ou mar', tipo: 'TEXT' },
      { nome: 'BACIAS AGRUPADAS', descricao: 'Agrupamento regional das bacias sedimentares', tipo: 'TEXT' },
      { nome: 'BACIA', descricao: 'Nome da bacia sedimentar', tipo: 'TEXT' },
      { nome: 'ÁREA (MIL km²)', descricao: 'Área do bloco em mil quilômetros quadrados', tipo: 'DECIMAL' },
      { nome: 'RODADA', descricao: 'Identificação da rodada de licitação', tipo: 'TEXT' },
      { nome: 'PERÍODO', descricao: 'Identificação do período exploratório: 1º, 2º, 3º ou único', tipo: 'TEXT' },
      { nome: 'PRESENÇA PAD', descricao: 'Indica se há ou houve Plano de Avaliação de Descobertas', tipo: 'TEXT' },
      { nome: 'DATA DA ASSINATURA CONTRATO', descricao: 'Data de assinatura do contrato de E&P', tipo: 'DATE' },
      { nome: 'DATA INÍCIO SUSPENSÃO', descricao: 'Data de início da suspensão do contrato', tipo: 'DATE' },
      { nome: '1º PE VENCIMENTO', descricao: 'Data de vencimento do 1º período exploratório', tipo: 'DATE' },
      { nome: '2º PE VENCIMENTO', descricao: 'Data de vencimento do 2º período exploratório', tipo: 'DATE' },
      { nome: '3º PE VENCIMENTO', descricao: 'Data de vencimento do 3º período exploratório', tipo: 'DATE' },
      { nome: 'ÚLTIMO PAD VENCIMENTO', descricao: 'Data de vencimento do último PAD', tipo: 'DATE' },
      { nome: 'FASE EXPLORATÓRIA VENCIMENTO', descricao: 'Data de vencimento da fase exploratória do bloco', tipo: 'DATE' },
      { nome: 'UTS COMPROMISSADAS', descricao: 'Unidades de Trabalho comprometidas no Programa Exploratório Mínimo', tipo: 'DECIMAL' },
      { nome: 'QTD DE POÇOS PERFURADOS', descricao: 'Número de poços perfurados na área contratada', tipo: 'INTEGER' },
      { nome: 'POÇOS PERFURADOS', descricao: 'Nome(s) dos poços ANP perfurados na área contratada', tipo: 'TEXT' },
    ] },
  { id: 'pads-andamento', titulo: 'PADs em Andamento',
    descricao: 'Dados gerais sobre os Planos de Avaliação de Descobertas (PADs) atualmente em andamento na fase de exploração.',
    fonte: 'ANP/SEP — SIGEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'CÓDIGO DO PAD', descricao: 'Nome do PAD — corresponde à acumulação principal da área', tipo: 'TEXT' },
      { nome: 'BLOCO', descricao: 'Nome do bloco exploratório', tipo: 'TEXT' },
      { nome: 'BACIA', descricao: 'Nome da bacia sedimentar', tipo: 'TEXT' },
      { nome: 'BACIAS AGRUPADAS', descricao: 'Agrupamento regional das bacias sedimentares', tipo: 'TEXT' },
      { nome: 'AMBIENTE', descricao: 'Localização por ambiente: terra ou mar', tipo: 'TEXT' },
      { nome: 'OPERADOR', descricao: 'Empresa operadora do contrato de E&P', tipo: 'TEXT' },
      { nome: 'CONTRATADOS', descricao: 'Empresas contratadas e sua participação percentual', tipo: 'TEXT' },
      { nome: 'RODADA', descricao: 'Identificação da rodada de licitação', tipo: 'TEXT' },
      { nome: 'REGIME CONTRATUAL', descricao: 'Modalidade contratual: Concessão ou Partilha', tipo: 'TEXT' },
      { nome: 'SITUAÇÃO', descricao: 'Situação atual do PAD', tipo: 'TEXT' },
      { nome: 'INÍCIO EFETIVO', descricao: 'Data do início efetivo do PAD', tipo: 'DATE' },
      { nome: 'TÉRMINO PREVISTO', descricao: 'Data do término previsto do PAD', tipo: 'DATE' },
    ] },
  { id: 'pads-concluidos', titulo: 'PADs Concluídos',
    descricao: 'Dados gerais sobre os Planos de Avaliação de Descobertas (PADs) concluídos na fase de exploração, incluindo resultado de comercialidade e área de desenvolvimento.',
    fonte: 'ANP/SEP — SIGEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'CÓDIGO DO PAD', descricao: 'Nome do PAD — corresponde à acumulação principal da área', tipo: 'TEXT' },
      { nome: 'BLOCO', descricao: 'Nome do bloco exploratório', tipo: 'TEXT' },
      { nome: 'BACIA', descricao: 'Nome da bacia sedimentar', tipo: 'TEXT' },
      { nome: 'AMBIENTE', descricao: 'Localização por ambiente: terra ou mar', tipo: 'TEXT' },
      { nome: 'OPERADOR', descricao: 'Empresa operadora do contrato de E&P', tipo: 'TEXT' },
      { nome: 'RODADA', descricao: 'Identificação da rodada de licitação', tipo: 'TEXT' },
      { nome: 'REGIME CONTRATUAL', descricao: 'Modalidade contratual: Concessão ou Partilha', tipo: 'TEXT' },
      { nome: 'INÍCIO EFETIVO', descricao: 'Data do início efetivo do PAD', tipo: 'DATE' },
      { nome: 'TÉRMINO EFETIVO', descricao: 'Data do término efetivo do PAD', tipo: 'DATE' },
      { nome: 'DECLAROU COMERCIALIDADE', descricao: 'Identifica se ocorreu declaração de comercialidade: Sim ou Não', tipo: 'TEXT' },
      { nome: 'ÁREA DE DESENVOLVIMENTO', descricao: 'Nome da área de desenvolvimento resultante', tipo: 'TEXT' },
    ] },
  { id: 'declaracoes-comercialidade', titulo: 'Declarações de Comercialidade',
    descricao: 'Dados gerais sobre as Declarações de Comercialidade nos blocos sob contrato na fase de exploração.',
    fonte: 'ANP/SEP — SIGEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'CÓDIGO DO PAD', descricao: 'Nome do PAD — corresponde à acumulação principal da área', tipo: 'TEXT' },
      { nome: 'BLOCO(S)', descricao: 'Nome(s) do(s) bloco(s) relacionado(s) à declaração', tipo: 'TEXT' },
      { nome: 'BACIA', descricao: 'Nome da bacia sedimentar', tipo: 'TEXT' },
      { nome: 'AMBIENTE', descricao: 'Localização por ambiente: terra ou mar', tipo: 'TEXT' },
      { nome: 'OPERADOR', descricao: 'Empresa operadora do contrato de E&P', tipo: 'TEXT' },
      { nome: 'RODADA', descricao: 'Identificação da rodada de licitação', tipo: 'TEXT' },
      { nome: 'REGIME CONTRATUAL', descricao: 'Modalidade contratual: Concessão ou Partilha', tipo: 'TEXT' },
      { nome: 'DATA DA DECLARAÇÃO DE COMERCIALIDADE', descricao: 'Data da declaração de comercialidade', tipo: 'DATE' },
      { nome: 'ÁREA DE DESENVOLVIMENTO', descricao: 'Nome da área de desenvolvimento resultante', tipo: 'TEXT' },
    ] },
  { id: 'processos-sancionadores', titulo: 'Processos Sancionadores',
    descricao: 'Dados gerais referente à situação dos Processos Sancionadores de exploração de petróleo e gás natural em trâmite na SEP.',
    fonte: 'ANP/SEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'EMPRESA', descricao: 'Nome da empresa autuada', tipo: 'TEXT' },
      { nome: 'CNPJ/CPF', descricao: 'Número do CNPJ ou CPF do contratado', tipo: 'TEXT' },
      { nome: 'Nº PROCESSO', descricao: 'Número do processo administrativo', tipo: 'TEXT' },
      { nome: 'Nº DF', descricao: 'Número do documento de fiscalização', tipo: 'TEXT' },
      { nome: 'DATA DO AUTO', descricao: 'Data do auto de infração', tipo: 'DATE' },
      { nome: 'MOTIVO', descricao: 'Fundamentação que deu ensejo à autuação', tipo: 'TEXT' },
      { nome: 'SITUAÇÃO PROCESSUAL', descricao: 'Situação do andamento do processo administrativo', tipo: 'TEXT' },
      { nome: 'MULTA APLICADA', descricao: 'Valor da multa aplicada como resultado do processo', tipo: 'DECIMAL' },
      { nome: 'RECURSO', descricao: 'Indica se houve recurso ao processo', tipo: 'TEXT' },
    ] },
  { id: 'ranp-708', titulo: 'Resolução ANP nº 708/2017',
    descricao: 'Dados sobre blocos exploratórios com período exploratório prorrogado pela Resolução ANP nº 708/2017.',
    fonte: 'ANP/SEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'BLOCO', descricao: 'Nome do bloco exploratório', tipo: 'TEXT' },
      { nome: 'CONTRATO', descricao: 'Nome fantasia do contrato de E&P', tipo: 'TEXT' },
      { nome: 'OPERADOR', descricao: 'Empresa operadora do contrato de E&P', tipo: 'TEXT' },
      { nome: 'ETAPA PRORROGADA', descricao: 'Etapa prorrogada: período único, 1º e 2º PE, ou 2º PE', tipo: 'TEXT' },
      { nome: 'DATA DE ADESÃO À RESOLUÇÃO', descricao: 'Data na qual se deu a adesão à Resolução nº 708/2017', tipo: 'DATE' },
    ] },
  { id: 'ranp-815', titulo: 'Resolução ANP nº 815/2020',
    descricao: 'Dados sobre blocos exploratórios com período exploratório prorrogado pela Resolução ANP nº 815/2020.',
    fonte: 'ANP/SEP', formato: 'CSV', frequencia: 'Mensal', contato: 'sigep_sep@anp.gov.br',
    colunas: [
      { nome: 'BLOCO', descricao: 'Nome do bloco exploratório', tipo: 'TEXT' },
      { nome: 'CONTRATO', descricao: 'Nome fantasia do contrato de E&P', tipo: 'TEXT' },
      { nome: 'OPERADOR', descricao: 'Empresa operadora do contrato de E&P', tipo: 'TEXT' },
      { nome: 'ETAPA PRORROGADA', descricao: 'Etapa prorrogada: período único, 1º e 2º PE, ou 2º PE', tipo: 'TEXT' },
      { nome: 'PAD', descricao: 'Nome do Plano de Avaliação de Descobertas associado à prorrogação', tipo: 'TEXT' },
      { nome: 'DATA DE ADESÃO À RESOLUÇÃO', descricao: 'Data na qual se deu a adesão à Resolução nº 815/2020', tipo: 'DATE' },
    ] },
];

const ONTOLOGY_TYPES = {
  tipologia: {
    label: 'Tipologia do Dado',
    desc: 'O que o dado representa quimicamente/operacionalmente',
    items: [
      { id: 'geo_org', label: 'Geoquímica Orgânica', desc: 'TOC, pirólise, biomarcadores, maturidade' },
      { id: 'geo_inorg', label: 'Geoquímica Inorgânica', desc: 'Isótopos, traços inorgânicos' },
      { id: 'geo_hidro', label: 'Hidrogeoquímica', desc: 'Análise de água de formação' },
      { id: 'pvt', label: 'PVT', desc: 'Propriedades pressão-volume-temperatura' },
      { id: 'show', label: 'Show de Fluido', desc: 'Observação visual em perfuração' },
      { id: 'teste', label: 'Teste de Formação', desc: 'DST, teste de produção' },
      { id: 'composicao', label: 'Composição Molecular', desc: 'GC, GC-MS, espectrometria' },
    ],
  },
  nivel: {
    label: 'Nível de Processamento',
    desc: 'Grau de transformação do dado bruto ao produto analítico',
    items: [
      { id: 'primario', label: 'Dado Primário', desc: 'Medida direta de amostra ou análise laboratorial' },
      { id: 'interpretado', label: 'Dado Interpretado', desc: 'Classificação, mapa ou modelo derivado das medidas' },
      { id: 'curado', label: 'Produto Curado', desc: 'Dataset validado, harmonizado e versionado' },
    ],
  },
};

const DOMAINS = [
  { id: 'ativos',      label: 'Ativos',      desc: 'Blocos, campos, concessões, PADs, regulatório ANP' },
  { id: 'fluidos',     label: 'Fluidos',     desc: 'Produção e injeção — óleo, gás, água, condensado, CO2, vapor' },
  { id: 'rocha',       label: 'Rocha',       desc: 'Bacias sedimentares, formações, estratigrafia, ambiente deposicional' },
  { id: 'geomecanica', label: 'Geomecânica', desc: 'Profundidade, estratificação, stress in-situ (em roadmap)' },
];

/* ─────────────────────────────────────────────────────────────
 * ENTITY GRAPH — nós por entidade (não por domínio)
 * ───────────────────────────────────────────────────────────── */

const COLORS = {
  operational: '#378ADD',
  contractual: '#7F77DD',
  actor:       '#D85A30',
  instrument:  '#888780',
  geological:  '#639922',
};
const SIZES = { operational: 28, contractual: 24, actor: 24, instrument: 20, geological: 20 };

/* Mapa: id-entidade-grafo → glossario_id (quando existe) */
const ENTITY_NODES = [
  /* operational */
  { id: 'poco',  label: 'Poço',             label_en: 'Well',                type: 'operational', glossId: 'poco-anp' },
  { id: 'bloco', label: 'Bloco',            label_en: 'Block',               type: 'operational', glossId: 'bloco' },
  { id: 'campo', label: 'Campo',            label_en: 'Field',               type: 'operational', glossId: null,
    definicaoOverride: 'Área produtora de petróleo ou gás natural a partir de um ou mais reservatórios contínuos. No regime ANP, um campo é declarado a partir da Declaração de Comercialidade que confirma a viabilidade econômica da descoberta.',
    fonte: 'ANP/SEP' },
  { id: 'bacia-sedimentar', label: 'Bacia Sedimentar', label_en: 'Sedimentary Basin', type: 'operational', glossId: 'bacia-sedimentar' },

  /* contractual */
  { id: 'contrato-ep',              label: 'Contrato E&P',                 label_en: 'E&P Contract',             type: 'contractual', glossId: 'contrato-ep' },
  { id: 'pad',                      label: 'PAD',                          label_en: 'Discovery Evaluation Plan', type: 'contractual', glossId: 'pad' },
  { id: 'rodada-licitacao',         label: 'Rodada de Licitação',          label_en: 'Bid Round',                type: 'contractual', glossId: 'rodada-licitacao' },
  { id: 'declaracao-comercialidade',label: 'Declaração de Comercialidade', label_en: 'Commerciality Declaration', type: 'contractual', glossId: 'declaracao-comercialidade' },

  /* actor */
  { id: 'operador', label: 'Operador', label_en: 'Operator', type: 'actor', glossId: 'operador' },
  { id: 'anp',      label: 'ANP',      label_en: 'ANP (Brazilian Oil & Gas Regulator)', type: 'actor', glossId: 'anp' },

  /* instrument */
  { id: 'sigep',                  label: 'SIGEP',                  label_en: 'SIGEP (E&P Information System)', type: 'instrument', glossId: 'sigep' },
  { id: 'sep',                    label: 'SEP',                    label_en: 'SEP (ANP Exploration Office)',   type: 'instrument', glossId: 'sep' },
  { id: 'uts',                    label: 'UTS',                    label_en: 'Work Units',                     type: 'instrument', glossId: 'uts' },
  { id: 'regime-contratual',      label: 'Regime Contratual',      label_en: 'Contract Regime',                type: 'instrument', glossId: 'regime-contratual' },
  { id: 'periodo-exploratorio',   label: 'Período Exploratório',   label_en: 'Exploratory Period',             type: 'instrument', glossId: 'periodo-exploratorio' },
  { id: 'processo-sancionador',   label: 'Processo Sancionador',   label_en: 'Sanctioning Proceeding',         type: 'instrument', glossId: 'processo-sancionador' },
  { id: 'notificacao-descoberta', label: 'Notificação Descoberta', label_en: 'Discovery Notification',         type: 'instrument', glossId: 'notificacao-descoberta' },
  { id: 'area-desenvolvimento',   label: 'Área de Desenvolvimento',label_en: 'Development Area',               type: 'instrument', glossId: 'area-desenvolvimento' },

  /* geological */
  { id: 'presal',           label: 'Pré-sal',         label_en: 'Pre-salt',         type: 'geological', glossId: 'presal' },
  { id: 'bacias-agrupadas', label: 'Bacias Agrupadas',label_en: 'Grouped Basins',   type: 'geological', glossId: 'bacias-agrupadas' },
  { id: 'ambiente',         label: 'Ambiente',        label_en: 'Environment',      type: 'geological', glossId: 'ambiente' },
];

const EDGES = [
  { source: 'poco',  target: 'bloco',            relation: 'drilled_in',    relation_label: 'perfurado em',         style: 'solid' },
  { source: 'poco',  target: 'bacia-sedimentar', relation: 'located_in',    relation_label: 'localizado em',        style: 'solid' },
  { source: 'poco',  target: 'operador',         relation: 'operated_by',   relation_label: 'operado por',          style: 'solid' },
  { source: 'poco',  target: 'notificacao-descoberta', relation: 'may_register', relation_label: 'pode registrar', style: 'dashed' },
  { source: 'poco',  target: 'presal',           relation: 'may_reach',     relation_label: 'pode atingir',         style: 'dashed' },

  { source: 'bloco', target: 'bacia-sedimentar', relation: 'delimited_in',  relation_label: 'delimitado em',        style: 'solid' },
  { source: 'bloco', target: 'contrato-ep',      relation: 'governed_by',   relation_label: 'regido por',           style: 'solid' },
  { source: 'bloco', target: 'operador',         relation: 'operated_by',   relation_label: 'operado por',          style: 'solid' },
  { source: 'bloco', target: 'pad',              relation: 'may_have',      relation_label: 'pode ter',             style: 'dashed' },
  { source: 'bloco', target: 'rodada-licitacao', relation: 'originated_in', relation_label: 'originado em',         style: 'solid' },

  { source: 'contrato-ep', target: 'anp',                  relation: 'signed_with',  relation_label: 'celebrado com',  style: 'solid' },
  { source: 'contrato-ep', target: 'regime-contratual',    relation: 'defines',      relation_label: 'define',         style: 'solid' },
  { source: 'contrato-ep', target: 'periodo-exploratorio', relation: 'organized_in', relation_label: 'organizado em',  style: 'solid' },
  { source: 'contrato-ep', target: 'uts',                  relation: 'measured_via', relation_label: 'mede via',       style: 'solid' },

  { source: 'pad', target: 'bloco',                       relation: 'evaluates', relation_label: 'avalia',     style: 'solid' },
  { source: 'pad', target: 'declaracao-comercialidade',   relation: 'may_yield', relation_label: 'pode gerar', style: 'dashed' },

  { source: 'declaracao-comercialidade', target: 'campo', relation: 'originates', relation_label: 'origina', style: 'solid' },
  { source: 'campo',    target: 'bacia-sedimentar', relation: 'located_in',  relation_label: 'localizado em', style: 'solid' },

  { source: 'operador', target: 'processo-sancionador', relation: 'may_have', relation_label: 'pode ter', style: 'dashed' },

  { source: 'anp', target: 'sigep', relation: 'manages_via',   relation_label: 'gerencia via',  style: 'solid' },
  { source: 'anp', target: 'sep',   relation: 'oversees_via',  relation_label: 'fiscaliza via', style: 'solid' },
];

/* ─────────────────────────────────────────────────────────────
 * BUILDERS
 * ───────────────────────────────────────────────────────────── */

const NOW = new Date().toISOString();
const VERSION = '1.0.0';

function gloss(id) { return GLOSSARIO.find((t) => t.id === id); }

function buildGlossary() {
  return {
    meta: { version: VERSION, generated: NOW, count: GLOSSARIO.length },
    terms: GLOSSARIO,
  };
}

function buildDatasets() {
  return {
    meta: { version: VERSION, generated: NOW, count: CONJUNTOS.length },
    datasets: CONJUNTOS,
  };
}

function buildOntologyTypes() {
  return {
    meta: { version: VERSION, generated: NOW },
    domains: DOMAINS,
    typology: ONTOLOGY_TYPES.tipologia,
    processing_levels: ONTOLOGY_TYPES.nivel,
  };
}

function buildEntityGraph() {
  const nodes = ENTITY_NODES.map((n) => {
    const g = n.glossId ? gloss(n.glossId) : null;
    return {
      id: n.id,
      label: n.label,
      label_en: n.label_en,
      type: n.type,
      color: COLORS[n.type],
      size: SIZES[n.type],
      definition: n.definicaoOverride || (g ? g.definicao : ''),
      legal_source: n.fonte || (g ? g.fonte : null),
      datasets: g && Array.isArray(g.apareceEm) ? g.apareceEm : [],
      kgraph_uri: null,
      glossary_id: n.glossId || null,
    };
  });
  return {
    version: VERSION,
    generated: NOW,
    source: 'Geolytics / ANP-SEP / SIGEP',
    nodes,
    edges: EDGES,
  };
}

function buildFull() {
  return {
    meta: {
      version: VERSION,
      generated: NOW,
      counts: {
        terms: GLOSSARIO.length,
        datasets: CONJUNTOS.length,
        entities: ENTITY_NODES.length,
        edges: EDGES.length,
        domains: DOMAINS.length,
      },
    },
    glossary: GLOSSARIO,
    datasets: CONJUNTOS,
    ontology: { domains: DOMAINS, typology: ONTOLOGY_TYPES.tipologia, processing_levels: ONTOLOGY_TYPES.nivel },
    entity_graph: { nodes: buildEntityGraph().nodes, edges: EDGES },
  };
}

/* ─────────────────────────────────────────────────────────────
 * API v1
 * ───────────────────────────────────────────────────────────── */

const BASE_URL_PLACEHOLDER = 'https://thiagoflc.github.io/geolytics-dictionary';

function buildApiIndex() {
  return {
    meta: { version: VERSION, generated: NOW, base_url: BASE_URL_PLACEHOLDER },
    endpoints: {
      terms:        `${BASE_URL_PLACEHOLDER}/api/v1/terms.json`,
      entities:     `${BASE_URL_PLACEHOLDER}/api/v1/entities.json`,
      datasets:     `${BASE_URL_PLACEHOLDER}/api/v1/datasets.json`,
      search_index: `${BASE_URL_PLACEHOLDER}/api/v1/search-index.json`,
      glossary:     `${BASE_URL_PLACEHOLDER}/data/glossary.json`,
      entity_graph: `${BASE_URL_PLACEHOLDER}/data/entity-graph.json`,
      ontology:     `${BASE_URL_PLACEHOLDER}/data/ontology-types.json`,
      full:         `${BASE_URL_PLACEHOLDER}/data/full.json`,
      rag_corpus:   `${BASE_URL_PLACEHOLDER}/ai/rag-corpus.jsonl`,
      system_prompt_pt: `${BASE_URL_PLACEHOLDER}/ai/system-prompt-ptbr.md`,
      system_prompt_en: `${BASE_URL_PLACEHOLDER}/ai/system-prompt-en.md`,
    },
  };
}

function buildApiTerms() {
  return {
    meta: { version: VERSION, generated: NOW, count: GLOSSARIO.length },
    terms: GLOSSARIO.map((t) => ({
      id: t.id,
      termo: t.termo,
      categoria: t.categoria,
      definicao: t.definicao,
      fonte: t.fonte,
      datasets: t.apareceEm,
    })),
  };
}

function buildApiEntities() {
  const graph = buildEntityGraph();
  const inEdges = (id) => graph.edges.filter((e) => e.target === id).map((e) => ({ from: e.source, relation: e.relation, label: e.relation_label, style: e.style }));
  const outEdges = (id) => graph.edges.filter((e) => e.source === id).map((e) => ({ to: e.target, relation: e.relation, label: e.relation_label, style: e.style }));
  return {
    meta: { version: VERSION, generated: NOW, count: graph.nodes.length },
    entities: graph.nodes.map((n) => ({
      ...n,
      relations: { outgoing: outEdges(n.id), incoming: inEdges(n.id) },
    })),
  };
}

function buildApiDatasets() {
  return {
    meta: { version: VERSION, generated: NOW, count: CONJUNTOS.length },
    datasets: CONJUNTOS.map((c) => ({
      id: c.id,
      titulo: c.titulo,
      descricao: c.descricao,
      fonte: c.fonte,
      formato: c.formato,
      frequencia: c.frequencia,
      contato: c.contato,
      colunas: c.colunas,
      terms_referenced: GLOSSARIO.filter((t) => Array.isArray(t.apareceEm) && t.apareceEm.includes(c.id)).map((t) => t.id),
    })),
  };
}

function tokenize(s) {
  return (s || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9 ]+/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 2);
}

function buildSearchIndex() {
  const items = [];
  for (const t of GLOSSARIO) {
    items.push({
      id: `term:${t.id}`,
      type: 'term',
      title: t.termo,
      text: `${t.termo}. ${t.definicao} Fonte: ${t.fonte}.`,
      tokens: Array.from(new Set(tokenize(`${t.termo} ${t.definicao} ${t.fonte}`))),
    });
  }
  for (const c of CONJUNTOS) {
    items.push({
      id: `dataset:${c.id}`,
      type: 'dataset',
      title: c.titulo,
      text: `${c.titulo}. ${c.descricao} Fonte: ${c.fonte}.`,
      tokens: Array.from(new Set(tokenize(`${c.titulo} ${c.descricao} ${c.fonte}`))),
    });
  }
  for (const n of buildEntityGraph().nodes) {
    items.push({
      id: `entity:${n.id}`,
      type: 'entity',
      title: n.label,
      text: `${n.label} (${n.label_en}). ${n.definition}`,
      tokens: Array.from(new Set(tokenize(`${n.label} ${n.label_en} ${n.definition}`))),
    });
  }
  return { meta: { version: VERSION, generated: NOW, count: items.length }, items };
}

/* ─────────────────────────────────────────────────────────────
 * RAG CORPUS — JSONL
 * ───────────────────────────────────────────────────────────── */

function datasetTitle(id) {
  const c = CONJUNTOS.find((x) => x.id === id);
  return c ? c.titulo : id;
}

function buildRagCorpus() {
  const lines = [];

  /* type=term */
  for (const t of GLOSSARIO) {
    const datasetTitles = (t.apareceEm || []).map(datasetTitle).join(', ');
    const text = `${t.termo}: ${t.definicao} Fonte: ${t.fonte}.${datasetTitles ? ` Aparece nos datasets: ${datasetTitles}.` : ''}`;
    lines.push({
      id: `term_${t.id}`,
      type: 'term',
      text,
      metadata: {
        id: t.id,
        category: t.categoria,
        legal_source: t.fonte,
        datasets: t.apareceEm || [],
      },
    });
  }

  /* type=column */
  for (const c of CONJUNTOS) {
    for (const col of c.colunas) {
      const text = `Coluna "${col.nome}" do dataset "${c.titulo}" (${c.id}): ${col.descricao}. Tipo: ${col.tipo}. Fonte do dataset: ${c.fonte}. Frequência: ${c.frequencia}.`;
      lines.push({
        id: `column_${c.id}_${col.nome.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')}`,
        type: 'column',
        text,
        metadata: {
          dataset_id: c.id,
          dataset_title: c.titulo,
          column_name: col.nome,
          column_type: col.tipo,
          source: c.fonte,
        },
      });
    }
  }

  /* type=entity */
  for (const n of buildEntityGraph().nodes) {
    const outRels = EDGES.filter((e) => e.source === n.id).map((e) => `${e.relation_label} ${ENTITY_NODES.find((x) => x.id === e.target)?.label || e.target}`);
    const text = `Entidade "${n.label}" (${n.label_en}), tipo ${n.type}. ${n.definition}${outRels.length ? ` Relações: ${outRels.join('; ')}.` : ''}${n.legal_source ? ` Fonte: ${n.legal_source}.` : ''}`;
    lines.push({
      id: `entity_${n.id}`,
      type: 'entity',
      text,
      metadata: {
        id: n.id,
        entity_type: n.type,
        label_en: n.label_en,
        legal_source: n.legal_source,
        datasets: n.datasets,
      },
    });
  }

  /* type=domain */
  for (const d of DOMAINS) {
    lines.push({
      id: `domain_${d.id}`,
      type: 'domain',
      text: `Domínio Geolytics "${d.label}": ${d.desc}. Os domínios organizam os termos do dicionário ANP em quatro grupos primários: Ativos (ciclo contratual e regulatório), Fluidos (produção e injeção), Rocha (geologia sedimentar) e Geomecânica (estrutura física dos poços).`,
      metadata: { id: d.id, label: d.label },
    });
  }

  /* type=type — tipologia geoquímica */
  for (const item of ONTOLOGY_TYPES.tipologia.items) {
    lines.push({
      id: `type_typology_${item.id}`,
      type: 'type',
      text: `Tipologia geoquímica "${item.label}": ${item.desc}. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.`,
      metadata: { id: item.id, group: 'typology', label: item.label },
    });
  }
  /* type=type — níveis de processamento */
  for (const item of ONTOLOGY_TYPES.nivel.items) {
    lines.push({
      id: `type_processing_${item.id}`,
      type: 'type',
      text: `Nível de processamento "${item.label}": ${item.desc}. Indica o grau de transformação do dado bruto até o produto analítico final.`,
      metadata: { id: item.id, group: 'processing_level', label: item.label },
    });
  }

  return lines.map((l) => JSON.stringify(l)).join('\n') + '\n';
}

/* ─────────────────────────────────────────────────────────────
 * SYSTEM PROMPTS
 * ───────────────────────────────────────────────────────────── */

const SYSTEM_PROMPT_PT = `# Contexto de domínio — Petróleo & Gás (Brasil)

Você é um agente conversacional especializado no domínio de Exploração e Produção (E&P) de petróleo e gás natural no Brasil. O setor é regulado pela **Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP)**, autarquia federal vinculada ao Ministério de Minas e Energia, criada pela **Lei nº 9.478/1997** (Lei do Petróleo). A ANP contrata, fiscaliza e regula todas as atividades exploratórias e produtivas do país.

A relação entre Estado e empresa é mediada por **contratos de E&P** (Concessão ou Partilha de Produção), assinados em **Rodadas de Licitação** públicas. Cada contrato vincula uma empresa **Operadora** (com participação de **Contratados**) a um **Bloco** exploratório dentro de uma **Bacia Sedimentar**. Os dados oficiais são publicados pela **Superintendência de Exploração (SEP)** da ANP através do sistema **SIGEP — Sistema de Informações Gerenciais de Exploração e Produção**.

## Entidades-chave

- **Poço (ANP)**: identificador padronizado de poço de óleo/gás no Brasil.
- **Bloco**: prisma vertical numa bacia sedimentar onde se realiza E&P; arrematado em rodada de licitação.
- **Campo**: área produtora resultante de uma Declaração de Comercialidade.
- **Bacia Sedimentar**: depressão da crosta com rochas sedimentares possivelmente portadoras de hidrocarbonetos.
- **Contrato de E&P**: instrumento jurídico entre concessionário e ANP; define **Regime Contratual** (Concessão ou Partilha) e **Período Exploratório**.
- **PAD — Plano de Avaliação de Descobertas**: avalia tecnicamente uma descoberta para determinar viabilidade comercial; pode resultar em Declaração de Comercialidade.
- **Operador**: empresa designada para conduzir as operações; responde pela execução do contrato.
- **Rodada de Licitação**: leilão público de áreas de exploração.
- **Declaração de Comercialidade**: declaração formal de viabilidade econômica de uma descoberta; encerra o PAD com sucesso e origina um Campo.

## Termos que confundem — alertas

- **PAD ≠ "pad exploratório / pad de perfuração"**: no contexto ANP, PAD é o Plano de Avaliação de Descobertas (instrumento contratual), não a base/locação física de perfuração.
- **UTS ≠ Unidade Territorial**: aqui significa **Unidades de Trabalho** — métrica de conversão para aferir o cumprimento do **PEM (Programa Exploratório Mínimo)**.
- **Período Exploratório ≠ "período de exploração genérico"**: é uma fase contratual específica (1º, 2º, 3º PE ou período único), com prazos e obrigações exploratórias mínimas.
- **Pré-sal**: definição estritamente geológica — camada abaixo de uma extensa camada de sal no subsolo. Atingir o pré-sal é dado oficial registrado por poço e tem consequências contratuais.
- **Concessão vs. Partilha**: regimes contratuais distintos. Em Partilha, a Petrobras é operadora obrigatória nos blocos do pré-sal; o petróleo produzido é dividido com a União.

## Datasets oficiais (ANP/SEP — SIGEP)

Poços Exploratórios em Blocos · Blocos sob Contrato · PADs em Andamento · PADs Concluídos · Declarações de Comercialidade · Processos Sancionadores · Resolução ANP nº 708/2017 · Resolução ANP nº 815/2020. Todos públicos, formato CSV, atualização mensal, contato: \`sigep_sep@anp.gov.br\`.

## Siglas

ANP, SEP, SIGEP, PEM (Programa Exploratório Mínimo), PE (Período Exploratório), PAD (Plano de Avaliação de Descobertas), UTS (Unidades de Trabalho), E&P (Exploração e Produção), DST (Drill Stem Test, teste de formação), TOC (Total Organic Carbon), PVT (Pressão-Volume-Temperatura), GC (Gas Chromatography).

Ao responder, use a terminologia ANP correta, distinga regimes contratuais quando relevante, e cite a fonte legal/regulatória sempre que possível (Lei 9.478/1997, resoluções ANP).
`;

const SYSTEM_PROMPT_EN = `# Domain context — Brazilian Oil & Gas (E&P)

You are a conversational agent specialized in the upstream (Exploration & Production, *E&P*) oil and gas sector in Brazil. The sector is regulated by the **National Agency of Petroleum, Natural Gas and Biofuels — *ANP*** (federal regulatory agency under the Ministry of Mines and Energy), established by **Law No. 9,478/1997** (the *Lei do Petróleo*). ANP contracts, oversees, and regulates all exploratory and productive activity in the country.

The State–company relationship is mediated by *contratos de E&P* (E&P contracts under Concession or Production Sharing regimes), signed at public bid rounds (*Rodadas de Licitação*). Each contract binds an **Operator** (*Operador*, with participating **Contractors** / *Contratados*) to an exploratory **Block** (*Bloco*) within a **Sedimentary Basin** (*Bacia Sedimentar*). Official data is published by ANP's **Exploration Office (*SEP*)** through the **SIGEP** information system.

## Key entities

- **Well (Poço ANP)**: standardized oil/gas well identifier in Brazil.
- **Block (*Bloco*)**: vertical prism within a sedimentary basin where E&P is carried out; awarded at a bid round.
- **Field (*Campo*)**: producing area resulting from a Commerciality Declaration.
- **Sedimentary Basin (*Bacia Sedimentar*)**: crustal depression containing sedimentary rocks possibly bearing hydrocarbons.
- **E&P Contract (*Contrato de E&P*)**: legal instrument between concessionaire and ANP; defines the **Contract Regime** (Concession or Production Sharing) and the **Exploratory Period**.
- **PAD (*Plano de Avaliação de Descobertas*)**: discovery evaluation plan that technically assesses a hydrocarbon discovery for commercial viability; may yield a Commerciality Declaration.
- **Operator (*Operador*)**: company designated to conduct operations; accountable for contract execution.
- **Bid Round (*Rodada de Licitação*)**: public auction of exploration acreage.
- **Commerciality Declaration (*Declaração de Comercialidade*)**: formal declaration of economic viability of a discovery; closes the PAD successfully and originates a Field.

## Confusable terms — explicit alerts

- **PAD ≠ "drilling pad"**: in the ANP context, PAD is the *Plano de Avaliação de Descobertas* (a contractual evaluation plan), **not** the physical drilling pad/location.
- **UTS ≠ "territorial unit"**: it means *Unidades de Trabalho* (Work Units) — a conversion metric used to verify compliance with the **PEM** (Minimum Exploratory Program).
- **Período Exploratório ≠ generic "exploration period"**: it's a specific contractual phase (1st, 2nd, 3rd PE, or single period), each with defined deadlines and minimum exploratory obligations.
- **Pré-sal**: strictly geological — layer beneath an extensive salt layer in the subsurface. Whether a well reached the pre-salt is an officially recorded fact with contractual implications.
- **Concession vs. Production Sharing**: distinct contract regimes. Under Production Sharing, Petrobras is the mandatory operator in pre-salt blocks and produced oil is split with the Union.

## Official datasets (ANP/SEP — SIGEP)

Exploratory Wells in Blocks · Blocks under Contract · PADs in Progress · Completed PADs · Commerciality Declarations · Sanctioning Proceedings · ANP Resolution 708/2017 · ANP Resolution 815/2020. All public, CSV format, monthly updates, contact: \`sigep_sep@anp.gov.br\`.

## Acronyms

ANP, SEP, SIGEP, PEM (Minimum Exploratory Program), PE (Exploratory Period), PAD, UTS (Work Units), E&P, DST (Drill Stem Test), TOC (Total Organic Carbon), PVT (Pressure-Volume-Temperature), GC (Gas Chromatography).

When answering, use correct ANP terminology, distinguish contract regimes where relevant, and cite the legal/regulatory source where possible (Law 9,478/1997, ANP resolutions). Brazilian-Portuguese terms are kept in italics on first occurrence and may be used directly in subsequent mentions.
`;

/* ─────────────────────────────────────────────────────────────
 * WRITE FILES
 * ───────────────────────────────────────────────────────────── */

function writeJson(rel, obj) {
  const p = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + '\n', 'utf8');
  console.log(`  ✓ ${rel}`);
}

function writeText(rel, content) {
  const p = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content, 'utf8');
  console.log(`  ✓ ${rel}`);
}

console.log('Generating data/...');
writeJson('data/glossary.json',       buildGlossary());
writeJson('data/datasets.json',       buildDatasets());
writeJson('data/entity-graph.json',   buildEntityGraph());
writeJson('data/ontology-types.json', buildOntologyTypes());
writeJson('data/full.json',           buildFull());

console.log('Generating api/v1/...');
writeJson('api/v1/index.json',        buildApiIndex());
writeJson('api/v1/terms.json',        buildApiTerms());
writeJson('api/v1/entities.json',     buildApiEntities());
writeJson('api/v1/datasets.json',     buildApiDatasets());
writeJson('api/v1/search-index.json', buildSearchIndex());

console.log('Generating ai/...');
writeText('ai/rag-corpus.jsonl',       buildRagCorpus());
writeText('ai/system-prompt-ptbr.md',  SYSTEM_PROMPT_PT);
writeText('ai/system-prompt-en.md',    SYSTEM_PROMPT_EN);

console.log('\n✓ Done.');
console.log(`  Terms: ${GLOSSARIO.length}`);
console.log(`  Datasets: ${CONJUNTOS.length}`);
console.log(`  Entity nodes: ${ENTITY_NODES.length}`);
console.log(`  Entity edges: ${EDGES.length}`);
