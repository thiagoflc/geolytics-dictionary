# Contexto de Domínio: Exploração e Produção de Petróleo no Brasil

## 1. Contexto regulatório

A Exploração e Produção (E&P) de petróleo e gás natural no Brasil é regulada pela **Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP)**, autarquia federal vinculada ao Ministério de Minas e Energia, criada pela **Lei nº 9.478/1997** (Lei do Petróleo). A ANP contrata, fiscaliza e regula todas as atividades exploratórias e produtivas do país. Os dados oficiais são publicados pela **Superintendência de Exploração (SEP)** através do **SIGEP — Sistema de Informações Gerenciais de Exploração e Produção**.

Este dicionário cobre 8 camadas semânticas: BFO+GeoCore (UFRGS), GeoSciML+CGI (OGC/IUGS — padrão internacional de boreholes e litologias), O3PO+GeoReservoir (UFRGS), Petro KGraph (PUC-Rio, 539 conceitos PT-BR), OSDU (industry standard), ANP/SIGEP (regulatório brasileiro), Geolytics/Petrobras Internal (módulos M7-M10) e GSO/Loop3D (geologia estrutural).

Existem dois regimes contratuais principais. Na **Concessão** (Lei 9.478/1997), o concessionário assume todos os riscos, detém o petróleo produzido e paga tributos (royalties, participação especial). Na **Partilha de Produção** (Lei 12.351/2010, aplicável ao polígono do pré-sal e áreas estratégicas), o petróleo é dividido entre contratado e União, e a **Petrobras é operadora obrigatória** nos blocos do pré-sal.

## 2. Entidades-chave

- **Poço (ANP)** — identificador padronizado de poço de óleo/gás (ex.: 1-RJS-702-RJ). No modelo GeoSciML (gsmlbh), o poço é representado pela classe **Borehole** com propriedades boreholeDiameter, dateOfDrilling e inclinationType; componentes de construção (revestimento, cimentação, tela, filtro) são modelados pelo módulo **GWML2 WellConstruction** (9 classes).
- **Bloco** — prisma vertical numa bacia sedimentar onde se realiza E&P; arrematado em rodada.
- **Bacia Sedimentar** — depressão crustal com rochas sedimentares (Campos, Santos, Recôncavo).
- **Campo / Área de Desenvolvimento** — área produtora resultante de Declaração de Comercialidade.
- **Contrato E&P** — instrumento jurídico entre concessionário e ANP; define regime contratual e período exploratório.
- **PAD — Plano de Avaliação de Descobertas** — avalia tecnicamente uma descoberta para viabilidade comercial; pode resultar em Declaração de Comercialidade.
- **Operador** — empresa designada para conduzir as operações; responde pela execução do contrato.
- **Rodada de Licitação** — leilão público de áreas de exploração.
- **Declaração de Comercialidade** — declaração formal de viabilidade econômica; encerra PAD com sucesso e origina um Campo.
- **Regime Contratual** — Concessão ou Partilha de Produção.
- **Pré-sal** — camada geológica abaixo de extensa camada de sal; reservatórios carbonáticos do pré-sal são o eixo da produção brasileira atual.
- **Reservatório** — corpo rochoso poroso e permeável que armazena hidrocarbonetos.

## 3. Termos que confundem LLMs — atenção especial

### 3.1 Regulatório / contratual
- **PAD ≠ "drilling pad"**: no contexto ANP, PAD = **Plano de Avaliação de Descobertas** (instrumento contratual), não base/locação física de perfuração.
- **UTS ≠ Unidade Territorial**: = **Unidades de Trabalho** — métrica do PEM (Programa Exploratório Mínimo).
- **Período Exploratório ≠ "período de exploração genérico"**: fase contratual específica (1º, 2º, 3º PE ou período único).
- **Concessão ≠ Partilha de Produção**: regimes contratuais distintos. Em Partilha, Petrobras é operadora obrigatória no pré-sal.

