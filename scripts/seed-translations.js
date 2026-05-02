#!/usr/bin/env node
/**
 * seed-translations.js — Popula CSVs de tradução PT/ES para conceitos GLOSIS.
 *
 * Lê:
 *   data/glosis/lithology.json (88 conceitos)
 *   data/glosis/petrography-codelists.json (22 codelists, 166 conceitos)
 *
 * Emite:
 *   data/glosis/translations/lithology.pt.csv
 *   data/glosis/translations/lithology.es.csv
 *   data/glosis/translations/petrography.pt.csv
 *   data/glosis/translations/petrography.es.csv
 *
 * Estratégia:
 *   1. Tabela curada de cognatos (CGNT) cobre os termos mais óbvios.
 *   2. Heurísticas de sufixo cobrem termos morfologicamente regulares
 *      (-ic→-ico, -ous→-oso, -ation→-ação/-ación, etc.).
 *   3. Termos não cobertos ficam com `suggestion=""` e flag `auto-needed`.
 *
 * Idempotência: se o CSV já existir, preserva linhas com `reviewed`
 * preenchido; reseed só linhas vazias.
 *
 * Uso: node scripts/seed-translations.js
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

// ── Curated cognates ─────────────────────────────────────────────────────────
// Format: [en_lower, pt, es]   (lowercase EN key for lookup)
// Sources: CPRM 2018, ABNT NBR 6502, IGME, Schlumberger Glossary.
const CGNT = new Map([
  // Igneous rocks
  ['igneous rock', ['rocha ígnea', 'roca ígnea']],
  ['acid igneous', ['ígnea ácida', 'ígnea ácida']],
  ['acidic igneous rock', ['rocha ígnea ácida', 'roca ígnea ácida']],
  ['basic igneous', ['ígnea básica', 'ígnea básica']],
  ['basic igneous rock', ['rocha ígnea básica', 'roca ígnea básica']],
  ['intermediate igneous', ['ígnea intermediária', 'ígnea intermedia']],
  ['ultrabasic igneous', ['ígnea ultrabásica', 'ígnea ultrabásica']],
  ['diorite', ['diorito', 'diorita']],
  ['grano-diorite', ['granodiorito', 'granodiorita']],
  ['quartz-diorite', ['quartzo-diorito', 'cuarzodiorita']],
  ['rhyolite', ['riolito', 'riolita']],
  ['gabbro', ['gabro', 'gabro']],
  ['basalt', ['basalto', 'basalto']],
  ['dolerite', ['dolerito', 'dolerita']],
  ['andesite, trachyte, phonolite', ['andesito, traquito, fonolito', 'andesita, traquita, fonolita']],
  ['diorite-syenite', ['diorito-sienito', 'diorita-sienita']],
  ['pyroclastic', ['piroclástico', 'piroclástico']],
  ['tuff, tuffite', ['tufo, tufito', 'toba, tobita']],
  ['volcanic scoria/breccia', ['escória/brecha vulcânica', 'escoria/brecha volcánica']],
  ['volcanic ash', ['cinza vulcânica', 'ceniza volcánica']],
  ['ignimbrite', ['ignimbrito', 'ignimbrita']],
  ['peridotite', ['peridotito', 'peridotita']],
  ['pyroxenite', ['piroxenito', 'piroxenita']],
  ['ilmenite, magnetite, ironstone, serpentine', ['ilmenita, magnetita, ironstone, serpentina', 'ilmenita, magnetita, ironstone, serpentina']],
  // Metamorphic
  ['metamorphic rock', ['rocha metamórfica', 'roca metamórfica']],
  ['acid metamorphic', ['metamórfica ácida', 'metamórfica ácida']],
  ['basic metamorphic', ['metamórfica básica', 'metamórfica básica']],
  ['ultrabasic metamorphic', ['metamórfica ultrabásica', 'metamórfica ultrabásica']],
  ['quartzite', ['quartzito', 'cuarcita']],
  ['gneiss, migmatite', ['gnaisse, migmatito', 'gneis, migmatita']],
  ['slate, phyllite (pelitic rocks)', ['ardósia, filito (rochas pelíticas)', 'pizarra, filita (rocas pelíticas)']],
  ['schist', ['xisto', 'esquisto']],
  ['(green)schist', ['xisto verde', 'esquisto verde']],
  ['gneiss rich in fe–mg minerals', ['gnaisse rico em minerais Fe–Mg', 'gneis rico en minerales Fe–Mg']],
  ['metamorphic limestone (marble)', ['mármore (calcário metamórfico)', 'mármol (caliza metamórfica)']],
  ['amphibolite', ['anfibolito', 'anfibolita']],
  ['eclogite', ['eclogito', 'eclogita']],
  ['serpentinite, greenstone', ['serpentinito, rocha verde', 'serpentinita, roca verde']],
  // Sedimentary consolidated
  ['sedimentary rock (consolidated)', ['rocha sedimentar (consolidada)', 'roca sedimentaria (consolidada)']],
  ['clastic sediments', ['sedimentos clásticos', 'sedimentos clásticos']],
  ['conglomerate, breccia', ['conglomerado, brecha', 'conglomerado, brecha']],
  ['sandstone, greywacke, arkose', ['arenito, grauvaca, arcósio', 'arenisca, grauvaca, arcosa']],
  ['silt-, mud-, claystone', ['siltito, lamito, argilito', 'limolita, lutita, arcillita']],
  ['shale', ['folhelho', 'lutita']],
  ['ironstone', ['ironstone (ferruginoso)', 'roca ferruginosa']],
  ['evaporites', ['evaporitos', 'evaporitas']],
  ['anhydrite, gypsum', ['anidrita, gipsita', 'anhidrita, yeso']],
  ['halite', ['halita', 'halita']],
  ['carbonatic, organic', ['carbonática, orgânica', 'carbonática, orgánica']],
  ['limestone, other carbonate rock', ['calcário, outras carbonáticas', 'caliza, otras carbonatadas']],
  ['marl and other mixtures', ['marga e outras misturas', 'marga y otras mezclas']],
  ['coals, bitumen and related rocks', ['carvões, betume e correlatas', 'carbones, betún y rocas afines']],
  // Unconsolidated
  ['sedimentary rock (unconsolidated)', ['sedimento (não consolidado)', 'sedimento (no consolidado)']],
  ['anthropogenic/technogenic', ['antropogênico/tecnogênico', 'antropogénico/tecnogénico']],
  ['redeposited natural material', ['material natural redepositado', 'material natural redepositado']],
  ['industrial/artisanal deposits', ['depósitos industriais/artesanais', 'depósitos industriales/artesanales']],
  ['colluvial', ['coluvial', 'coluvial']],
  ['slope deposits', ['depósitos de encosta', 'depósitos de ladera']],
  ['lahar', ['lahar', 'lahar']],
  ['eolian', ['eólico', 'eólico']],
  ['loess', ['loess', 'loess']],
  ['fluvial', ['fluvial', 'fluvial']],
  ['sand and gravel', ['areia e cascalho', 'arena y grava']],
  ['clay, silt and loam', ['argila, silte e franco', 'arcilla, limo y franco']],
  ['glacial', ['glacial', 'glacial']],
  ['moraine', ['morena', 'morrena']],
  ['ug2 glacio-fluvial sand', ['areia glácio-fluvial', 'arena glaciofluvial']],
  ['ug3 glacio-fluvial gravel', ['cascalho glácio-fluvial', 'grava glaciofluvial']],
  ['kryogenic', ['criogênico', 'criogénico']],
  ['periglacial rock debris', ['detritos rochosos periglaciais', 'detritos rocosos periglaciares']],
  ['periglacial solifluction layer', ['camada de solifluxão periglacial', 'capa de solifluxión periglaciar']],
  ['lacustrine', ['lacustre', 'lacustre']],
  ['sand', ['areia', 'arena']],
  ['silt and clay', ['silte e argila', 'limo y arcilla']],
  ['marine, estuarine', ['marinho, estuarino', 'marino, estuarino']],
  ['clay and silt', ['argila e silte', 'arcilla y limo']],
  ['organic', ['orgânico', 'orgánico']],
  ['rainwater-fed moor peat', ['turfa de pântano alimentada por chuva', 'turba de páramo alimentada por lluvia']],
  ['groundwater-fed bog peat', ['turfa de brejo alimentada por aquífero', 'turba de ciénaga alimentada por acuífero']],
  ['weathered residuum', ['resíduo de intemperismo', 'residuo de meteorización']],
  ['bauxite, laterite', ['bauxita, laterita', 'bauxita, laterita']],
  ['unspecified deposits', ['depósitos não especificados', 'depósitos no especificados']],
  ['clay', ['argila', 'arcilla']],
  ['loam and silt', ['franco e silte', 'franco y limo']],
  ['gravelly sand', ['areia com cascalho', 'arena con grava']],
  ['gravel, broken rock', ['cascalho, fragmentos de rocha', 'grava, fragmentos de roca']],
  ['gravel', ['cascalho', 'grava']],

  // Petrography — cementation
  ['cemented', ['cimentado', 'cementado']],
  ['indurated', ['endurecido', 'endurecido']],
  ['moderately cemented', ['moderadamente cimentado', 'moderadamente cementado']],
  ['non-cemented and non-compacted', ['não cimentado e não compactado', 'no cementado y no compactado']],
  ['weakly cemented', ['fracamente cimentado', 'débilmente cementado']],
  ['compacted but non-cemented', ['compactado mas não cimentado', 'compactado pero no cementado']],
  ['nodular', ['nodular', 'nodular']],
  ['pisolithic', ['pisolítico', 'pisolítico']],
  ['platy', ['placoso', 'laminar']],
  ['vesicular', ['vesicular', 'vesicular']],
  ['iron', ['ferro', 'hierro']],
  ['iron–manganese (sesquioxides)', ['ferro–manganês (sesquióxidos)', 'hierro–manganeso (sesquióxidos)']],
  ['iron–organic matter', ['ferro–matéria orgânica', 'hierro–materia orgánica']],
  ['clay–sesquioxides', ['argila–sesquióxidos', 'arcilla–sesquióxidos']],
  // Weathering
  ['fresh or slightly weathered', ['fresco ou levemente intemperizado', 'fresco o ligeramente meteorizado']],
  ['strongly weathered', ['fortemente intemperizado', 'fuertemente meteorizado']],
  ['weathered', ['intemperizado', 'meteorizado']],
  // Porosity
  ['very low', ['muito baixa', 'muy baja']],
  ['low', ['baixa', 'baja']],
  ['medium', ['média', 'media']],
  ['high', ['alta', 'alta']],
  ['very high', ['muito alta', 'muy alta']],
  // Structure
  ['weak', ['fraca', 'débil']],
  ['weak to moderate', ['fraca a moderada', 'débil a moderada']],
  ['moderate', ['moderada', 'moderada']],
  ['moderate to strong', ['moderada a forte', 'moderada a fuerte']],
  ['strong', ['forte', 'fuerte']],
  ['fine/thin', ['fina', 'fina']],
  ['very fine/thin', ['muito fina', 'muy fina']],
  ['coarse/thick', ['grossa', 'gruesa']],
  ['very coarse/thick', ['muito grossa', 'muy gruesa']],
  ['extremely coarse', ['extremamente grossa', 'extremadamente gruesa']],
  // Plasticity & stickiness
  ['non-plastic', ['não plástica', 'no plástica']],
  ['slightly plastic', ['ligeiramente plástica', 'ligeramente plástica']],
  ['slightly plastic to plastic', ['ligeira a plástica', 'ligera a plástica']],
  ['plastic', ['plástica', 'plástica']],
  ['plastic to very plastic', ['plástica a muito plástica', 'plástica a muy plástica']],
  ['very plastic', ['muito plástica', 'muy plástica']],
  ['non-sticky', ['não pegajosa', 'no pegajosa']],
  ['slightly sticky', ['ligeiramente pegajosa', 'ligeramente pegajosa']],
  ['slightly sticky to sticky', ['ligeira a pegajosa', 'ligera a pegajosa']],
  ['sticky', ['pegajosa', 'pegajosa']],
  ['sticky to very sticky', ['pegajosa a muito pegajosa', 'pegajosa a muy pegajosa']],
  ['very sticky', ['muito pegajosa', 'muy pegajosa']],
  // Rock fragments
  ['angular', ['angular', 'angular']],
  ['flat', ['achatado', 'plano']],
  ['rounded', ['arredondado', 'redondeado']],
  ['subrounded', ['subarredondado', 'subredondeado']],
  ['boulders', ['matacões', 'bloques']],
  ['boulders and large boulders', ['matacões e blocos grandes', 'bloques y grandes bloques']],
  ['rock fragments', ['fragmentos de rocha', 'fragmentos de roca']],
  ['artefacts', ['artefatos', 'artefactos']],
  ['fine artefacts', ['artefatos finos', 'artefactos finos']],
  ['medium artefacts', ['artefatos médios', 'artefactos medios']],
  ['coarse artefacts', ['artefatos grossos', 'artefactos gruesos']],
  ['very fine artefacts', ['artefatos muito finos', 'artefactos muy finos']],
  ['combination of classes', ['combinação de classes', 'combinación de clases']],
  ['fine and medium gravel/artefacts', ['cascalho/artefatos finos e médios', 'grava/artefactos finos y medios']],
  ['medium and coarse gravel/artefacts', ['cascalho/artefatos médios e grossos', 'grava/artefactos medios y gruesos']],
  ['coarse gravel and stones', ['cascalho grosso e pedras', 'grava gruesa y piedras']],
  // Landforms
  ['level land', ['terreno plano', 'tierra llana']],
  ['depression', ['depressão', 'depresión']],
  ['plateau', ['planalto', 'meseta']],
  ['plain', ['planície', 'llanura']],
  ['valley floor', ['fundo de vale', 'fondo de valle']],
  ['sloping land', ['terreno inclinado', 'tierra inclinada']],
  ['medium-gradient escarpment zone', ['zona de escarpa de gradiente médio', 'zona de escarpe de gradiente medio']],
  ['medium-gradient hill', ['colina de gradiente médio', 'colina de gradiente medio']],
  ['medium-gradient mountain', ['montanha de gradiente médio', 'montaña de gradiente medio']],
  ['dissected plain', ['planície dissecada', 'llanura disectada']],
  // Cementation nature (additional)
  ['gypsum', ['gipsita', 'yeso']],
  ['ice', ['gelo', 'hielo']],
  ['carbonates', ['carbonatos', 'carbonatos']],
  ['carbonates–silica', ['carbonatos–sílica', 'carbonatos–sílice']],
  ['mechanical', ['mecânica', 'mecánica']],
  ['not known', ['desconhecida', 'desconocida']],
  ['ploughing', ['aração', 'arado']],
  ['silica', ['sílica', 'sílice']],
  ['broken', ['quebrada', 'rota']],
  ['continuous', ['contínua', 'continua']],
  ['discontinuous', ['descontínua', 'discontinua']],
  // Fragment sizes
  ['coarse gravel', ['cascalho grosso', 'grava gruesa']],
  ['fine gravel', ['cascalho fino', 'grava fina']],
  ['medium gravel', ['cascalho médio', 'grava media']],
  ['large boulders', ['blocos grandes', 'bloques grandes']],
  ['stones', ['pedras', 'piedras']],
  ['stones and boulders', ['pedras e matacões', 'piedras y bloques']],
  ['stone line', ['linha de pedras', 'línea de piedras']],
  // Abundance
  ['abundant', ['abundante', 'abundante']],
  ['common', ['comum', 'común']],
  ['dominant', ['dominante', 'dominante']],
  ['few', ['poucos', 'pocos']],
  ['many', ['muitos', 'muchos']],
  ['none', ['nenhum', 'ninguno']],
  ['very few', ['muito poucos', 'muy pocos']],
  // Dry consistence
  ['extremely hard', ['extremamente duro', 'extremadamente duro']],
  ['hard', ['duro', 'duro']],
  ['hard to very hard', ['duro a muito duro', 'duro a muy duro']],
  ['loose', ['solto', 'suelto']],
  ['slightly hard', ['ligeiramente duro', 'ligeramente duro']],
  ['slightly hard to hard', ['ligeiramente duro a duro', 'ligeramente duro a duro']],
  ['soft', ['macio', 'blando']],
  ['soft to slightly hard', ['macio a ligeiramente duro', 'blando a ligeramente duro']],
  ['very hard', ['muito duro', 'muy duro']],
  // Moist consistence
  ['extremely firm', ['extremamente firme', 'extremadamente firme']],
  ['firm', ['firme', 'firme']],
  ['friable', ['friável', 'friable']],
  ['very firm', ['muito firme', 'muy firme']],
  ['very friable', ['muito friável', 'muy friable']],
  // Fragments classes (volumetric/gravimetric — abstract identifiers, keep EN as fallback)
  ['fragmentsgravimetricfraction01', ['fração gravimétrica 01', 'fracción gravimétrica 01']],
  ['fragmentsgravimetricfraction02', ['fração gravimétrica 02', 'fracción gravimétrica 02']],
  ['fragmentsgravimetricfraction03', ['fração gravimétrica 03', 'fracción gravimétrica 03']],
  ['fragmentsgravimetricfraction04', ['fração gravimétrica 04', 'fracción gravimétrica 04']],
  ['fragmentsgravimetrictotal', ['fração gravimétrica total', 'fracción gravimétrica total']],
  ['fragmentsvolumetric01', ['fração volumétrica 01', 'fracción volumétrica 01']],
  ['fragmentsvolumetric02', ['fração volumétrica 02', 'fracción volumétrica 02']],
  ['fragmentsvolumetric03', ['fração volumétrica 03', 'fracción volumétrica 03']],
  ['fragmentsvolumetricestimate', ['estimativa volumétrica de fragmentos', 'estimación volumétrica de fragmentos']],
  ['fragmentsvolumetrictotal', ['fração volumétrica total', 'fracción volumétrica total']],
  // Landforms (additional)
  ['medium-gradient valley', ['vale de gradiente médio', 'valle de gradiente medio']],
  ['steep land', ['terreno íngreme', 'tierra escarpada']],
  ['high-gradient escarpment zone', ['zona de escarpa de gradiente alto', 'zona de escarpe de gradiente alto']],
  ['high-gradient hill', ['colina de gradiente alto', 'colina de gradiente alto']],
  ['high-gradient mountain', ['montanha de gradiente alto', 'montaña de gradiente alto']],
  ['high-gradient valley', ['vale de gradiente alto', 'valle de gradiente alto']],
  // Slope position
  ['bottom (drainage line)', ['fundo (linha de drenagem)', 'fondo (línea de drenaje)']],
  ['bottom (flat)', ['fundo (plano)', 'fondo (plano)']],
  ['crest (summit)', ['crista (cume)', 'cresta (cumbre)']],
  ['higher part (rise)', ['parte alta (elevação)', 'parte alta (elevación)']],
  ['intermediate part (talf)', ['parte intermediária (talvegue)', 'parte intermedia (talvegue)']],
  ['lower part (and dip)', ['parte baixa (e mergulho)', 'parte baja (y buzamiento)']],
  ['lower slope (foot slope)', ['baixa encosta (sopé)', 'ladera baja (pie de ladera)']],
  ['middle slope (back slope)', ['meia encosta', 'ladera media']],
  ['toe slope', ['sopé', 'pie de ladera']],
  ['upper slope (shoulder)', ['alta encosta (ombro)', 'ladera alta (hombro)']],
  // Slope form
  ['concave', ['côncava', 'cóncava']],
  ['straight', ['retilínea', 'recta']],
  ['terraced', ['em terraços', 'aterrazada']],
  ['convex', ['convexa', 'convexa']],
  ['complex (irregular)', ['complexa (irregular)', 'compleja (irregular)']],
  // Slope gradient classes
  ['very steep', ['muito íngreme', 'muy escarpada']],
  ['level', ['plano', 'llano']],
  ['nearly level', ['quase plano', 'casi llano']],
  ['very gently sloping', ['muito suavemente inclinado', 'muy suavemente inclinada']],
  ['gently sloping', ['suavemente inclinado', 'suavemente inclinada']],
  ['sloping', ['inclinado', 'inclinada']],
  ['strongly sloping', ['fortemente inclinado', 'fuertemente inclinada']],
  ['moderately steep', ['moderadamente íngreme', 'moderadamente escarpada']],
  ['steep', ['íngreme', 'escarpada']]
]);

function lookup(en) {
  return CGNT.get(en.toLowerCase()) || null;
}

// ── Heuristic suffix transforms ──────────────────────────────────────────────
// Apply ONLY when curated lookup misses. Conservative — must be reversible
// and well-formed in both languages.
function heuristic(en) {
  const l = en.toLowerCase().trim();
  if (!l) return null;
  // Single-word suffix rules
  // -ation → -ação / -ación   (e.g., cementation, formation)
  if (/\b\w+ation\b/.test(l)) {
    const pt = l.replace(/(\w+)ation\b/g, '$1ação');
    const es = l.replace(/(\w+)ation\b/g, '$1ación');
    return [pt, es];
  }
  // -ity → -idade / -idad   (e.g., porosity, viscosity)
  if (/\b\w+ity\b/.test(l)) {
    const pt = l.replace(/(\w+)ity\b/g, '$1idade');
    const es = l.replace(/(\w+)ity\b/g, '$1idad');
    return [pt, es];
  }
  return null;
}

// ── CSV utilities ────────────────────────────────────────────────────────────
function escapeCsv(s) {
  if (s == null) return '';
  const v = String(s);
  if (/[",\n]/.test(v)) return `"${v.replace(/"/g, '""')}"`;
  return v;
}

function readExistingCsv(filepath) {
  // Returns Map<id, row> for rows that already have `reviewed` populated.
  if (!fs.existsSync(filepath)) return new Map();
  const text = fs.readFileSync(filepath, 'utf8');
  const lines = text.split('\n').filter(Boolean);
  const header = lines.shift().split(',');
  const out = new Map();
  for (const line of lines) {
    // Robust split — naive but works since we don't put commas in source IDs.
    const cells = parseCsvLine(line);
    const row = Object.fromEntries(header.map((h, i) => [h, cells[i] || '']));
    if (row.id && row.reviewed && row.reviewed.trim() !== '') {
      out.set(row.id, row);
    }
  }
  return out;
}

function parseCsvLine(line) {
  const cells = [];
  let cur = '', inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inQ) {
      if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') { inQ = false; }
      else cur += c;
    } else {
      if (c === ',') { cells.push(cur); cur = ''; }
      else if (c === '"' && cur === '') { inQ = true; }
      else cur += c;
    }
  }
  cells.push(cur);
  return cells;
}

function writeCsv(filepath, rows) {
  const header = ['id', 'en', 'suggestion', 'reviewed', 'source', 'reviewer', 'notes'];
  const lines = [header.join(',')];
  for (const r of rows) {
    lines.push(header.map(h => escapeCsv(r[h] || '')).join(','));
  }
  fs.writeFileSync(filepath, lines.join('\n') + '\n');
}

// ── Main seeding ─────────────────────────────────────────────────────────────
function seedLanguage(concepts, lang, outpath) {
  const langIdx = lang === 'pt' ? 0 : 1;
  const existing = readExistingCsv(outpath);
  const rows = [];
  let curated = 0, heuristics = 0, blank = 0;

  for (const c of concepts) {
    const en = c.prefLabel || c.label_en || '';
    if (!en) continue;
    const id = c.id;

    // Preserve manual reviews
    if (existing.has(id)) {
      rows.push(existing.get(id));
      continue;
    }

    let suggestion = '';
    let source = '';
    const cog = lookup(en);
    if (cog) {
      suggestion = cog[langIdx];
      source = 'auto:cognate';
      curated++;
    } else {
      const h = heuristic(en);
      if (h) {
        suggestion = h[langIdx];
        source = 'auto:heuristic';
        heuristics++;
      } else {
        blank++;
      }
    }
    rows.push({
      id, en,
      suggestion,
      reviewed: '',
      source,
      reviewer: '',
      notes: ''
    });
  }

  writeCsv(outpath, rows);
  return { total: rows.length, curated, heuristics, blank };
}

// ── Run ─────────────────────────────────────────────────────────────────────
function loadLithology() {
  const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/glosis/lithology.json'), 'utf8')).data;
  return Object.values(data).map(c => ({
    id: c.id,
    prefLabel: c.prefLabel
  }));
}

function loadPetrography() {
  const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/glosis/petrography-codelists.json'), 'utf8')).data;
  const out = [];
  for (const [scheme, info] of Object.entries(data)) {
    for (const c of info.concepts) {
      out.push({ id: c.id, prefLabel: c.prefLabel, scheme });
    }
  }
  return out;
}

const litho = loadLithology();
const petro = loadPetrography();

console.log(`Loaded ${litho.length} lithology concepts, ${petro.length} petrography concepts.`);

const outdir = path.join(ROOT, 'data/glosis/translations');
fs.mkdirSync(outdir, { recursive: true });

for (const [name, concepts] of [['lithology', litho], ['petrography', petro]]) {
  for (const lang of ['pt', 'es']) {
    const outpath = path.join(outdir, `${name}.${lang}.csv`);
    const stats = seedLanguage(concepts, lang, outpath);
    console.log(`  ${name}.${lang}.csv: ${stats.total} rows  curated=${stats.curated}  heuristic=${stats.heuristics}  blank=${stats.blank}`);
  }
}
console.log('\nReview CSVs and fill `reviewed` column. Then run apply-translations.js.');
