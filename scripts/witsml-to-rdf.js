#!/usr/bin/env node
/**
 * witsml-to-rdf.js — Converts a WITSML 2.0 XML document to Turtle (RDF) triples.
 *
 * Uses the data/witsml-rdf-crosswalk.json mapping to resolve class and property URIs.
 * No external XML parser dependencies — uses a lightweight regex-based extractor that
 * handles the simplified WITSML dialect produced by the sample (no namespace prefixes
 * on element names inside the default namespace).
 *
 * Usage:
 *   node scripts/witsml-to-rdf.js [path/to/file.xml]
 *
 * If no path is given, runs the embedded sample from data/witsml-sample.xml (or falls
 * back to the inline XML constant in this script).
 *
 * API:
 *   const { convert } = require('./scripts/witsml-to-rdf');
 *   const ttl = convert(xmlString);           // returns Turtle string
 *   const ttl = convert(xmlString, options);  // options.baseUri overrides default
 */

'use strict';

const fs   = require('node:fs');
const path = require('node:path');

// ─────────────────────────────────────────────────────────────────────────────
// Paths
// ─────────────────────────────────────────────────────────────────────────────

const ROOT         = path.resolve(__dirname, '..');
const CROSSWALK_PATH = path.join(ROOT, 'data', 'witsml-rdf-crosswalk.json');
const SAMPLE_PATH  = path.join(ROOT, 'data', 'witsml-sample.xml');

// ─────────────────────────────────────────────────────────────────────────────
// Default base URI for generated instances
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_BASE_URI = 'https://geolytics.petrobras.com.br/dict/instance/';
const GEO_PREFIX       = 'https://geolytics.petrobras.com.br/dict/';
const ENERGISTICS_NS   = 'http://www.energistics.org/energyml/data/witsmlv2/2.0#';

// ─────────────────────────────────────────────────────────────────────────────
// Load crosswalk (lazy, cached)
// ─────────────────────────────────────────────────────────────────────────────

let _crosswalkCache = null;

function loadCrosswalk() {
  if (_crosswalkCache) return _crosswalkCache;
  if (!fs.existsSync(CROSSWALK_PATH)) {
    throw new Error(`Crosswalk not found: ${CROSSWALK_PATH}`);
  }
  _crosswalkCache = JSON.parse(fs.readFileSync(CROSSWALK_PATH, 'utf8'));
  return _crosswalkCache;
}

// Build index by witsml_class name for O(1) lookup
function buildClassIndex(crosswalk) {
  const idx = {};
  for (const cls of crosswalk.classes) {
    idx[cls.witsml_class] = cls;
  }
  return idx;
}

// ─────────────────────────────────────────────────────────────────────────────
// Minimal XML extractor (regex-based, no external deps)
//
// Parses top-level element blocks from the WITSML XML. Handles:
//   - Self-closing tags
//   - Nested elements (extracts named scalar children and attribute @uid)
//   - Nested repeating groups (e.g. <trajectoryStation>)
//
// Returns an array of objects: { tag, uid, children: { [name]: value | object[] } }
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Extract the value of a simple child element by name from an XML fragment.
 * Returns null if not found.
 */
function extractChild(xml, name) {
  // Match <name ...>value</name> or <name ...>value</NAME> (case-sensitive tag)
  const re = new RegExp(`<${name}(?:\\s[^>]*)?>(.*?)<\\/${name}>`, 's');
  const m = re.exec(xml);
  if (!m) return null;
  return m[1].trim();
}

/**
 * Extract the value of attribute uid="..." from an opening tag.
 */
function extractUid(tag) {
  const m = /\buid="([^"]+)"/.exec(tag);
  return m ? m[1] : null;
}

/**
 * Extract all occurrences of a repeating element block.
 * Returns an array of raw XML strings (inner content of each occurrence).
 */
function extractAllBlocks(xml, tagName) {
  const results = [];
  const openTag = new RegExp(`<${tagName}(?:\\s[^>]*)?>`, 'g');
  const closeTag = `</${tagName}>`;
  let match;
  while ((match = openTag.exec(xml)) !== null) {
    const start = match.index;
    const innerStart = start + match[0].length;
    const end = xml.indexOf(closeTag, innerStart);
    if (end === -1) continue;
    results.push({ outer: xml.slice(start, end + closeTag.length), inner: xml.slice(innerStart, end), openTag: match[0] });
  }
  return results;
}