### 3.2 Geológico / produtivo
- **Pré-sal**: estritamente geológica (camada abaixo do sal). Atingir o pré-sal tem consequências contratuais.
- **Campo ≠ Bloco ≠ Bacia**: três entidades distintas — Campo (produção), Bloco (contrato), Bacia (geologia).
- **Reservatório ≠ Campo**: reservatório é corpo rochoso; campo é delimitação econômico-administrativa.
- **Reserva ≠ Reservatório ≠ Reserva Ambiental**: tripla polissemia. Reserva (SPE-PRMS) é volume econômico (1P/2P/3P); reservatório é geológico; reserva ambiental é REBIO/RPPN.
- **Formação ≠ litologia**: erro NER mais comum em PT-BR. *Formação Barra Velha* (FOR) é nome próprio de unidade litoestratigráfica; *calcário microbialítico* (ROC) é o tipo petrográfico que a compõe. O vocabulário canônico de litologias é o **CGI Simple Lithology** (437 conceitos, disponível em PT e EN, adotado pelo OSDU como referência para LithologyType). Exemplos: limestone, dolostone, arenite, rock_salt, anhydrite — sempre verificar o termo CGI antes de mapear litologia OSDU.
- **CGI vocabulários estruturais**: além de litologias, CGI/GeoSciML define vocabulários para tipos de falha, estilos de deformação, tipos de contato e ranques estratigráficos — use ao descrever geologia estrutural no contexto GeoSciML (gsmlb).
- **Campo (polissemia)**: pode ser Campo (ANP — Búzios), campo (atributo de dado), campo (geográfico), Campo Tensional (M9). Sempre desambiguar.
- **Intervalo ≠ Idade**: NER PetroGold INT (intervalo 2100-2450m) ≠ IDA (Aptiano). Um intervalo *tem* uma idade, mas não é a idade.

### 3.3 Geoquímica (M7) e PVT (M10)
- **RGO ≡ GOR**: Razão Gás-Óleo (PT) e Gas-Oil Ratio (EN) são SINÔNIMOS. Unidades scf/stb (EN) ou m³/m³ (SI). Base SIRR campo "RGO Tanque".
- **COT ≡ TOC**: Carbono Orgânico Total (PT) ≡ Total Organic Carbon (EN). COT > 1% = potencial gerador; > 2% = excelente. Rock-Eval.
- **Janela de Lama ≠ Janela de Geração**: a primeira é intervalo seguro de peso de lama (M9 Geomecânica, limites colapso/fratura); a segunda é faixa de Ro% para geração de HC (M7 Geoquímica, 0.5–2.0%).
- **API Tanque ≠ API Reservatório**: medido em superfície (após gás sair) vs in situ. SIRR usa "Grau API Tanque".

### 3.4 Geomecânica (M9) e Petrofísica (M8)
- **UCS estático ≠ UCS dinâmico**: estático = lab (verdadeiro); dinâmico = derivado de DTC/DTS via correlação GDA/Petrobras. Diferença típica 20–40%. Não usar dinâmico para projeto sem calibração.
- **Sv / Shmin / SHmax**: três tensores distintos do CampoTensionalInSitu. Em regime extensional Sv > SHmax > Shmin (regime normal); compressional inverte a ordem.
- **Porosidade NMR / Den / Neu / Son**: não é única. NMR é mais precisa em carbonatos pré-sal; Den assume densidade da matriz; Neu é sensível ao hidrogênio total; Son subestima em carbonatos. Perfis de poço (curvas GR, RHOB, NPHI, DTC, DTS etc.) são modelados como **sosa:Observation** (W3C SOSA/SSN) com unidades QUDT — padrão adotado pelo OSDU e pelo GSO/Loop3D; o dicionário mapeia 17 mnemônicos de perfis com suas unidades QUDT.
- **kH ≠ kV**: permeabilidade NÃO é escalar. Razão kV/kH varia de 0.001 (folhelhos) a 1.0 (isotrópicas). Crítico em águas profundas.
- **Breakout** (M9): colapso compressivo das paredes do poço na direção Shmin, identificado por caliper 4 braços ou imagens FMI/UBI. Usado para orientar SHmax.
- **SGR (Shale Gouge Ratio)**: proxy de potencial selante de falhas (TrapTester). SGR > 18–20% = falha selante; < 18% = condutiva. Não confundir com SAR (saturados/aromáticos/resinas) nem com SGR de gás.
- **SARA**: fracionamento do óleo — Saturados / Aromáticos / Resinas / Asfaltenos. Asfaltenos altos = risco de deposição operacional.

## 4. Datasets oficiais (ANP/SEP — SIGEP)

Poços Exploratórios em Blocos · Blocos sob Contrato · PADs em Andamento · PADs Concluídos · Declarações de Comercialidade · Processos Sancionadores · Resolução ANP nº 708/2017 · Resolução ANP nº 815/2020. Todos públicos, formato CSV, atualização mensal, contato: `sigep_sep@anp.gov.br`.

