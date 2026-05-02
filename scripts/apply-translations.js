#!/usr/bin/env node
/**
 * apply-translations.js — Aplica traduções PT/ES dos CSVs para JSON + TTL.
 *
 * Reads:
 *   data/glosis/translations/{lithology,petrography}.{pt,es}.csv
 *   data/glosis/lithology.json
 *   data/glosis/petrography-codelists.json
 *
 * Writes:
 *   data/glosis/lithology.json (prefLabel migra de string para {en,pt,es})
 *   data/glosis/petrography-codelists.json (idem)
 *   data/glosis/geolytics-glosis-ext.ttl (append @pt @es prefLabels for litho)
 *   data/glosis/geolytics-petrography-i18n.ttl (new — labels for 166 petro)
 *
 * Validation:
 *   - falha se algum row tiver `reviewed` vazio
 *   - falha se algum row tiver source='auto:cognate' (não promovido)
 *
 * Backward compat:
 *   - prefLabel preserved as prefLabel.en
 *   - prefLabel_legacy adicionado com a string original
 *
 * Usage: node scripts/apply-translations.js
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const TR_DIR = path.join(ROOT, 'data/glosis/translations');

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

function loadCsv(filename) {
  const text = fs.readFileSync(path.join(TR_DIR, filename), 'utf8');
  const lines = text.split('\n').filter(l => l.length > 0);
  const header = parseCsvLine(lines.shift());
  const rows = lines.map(line => {
    const cells = parseCsvLine(line);
    return Object.fromEntries(header.map((h, i) => [h, cells[i] || '']));
  });
  return rows;
}

function validateRows(rows, filename) {
  const errs = [];
  for (const r of rows) {
    if (!r.reviewed || r.reviewed.trim() === '') {
      errs.push(`${filename}: ${r.id} — reviewed is empty`);
    }
    if (r.source === 'auto:cognate') {
      errs.push(`${filename}: ${r.id} — source='auto:cognate' (not promoted to reviewed)`);
    }
  }
  return errs;
}

// ── Load all 4 CSVs ──────────────────────────────────────────────────────────
const lithoPt = loadCsv('lithology.pt.csv');
const lithoEs = loadCsv('lithology.es.csv');
const petroPt = loadCsv('petrography.pt.csv');
const petroEs = loadCsv('petrography.es.csv');

const allErrs = [
  ...validateRows(lithoPt, 'lithology.pt'),
  ...validateRows(lithoEs, 'lithology.es'),
  ...validateRows(petroPt, 'petrography.pt'),
  ...validateRows(petroEs, 'petrography.es')
];
if (allErrs.length) {
  console.error(`FAIL — ${allErrs.length} translation issue(s):`);
  allErrs.slice(0, 20).forEach(e => console.error('  ' + e));
  process.exit(1);
}
console.log(`Loaded ${lithoPt.length + lithoEs.length + petroPt.length + petroEs.length} translation rows — all validated.`);

// Build id → translation lookup
const tr = {};   // tr[id] = { en, pt, es }
for (const r of lithoPt) {
  tr[r.id] = tr[r.id] || { en: r.en };
  tr[r.id].pt = r.reviewed;
}
for (const r of lithoEs) {
  tr[r.id] = tr[r.id] || { en: r.en };
  tr[r.id].es = r.reviewed;
}
for (const r of petroPt) {
  tr[r.id] = tr[r.id] || { en: r.en };
  tr[r.id].pt = r.reviewed;
}
for (const r of petroEs) {
  tr[r.id] = tr[r.id] || { en: r.en };
  tr[r.id].es = r.reviewed;
}

// ── Patch lithology.json ─────────────────────────────────────────────────────
const lithoPath = path.join(ROOT, 'data/glosis/lithology.json');
const lithoDoc = JSON.parse(fs.readFileSync(lithoPath, 'utf8'));
let lithoPatched = 0;
for (const [id, c] of Object.entries(lithoDoc.data)) {
  if (!tr[id]) continue;
  if (typeof c.prefLabel === 'string') {
    c.prefLabel_legacy = c.prefLabel;
    c.prefLabel = { en: tr[id].en, pt: tr[id].pt, es: tr[id].es };
    lithoPatched++;
  } else if (typeof c.prefLabel === 'object' && c.prefLabel) {
    c.prefLabel.pt = tr[id].pt;
    c.prefLabel.es = tr[id].es;
    lithoPatched++;
  }
}
lithoDoc.meta = lithoDoc.meta || {};
lithoDoc.meta.languages = ['en', 'pt', 'es'];
lithoDoc.meta.translations_applied_at = new Date().toISOString();
fs.writeFileSync(lithoPath, JSON.stringify(lithoDoc, null, 2));
console.log(`lithology.json: patched ${lithoPatched} concepts with PT/ES labels`);

// ── Patch petrography-codelists.json ─────────────────────────────────────────
const petroPath = path.join(ROOT, 'data/glosis/petrography-codelists.json');
const petroDoc = JSON.parse(fs.readFileSync(petroPath, 'utf8'));
let petroPatched = 0;
for (const [scheme, info] of Object.entries(petroDoc.data)) {
  for (const c of info.concepts) {
    if (!tr[c.id]) continue;
    if (typeof c.prefLabel === 'string') {
      c.prefLabel_legacy = c.prefLabel;
      c.prefLabel = { en: tr[c.id].en, pt: tr[c.id].pt, es: tr[c.id].es };
      petroPatched++;
    } else if (typeof c.prefLabel === 'object' && c.prefLabel) {
      c.prefLabel.pt = tr[c.id].pt;
      c.prefLabel.es = tr[c.id].es;
      petroPatched++;
    }
  }
}
petroDoc.meta = petroDoc.meta || {};
petroDoc.meta.languages = ['en', 'pt', 'es'];
petroDoc.meta.translations_applied_at = new Date().toISOString();
fs.writeFileSync(petroPath, JSON.stringify(petroDoc, null, 2));
console.log(`petrography-codelists.json: patched ${petroPatched} concepts with PT/ES labels`);

// ── Emit i18n TTL — petrography ─────────────────────────────────────────────
function escTtl(s) { return s.replace(/\\/g, '\\\\').replace(/"/g, '\\"'); }

const petroTtlLines = [
  '# ============================================================================',
  '# Geolytics petrography i18n — PT/ES SKOS prefLabels',
  '# ============================================================================',
  '# Generated: ' + new Date().toISOString(),
  '# Source: data/glosis/translations/petrography.{pt,es}.csv',
  '# Sources cited: CPRM 2018, ABNT NBR 6502, IGME Diccionario, Schlumberger',
  '# Pattern: <glosis_cl:concept-IRI>  skos:prefLabel "term"@pt, "term"@es',
  '# ============================================================================',
  '',
  '@prefix glosis_cl: <http://w3id.org/glosis/model/codelists/> .',
  '@prefix skos:      <http://www.w3.org/2004/02/skos/core#> .',
  '@prefix owl:       <http://www.w3.org/2002/07/owl#> .',
  '@prefix dct:       <http://purl.org/dc/terms/> .',
  '',
  '<https://geolytics.petrobras.com.br/dict/petrography-i18n>',
  '    a              owl:Ontology ;',
  '    owl:versionInfo "1.0.0" ;',
  '    dct:title "GLOSIS petrography i18n labels (PT/ES)"@en ;',
  '    dct:description "PT/ES SKOS prefLabels for 166 GLOSIS petrography concepts."@en .',
  ''
];

let petroTtlCount = 0;
for (const [scheme, info] of Object.entries(petroDoc.data)) {
  for (const c of info.concepts) {
    if (!tr[c.id]) continue;
    petroTtlLines.push(`glosis_cl:${c.id}`);
    petroTtlLines.push(`    skos:prefLabel "${escTtl(tr[c.id].pt)}"@pt , "${escTtl(tr[c.id].es)}"@es .`);
    petroTtlLines.push('');
    petroTtlCount++;
  }
}
petroTtlLines.push('# === EOF ===', '');
const petroTtlPath = path.join(ROOT, 'data/glosis/geolytics-petrography-i18n.ttl');
fs.writeFileSync(petroTtlPath, petroTtlLines.join('\n'));
console.log(`geolytics-petrography-i18n.ttl: ${petroTtlCount} concepts × 2 lang = ${petroTtlCount*2} prefLabel triples`);

// ── Append i18n labels to geolytics-glosis-ext.ttl ──────────────────────────
const extPath = path.join(ROOT, 'data/glosis/geolytics-glosis-ext.ttl');
let extTtl = fs.readFileSync(extPath, 'utf8');

const i18nMarker = '# 8. Lithology i18n labels (PT/ES)';
if (!extTtl.includes(i18nMarker)) {
  // Strip trailing # === EOF === if present
  extTtl = extTtl.replace(/# === EOF ===\s*$/, '').trimEnd() + '\n\n';
  const i18nBlock = [
    '# ============================================================================',
    '# 8. Lithology i18n labels (PT/ES)',
    '# ============================================================================',
    '# Source: data/glosis/translations/lithology.{pt,es}.csv',
    '# 88 GLOSIS lithology concepts × 2 languages = 176 prefLabel triples',
    '#',
    ''
  ];
  let lithoTtlCount = 0;
  for (const [id, c] of Object.entries(lithoDoc.data)) {
    if (!tr[id]) continue;
    i18nBlock.push(`glosis_cl:${id}`);
    i18nBlock.push(`    skos:prefLabel "${escTtl(tr[id].pt)}"@pt , "${escTtl(tr[id].es)}"@es .`);
    i18nBlock.push('');
    lithoTtlCount++;
  }
  i18nBlock.push('# === EOF ===', '');
  fs.writeFileSync(extPath, extTtl + i18nBlock.join('\n'));
  console.log(`geolytics-glosis-ext.ttl: appended ${lithoTtlCount} concepts × 2 = ${lithoTtlCount*2} prefLabel triples`);
} else {
  console.log('geolytics-glosis-ext.ttl: i18n block already present — skipping');
}

console.log('\nApplied successfully. Run python3 scripts/validate.py --self-check to verify.');