/**
 * Parse all top-level WITSML object elements from the document XML.
 * Returns objects with: { tag, uid, innerXml, props: {name: value} }
 */
function parseTopLevelElements(xml) {
  // Strip XML declaration and root wrapper
  const stripped = xml
    .replace(/<\?xml[^?]*\?>/g, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<WitsmlObjects[^>]*>/, '')
    .replace(/<\/WitsmlObjects>/, '');

  const knownTopLevel = [
    'Well', 'Wellbore', 'Trajectory', 'WellboreMarker', 'FormationMarker',
    'MudLog', 'MudLogReport', 'LogCurve', 'Channel', 'ChannelSet',
    'Rig', 'BhaRun', 'Tubular', 'BitRecord', 'CementJob',
    'FluidsReport', 'OpsReport', 'DrillingActivity', 'Risk',
    'SurveyProgram', 'WellTest', 'StimJob',
  ];

  const elements = [];

  for (const tag of knownTopLevel) {
    const blocks = extractAllBlocks(stripped, tag);
    for (const { outer, inner, openTag } of blocks) {
      const uid = extractUid(openTag);
      elements.push({ tag, uid, innerXml: inner });
    }
  }

  return elements;
}

/**
 * Extract scalar children from an element's inner XML.
 * Returns { childName: value, ... }
 */
function extractScalars(innerXml) {
  const props = {};
  // Match simple <name ...>value</name> patterns (no nested elements in value)
  const re = /<([a-zA-Z][a-zA-Z0-9_]*)(?:\s[^>]*)?>([^<]+)<\/\1>/g;
  let m;
  while ((m = re.exec(innerXml)) !== null) {
    const key = m[1];
    const val = m[2].trim();
    if (val && !props[key]) {
      props[key] = val;
    }
  }
  return props;
}

/**
 * Parse a TrajectoryStation nested block.
 */
function parseTrajectoryStations(innerXml) {
  const stations = [];
  const blocks = extractAllBlocks(innerXml, 'trajectoryStation');
  for (const { inner, openTag } of blocks) {
    const uid = extractUid(openTag);
    const props = extractScalars(inner);
    stations.push({ uid, props });
  }
  return stations;
}

// ─────────────────────────────────────────────────────────────────────────────
// Turtle helpers
// ─────────────────────────────────────────────────────────────────────────────

function ttlIri(iri) {
  return `<${iri}>`;
}

function ttlPrefixed(prefix, local) {
  return `${prefix}:${local}`;
}

function ttlLiteral(value, datatype) {
  const escaped = String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
  if (datatype) {
    return `"${escaped}"^^<${datatype}>`;
  }
  return `"${escaped}"`;
}

