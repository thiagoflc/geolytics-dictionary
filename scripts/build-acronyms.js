#!/usr/bin/env node
/**
 * build-acronyms.js — Parser, limpador e categorizador do siglário O&G.
 *
 * Lê scripts/acronyms-source.txt, parseia cada linha "SIGLA. – PRINCIPAL (ALT)",
 * detecta língua de cada lado por diacríticos, categoriza por keyword matching,
 * deduplica e produz data/acronyms.json.
 *
 * Categorias (campo `category`):
 *   regulator, standard_body, equipment, process, contract, environmental,
 *   measurement, unit, fluid, lithology, well_state, geophysics, it_generic,
 *   organization, general
 *
 * `it_generic: true` é uma flag (não categoria) para excluir do RAG corpus
 * siglas puramente computacionais que não pertencem ao domínio O&G.
 *
 * Uso: node scripts/build-acronyms.js
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'scripts/acronyms-source.txt');
const OUT = path.join(ROOT, 'data/acronyms.json');

/* ─────────────────────────────────────────────────────────────
 * Detecção de língua via diacríticos + palavras-chave
 * ───────────────────────────────────────────────────────────── */

const PT_DIACRITICS = /[ãáàâçéêíõóôúüÃÁÀÂÇÉÊÍÕÓÔÚÜ]/;
const PT_KEYWORDS = /\b(Associação|Brasileira|Brasileiro|Brasil|Análise|Avaliação|Sistema|Razão|Pressão|Profundidade|Coluna|Bomba|Válvula|Árvore|Lâmina|Embarcação|Plataforma|Equipamento|Estudo|Relatório|Instituto|Conselho|Agência|Comissão|Câmara|Federação|Confederação|Superintendência|Secretaria|Tubulação|Pertinente|Contratante|Operadora|Recuperação|Penetração|Decimal|Codificação|Modulação|Frequência|Acordo)\b/i;

function isPortuguese(s) {
  return PT_DIACRITICS.test(s) || PT_KEYWORDS.test(s);
}

/* ─────────────────────────────────────────────────────────────
 * Regras de categorização (ordem importa: primeira regra que casa vence)
 * ───────────────────────────────────────────────────────────── */