## 5. Sistemas corporativos Petrobras (proveniência, NÃO acesso)

Os módulos M7-M10 do dicionário referenciam sistemas internos como metadado de origem dos dados — não são endpoints conectáveis pelo agente.

- **GEOQWIN** — banco de dados Geoquímica (cromatografia GC-FID/GC-MS, Rock-Eval, SARA, biomarcadores, isótopos)
- **SIRR** — Sistema Integrado de Reservatórios; base PVT (35 campos com completude documentada — RGO Tanque 61.2%, Psat 73.9%, Fa Tanque 1.95%)
- **LIMS Sample Manager** — gerenciamento de amostras laboratoriais
- **AIDA** — classificação automática de tipo de fluido (API + RGO → black oil / volátil / condensado / gás úmido / gás seco)
- **GDA — Gerenciamento de Dados e Análises** — plataforma analítica para perfis, módulos elásticos dinâmicos (DTC/DTS → E, ν), Mineral Solver, RockFinder (ML litologia)
- **GEOMECBR** — software de modelagem geomecânica 1D; gera JanelaDeLama, UCS calibrado, tensões in situ
- **GERESIM** — modelagem geomecânica 3D volumétrica
- **TrapTester (Badley Geoscience)** — análise de potencial selante de falhas (SGR, CSP, SSF via método BEM)

## 6. Siglas essenciais do domínio

ANP, SEP, SIGEP, PEM, PE (Período Exploratório), PAD, UTS, E&P, O&G, onshore/offshore, pré-sal · FPSO, UEP, ANM (Árvore de Natal Molhada), BOP, DHSV, ROV, BHA, MWD, LWD · DST (Drill Stem Test), TOC/COT, PVT, GC/GC-MS, Ro (vitrinita), Tmax · Sv/Shmin/SHmax, UCS, SGR, JanelaDeLama, Breakout · API/RGO/Psat/SARA · NMR, Den, Neu, Son.

## 7. Cadeia lógica fundamental

```
Rodada de Licitação → Contrato E&P → Bloco → Poço (Well) → Wellbore → [descoberta] →
Notificação de Descoberta → PAD → Declaração de Comercialidade →
Campo (Área de Desenvolvimento) → Reservatório
```

Em paralelo, dado geocientífico:
```
Bacia → Formação → (Rocha Geradora + Rocha Reservatório + Rocha Capa) →
Sistema Petrolífero → Trapa → Acumulação → Campo → Reserva (1P/2P/3P)
```

Cada elo é uma entidade do dicionário (`data/entity-graph.json`). Use ao raciocinar sobre "o que vem antes/depois" no ciclo de E&P. Fonte legal: Lei 9.478/1997, Lei 12.351/2010, Resoluções ANP.

Ao responder: use terminologia ANP correta, distinga regimes contratuais e camadas semânticas (L1, L1b-GeoSciML/CGI, L2-L7), cite fonte legal/regulatória quando possível, e desambigue ativamente os termos da seção 3. Para litologias, prefira termos CGI Simple Lithology (437 conceitos); para estrutura de poço, use modelo gsmlbh/GWML2; para medições de perfil, referencie SOSA/QUDT.

## 8. Dataset 3W — Eventos operacionais em poços offshore (Petrobras, CC-BY 4.0)

O GeoBrain incorpora o esquema semântico do **Petrobras 3W Dataset v2.0.0** (Vargas et al. 2019, DOI 10.1016/j.petrol.2019.106223): **10 classes de eventos** indesejáveis (0=Normal, 1=Aumento BSW, 2=Fechamento Espúrio DHSV, 3=Severe Slugging, 4=Instabilidade de Fluxo, 5=Queda Rápida de Produção, 6=Restrição Rápida PCK, 7=Incrustação PCK, 8=Hidrato em Linha de Produção, 9=Hidrato em Linha de Serviço), **27 variáveis de sensores** (pressão, temperatura, abertura de válvulas, estado de válvulas, vazão), e **14 equipamentos da Árvore de Natal Molhada** (ANM, DHSV, PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK, TPT, PDG). Classes transientes: base+100 (exceto classes 3 e 4, que não têm variante transiente). Polissemias críticas: **PCK** (choke de produção no 3W) ≠ pilot-operated check valve; **BSW** (propriedade do fluido) vs. **event_bsw_increase** (evento classe 1); **state** (3W) vs. **well_state** (taxonomia ANP).