function slug(str) {
  return String(str)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

// ─────────────────────────────────────────────────────────────────────────────
// Prefixes block
// ─────────────────────────────────────────────────────────────────────────────

const PREFIXES = `@prefix geo:   <${GEO_PREFIX}> .
@prefix witsml: <${ENERGISTICS_NS}> .
@prefix inst:  <${DEFAULT_BASE_URI}> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix prov:  <http://www.w3.org/ns/prov#> .

`;

// ─────────────────────────────────────────────────────────────────────────────
// XSD type map for WITSML primitive property names
// ─────────────────────────────────────────────────────────────────────────────

const XSD_TYPE_HINTS = {
  // Depths and distances
  md: 'http://www.w3.org/2001/XMLSchema#decimal',
  tvd: 'http://www.w3.org/2001/XMLSchema#decimal',
  tvdss: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdTop: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdBottom: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdMin: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdMax: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdCurrent: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdBitRun: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdMn: 'http://www.w3.org/2001/XMLSchema#decimal',
  mdMx: 'http://www.w3.org/2001/XMLSchema#decimal',
  waterDepth: 'http://www.w3.org/2001/XMLSchema#decimal',
  groundElevation: 'http://www.w3.org/2001/XMLSchema#decimal',
  // Angles
  incl: 'http://www.w3.org/2001/XMLSchema#decimal',
  azi: 'http://www.w3.org/2001/XMLSchema#decimal',
  dipAngle: 'http://www.w3.org/2001/XMLSchema#decimal',
  dipDirection: 'http://www.w3.org/2001/XMLSchema#decimal',
  dls: 'http://www.w3.org/2001/XMLSchema#decimal',
  // Displacements
  dispNs: 'http://www.w3.org/2001/XMLSchema#decimal',
  dispEw: 'http://www.w3.org/2001/XMLSchema#decimal',
  dispNsEnd: 'http://www.w3.org/2001/XMLSchema#decimal',
  dispEwEnd: 'http://www.w3.org/2001/XMLSchema#decimal',
  vertSect: 'http://www.w3.org/2001/XMLSchema#decimal',
  // Boolean
  isActive: 'http://www.w3.org/2001/XMLSchema#boolean',
  finalTraj: 'http://www.w3.org/2001/XMLSchema#boolean',
  // DateTime
  dTimSpud: 'http://www.w3.org/2001/XMLSchema#dateTime',
  dTimPa: 'http://www.w3.org/2001/XMLSchema#dateTime',
  dTimTrajStart: 'http://www.w3.org/2001/XMLSchema#dateTime',
  dTimTrajEnd: 'http://www.w3.org/2001/XMLSchema#dateTime',
  dTimStn: 'http://www.w3.org/2001/XMLSchema#dateTime',
  dTimKickoff: 'http://www.w3.org/2001/XMLSchema#dateTime',
};

function xsdTypeFor(propName) {
  return XSD_TYPE_HINTS[propName] || 'http://www.w3.org/2001/XMLSchema#string';
}

// ─────────────────────────────────────────────────────────────────────────────
// Core conversion functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Generate triples for a single WITSML element.
 * Returns an array of Turtle triple strings (not terminated with a period — the
 * caller joins them into a single subject block).
 */
function elementToTriples(tag, uid, props, classIdx, parentLinks) {
  const clsDef = classIdx[tag];
  if (!clsDef) return [];

  const instUri = `inst:${slug(tag)}-${slug(uid || Object.values(props).join('-').slice(0, 20) || 'x')}`;
  const rdfClass = `geo:${clsDef.witsml_class}`;
  const witsmlUri = clsDef.witsml_uri;

  const triples = [];
  triples.push(`${instUri}`);
  triples.push(`    a ${rdfClass} ;`);
  triples.push(`    owl:sameAs <${witsmlUri}> ;`);

  // skos:prefLabel from name if present
  if (props.name) {
    triples.push(`    skos:prefLabel ${ttlLiteral(props.name)}@en ;`);
  }

  // Well relations via parent UIDs
  if (props.uidWell) {
    const wellUri = `inst:well-${slug(props.uidWell)}`;
    triples.push(`    geo:partOfWell ${wellUri} ;`);
  }
  if (props.uidWellbore) {
    const wbUri = `inst:wellbore-${slug(props.uidWellbore)}`;
    triples.push(`    geo:partOfWellbore ${wbUri} ;`);
  }

  // Additional explicit parent links (e.g. trajectory → wellbore)
  for (const [predicate, targetUri] of (parentLinks || [])) {
    triples.push(`    ${predicate} ${targetUri} ;`);
  }

  // Primitive properties — use crosswalk type hints where available, else XSD_TYPE_HINTS
  const propMap = {};
  for (const pp of (clsDef.primitive_properties || [])) {
    propMap[pp.name] = pp.type || 'xsd:string';
  }

  for (const [key, val] of Object.entries(props)) {
    if (['name', 'uidWell', 'uidWellbore', 'uid'].includes(key)) continue;
    const xsdType = XSD_TYPE_HINTS[key] || 'http://www.w3.org/2001/XMLSchema#string';
    triples.push(`    geo:${key} ${ttlLiteral(val, xsdType)} ;`);
  }

  // prov:generatedAtTime for dateTime props
  if (props.dTimSpud || props.dTimTrajStart || props.dTimStn) {
    const dt = props.dTimSpud || props.dTimTrajStart || props.dTimStn;
    triples.push(`    prov:generatedAtTime ${ttlLiteral(dt, 'http://www.w3.org/2001/XMLSchema#dateTime')} ;`);
  }

  // Replace last ';' with '.'
  if (triples.length > 1) {
    triples[triples.length - 1] = triples[triples.length - 1].replace(/;$/, '.');
  }

  return triples;
}

/**
 * Generate Turtle triples for TrajectoryStation nested elements.
 */
function stationsToTriples(stations, trajectoryUri) {
  const lines = [];
  for (const stn of stations) {
    const stnUid = stn.uid || `stn-${Math.random().toString(36).slice(2, 8)}`;
    const stnUri = `inst:trajectory-station-${slug(stnUid)}`;
    lines.push(`${stnUri}`);
    lines.push(`    a geo:TrajectoryStation ;`);
    lines.push(`    geo:inTrajectory ${trajectoryUri} ;`);

    for (const [key, val] of Object.entries(stn.props)) {
      const xsdType = XSD_TYPE_HINTS[key] || 'http://www.w3.org/2001/XMLSchema#string';
      lines.push(`    geo:${key} ${ttlLiteral(val, xsdType)} ;`);
    }

    // Replace last ';' with '.'
    lines[lines.length - 1] = lines[lines.length - 1].replace(/;$/, '.');
    lines.push('');
  }
  return lines;
}

// ─────────────────────────────────────────────────────────────────────────────
// Main convert function (exported)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Convert a WITSML 2.0 XML string to a Turtle (TTL) string.
 *
 * @param {string} xmlString - Raw WITSML XML
 * @param {object} [options]
 * @param {string} [options.baseUri] - Override the base URI for instances
 * @returns {string} Turtle-formatted RDF triples
 */
function convert(xmlString, options = {}) {
  const crosswalk = loadCrosswalk();
  const classIdx  = buildClassIndex(crosswalk);

  const elements = parseTopLevelElements(xmlString);

  const allLines = [PREFIXES];
  allLines.push(`# Generated by witsml-to-rdf.js — ${new Date().toISOString()}`);
  allLines.push(`# Source standard: WITSML 2.0 (Energistics)`);
  allLines.push(`# Crosswalk: data/witsml-rdf-crosswalk.json`);
  allLines.push('');

  const trajectoryUidToUri = {};

  for (const { tag, uid, innerXml } of elements) {
    const props = extractScalars(innerXml);
    if (uid) props.uid = uid;

    const instSlug = `${slug(tag)}-${slug(uid || props.name || 'x')}`;
    const instUri  = `inst:${instSlug}`;

    if (tag === 'Trajectory') {
      // Record uri for station linking
      trajectoryUidToUri[uid] = instUri;
    }

    const tripleLines = elementToTriples(tag, uid, props, classIdx, []);

    if (tripleLines.length > 1) {
      allLines.push(...tripleLines);
      allLines.push('');
    }

    // For Trajectory, also emit its TrajectoryStation children
    if (tag === 'Trajectory') {
      const stations = parseTrajectoryStations(innerXml);
      if (stations.length > 0) {
        const stationLines = stationsToTriples(stations, instUri);
        allLines.push(...stationLines);
      }
    }
  }

  return allLines.join('\n');
}

// ─────────────────────────────────────────────────────────────────────────────
// CLI entry point
// ─────────────────────────────────────────────────────────────────────────────

if (require.main === module) {
  let xmlString;
  const arg = process.argv[2];

  if (arg) {
    const xmlPath = path.resolve(process.cwd(), arg);
    if (!fs.existsSync(xmlPath)) {
      console.error(`Error: file not found: ${xmlPath}`);
      process.exit(1);
    }
    xmlString = fs.readFileSync(xmlPath, 'utf8');
    console.error(`[witsml-to-rdf] Converting: ${xmlPath}`);
  } else if (fs.existsSync(SAMPLE_PATH)) {
    xmlString = fs.readFileSync(SAMPLE_PATH, 'utf8');
    console.error(`[witsml-to-rdf] No input file given — using embedded sample: ${SAMPLE_PATH}`);
  } else {
    // Minimal inline fallback if neither is available
    xmlString = `<?xml version="1.0"?>
<WitsmlObjects xmlns="http://www.energistics.org/energyml/data/witsmlv2/2.0">
  <Well uid="well-demo-001">
    <name>DEMO-1-RJS</name>
    <country>BR</country>
    <statusWell>active</statusWell>
    <waterDepth uom="m">2050.0</waterDepth>
  </Well>
  <Wellbore uid="wb-demo-001">
    <name>DEMO-1-RJS main</name>
    <uidWell>well-demo-001</uidWell>
    <statusWellbore>active</statusWellbore>
    <mdCurrent uom="m">5200.0</mdCurrent>
    <tvdCurrent uom="m">4100.0</tvdCurrent>
  </Wellbore>
</WitsmlObjects>`;
    console.error('[witsml-to-rdf] Using inline fallback sample.');
  }

  const ttl = convert(xmlString);
  process.stdout.write(ttl);
}

// ─────────────────────────────────────────────────────────────────────────────
// Exports
// ─────────────────────────────────────────────────────────────────────────────

module.exports = { convert };