const CATEGORY_RULES = [
  /* IT-generic: termos puramente computacionais sem peso O&G */
  { cat: 'it_generic', re: /\b(memory|memória|read-only|random access|complementary metal|metal-oxide|transistor logic|binary coded|programmable read-only|object model|component object|electronically erasable|erasable programmable|interconnection|local area network|distributed component|fiber bragg|amplitude modulation|frequency modulation|phase modulation|pulse code modulation|pulse width modulation|fast fourier|frequency domain|cathode ray|hard disk|biblioteca de ligação|highway addressable|n-type metal|bipolar complementary|interconexão de sistemas)\b/i },

  /* Regulators (governo / agências reguladoras) */
  { cat: 'regulator', re: /\b(agência|agency|autarquia|superintendência|ministério|ministry|órgão regulador|conselho nacional|national council|securities and exchange|autoridade|government agency|federal agency|conselho|brazilian institute of environment|environmental protection agency|conselho de política energética|conselho do meio ambiente|conselho nacional de metrologia|comissão de valores|consolidação das leis|laws of brazil|departamento de minas)\b/i },

  /* Standard bodies / industry associations */
  { cat: 'standard_body', re: /\b(associação|association|society of|sociedade|federação|federation|comissão pan-?americana|comitê técnico|technical committee|forum|fórum|congresso|congress|chamber|câmara|standardization|normalização|institute of (?:cost|metrology|quality|engineering|industrial property|geography|steel|petroleum|environment)|standards|normas técnicas|brazilian (?:institute|association|industry)|american (?:society|association|institute|petroleum|welding|society for|bureau)|international (?:organization|electrotechnical|maritime|safety|energy|standards)|world (?:petroleum|intellectual)|organization of petroleum|organização|portuguese association|coordinating european)\b/i },

  /* Environmental */
  { cat: 'environmental', re: /\b(ambiental|environmental|impacto ambiental|impact study|impact report|impact assessment|impact declaration|impact evaluation|conservação|conservation|preservação|preservation|reserva (?:biológica|particular|natural)|biological reserve|nature conservation|coastal|costeira|costeiro|emergência|emergency control|spill|derramamento|poluição|pollution|carbono|carbon emission|greenhouse|reabilitação ambiental|estudo (?:ambiental|de viabilidade ambiental|de impacto)|relatório (?:de impacto|de qualidade ambiental|de avaliação ambiental|de controle ambiental)|plano (?:de controle ambiental|de descomissionamento|de contingência|de gerenciamento costeiro|de emergência)|área de preservação|zona costeira|zoneamento ecológico|biodiversidade|conservação da natureza|risco ambiental|laudo técnico das condições ambientais|licença (?:ambiental|de pesquisa))\b/i },

  /* Contracts / commercial / fiscal */
  { cat: 'contract', re: /\b(contrato|contract|partilha de produção|production sharing|concessão|concession|lease|arrendamento|build,? (?:lease|own|operate|transfer|finance)|design,? build|construção,? (?:arrendamento|posse|operação|transferência|treinamento)|acordo|agreement|operating agreement|tax|imposto|tarifa|tariff|royalty|royalties|fee|aprovação de gastos|approval for expenditure|autorização de dispêndio|investimento|investment fund|cost,? (?:and|insurance|freight)|free on board|ex works|free of particular|memorando de entendimento|memorandum of understanding|take or pay|joint industry|joint operating|preço (?:contratual|de revenda|de produção)|preços independentes|empreitada|lump sum|turn key|repetro|cofins|icms|ipi|iss|capital expenditure|operating expenditure|life cycle cost|net present value|valor presente líquido|return on investment|retorno sobre o investimento|debt service|coverage ratio|special remuneratory|benefício remuneratório|government take|participações especiais|special purpose|propósito específico|petroleum revenue tax|imposto sobre|special customs|aduaneiro)\b/i },

  /* Equipment (físico) */
  { cat: 'equipment', re: /\b(válvula|valve|bomba|pump|pumping unit|árvore (?:de natal|submarina|de fluxo)|christmas tree|wet (?:christmas)? ?tree|riser|manifold|manifolde|hub|mandril|sonda|rig|jack ?up|navio|vessel|embarcação|drillship|drill ?ship|plataforma|platform|tubulação|piping|tubo (?:de perfuração|de produção|spool)|broca|bit|coluna (?:de perfuração|de produção|de injeção)|drill string|drill stem|drill collar|drillpipe|preventor|preventer|blowout|obturador|packer|estabilizador|stabilizer|compensador|compensator|umbilical|wellhead|cabeça (?:do revestimento|do poço|de poço)|gaveta|ram|annulus|anular|veículo|vehicle|rov|auv|esp(?!\b)|electrical submersible|bottom-?hole assembly|pipe ram|safety valve|tubing hanger|suspensor de coluna|adapter base|guide base|base (?:guia|adaptadora)|pipeline end|inteceptor|interceptor|wear bushing|kelly|bushing|junk basket|cesta|tanque|tank|caisson|tension leg|monocolumn|monocoluna|spar|fpso|floating production|filtro|cyclone|ciclone|separator|separador|cement bond|formation density|gamma ray (?:tool|log)|mud logging|mud lift|mudlift|measure while|logging while|coiled tubing|flexitubo|seabed)\b/i },

  /* Geophysics / well logging */
  { cat: 'geophysics', re: /\b(seismic|sísmica|sísmico|amplitude variation|bright spot|migration|moveout|reflection|reflexão|raio gama|gamma ray|sismograma|magnetometer|magnetômetro|geophysical|sub-?bottom|ground penetrating|low-?velocity zone|ocean bottom|electromagnetic method|electromagnetic propagation|induced polarization|spontaneous potential|formation density|formation analysis|cement bond log|casing collar|neutron log|propagation log|electric log|sonic|acoustic|imaging|tomography|tomografia|froude|reynolds|virtual geomagnetic|paleomagnetic|carbonate compensation|common (?:depth|mid|reflection) point|shot point|vertical seismic|perfil sísmico|perfilagem)\b/i },

  /* Process / operations (drilling, completion, production) */
  { cat: 'process', re: /\b(perfuração|drilling|completação|completion|workover|intervenção|restauro|produção|production|injeção|injection|estimulação|stimulation|fraturamento|fracturing|acidificação|acidizing|cimentação|cementing|perfilagem|logging|sísmica de aquisição|exploração|exploration|recuperação avançada|enhanced oil recovery|improved oil recovery|recuperação melhorada|recuperação microbiológica|microbial enhanced|comissionamento|commissioning|descomissionamento|decommissioning|bombeamento|elevação artificial|artificial lift|gas lift|gas-?lift|pumping|abandono|abandonment|tamponamento|plugging|canhoneio|perforation|teste de formação|drill stem test|teste de longa duração|teste de cedência|leak off test|step rate test|formation test|kick off|trip in|trip out|going in hole|pulling out|round trip|manobra|movimentação|moving in|nippling up|fishing|pesca|circulação|circulating|condicionamento|condition the mud|coring|testemunhando|drilling ahead|drilling deeper|drilled deeper|managed pressure|pressão controlada|dual-?gradient|simultaneous drilling|simultaneous production|jetting|injection)\b/i },

  /* Lithology */
  { cat: 'lithology', re: /\b(argillaceous|argiloso|carbonaceous|carbonáceo|calcareous|calcário|dolomitic|dolomítico|limestone|sandstone|arenito|shale|folhelho|xisto|conglomerate|conglomerado|granular|porous|poroso|argila|sand|areia|silt|clay|cuttings|cavings|aluimento|amostras de calha|core(?!\s+(?:business|skill))|testemunho|caroteiro|caroteador|grain|grão|sandstone|argila|matrix|matriz|fractured|fraturado|friable|friável|foraminifera|foraminíferos|micaceous|micáceo|microcrystalline|microcristalino|oolitic|oolítico|gypsum|gesso|gipsífero|consolidated|consolidado|laminated|laminado|crossbedded|estratificação cruzada|sorted|calibrado|loose|trace|vestígio|coarse|grosseiro|fine|fino|pebble|cascalho|boulder|pedregulho|brown|castanho|clear|hialino|transparente|barite|baritina|calcarenite|calcarenito|eocene|eoceno|round|redondo|sortida)\b/i },

  /* Fluid / hydrocarbon types */
  { cat: 'fluid', re: /\b(óleo|oil(?!\s+(?:and gas|company))|gás|gas(?!\s+(?:lift|injection|cut|carried))|água|water(?!\s+(?:depth|cut|cushion))|condensado|condensate|petróleo|petroleum|hidrocarboneto|hydrocarbon|metano|methane|biocombustível|biofuel|álcool|ethanol|diesel|gasolina|gasoline|gás natural|natural gas|liquefeito|liquefied|gás liquefeito|lpg|lng|gnl|glp|nitrogênio|nitrogen|metanol|methanol|monoetileno|asfalteno|parafina|wax|cera|emulsão|emulsion|fluido|fluid|lama|mud|drilling fluid|fluido de perfuração|salmoura|brine|spume|espuma|foam|salt water|água salgada|free water|água livre|formation gas|gás de formação|carbono orgânico|organic carbon)\b/i },

  /* Measurement / instrumental data types */
  { cat: 'measurement', re: /\b(profundidade|depth|pressão|pressure|temperatura|temperature|densidade|density|volume|fluxo|flow rate|vazão|gradient|gradiente|índice|index|fator|factor|razão|ratio|coeficiente|coefficient|porosity|porosidade|saturation|saturação|permeability|permeabilidade|condutividade|conductivity|resistividade|resistivity|tensão interfacial|interfacial tension|viscosidade|viscosity|hardness|dureza|fluorescence|fluorescência|composition|composição|alkalinity|alcalinidade|acid number|índice de acidez|base number|índice de basicidade|hydrogen index|índice de hidrogênio|gas-?oil ratio|oil-?water|water-?oil|ratio of|productivity index|injectivity index|absolute open flow|kick tolerance|hardness coefficient|brinell|rockwell|specific gravity|gravidade específica|nephelometric|turbidity|water depth|water cut|specific gravity|api gravity|reid vapor pressure|sample|amostra|analysis|análise|chromatography|cromatografia|petroleum revenue|reservoir pressure|hydrostatic pressure|atmospheric pressure|pressão atmosférica|crude oil)\b/i },

  /* Unit / dimensional */
  { cat: 'unit', re: /\b(barril|barrel|barris|barrels per|cubic feet|pés cúbicos|tonelagem|tonnage|gallons|galões|libras por|pounds per|psi|psia|psid|degree|grau|atmosfera|atmosphere|decibel|btu|million barrels|milhões de barris|equivalent|equivalente|standard cubic|padrão|cubic metres|metros cúbicos|tonelada equivalente|ton of oil|kilogram|kg|metro|liter|litro|cavalo-vapor|horsepower|gallon|saybolt|nephelometric|partes por milhão|parts per million|polegada quadrada|square inch|stock tank|condições de tanque|standard temperature|standard pressure|cnpt|ptn|sistema internacional de unidades)\b/i },

  /* Well state / status */
  { cat: 'well_state', re: /\b(wildcat|pioneiro|abandoned|abandonado|temporarily abandoned|temporariamente abandonado|plugged|tamponado|junked|seco|dry|active|ativo|injetor|injector|produtor|producer|exploratório|exploratory|delimitador|appraisal|comercial|commercial well|drilled deeper|aprofundado|plugged back|tamponado|kick(?:ed)? off|desviado|directional|direcional|completed|completado|suspenso|suspended|shut-?in|fechado|fechamento|extended reach|longo alcance|sidetrack|onshore|offshore|terra|mar|production well)\b/i },

  /* Default heading */
  { cat: 'organization', re: /\b(institute|instituto|forum|fórum|congress|company|empresa|associação|center|centro)\b/i },
];

function categorize(text) {
  for (const rule of CATEGORY_RULES) {
    if (rule.re.test(text)) return rule.cat;
  }
  return 'general';
}

/* ─────────────────────────────────────────────────────────────
 * Parser de linha
 * ───────────────────────────────────────────────────────────── */

const LINE_RE = /^([A-Za-zÀ-ÿ0-9/&,\-η()% ]+?)\.\s*(?:[–-]\s*)?(.+)$/;

function splitLastParen(s) {
  /* Captura o último bloco "(...)" como tradução, retornando { main, paren } */
  const m = s.match(/^(.*?)\s*\(([^()]+)\)\s*\.?\s*$/);
  if (!m) return { main: s.trim(), paren: null };
  return { main: m[1].trim(), paren: m[2].trim() };
}

function stripTrailingMeta(s) {
  /* Remove anotações tipo "(Port.)", "(Ang.)", "Brazil," — exige separador
     após o token (ponto, vírgula, fim) para não morder "Brazilian", "Brasília" etc. */
  return s.replace(/^(Port\.|Ang\.|Portugal|Brasil|Brazil|Angola)(?=[,;\s.\-)]|$)[,;\s.\-)]*/i, '').trim();
}

function parseLine(rawLine) {
  const line = rawLine.trim();
  if (!line) return null;
  const m = line.match(LINE_RE);
  if (!m) return null;
  const sigla = m[1].trim().split(',')[0].trim().toUpperCase();
  let body = m[2].trim();

  /* Hífen + sufixo descritivo (BO-BTM, CMC-MIC, FLH-HUB) é marcador de
     desambiguação de múltiplos sentidos para a mesma sigla. Sigla pública
     fica só com o prefixo, ID interno preserva o sufixo. */
  const hasDisambig = /^[A-Z0-9]+-[A-Z]{2,}$/.test(sigla);
  const canonicalSigla = hasDisambig ? sigla.split('-')[0] : sigla;

  /* Extrai (parte_alt) do final */
  const { main, paren } = splitLastParen(body);
  const altRaw = paren ? stripTrailingMeta(paren) : null;

  let pt, en;
  const mainIsPT = isPortuguese(main);
  if (altRaw) {
    const altIsPT = isPortuguese(altRaw);
    if (mainIsPT && !altIsPT) { pt = main; en = altRaw; }
    else if (!mainIsPT && altIsPT) { en = main; pt = altRaw; }
    else if (mainIsPT && altIsPT) { pt = main; en = altRaw; /* ambíguo, assume primário=PT */ }
    else { en = main; pt = altRaw; }
  } else {
    if (mainIsPT) { pt = main; en = null; }
    else { en = main; pt = null; }
  }

  return {
    sigla: canonicalSigla,
    sigla_raw: sigla,
    expansion_pt: pt,
    expansion_en: en,
    full_text: line,
  };
}

/* ─────────────────────────────────────────────────────────────
 * Pipeline
 * ───────────────────────────────────────────────────────────── */

const raw = fs.readFileSync(SRC, 'utf8');
const lines = raw.split('\n').filter((l) => l.trim());

const seen = new Map(); /* sigla → entry */
const failed = [];

for (const line of lines) {
  const parsed = parseLine(line);
  if (!parsed) { failed.push(line); continue; }

  const cat = categorize(`${parsed.expansion_pt || ''} ${parsed.expansion_en || ''}`);

  /* ID único usa sigla_raw (preserva sufixos de desambiguação).
     Sigla pública é canônica (sem sufixo). */
  const id = parsed.sigla_raw.toLowerCase().replace(/[^a-z0-9]/g, '_');
  const entry = {
    id,
    sigla: parsed.sigla,
    expansion_pt: parsed.expansion_pt,
    expansion_en: parsed.expansion_en,
    category: cat,
    it_generic: cat === 'it_generic',
  };

  if (seen.has(id)) {
    const prev = seen.get(id);
    if (!prev.expansion_pt && entry.expansion_pt) prev.expansion_pt = entry.expansion_pt;
    if (!prev.expansion_en && entry.expansion_en) prev.expansion_en = entry.expansion_en;
    continue;
  }
  seen.set(id, entry);
}

const acronyms = Array.from(seen.values()).sort((a, b) => a.sigla.localeCompare(b.sigla));

/* Stats */
const byCat = {};
for (const a of acronyms) byCat[a.category] = (byCat[a.category] || 0) + 1;

const out = {
  meta: {
    version: '1.0.0',
    generated: new Date().toISOString(),
    source: 'Siglário comunitário O&G (PT/EN) — comunidade técnica brasileira',
    total: acronyms.length,
    by_category: byCat,
    parse_failures: failed.length,
  },
  acronyms,
};

fs.writeFileSync(OUT, JSON.stringify(out, null, 2) + '\n', 'utf8');
console.log(`✓ data/acronyms.json — ${acronyms.length} siglas únicas`);
console.log(`  Por categoria:`);
for (const [c, n] of Object.entries(byCat).sort((a, b) => b[1] - a[1])) {
  console.log(`    ${c.padEnd(18)} ${n}`);
}
if (failed.length) {
  console.log(`  Linhas não parseadas: ${failed.length}`);
  failed.slice(0, 5).forEach((l) => console.log(`    ⚠ ${l.slice(0, 80)}`));
}
